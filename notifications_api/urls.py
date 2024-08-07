from django.urls import re_path, path
from . import views


urlpatterns = [
    path("notifications/list/<str:type>", views.NotificationView.as_view()),
    path("notifications/<int:id>/", views.NotificationReadDelView.as_view()),
    path("notifications/bulk-read/", views.NotificationBulkReadDelView.as_view()),
    path("notifications/bulk-delete/", views.NotificationBulkReadDelView.as_view()),
]
