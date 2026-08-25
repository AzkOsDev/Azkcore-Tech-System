from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404
from .models import ScanJob
from .scanner import InvalidTargetError, lanzar_escaneo_async, validar_target
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .scanner import cancelar_escaneo

@login_required
@require_POST
def cancelar_scan_view(request, pk):
    job = get_object_or_404(ScanJob, id=pk)

    if job.estado not in [ScanJob.Estado.RUNNING, ScanJob.Estado.PENDING]:
        return JsonResponse({"ok": False, "error": "Este escaneo ya no está en progreso."}, status=400)

    cancelar_escaneo(job)
    return JsonResponse({"ok": True})

@login_required
def scan_network_view(request):
    if request.method == "POST":
        target_raw = request.POST.get("target", "")
        tipo = request.POST.get("tipo", ScanJob.Tipo.NMAP_FAST)

        if tipo not in ScanJob.Tipo.values:
            tipo = ScanJob.Tipo.NMAP_FAST

        try:
            target = validar_target(target_raw)
        except InvalidTargetError as e:
            messages.error(request, str(e))
            return redirect("scan_network")

        job = ScanJob.objects.create(
            target=target,
            tipo=tipo,
            estado=ScanJob.Estado.PENDING,
            creado_por=request.user if request.user.is_authenticated else None,
        )

        lanzar_escaneo_async(job.id)

        messages.success(request, f"Escaneo de {target} iniciado.")
        return redirect("scan_network")

    # ---- GET: listado + filtro + stats ----
    estado_filtro = request.GET.get("estado", "todos")

    scans_qs = ScanJob.objects.all()
    if estado_filtro and estado_filtro != "todos":
        if estado_filtro == "running":
            scans_qs = scans_qs.filter(estado__in=[ScanJob.Estado.RUNNING, ScanJob.Estado.PENDING])
        else:
            scans_qs = scans_qs.filter(estado=estado_filtro)

    paginator = Paginator(scans_qs, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    all_jobs = ScanJob.objects.all()
    context = {
        "scans": page_obj.object_list,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "estado_filtro": estado_filtro,
        "total_count": all_jobs.count(),
        "running_count": all_jobs.filter(estado__in=[ScanJob.Estado.RUNNING, ScanJob.Estado.PENDING]).count(),
        "done_count": all_jobs.filter(estado=ScanJob.Estado.DONE).count(),
        "error_count": all_jobs.filter(estado=ScanJob.Estado.ERROR).count(),
    }
    return render(request, "home/scan_network.html", context)