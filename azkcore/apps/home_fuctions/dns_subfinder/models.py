import uuid
from django.conf import settings
from django.db import models


class DnsScanJob(models.Model):
    class Estado(models.TextChoices):
        PENDING = "pending", "Pendiente"
        RUNNING = "running", "En progreso"
        DONE = "done", "Completado"
        ERROR = "error", "Error"
        CANCELLED = "cancelled", "Cancelado"

    class Fuentes(models.TextChoices):
        ALL = "all", "Todas las fuentes"
        PASSIVE = "passive", "Solo pasivas"
        ACTIVE = "active", "Activas (bruteforce DNS)"

    class Resolve(models.TextChoices):
        RESOLVE = "resolve", "Resolver IPs (mostrar solo activos)"
        NO_RESOLVE = "no_resolve", "No resolver (más rápido)"

    class Wordlist(models.TextChoices):
        NONE = "", "Ninguna (solo fuentes pasivas)"
        COMMON = "common", "subdomains-top1million-5000.txt"
        MEDIUM = "medium", "subdomains-top1million-20000.txt"
        BIG = "big", "subdomains-top1million-110000.txt"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target = models.CharField(max_length=255)
    fuentes = models.CharField(max_length=20, choices=Fuentes.choices, default=Fuentes.ALL)
    resolve = models.CharField(max_length=20, choices=Resolve.choices, default=Resolve.RESOLVE)
    wordlist = models.CharField(max_length=20, choices=Wordlist.choices, blank=True, default="")

    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDING)
    resultado = models.TextField(blank=True, default="")
    total_subdominios = models.PositiveIntegerField(default=0)
    error_msg = models.TextField(blank=True, default="")
    pid = models.IntegerField(null=True, blank=True)

    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.target} ({self.estado})"