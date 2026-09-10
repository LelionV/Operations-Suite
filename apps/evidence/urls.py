
from django.urls import path
from . import views
app_name="evidence"
urlpatterns=[
    path("",views.EvidenceListView.as_view(),name="list"),
    path("upload/",views.EvidenceUploadView.as_view(),name="upload"),
]
