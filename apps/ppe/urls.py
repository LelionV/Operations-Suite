
from django.urls import path
from . import views
app_name="ppe"
urlpatterns=[
    path("",views.PPEListView.as_view(),name="list"),
    path("new/",views.PPECreateView.as_view(),name="create"),
    path("<int:pk>/",views.PPEDetailView.as_view(),name="detail"),
    path("<int:pk>/edit/",views.PPEUpdateView.as_view(),name="edit"),
]
