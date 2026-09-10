
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin

class TrainingCourse(models.Model):
    title=models.CharField(max_length=255)
    description=models.TextField(blank=True)
    category=models.CharField(max_length=100,blank=True)
    provider=models.CharField(max_length=200,blank=True)
    duration_hours=models.DecimalField(max_digits=6,decimal_places=1,null=True,blank=True)
    validity_months=models.PositiveIntegerField(default=12,help_text="Certification valid for N months")
    is_mandatory=models.BooleanField(default=False)
    class Meta: ordering=["title"]
    def __str__(self): return self.title

class TrainingRecord(AuditMixin):
    class Status(models.TextChoices):
        SCHEDULED="SCHEDULED","Scheduled"
        IN_PROGRESS="IN_PROGRESS","In Progress"
        COMPLETED="COMPLETED","Completed"
        FAILED="FAILED","Failed"
        EXPIRED="EXPIRED","Expired"
    employee=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="training_records")
    course=models.ForeignKey(TrainingCourse,on_delete=models.CASCADE,related_name="records")
    status=models.CharField(max_length=20,choices=Status.choices,default=Status.SCHEDULED)
    scheduled_date=models.DateField()
    completed_date=models.DateField(null=True,blank=True)
    expiry_date=models.DateField(null=True,blank=True)
    score=models.DecimalField(max_digits=5,decimal_places=1,null=True,blank=True,help_text="Score %")
    pass_mark=models.DecimalField(max_digits=5,decimal_places=1,default=80)
    certificate_number=models.CharField(max_length=100,blank=True)
    certificate_file=models.FileField(upload_to="training_certs/",null=True,blank=True)
    trainer=models.CharField(max_length=200,blank=True)
    notes=models.TextField(blank=True)
    class Meta: ordering=["-scheduled_date"]
    def __str__(self): return f"{self.employee.get_full_name()} — {self.course.title}"
    @property
    def is_expired(self):
        from django.utils import timezone
        return self.expiry_date and self.expiry_date<timezone.now().date()
    @property
    def status_css(self):
        return {"SCHEDULED":"head","IN_PROGRESS":"hod","COMPLETED":"approved","FAILED":"danger","EXPIRED":"muted"}.get(self.status,"draft")
