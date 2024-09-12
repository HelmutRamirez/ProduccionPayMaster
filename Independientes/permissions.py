from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models

class Permisos(models.Model):
    class Meta:
        permissions = [
            ('ver_pagina_registro', 'Puede ver la página de registro de independientes'),
            ('editar_empleado', 'Puede editar empleados'),
        ]

    @staticmethod
    def add_permissions():
        content_type = ContentType.objects.get_for_model(Permisos)
        Permission.objects.get_or_create(codename='ver_pagina_registro', name='Puede ver la página de registro de independientes', content_type=content_type)
        Permission.objects.get_or_create(codename='editar_empleado', name='Puede editar empleados', content_type=content_type)
