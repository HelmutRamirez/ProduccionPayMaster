from django.contrib import admin
from .models import Independiente,Usuarios,PasswordResetRequest, DatosCalculos, Calculos
# Register your models here.


admin.site.register(Independiente)
admin.site.register(Usuarios)
admin.site.register(PasswordResetRequest)
admin.site.register(DatosCalculos)
admin.site.register(Calculos)
