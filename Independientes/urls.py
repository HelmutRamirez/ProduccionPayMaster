from django.urls import path # type: ignore
from . import views


urlpatterns = [
    path('login/', views.GestionLogin.login_view, name='login'),
    path('recuperar-contrasena/', views.GestionLogin.recuperar_contrasena, name='recuperar_contrasena'),

    #path('resetear-contrasena/<str:uidb64>/<str:token>/', views.GestionLogin.resetear_contrasena, name='resetear_contrasena'),
    path('password-reset/', views.GestionLogin.password_reset, name='password_reset'),
    path('activate-acount/<int:numero_identificacion>/', views.GestionLogin.activateAcount, name='activate_acount'),
    path('cerrar_sesion/', views.GestionLogin.cerrar_sesion, name='cerrar_sesion'),
    path('cerrar_sesion_redirect/', views.GestionLogin.cerrar_sesion_redirect, name='cerrar_sesion_redirect'),
    path('home/', views.homeIndependientes, name='homeIndependiente'),
    path('registroIndepe/', views.GestionIndependiente.RegistroIndependi, name='registrarIndependiente'),
    path('editaIndepe/<int:numero_identificacion>/', views.GestionIndependiente.editarIndependiente, name='editarIndependiente'),
    path('actualizaIndepe/<int:numero_identificacion>/', views.GestionIndependiente.actualizarIndependiente, name='actualizarIndependiente'),
    path('eliminarIndepen/<int:numero_identificacion>/', views.GestionIndependiente.eliminarIndependi, name='eliminarindepen'),
    
    # path('calcularinde/', views.CalculosGenerales.calcular_aportes, name='calcularinde'),
    path('calcularinde/<str:numero_identificacion>/', views.CalculosGenerales.calcular_aportes, name='calcularinde'),
    path('calculoss/<str:documento>/', views.CalculosGenerales.HistorialNomina, name='verNominaInde'),
    path('todos_los_calculoss<int:numero_identificacion>/', views.CalculosGenerales.obtener_todos_los_calculos, name='historial'),

]