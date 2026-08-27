# apps/filescanner/views.py  (ajusta la ruta a tu app real)
import mimetypes
import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import FileScanJob

# Límite de tamaño de subida (ajusta a tu gusto)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Extensiones consideradas de mayor riesgo (heurística simple, no un AV real)
EXTENSIONES_RIESGO = {
    ".exe", ".bat", ".cmd", ".com", ".scr", ".pif",
    ".vbs", ".js", ".jse", ".wsf", ".ps1", ".jar",
    ".msi", ".dll", ".hta",
}


def analizar_archivo(scan_job: FileScanJob) -> None:
    """
    Análisis básico del archivo. Aquí es donde conectarías un motor
    real (ClamAV vía clamd, VirusTotal API, YARA, etc.) más adelante.
    """
    scan_job.calcular_hashes()

    nombre = scan_job.nombre_original
    _, ext = os.path.splitext(nombre)
    ext = ext.lower()
    scan_job.extension = ext

    mime_type, _ = mimetypes.guess_type(nombre)

    detalles = {
        "mime_type": mime_type or "desconocido",
        "extension_riesgo": ext in EXTENSIONES_RIESGO,
    }

    # --- Heurística simple de veredicto ---
    if ext in EXTENSIONES_RIESGO:
        scan_job.veredicto = FileScanJob.Veredicto.SOSPECHOSO
        resultado = (
            f"La extensión '{ext}' es de un tipo comúnmente asociado a malware "
            f"(ejecutables/scripts). Se recomienda verificar el origen del archivo."
        )
    else:
        scan_job.veredicto = FileScanJob.Veredicto.LIMPIO
        resultado = "No se encontraron indicadores de riesgo en el análisis básico."

    scan_job.detalles = detalles
    scan_job.resultado = resultado
    scan_job.estado = FileScanJob.Estado.DONE


@login_required
def file_scanner_view(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')

        if not archivo:
            messages.error(request, 'Debes seleccionar un archivo para escanear.')
            return redirect('file_scanner')

        if archivo.size > MAX_FILE_SIZE:
            messages.error(request, f'El archivo supera el límite de {MAX_FILE_SIZE // (1024*1024)} MB.')
            return redirect('file_scanner')

        scan_job = FileScanJob.objects.create(
            archivo=archivo,
            nombre_original=archivo.name,
            tamano_bytes=archivo.size,
            estado=FileScanJob.Estado.RUNNING,
            creado_por=request.user,
        )

        try:
            analizar_archivo(scan_job)
        except Exception as e:
            scan_job.estado = FileScanJob.Estado.ERROR
            scan_job.error_msg = str(e)
            messages.error(request, 'Ocurrió un error al analizar el archivo.')
        else:
            messages.success(request, 'Archivo analizado correctamente.')

        scan_job.save()
        return redirect('file_scanner')

    escaneos = FileScanJob.objects.filter(creado_por=request.user)

    context = {
        'escaneos': escaneos,
        'max_file_size_mb': MAX_FILE_SIZE // (1024 * 1024),
    }
    return render(request, 'home/file_scanner.html', context)


@login_required
def file_scan_delete(request, scan_id):
    scan_job = get_object_or_404(FileScanJob, id=scan_id, creado_por=request.user)
    if request.method == 'POST':
        scan_job.archivo.delete(save=False)
        scan_job.delete()
        messages.success(request, 'Escaneo eliminado.')
    return redirect('file_scanner')