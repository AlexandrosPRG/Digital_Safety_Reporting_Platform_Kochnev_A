from datetime import date, timedelta
from django.contrib.auth.models import User
from incidents.models import EmployeeProfile, Location, IncidentCategory, Incident


user = User.objects.get(username="demo")
profile, _ = EmployeeProfile.objects.get_or_create(
    user=user,
    defaults={"role": EmployeeProfile.ROLE_EMPLOYEE},
)

warehouse_a, _ = Location.objects.get_or_create(name="Warehouse A")
office, _ = Location.objects.get_or_create(name="Office")

slips, _ = IncidentCategory.objects.get_or_create(name="Slips")
ppe, _ = IncidentCategory.objects.get_or_create(name="PPE")

incidents_data = [
    {
        "title": "Forklift near miss",
        "description": "Near collision with pedestrian",
        "incident_type": Incident.TYPE_NEAR_MISS,
        "risk_level": Incident.RISK_HIGH,
        "status": Incident.STATUS_NEW,
        "date_occurred": date.today() - timedelta(days=2),
        "location": warehouse_a,
        "categories": [slips],
    },
    {
        "title": "Wet floor",
        "description": "Slippery surface",
        "incident_type": Incident.TYPE_UNSAFE,
        "risk_level": Incident.RISK_MEDIUM,
        "status": Incident.STATUS_IN_PROGRESS,
        "date_occurred": date.today() - timedelta(days=5),
        "location": warehouse_a,
        "categories": [slips],
    },
]

created_count = 0

for item in incidents_data:
    incident, created = Incident.objects.get_or_create(
        title=item["title"],
        defaults={
            "description": item["description"],
            "incident_type": item["incident_type"],
            "risk_level": item["risk_level"],
            "status": item["status"],
            "date_occurred": item["date_occurred"],
            "reported_by": profile,
            "location": item["location"],
        }
    )

    if created:
        incident.categories.set(item["categories"])
        created_count += 1

print(f"Created {created_count} incidents")
print(f"Total: {Incident.objects.count()}")