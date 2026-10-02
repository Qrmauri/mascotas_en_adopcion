from django.contrib import admin

from .models import Mascota


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "especie", "edad_meses", "estado", "autor", "creado")
    list_filter = ("especie", "estado")
    search_fields = ("nombre", "descripcion")
