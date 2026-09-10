from django.urls import path
from . import views
app_name='stock'
urlpatterns=[
    path('',          views.StockDashboardView.as_view(), name='dashboard'),
    path('items/',    views.StockListView.as_view(),       name='list'),
    path('upload/',   views.StockUploadView.as_view(),     name='upload'),
    path('analysis/', views.StockAnalysisView.as_view(),   name='analysis'),
    path('report/',   views.download_report,               name='report'),
]
