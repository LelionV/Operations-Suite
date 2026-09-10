
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import MaintenanceRecord
from .forms import MaintenanceForm

class MaintenanceListView(LoginRequiredMixin, ListView):
    model=MaintenanceRecord; template_name="maintenance/list.html"; context_object_name="records"; paginate_by=25
    def get_queryset(self):
        qs=MaintenanceRecord.objects.select_related("equipment","assigned_to")
        st=self.request.GET.get("status",""); mt=self.request.GET.get("type",""); q=self.request.GET.get("q","")
        if st: qs=qs.filter(status=st)
        if mt: qs=qs.filter(maintenance_type=mt)
        if q: qs=qs.filter(title__icontains=q)
        return qs
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw)
        ctx.update({"status_f":self.request.GET.get("status",""),"type_f":self.request.GET.get("type",""),
            "q":self.request.GET.get("q",""),"status_choices":MaintenanceRecord.Status.choices,
            "type_choices":MaintenanceRecord.MaintenanceType.choices})
        return ctx

class MaintenanceDetailView(LoginRequiredMixin, DetailView):
    model=MaintenanceRecord; template_name="maintenance/detail.html"; context_object_name="record"

class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    model=MaintenanceRecord; form_class=MaintenanceForm; template_name="maintenance/form.html"
    success_url=reverse_lazy("maintenance:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.created_by=self.request.user; obj.save()
        messages.success(self.request,"Maintenance record created."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Add Maintenance"; return ctx

class MaintenanceUpdateView(LoginRequiredMixin, UpdateView):
    model=MaintenanceRecord; form_class=MaintenanceForm; template_name="maintenance/form.html"
    success_url=reverse_lazy("maintenance:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.updated_by=self.request.user; obj.save()
        messages.success(self.request,"Updated."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Edit Maintenance"; return ctx
