
from django.urls import path
from . import views
app_name="inspections"
urlpatterns=[
    path("",views.InspectionListView.as_view(),name="list"),
    path("new/",views.InspectionCreateView.as_view(),name="create"),
    path("<int:pk>/",views.InspectionDetailView.as_view(),name="detail"),
    path("<int:pk>/edit/",views.InspectionUpdateView.as_view(),name="edit"),
    path("<int:pk>/complete/",views.complete_inspection,name="complete"),
]
