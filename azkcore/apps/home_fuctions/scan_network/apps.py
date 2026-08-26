from django.apps import AppConfig


class ScanNetworkConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.home_fuctions.scan_network"  # ← debe ser la ruta completa desde la raíz del proyecto
    label = "scan_network"
    verbose_name = " Table | Network Scan"  # opcional, pero útil si hay conflicto de nombres con otra app