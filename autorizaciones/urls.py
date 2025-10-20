from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('qr/', core_views.qr_index, name='qr_index'),
    path('qr/gracias/', core_views.qr_gracias, name='qr_gracias'),
    path('', core_views.panel_index, name='panel'),

    path('v1/patients/', core_views.patients_api, name='patients_api'),
    path('v1/patients/<int:pk>/', core_views.patient_detail_api, name='patient_detail_api'),
    path('v1/attachments/', core_views.attachments_api, name='attachments_api'),

    path('accounts/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
