from django import forms
from .models import Incident


class IncidentForm(forms.ModelForm):
    """Formular pro vytvoreni noveho incidentu."""

    date_occurred = forms.DateField(
        input_formats=["%d.%m.%Y", "%Y-%m-%d"],
        help_text="Zadejte datum ve formatu DD.MM.YYYY nebo vyberte z kalendare.",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "placeholder": "DD.MM.YYYY",
            }
        ),
    )

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
