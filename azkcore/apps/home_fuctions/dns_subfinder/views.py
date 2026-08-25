from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST

from .models import DnsScanJob
from .subfinder import InvalidTargetError, lanzar_escaneo_async, validar_target, cancelar_escaneo


@login_required
def dns_subfinder_view(request):
    if request.method == "POST":
        target_raw = request.POST.get("target", "")
        fuentes = request.POST.get("fuentes", DnsScanJob.Fuentes.ALL)
        resolve = request.POST.get("resolve", DnsScanJob.Resolve.RESOLVE)
        wordlist = request.POST.get("wordlist", "")

        if fuentes not in DnsScanJob.Fuentes.values:
            fuentes = DnsScanJob.Fuentes.ALL
        if resolve not in DnsScanJob.Resolve.values:
            resolve = DnsScanJob.Resolve.RESOLVE
        if wordlist not in DnsScanJob.Wordlist.values:
            wordlist = ""

        try:
            target = validar_target(target_raw)
        except InvalidTargetError as e:
            messages.error(request, str(e))
            return redirect("dns_subfinder")

        job = DnsScanJob.objects.create(
            target=target,
            fuentes=fuentes,
            resolve=resolve,
            wordlist=wordlist,
            estado=DnsScanJob.Estado.PENDING,
            creado_por=request.user if request.user.is_authenticated else None,
        )

        lanzar_escaneo_async(job.id)

        messages.success(request, f"Escaneo de subdominios para {target} iniciado.")
        return redirect("dns_subfinder")

    # ---- GET: listado + filtro + stats ----
    estado_filtro = request.GET.get("estado", "todos")

    scans_qs = DnsScanJob.objects.all()
    if estado_filtro and estado_filtro != "todos":
        if estado_filtro == "running":
            scans_qs = scans_qs.filter(estado__in=[DnsScanJob.Estado.RUNNING, DnsScanJob.Estado.PENDING])
        else:
            scans_qs = scans_qs.filter(estado=estado_filtro)

    paginator = Paginator(scans_qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    all_jobs = DnsScanJob.objects.all()
    context = {
        "scans": page_obj.object_list,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "estado_filtro": estado_filtro,
        "total_count": all_jobs.count(),
        "running_count": all_jobs.filter(estado__in=[DnsScanJob.Estado.RUNNING, DnsScanJob.Estado.PENDING]).count(),
        "done_count": all_jobs.filter(estado=DnsScanJob.Estado.DONE).count(),
        "error_count": all_jobs.filter(estado=DnsScanJob.Estado.ERROR).count(),
    }
    return render(request, "home/dns_subfinder.html", context)


@login_required
@require_POST
def cancelar_dns_scan_view(request, pk):
    job = get_object_or_404(DnsScanJob, id=pk)

    if job.estado not in [DnsScanJob.Estado.RUNNING, DnsScanJob.Estado.PENDING]:
        return JsonResponse({"ok": False, "error": "Este escaneo ya no está en progreso."}, status=400)

    cancelar_escaneo(job)
    return JsonResponse({"ok": True})