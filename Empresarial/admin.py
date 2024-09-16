from django.contrib import admin # type: ignore

# Register your models here.
from .models import Cargo,  Contrato,  Empleado, Empresa, HorasExtrasRecargos, Liquidacion, NivelEstudio, NivelGrado, PorcentajesLegales, Usuarios,PasswordResetRequest, vacacionesCesantias

admin.site.register(Empleado)
admin.site.register(Empresa)
admin.site.register(Usuarios)
admin.site.register(NivelEstudio)
admin.site.register(NivelGrado)
admin.site.register(Cargo)
admin.site.register(Contrato)
admin.site.register(Liquidacion)
admin.site.register(vacacionesCesantias)
admin.site.register(PasswordResetRequest)
admin.site.register(HorasExtrasRecargos)
admin.site.register(PorcentajesLegales)