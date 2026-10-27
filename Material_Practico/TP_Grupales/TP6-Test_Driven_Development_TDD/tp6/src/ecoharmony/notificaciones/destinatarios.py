"""Validacion de la direccion a la que se envia el mail."""
import re

from ecoharmony.dominio.errores import ErrorDeValidacion

_PATRON_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def validar_destinatario(destinatario):
    if not _PATRON_EMAIL.fullmatch(destinatario or ""):
        raise ErrorDeValidacion(
            "email", "La dirección de mail no es válida."
        )
    return destinatario
