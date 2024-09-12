from datetime import datetime
import re
from Independientes.forms import IndependienteForm,LoginForm,PasswordResetForm,habilitarCuentaForm
from .models import DatosCalculos, Independiente, Usuarios,PasswordResetRequest,Calculos
from django.shortcuts import render ,redirect, get_object_or_404  # type: ignore
from django.contrib import messages  # type: ignore
from django.contrib.auth import logout  # type: ignore
from django.http import JsonResponse, HttpResponseRedirect  # type: ignore
from .forms import DatosCalculosForm, RecuperarContrasenaForm
from django.core.mail import send_mail  # type: ignore
from django.template.loader import render_to_string  # type: ignore
from django.utils.html import strip_tags  # type: ignore
from django.http import HttpRequest # type: ignore
import secrets




def cargar_token(request): 
        return render(request,'independientes/resetear_contrasena.html') #genera un token para la recuperacion de contraseña

class GestionLogin:

    @staticmethod
    def recuperar_contrasena(request):
        if request.method == 'POST':
            form = RecuperarContrasenaForm(request.POST)
            if form.is_valid():
                numero_identificacion = form.cleaned_data['numero_identificacion'] # Obtener el número de identificación del formulario validado

                try:
                    usuario = Independiente.objects.get(numero_identificacion=numero_identificacion)

                    # Crear una solicitud de recuperación de contraseña y guardarla en la base de datos
                    solicitud = PasswordResetRequest(usuario=usuario, token=GestionLogin.generate_token())
                    solicitud.save()

                    # Enviar el correo electrónico con el token para restablecer la contraseña
                    subject = 'Recuperación de Contraseña'
                    html_message = render_to_string('independientes/email/recuperacion_contrasena.html', {'usuario': usuario, 'token': solicitud.token})
                    plain_message = strip_tags(html_message)
                    from_email = 'p4ym4ster@gmail.com'  # Cambiar por tu dirección de correo
                    to_email = usuario.correo
                    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

                    messages.success(request, 'Se ha enviado un correo electrónico con el token para restablecer tu contraseña.')
                    return redirect('password_reset')  # Redirigir a la página para ingresar el token

                except Independiente.DoesNotExist:
                    messages.error(request, 'No se encontró un usuario con ese número de identificación.')

        else:
            form = RecuperarContrasenaForm()

        return render(request, 'independientes/recuperar_contrasena.html', {'form': form})

    def password_reset(request):
        if request.method == 'POST':
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                token = form.cleaned_data['token']  # Obtener el token del formulario validado
                new_password = form.cleaned_data['new_password']  # Obtener la nueva contraseña del formulario validado
                confirm_password = form.cleaned_data['confirm_password']  # Obtener la confirmación de la contraseña del formulario validado
                
                try:
                    reset_request = PasswordResetRequest.objects.get(token=token, used=False)
                except PasswordResetRequest.DoesNotExist:
                    reset_request = None  # Si no se encuentra, establecer reset_request como None

                if new_password != confirm_password:
                    messages.error(request, 'Las contraseñas no coinciden.') # Verificar si las contraseñas coinciden
                else:
                    if len(new_password) < 6:
                        messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')  # Verificar si la nueva contraseña tiene al menos 6 caracteres
                    elif not re.search(r'[A-Za-z]', new_password):
                        messages.error(request, 'La contraseña debe contener al menos una letra.')  # Verificar si la nueva contraseña contiene al menos una letra
                    elif not re.search(r'[A-Z]', new_password):
                        messages.error(request, 'La contraseña debe contener al menos una letra Mayuscula.')  # Verificar si la nueva contraseña contiene al menos una letra mayúscula
                    elif not re.search(r'\d', new_password):
                        messages.error(request, 'La contraseña debe contener al menos un número.')  # Verificar si la nueva contraseña contiene al menos un número
                    elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
                        messages.error(request, 'La contraseña debe contener al menos un carácter especial.')  # Verificar si la nueva contraseña contiene al menos un carácter especial
                    elif reset_request:
                        usuario = reset_request.usuario   # Obtener el usuario asociado a la solicitud de restablecimiento
                        usuario = Usuarios.objects.get(usuario=usuario) # Obtener el objeto del usuario desde la base de datos
                        
                        usuario.set_password(new_password)  # Establecer la nueva contraseña para el usuario

                        reset_request.used = True  # Marcar la solicitud de restablecimiento como usada
                        reset_request.save()  # Guardar los cambios en la solicitud de restablecimiento

                        usuario.intentos = 0  # Restablecer el contador de intentos del usuario
                        usuario.estado_u = True  # Cambiar el estado del usuario a activo
                        usuario.save()  # Guardar los cambios en el usuario
                        
                        messages.success(request, 'Contraseña actualizada correctamente. Por favor, inicia sesión.')  # Mostrar mensaje de éxito
                        return redirect('login')  # Redirigir a la página de inicio de sesión después de cambiar la contraseña
                    else:
                        messages.error(request, 'El token de restablecimiento de contraseña no es válido o ya ha sido utilizado.') # Mostrar mensaje de error si el token no es válido o ya ha sido usado
            else:
                messages.error(request, 'Por favor, corrige los errores del formulario.') # Mostrar mensaje de error si el formulario no es válido
        else:
            form = PasswordResetForm() # Crear una instancia del formulario de restablecimiento de contraseña

        return render(request, 'independientes/password_reset.html', {'form': form})
                



    @staticmethod
    def generate_token():
        # Generar un token único y seguro
        return secrets.token_urlsafe(20)


    def login_view(request):
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                numero_identificacion = form.cleaned_data['numero_identificacion']  # Obtener el número de identificación del formulario validado
                contrasena = form.cleaned_data['contrasena']  # Obtener la contraseña del formulario validado

                try:
                    # Busca el usuario por número de identificación en tu modelo personalizado
                    usuario = Usuarios.objects.get(usuario__numero_identificacion=numero_identificacion)
                    indepe = Independiente.objects.get(pk=numero_identificacion)  # Obtener el independiente por su número de identificación
                    permisos = usuario.id_rol  # Obtener los permisos del usuario
                    userName = indepe.primer_nombre  # Obtener el primer nombre del independiente

                    if usuario.estado_u == True:  # Verificar si la cuenta del usuario está activada
                        if usuario and usuario.check_password(contrasena):  # Verificar si la contraseña es correcta
                        # Autenticación exitosa
                            request.session['numero_identificacion'] = numero_identificacion  # Guardar el número de identificación en la sesión
                            request.session['estadoSesion'] = True  # Guardar el estado de la sesión como activa
                            request.session['permisos'] = permisos  # Guardar los permisos en la sesión
                            request.session['user'] = userName  # Guardar el nombre de usuario en la sesión

                            # Redirige al usuario a la página deseada después del inicio de sesión
                            return redirect('homeIndependiente')
                        else:
                            messages.error(request, 'Cuenta no esta activada')  # Mostrar mensaje de error si la cuenta no está activada
                    else:
                        messages.error(request, 'El usuario no existe')  # Mostrar mensaje de error si el usuario no existe
                except Usuarios.DoesNotExist:
                    messages.error(request, 'El usuario no existe')

        else:
            form = LoginForm()

        return render(request, 'independientes/login.html', {'form': form})
    
    def activateAcount(request,numero_identificacion):
            
            if request.method == 'POST':
                form = habilitarCuentaForm(request.POST)
                if form.is_valid():
                    token = form.cleaned_data['token'] # Obtener el token del formulario validado
                    independi=Independiente.objects.get(pk=numero_identificacion) # Obtener el objeto Independiente por su número de identificación
                    usuario = Usuarios.objects.get(usuario=independi) # Obtener el usuario asociado al Independiente
                    try:
                        reset_request = PasswordResetRequest.objects.get(token=token, used=False) # Buscar la solicitud de restablecimiento de contraseña que coincida con el token y no haya sido usada
                    except PasswordResetRequest.DoesNotExist:
                        reset_request = None # Si no se encuentra, establecer reset_request como None

                    if reset_request:
                        usuario.estado_u = True  # Activar la cuenta del usuario
                        usuario.save()  # Guardar los cambios en el usuario
                        
                        messages.success(request, 'Usuario habilitado. Por favor, inicia sesión.')
                        return redirect('login') 
                    else:
                        messages.error(request, 'El token de activacion de cuenta  no es válido o ya ha sido utilizado.')
                
                else:
                    messages.error(request, 'Por favor, corrige los errores del formulario.')

            else:
                form = habilitarCuentaForm()

            return render(request, 'empresarial/habilitar_usuario.html', {'form': form})


