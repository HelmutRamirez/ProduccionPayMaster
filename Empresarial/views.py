
import calendar
from datetime import date, datetime
from decimal import Decimal
from django.db.models import Sum,Q
from django.utils import timezone # type: ignore
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View # type: ignore
from Empresarial.forms import CargoForm, ContratoForm, CrearUsuarioForm, EmpresaForm, EmpleadoForm,LoginForm, NivelGradoForm, PasswordResetForm, PorcentajesLegalesForm,RecuperarContrasenaForm,HorasExtrasRecargos, UsuarioForm
from .models import Cargo, Contrato, Empresa, Empleado, NivelGrado, PorcentajesLegales, Usuarios, Liquidacion,PasswordResetRequest, vacacionesCesantias
from django.core.mail import send_mail # type: ignore
from django.template.loader import render_to_string # type: ignore
from django.utils.html import strip_tags # type: ignore
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, JsonResponse, HttpResponseRedirect # type: ignore
import secrets
from django.contrib import messages # type: ignore
from django.contrib.auth import logout # type: ignore
from django.utils.http import urlsafe_base64_decode # type: ignore
from django.utils.encoding import force_str # type: ignore
from django.http import JsonResponse # type: ignore
from django.views.decorators.http import require_POST # type: ignore
import re
from django.contrib.humanize.templatetags.humanize import intcomma

from Empresarial import models



class GestionLogin:

    @staticmethod
    def recuperar_contrasena(request):
        if request.method == 'POST':
            form = RecuperarContrasenaForm(request.POST)  # Crear una instancia del formulario con los datos POST
            if form.is_valid():
                numero_identificacion_e = form.cleaned_data['numero_identificacion']  # Obtener el numero de identificacion del formulario

                try:
                    usuario = Empleado.objects.get(numero_identificacion_e=numero_identificacion_e)  # Buscar al usuario por su número de identificación

                    # Crear una solicitud de recuperación de contraseña y guardarla en la base de datos
                    solicitud = PasswordResetRequest(usuario=usuario, token=GestionLogin.generate_token())
                    solicitud.save()

                    # Enviar el correo electrónico con el token para restablecer la contraseña
                    subject = 'Recuperación de Contraseña'
                    html_message = render_to_string('empresarial/email/recuperacion_contrasena.html', {'usuario': usuario, 'token': solicitud.token})
                    plain_message = strip_tags(html_message)
                    from_email = 'p4ym4ster@gmail.com'  # Cambiar por tu dirección de correo
                    to_email = usuario.correo
                    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

                    messages.success(request, 'Se ha enviado un correo electrónico con el token para restablecer tu contraseña.')
                    return redirect('password_reset_empre')  # Redirigir a la página para ingresar el token

                except Empleado.DoesNotExist:
                    messages.error(request, 'No se encontró un usuario con ese número de identificación.')

        else:
            form = RecuperarContrasenaForm()  # Crear una instancia vacía del formulario

        return render(request, 'empresarial/recuperar_contrasena.html', {'form': form})  # Renderizar la plantilla con el formulario

    def password_reset(request):
        if request.method == 'POST':
            form = PasswordResetForm(request.POST)  # Crear una instancia del formulario con los datos POST
            if form.is_valid():
                token = form.cleaned_data['token']
                new_password = form.cleaned_data['new_password']
                confirm_password = form.cleaned_data['confirm_password']
                
                try:
                    reset_request = PasswordResetRequest.objects.get(token=token, used=False)  # Buscar la solicitud de restablecimiento de contraseña por el token y que no haya sido usada
                except PasswordResetRequest.DoesNotExist:
                    reset_request = None
                #aca se se hace la validacion de la contraseña para que se le aplique 
                if new_password != confirm_password:
                    messages.error(request, 'Las contraseñas no coinciden.')
                else:
                    if len(new_password) < 6:
                        messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
                    elif not re.search(r'[A-Za-z]', new_password):# el re.search busca un patrón dentro de una cadena.
                        messages.error(request, 'La contraseña debe contener al menos una letra.')
                    elif not re.search(r'[A-Z]', new_password):
                        messages.error(request, 'La contraseña debe contener al menos una letra mayúscula.')
                    elif not re.search(r'\d', new_password):
                        messages.error(request, 'La contraseña debe contener al menos un número.')
                    elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
                        messages.error(request, 'La contraseña debe contener al menos un carácter especial.')
                    elif reset_request:
                        usuario = reset_request.usuario  # Ajusta según tu modelo de PasswordResetRequest
                        usuario = Usuarios.objects.get(usuario=usuario)
                        
                        usuario.set_password(new_password)  # Establecer la nueva contraseña

                        reset_request.used = True
                        reset_request.save()

                        usuario.intentos = 0
                        usuario.estado_u = True
                        usuario.save()
                        
                        messages.success(request, 'Contraseña actualizada correctamente. Por favor, inicia sesión.')
                        return redirect('loginEmpresa')  # Redirige a la página de inicio de sesión después de cambiar la contraseña
                    else:
                        messages.error(request, 'El token de restablecimiento de contraseña no es válido o ya ha sido utilizado.')
            else:
                messages.error(request, 'Por favor, corrige los errores del formulario.')
        else:
            form = PasswordResetForm()  # Crear una instancia vacía del formulario

        return render(request, 'empresarial/password_reset.html', {'form': form})  # Renderizar la plantilla con el formulario

    @staticmethod
    def generate_token():
        # Generar un token único y seguro
        return secrets.token_urlsafe(20)

    def login_view(request):
        if request.method == 'POST':
            form = LoginForm(request.POST)  # Crear una instancia del formulario con los datos POST
            if form.is_valid():
                numero_identificacion_e = form.cleaned_data['numero_identificacion']
                contrasena = form.cleaned_data['contrasena']

                try:
                    # Buscar el usuario por su número de identificación o por su ID de usuario
                    usuario = Usuarios.objects.get(
                        Q(usuario__numero_identificacion_e=numero_identificacion_e) | 
                        Q(pk=numero_identificacion_e)
                    )

                    # Obtener los datos del empleado asociado
                    #indepe = Empleado.objects.get(pk=numero_identificacion_e)
                    permisos = usuario.rol
                    userName = usuario.rol

                    if usuario.estado_u:
                        if usuario.check_password(contrasena):  # Verificar la contraseña
                            usuario.intentos = 0
                            usuario.save()

                            # Guardar información en la sesión
                            request.session['numero_identificacion_e'] = numero_identificacion_e
                            request.session['estadoSesion'] = True
                            request.session['permisos'] = permisos
                            request.session['user'] = userName

                            # Redirigir según el rol del usuario
                            if permisos in ['ContadorL', 'Auxiliar Contable', 'RRHHL', 'Admin','RRHH']:
                                return redirect('ListarEmpresa')  # Redirigir a la lista de empresas
                            elif permisos == 'Empleado General':
                                return redirect('homeEmpleado', numero_identificacion_e=numero_identificacion_e)  # Redirigir a la página de inicio del empleado

                        else:
                            usuario.intentos += 1
                            usuario.save()
                            if usuario.intentos >= 3:
                                usuario.estado_u = False
                                usuario.save()
                                messages.error(request, 'La cuenta ha sido inhabilitada debido a múltiples intentos fallidos de inicio de sesión.')
                            else:
                                messages.error(request, 'Número de identificación o contraseña incorrectos.')
                    else:
                        messages.error(request, 'La cuenta está inhabilitada.')

                except Usuarios.DoesNotExist:
                    messages.error(request, 'El usuario no existe.')

        else:
            form = LoginForm()  # Crear una instancia vacía del formulario

        return render(request, 'empresarial/login.html', {'form': form})  # Renderizar la plantilla con el formulario



    def cerrar_sesion(request):
        # Función para cerrar la sesión del usuario mediante una solicitud POST
        if request.method == 'POST':
            logout(request)  # Cierra la sesión actual del usuario
            request.session.flush()  # Limpia todos los datos de la sesión
            return JsonResponse({'status': 'ok'})  # Retorna un JSON de estado exitoso
        return JsonResponse({'status': 'error'}, status=400)  # Retorna un JSON de error si no es POST

    def cerrar_sesion_redirect(request):
        # Función para cerrar la sesión del usuario y redirigir a la página de login
        logout(request)  # Cierra la sesión actual del usuario
        request.session.flush()  # Limpia todos los datos de la sesión
        return redirect('loginEmpresa')  # Redirige a la vista 'loginEmpresa'

    def keep_session_alive(request):
        # Función para verificar si la sesión del usuario está activa mediante una solicitud GET
        if request.method == 'GET':
            return JsonResponse({'status': 'Session is alive'})  # Retorna un JSON indicando que la sesión está activa
        else:
            return JsonResponse({'status': 'Method not allowed'}, status=405)  # Retorna un JSON de error si no es GET




