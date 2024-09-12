
from datetime import timedelta
from django import forms   # type: ignore 
from .models import Empleado,Usuarios,Empresa, Liquidacion,HorasExtrasRecargos,Contrato
from django.core.exceptions import ValidationError # type: ignore
from django.utils import timezone # type: ignore

class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ['fecha_inicio','fecha_fin',
                  'horas_semanales',
                  'salario_asignado',
                  'tipo_contrato',
                  'id_cargo'
                  ]
        labels = {
                    'id_cargo': 'Cargo',  # Cambia el nombre que aparecerá en el formulario
                }
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
             }
class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = '__all__'

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = [
            'numero_identificacion_e', 'primer_nombre', 'segundo_nombre',
            'primer_apellido', 'segundo_apellido', 'estado_civil', 'tipo_documento',
            'correo', 'celular', 'genero', 'fecha_nacimiento', 
            'fecha_exp_documento','direccion','nit', 'imagen_empleado','numero_cuenta_bancaria',
            'banco','id_nivel_estudio'
        ]
        labels = {
                    'numero_identificacion_e': 'Numero de identificación',  # Cambia el nombre que aparecerá en el formulario
                }
        widgets = {
            'nit': forms.HiddenInput(),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'fecha_exp_documento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
             }
    
    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            hoy = timezone.now().date()
            edad_minima = hoy - timedelta(days=18*365)
            if fecha_nacimiento > edad_minima:
                raise ValidationError('La fecha de nacimiento debe ser al menos 18 años antes de hoy.')
        return fecha_nacimiento

    def clean_fecha_exp_documento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        fecha_exp_documento = self.cleaned_data.get('fecha_exp_documento')
        if fecha_nacimiento and fecha_exp_documento:
            edad_minima_exp = fecha_nacimiento + timedelta(days=18*365)
            if fecha_exp_documento < edad_minima_exp:
                raise ValidationError('La fecha de expedición del documento debe ser al menos 18 años después de la fecha de nacimiento.')
        return fecha_exp_documento

    def clean(self):
        cleaned_data = super().clean()
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
        fecha_exp_documento = cleaned_data.get('fecha_exp_documento')

        if fecha_nacimiento and fecha_exp_documento:
            edad_minima_exp = fecha_nacimiento + timedelta(days=18*365)
            if fecha_exp_documento < edad_minima_exp:
                self.add_error('fecha_exp_documento', 'La fecha de expedición del documento debe ser al menos 18 años después de la fecha de nacimiento.')
        return cleaned_data
            

        #Este codigo permite bloquear los espacios pero afecta cuando se va a registrar un nuevo empleado, entonces hace falta adaptarlo solo para el fomrulario de modificar
        # ['numero_identificacion', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido', 'estado_civil']

    # def __init__(self, *args, **kwargs):
    #     super(EmpleadoForm, self).__init__(*args, **kwargs)
    #     readonly_fields = ['numero_identificacion', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido']
    #     for filtro in self.fields:
    #         if filtro in readonly_fields:
    #             self.fields[filtro].widget.attrs['readonly'] = True

class LoginForm(forms.Form):
    numero_identificacion = forms.IntegerField(label='Número de identificación')
    contrasena = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


class RecuperarContrasenaForm(forms.Form):
    numero_identificacion = forms.IntegerField(label='Número de Identificación')


class PasswordResetForm(forms.Form):
    token = forms.CharField(label='Token', max_length=255)
    new_password = forms.CharField(label='Nueva Contraseña', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput)
    

class HorasExtrasForm(forms.ModelForm):
    class Meta:
        model = HorasExtrasRecargos
        fields = [
            'HorasExDiu',
            'HorasExNoc',
            'HorasExFestivaNoc',
            'HorasExFestivaDiu',
            'recargoDiuFes',
            'recargoNoc',
            'recargoNocFest',
        ]

    def clean(self):
        cleaned_data = super().clean()
        
        # Definir una función para obtener el valor del campo o devolver 0 si es None o vacío
        def get_valor_campo(campo):
            valor = cleaned_data.get(campo)
            return valor if valor is not None and valor != '' else 0
        
        # Obtener los valores de los campos y manejar valores vacíos o None
        horas_ex_diu = get_valor_campo('HorasExDiu')
        horas_ex_noc = get_valor_campo('HorasExNoc')
        horas_ex_festiva_noc = get_valor_campo('HorasExFestivaNoc')
        horas_ex_festiva_diu = get_valor_campo('HorasExFestivaDiu')
        recargo_diu_fes = get_valor_campo('recargoDiuFes')
        recargo_noc = get_valor_campo('recargoNoc')
        recargo_noc_fest = get_valor_campo('recargoNocFest')

        # Calcular la suma total de horas
        horas_totales = (
            horas_ex_diu + horas_ex_noc +
            horas_ex_festiva_noc + horas_ex_festiva_diu
        )

        # Validar si la suma total de horas excede 48
        if horas_totales > 48:
            raise forms.ValidationError('La suma de horas no puede exceder 48.')

        return cleaned_data