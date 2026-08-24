from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.home_fuctions.scan_network.models import ScanJob


@admin.register(ScanJob)
class ScanJobAdmin(admin.ModelAdmin):
    # ---- Columnas visibles en la lista ----
    list_display = (
        "target",
        "tipo_badge",
        "estado_badge",
        "creado_por",
        "creado",
        "actualizado",
    )

    # ---- Filtros laterales ----
    list_filter = ("estado", "tipo", "creado")

    # ---- Buscador ----
    search_fields = ("target", "creado_por__username", "resultado", "error_msg")

    # ---- Orden por defecto ----
    ordering = ("-creado",)

    # ---- Paginación en el admin ----
    list_per_page = 25

    # ---- Navegación rápida por fecha (barra de calendario arriba) ----
    date_hierarchy = "creado"

    # ---- Campos de solo lectura (no queremos editar resultados a mano) ----
    readonly_fields = (
        "id",
        "creado",
        "actualizado",
        "resultado_pretty",
    )

    # ---- Organización del formulario de detalle ----
    fieldsets = (
        ("Información del escaneo", {
            "fields": ("target", "tipo", "estado", "creado_por")
        }),
        ("Resultado", {
            "fields": ("resultado_pretty", "error_msg")
        }),
        ("Metadatos", {
            "fields": ("id", "creado", "actualizado"),
            "classes": ("collapse",),
        }),
    )

    # ---- No permitir crear escaneos manualmente desde el admin ----
    def has_add_permission(self, request):
        return False

    # ---- Columna: tipo con estilo ----
    def tipo_badge(self, obj):
        etiquetas = {
            "nmap_fast": ("Rápido", "#3D8EFF"),
            "nmap_full": ("Completo", "#8B5CF6"),
        }
        texto, color = etiquetas.get(obj.tipo, (obj.get_tipo_display(), "#8B96A8"))
        return format_html(
            '<span style="color:{}; font-weight:600; font-size:11px;">{}</span>',
            color, texto
        )
    tipo_badge.short_description = "Tipo"
    tipo_badge.admin_order_field = "tipo"

    # ---- Columna: estado con badge de color ----
    def estado_badge(self, obj):
        colores = {
            "pending": "#F59E0B",
            "running": "#F59E0B",
            "done": "#22C55E",
            "error": "#EF4444",
        }
        color = colores.get(obj.estado, "#8B96A8")
        return format_html(
            '<span style="background:{}20; color:{}; border:1px solid {}40; '
            'padding:2px 10px; border-radius:999px; font-size:11px; font-weight:600;">{}</span>',
            color, color, color, obj.get_estado_display()
        )
    estado_badge.short_description = "Estado"
    estado_badge.admin_order_field = "estado"

    # ---- Resultado formateado (bonito en el detalle) ----
    def resultado_pretty(self, obj):
        if not obj.resultado:
            return "—"
        return format_html(
            '<pre style="white-space:pre-wrap; background:#111; color:#ddd; '
            'padding:12px; border-radius:8px; font-size:12px; max-height:400px; overflow:auto;">{}</pre>',
            obj.resultado
        )
    resultado_pretty.short_description = "Salida de nmap"