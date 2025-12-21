from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Incident
from .serializers import IncidentSerializer


class IncidentListApiView(generics.ListAPIView):
    """API view pro seznam incidentu (jen pro prihlaseneho uzivatele)."""
    permission_classes = [IsAuthenticated]
    queryset = Incident.objects.all().order_by('-date_reported')
    serializer_class = IncidentSerializer


class IncidentDetailApiView(generics.RetrieveAPIView):
    """API view pro detail incidentu (jen pro prihlaseneho uzivatele)."""
    permission_classes = [IsAuthenticated]
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
