from django.db import models

class Patient(models.Model):
    SECTOR_CHOICES = (('trauma','Traumatología'), ('hemo','Hemodinamia'))
    nombre = models.CharField(max_length=200)
    dni = models.CharField(max_length=32, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=64, blank=True, null=True)
    cobertura = models.CharField(max_length=128, blank=True, null=True)
    medico = models.CharField(max_length=128, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    sector_code = models.CharField(max_length=16, choices=SECTOR_CHOICES, default='trauma')
    estado = models.CharField(max_length=64, default='Pendiente')
    fecha_cx = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.nombre} ({self.dni or ''})"

def upload_to(instance, filename):
    return f"patients/{instance.patient_id}/{filename}"

class Attachment(models.Model):
    KIND_CHOICES = (
        ('orden','Orden'),
        ('dni','DNI'),
        ('credencial','Credencial'),
        ('materiales','Materiales'),
        ('otro','Otro'),
    )
    patient = models.ForeignKey(Patient, related_name='attachments', on_delete=models.CASCADE)
    kind = models.CharField(max_length=32, choices=KIND_CHOICES, default='otro')
    file = models.FileField(upload_to=upload_to)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def url(self):
        try:
            return self.file.url
        except Exception:
            return ""
