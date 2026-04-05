from django.db import models
from django.contrib.auth.models import User


class EmployeeProfile(models.Model):
    """Represents an employee profile with a role in the system."""

    ROLE_EMPLOYEE = 'EMPLOYEE'
    ROLE_MANAGER = 'SAFETY_MANAGER'

    ROLE_CHOICES = [
        (ROLE_EMPLOYEE, 'Employee'),
        (ROLE_MANAGER, 'Safety Manager'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Location(models.Model):
    """Represents a workplace location or area."""

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class IncidentCategory(models.Model):
    """Represents a category assigned to incidents."""

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Incident(models.Model):
    """Represents a safety incident or near miss."""

    TYPE_NEAR_MISS = 'NEAR_MISS'
    TYPE_INJURY = 'INJURY'
    TYPE_UNSAFE = 'UNSAFE'

    TYPE_CHOICES = [
        (TYPE_NEAR_MISS, 'Near Miss'),
        (TYPE_INJURY, 'Injury'),
        (TYPE_UNSAFE, 'Unsafe Condition'),
    ]

    RISK_LOW = 'LOW'
    RISK_MEDIUM = 'MEDIUM'
    RISK_HIGH = 'HIGH'

    RISK_CHOICES = [
        (RISK_LOW, 'Low'),
        (RISK_MEDIUM, 'Medium'),
        (RISK_HIGH, 'High'),
    ]

    STATUS_NEW = 'NEW'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_CLOSED = 'CLOSED'

    STATUS_CHOICES = [
        (STATUS_NEW, 'New'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_CLOSED, 'Closed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()

    incident_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
    )

    date_occurred = models.DateField()
    date_reported = models.DateTimeField(auto_now_add=True)

    reported_by = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    categories = models.ManyToManyField(IncidentCategory, blank=True)

    class Meta:
        ordering = ['-date_reported']
        verbose_name = 'Incident'
        verbose_name_plural = 'Incidents'

    def __str__(self):
        return f"{self.title} ({self.get_risk_level_display()})"


class CorrectiveAction(models.Model):
    """Represents a corrective action linked to an incident."""

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

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.incident.title} - Action"