# @login_required
# def editarIndependiente(request, numero_identificacion):
#     try:
#         empleado = Independiente.objects.get(pk=numero_identificacion)
#         formulario = IndependienteForm(instance=empleado)
#         return render(request, 'independientes/editarIndependi.html', {"form": formulario, "empleado": empleado})
#     except Independiente.DoesNotExist:
#         messages.error(request, 'No se encontró el perfil de Independiente asociado')
#         return redirect('home')


    def cerrar_sesion(request):
            if request.method == 'POST':
                logout(request)  # Cerrar la sesión del usuario
                request.session.flush()  # Eliminar todos los datos de la sesión
                return JsonResponse({'status': 'ok'})  # Retornar una respuesta JSON con estado 'ok'
            return JsonResponse({'status': 'error'}, status=400)  # Retornar una respuesta JSON con estado 'error' si no es un método POST

    def cerrar_sesion_redirect(request):
        logout(request)  # Cerrar la sesión del usuario
        request.session.flush()  # Eliminar todos los datos de la sesión
        return redirect('login')  # Redirigir a la página de inicio de sesión
        
def homeIndependientes(request):
    numero_identificacion = request.session.get('numero_identificacion')  # Obtener el número de identificación de la sesión
    try:
        independi = Independiente.objects.get(pk=numero_identificacion) # Buscar el objeto Independiente por su número de identificación
        return render(request, 'independientes/home.html', {'independi': independi}) # Renderizar la plantilla con el objeto Independiente
    except Independiente.DoesNotExist:
        messages.error(request, 'No se encontró el perfil de Independiente asociado')  # Mostrar mensaje de error si no se encuentra el perfil
        return redirect('login')  # Redirigir a la página de inicio de sesión si no se encuentra el perfil



