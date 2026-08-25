from django.contrib import admin
from django.utils.html import format_html

from .models import DnsScanJob


@admin.register(DnsScanJob)
class DnsScanJobAdmin(admin.ModelAdmin):
    list_display = (
        "target",
        "fuentes_badge",
        "estado_badge",
        "total_subdominios",
        "creado_por",
        "creado",
    )
    list_filter = ("estado", "fuentes", "resolve", "creado")
    search_fields = ("target", "creado_por__username", "resultado", "error_msg")
    ordering = ("-creado",)
    list_per_page = 25
    date_hierarchy = "creado"

    readonly_fields = ("id", "creado", "actualizado", "resultado_pretty", "total_subdominios", "pid")

    fieldsets = (
        ("Información del escaneo", {
            "fields": ("target", "fuentes", "resolve", "wordlist", "estado", "creado_por")
        }),
        ("Resultado", {
            "fields": ("total_subdominios", "resultado_pretty", "error_msg")
        }),
        ("Metadatos", {
            "fields": ("id", "pid", "creado", "actualizado"),
            "classes": ("collapse",),
        }),
    )

    def has_add_permission(self, request):
        return False

    def fuentes_badge(self, obj):
        colores = {"all": "#3D8EFF", "passive": "#8B5CF6", "active": "#F59E0B"}
        color = colores.get(obj.fuentes, "#8B96A8")
        return format_html('<span style="color:{}; font-weight:600; font-size:11px;">{}</span>', color, obj.get_fuentes_display())
    fuentes_badge.short_description = "Fuentes"
    fuentes_badge.admin_order_field = "fuentes"

    def estado_badge(self, obj):
        colores = {"pending": "#F59E0B", "running": "#F59E0B", "done": "#22C55E", "error": "#EF4444", "cancelled": "#8B96A8"}
        color = colores.get(obj.estado, "#8B96A8")
        return format_html(
            '<span style="background:{}20; color:{}; border:1px solid {}40; '
            'padding:2px 10px; border-radius:999px; font-size:11px; font-weight:600;">{}</span>',
            color, color, color, obj.get_estado_display()
        )
    estado_badge.short_description = "Estado"
    estado_badge.admin_order_field = "estado"

    def resultado_pretty(self, obj):
        if not obj.resultado:
            return "—"
        return format_html(
            '<pre style="white-space:pre-wrap; background:#111; color:#ddd; '
            'padding:12px; border-radius:8px; font-size:12px; max-height:400px; overflow:auto;">{}</pre>',
            obj.resultado
        )
    resultado_pretty.short_description = "Subdominios encontrados"