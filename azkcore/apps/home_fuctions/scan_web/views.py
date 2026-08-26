from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from apps.logs.utils import registrar_log

from .models import ScanWeb
from .utils import (
    InvalidOptionError,
    InvalidTargetError,
    lanzar_escaneo_async,
    preparar_opciones,
    validar_target,
)

HERRAMIENTAS_VALIDAS = {choice.value for choice in ScanWeb.Herramienta}
PAGE_SIZE = 5


@login_required
def scan_web_view(request):
    """Vista principal: lista + filtros + lanzamiento de nuevo escaneo.
    OJO: el nombre de esta función es distinto al del modelo (ScanWeb)
    a propósito, para que un `from .views import ScanWeb` nunca pueda
    traer el modelo por error en vez de la vista."""

    if request.method == "POST":
        return _crear_escaneo(request)

    estado_filtro = request.GET.get("estado", "todos")

    scans_qs = ScanWeb.objects.all()
    if estado_filtro and estado_filtro != "todos":
        scans_qs = scans_qs.filter(estado=estado_filtro)

    paginator = Paginator(scans_qs, PAGE_SIZE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    todos_los_scans = ScanWeb.objects.all()
    context = {
        "scans": page_obj.object_list,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "estado_filtro": estado_filtro,
        "total_count": todos_los_scans.count(),
        "running_count": todos_los_scans.filter(
            estado__in=[ScanWeb.Estado.RUNNING, ScanWeb.Estado.PENDING]
        ).count(),
        "done_count": todos_los_scans.filter(estado=ScanWeb.Estado.DONE).count(),
        "error_count": todos_los_scans.filter(estado=ScanWeb.Estado.ERROR).count(),
    }
    return render(request, "home/scan_web.html", context)


def _crear_escaneo(request):
    target_raw = request.POST.get("target", "")
    herramienta = request.POST.get("herramienta", "")

    if herramienta not in HERRAMIENTAS_VALIDAS:
        messages.error(request, "Herramienta inválida.")
        return redirect("scan_web")

    try:
        target = validar_target(target_raw)
    except InvalidTargetError as exc:
        messages.error(request, str(exc))
        return redirect("scan_web")

    try:
        opciones = preparar_opciones(herramienta, request.POST)
    except InvalidOptionError as exc:
        messages.error(request, str(exc))
        return redirect("scan_web")

    job = ScanWeb.objects.create(
        target=target,
        herramienta=herramienta,
        opciones=opciones,
        estado=ScanWeb.Estado.PENDING,
        creado_por=request.user,
    )

    registrar_log(
        f"Escaneo web solicitado: {target} ({herramienta})",
        nivel="info",
        origen="scan_web",
        usuario=request.user,
    )

    lanzar_escaneo_async(job.id)

    messages.success(request, f"Escaneo de {herramienta} lanzado sobre {target}.")
    return redirect("scan_web")


@login_required
def cancelar_escaneo_view(request, job_id):
    from .utils import cancelar_escaneo

    job = ScanWeb.objects.filter(id=job_id).first()
    if job is None:
        messages.error(request, "Escaneo no encontrado.")
        return redirect("scan_web")

    if job.estado in (ScanWeb.Estado.RUNNING, ScanWeb.Estado.PENDING):
        cancelar_escaneo(job)
        messages.success(request, "Escaneo cancelado.")
    else:
        messages.info(request, "Este escaneo ya no está en progreso.")

    return redirect("scan_web")