
from django.urls import path
from . import views
app_name="compliance"
urlpatterns=[
    path("",views.ComplianceListView.as_view(),name="list"),
    path("new/",views.ComplianceCreateView.as_view(),name="create"),
    path("<int:pk>/",views.ComplianceDetailView.as_view(),name="detail"),
    path("<int:pk>/edit/",views.ComplianceUpdateView.as_view(),name="edit"),
]
