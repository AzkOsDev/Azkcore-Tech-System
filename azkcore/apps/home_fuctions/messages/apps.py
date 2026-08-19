from django.apps import AppConfig

class MessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.home_fuctions.messages' # ← debe ser la ruta completa desde la raíz del proyecto
    label = 'home_messages'