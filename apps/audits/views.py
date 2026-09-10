
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Audit

class AuditListView(LoginRequiredMixin, ListView):
    model=Audit; template_name="audits/list.html"
    context_object_name="auditss"; paginate_by=25
    def get_queryset(self):
        qs=Audit.objects.all()
        q=self.request.GET.get("q","")
        if q: qs=qs.filter(title__icontains=q) if hasattr(Audit,"title") else qs
        return qs
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw); ctx["q"]=self.request.GET.get("q",""); return ctx

class AuditDetailView(LoginRequiredMixin, DetailView):
    model=Audit; template_name="audits/detail.html"; context_object_name="audit"

class AuditCreateView(LoginRequiredMixin, CreateView):
    model=Audit; fields="__all__"; template_name="audits/form.html"
    success_url=reverse_lazy("audits:list")
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Add Audits"; return ctx

class AuditUpdateView(LoginRequiredMixin, UpdateView):
    model=Audit; fields="__all__"; template_name="audits/form.html"
    success_url=reverse_lazy("audits:list")
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Edit Audits"; return ctx
