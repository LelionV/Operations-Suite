from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('upload/', views.QBUploadView.as_view(), name='upload'),
    path('items/', views.QBItemListView.as_view(), name='item_list'),
    path('items/search/', views.qb_item_search, name='item_search'),
]
