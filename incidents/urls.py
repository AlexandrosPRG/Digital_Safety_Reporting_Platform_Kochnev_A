from django.urls import path
from . import views
from .api import IncidentListApiView, IncidentDetailApiView
from .views import export_incidents_excel

urlpatterns = [
    path('', views.incident_list, name='incident_list'),
    path('incidents/<int:pk>/', views.incident_detail, name='incident_detail'),
    path('incidents/new/', views.incident_create, name='incident_create'),
    path('incidents/<int:pk>/status/', views.incident_update_status, name='incident_update_status'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/incidents/', IncidentListApiView.as_view(), name='api_incident_list'),
    path('api/incidents/<int:pk>/', IncidentDetailApiView.as_view(), name='api_incident_detail'),
    path("reports/incidents.xlsx", export_incidents_excel, name="export_incidents_excel"),
]
