
from django.urls import path
from . import views
app_name="training"
urlpatterns=[
    path("",views.TrainingRecordListView.as_view(),name="list"),
    path("new/",views.TrainingRecordCreateView.as_view(),name="create"),
    path("<int:pk>/",views.TrainingRecordDetailView.as_view(),name="detail"),
    path("<int:pk>/edit/",views.TrainingRecordUpdateView.as_view(),name="edit"),
]
