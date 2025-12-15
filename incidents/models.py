from django.db import models
from django.contrib.auth.models import User


class EmployeeProfile(models.Model):
    """Model pro profil zamestnance s roli v systemu."""
    ROLE_CHOICES = [
        ('EMPLOYEE', 'Employee'),
        ('SAFETY_MANAGER', 'Safety Manager'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        """Vraci jmeno uzivatele a jeho roli."""
        return f"{self.user.username} ({self.role})"


class Location(models.Model):
    """Model pro pracovni lokalitu nebo usek."""
    name = models.CharField(max_length=100)

    def __str__(self):
        """Vraci nazev lokality."""
        return self.name


class IncidentCategory(models.Model):
    """Model pro kategorii incidentu."""
    name = models.CharField(max_length=100)

    def __str__(self):
        """Vraci nazev kategorie incidentu."""
        return self.name


class Incident(models.Model):
    """Model pro bezpecnostni incident nebo near miss."""

    TYPE_CHOICES = [
        ('NEAR_MISS', 'Near Miss'),
        ('INJURY', 'Injury'),
        ('UNSAFE', 'Unsafe Condition'),
    ]

    RISK_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('IN_PROGRESS', 'In Progress'),
        ('CLOSED', 'Closed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    incident_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES)
    date_occurred = models.DateField()
    date_reported = models.DateTimeField(auto_now_add=True)

    reported_by = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    categories = models.ManyToManyField(IncidentCategory, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NEW',
    )

    def __str__(self):
        """Vraci kratky nazev incidentu."""
        return self.title


class CorrectiveAction(models.Model):
    """Model pro korektivni opatreni k incidentu."""

    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    description = models.TextField()
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        """Vraci popis opatreni s referenci na incident."""
        return f"Action for {self.incident.title}"
