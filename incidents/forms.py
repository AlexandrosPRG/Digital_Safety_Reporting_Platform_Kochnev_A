from django import forms
from .models import Incident


class IncidentForm(forms.ModelForm):
    """Formular pro vytvoreni noveho incidentu."""

    class Meta:
        """Nastaveni poli pro IncidentForm."""
        model = Incident
        fields = [
            'title',
            'incident_type',
            'risk_level',
            'date_occurred',
            'location',
            'categories',
            'description',
        ]


class IncidentStatusForm(forms.ModelForm):
    """Formular pro zmenu stavu incidentu."""

    class Meta:
        """Nastaveni poli pro IncidentStatusForm."""
        model = Incident
        fields = ['status']
