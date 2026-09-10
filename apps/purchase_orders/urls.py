from django.urls import path
from . import views

app_name = 'purchase_orders'

urlpatterns = [
    path('',                        views.POListView.as_view(),   name='list'),
    path('new/',                    views.POCreateView.as_view(), name='create'),
    path('<int:pk>/',               views.PODetailView.as_view(), name='detail'),
    path('<int:pk>/edit/',          views.POUpdateView.as_view(), name='edit'),
    path('<int:pk>/submit/',        views.submit_po,              name='submit'),
    path('<int:pk>/hod-approve/',   views.hod_approve_po,         name='hod_approve'),
    path('<int:pk>/head-approve/',  views.head_approve_po,        name='head_approve'),
    path('<int:pk>/reject/',        views.reject_po,              name='reject'),
    path('<int:pk>/reject-items/',  views.reject_items,           name='reject_items'),
    path('<int:pk>/cancel/',        views.cancel_po,              name='cancel'),

    path('<int:pk>/sign/', views.save_signature, name='save_signature'),
    path('<int:pk>/pdf/',  views.export_po_pdf,  name='pdf'),
]
