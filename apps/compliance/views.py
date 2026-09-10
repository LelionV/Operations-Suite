
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import ComplianceRequirement
from .forms import ComplianceForm

class ComplianceListView(LoginRequiredMixin, ListView):
    model=ComplianceRequirement; template_name="compliance/list.html"; context_object_name="items"; paginate_by=30
    def get_queryset(self):
        qs=ComplianceRequirement.objects.select_related("owner")
        cat=self.request.GET.get("cat",""); status=self.request.GET.get("status",""); q=self.request.GET.get("q","")
        if cat: qs=qs.filter(category=cat)
        if status: qs=qs.filter(status=status)
        if q: qs=qs.filter(title__icontains=q)
        return qs
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw)
        ctx.update({"cat_f":self.request.GET.get("cat",""),"status_f":self.request.GET.get("status",""),
            "q":self.request.GET.get("q",""),"category_choices":ComplianceRequirement.Category.choices,
            "status_choices":ComplianceRequirement.Status.choices})
        return ctx

class ComplianceDetailView(LoginRequiredMixin, DetailView):
    model=ComplianceRequirement; template_name="compliance/detail.html"; context_object_name="item"

class ComplianceCreateView(LoginRequiredMixin, CreateView):
    model=ComplianceRequirement; form_class=ComplianceForm; template_name="compliance/form.html"
    success_url=reverse_lazy("compliance:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.created_by=self.request.user; obj.save()
        messages.success(self.request,"Requirement added."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Add Requirement"; return ctx

class ComplianceUpdateView(LoginRequiredMixin, UpdateView):
    model=ComplianceRequirement; form_class=ComplianceForm; template_name="compliance/form.html"
    success_url=reverse_lazy("compliance:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.updated_by=self.request.user; obj.save()
        messages.success(self.request,"Updated."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Edit Requirement"; return ctx
