
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import PPEItem, PPEType
from .forms import PPEItemForm

class PPEListView(LoginRequiredMixin, ListView):
    model=PPEItem; template_name="ppe/list.html"; context_object_name="items"; paginate_by=30
    def get_queryset(self):
        qs=PPEItem.objects.select_related("ppe_type","issued_to","department")
        st=self.request.GET.get("status",""); pt=self.request.GET.get("type",""); q=self.request.GET.get("q","")
        if st: qs=qs.filter(status=st)
        if pt: qs=qs.filter(ppe_type_id=pt)
        if q: qs=qs.filter(item_code__icontains=q)
        return qs
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw)
        ctx.update({"status_f":self.request.GET.get("status",""),"type_f":self.request.GET.get("type",""),
            "q":self.request.GET.get("q",""),"status_choices":PPEItem.Status.choices,"ppe_types":PPEType.objects.all()})
        return ctx

class PPEDetailView(LoginRequiredMixin, DetailView):
    model=PPEItem; template_name="ppe/detail.html"; context_object_name="item"

class PPECreateView(LoginRequiredMixin, CreateView):
    model=PPEItem; form_class=PPEItemForm; template_name="ppe/form.html"
    success_url=reverse_lazy("ppe:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.created_by=self.request.user; obj.save()
        messages.success(self.request,"PPE item added."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Add PPE Item"; return ctx

class PPEUpdateView(LoginRequiredMixin, UpdateView):
    model=PPEItem; form_class=PPEItemForm; template_name="ppe/form.html"
    success_url=reverse_lazy("ppe:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.updated_by=self.request.user; obj.save()
        messages.success(self.request,"Updated."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Edit PPE Item"; return ctx
