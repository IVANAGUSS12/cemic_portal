from django import forms
from .models import PatientSubmission

class QRForm(forms.ModelForm):
    class Meta:
        model = PatientSubmission
        fields = ['nombre','dni','email','telefono','cobertura','medico','fecha_cx','sector',
                  'observaciones','orden_medica','dni_file','credencial','orden_materiales']

class FilterForm(forms.Form):
    q = forms.CharField(required=False, label='Buscar')
    desde = forms.DateField(required=False, widget=forms.DateInput(attrs={'type':'date'}))
    hasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'type':'date'}))
    cobertura = forms.CharField(required=False)
    medico = forms.CharField(required=False)
    estado = forms.CharField(required=False)
    sector = forms.CharField(required=False)
