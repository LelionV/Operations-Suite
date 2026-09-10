
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import RiskRegister
from .forms import RiskForm

class RiskListView(LoginRequiredMixin, ListView):
    model=RiskRegister; template_name="risks/list.html"; context_object_name="risks"; paginate_by=25
    def get_queryset(self):
        qs=RiskRegister.objects.select_related("owner","department","site")
        status=self.request.GET.get("status",""); dept=self.request.GET.get("dept",""); q=self.request.GET.get("q","")
        if status: qs=qs.filter(status=status)
        if dept: qs=qs.filter(department_id=dept)
        if q: qs=qs.filter(title__icontains=q)
        return qs
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw)
        from apps.departments.models import Department
        ctx.update({"status_f":self.request.GET.get("status",""),"dept_f":self.request.GET.get("dept",""),
            "q":self.request.GET.get("q",""),"status_choices":RiskRegister.Status.choices,
            "departments":Department.objects.all()})
        all_risks=list(RiskRegister.objects.all())
        ctx["critical"]=sum(1 for r in all_risks if r.risk_rating=="CRITICAL")
        ctx["high"]=sum(1 for r in all_risks if r.risk_rating=="HIGH")
        ctx["medium"]=sum(1 for r in all_risks if r.risk_rating=="MEDIUM")
        ctx["low"]=sum(1 for r in all_risks if r.risk_rating=="LOW")
        return ctx

class RiskDetailView(LoginRequiredMixin, DetailView):
    model=RiskRegister; template_name="risks/detail.html"; context_object_name="risk"

class RiskCreateView(LoginRequiredMixin, CreateView):
    model=RiskRegister; form_class=RiskForm; template_name="risks/form.html"
    success_url=reverse_lazy("risks:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.created_by=self.request.user; obj.save()
        messages.success(self.request,"Risk added."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Add Risk"; return ctx

class RiskUpdateView(LoginRequiredMixin, UpdateView):
    model=RiskRegister; form_class=RiskForm; template_name="risks/form.html"
    success_url=reverse_lazy("risks:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.updated_by=self.request.user; obj.save()
        messages.success(self.request,"Updated."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Edit Risk"; return ctx
