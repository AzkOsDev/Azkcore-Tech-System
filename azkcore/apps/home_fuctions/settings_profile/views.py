import itertools
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.home_fuctions.dns_subfinder.models import DnsScanJob      # ajusta el import a tu app real
from apps.home_fuctions.scan_network.models import ScanJob     # ajusta el import a tu app real
from apps.home_fuctions.scan_web.models import ScanWeb         # ajusta el import a tu app real
from apps.logs.models import LogEntry       # ajusta el import a tu app real


@login_required
def profile_view(request):
    user = request.user

    dns_qs = DnsScanJob.objects.filter(creado_por=user)
    net_qs = ScanJob.objects.filter(creado_por=user)
    web_qs = ScanWeb.objects.filter(creado_por=user)

    total_escaneos = dns_qs.count() + net_qs.count() + web_qs.count()

    hallazgos_criticos = LogEntry.objects.filter(
        usuario=user, nivel=LogEntry.Nivel.CRITICAL
    ).count()

    # Unificamos los 3 tipos de escaneo en una sola lista para "actividad reciente"
    def normalizar(qs, tipo):
        return [
            {"target": s.target, "estado": s.estado, "creado": s.creado, "tipo": tipo}
            for s in qs
        ]

    scans_recientes = sorted(
        itertools.chain(
            normalizar(dns_qs, "DNS"),
            normalizar(net_qs, "Red"),
            normalizar(web_qs, "Web"),
        ),
        key=lambda s: s["creado"],
        reverse=True,
    )[:5]

    context = {
        "total_escaneos": total_escaneos,
        "hallazgos_criticos": hallazgos_criticos,
        "ultimo_acceso": user.last_login,
        "scans_recientes": scans_recientes,
    }
    return render(request, "home/profile.html", context)