
from django.urls import path
from . import views
app_name="risks"
urlpatterns=[
    path("",views.RiskListView.as_view(),name="list"),
    path("new/",views.RiskCreateView.as_view(),name="create"),
    path("<int:pk>/",views.RiskDetailView.as_view(),name="detail"),
    path("<int:pk>/edit/",views.RiskUpdateView.as_view(),name="edit"),
]
