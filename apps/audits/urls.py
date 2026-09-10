
from django.urls import path
from . import views
app_name="audits"
urlpatterns=[
    path("",views.AuditListView.as_view(),name="list"),
    path("new/",views.AuditCreateView.as_view(),name="create"),
    path("<int:pk>/",views.AuditDetailView.as_view(),name="detail"),
    path("<int:pk>/edit/",views.AuditUpdateView.as_view(),name="edit"),
]
