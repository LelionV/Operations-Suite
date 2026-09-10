
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Action
from .forms import ActionForm

class ActionListView(LoginRequiredMixin, ListView):
    model=Action; template_name="actions/list.html"; context_object_name="actions"; paginate_by=25
    def get_queryset(self):
        qs=Action.objects.select_related("owner","department")
        st=self.request.GET.get("status",""); at=self.request.GET.get("type",""); q=self.request.GET.get("q","")
        if st: qs=qs.filter(status=st)
        if at: qs=qs.filter(action_type=at)
        if q: qs=qs.filter(title__icontains=q)
        return qs
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw)
        ctx.update({"status_f":self.request.GET.get("status",""),"type_f":self.request.GET.get("type",""),
            "q":self.request.GET.get("q",""),"status_choices":Action.Status.choices,
            "type_choices":Action.ActionType.choices})
        all_a=Action.objects.all()
        ctx["open_count"]=all_a.filter(status__in=["OPEN","IN_PROGRESS"]).count()
        ctx["overdue_count"]=sum(1 for a in all_a if a.is_overdue)
        return ctx

class ActionDetailView(LoginRequiredMixin, DetailView):
    model=Action; template_name="actions/detail.html"; context_object_name="action"

class ActionCreateView(LoginRequiredMixin, CreateView):
    model=Action; form_class=ActionForm; template_name="actions/form.html"
    success_url=reverse_lazy("actions:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.created_by=self.request.user; obj.save()
        messages.success(self.request,"Action created."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Add Action"; return ctx

class ActionUpdateView(LoginRequiredMixin, UpdateView):
    model=Action; form_class=ActionForm; template_name="actions/form.html"
    success_url=reverse_lazy("actions:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.updated_by=self.request.user; obj.save()
        messages.success(self.request,"Updated."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Edit Action"; return ctx
