from rest_framework import serializers
from .models import Incident


class IncidentSerializer(serializers.ModelSerializer):
    """Serializer pro model Incident (REST API)."""

    class Meta:
        """Nastaveni poli pro IncidentSerializer."""
        model = Incident
        fields = [
            'id',
            'title',
            'description',
            'incident_type',
            'risk_level',
            'status',
            'date_occurred',
            'date_reported',
        ]
