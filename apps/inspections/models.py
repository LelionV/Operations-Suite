
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin

class InspectionChecklist(models.Model):
    name=models.CharField(max_length=200); description=models.TextField(blank=True)
    category=models.CharField(max_length=50, blank=True)
    class Meta: ordering=["name"]
    def __str__(self): return self.name

class ChecklistItem(models.Model):
    checklist=models.ForeignKey(InspectionChecklist,on_delete=models.CASCADE,related_name="items")
    order=models.PositiveIntegerField(default=0); question=models.CharField(max_length=500)
    is_mandatory=models.BooleanField(default=True)
    class Meta: ordering=["order"]
    def __str__(self): return self.question[:60]

class Inspection(AuditMixin):
    class Status(models.TextChoices):
        SCHEDULED="SCHEDULED","Scheduled"
        IN_PROGRESS="IN_PROGRESS","In Progress"
        COMPLETED="COMPLETED","Completed"
        OVERDUE="OVERDUE","Overdue"
    class InspectionType(models.TextChoices):
        SAFETY="SAFETY","Safety Inspection"
        EQUIPMENT="EQUIPMENT","Equipment Inspection"
        SITE="SITE","Site Inspection"
        DEPT="DEPT","Department Inspection"
        FIRE="FIRE","Fire Safety"
        ELECTRICAL="ELECTRICAL","Electrical"
        OTHER="OTHER","Other"

    title=models.CharField(max_length=255)
    inspection_type=models.CharField(max_length=20,choices=InspectionType.choices,default=InspectionType.SAFETY)
    checklist=models.ForeignKey(InspectionChecklist,null=True,blank=True,on_delete=models.SET_NULL,related_name="inspections")
    equipment=models.ForeignKey("equipment.Equipment",null=True,blank=True,on_delete=models.SET_NULL,related_name="inspections")
    department=models.ForeignKey("departments.Department",null=True,blank=True,on_delete=models.SET_NULL)
    site=models.ForeignKey("accounts.Site",null=True,blank=True,on_delete=models.SET_NULL)
    inspector=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="inspections_conducted")
    scheduled_date=models.DateField()
    completed_date=models.DateField(null=True,blank=True)
    next_inspection_date=models.DateField(null=True,blank=True)
    status=models.CharField(max_length=20,choices=Status.choices,default=Status.SCHEDULED)
    overall_result=models.CharField(max_length=20,choices=[("PASS","Pass"),("FAIL","Fail"),("CONDITIONAL","Conditional")],blank=True)
    summary=models.TextField(blank=True); defects_found=models.TextField(blank=True)
    notes=models.TextField(blank=True)
    class Meta: ordering=["-scheduled_date"]
    def __str__(self): return f"{self.title} ({self.scheduled_date})"
    @property
    def status_css(self):
        return {"SCHEDULED":"head","IN_PROGRESS":"hod","COMPLETED":"approved","OVERDUE":"danger"}.get(self.status,"muted")

class InspectionResult(models.Model):
    inspection=models.ForeignKey(Inspection,on_delete=models.CASCADE,related_name="results")
    checklist_item=models.ForeignKey(ChecklistItem,on_delete=models.CASCADE)
    result=models.CharField(max_length=20,choices=[("PASS","Pass"),("FAIL","Fail"),("N/A","N/A")],default="PASS")
    notes=models.TextField(blank=True)
    photo=models.ImageField(upload_to="inspection_photos/",null=True,blank=True)
    def __str__(self): return f"{self.inspection} — {self.checklist_item.question[:40]}"
