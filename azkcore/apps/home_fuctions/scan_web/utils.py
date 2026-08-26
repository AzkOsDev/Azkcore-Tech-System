import re
import shutil
import subprocess
import threading

from apps.logs.utils import registrar_log

# ---------------------------------------------------------------------------
# Validaciones
# ---------------------------------------------------------------------------

TARGET_RE = re.compile(
    r"^(https?://)?"
    r"(?=.{1,253}$)"
    r"(([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*)"
    r"(:[0-9]{1,5})?"
    r"(/[a-zA-Z0-9\-._~%/]*)?$"
)

SEVERITY_RE = re.compile(r"^[a-z]+(,[a-z]+)*$")
TAGS_RE = re.compile(r"^[a-zA-Z0-9_\-,]+$")
TOKEN_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")
PORT_RE = re.compile(r"^[0-9]{1,5}$")
EXT_RE = re.compile(r"^[a-zA-Z0-9,]+$")

WPSCAN_ENUM_CHOICES = {"vp", "vt", "u", "ap,at,cb,dbe"}
NIKTO_SSL_CHOICES = {"auto", "on", "off"}
GOBUSTER_WORDLIST_CHOICES = {"common", "medium", "big"}


class InvalidTargetError(Exception):
    pass


class InvalidOptionError(Exception):
    pass


def validar_target(target: str) -> str:
    target = target.strip()
    if not TARGET_RE.match(target):
        raise InvalidTargetError(
            "Target inválido. Usa una URL o hostname válido, sin espacios ni caracteres especiales."
        )
    return target


def _validar_opciones(herramienta: str, opciones: dict) -> dict:
    limpio = {}

    if herramienta == "nuclei":
        severity = (opciones.get("nuclei_severity") or "all").strip()
        tags = (opciones.get("nuclei_tags") or "").strip()

        if severity != "all" and not SEVERITY_RE.match(severity):
            raise InvalidOptionError("Severidad de Nuclei inválida.")
        if tags and not TAGS_RE.match(tags):
            raise InvalidOptionError("Tags de Nuclei inválidos.")

        limpio["severity"] = severity
        limpio["tags"] = tags

    elif herramienta == "wpscan":
        enumerate_ = (opciones.get("wpscan_enumerate") or "vp").strip()
        token = (opciones.get("wpscan_token") or "").strip()

        if enumerate_ not in WPSCAN_ENUM_CHOICES:
            raise InvalidOptionError("Opción de enumeración de WPScan inválida.")
        if token and not TOKEN_RE.match(token):
            raise InvalidOptionError("API Token de WPScan inválido.")

        limpio["enumerate"] = enumerate_
        limpio["token"] = token

    elif herramienta == "nikto":
        port = (opciones.get("nikto_port") or "443").strip()
        ssl = (opciones.get("nikto_ssl") or "auto").strip()

        if not PORT_RE.match(port) or not (0 < int(port) < 65536):
            raise InvalidOptionError("Puerto de Nikto inválido.")
        if ssl not in NIKTO_SSL_CHOICES:
            raise InvalidOptionError("Opción SSL de Nikto inválida.")

        limpio["port"] = port
        limpio["ssl"] = ssl

    else:
        raise InvalidOptionError("Herramienta desconocida.")

    return limpio


def _build_cmd(job) -> list:
    from .models import ScanWeb

    target = job.target
    opts = job.opciones or {}

    if job.herramienta == ScanWeb.Herramienta.NUCLEI:
        cmd = ["nuclei", "-u", target, "-nc"]
        severity = opts.get("severity", "all")
        if severity and severity != "all":
            cmd += ["-severity", severity]
        tags = opts.get("tags", "")
        if tags:
            cmd += ["-tags", tags]
        return cmd

    if job.herramienta == ScanWeb.Herramienta.WPSCAN:
        cmd = ["wpscan", "--url", target, "--no-banner", "--random-user-agent"]
        enumerate_ = opts.get("enumerate", "vp")
        cmd += ["--enumerate", enumerate_]
        token = opts.get("token", "")
        if token:
            cmd += ["--api-token", token]
        return cmd

    if job.herramienta == ScanWeb.Herramienta.NIKTO:
        cmd = ["nikto", "-h", target]
        port = opts.get("port", "443")
        cmd += ["-p", port]
        ssl = opts.get("ssl", "auto")
        if ssl == "on":
            cmd += ["-ssl"]
        elif ssl == "off":
            cmd += ["-nossl"]
        return cmd

    raise InvalidOptionError("Herramienta desconocida.")


TOOL_BINARIES = {
    "nuclei": "nuclei",
    "wpscan": "wpscan",
    "nikto": "nikto",
}

TOOL_TIMEOUTS = {
    "nuclei": 900,
    "wpscan": 900,
    "nikto": 1200,
}


def preparar_opciones(herramienta: str, post_data) -> dict:
    return _validar_opciones(herramienta, post_data)


def lanzar_escaneo_async(scan_job_id):
    from .models import ScanWeb

    def _run():
        job = ScanWeb.objects.get(id=scan_job_id)
        job.estado = ScanWeb.Estado.RUNNING
        job.save(update_fields=["estado", "actualizado"])

        registrar_log(
            f"Escaneo web iniciado: {job.target} ({job.get_herramienta_display()})",
            nivel="info",
            origen="scan_web",
            usuario=job.creado_por,
        )

        binario = TOOL_BINARIES.get(job.herramienta)
        if binario is None or shutil.which(binario) is None:
            job.estado = ScanWeb.Estado.ERROR
            job.error_msg = f"{binario or job.herramienta} no está instalado en el servidor."
            job.save(update_fields=["estado", "error_msg", "actualizado"])
            registrar_log(
                f"Error en escaneo web: {job.error_msg}",
                nivel="error",
                origen="scan_web",
                usuario=job.creado_por,
            )
            return

        try:
            cmd = _build_cmd(job)
        except InvalidOptionError as exc:
            job.estado = ScanWeb.Estado.ERROR
            job.error_msg = str(exc)
            job.save(update_fields=["estado", "error_msg", "actualizado"])
            return

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        job.pid = proc.pid
        job.save(update_fields=["pid"])

        timeout = TOOL_TIMEOUTS.get(job.herramienta, 900)
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()

        job.refresh_from_db()
        if job.estado == ScanWeb.Estado.CANCELLED:
            registrar_log(
                f"Escaneo web cancelado: {job.target}",
                nivel="warning",
                origen="scan_web",
                usuario=job.creado_por,
            )
            return

        es_error = proc.returncode != 0 and job.herramienta != ScanWeb.Herramienta.WPSCAN

        if es_error and not stdout.strip():
            job.estado = ScanWeb.Estado.ERROR
            job.error_msg = stderr.strip() or f"{job.herramienta} terminó con código {proc.returncode}"
            job.save(update_fields=["estado", "error_msg", "actualizado"])
            registrar_log(
                f"Error en escaneo web: {job.target}",
                nivel="error",
                origen="scan_web",
                detalle=job.error_msg,
                usuario=job.creado_por,
            )
            return

        job.resultado = stdout or stderr
        job.estado = ScanWeb.Estado.DONE
        job.save(update_fields=["resultado", "estado", "actualizado"])

        registrar_log(
            f"Escaneo web completado: {job.target}",
            nivel="info",
            origen="scan_web",
            usuario=job.creado_por,
        )

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()


def cancelar_escaneo(job):
    import os
    import signal

    if job.pid:
        try:
            os.kill(job.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass

    job.estado = job.Estado.CANCELLED
    job.save(update_fields=["estado", "actualizado"])