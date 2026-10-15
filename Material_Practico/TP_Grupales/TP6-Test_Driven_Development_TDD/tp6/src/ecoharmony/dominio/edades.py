"""Validacion de la edad de un visitante."""
from ecoharmony.dominio.errores import crear_error

EDAD_MAXIMA = 120


def validar_edad(valor, posicion=None):
    edad = _a_entero(valor, posicion)
    if edad < 0 or edad > EDAD_MAXIMA:
        raise crear_error(
            "edad",
            f"La edad debe estar entre 0 y {EDAD_MAXIMA}.",
            posicion,
        )
    return edad


def _a_entero(valor, posicion):
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise crear_error("edad", "La edad es obligatoria.", posicion)
    if isinstance(valor, (bool, float)):
        raise crear_error("edad", "La edad debe ser un entero.", posicion)
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise crear_error(
            "edad", "La edad debe ser un entero.", posicion
        ) from None
