
from django.urls import path
from . import views
app_name="policies"
urlpatterns=[
    path("",views.PolicyListView.as_view(),name="list"),
    path("new/",views.PolicyCreateView.as_view(),name="create"),
    path("<int:pk>/",views.PolicyDetailView.as_view(),name="detail"),
    path("<int:pk>/edit/",views.PolicyUpdateView.as_view(),name="edit"),
    path("<int:pk>/acknowledge/",views.acknowledge_policy,name="acknowledge"),
]
