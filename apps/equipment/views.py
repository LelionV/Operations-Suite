
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Equipment, EquipmentCategory
from .forms import EquipmentForm

class EquipmentListView(LoginRequiredMixin, ListView):
    model=Equipment; template_name="equipment/list.html"; context_object_name="items"; paginate_by=30
    def get_queryset(self):
        qs=Equipment.objects.select_related("category","department","site","responsible_person")
        cat=self.request.GET.get("cat",""); st=self.request.GET.get("status",""); q=self.request.GET.get("q","")
        safety=self.request.GET.get("safety","")
        if cat: qs=qs.filter(category_id=cat)
        if st: qs=qs.filter(status=st)
        if q: qs=qs.filter(name__icontains=q)|qs.filter(asset_id__icontains=q)
        if safety: qs=qs.filter(is_safety_critical=True)
        return qs
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw)
        ctx.update({"cat_f":self.request.GET.get("cat",""),"status_f":self.request.GET.get("status",""),
            "q":self.request.GET.get("q",""),"safety_f":self.request.GET.get("safety",""),
            "categories":EquipmentCategory.objects.all(),"status_choices":Equipment.Status.choices})
        return ctx

class EquipmentDetailView(LoginRequiredMixin, DetailView):
    model=Equipment; template_name="equipment/detail.html"; context_object_name="item"

class EquipmentCreateView(LoginRequiredMixin, CreateView):
    model=Equipment; form_class=EquipmentForm; template_name="equipment/form.html"
    success_url=reverse_lazy("equipment:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.created_by=self.request.user; obj.save()
        messages.success(self.request,f"Equipment {obj.asset_id} added."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Add Equipment"; return ctx

class EquipmentUpdateView(LoginRequiredMixin, UpdateView):
    model=Equipment; form_class=EquipmentForm; template_name="equipment/form.html"
    success_url=reverse_lazy("equipment:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.updated_by=self.request.user; obj.save()
        messages.success(self.request,"Updated."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Edit Equipment"; return ctx
