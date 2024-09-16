from django.db import models
from django.db import models  # type: ignore
from django.core.validators import MaxValueValidator,MinValueValidator # type: ignore
from django.utils import timezone # type: ignore
from django.db import models # type: ignore
from django.contrib.auth.hashers import make_password, check_password # type: ignore
from django.contrib.auth.models import Permission # type: ignore
from django.contrib.auth.hashers import check_password as django_check_password # type: ignore
from django.core.validators import MaxValueValidator,MinValueValidator # type: ignore
from django.utils import timezone # type: ignore
from django.utils.timezone import timedelta # type: ignore




class Empresa(models.Model):
    nit = models.CharField(max_length=11, primary_key=True)
    razon_social = models.CharField(max_length=100)
    telefono_entidad = models.CharField(max_length=10)
    correo_entidad = models.EmailField(max_length=255,unique=True) 
    imagen_empresa=models.ImageField(upload_to='photos')
    def __str__(self):
                return f'{self.razon_social}'
       

class NivelEstudio(models.Model):
    id_nivel_estudio = models.AutoField(primary_key=True)
    descripcion_nivel_estudio = models.CharField(max_length=30)
    estado_estudio= models.CharField(max_length=20,choices= [('Culminado','Culminado'),('Cursando', 'Cursando'),('Aplazado', 'Aplazado')])
    nivel_academico=models.CharField(max_length=20,choices= [('Primaria', 'Primaria'),('Secundaria', 'Secundaria'),('Media', 'Media'),('Técnico', 'Técnico'),('Tecnológico', 'Tecnológico'),('Pregrado', 'Pregrado'),('Especialización', 'Especialización'),('Maestría', 'Maestría'),('Doctorado', 'Doctorado')],)
    def __str__(self):
                return f'{self.descripcion_nivel_estudio}'

class NivelGrado(models.Model):
    id_nivel_grado = models.AutoField(primary_key=True)
    tipo_nivel_grado = models.CharField(max_length=10, choices=[('Grado', 'Grado'), ('Nivel', 'Nivel'),('No aplica', 'No aplica')])
    salario_minimo= models.DecimalField( max_digits=10,decimal_places=2)
    salario_maximo = models.DecimalField( max_digits=10,decimal_places=2)
    min_meses_expe = models.IntegerField()
    id_nivel_estudio_requerido= models.ForeignKey(NivelEstudio, on_delete=models.CASCADE)
    def __str__(self):
                return f'{self.id_nivel_grado}-{self.tipo_nivel_grado}'


class Cargo(models.Model):
    nivel_riesgo=[
        ('1', 'Nivel 1'),
        ('2', 'Nivel 2'),
        ('3', 'Nivel 3'),
        ('4', 'Nivel 4'),
        ('5', 'Nivel 5'), 
    ]
    id_cargo = models.AutoField(primary_key=True)
    nombre_cargo = models.CharField(max_length=30)
    descripcion_cargo = models.TextField()
    nivel_riesgo=models.CharField(max_length=10, choices=nivel_riesgo)
    id_nivel_grado = models.ForeignKey(NivelGrado, on_delete=models.CASCADE)
    def __str__(self):
                return f'{self.nombre_cargo}'

    
