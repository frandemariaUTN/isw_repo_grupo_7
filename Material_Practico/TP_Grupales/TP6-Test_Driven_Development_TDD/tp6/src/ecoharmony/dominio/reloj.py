"""Hora local del parque. Argentina no tiene horario de verano (UTC-3)."""
from datetime import timedelta, timezone

ZONA_PARQUE = timezone(timedelta(hours=-3), "ART")


def a_hora_local(instante):
    if instante.tzinfo is None:
        raise ValueError("El instante debe incluir zona horaria.")
    return instante.astimezone(ZONA_PARQUE)


def hoy_local(instante):
    return a_hora_local(instante).date()


def hora_local(instante):
    return a_hora_local(instante).time()
