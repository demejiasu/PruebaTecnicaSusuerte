from django.contrib import admin

from tickets.models import Tiquete, Usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "saldo", "creado_en")
    search_fields = ("nombre",)


@admin.register(Tiquete)
class TiqueteAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "monto", "estado", "creado_en")
    list_filter = ("estado",)
    search_fields = ("usuario__nombre",)