
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import NonConformity
from .forms import NCForm

class NCListView(LoginRequiredMixin, ListView):
    model=NonConformity; template_name="nonconformities/list.html"; context_object_name="ncs"; paginate_by=25
    def get_queryset(self):
        qs=NonConformity.objects.select_related("responsible_person","department")
        st=self.request.GET.get("status",""); sv=self.request.GET.get("severity",""); q=self.request.GET.get("q","")
        if st: qs=qs.filter(status=st)
        if sv: qs=qs.filter(severity=sv)
        if q: qs=qs.filter(title__icontains=q)
        return qs
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw)
        ctx.update({"status_f":self.request.GET.get("status",""),"severity_f":self.request.GET.get("severity",""),
            "q":self.request.GET.get("q",""),"status_choices":NonConformity.Status.choices,
            "severity_choices":NonConformity.Severity.choices})
        all_nc=NonConformity.objects.all()
        ctx["open_count"]=all_nc.filter(status="OPEN").count()
        ctx["overdue_count"]=sum(1 for n in all_nc if n.is_overdue)
        return ctx

class NCDetailView(LoginRequiredMixin, DetailView):
    model=NonConformity; template_name="nonconformities/detail.html"; context_object_name="nc"

class NCCreateView(LoginRequiredMixin, CreateView):
    model=NonConformity; form_class=NCForm; template_name="nonconformities/form.html"
    success_url=reverse_lazy("nonconformities:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.created_by=self.request.user; obj.save()
        messages.success(self.request,"Non-conformity recorded."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Record Non-Conformity"; return ctx

class NCUpdateView(LoginRequiredMixin, UpdateView):
    model=NonConformity; form_class=NCForm; template_name="nonconformities/form.html"
    success_url=reverse_lazy("nonconformities:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.updated_by=self.request.user; obj.save()
        messages.success(self.request,"Updated."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Edit NC"; return ctx
