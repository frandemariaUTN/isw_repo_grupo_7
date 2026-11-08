"""Validacion de la edad de un visitante."""
from ecoharmony.dominio.conversiones import a_entero
from ecoharmony.dominio.errores import crear_error

EDAD_MAXIMA = 120


def validar_edad(valor, posicion=None):
    edad = a_entero(valor, "edad", "La edad", posicion)
    if edad < 0 or edad > EDAD_MAXIMA:
        raise crear_error(
            "edad",
            f"La edad debe estar entre 0 y {EDAD_MAXIMA}.",
            posicion,
        )
    return edad
