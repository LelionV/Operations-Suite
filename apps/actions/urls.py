
from django.urls import path
from . import views
app_name="actions"
urlpatterns=[
    path("",views.ActionListView.as_view(),name="list"),
    path("new/",views.ActionCreateView.as_view(),name="create"),
    path("<int:pk>/",views.ActionDetailView.as_view(),name="detail"),
    path("<int:pk>/edit/",views.ActionUpdateView.as_view(),name="edit"),
]
