from django.db import models  # type: ignore
from django.contrib.auth.hashers import make_password, check_password  # type: ignore
from django.contrib.auth.models import Permission  # type: ignore
from django.contrib.auth.hashers import check_password as django_check_password  # type: ignore
from django.core.validators import MaxValueValidator,MinValueValidator  # type: ignore
from django.utils import timezone  # type: ignore
from django.utils.timezone import timedelta  # type: ignore
# Create your models here.
class Independiente(models.Model):
    estado_civil=[
        ('SOLTERO', 'Soltero/a'),
        ('CASADO', 'Casado/a'),
        ('DIVORCIADO', 'Divorciado/a'),
        ('VIUDO', 'Viudo/a'),
    ]
    tipo_documento=[
        ('Cc', 'Cedula de ciudadania'),
        ('Ce', 'Cedula de extrangeria'),
        ('Passpor', 'Pasaporte'),
    ]
    genero=[
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
        ('P', 'Prefiero no decir'),
    ]
    ccf=[
        ('Ninguna','Ninguna'),
        ('Compensar', 'Compensar'),
        ('Colsubcidio', 'Colsubcidio'),
        ('Cafam', 'Cafam'),
        ('Cofrem', 'Cofrem'),
        ('Comfacesar', 'Comfacesar'),
    ]
    arl=[ ('Ninguna','Ninguna'),
        ('CIA. DE SEGUROS BOLIVAR S.A.	','CIA. DE SEGUROS BOLIVAR S.A.	'),
        ('COMPAÑIA DE SEGUROS DE VIDA AURORA	', 'COMPAÑIA DE SEGUROS DE VIDA AURORA	'),
        ('COMPAÑIA SURAMERICANA ADMINISTRADORA DE RIESGOS PROFESIONALES Y SEGUROS VIDA	', 'COMPAÑIA SURAMERICANA ADMINISTRADORA DE RIESGOS PROFESIONALES Y SEGUROS VIDA	'),
        ('LA EQUIDAD SEGUROS DE VIDA ORGANISMO COOPERATIVO – LA EQUIDAD VIDA', 'LA EQUIDAD SEGUROS DE VIDA ORGANISMO COOPERATIVO – LA EQUIDAD VIDA'),
        ('MAPFRE COLOMBIA VIDA SEGUROS S', 'MAPFRE COLOMBIA VIDA SEGUROS S'),
        ('POSITIVA COMPAÑIA DE SEGUROS', 'POSITIVA COMPAÑIA DE SEGUROS'),
        ('RIESGOS PROFESIONALES COLMENA S.A COMPAÑÍA DE SEGUROS DE VIDA', 'RIESGOS PROFESIONALES COLMENA S.A COMPAÑÍA DE SEGUROS DE VIDA'),
        ('SEGUROS DE VIDA ALFA S.A.', 'SEGUROS DE VIDA ALFA S.A.'),
        ('SEGUROS DE VIDA COLPATRIA S.A.', 'SEGUROS DE VIDA COLPATRIA S.A.'),
        
        
    ]

    numero_identificacion = models.IntegerField(primary_key=True)
    primer_nombre = models.CharField(max_length=30)
    segundo_nombre = models.CharField(max_length=30, blank=True, null=True)
    primer_apellido = models.CharField(max_length=30)
    segundo_apellido = models.CharField(max_length=30, blank=True, null=True)
    estado_civil = models.CharField(max_length=20, choices=estado_civil)
    tipo_documento = models.CharField(max_length=50, choices=tipo_documento)
    correo = models.EmailField(unique=True)
    celular = models.CharField(max_length=15)
    genero = models.CharField(max_length=10,choices=genero)
    salario=models.FloatField(validators=[MinValueValidator(1300000)],default=1300000)
    fecha_nacimiento = models.DateField()
    fecha_exp_documento = models.DateField()
    caja_comprensacion= models.CharField(max_length=80, choices=ccf, default='Ninguna',blank=True, null=True)
    riesgos_laborales= models.CharField(max_length=80, choices=arl, default='Ninguna',blank=True, null=True)
    imagen=models.ImageField(upload_to='photos')

    def __str__(self):
        return self.primer_nombre