class GestionIndependiente():
    def RegistroIndependi(request):
        error_message = None # Variable para almacenar mensajes de error
        
        if request.method == 'POST':
                formulario = IndependienteForm(request.POST, request.FILES) # Crear una instancia del formulario con los datos POST y archivos
                if formulario.is_valid():
                    formula = formulario.save()  # Guardar el formulario y obtener el objeto Independiente
                    raw_password = formula.primer_nombre + str(formula.numero_identificacion) + '@'  # Generar una contraseña temporal
                
                    usuario = Usuarios(
                        usuario=formula,
                        intentos=0,
                        estado_u=False, # Establecer el estado del usuario como inactivo
                        id_rol='Independiente'
                    )
                    solicitud = PasswordResetRequest(usuario=formula, token=GestionLogin.generate_token())
                    solicitud.save() # Guardar la solicitud
                    if solicitud:
                        usuario.save()  # Guardar el usuario
                        usuario.set_password(raw_password)  # Establecer la contraseña del usuario
                        datos_calculos = DatosCalculos(documento=formula)  # Crear una instancia de DatosCalculos con el objeto Independiente
                        datos_calculos.save()  # Guardar los datos de cálculos
                        
                        # Enviar el correo electrónico con el token para restablecer la contraseña
                        subject = 'Bienvenido a PayMaster'
                        html_message = render_to_string('independientes/email/envio_credencial.html', {'usuario': formula, 'token': solicitud.token, 'password': raw_password})
                        plain_message = strip_tags(html_message)  # Convertir el mensaje HTML a texto plano
                        from_email = 'p4ym4ster@gmail.com'  # Cambiar por tu dirección de correo
                        to_email = formula.correo  # Dirección de correo del destinatario
                        send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)  # Enviar el correo

                        messages.success(request, 'Se ha enviado un correo electrónico con el token para activar la cuenta.')
                        return redirect('activate_acount', formula.numero_identificacion)  # Redirigir a la página para ingresar el token

                    return redirect('login') 
                else:
                    error_message = "Hay errores en el formulario, por favor verifique los datos."
        else:
                formulario = IndependienteForm()

        return render(request, 'independientes/registroIndependi.html', {'form': formulario, 'error_message': error_message})

    
        
        
        
    def editarIndependiente(request, numero_identificacion):
        independiente = get_object_or_404(Independiente, pk=numero_identificacion) # Obtener el objeto Independiente o retornar 404 si no existe
        formulario = IndependienteForm(instance=independiente) # Crear una instancia del formulario con los datos del Independiente
        return render(request, 'independientes/editarIndependi.html', {'form': formulario, 'independi': independiente}) # Renderizar la plantilla con el formulario y el Independiente

    def actualizarIndependiente(request, numero_identificacion):
        independiente = Independiente.objects.get(pk=numero_identificacion) # Obtener el objeto Independiente por su número de identificación
        formulario = IndependienteForm(request.POST, instance=independiente) # Crear una instancia del formulario con los datos POST y el objeto Independiente
        if formulario.is_valid():
            formulario.save()  # Guardar los cambios en el Independiente
            independiente = Independiente.objects.get(pk=numero_identificacion)  # Obtener de nuevo el objeto Independiente para asegurarse de tener los datos actualizados
        return render(request, 'independientes/home.html', {"independi": independiente})  # Renderizar la plantilla con el objeto Independiente actualizado


    def eliminarIndependi(request, numero_identificacion):
    #     independiente=Independiente.objects.get(pk=numero_identificacion)  # Obtener el objeto Independiente por su número de identificación
    #     independiente.delete()  # Eliminar el objeto Independiente
    #     independientes=Independiente.objects.all() # Obtener todos los objetos Independiente
       return render (request, 'independientes/listarEmpleado.html')