class Empleado(models.Model):
    numero_identificacion_e = models.CharField(max_length=10, primary_key=True)
    primer_nombre = models.CharField(max_length=30)
    segundo_nombre = models.CharField(max_length=30, null=True, blank=True)
    primer_apellido = models.CharField(max_length=30)
    segundo_apellido = models.CharField(max_length=30, null=True, blank=True)
    estado_civil = models.CharField(max_length=10, choices=[('Soltero', 'Soltero'), ('Casado', 'Casado'), ('Divorciado', 'Divorciado'), ('Viudo', 'Viudo'), ('No indica', 'No indica')])
    tipo_documento = models.CharField(max_length=25, choices=[('Cédula', 'Cédula'), ('Pasaporte', 'Pasaporte'), ('Tarjeta de Identidad', 'Tarjeta de Identidad'), ('Cédula de extranjería', 'Cédula de extranjería')])
    correo = models.EmailField(max_length=100,unique=True)
    celular = models.CharField(max_length=10, unique=True)
    genero = models.CharField(max_length=10, choices=[('Masculino', 'Masculino'), ('Femenino', 'Femenino'), ('Otro', 'Otro')])
    fecha_nacimiento = models.DateField(help_text="Ingrese la fecha de nacimiento (YYYY-MM-DD)")
    fecha_exp_documento = models.DateField()
    direccion = models.CharField(max_length=50)
    numero_cuenta_bancaria = models.CharField(max_length=20)
    banco = models.CharField(max_length=30)
    nit = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    id_nivel_estudio = models.ForeignKey(NivelEstudio, on_delete=models.CASCADE)
    imagen_empleado=models.ImageField(upload_to='photos')
    def __str__(self):
                return f'{self.numero_identificacion_e}'
    
    
