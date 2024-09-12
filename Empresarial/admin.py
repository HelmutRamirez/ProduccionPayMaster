from django.contrib import admin # type: ignore

# Register your models here.
from .models import Cargo, Ciudad, Contrato, Departamento, Empleado, Empresa, HorasExtrasRecargos, Liquidacion, NivelEstudio, NivelGrado, Usuarios,PasswordResetRequest, vacacionesCesantias

admin.site.register(Empleado)
admin.site.register(Empresa)
admin.site.register(Usuarios)

admin.site.register(Departamento)
admin.site.register(Ciudad)
admin.site.register(NivelEstudio)
admin.site.register(NivelGrado)
admin.site.register(Cargo)
admin.site.register(Contrato)
admin.site.register(Liquidacion)
admin.site.register(vacacionesCesantias)
admin.site.register(PasswordResetRequest)
admin.site.register(HorasExtrasRecargos)
