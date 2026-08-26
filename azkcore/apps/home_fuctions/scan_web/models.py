from django.conf import settings
from django.db import models


class ScanWeb(models.Model):

    class Herramienta(models.TextChoices):
        NUCLEI = "nuclei", "Nuclei"
        WPSCAN = "wpscan", "WPScan"
        NIKTO = "nikto", "Nikto"

    class Estado(models.TextChoices):
        PENDING = "pending", "Pendiente"
        RUNNING = "running", "En progreso"
        DONE = "done", "Completado"
        ERROR = "error", "Error"
        CANCELLED = "cancelled", "Cancelado"

    target = models.CharField(max_length=255)
    herramienta = models.CharField(max_length=20, choices=Herramienta.choices)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDING)

    # Opciones específicas de cada herramienta, guardadas tal cual llegan del form.
    # Ej: {"severity": "critical,high", "tags": "cve,exposure"}
    opciones = models.JSONField(blank=True, default=dict)

    resultado = models.TextField(blank=True, null=True)
    error_msg = models.TextField(blank=True, null=True)
    pid = models.IntegerField(blank=True, null=True)

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scan_web_jobs",
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "Escaneo web"
        verbose_name_plural = "Escaneos web"

    def __str__(self):
        return f"{self.herramienta} -> {self.target} ({self.estado})"