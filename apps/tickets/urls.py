from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('',                            views.TicketDashboardView.as_view(), name='dashboard'),
    path('list/',                       views.TicketListView.as_view(),      name='list'),
    path('new/',                        views.TicketCreateView.as_view(),    name='create'),
    path('<int:pk>/',                   views.TicketDetailView.as_view(),    name='detail'),
    path('<int:pk>/edit/',              views.TicketUpdateView.as_view(),    name='edit'),
    path('<int:pk>/status/',            views.update_status,                 name='update_status'),
    path('<int:pk>/comment/',           views.add_comment,                   name='add_comment'),
    path('<int:pk>/close/',             views.close_ticket,                  name='close'),
    path('<int:ticket_id>/file/<int:file_id>/', views.download_attachment,   name='download_file'),
]
