
from django.urls import path
from . import views
app_name="chemicals"
urlpatterns=[
    path("",views.ChemicalListView.as_view(),name="list"),
    path("new/",views.ChemicalCreateView.as_view(),name="create"),
    path("<int:pk>/",views.ChemicalDetailView.as_view(),name="detail"),
    path("<int:pk>/edit/",views.ChemicalUpdateView.as_view(),name="edit"),
]
