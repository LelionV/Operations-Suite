
from django.urls import path
from . import views
app_name="nonconformities"
urlpatterns=[
    path("",views.NCListView.as_view(),name="list"),
    path("new/",views.NCCreateView.as_view(),name="create"),
    path("<int:pk>/",views.NCDetailView.as_view(),name="detail"),
    path("<int:pk>/edit/",views.NCUpdateView.as_view(),name="edit"),
]
