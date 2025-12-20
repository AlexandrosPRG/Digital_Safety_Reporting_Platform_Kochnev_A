from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count

from .forms import IncidentForm, IncidentStatusForm
from .models import EmployeeProfile, Incident


def _get_profile(user):
    """Pomocna funkce pro ziskani profilu uzivatele."""
    return EmployeeProfile.objects.get(user=user)


def _is_manager(user):
    """Vraci True, pokud ma uzivatel roli SAFETY_MANAGER."""
    profile = _get_profile(user)
    return profile.role == 'SAFETY_MANAGER'


@login_required
def incident_list(request):
    """Zobrazi seznam incidentu pro prihlaseneho uzivatele."""
    incidents = Incident.objects.select_related('location').order_by('-date_reported')
    return render(request, 'incidents/incident_list.html', {'incidents': incidents})


@login_required
def incident_detail(request, pk):
    """Zobrazi detail konkretniho incidentu."""
    incident = get_object_or_404(Incident, pk=pk)
    return render(request, 'incidents/incident_detail.html', {'incident': incident})


@login_required
def incident_create(request):
    """Umoznuje vytvorit novy incident pomoci POST formulare."""
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reported_by = _get_profile(request.user)
            incident.save()
            form.save_m2m()
            return redirect('incident_detail', pk=incident.pk)
    else:
        form = IncidentForm()

    return render(request, 'incidents/incident_form.html', {'form': form})


@login_required
def incident_update_status(request, pk):
    """Umoznuje safety managerovi zmenit stav incidentu pomoci POST."""
    if not _is_manager(request.user):
        return HttpResponseForbidden("Forbidden")

    incident = get_object_or_404(Incident, pk=pk)

    if request.method == 'POST':
        form = IncidentStatusForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            return redirect('incident_detail', pk=incident.pk)
    else:
        form = IncidentStatusForm(instance=incident)

    return render(
        request,
        'incidents/incident_status_form.html',
        {'form': form, 'incident': incident},
    )


@login_required
def dashboard(request):
    """Zobrazi zakladni statistiky (jen pro safety managera)."""
    if not _is_manager(request.user):
        return HttpResponseForbidden("Forbidden")

    by_risk = Incident.objects.values('risk_level').annotate(count=Count('id')).order_by('risk_level')
    by_status = Incident.objects.values('status').annotate(count=Count('id')).order_by('status')

    context = {
        'by_risk': by_risk,
        'by_status': by_status,
    }
    return render(request, 'incidents/dashboard.html', context)