class Paginas(HttpRequest):
    def home(request): 
        return render(request, 'empresarial/home.html')  # Renderiza la página 'home.html'
    
    def homeEmpleado(request, numero_identificacion_e): 
        indepe = Empleado.objects.get(pk=numero_identificacion_e)
        data = {'independi': indepe}
        return render(request, 'empresarial/Empleado.html', data)  # Renderiza 'Empleado.html' con datos del empleado identificado por 'numero_identificacion_e'
    
    def homeEmpresa(request):
        numero_identificacion_e = request.session.get('numero_identificacion_e')
        try:
            independi = Empleado.objects.get(pk=numero_identificacion_e)
            return render(request, 'empresarial/homeEmpresa.html', {'independi': independi})  # Renderiza 'homeEmpresa.html' con datos del empleado en sesión
        except Empleado.DoesNotExist:
            messages.error(request, 'No se encontró el perfil de Empleado asociado')
            return redirect('loginEmpresa')  # Redirige a 'loginEmpresa' si no existe el perfil del empleado

class GestionEmpleado(HttpRequest):
    
    def ListarTodosEmpleados(request):
        get_empleados = Empleado.objects.all()
       
        return render(request, 'empresarial/todosEmpleados.html', {'get_empleados': get_empleados})
        # Renderiza la lista de empresas ('listarEmpresa.html')
    
    
   
    def crearEmpleado(request, nit):
        empresa = get_object_or_404(Empresa, nit=nit)  

        if request.method == 'POST':
            formulario = EmpleadoForm(request.POST, request.FILES)
            if formulario.is_valid():
                empleado = formulario.save(commit=False)
                id_empleado=empleado.numero_identificacion_e
                empleado.nit = empresa  # Asigna la empresa al empleado
                empleado.save()
                raw_password = empleado.primer_nombre + str(empleado.numero_identificacion_e) + '@'
                usuario = Usuarios(
                    usuario=empleado,
                    intentos=0,
                    estado_u=False,
                    rol='Empleado General'
                )
                usuario.set_password(raw_password)
                usuario.save()
                subject = 'Bienvenido a PayMaster'
                html_message = render_to_string('empresarial/email/envio_credencial.html', {'usuario': empleado })
                plain_message = strip_tags(html_message)  # Convertir el mensaje HTML a texto plano
                from_email = 'p4ym4ster@gmail.com'  # Cambiar por tu dirección de correo
                to_email = empleado.correo  # Dirección de correo del destinatario
                send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)  # Enviar el correo
                
                return redirect('registContrat', id_empleado)
        else:
            formulario = EmpleadoForm(initial={'nit': empresa.nit})  # Inicializa el formulario con el valor de la empresa

        return render(request, 'empresarial/registroEmpleado.html', {'form': formulario, 'mensaje': 'ok', 'empresa': empresa})
        

    def EmpleadosContratar(request,nit):
        empresa=Empresa.objects.get(pk=nit)
        empleados_sin_empresa = Empleado.objects.filter(nit__isnull=True)
        empleados_filtrados = []

        for empleado in empleados_sin_empresa:
            caractere = len(empleado.numero_identificacion_e)
            if caractere > 6:
                empleados_filtrados.append(empleado)

        data = {
            'get_empleados': empleados_filtrados,
            'empresa':empresa
        }

        return render(request, 'empresarial/listadoEmpleados.html', data)
    def Contratacion(request, numero_identificacion_e, nit):
    
        empleado = Empleado.objects.get(pk=numero_identificacion_e)
        empresa = Empresa.objects.get(nit=nit)
        
        empleado.nit = empresa
        empleado.save() 
        
        return redirect('empleadoss',nit)
    #########################################################
    
    def eliminarEmpleado(request, numero_identificacion_e):
    
        empleado = Empleado.objects.get(pk=numero_identificacion_e)
        
        # Eliminar el empleado
        empleado.delete()
        
        return redirect('listarTodosEmpleados') 
    
          
    def DesvincularEmpelado(request, numero_identificacion_e):
        empleado = Empleado.objects.get(pk=numero_identificacion_e)
        empresa = empleado.nit.nit
        empleado.nit= None
        empleado.save()  
        usuario=Usuarios.objects.get(usuario=numero_identificacion_e)
        usuario.estado_u=False
        usuario.save()
        return redirect('ListarEmpleados', nit=empresa)  
    
    
        
    def ListarEmpleados(request, nit):
        try:
            # Obtén la empresa por su NIT
            empresa = Empresa.objects.get(pk=nit)
            
            # Filtra los empleados por la empresa
            get_empleados = Empleado.objects.filter(nit=empresa)
        
            empleados_con_antiguedad = []
            for empleado in get_empleados:
                try:
                    # Filtra los contratos activos del empleado para la empresa y obtiene el más reciente
                    contrato_activo = Contrato.objects.filter(
                        numero_identificacion_e=empleado,
                        empresa=empresa
                        
                    ).latest('fecha_inicio')  # Asegúrate de tener contratos activos
                    
                    # Extrae la información del contrato
                    estado_contrato = contrato_activo.estado
                    numero_identificacion = contrato_activo.numero_identificacion_e.numero_identificacion_e
                    
                    # Calcula la antigüedad solo si es necesario
                    a, b, antiguedad_dias = CalculosGenerales.diasTrabajados(contrato_activo.fecha_inicio)
                    
                    empleados_con_antiguedad.append({
                        'empleado': empleado,
                        'antiguedad': antiguedad_dias,
                        'estado': estado_contrato,
                        'numero_identificacion': numero_identificacion  # Añadido
                    })
                except Contrato.DoesNotExist:
                    # Si no hay contratos activos, agrega un registro con 'Sin informacion'
                    empleados_con_antiguedad.append({
                        'empleado': empleado,
                        'antiguedad': 'Sin informacion',
                        'estado': 'Sin informacion',
                        'numero_identificacion': 'Sin informacion'  # Añadido
                    })
            
            data = {
                'empleados_con_antiguedad': empleados_con_antiguedad,
                'empresa': empresa
            }
            
            return render(request, 'empresarial/listarEmpleado.html', data)
        except Empresa.DoesNotExist:
            # Manejo del error si la empresa no existe
            return HttpResponse("La empresa con el NIT proporcionado no existe.")


            
    def editarEmpleado(request, numero_identificacion_e):
        empleado = Empleado.objects.get(pk=numero_identificacion_e)
        formulario = EmpleadoForm(instance=empleado)
        nit=empleado.nit.nit
        empresa=Empresa.objects.get(pk=nit)
        return render(request, 'empresarial/editarEmpleado.html', {"form": formulario, "empleado": empleado, "numero_identificacion_e": numero_identificacion_e,'empresa':empresa})
        # Renderiza el formulario de edición de empleado ('editarEmpleado.html')

    def actualizarEmpleado(request, numero_identificacion_e):
        empleado = Empleado.objects.get(pk=numero_identificacion_e)
        formulario = EmpleadoForm(request.POST, instance=empleado)
        empresa = empleado.nit.nit

        if formulario.is_valid():
            formulario.save()
        
        return redirect('ListarEmpleados', empresa)
    
    def get_salario_minimo(request, cargo_id):
        try:
            cargo = Cargo.objects.get(id_cargo=cargo_id)
            return JsonResponse({'salario_minimo': str(cargo.salario_minimo)})
        except Cargo.DoesNotExist:
            return JsonResponse({'salario_minimo': ''})
        
        
        
    def registroContrato(request, numero_identificacion_e):
        empleado = Empleado.objects.get(pk=numero_identificacion_e)
        empresa = empleado.nit  

        
        if request.method == 'GET':
            formulario = ContratoForm()  

       
        elif request.method == 'POST':
            formulario = ContratoForm(request.POST, request.FILES)
            if formulario.is_valid():
                
                contrato = formulario.save(commit=False)
                contrato.estado = 'Activo'
                contrato.numero_identificacion_e = empleado  
                contrato.empresa = empresa 
                contrato.save() 
                
               
                return redirect('ListarEmpleados', empresa.nit)  

        return render(request, 'empresarial/registroContrato.html', {'form': formulario, 'mensaje': 'ok', 'id_empleado': numero_identificacion_e, 'empresa': empresa})

            
    def cancelarContrato(request, numero_identificacion_e):
        empleado = Empleado.objects.get(pk=numero_identificacion_e)
        nit=empleado.nit
        empresa = empleado.nit.nit
        contrato = Contrato.objects.get(numero_identificacion_e=numero_identificacion_e,empresa=nit)
      
        contrato.estado='Inactivo'
        contrato.fecha_fin=datetime.now()
        contrato.save()
        return redirect('ListarEmpleados', nit=empresa)

