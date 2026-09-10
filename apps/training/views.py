
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import TrainingRecord

class TrainingRecordListView(LoginRequiredMixin, ListView):
    model=TrainingRecord; template_name="training/list.html"
    context_object_name="trainings"; paginate_by=25
    def get_queryset(self):
        qs=TrainingRecord.objects.all()
        q=self.request.GET.get("q","")
        if q: qs=qs.filter(title__icontains=q) if hasattr(TrainingRecord,"title") else qs
        return qs
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw); ctx["q"]=self.request.GET.get("q",""); return ctx

class TrainingRecordDetailView(LoginRequiredMixin, DetailView):
    model=TrainingRecord; template_name="training/detail.html"; context_object_name="training"

class TrainingRecordCreateView(LoginRequiredMixin, CreateView):
    model=TrainingRecord; fields="__all__"; template_name="training/form.html"
    success_url=reverse_lazy("training:list")
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Add Training Records"; return ctx

class TrainingRecordUpdateView(LoginRequiredMixin, UpdateView):
    model=TrainingRecord; fields="__all__"; template_name="training/form.html"
    success_url=reverse_lazy("training:list")
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Edit Training Records"; return ctx
