"""Validacion de la fecha de visita."""
from datetime import date

from ecoharmony.dominio.calendario import motivo_no_disponible
from ecoharmony.dominio.errores import ErrorDeValidacion

CAMPO = "fecha_visita"


def validar_fecha_visita(valor, ahora):
    fecha = _a_fecha(valor)
    motivo = motivo_no_disponible(fecha, ahora)
    if motivo is not None:
        raise ErrorDeValidacion(CAMPO, motivo)
    return fecha


def _a_fecha(valor):
    if isinstance(valor, date):
        return valor
    if valor is None or not str(valor).strip():
        raise ErrorDeValidacion(
            CAMPO, "La fecha de visita es obligatoria."
        )
    try:
        return date.fromisoformat(str(valor).strip())
    except ValueError:
        raise ErrorDeValidacion(
            CAMPO, "La fecha de visita no tiene un formato válido."
        ) from None