class CalculosGenerales(HttpRequest):

    def calcular_aportes(request, numero_identificacion):
        independiente = Independiente.objects.get(pk=numero_identificacion)  # Obtener el objeto Independiente por su número de identificación

        # Busca la instancia de DatosCalculos relacionada con el independiente
        try:
            datos_calculos = DatosCalculos.objects.get(documento=independiente)  # Intentar obtener los datos de cálculos para el Independiente
        except DatosCalculos.DoesNotExist:
            datos_calculos = None  # Si no existen datos, asignar None

        if request.method == 'POST':
            form = DatosCalculosForm(request.POST, instance=datos_calculos)  # Crear una instancia del formulario con los datos POST y el objeto DatosCalculos
            if form.is_valid():
                # Asigna la relación con independiente si es una nueva instancia
                calculos = form.save(commit=False)  # Guardar el formulario pero no cometer aún
                if datos_calculos is None:
                    calculos.documento = independiente  # Establecer la relación con el Independiente si es una nueva instancia
                calculos.save()  # Guardar los cálculos

            datos_calculos = DatosCalculos.objects.filter(documento=independiente)  # Obtener los datos de cálculos para el Independiente
                
            for objeto in datos_calculos:
                salario_base = objeto.salarioBase
                nivel_arl = objeto.arl
                ccf = objeto.CCF
                porcentaje_ibc = objeto.ibc
                
            ibc = salario_base * (porcentaje_ibc / 100)  # Calcular el IBC (Ingreso Base de Cotización)
            if ibc < 1300000:
                ibc = 1300000  # Asegurar que el IBC no sea menor al mínimo legal

            salud = ibc * 0.125  # Calcular aporte a salud
            pension = ibc * 0.16  # Calcular aporte a pensión

            if nivel_arl != 'Ninguno':
                arl = CalculosGenerales.calcular_arl(ibc, nivel_arl)  # Calcular el aporte a ARL (Riesgos Laborales)
            else:
                arl = 0
                
            if ccf != 'Ninguna':
                ccf = ibc * 0.04  # Calcular el aporte a Caja de Compensación Familiar (CCF)
            else:
                ccf = 0

            calculosG = Calculos(
                documento=independiente,
                salud=salud,
                pension=pension,
                arl=arl,
                salarioBase=ibc,
                cajaCompensacion=ccf,
            )
            calculosG.save()  # Guardar los cálculos

            context = {
                'independiente': independiente,
                'salario_base': salario_base,
                'ibc': ibc,
                'salud': salud,
                'pension': pension,
                'arl': arl,
                'ccf': ccf,
            }
            return render(request, 'independientes/resultado_calculos.html', context)  # Renderizar la plantilla con los resultados

        else:
            form = DatosCalculosForm()  # Crear una instancia vacía del formulario

        return render(request, 'independientes/calcular_aportes.html', {'form': form, 'independiente': independiente})  # Renderizar la plantilla con el formulario

    # def calcular_fsp(ibc):
    #         smmlv = 1300000  
    #         if 4 * smmlv <= ibc < 16 * smmlv:
    #             return ibc * 0.01
    #         elif 16 * smmlv <= ibc < 17 * smmlv:
    #             return ibc * 0.012
    #         elif 17 * smmlv <= ibc < 18 * smmlv:
    #             return ibc * 0.014
    #         elif 18 * smmlv <= ibc < 19 * smmlv:
    #             return ibc * 0.016
    #         elif 19 * smmlv <= ibc < 20 * smmlv:
    #             return ibc * 0.018
    #         elif ibc >= 20 * smmlv:
    #             return ibc * 0.02
    #         else:
    #             return 0

    def calcular_arl(ibc, arl_nivel):
        # Calcular el aporte a ARL (Riesgos Laborales) basado en el nivel
        if arl_nivel == '1':
            arl = ibc * 0.00522
        elif arl_nivel == '2':
            arl = ibc * 0.01044
        elif arl_nivel == '3':
            arl = ibc * 0.02436
        elif arl_nivel == '4':
            arl = ibc * 0.04350
        elif arl_nivel == '5':
            arl = ibc * 0.06960
        elif arl_nivel == '0':
            arl = 0
        return arl

    def HistorialNomina(request, documento):
        empleado = get_object_or_404(Independiente, pk=documento)  # Obtener el Independiente o retornar 404 si no existe

        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()  # Convertir la fecha a un objeto de fecha

        calculos_empleado = Calculos.objects.filter(documento=empleado, fecha_calculos=fecha)  # Obtener los cálculos para la fecha específica

        calculo = calculos_empleado.first()  # Obtener el primer cálculo (asumiendo uno por fecha)

        salario_total = (
            (calculo.salarioBase if calculo.salarioBase else 0.0)  - (
                (calculo.pension if calculo.pension else 0.0) +
                (calculo.arl if calculo.arl else 0.0) +
                (calculo.cajaCompensacion if calculo.cajaCompensacion else 0.0) +
                (calculo.FSP if calculo.FSP else 0.0))
        )
        salario_pagar = (
            ((calculo.salud if calculo.salud else 0.0) +
            (calculo.pension if calculo.pension else 0.0) +
            (calculo.arl if calculo.arl else 0.0) +
            (calculo.cajaCompensacion if calculo.cajaCompensacion else 0.0) +
            (calculo.FSP if calculo.FSP else 0.0))
        )

        context = {
            'fecha': calculo.fecha_calculos,
            'empleado': empleado,
            'salud': calculo.salud,
            'pension': calculo.pension,
            'arl': calculo.arl,
            'transporte': calculo.transporte,
            'sena': calculo.sena,
            'ICBF': calculo.icbf,
            'CajaCompensa': calculo.cajaCompensacion,
            'cesantias': calculo.cesantias,
            'intereses_cesantias': calculo.interesCesantias,
            'valor_vacaciones': calculo.vacaciones,
            'dias_vacaciones': calculo.dias_vacaciones,
            'HorasExDiu': calculo.HorasExDiu,
            'HorasExNoc': calculo.HorasExNoc,
            'HorasExFestivaDiu': calculo.HorasExFestivaDiu,
            'HorasExFestivaNoc': calculo.HorasExFestivaNoc,
            'recargoDiuFes': calculo.recargoDiuFes,
            'recargoNoc': calculo.recargoNoc,
            'recargoNocFest': calculo.recargoNocFest,
            'salario_total': salario_total,
            'salario_pagar': salario_pagar,
        }

        return render(request, 'empresarial/historialNomina.html', context)  # Renderizar la plantilla con el contexto

    def obtener_todos_los_calculos(request, numero_identificacion):
        empleado = get_object_or_404(Independiente, pk=numero_identificacion)  # Obtener el Independiente o retornar 404 si no existe
        todos_los_calculos = Calculos.objects.filter(documento=empleado)  # Obtener todos los cálculos para el Independiente

        # Preparar el contexto
        context = {
            'calculos': todos_los_calculos,
            'empleado': numero_identificacion
        }

        # Renderizar la plantilla con el contexto
        return render(request, 'empresarial/HistoricoGeneral.html', context)  # Renderizar la plantilla con todos los cálculos
