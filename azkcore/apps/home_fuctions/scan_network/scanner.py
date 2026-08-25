import re
import shutil
import subprocess
import threading

from apps.logs.utils import registrar_log

TARGET_RE = re.compile(
    r"^(?=.{1,253}$)"
    r"(([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*)$"
)

NMAP_ARGS = {
    "nmap_fast": ["-F", "-T4"],
    "nmap_full": ["-p-", "-T4"],
}


class InvalidTargetError(Exception):
    pass


def validar_target(target: str) -> str:
    target = target.strip()
    if not TARGET_RE.match(target):
        raise InvalidTargetError("Target inválido. Usa un hostname o IP válido, sin espacios ni caracteres especiales.")
    return target


def lanzar_escaneo_async(scan_job_id):
    from .models import ScanJob

    def _run():
        job = ScanJob.objects.get(id=scan_job_id)
        job.estado = ScanJob.Estado.RUNNING
        job.save(update_fields=["estado", "actualizado"])

        registrar_log(
            f"Escaneo iniciado: {job.target} ({job.get_tipo_display()})",
            nivel="info",
            origen="scan_network",
            usuario=job.creado_por,
        )

        if shutil.which("nmap") is None:
            job.estado = ScanJob.Estado.ERROR
            job.error_msg = "nmap no está instalado en el servidor."
            job.save(update_fields=["estado", "error_msg", "actualizado"])
            return

        args = NMAP_ARGS.get(job.tipo, NMAP_ARGS["nmap_fast"])
        cmd = ["nmap", *args, job.target]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Guarda el PID para poder cancelarlo después
        job.pid = proc.pid
        job.save(update_fields=["pid"])

        try:
            stdout, stderr = proc.communicate(timeout=600)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()

        # Refresca el job por si fue cancelado mientras corría
        job.refresh_from_db()
        if job.estado == ScanJob.Estado.CANCELLED:
            registrar_log(
                f"Escaneo cancelado: {job.target}",
                nivel="warning",
                origen="scan_network",
                usuario=job.creado_por,
            )
            return

        if proc.returncode != 0:
            job.estado = ScanJob.Estado.ERROR
            job.error_msg = stderr.strip() or f"nmap terminó con código {proc.returncode}"
            job.save(update_fields=["estado", "error_msg", "actualizado"])
            registrar_log(
                f"Error en escaneo: {job.target}",
                nivel="error",
                origen="scan_network",
                detalle=job.error_msg,
                usuario=job.creado_por,
            )
            return

        job.resultado = stdout
        job.estado = ScanJob.Estado.DONE
        job.save(update_fields=["resultado", "estado", "actualizado"])

        registrar_log(
            f"Escaneo completado: {job.target}",
            nivel="info",
            origen="scan_network",
            usuario=job.creado_por,
        )

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()


def cancelar_escaneo(job):
    """Intenta matar el proceso de nmap asociado a este job."""
    import os
    import signal

    if job.pid:
        try:
            os.kill(job.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass  # el proceso ya terminó por su cuenta

    job.estado = job.Estado.CANCELLED
    job.save(update_fields=["estado", "actualizado"])