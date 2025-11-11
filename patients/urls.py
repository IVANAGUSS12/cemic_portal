from django.urls import path
from . import views

urlpatterns = [
    path("", views.panel, name="panel"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("day/<str:iso>/", views.api_day, name="api_day"),
    path("stats/", views.stats_view, name="stats"),
    path("qr/", views.qr_form, name="qr_form"),
]
