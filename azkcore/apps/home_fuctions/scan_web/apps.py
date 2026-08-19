from django.apps import AppConfig

class ScanWebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.home_fuctions.scan_web' # ← debe ser la ruta completa desde la raíz del proyecto
    label = 'home_scan_web'