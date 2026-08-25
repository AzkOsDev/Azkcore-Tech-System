from django.contrib import admin
from django.utils.html import format_html
from .models import LogEntry


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("nivel_badge", "mensaje", "origen", "usuario", "ip", "creado")
    list_filter = ("nivel", "origen", "creado")
    search_fields = ("mensaje", "detalle", "ip", "usuario__username")
    date_hierarchy = "creado"
    readonly_fields = ("nivel", "mensaje", "detalle", "origen", "ip", "usuario", "creado")
    ordering = ("-creado",)

    def has_add_permission(self, request):
        return False

    def nivel_badge(self, obj):
        colores = {"info": "#3D8EFF", "warning": "#F59E0B", "error": "#EF4444", "critical": "#EF4444"}
        color = colores.get(obj.nivel, "#8B96A8")
        return format_html(
            '<span style="background:{}20; color:{}; border:1px solid {}40; '
            'padding:2px 10px; border-radius:999px; font-size:11px; font-weight:600;">{}</span>',
            color, color, color, obj.get_nivel_display()
        )
    nivel_badge.short_description = "Nivel"
    nivel_badge.admin_order_field = "nivel"