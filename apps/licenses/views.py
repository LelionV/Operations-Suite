
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import License

class LicenseListView(LoginRequiredMixin, ListView):
    model=License; template_name="licenses/list.html"
    context_object_name="licensess"; paginate_by=25
    def get_queryset(self):
        qs=License.objects.all()
        q=self.request.GET.get("q","")
        if q: qs=qs.filter(title__icontains=q) if hasattr(License,"title") else qs
        return qs
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw); ctx["q"]=self.request.GET.get("q",""); return ctx

class LicenseDetailView(LoginRequiredMixin, DetailView):
    model=License; template_name="licenses/detail.html"; context_object_name="license"

class LicenseCreateView(LoginRequiredMixin, CreateView):
    model=License; fields="__all__"; template_name="licenses/form.html"
    success_url=reverse_lazy("licenses:list")
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Add Licenses"; return ctx

class LicenseUpdateView(LoginRequiredMixin, UpdateView):
    model=License; fields="__all__"; template_name="licenses/form.html"
    success_url=reverse_lazy("licenses:list")
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Edit Licenses"; return ctx
