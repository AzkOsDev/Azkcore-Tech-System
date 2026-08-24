import re
import shutil
import subprocess
import threading

# Solo permite hostnames/IPs razonables. Nada de espacios, ; | & $ ( ) ` etc.
TARGET_RE = re.compile(
    r"^(?=.{1,253}$)"
    r"(([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*)$"
)

NMAP_ARGS = {
    "nmap_fast": ["-F", "-T4"],          # puertos comunes
    "nmap_full": ["-p-", "-T4"],         # todos los puertos
}


class InvalidTargetError(Exception):
    pass


def validar_target(target: str) -> str:
    target = target.strip()
    if not TARGET_RE.match(target):
        raise InvalidTargetError("Target inválido. Usa un hostname o IP válido, sin espacios ni caracteres especiales.")
    return target


def ejecutar_nmap(target: str, tipo: str, timeout: int = 600) -> str:
    if shutil.which("nmap") is None:
        raise RuntimeError("nmap no está instalado en el servidor.")

    args = NMAP_ARGS.get(tipo, NMAP_ARGS["nmap_fast"])
    cmd = ["nmap", *args, target]

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"nmap terminó con código {proc.returncode}")

    return proc.stdout


def lanzar_escaneo_async(scan_job_id):
    """Corre el escaneo en un hilo aparte y actualiza el ScanJob al terminar."""
    from .models import ScanJob  # import local para evitar problemas de import circular

    def _run():
        try:
            job = ScanJob.objects.get(id=scan_job_id)
            job.estado = ScanJob.Estado.RUNNING
            job.save(update_fields=["estado", "actualizado"])

            salida = ejecutar_nmap(job.target, job.tipo)

            job.resultado = salida
            job.estado = ScanJob.Estado.DONE
            job.save(update_fields=["resultado", "estado", "actualizado"])

        except Exception as e:
            try:
                job = ScanJob.objects.get(id=scan_job_id)
                job.estado = ScanJob.Estado.ERROR
                job.error_msg = str(e)
                job.save(update_fields=["estado", "error_msg", "actualizado"])
            except ScanJob.DoesNotExist:
                pass

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()