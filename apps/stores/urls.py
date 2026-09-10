from django.urls import path
from . import views

app_name = 'stores'

urlpatterns = [
    path('',                     views.StoresDashboardView.as_view(), name='dashboard'),
    path('received/',            views.ReceivedItemsView.as_view(),   name='received_list'),
    path('grn/po/<int:po_pk>/',  views.GRNCreateView.as_view(),       name='grn_create'),
    path('grn/<int:pk>/',        views.GRNDetailView.as_view(),        name='grn_detail'),
    path('grn/<int:pk>/update/', views.GRNUpdateView.as_view(),        name='grn_update'),
]
