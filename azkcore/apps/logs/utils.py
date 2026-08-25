from .models import LogEntry


def registrar_log(mensaje, nivel="info", origen="", detalle="", usuario=None, request=None):
    ip = None
    if request is not None:
        if usuario is None and request.user.is_authenticated:
            usuario = request.user
        ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR")

    LogEntry.objects.create(
        nivel=nivel,
        mensaje=mensaje,
        detalle=detalle,
        origen=origen,
        ip=ip,
        usuario=usuario,
    )