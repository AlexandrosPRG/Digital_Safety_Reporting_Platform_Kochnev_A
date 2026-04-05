from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from openpyxl import Workbook

from .forms import IncidentForm, IncidentStatusForm
from .models import EmployeeProfile, Incident


def _get_profile(user):
    """Ziska nebo vytvori EmployeeProfile pro prihlaseneho uzivatele."""
    profile, _ = EmployeeProfile.objects.get_or_create(
        user=user,
        defaults={"role": "EMPLOYEE"},
    )
    return profile


def _is_manager(user):
    """Vraci True, pokud ma uzivatel roli SAFETY_MANAGER."""
    profile = _get_profile(user)
    return profile.role == "SAFETY_MANAGER"


def _is_demo_user(user):
    """Vraci True, pokud je prihlaseny demo uzivatel."""
    return user.username == "demo"


def _can_access_dashboard(user):
    """Vraci True, pokud uzivatel muze otevrit dashboard."""
    return _is_manager(user) or _is_demo_user(user)


@login_required
def incident_list(request):
    """Zobrazi seznam incidentu pro prihlaseneho uzivatele."""
    incidents = Incident.objects.select_related("location").order_by("-date_reported")
    return render(request, "incidents/incident_list.html", {"incidents": incidents})


@login_required
def incident_detail(request, pk):
    """Zobrazi detail konkretniho incidentu."""
    incident = get_object_or_404(Incident, pk=pk)
    return render(request, "incidents/incident_detail.html", {"incident": incident})


@login_required
def incident_create(request):
    """Umoznuje vytvorit novy incident pomoci POST formulare."""
    if _is_demo_user(request.user):
        return HttpResponseForbidden("Demo mode: creating incidents is not allowed.")

    if request.method == "POST":
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reported_by = _get_profile(request.user)
            incident.save()
            form.save_m2m()
            return redirect("incident_detail", pk=incident.pk)
    else:
        form = IncidentForm()

    return render(request, "incidents/incident_form.html", {"form": form})


@login_required
def incident_update_status(request, pk):
    """Umoznuje safety managerovi zmenit stav incidentu pomoci POST."""
    if _is_demo_user(request.user):
        return HttpResponseForbidden("Demo mode: status updates are not allowed.")

    if not _is_manager(request.user):
        return HttpResponseForbidden("Forbidden")

    incident = get_object_or_404(Incident, pk=pk)

    if request.method == "POST":
        form = IncidentStatusForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            return redirect("incident_detail", pk=incident.pk)
    else:
        form = IncidentStatusForm(instance=incident)

    return render(
        request,
        "incidents/incident_status_form.html",
        {"form": form, "incident": incident},
    )


@login_required
def dashboard(request):
    """Zobrazi zakladni statistiky pro managera nebo demo uzivatele."""
    if not _can_access_dashboard(request.user):
        return HttpResponseForbidden("Forbidden")

    by_risk = list(
        Incident.objects.values("risk_level")
        .annotate(count=Count("id"))
        .order_by("risk_level")
    )

    by_status = list(
        Incident.objects.values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )

    risk_display_map = dict(Incident.RISK_CHOICES)
    status_display_map = dict(Incident.STATUS_CHOICES)

    for row in by_risk:
        row["risk_level_display"] = risk_display_map.get(
            row["risk_level"],
            row["risk_level"],
        )

    for row in by_status:
        row["status_display"] = status_display_map.get(
            row["status"],
            row["status"],
        )

    total_incidents = Incident.objects.count()
    open_incidents = Incident.objects.filter(status="open").count()
    high_risk_incidents = Incident.objects.filter(risk_level="high").count()

    context = {
        "by_risk": by_risk,
        "by_status": by_status,
        "total_incidents": total_incidents,
        "open_incidents": open_incidents,
        "high_risk_incidents": high_risk_incidents,
        "is_demo": _is_demo_user(request.user),
    }
    return render(request, "incidents/dashboard.html", context)


@login_required
def export_incidents_excel(request):
    """Exportuje incidenty do Excel souboru (XLSX)."""
    if not _can_access_dashboard(request.user):
        return HttpResponseForbidden("Forbidden")

    wb = Workbook()
    ws = wb.active
    ws.title = "Incidents"

    ws.append(["ID", "Title", "Type", "Risk", "Status", "Date occurred", "Location"])

    incidents = Incident.objects.select_related("location").order_by("-date_reported")

    for incident in incidents:
        ws.append([
            incident.id,
            incident.title,
            incident.get_incident_type_display(),
            incident.get_risk_level_display(),
            incident.get_status_display(),
            incident.date_occurred,
            incident.location.name if incident.location else "",
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="incidents_{date.today().isoformat()}.xlsx"'
    )

    wb.save(response)
    return response