
from django.urls import path
from . import views
from .api import views as api_views

app_name = "visitors"

urlpatterns = [
    # Web views
    path("",                          views.VisitorDashboardView.as_view(), name="dashboard"),
    path("list/",                     views.AppointmentListView.as_view(),  name="list"),
    path("new/",                      views.AppointmentCreateView.as_view(),name="create"),
    path("<int:pk>/",                 views.AppointmentDetailView.as_view(),name="detail"),
    path("<int:pk>/edit/",            views.AppointmentUpdateView.as_view(),name="edit"),
    path("<int:pk>/arrive/",          views.mark_arrived,                   name="arrive"),
    path("<int:pk>/status/",          views.update_status,                  name="update_status"),
    path("whatsapp/",                 views.WhatsAppConfigView.as_view(),   name="whatsapp_config"),
    path("whatsapp/test/",            views.test_whatsapp,                  name="test_whatsapp"),

    # REST API — mobile
    path("api/appointments/",             api_views.appointment_list_create, name="api_list"),
    path("api/appointments/<str:ref>/",   api_views.appointment_detail,      name="api_detail"),
    path("api/appointments/<str:ref>/arrive/", api_views.appointment_arrive, name="api_arrive"),
    path("api/appointments/<str:ref>/status/", api_views.appointment_status, name="api_status"),
    path("api/today/",                    api_views.today_appointments,      name="api_today"),
    path("api/users/",                    api_views.user_list,               name="api_users"),
    path("api/departments/",              api_views.department_list,         name="api_departments"),
    path("api/docs/",                     views.api_docs,                    name="api_docs"),
]
