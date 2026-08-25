import os
import re
import shutil
import signal
import subprocess
import threading

from apps.logs.utils import registrar_log

DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)"
    r"(([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+)$"
)


class InvalidTargetError(Exception):
    pass


def validar_target(target: str) -> str:
    target = target.strip().lower()
    if not DOMAIN_RE.match(target):
        raise InvalidTargetError("Dominio inválido. Usa un formato como ejemplo.com, sin espacios ni caracteres especiales.")
    return target


def lanzar_escaneo_async(scan_job_id):
    """Corre subfinder en un hilo aparte, guarda el PID y actualiza el DnsScanJob al terminar."""
    from .models import DnsScanJob

    def _run():
        job = DnsScanJob.objects.get(id=scan_job_id)
        job.estado = DnsScanJob.Estado.RUNNING
        job.save(update_fields=["estado", "actualizado"])

        registrar_log(
            f"Escaneo DNS iniciado: {job.target} ({job.get_fuentes_display()})",
            nivel="info",
            origen="dns_subfinder",
            usuario=job.creado_por,
        )

        if shutil.which("subfinder") is None:
            job.estado = DnsScanJob.Estado.ERROR
            job.error_msg = "subfinder no está instalado en el servidor."
            job.save(update_fields=["estado", "error_msg", "actualizado"])
            registrar_log(
                f"Error en escaneo DNS: {job.target}",
                nivel="error",
                origen="dns_subfinder",
                detalle=job.error_msg,
                usuario=job.creado_por,
            )
            return

        cmd = ["subfinder", "-d", job.target, "-silent", "-max-time", "4"]

        if job.fuentes == "active":
            cmd += ["-all"]
        if job.resolve == "resolve":
            cmd += ["-active"]

        print(f"[DEBUG] Comando: {' '.join(cmd)}", flush=True)

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except Exception as e:
            job.estado = DnsScanJob.Estado.ERROR
            job.error_msg = f"No se pudo iniciar subfinder: {e}"
            job.save(update_fields=["estado", "error_msg", "actualizado"])
            registrar_log(
                f"Error en escaneo DNS: {job.target}",
                nivel="error",
                origen="dns_subfinder",
                detalle=job.error_msg,
                usuario=job.creado_por,
            )
            return

        # Guarda el PID para poder cancelarlo después
        job.pid = proc.pid
        job.save(update_fields=["pid"])

        try:
            stdout, stderr = proc.communicate(timeout=300)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()

        print(f"[DEBUG] returncode: {proc.returncode}", flush=True)
        print(f"[DEBUG] stdout (primeras 500 chars): {stdout[:500]!r}", flush=True)
        print(f"[DEBUG] stderr: {stderr!r}", flush=True)

        # Refresca el job por si fue cancelado mientras corría
        job.refresh_from_db()
        if job.estado == DnsScanJob.Estado.CANCELLED:
            registrar_log(
                f"Escaneo DNS cancelado: {job.target}",
                nivel="warning",
                origen="dns_subfinder",
                usuario=job.creado_por,
            )
            return

        if proc.returncode != 0 and not stdout.strip():
            job.estado = DnsScanJob.Estado.ERROR
            job.error_msg = stderr.strip() or f"subfinder terminó con código {proc.returncode}"
            job.save(update_fields=["estado", "error_msg", "actualizado"])
            registrar_log(
                f"Error en escaneo DNS: {job.target}",
                nivel="error",
                origen="dns_subfinder",
                detalle=job.error_msg,
                usuario=job.creado_por,
            )
            return

        subdominios = [linea.strip() for linea in stdout.splitlines() if linea.strip()]

        job.resultado = "\n".join(subdominios)
        job.total_subdominios = len(subdominios)
        job.estado = DnsScanJob.Estado.DONE
        job.save(update_fields=["resultado", "total_subdominios", "estado", "actualizado"])

        registrar_log(
            f"Escaneo DNS completado: {job.target} ({len(subdominios)} subdominios)",
            nivel="info",
            origen="dns_subfinder",
            usuario=job.creado_por,
        )

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()


def cancelar_escaneo(job):
    """Intenta matar el proceso de subfinder asociado a este job."""
    if job.pid:
        try:
            os.kill(job.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass  # el proceso ya había terminado por su cuenta

    job.estado = job.Estado.CANCELLED
    job.save(update_fields=["estado", "actualizado"])