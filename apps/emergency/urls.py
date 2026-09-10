
from django.urls import path
from . import views
app_name="emergency"
urlpatterns=[path("",views.EmergencyProcedureListView.as_view(),name="list")]
