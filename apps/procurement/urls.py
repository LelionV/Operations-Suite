from django.urls import path
from . import views

app_name = 'procurement'

urlpatterns = [
    path('',                         views.ProcurementDashboardView.as_view(),  name='dashboard'),
    path('po/<int:po_pk>/open/',     views.ProcurementOrderCreateView.as_view(), name='create_order'),
    path('order/<int:pk>/',          views.ProcurementOrderDetailView.as_view(), name='order_detail'),
    path('order/<int:pk>/edit/',     views.ProcurementOrderUpdateView.as_view(), name='edit_order'),
    path('order/<int:pk>/ordered/',  views.mark_ordered,                         name='mark_ordered'),
    path('export/', views.export_orders_excel, name='export'),
]
