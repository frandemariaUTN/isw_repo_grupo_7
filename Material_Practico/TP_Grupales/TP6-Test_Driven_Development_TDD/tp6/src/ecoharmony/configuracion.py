"""Lectura del archivo .env (datos que no se suben a git)."""
import os


def cargar_env(ruta, entorno=os.environ):
    """Carga las lineas CLAVE=valor sin pisar variables ya definidas."""
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#") and "=" in linea:
            clave, valor = linea.split("=", 1)
            entorno.setdefault(clave.strip(), valor.strip())
