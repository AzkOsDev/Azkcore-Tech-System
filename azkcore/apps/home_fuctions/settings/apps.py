from django.apps import AppConfig

class SettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.home_fuctions.settings' # ← debe ser la ruta completa desde la raíz del proyecto
    label = 'home_settings'