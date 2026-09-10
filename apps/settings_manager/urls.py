from django.urls import path
from . import views

app_name = 'settings_manager'

urlpatterns = [
    path('email/',      views.EmailSettingsView.as_view(), name='email'),
    path('test-email/', views.test_email,                  name='test_email'),
]
