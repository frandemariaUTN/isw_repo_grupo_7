"""Tipos de pase de entrada."""
from enum import Enum

from ecoharmony.dominio.errores import crear_error


class Pase(Enum):
    COMUN = "COMUN"
    VIP = "VIP"


def validar_pase(valor, posicion=None):
    if isinstance(valor, Pase):
        return valor
    if valor is None or not str(valor).strip():
        raise crear_error("pase", "El tipo de pase es obligatorio.", posicion)
    try:
        return Pase(str(valor).strip().upper())
    except ValueError:
        raise crear_error(
            "pase", "El tipo de pase no existe.", posicion
        ) from None
