
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from .models import Inspection
from .forms import InspectionForm

class InspectionListView(LoginRequiredMixin, ListView):
    model=Inspection; template_name="inspections/list.html"; context_object_name="inspections"; paginate_by=25
    def get_queryset(self):
        qs=Inspection.objects.select_related("inspector","department","site","equipment")
        st=self.request.GET.get("status",""); it=self.request.GET.get("type",""); q=self.request.GET.get("q","")
        if st: qs=qs.filter(status=st)
        if it: qs=qs.filter(inspection_type=it)
        if q: qs=qs.filter(title__icontains=q)
        return qs
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw)
        ctx.update({"status_f":self.request.GET.get("status",""),"type_f":self.request.GET.get("type",""),
            "q":self.request.GET.get("q",""),"status_choices":Inspection.Status.choices,
            "type_choices":Inspection.InspectionType.choices})
        return ctx

class InspectionDetailView(LoginRequiredMixin, DetailView):
    model=Inspection; template_name="inspections/detail.html"; context_object_name="inspection"
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw); ctx["results"]=self.object.results.select_related("checklist_item"); return ctx

class InspectionCreateView(LoginRequiredMixin, CreateView):
    model=Inspection; form_class=InspectionForm; template_name="inspections/form.html"
    success_url=reverse_lazy("inspections:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.created_by=self.request.user; obj.save()
        messages.success(self.request,"Inspection scheduled."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Schedule Inspection"; return ctx

class InspectionUpdateView(LoginRequiredMixin, UpdateView):
    model=Inspection; form_class=InspectionForm; template_name="inspections/form.html"
    success_url=reverse_lazy("inspections:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.updated_by=self.request.user; obj.save()
        messages.success(self.request,"Updated."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Edit Inspection"; return ctx

@login_required
def complete_inspection(request, pk):
    insp=get_object_or_404(Inspection, pk=pk)
    if request.method=="POST":
        insp.status="COMPLETED"; insp.completed_date=timezone.now().date()
        insp.overall_result=request.POST.get("overall_result","PASS")
        insp.summary=request.POST.get("summary",""); insp.defects_found=request.POST.get("defects_found","")
        nid=request.POST.get("next_inspection_date","")
        if nid: insp.next_inspection_date=nid
        insp.updated_by=request.user; insp.save()
        messages.success(request, "Inspection completed.")
    return redirect(reverse("inspections:detail", kwargs={"pk":pk}))
