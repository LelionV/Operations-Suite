
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import EnvironmentalAspect

class EnvironmentalAspectListView(LoginRequiredMixin, ListView):
    model=EnvironmentalAspect; template_name="environmental/list.html"
    context_object_name="environmentals"; paginate_by=25
    def get_queryset(self):
        qs=EnvironmentalAspect.objects.all()
        q=self.request.GET.get("q","")
        if q: qs=qs.filter(title__icontains=q) if hasattr(EnvironmentalAspect,"title") else qs
        return qs
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw); ctx["q"]=self.request.GET.get("q",""); return ctx

class EnvironmentalAspectDetailView(LoginRequiredMixin, DetailView):
    model=EnvironmentalAspect; template_name="environmental/detail.html"; context_object_name="environmental"

class EnvironmentalAspectCreateView(LoginRequiredMixin, CreateView):
    model=EnvironmentalAspect; fields="__all__"; template_name="environmental/form.html"
    success_url=reverse_lazy("environmental:list")
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Add Environmental Aspects"; return ctx

class EnvironmentalAspectUpdateView(LoginRequiredMixin, UpdateView):
    model=EnvironmentalAspect; fields="__all__"; template_name="environmental/form.html"
    success_url=reverse_lazy("environmental:list")
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Edit Environmental Aspects"; return ctx
