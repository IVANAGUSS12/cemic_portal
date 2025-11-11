
from django.contrib import admin
from .models import PatientSubmission, Profile
@admin.register(PatientSubmission)
class PatientSubmissionAdmin(admin.ModelAdmin):
    list_display=("id","nombre","dni","cobertura","medico","sector","fecha_cx","estado","timestamp")
    list_filter=("sector","estado","cobertura","medico")
    search_fields=("nombre","dni","cobertura","medico")
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=("user","rol","telefono","centro")
    list_filter=("rol",)
    search_fields=("user__username","user__email")
