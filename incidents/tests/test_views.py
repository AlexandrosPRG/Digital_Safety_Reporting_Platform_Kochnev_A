import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date

from incidents.models import EmployeeProfile, Location, Incident, IncidentCategory


@pytest.fixture
def employee_user(db):
    """Vytvori uzivatele s roli EMPLOYEE."""
    user = User.objects.create_user(username="emp", password="pass12345")
    EmployeeProfile.objects.create(user=user, role="EMPLOYEE")
    return user


@pytest.fixture
def manager_user(db):
    """Vytvori uzivatele s roli SAFETY_MANAGER."""
    user = User.objects.create_user(username="mgr", password="pass12345")
    EmployeeProfile.objects.create(user=user, role="SAFETY_MANAGER")
    return user


@pytest.fixture
def sample_data(db, employee_user):
    """Vytvori zakladni data pro testy (location, category, incident)."""
    loc = Location.objects.create(name="Sklad A")
    cat = IncidentCategory.objects.create(name="Near miss")
    incident = Incident.objects.create(
        title="Test incident",
        description="Popis",
        incident_type="NEAR_MISS",
        risk_level="LOW",
        status="NEW",
        date_occurred=date.today(),
        reported_by=EmployeeProfile.objects.get(user=employee_user),
        location=loc,
    )
    incident.categories.add(cat)
    return {"loc": loc, "cat": cat, "incident": incident}


@pytest.mark.django_db
def test_incident_list_redirect_for_anonymous(client):
    """Neprihlaseny uzivatel je presmerovan na login."""
    url = reverse("incident_list")
    res = client.get(url)
    assert res.status_code == 302
    assert "/accounts/login/" in res["Location"]


@pytest.mark.django_db
def test_incident_list_ok_for_logged_in(client, employee_user, sample_data):
    """Prihlaseny uzivatel vidi seznam incidentu."""
    client.login(username="emp", password="pass12345")
    url = reverse("incident_list")
    res = client.get(url)
    assert res.status_code == 200
    assert "Seznam incidentu" in res.content.decode()


@pytest.mark.django_db
def test_incident_detail_redirect_for_anonymous(client, sample_data):
    """Neprihlaseny uzivatel se nedostane na detail."""
    url = reverse("incident_detail", kwargs={"pk": sample_data["incident"].pk})
    res = client.get(url)
    assert res.status_code == 302


@pytest.mark.django_db
def test_incident_detail_ok_for_logged_in(client, employee_user, sample_data):
    """Prihlaseny uzivatel vidi detail incidentu."""
    client.login(username="emp", password="pass12345")
    url = reverse("incident_detail", kwargs={"pk": sample_data["incident"].pk})
    res = client.get(url)
    assert res.status_code == 200
    assert "Detail incidentu" in res.content.decode()


@pytest.mark.django_db
def test_incident_create_get_ok(client, employee_user):
    """GET na formular funguje pro prihlaseneho uzivatele."""
    client.login(username="emp", password="pass12345")
    url = reverse("incident_create")
    res = client.get(url)
    assert res.status_code == 200
    assert "Novy incident" in res.content.decode()


@pytest.mark.django_db
def test_incident_create_post_creates_incident(client, employee_user):
    """POST vytvori novy incident."""
    client.login(username="emp", password="pass12345")
    loc = Location.objects.create(name="Hala 1")
    cat = IncidentCategory.objects.create(name="Unsafe")
    url = reverse("incident_create")

    payload = {
        "title": "New incident",
        "description": "Test",
        "incident_type": "UNSAFE",
        "risk_level": "MEDIUM",
        "date_occurred": str(date.today()),
        "location": loc.id,
        "categories": [cat.id],
    }

    res = client.post(url, data=payload)
    assert res.status_code == 302
    assert Incident.objects.filter(title="New incident").exists()


@pytest.mark.django_db
def test_update_status_forbidden_for_employee(client, employee_user, sample_data):
    """Employee nema pristup ke zmene stavu."""
    client.login(username="emp", password="pass12345")
    url = reverse("incident_update_status", kwargs={"pk": sample_data["incident"].pk})
    res = client.get(url)
    assert res.status_code == 403


@pytest.mark.django_db
def test_update_status_ok_for_manager(client, manager_user, sample_data):
    """Manager muze zmenit stav incidentu."""
    client.login(username="mgr", password="pass12345")
    url = reverse("incident_update_status", kwargs={"pk": sample_data["incident"].pk})
    res = client.get(url)
    assert res.status_code == 200
    assert "Zmena stavu" in res.content.decode()


@pytest.mark.django_db
def test_dashboard_forbidden_for_employee(client, employee_user):
    """Employee nema pristup na dashboard."""
    client.login(username="emp", password="pass12345")
    url = reverse("dashboard")
    res = client.get(url)
    assert res.status_code == 403


@pytest.mark.django_db
def test_dashboard_ok_for_manager(client, manager_user, sample_data):
    """Manager vidi dashboard."""
    client.login(username="mgr", password="pass12345")
    url = reverse("dashboard")
    res = client.get(url)
    assert res.status_code == 200
    assert "Dashboard" in res.content.decode()
