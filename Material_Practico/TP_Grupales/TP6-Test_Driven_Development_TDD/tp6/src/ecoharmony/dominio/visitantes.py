"""Visitante de una compra de entradas."""
from dataclasses import dataclass

from ecoharmony.dominio.edades import validar_edad
from ecoharmony.dominio.errores import ErrorDeValidacion
from ecoharmony.dominio.pases import Pase, validar_pase


@dataclass(frozen=True)
class Visitante:
    edad: int
    pase: Pase


def construir_visitantes(datos):
    if not datos:
        raise ErrorDeValidacion(
            "visitantes", "Debe cargar al menos un visitante."
        )
    return [
        Visitante(
            edad=validar_edad(dato.get("edad"), posicion),
            pase=validar_pase(dato.get("pase"), posicion),
        )
        for posicion, dato in enumerate(datos, start=1)
    ]
