from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.logs.models import LogEntry
from apps.home_fuctions.scan_network.models import ScanJob
# Create your views here.
@login_required


def dashboard_view(request):
    # ... tu código existente ...

    logs_recientes = LogEntry.objects.select_related("usuario").all()[:3]
    scans_recientes = ScanJob.objects.select_related("creado_por").all()[:3]

    context = {
        # ... tus otras variables ...
        "logs_recientes": logs_recientes,
        "scans_recientes": scans_recientes,
    }
    return render(request, "home/dashboard.html", context)