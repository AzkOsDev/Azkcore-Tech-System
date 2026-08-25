from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .utils import registrar_log


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    registrar_log(
        f"Inicio de sesión: {user.username}",
        nivel="info",
        origen="auth",
        usuario=user,
        request=request,
    )


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    registrar_log(
        f"Cierre de sesión: {user.username if user else 'desconocido'}",
        nivel="info",
        origen="auth",
        usuario=user,
        request=request,
    )


@receiver(user_login_failed)
def log_login_failed(sender, credentials, request=None, **kwargs):
    username = credentials.get("username", "desconocido")
    registrar_log(
        f"Intento de inicio de sesión fallido: {username}",
        nivel="warning",
        origen="auth",
        detalle=f"Credenciales usadas: {username}",
        request=request,
    )