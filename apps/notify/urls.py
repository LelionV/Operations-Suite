from django.urls import path
from . import views
app_name="notify"
urlpatterns=[
    path("",views.notification_list,name="list"),
    path("unread/",views.unread_count,name="unread"),
    path("<int:pk>/read/",views.mark_read,name="mark_read"),
    path("read-all/",views.mark_all_read,name="mark_all_read"),
]
