
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import EvidenceFile
from django import forms
class EvidenceListView(LoginRequiredMixin, ListView):
    model=EvidenceFile; template_name="evidence/list.html"; context_object_name="files"; paginate_by=30
    def get_queryset(self):
        qs=EvidenceFile.objects.select_related("uploaded_by")
        q=self.request.GET.get("q",""); dt=self.request.GET.get("doc_type",""); mod=self.request.GET.get("module","")
        if q: qs=qs.filter(title__icontains=q)
        if dt: qs=qs.filter(doc_type=dt)
        if mod: qs=qs.filter(module=mod)
        return qs
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw)
        ctx.update({"q":self.request.GET.get("q",""),"dt_f":self.request.GET.get("doc_type",""),
            "mod_f":self.request.GET.get("module",""),"doc_type_choices":EvidenceFile.DocType.choices}); return ctx
class EvidenceUploadView(LoginRequiredMixin, CreateView):
    model=EvidenceFile; fields=["title","doc_type","file","description","related_to","module","tags"]
    template_name="evidence/form.html"; success_url=reverse_lazy("evidence:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.uploaded_by=self.request.user; obj.save()
        from django.contrib import messages; messages.success(self.request,"File uploaded.")
        from django.shortcuts import redirect; return redirect(self.success_url)