class GestionarEmpresa(HttpRequest):
    
    def crearEmpresa(request):
        formulario = EmpresaForm(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            formulario = EmpresaForm()
            return redirect('ListarEmpresa')
        return render(request, 'empresarial/registroEmpresa.html', {'form': formulario, 'mensaje': 'ok'})
        # Renderiza el formulario de registro de empresa ('registroEmpresa.html')

    def ListarEmpresa(request):
        get_empresa = Empresa.objects.all()
        data = {
            'get_empresa': get_empresa
        }
        return render(request, 'empresarial/listarEmpresa.html', data)
        # Renderiza la lista de empresas ('listarEmpresa.html')

    def editarEmpresa(request, nit):
        empresa = Empresa.objects.get(pk=nit)
        formulario = EmpresaForm(instance=empresa)
        return render(request, 'empresarial/editarEmpresa.html', {"form": formulario, "empresa": empresa})
        # Renderiza el formulario de edición de empresa 

    def actualizarEmpresa(request, nit):
        empresa = Empresa.objects.get(pk=nit)
        formulario = EmpresaForm(request.POST, instance=empresa)
        if formulario.is_valid():
            formulario.save()
        empresas = Empresa.objects.all()
        return render(request, 'empresarial/listarEmpresa.html', {"get_empresa": empresas})
        # Actualiza los datos de la empresa y luego renderiza la lista actualizada de empresas 

   
    def eliminarEmpresa(request, nit):
        empresa  = Empresa.objects.get(pk=nit)
        empleados = Empleado.objects.filter(nit=nit)
    
        for emplea in empleados:
            emplea.nit= None
            emplea.save()  
           
        empresa.delete()
        return redirect('ListarEmpresa')
        
        

    
class CalculosGenerales(HttpRequest):
    porcentaje= PorcentajesLegales.objects.filter(vigente=True).first()
   
    
    def calcularSalario(request, numero_identificacion_e):
       
        # Obtener el empleado por su número de identificación
        empleado = get_object_or_404(Empleado, pk=numero_identificacion_e)
            
            # Obtener la empresa asociada al empleado
        empresa = get_object_or_404(Empresa, pk=empleado.nit.pk)
            
            # Filtrar contratos del empleado por empresa y estado activo
        contrato = Contrato.objects.filter(
                numero_identificacion_e=empleado,
                empresa=empresa,
                estado='Activo'
            ).order_by('-fecha_inicio').first()
            

        # Verificar si ya existe un cálculo para este mes
        hoy = datetime.now()
        mes_actual = hoy.month
        anio_actual = hoy.year
        
        # existe_calculo = Liquidacion.objects.filter(
        #     numero_identificacion_e=empleado,
        #     fecha_calculo__year=anio_actual,
        #     fecha_calculo__month=mes_actual
        # ).exists()
        
        
        
        # Si no existe el cálculo, procedemos a realizarlo
        dias_trabajados = contrato.fecha_inicio
        dias_trabajados_anteriores, dias_trabajados_actuales, dias_antiguedad = CalculosGenerales.diasTrabajados(dias_trabajados)
        salario_base = contrato.salario_asignado
        transporte = CalculosGenerales.auxilioTrasnporte(salario_base)
       
        
        # Cálculo de aportes a seguridad social
        salario_base = Decimal(salario_base)
        salario_base_sin_trasnpo = salario_base
        salario_base = Decimal(salario_base)
        transporte = Decimal(transporte)
        salario_base_transpor = salario_base + transporte
        salario_base_sin_trasnpo = Decimal(salario_base_sin_trasnpo)
        
        salud = salario_base_sin_trasnpo * CalculosGenerales.porcentaje.salud_empleado
        salud_empleador = salario_base_sin_trasnpo * CalculosGenerales.porcentaje.salud_empresa
        
        pension = salario_base_sin_trasnpo * CalculosGenerales.porcentaje.pension_empleado
        pension_empleador = salario_base_sin_trasnpo * CalculosGenerales.porcentaje.pension_empresa # Aportes adicionales del empleador
        
            
        # Obtener el cargo del contrato
        # Obtener el objeto Cargo desde el contrato
        cargo = contrato.id_cargo  # Aquí 'cargo' es un objeto Cargo

        # Obtener el nivel de riesgo del objeto Cargo
        nivel_riesgo_numero = int(cargo.nivel_riesgo)

        # Usar el nivel de riesgo en el cálculo del ARL
        arl = CalculosGenerales.nivelRiesgo(salario_base, nivel_riesgo_numero)
                

        
        # # Cálculo de novedades
        # horas_extras = CalculosGenerales.horasExtras(salario_base, empleado)
        # horas_extras_diurnas = horas_extras['diurna']
        # horas_extras_nocturnas = horas_extras['nocturna']
        # horas_extras_diurnas_festivas = horas_extras['diurna_festiva']
        # horas_extras_nocturnas_festivas = horas_extras['nocturna_festiva']
        
        # recargo1 = 0
        # recargo2 = 0
        # recargo3 = 0
        
        
        cesantias, intereses_cesantias = CalculosGenerales.calculoCesantias(salario_base_sin_trasnpo, dias_trabajados_actuales)
        dias_vacaciones, valor_vacaciones = CalculosGenerales.calculoVacaciones(salario_base_sin_trasnpo, dias_antiguedad)
        
        # Cálculo de aportes parafiscales
        sena, icbf, cajaCompensacion = CalculosGenerales.prestacionesSociales(salario_base)
        
        # Guardar el cálculo en la base de datos
        salud = Decimal(salud)
        pension = Decimal(pension)
        salario_base_transporte = Decimal(salario_base_transpor)

        total = salario_base_transporte - salud - pension
        
        calculos = Liquidacion(
            fecha_inicio=datetime(anio_actual, mes_actual, 1),
            fecha_fin=datetime(anio_actual, mes_actual, calendar.monthrange(anio_actual, mes_actual)[1]),
            fecha_calculo=hoy,
            salud_empleado=salud,
            pension_empleado=pension,
            salud_empresa=salud_empleador,
            pension_empresa=pension_empleador,
        
            arl=arl,
            caja_compensacion=cajaCompensacion,
            vacaciones=valor_vacaciones,
            cesantias=cesantias,
            intereses_cesantias=intereses_cesantias,
            numero_identificacion_e=empleado,

            total_antes_deducciones=salario_base_sin_trasnpo,
            total_final=total,
            empresa=empresa
            # Se guarda la fecha actual como fecha de cálculo
            # HorasExDiu=horas_extras_diurnas,
            # HorasExNoc=horas_extras_nocturnas,
            # HorasExFestivaDiu=horas_extras_diurnas_festivas,
            # HorasExFestivaNoc=horas_extras_nocturnas_festivas,
            # recargoDiuFes=recargo1,
            # recargoNoc=recargo2,
            # recargoNocFest=recargo3,
           
        )
        
        calculos.save()
        
        vacaciones_cesantias, created = vacacionesCesantias.objects.get_or_create(
        numero_identificacion_e=empleado,  
        defaults={
            'vacaciones_acumulado': Decimal(valor_vacaciones),
            'cesantias_acumuladas': Decimal(cesantias),
            'intereses_cesantias': Decimal(intereses_cesantias),
            'antiguedad': dias_antiguedad,
            'dias_vacaciones': dias_vacaciones
            }
        )   

        if not created:
            vacaciones_cesantias.vacaciones_acumulado += Decimal(valor_vacaciones)
            vacaciones_cesantias.cesantias_acumuladas += Decimal(cesantias)
            vacaciones_cesantias.intereses_cesantias += Decimal(intereses_cesantias)
            vacaciones_cesantias.antiguedad += dias_antiguedad
            vacaciones_cesantias.dias_vacaciones += dias_vacaciones

            vacaciones_cesantias.save()
        
        context = {
            'calculos': calculos,
            'empresa': empresa,
            'empleadoC':empleado,
            'empleado': numero_identificacion_e,
            'salud': salud,
            'pension': pension,
            'arl': arl,
            'transporte': transporte,
            'sena': sena,
            'ICBF': icbf,
            'CajaCompensa': cajaCompensacion,
            'cesantias': cesantias,
            'intereses_cesantias': intereses_cesantias,
            'valor_vacaciones': valor_vacaciones,
            'antiguedad': dias_antiguedad,
            'dias_vacaciones': dias_vacaciones,
            # 'valor_horas_extras': horas_extras,
            'salario_total': total,
            'salud_empeador': salud_empleador,
            'pension_empleador': pension_empleador,
            'dias_antiguedad': dias_antiguedad,
            'dias_trabajados': dias_trabajados
        }
        
        return render(request, 'empresarial/resultado_calculo.html', context)
        # Renderiza la plantilla 'resultado_calculo.html' con el contexto generado

    # def horasExtras(salario, empleado):
    #     # Obtener el año y mes actual
    #     año_actual = timezone.now().year
    #     mes_actual = timezone.now().month
        
    #     # Consultar las horas extras registradas para el empleado en el mes actual
    #     horas_extras = Novedades.objects.filter(
    #         empleado=empleado,
    #         fecha_novedad__year=año_actual,
    #         fecha_novedad__month=mes_actual
    #     ).aggregate(
    #         total_horas_diu=Sum('HorasExDiu'),
    #         total_horas_noc=Sum('HorasExNoc'),
    #         total_horas_diu_fest=Sum('HorasExFestivaDiu'),
    #         total_horas_noc_fest=Sum('HorasExFestivaNoc')
    #     )
        
    #     salario = salario / 235  # Dividir el salario por el número de días laborales promedio al mes
        
    #     # Calcular el valor de las horas extras usando los porcentajes establecidos
    #     valor_horas_extras = {
    #         'diurna': (salario * 1.25) * (horas_extras['total_horas_diu'] or 0),
    #         'nocturna': (salario * 1.75) * (horas_extras['total_horas_noc'] or 0),
    #         'diurna_festiva': (salario * 2) * (horas_extras['total_horas_diu_fest'] or 0),
    #         'nocturna_festiva': (salario * 2.5) * (horas_extras['total_horas_noc_fest'] or 0)
    #     }
        
    #     return valor_horas_extras
    #     # Retorna un diccionario con los valores calculados para las horas extras

    def nivelRiesgo(salario_base, nivel_riesgo):
        # Calcula el valor del aporte a ARL basado en el nivel de riesgo
        salario_base = Decimal(salario_base)
        
        if nivel_riesgo == 1:
            arl = salario_base * CalculosGenerales.porcentaje.riesgo_laboral1
        elif nivel_riesgo == 2:
            arl = salario_base * CalculosGenerales.porcentaje.riesgo_laboral2
        elif nivel_riesgo == 3:
            arl = salario_base * CalculosGenerales.porcentaje.riesgo_laboral3
        elif nivel_riesgo == 4:
            arl = salario_base * CalculosGenerales.porcentaje.riesgo_laboral4
        elif nivel_riesgo == 5:
            arl = salario_base * CalculosGenerales.porcentaje.riesgo_laboral5
        else:
            arl = 0
        
        return arl
        # Retorna el cálculo del aporte a ARL basado en el nivel de riesgo proporcionado

    def auxilioTrasnporte(salario_base):
        # Calcula el valor del auxilio de transporte según el salario base
        if salario_base >= 1300000 and salario_base <= 2600000 and salario_base > 0:
            auxilio = CalculosGenerales.porcentaje.auxilio_transporte
        else:
            auxilio = 0
        
        return auxilio
        # Retorna el valor calculado del auxilio de transporte

    def prestacionesSociales(salario_base):
        # Calcula los valores de los aportes a SENA, ICBF y caja de compensación
        salario_base = Decimal(salario_base)
        porcentaje_sena = Decimal(CalculosGenerales.porcentaje.sena)
        porcentaje_icbf = Decimal(CalculosGenerales.porcentaje.icbf)
        porcentaje_caja_compensacion = Decimal(CalculosGenerales.porcentaje.caja_compensacion)

        sena = Decimal(0)
        icbf = Decimal(0)
        cajaCompensacion = Decimal(0)

        if salario_base >= Decimal(10000000) and salario_base > Decimal(0):
            sena = salario_base * porcentaje_sena
            icbf = salario_base * porcentaje_icbf
            cajaCompensacion = salario_base * porcentaje_caja_compensacion
        else:
            cajaCompensacion = salario_base * porcentaje_caja_compensacion

        return sena, icbf, cajaCompensacion
            # Retorna los valores calculados para SENA, ICBF y caja de compensación

    def diasTrabajados(fecha_ingreso):
        # Verifica si fecha_ingreso es datetime.date y conviértelo a str si es necesario
        if isinstance(fecha_ingreso, date):
            fecha_ingreso = fecha_ingreso.strftime("%d-%m-%Y")
        
        # Convierte la fecha_ingreso de string a objeto datetime
        fecha_ingresada = datetime.strptime(fecha_ingreso, "%d-%m-%Y")
        
        # Obtiene la fecha de hoy
        hoy = datetime.today()
        
        # Calcula la diferencia en días entre hoy y la fecha ingresada
        dias_diferencia = (hoy - fecha_ingresada).days
        
        if dias_diferencia > 0:
            dias_diferencia -= 1
        
        # Establece la fecha de referencia
        fecha_referencia = datetime(hoy.year, 1, 1)
        
        # Inicializa variables
        dias_trabajados_anteriores = 0
        dias_trabajados_actuales = 0
        
        # Clasifica los días trabajados
        if fecha_ingresada < fecha_referencia:
            dias_trabajados_anteriores = (fecha_referencia - fecha_ingresada).days
            dias_trabajados_actuales = dias_diferencia - dias_trabajados_anteriores
        else:
            dias_trabajados_actuales = dias_diferencia
        
        return dias_trabajados_anteriores, dias_trabajados_actuales, dias_diferencia
        # Retorna el número de días trabajados antes del año actual, días trabajados en el año actual y la antigüedad

    def calculoCesantias(salario_base_transpor, dias_trabajados_actuales):
        # Calcula el valor de las cesantías e intereses de cesantías
        cesantias = (salario_base_transpor * dias_trabajados_actuales) / CalculosGenerales.porcentaje.cesantias
        interes_cesantias = (cesantias * dias_trabajados_actuales * CalculosGenerales.porcentaje.intereses_cesantias) / 360
        
        return cesantias, interes_cesantias
        # Retorna el valor calculado de las cesantías e intereses de cesantías

    def calculoVacaciones(salario_base, dias_antiguedad):
        # Calcula los días y el valor de las vacaciones basado en el salario base y la antigüedad
        salario_base = Decimal(salario_base)  
        vacaciones_porcentaje = Decimal(CalculosGenerales.porcentaje.vacaciones)  

        # Calcular valor_dia y convertir a Decimal
        valor_dia = salario_base / Decimal(30)
        dias_antiguedad = Decimal(dias_antiguedad)  
        dias_vaciones = (dias_antiguedad / Decimal(360)) * vacaciones_porcentaje

        # Calcular valor_vacciones
        valor_vacciones = valor_dia * dias_vaciones
        return dias_vaciones, valor_vacciones
        # Retorna el número de días de vacaciones y el valor calculado de las vacaciones

    # def registroNovedades(request, numero_identificacion_e):
    #     empleado = get_object_or_404(Empleado, pk=numero_identificacion_e)
        
    #     if request.method == 'POST':
    #         formularioNov = HorasExtrasRecargos(request.POST)
            
    #         if formularioNov.is_valid():
    #             novedad = formularioNov.save(commit=False)
    #             novedad.empleado = empleado
    #             novedad.fecha_novedad = timezone.now()
                
    #             # Obtén el límite máximo de horas permitido
    #             limite_maximo_horas = 48
                
    #             # Calcula la suma total de horas considerando los campos llenados en el formulario
    #             suma_total = Novedades.objects.filter(
    #                 empleado=empleado,
    #                 fecha_novedad__year=timezone.now().year,
    #                 fecha_novedad__m
    #                 onth=timezone.now().month
    #             ).aggregate(
    #                 total_horas=Sum('HorasExDiu') + Sum('HorasExNoc') +
    #                             Sum('HorasExFestivaNoc') + Sum('HorasExFestivaDiu')
    #             )['total_horas'] or 0
                
    #             # Verifica si la suma total más el nuevo registro excede el límite máximo de horas
    #             if (suma_total or 0) + (novedad.HorasExDiu or 0) + (novedad.HorasExNoc or 0) + \
    #             (novedad.HorasExFestivaNoc or 0) + (novedad.HorasExFestivaDiu or 0) > limite_maximo_horas:
    #                 error_message = f"La suma de horas excede el límite máximo permitido de {limite_maximo_horas} horas en el mes."
    #                 return render(request, 'empresarial/HorasExtrasRecargos.html', {'formularioNov': formularioNov, 'error_message': error_message, 'empleado': empleado})
                
    #             novedad.save()
    #             return redirect('ListarEmpleados', nit=empleado.empresa.nit)
        
    #     else:
    #         formularioNov = HorasExtrasRecargos()
        
    #     return render(request, 'empresarial/HorasExtrasRecargos.html', {'formularioNov': formularioNov, 'empleado': empleado})
    #     # Renderiza la plantilla 'HorasExtrasRecargos.html' con el formulario para registrar novedades

    def HistorialNomina(request, documento, fecha):
        empleado = get_object_or_404(Empleado, pk=documento)
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        calculos_empleado = Liquidacion.objects.filter(numero_identificacion_e=empleado, fecha_calculo=fecha)
        empresa = empleado.nit
        calculo = calculos_empleado.first()
        contrato = Contrato.objects.filter(numero_identificacion_e=empleado).first()
        he = HorasExtrasRecargos.objects.filter(empleado=empleado).first()
        
        salario_total = (
            (Decimal(contrato.salario_asignado) if contrato.salario_asignado else Decimal(0)) +
            ((calculo.salud_empleado if calculo.salud_empleado else Decimal(0)) + 
            (calculo.pension_empleado if calculo.pension_empleado else Decimal(0)))
        )
   
        dias_trabajados = contrato.fecha_inicio
        dias_trabajados_anteriores, dias_trabajados_actuales, dias_antiguedad = CalculosGenerales.diasTrabajados(dias_trabajados)
        vacacionesCesa=vacacionesCesantias.objects.filter(numero_identificacion_e=empleado).first()
        dias_vacaciones=vacacionesCesa.dias_vacaciones
        transporte=162000
       
        transporte_formatted = f"$ {intcomma(transporte)}"
       
        context = {
            'empresa': empresa,
            'fecha': calculo.fecha_calculo,
            'empleado': empleado,
            'salud': calculo.salud_empleado,
            'pension': calculo.pension_empleado,
            'arl': calculo.arl,
            'cesantias': calculo.cesantias,
            'intereses_cesantias': calculo.intereses_cesantias,
            'valor_vacaciones': calculo.vacaciones,
            'dias_vacaciones': dias_vacaciones,
            'antiguedad':dias_antiguedad,
            'fecha_ingreso':contrato.fecha_inicio,
            'transporte':transporte_formatted,
            'salud_empre':calculo.salud_empresa,
            'pension_empre':calculo.pension_empresa,
            'CajaCompensa':calculo.caja_compensacion,
            # 'HorasExDiu': calculo.HorasExDiu,
            # 'HorasExNoc': calculo.HorasExNoc,
            # 'HorasExFestivaDiu': calculo.HorasExFestivaDiu,
            # 'HorasExFestivaNoc': calculo.HorasExFestivaNoc,
            # 'recargoDiuFes': calculo.recargoDiuFes,
            # 'recargoNoc': calculo.recargoNoc,
            # 'recargoNocFest': calculo.recargoNocFest,
            'salario_total': salario_total,
            'calculo': calculo
        }
        
        return render(request, 'empresarial/historialNomina.html', context)
        # Renderiza la plantilla 'historialNomina.html' con el historial de nómina del empleado para la fecha especificada

    def obtener_todos_los_calculos(request, numero_identificacion_e):
        empleado = get_object_or_404(Empleado, pk=numero_identificacion_e)
        nit=empleado.nit
        todos_los_calculos = Liquidacion.objects.filter(numero_identificacion_e=empleado,empresa=nit)
        nit = empleado.nit
       
        # Prepara el contexto
        context = {
            'calculos': todos_los_calculos,
            'empleado': empleado,
            'empresa': nit
        }
        
        # Renderiza la plantilla 'HistoricoGeneral.html' con el contexto generado
        return render(request, 'empresarial/HistoricoGeneral.html', context)

        
class GestionUsuarios(HttpRequest):
    
    
    def listar_usuarios(request):
        usuarios = Usuarios.objects.all()
        return render(request, 'empresarial/gestionGeneral.html', {'usuarios': usuarios})
    
    def crear_usuario(request):
        if request.method == 'POST':
            form = CrearUsuarioForm(request.POST)
            if form.is_valid():
                form.save()  # Guardar el usuario con la contraseña encriptada
                return redirect('listar_usuarios')  # Redirige a la lista de usuarios (ajusta la URL si es necesario)
        else:
            form = CrearUsuarioForm()

        return render(request, 'empresarial/registroUsuarios.html', {'form': form})
    
    def modificarUsuario(request, id_usu):
        usuario = get_object_or_404(Usuarios, pk=id_usu)

        if request.method == 'POST':
            form = UsuarioForm(request.POST, instance=usuario)
            if form.is_valid():
                form.save()
                return redirect('listar_usuarios') 
        else:
            form = UsuarioForm(instance=usuario)

        return render(request, 'empresarial/modificacionUsuarios.html', {'form': form, 'usuario': usuario})
    
class Porcentajes(HttpRequest):   
    
    def listar_porcentajes_legales(request):
        porcentajes_legales = PorcentajesLegales.objects.all()
        return render(request, 'empresarial/verPorcentajes.html', {'porcentajes_legales': porcentajes_legales})
    
    def crear_porcentajes_legales(request):
        if request.method == 'POST':
            form = PorcentajesLegalesForm(request.POST)
            if form.is_valid():
                form.save()  # Guardar el registro
                return redirect('ListarEmpresa')  # Redirige a la lista de porcentajes legales (ajusta la URL si es necesario)
        else:
            form = PorcentajesLegalesForm()

        return render(request, 'empresarial/porcentajes.html', {'form': form})
    
    def actualizar_porcentajes_legales(request, pk):
        porcentaje_legales = get_object_or_404(PorcentajesLegales, pk=pk)
        if request.method == 'POST':
            form = PorcentajesLegalesForm(request.POST, instance=porcentaje_legales)
            if form.is_valid():
                form.save()  # Guardar el registro actualizado
                return redirect('ListarEmpresa')  # Redirige a la lista de porcentajes legales (ajusta la URL si es necesario)
        else:
            form = PorcentajesLegalesForm(instance=porcentaje_legales)

        return render(request, 'empresarial/porcentajes.html', {'form': form})
    
class Cargos(HttpRequest):

    def listar_nivel_grado(request):
        nivelgrados = NivelGrado.objects.all()
        return render(request, 'empresarial/nivelGrado.html', {'nivelgrados': nivelgrados})

    def crear_nivel_grado(request):
        if request.method == 'POST':
            form = NivelGradoForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('nivelgrado_list')
        else:
            form = NivelGradoForm()
        return render(request, 'empresarial/resgistrarNivelGrado.html', {'form': form})

    def actualizar_nivel_grado(request, id):
        nivelgrado = get_object_or_404(NivelGrado, pk=id)
        if request.method == 'POST':
            form = NivelGradoForm(request.POST, instance=nivelgrado)
            if form.is_valid():
                form.save()
                return redirect('nivelgrado_list')
        else:
            form = NivelGradoForm(instance=nivelgrado)
        return render(request, 'empresarial/editarNivelGrado.html', {'form': form})

    def eliminar_nivel_grado(request, id):
        nivelgrado = get_object_or_404(NivelGrado, pk=id)
        nivelgrados = NivelGrado.objects.all()
        nivelgrado.delete()
        return render(request, 'empresarial/nivelGrado.html', {'nivelgrados': nivelgrados})
    
    
    
    
    def cargo_list(request):
        cargos = Cargo.objects.all()
        return render(request, 'cargo/cargo_list.html', {'cargos': cargos})

# Crear
    def cargo_create(request):
        if request.method == 'POST':
            form = CargoForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('cargo_list')
        else:
            form = CargoForm()
        return render(request, 'cargo/cargo_form.html', {'form': form})

    # Modificar
    def cargo_update(request, pk):
        cargo = get_object_or_404(Cargo, pk=pk)
        if request.method == 'POST':
            form = CargoForm(request.POST, instance=cargo)
            if form.is_valid():
                form.save()
                return redirect('cargo_list')
        else:
            form = CargoForm(instance=cargo)
        return render(request, 'cargo/cargo_form.html', {'form': form})

    # Eliminar
    def cargo_delete(request, pk):
        cargo = get_object_or_404(Cargo, pk=pk)
        if request.method == 'POST':
            cargo.delete()
            return redirect('cargo_list')
        return render(request, 'cargo/cargo_confirm_delete.html', {'cargo': cargo})
