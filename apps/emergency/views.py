
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import EmergencyContact, EmergencyProcedure
class EmergencyProcedureListView(LoginRequiredMixin, ListView):
    model=EmergencyProcedure; template_name="emergency/list.html"; context_object_name="procedures"
    def get_context_data(self,**kw):
        ctx=super().get_context_data(**kw)
        ctx["contacts"]=EmergencyContact.objects.filter(is_active=True).order_by("order","name"); return ctx
