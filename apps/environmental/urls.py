
from django.urls import path
from . import views
app_name="environmental"
urlpatterns=[
    path("",views.EnvironmentalAspectListView.as_view(),name="list"),
    path("new/",views.EnvironmentalAspectCreateView.as_view(),name="create"),
    path("<int:pk>/",views.EnvironmentalAspectDetailView.as_view(),name="detail"),
    path("<int:pk>/edit/",views.EnvironmentalAspectUpdateView.as_view(),name="edit"),
]
