from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginViewCustom.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.panel, name='panel'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/day/<iso>/', views.api_day, name='api_day'),
    path('stats/', views.stats_view, name='stats'),
    path('qr/', views.qr_form, name='qr'),
]
