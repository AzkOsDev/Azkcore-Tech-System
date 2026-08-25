from django.conf import settings
from django.db import models


class LogEntry(models.Model):
    class Nivel(models.TextChoices):
        INFO = "info", "Info"
        WARNING = "warning", "Warning"
        ERROR = "error", "Error"
        CRITICAL = "critical", "Critical"

    nivel = models.CharField(max_length=10, choices=Nivel.choices, default=Nivel.INFO)
    mensaje = models.CharField(max_length=500)
    detalle = models.TextField(blank=True, default="")
    origen = models.CharField(max_length=100, blank=True, default="")
    ip = models.GenericIPAddressField(blank=True, null=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="app_log_entries",   # ← esto arregla el choque
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]
        indexes = [
            models.Index(fields=["-creado"]),
            models.Index(fields=["nivel"]),
        ]

    def __str__(self):
        return f"[{self.nivel}] {self.mensaje}"