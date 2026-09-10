
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin

class Incident(AuditMixin):
    class IncidentType(models.TextChoices):
        ACCIDENT="ACCIDENT","Accident"
        NEAR_MISS="NEAR_MISS","Near Miss"
        INJURY="INJURY","Injury / Illness"
        ENVIRONMENTAL="ENVIRONMENTAL","Environmental Incident"
        EQUIPMENT="EQUIPMENT","Equipment Incident"
        SECURITY="SECURITY","Security Incident"
        FIRE="FIRE","Fire / Explosion"
        SPILLAGE="SPILLAGE","Chemical Spillage"
        OTHER="OTHER","Other"
    class Severity(models.TextChoices):
        CRITICAL="CRITICAL","Critical / Fatality"
        MAJOR="MAJOR","Major"
        MODERATE="MODERATE","Moderate"
        MINOR="MINOR","Minor"
        NEGLIGIBLE="NEGLIGIBLE","Negligible / Near Miss"
    class Status(models.TextChoices):
        OPEN="OPEN","Open"
        INVESTIGATING="INVESTIGATING","Under Investigation"
        CLOSED="CLOSED","Closed"

    title=models.CharField(max_length=300)
    incident_type=models.CharField(max_length=20,choices=IncidentType.choices,default=IncidentType.ACCIDENT)
    severity=models.CharField(max_length=20,choices=Severity.choices,default=Severity.MINOR)
    status=models.CharField(max_length=20,choices=Status.choices,default=Status.OPEN)
    incident_date=models.DateTimeField()
    location=models.CharField(max_length=255,blank=True)
    department=models.ForeignKey("departments.Department",null=True,blank=True,on_delete=models.SET_NULL)
    site=models.ForeignKey("accounts.Site",null=True,blank=True,on_delete=models.SET_NULL)
    reported_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="incidents_reported")
    persons_involved=models.TextField(blank=True,help_text="Names of persons involved")
    witnesses=models.TextField(blank=True)
    description=models.TextField()
    immediate_action=models.TextField(blank=True,help_text="Immediate actions taken")
    root_cause=models.TextField(blank=True)
    contributing_factors=models.TextField(blank=True)
    investigation_notes=models.TextField(blank=True)
    injuries_description=models.TextField(blank=True)
    lost_time_days=models.PositiveIntegerField(default=0)
    property_damage_value=models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    regulatory_notification_required=models.BooleanField(default=False)
    regulatory_notified=models.BooleanField(default=False)
    regulatory_ref=models.CharField(max_length=100,blank=True)
    closed_date=models.DateField(null=True,blank=True)
    class Meta: ordering=["-incident_date"]
    def __str__(self): return f"{self.title} ({self.incident_date.date()})"
    @property
    def severity_css(self):
        return {"CRITICAL":"danger","MAJOR":"danger","MODERATE":"warning","MINOR":"hod","NEGLIGIBLE":"approved"}.get(self.severity,"draft")
    @property
    def status_css(self):
        return {"OPEN":"danger","INVESTIGATING":"warning","CLOSED":"approved"}.get(self.status,"draft")
