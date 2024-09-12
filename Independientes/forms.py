
from datetime import timedelta
from django import forms   # type: ignore 
from .models import Independiente, DatosCalculos
from django.core.exceptions import ValidationError
from django.utils import timezone

class IndependienteForm(forms.ModelForm):
    class Meta:
        model = Independiente
        fields = [
            'numero_identificacion', 'primer_nombre', 'segundo_nombre',
            'primer_apellido', 'segundo_apellido', 'estado_civil', 'tipo_documento',
            'correo', 'celular', 'genero', 'salario', 'fecha_nacimiento', 
            'fecha_exp_documento', 'caja_comprensacion', 'riesgos_laborales', 'imagen'
        ]
        widgets = {
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

class LoginForm(forms.Form):
    numero_identificacion = forms.IntegerField(label='Número de identificación')
    contrasena = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


class RecuperarContrasenaForm(forms.Form):
    numero_identificacion = forms.IntegerField(label='Número de Identificación')


class PasswordResetForm(forms.Form):
    token = forms.CharField(label='Token')
    new_password = forms.CharField(label='Nueva Contraseña', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput)

class habilitarCuentaForm(forms.Form):
    token = forms.CharField(label='Token')

class DatosCalculosForm(forms.ModelForm):
    class Meta:
        model = DatosCalculos
        fields = ['salarioBase', 'ibc', 'salud', 'pension', 'arl', 'CCF']