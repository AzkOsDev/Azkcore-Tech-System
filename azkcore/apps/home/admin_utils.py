from django.conf import settings


def environment_callback(request):
    if settings.DEBUG:
        return ["Desarrollo", "warning"]
    return ["Producción", "danger"]


def dashboard_callback(request, context):
    from apps.home_fuctions.dns_subfinder.models import DnsScanJob
    from apps.home_fuctions.scan_network.models import ScanJob
    from apps.logs.models import LogEntry

    context.update({
        "kpi": [
            {"title": "Escaneos DNS", "metric": DnsScanJob.objects.count(), "footer": "Total histórico"},
            {"title": "Network Scans", "metric": ScanJob.objects.count(), "footer": "Total histórico"},
            {"title": "Logs registrados", "metric": LogEntry.objects.count(), "footer": "Total histórico"},
        ],
    })
    return context