from django.urls import path # type: ignore
from . import views
urlpatterns = [
    #gestion login
    path('accounts/login/', views.GestionLogin.login_view, name='loginEmpresa'), #redirecion al login
    path('recuperar-contrasena_empre/', views.GestionLogin.recuperar_contrasena, name='recuperar_contrasena_empre'), #redirecion para pedir un token
    path('password-reset_empre/', views.GestionLogin.password_reset, name='password_reset_empre'), #redirecion para cambiar la contraseña
    path('cerrar_sesion_empre/', views.GestionLogin.cerrar_sesion, name='cerrar_sesion_empre'),
    path('cerrar_sesion_redirect_de/', views.GestionLogin.cerrar_sesion_redirect, name='cerrar_sesion_redirect_e'),
    path('keep-session-alive/', views.GestionLogin.keep_session_alive, name='keep_session_alive'),
    
    #Gestion de Empresa
    path('empresa', views.Paginas.homeEmpresa, name='homeEmpresa'), #redirecion al home de empresas
    path('registroEmpresa', views.GestionarEmpresa.crearEmpresa, name='registroEmpresa'), #redirecion al registro de empresas
    path('listarEmpresa', views.GestionarEmpresa.ListarEmpresa, name='ListarEmpresa'),#redirecion para ver las empresas
    path('editarEmpresa/<int:nit>/', views.GestionarEmpresa.editarEmpresa, name='editarEmpresa'), #redirecion para editar las empresas
    path('actualizarempre/<int:nit>/', views.GestionarEmpresa.actualizarEmpresa, name='actualizarEmpresa'),#redirecion Actualiza la informacion de las empresas
    path('eliminarEmpre/<int:nit>/', views.GestionarEmpresa.eliminarEmpresa, name='eliminarempre'),

    #Gestion de empleado
    path('empleados/<int:nit>', views.GestionEmpleado.EmpleadosContratar, name='empleadoss'),
    path('empleado/<int:numero_identificacion_e>', views.Paginas.homeEmpleado, name='homeEmpleado'),
    path('registroEmpleado/<int:nit>', views.GestionEmpleado.crearEmpleado, name='registroEmpleado'),
    path('listarEmpleados/<int:nit>', views.GestionEmpleado.ListarEmpleados, name='ListarEmpleados'), #redirecion para ver los empleados
    path('editarEmpleado/<int:numero_identificacion_e>/', views.GestionEmpleado.editarEmpleado, name='editarEmpleado'),
    path('actualizar/<int:numero_identificacion_e>/', views.GestionEmpleado.actualizarEmpleado, name='actualizarEmpleado'),
    path('eliminar/<int:numero_identificacion_e>/', views.GestionEmpleado.eliminarEmpleado, name='eliminaremple'),
    path('finalizaContra/<int:numero_identificacion_e>/', views.GestionEmpleado.cancelarContrato, name='terminarContrat'),
    
    #gestion de contratos
    path('registroContrat/<int:numero_identificacion_e>/', views.GestionEmpleado.registroContrato, name='registContrat'),
    path('contratacion/<int:numero_identificacion_e>/<int:nit>', views.GestionEmpleado.Contratacion, name='contratacion'),
    
    
    
    #Gestion de Calculos
    path('calcular/<int:numero_identificacion_e>/', views.CalculosGenerales.calcularSalario, name='calcularemple'),
    # path('registro_novedades/<int:numero_identificacion>/', views.CalculosGenerales.registroNovedades, name='registroNovedades'),
    path('calculos/<str:documento>/<str:fecha>/', views.CalculosGenerales.HistorialNomina, name='verNomina'),
    path('todos_los_calculos<int:numero_identificacion_e>/', views.CalculosGenerales.obtener_todos_los_calculos, name='todos_los_calculos'),
]