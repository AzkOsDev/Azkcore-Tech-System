from django.apps import AppConfig

class SettingsProfileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.home_fuctions.settings_profile' # ← debe ser la ruta completa desde la raíz del proyecto
    label = 'home_settings_profile'
