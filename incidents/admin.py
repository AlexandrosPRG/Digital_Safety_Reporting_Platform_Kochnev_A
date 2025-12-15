from django.contrib import admin
from .models import EmployeeProfile, Location, IncidentCategory, Incident, CorrectiveAction


class IncidentAdmin(admin.ModelAdmin):
    """Admin nastaveni pro model Incident."""
    list_display = ('title', 'incident_type', 'risk_level', 'status', 'date_occurred')
    list_filter = ('incident_type', 'risk_level', 'status')
    search_fields = ('title', 'description')


admin.site.register(EmployeeProfile)
admin.site.register(Location)
admin.site.register(IncidentCategory)
admin.site.register(Incident, IncidentAdmin)
admin.site.register(CorrectiveAction)
