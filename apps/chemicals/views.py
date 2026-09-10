
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Chemical

class ChemicalListView(LoginRequiredMixin, ListView):
    model=Chemical; template_name="chemicals/list.html"
    context_object_name="chemicalss"; paginate_by=25
    def get_queryset(self):
        qs=Chemical.objects.all()
        q=self.request.GET.get("q","")
        if q: qs=qs.filter(title__icontains=q) if hasattr(Chemical,"title") else qs
        return qs
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw); ctx["q"]=self.request.GET.get("q",""); return ctx

class ChemicalDetailView(LoginRequiredMixin, DetailView):
    model=Chemical; template_name="chemicals/detail.html"; context_object_name="chemical"

class ChemicalCreateView(LoginRequiredMixin, CreateView):
    model=Chemical; fields="__all__"; template_name="chemicals/form.html"
    success_url=reverse_lazy("chemicals:list")
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Add Chemicals"; return ctx

class ChemicalUpdateView(LoginRequiredMixin, UpdateView):
    model=Chemical; fields="__all__"; template_name="chemicals/form.html"
    success_url=reverse_lazy("chemicals:list")
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Edit Chemicals"; return ctx
