from django.urls import path
from . import views
app_name="assets"
urlpatterns=[
    path("",views.AssetDashboardView.as_view(),name="dashboard"),
    path("list/",views.AssetListView.as_view(),name="list"),
    path("new/",views.AssetCreateView.as_view(),name="create"),
    path("<int:pk>/",views.AssetDetailView.as_view(),name="detail"),
    path("<int:pk>/edit/",views.AssetUpdateView.as_view(),name="edit"),
    path("<int:pk>/allocate/",views.allocate_asset,name="allocate"),
    path("<int:pk>/transfer/",views.transfer_asset,name="transfer"),
    path("<int:pk>/offboard/",views.offboard_asset,name="offboard"),
    path("<int:pk>/status/",views.change_status,name="change_status"),
    path("<int:pk>/note/",views.add_note,name="add_note"),
    path("export/",views.export_assets,name="export"),
]