class Contrato(models.Model):
    tipo_contrato=[
        ('Termino Fijo', 'Termino Fijo'),
        ('Indefinido', 'Indefinido'),
    ]
    
    id_contrato = models.AutoField(primary_key=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    horas_semanales = models.IntegerField()
    salario_asignado = models.FloatField(validators=[MinValueValidator(1300000)])
    estado = models.CharField(max_length=10, choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')])
    tipo_contrato =  models.CharField(max_length=20, choices=tipo_contrato)
    id_cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    numero_identificacion_e = models.ForeignKey(Empleado, on_delete=models.CASCADE)


class Liquidacion(models.Model):
    id_liquidacion = models.AutoField(primary_key=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_calculo = models.DateField(null=True)
    salud_empleado = models.DecimalField(max_digits=10, decimal_places=2)
    pension_empleado = models.DecimalField(max_digits=10, decimal_places=2)
    salud_empresa = models.DecimalField(max_digits=10, decimal_places=2)
    pension_empresa = models.DecimalField(max_digits=10, decimal_places=2)
    arl = models.DecimalField(max_digits=10, decimal_places=2)
    caja_compensacion = models.DecimalField(max_digits=10, decimal_places=2)
    vacaciones = models.IntegerField(null=True)
    cesantias = models.IntegerField(null=True)
    intereses_cesantias = models.IntegerField(null=True)
    numero_identificacion_e = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    total_antes_deducciones = models.DecimalField(max_digits=10, decimal_places=2)
    total_final = models.DecimalField(max_digits=10, decimal_places=2)
    empresa=models.IntegerField(null=True)


class vacacionesCesantias(models.Model):
    numero_identificacion_e = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    vacaciones_acumulado=models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cesantias_acumuladas=models.DecimalField(max_digits=10, decimal_places=2, null=True)
    intereses_cesantias=models.DecimalField(max_digits=10, decimal_places=2, null=True)
    antiguedad=models.IntegerField(null=True)
    dias_vacaciones=models.IntegerField(null=True)

class TipoNovedad(models.Model):
    id_tipo_novedad = models.AutoField(primary_key=True)
    descripcion_tipo_novedad = models.CharField(max_length=100)

class Novedades(models.Model):
    id_novedad = models.AutoField(primary_key=True)
    numero_identificacion_e = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    id_tipo_novedad = models.ForeignKey(TipoNovedad, on_delete=models.CASCADE)
    fecha_novedad = models.DateField()
    descripcion_novedad = models.TextField()


class PasswordResetRequest(models.Model):
    usuario = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True)
    used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.expires_at = self.created_at + timedelta(minutes=15)
        super().save(*args, **kwargs)

class Usuarios(models.Model):
    id_rol=[
        ('Admin', 'Admin'),
        ('ContadorL', 'ContadorL'),
        ('Auxiliar Contable', 'Auxiliar Contable'),
        ('RRHHL', 'RRHHL'),
        ('RRHH', 'RRHH'),
        ('Empleado General', 'Empleado General'),
    ]

    usuario = models.ForeignKey(Empleado, on_delete=models.CASCADE, null=True, blank=True) 
    intentos = models.IntegerField(default=0)
    estado_u = models.BooleanField(default=False)
    contrasena = models.CharField(max_length=88)
    rol= models.CharField(max_length=30,choices=id_rol) 
    
    def set_password(self, raw_password):
        self.contrasena = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return django_check_password(raw_password, self.contrasena)
    
class HorasExtrasRecargos(models.Model):
        empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
        fecha_registro=models.DateField()
        HorasExDiu=models.IntegerField(validators=[MaxValueValidator(48),MinValueValidator(0)],blank=True,null=True)
        HorasExNoc=models.IntegerField(validators=[MaxValueValidator(48),MinValueValidator(0)],blank=True,null=True)
        HorasExFestivaDiu=models.IntegerField(validators=[MaxValueValidator(48),MinValueValidator(0)],blank=True,null=True)
        HorasExFestivaNoc=models.IntegerField(validators=[MaxValueValidator(48),MinValueValidator(0)],blank=True,null=True)
        recargoDiuFes=models.IntegerField(blank=True,null=True)
        recargoNoc=models.IntegerField(blank=True,null=True)
        recargoNocFest=models.IntegerField(blank=True,null=True)
        
class PorcentajesLegales(models.Model):
    # Porcentajes de salud
    salud_empleado = models.DecimalField(max_digits=5, decimal_places=4, help_text="Porcentaje de salud a cargo del empleado ejemplo: 4 % ingrese 0.04")
    salud_empresa = models.DecimalField(max_digits=5, decimal_places=4, help_text="Porcentaje de salud a cargo de la empresa")
    
    # Porcentajes de pensión
    pension_empleado = models.DecimalField(max_digits=5, decimal_places=4, help_text="Porcentaje de pensión a cargo del empleado")
    pension_empresa = models.DecimalField(max_digits=5, decimal_places=4, help_text="Porcentaje de pensión a cargo de la empresa")
    
    # Otros porcentajes de prestaciones
    vacaciones = models.DecimalField(max_digits=5, decimal_places=4, help_text="Porcentaje de vacaciones")
    cesantias = models.DecimalField(max_digits=5, decimal_places=4, help_text="Porcentaje de cesantías")
    intereses_cesantias = models.DecimalField(max_digits=5, decimal_places=4, help_text="Porcentaje de intereses sobre cesantías")
    
    # Contribuciones parafiscales
    icbf = models.DecimalField(max_digits=5, decimal_places=4, help_text="Porcentaje de contribución al ICBF")
    sena = models.DecimalField(max_digits=5, decimal_places=4, help_text="Porcentaje de contribución al SENA")
    caja_compensacion = models.DecimalField(max_digits=5, decimal_places=4, help_text="Porcentaje de contribución a la caja de compensación")

    # Riesgo de trabajo y transporte
    riesgo_laboral1 = models.DecimalField(max_digits=6, decimal_places=5, help_text="Porcentaje de riesgo laboral - Clase 1")
    riesgo_laboral2 = models.DecimalField(max_digits=6, decimal_places=5, help_text="Porcentaje de riesgo laboral - Clase 2")
    riesgo_laboral3 = models.DecimalField(max_digits=6, decimal_places=5, help_text="Porcentaje de riesgo laboral - Clase 3")
    riesgo_laboral4 = models.DecimalField(max_digits=6, decimal_places=5, help_text="Porcentaje de riesgo laboral - Clase 4")
    riesgo_laboral5 = models.DecimalField(max_digits=6, decimal_places=5, help_text="Porcentaje de riesgo laboral - Clase 5")
    
    auxilio_transporte = models.IntegerField( help_text="Monto del auxilio de transporte")
    
    fecha_vigencia = models.DateField(help_text="Fecha de inicio de vigencia de estos porcentajes")
    vigente=models.BooleanField(default=True)
    
    def __str__(self):
        return f"Porcentajes Legales - Vigencia desde {self.fecha_vigencia}"