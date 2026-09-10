
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Incident

class IncidentListView(LoginRequiredMixin, ListView):
    model=Incident; template_name="incidents/list.html"
    context_object_name="incidentss"; paginate_by=25
    def get_queryset(self):
        qs=Incident.objects.all()
        q=self.request.GET.get("q","")
        if q: qs=qs.filter(title__icontains=q) if hasattr(Incident,"title") else qs
        return qs
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw); ctx["q"]=self.request.GET.get("q",""); return ctx

class IncidentDetailView(LoginRequiredMixin, DetailView):
    model=Incident; template_name="incidents/detail.html"; context_object_name="incident"

class IncidentCreateView(LoginRequiredMixin, CreateView):
    model=Incident; fields="__all__"; template_name="incidents/form.html"
    success_url=reverse_lazy("incidents:list")
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Add Incidents"; return ctx

class IncidentUpdateView(LoginRequiredMixin, UpdateView):
    model=Incident; fields="__all__"; template_name="incidents/form.html"
    success_url=reverse_lazy("incidents:list")
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Edit Incidents"; return ctx
