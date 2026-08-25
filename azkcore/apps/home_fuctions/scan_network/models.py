import uuid
from django.conf import settings
from django.db import models


class ScanJob(models.Model):
    class Estado(models.TextChoices):
        PENDING = "pending", "Pendiente"
        RUNNING = "running", "En progreso"
        DONE = "done", "Completado"
        ERROR = "error", "Error"

    class Tipo(models.TextChoices):
        NMAP_FAST = "nmap_fast", "Rápido (puertos comunes)"
        NMAP_FULL = "nmap_full", "Completo (todos los puertos)"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.NMAP_FAST)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDING)
    resultado = models.TextField(blank=True, default="")
    error_msg = models.TextField(blank=True, default="")
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    pid = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.target} ({self.estado})"