
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin

class Audit(AuditMixin):
    class AuditType(models.TextChoices):
        INTERNAL="INTERNAL","Internal Audit"
        EXTERNAL="EXTERNAL","External Audit"
        REGULATORY="REGULATORY","Regulatory / Government"
        CERTIFICATION="CERT","Certification Audit"
        SURVEILLANCE="SURV","Surveillance Audit"
    class Status(models.TextChoices):
        PLANNED="PLANNED","Planned"
        IN_PROGRESS="IN_PROGRESS","In Progress"
        COMPLETED="COMPLETED","Completed"
        CANCELLED="CANCELLED","Cancelled"
    class Result(models.TextChoices):
        PASS="PASS","Pass / No Major Findings"
        CONDITIONAL="CONDITIONAL","Conditional Pass"
        FAIL="FAIL","Fail / Major Findings"

    title=models.CharField(max_length=255)
    audit_type=models.CharField(max_length=20,choices=AuditType.choices,default=AuditType.INTERNAL)
    auditor=models.CharField(max_length=255,blank=True)
    lead_auditor=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="audits_led")
    department=models.ForeignKey("departments.Department",null=True,blank=True,on_delete=models.SET_NULL)
    site=models.ForeignKey("accounts.Site",null=True,blank=True,on_delete=models.SET_NULL)
    scheduled_date=models.DateField()
    completed_date=models.DateField(null=True,blank=True)
    status=models.CharField(max_length=20,choices=Status.choices,default=Status.PLANNED)
    result=models.CharField(max_length=20,choices=Result.choices,blank=True)
    scope=models.TextField(blank=True)
    summary=models.TextField(blank=True)
    report_file=models.FileField(upload_to="audit_reports/",null=True,blank=True)
    findings_count=models.PositiveIntegerField(default=0)
    major_nc_count=models.PositiveIntegerField(default=0)
    minor_nc_count=models.PositiveIntegerField(default=0)
    observations_count=models.PositiveIntegerField(default=0)
    next_audit_date=models.DateField(null=True,blank=True)
    notes=models.TextField(blank=True)
    class Meta: ordering=["-scheduled_date"]
    def __str__(self): return f"{self.title} ({self.scheduled_date})"
    @property
    def status_css(self):
        return {"PLANNED":"head","IN_PROGRESS":"hod","COMPLETED":"approved","CANCELLED":"muted"}.get(self.status,"draft")
    @property
    def result_css(self):
        return {"PASS":"approved","CONDITIONAL":"warning","FAIL":"danger"}.get(self.result,"draft")
