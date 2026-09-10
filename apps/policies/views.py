
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from .models import PolicyDocument, PolicyAcknowledgement
from .forms import PolicyForm

class PolicyListView(LoginRequiredMixin, ListView):
    model=PolicyDocument; template_name="policies/list.html"; context_object_name="docs"; paginate_by=25
    def get_queryset(self):
        qs=PolicyDocument.objects.all()
        dt=self.request.GET.get("doc_type",""); st=self.request.GET.get("status",""); q=self.request.GET.get("q","")
        if dt: qs=qs.filter(doc_type=dt)
        if st: qs=qs.filter(status=st)
        if q: qs=qs.filter(title__icontains=q)
        return qs
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw)
        ctx.update({"dt_f":self.request.GET.get("doc_type",""),"st_f":self.request.GET.get("status",""),
            "q":self.request.GET.get("q",""),"doc_type_choices":PolicyDocument.DocType.choices,
            "status_choices":PolicyDocument.Status.choices})
        return ctx

class PolicyDetailView(LoginRequiredMixin, DetailView):
    model=PolicyDocument; template_name="policies/detail.html"; context_object_name="doc"
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw)
        ctx["user_acked"]=PolicyAcknowledgement.objects.filter(policy=self.object,employee=self.request.user).exists()
        ctx["ack_count"]=self.object.acknowledgements.count()
        ctx["acks"]=self.object.acknowledgements.select_related("employee")
        return ctx

class PolicyCreateView(LoginRequiredMixin, CreateView):
    model=PolicyDocument; form_class=PolicyForm; template_name="policies/form.html"
    success_url=reverse_lazy("policies:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.created_by=self.request.user; obj.save()
        form.save_m2m(); messages.success(self.request,"Document created."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Add Document"; return ctx

class PolicyUpdateView(LoginRequiredMixin, UpdateView):
    model=PolicyDocument; form_class=PolicyForm; template_name="policies/form.html"
    success_url=reverse_lazy("policies:list")
    def form_valid(self,form):
        obj=form.save(commit=False); obj.updated_by=self.request.user; obj.save()
        form.save_m2m(); messages.success(self.request,"Updated."); return redirect(self.success_url)
    def get_context_data(self,**kw): ctx=super().get_context_data(**kw); ctx["page_title"]="Edit Document"; return ctx

@login_required
def acknowledge_policy(request, pk):
    doc=get_object_or_404(PolicyDocument, pk=pk)
    if request.method=="POST":
        PolicyAcknowledgement.objects.get_or_create(policy=doc, employee=request.user)
        messages.success(request, f"You have acknowledged: {doc.title}")
    return redirect(reverse("policies:detail", kwargs={"pk":pk}))
