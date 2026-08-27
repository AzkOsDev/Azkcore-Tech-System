# apps/passwordanalyzer/models.py
import uuid
from django.conf import settings
from django.db import models


class PasswordAnalysisLog(models.Model):
    class Fortaleza(models.TextChoices):
        MUY_DEBIL = "muy_debil", "Muy débil"
        DEBIL = "debil", "Débil"
        MEDIA = "media", "Media"
        FUERTE = "fuerte", "Fuerte"
        MUY_FUERTE = "muy_fuerte", "Muy fuerte"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # NUNCA se guarda la contraseña real, solo métricas
    longitud = models.PositiveIntegerField()
    tiene_mayusculas = models.BooleanField(default=False)
    tiene_minusculas = models.BooleanField(default=False)
    tiene_numeros = models.BooleanField(default=False)
    tiene_simbolos = models.BooleanField(default=False)
    entropia_bits = models.FloatField(default=0)
    fortaleza = models.CharField(max_length=20, choices=Fortaleza.choices)
    fue_filtrada = models.BooleanField(null=True, blank=True)  # HIBP result

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="password_analysis_logs",
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "Análisis de contraseña"
        verbose_name_plural = "Análisis de contraseñas"

    def __str__(self):
        return f"{self.get_fortaleza_display()} ({self.longitud} caracteres)"