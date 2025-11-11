
from django.db import models
from django.contrib.auth.models import User
SECTORES=[('TRAUMATOLOGIA','Traumatología'),('HEMODINAMIA','Hemodinamia'),('CIRUGIA_GENERAL','Cirugía General'),('OTORRINO','Otorrino'),('CIRUGIA_PLASTICA','Cirugía Plástica'),('CARDIOLOGIA','Cardiología'),('UROLOGIA','Urología')]
ESTADOS=[('Pendiente','Pendiente'),('Autorizado','Autorizado'),('Falta materiales','Falta materiales'),('Solicitado','Solicitado'),('Materiales OK','Materiales OK'),('Autorizado material pendiente','Autorizado material pendiente'),('rechazado por cobertura','Rechazado por cobertura')]
PRESUP=[('','Sin presupuesto'),('En curso','En curso'),('Aprobado','Aprobado')]
class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    telefono=models.CharField(max_length=40,blank=True)
    centro=models.CharField(max_length=80,blank=True)
    avatar=models.ImageField(upload_to='avatars/',blank=True,null=True)
    rol=models.CharField(max_length=16,choices=[('operador','operador'),('admin','admin')],default='operador')
    def __str__(self): return f"Perfil {self.user.username}"
class PatientSubmission(models.Model):
    timestamp=models.DateTimeField(auto_now_add=True)
    nombre=models.CharField(max_length=120)
    dni=models.CharField(max_length=32)
    email=models.EmailField()
    telefono=models.CharField(max_length=40)
    cobertura=models.CharField(max_length=120)
    medico=models.CharField(max_length=120)
    fecha_cx=models.DateField(blank=True,null=True)
    sector=models.CharField(max_length=32,choices=SECTORES)
    observaciones=models.TextField(blank=True)
    estado=models.CharField(max_length=40,choices=ESTADOS,default='Pendiente')
    presupuesto=models.CharField(max_length=24,choices=PRESUP,default='')
    obs_proveedores=models.CharField(max_length=255,blank=True)
    reprogramacion=models.DateField(blank=True,null=True)
    observaciones_reprogramacion=models.CharField(max_length=255,blank=True)
    orden_medica=models.FileField(upload_to='ordenes/')
    dni_file=models.FileField(upload_to='dni/')
    credencial=models.FileField(upload_to='credencial/')
    orden_materiales=models.FileField(upload_to='materiales/',blank=True,null=True)
    subcarpeta_url=models.CharField(max_length=512,blank=True)
    def __str__(self): return f"{self.nombre} ({self.dni})"