class Usuarios(models.Model):
    id_rol_choices = [
        ('Independiente', 'Independiente'),
    ]

    usuario = models.ForeignKey(Independiente, on_delete=models.CASCADE)
    intentos = models.IntegerField(default=0)
    estado_u = models.BooleanField(default=False)
    contrasena = models.CharField(max_length=120, null=True)
    id_rol = models.CharField(max_length=30, choices=id_rol_choices)

    def set_password(self, raw_password):
        self.contrasena = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return django_check_password(raw_password, self.contrasena)
    
class PasswordResetRequest(models.Model):
    usuario = models.ForeignKey(Independiente, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True)

    used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Es un nuevo objeto, establece la fecha de expiración
            self.expires_at = self.created_at + timedelta(minutes=15)
        super().save(*args, **kwargs)
    
    
class Calculos(models.Model):
    documento = models.ForeignKey(Independiente, on_delete=models.CASCADE)
    salud=models.FloatField(blank=True, null=True)
    pension=models.FloatField(blank=True,null=True)
    arl=models.FloatField(blank=True,null=True)
    salarioBase=models.FloatField(blank=True,null=True)
    cajaCompensacion=models.FloatField(blank=True,null=True)
    FSP=models.FloatField(blank=True,null=True)
    
class DatosCalculos(models.Model):
    
    arlN=[
        ('0', 'Ninguno'),
        ('1', 'Nivel 1'),
        ('2', 'Nivel 2'),
        ('3', 'Nivel 3'),
        ('4', 'Nivel 4'),
        ('5', 'Nivel 5'), 
    ]
    
    ccf=[
        ('Ninguna','Ninguna'),
        ('Compensar', 'Compensar'),
        ('Colsubcidio', 'Colsubcidio'),
        ('Cafam', 'Cafam'),
        ('Cofrem', 'Cofrem'),
        ('Comfacesar', 'Comfacesar'),
    ]
    arl=[('Ninguna','Ninguna'),
        ('CIA. DE SEGUROS BOLIVAR S.A.	','CIA. DE SEGUROS BOLIVAR S.A.	'),
        ('COMPAÑIA DE SEGUROS DE VIDA AURORA	', 'COMPAÑIA DE SEGUROS DE VIDA AURORA	'),
        ('COMPAÑIA SURAMERICANA ADMINISTRADORA DE RIESGOS PROFESIONALES Y SEGUROS VIDA	', 'COMPAÑIA SURAMERICANA ADMINISTRADORA DE RIESGOS PROFESIONALES Y SEGUROS VIDA	'),
        ('LA EQUIDAD SEGUROS DE VIDA ORGANISMO COOPERATIVO – LA EQUIDAD VIDA', 'LA EQUIDAD SEGUROS DE VIDA ORGANISMO COOPERATIVO – LA EQUIDAD VIDA'),
        ('MAPFRE COLOMBIA VIDA SEGUROS S', 'MAPFRE COLOMBIA VIDA SEGUROS S'),
        ('POSITIVA COMPAÑIA DE SEGUROS', 'POSITIVA COMPAÑIA DE SEGUROS'),
        ('RIESGOS PROFESIONALES COLMENA S.A COMPAÑÍA DE SEGUROS DE VIDA', 'RIESGOS PROFESIONALES COLMENA S.A COMPAÑÍA DE SEGUROS DE VIDA'),
        ('SEGUROS DE VIDA ALFA S.A.', 'SEGUROS DE VIDA ALFA S.A.'),
        ('SEGUROS DE VIDA COLPATRIA S.A.', 'SEGUROS DE VIDA COLPATRIA S.A.'),
        
        
    ]
    
    documento = models.ForeignKey(Independiente, on_delete=models.CASCADE)
    salarioBase=models.FloatField(validators=[MinValueValidator(1300000)],default=1300000)
    ibc=models.FloatField(validators=[MaxValueValidator(100),MinValueValidator(40)],default=40)
    salud=models.FloatField( max_length=50, default=12.5)
    pension=models.FloatField(max_length=50, default=16)
    riesgos_laborales= models.CharField(max_length=100, choices=arl, default='Ninguna',blank=True, null=True)
    arl=models.CharField(max_length=20,blank=True,null=True, choices=arlN,default='0')
    caja_comprensacion= models.CharField(max_length=100, choices=ccf, default='Ninguna',blank=True, null=True)
    CCF=models.CharField(max_length=20,blank=True,null=True, choices=ccf,default='Ninguna')
    FSP=models.FloatField(blank=True,null=True)