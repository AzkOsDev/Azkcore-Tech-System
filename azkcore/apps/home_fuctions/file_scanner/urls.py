from django.urls import path
from .views import file_scanner_view, file_scan_delete

urlpatterns = [
    # ...tus otras rutas...
    path('', file_scanner_view, name='file_scanner'),
    path('/<uuid:scan_id>/eliminar/', file_scan_delete, name='file_scan_delete'),
]