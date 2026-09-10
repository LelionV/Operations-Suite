
from django.urls import path
from . import views
app_name="licenses"
urlpatterns=[
    path("",views.LicenseListView.as_view(),name="list"),
    path("new/",views.LicenseCreateView.as_view(),name="create"),
    path("<int:pk>/",views.LicenseDetailView.as_view(),name="detail"),
    path("<int:pk>/edit/",views.LicenseUpdateView.as_view(),name="edit"),
]
