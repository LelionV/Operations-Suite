
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Contractor

class ContractorListView(LoginRequiredMixin, ListView):
    model=Contractor; template_name="contractors/list.html"
    context_object_name="contractorss"; paginate_by=25
    def get_queryset(self):
        qs=Contractor.objects.all()
        q=self.request.GET.get("q","")
        if q: qs=qs.filter(title__icontains=q) if hasattr(Contractor,"title") else qs
        return qs
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw); ctx["q"]=self.request.GET.get("q",""); return ctx

class ContractorDetailView(LoginRequiredMixin, DetailView):
    model=Contractor; template_name="contractors/detail.html"; context_object_name="contractor"

class ContractorCreateView(LoginRequiredMixin, CreateView):
    model=Contractor; fields="__all__"; template_name="contractors/form.html"
    success_url=reverse_lazy("contractors:list")
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Add Contractors"; return ctx

class ContractorUpdateView(LoginRequiredMixin, UpdateView):
    model=Contractor; fields="__all__"; template_name="contractors/form.html"
    success_url=reverse_lazy("contractors:list")
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Edit Contractors"; return ctx
