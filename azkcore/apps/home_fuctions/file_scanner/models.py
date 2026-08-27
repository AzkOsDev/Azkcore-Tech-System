# apps/filescanner/models.py  (ajusta la ruta a tu app real)
import hashlib
import os
import uuid

from django.conf import settings
from django.db import models


class FileScanJob(models.Model):

    class Estado(models.TextChoices):
        PENDING = "pending", "Pendiente"
        RUNNING = "running", "En progreso"
        DONE = "done", "Completado"
        ERROR = "error", "Error"

    class Veredicto(models.TextChoices):
        LIMPIO = "limpio", "Limpio"
        SOSPECHOSO = "sospechoso", "Sospechoso"
        MALICIOSO = "malicioso", "Malicioso"
        SIN_ANALIZAR = "", "Sin analizar"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    archivo = models.FileField(upload_to="file_scans/%Y/%m/%d/")
    nombre_original = models.CharField(max_length=255)
    extension = models.CharField(max_length=20, blank=True, default="")
    tamano_bytes = models.BigIntegerField(default=0)

    hash_md5 = models.CharField(max_length=32, blank=True, default="")
    hash_sha1 = models.CharField(max_length=40, blank=True, default="")
    hash_sha256 = models.CharField(max_length=64, blank=True, default="")

    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDING)
    veredicto = models.CharField(max_length=20, choices=Veredicto.choices, blank=True, default="")
    detalles = models.JSONField(blank=True, default=dict)
    resultado = models.TextField(blank=True, default="")
    error_msg = models.TextField(blank=True, default="")

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="file_scan_jobs",
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "Escaneo de archivo"
        verbose_name_plural = "Escaneos de archivos"

    def __str__(self):
        return f"{self.nombre_original} ({self.estado})"

    def calcular_hashes(self):
        """Calcula MD5, SHA1 y SHA256 del archivo subido."""
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256()

        self.archivo.seek(0)
        for chunk in self.archivo.chunks():
            md5.update(chunk)
            sha1.update(chunk)
            sha256.update(chunk)
        self.archivo.seek(0)

        self.hash_md5 = md5.hexdigest()
        self.hash_sha1 = sha1.hexdigest()
        self.hash_sha256 = sha256.hexdigest()