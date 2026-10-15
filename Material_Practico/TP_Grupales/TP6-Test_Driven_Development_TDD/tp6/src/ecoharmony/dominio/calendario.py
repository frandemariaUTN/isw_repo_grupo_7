"""Calendario del parque: dias de apertura y fechas disponibles."""
import calendar
from datetime import date, time, timedelta

from ecoharmony.dominio.reloj import hora_local, hoy_local

LUNES = 0
FERIADOS_CERRADO = {(12, 25), (1, 1)}
HORA_LIMITE_COMPRA = time(17, 30)

MOTIVO_PASADA = "La fecha de visita ya pasó."
MOTIVO_LEJANA = "Solo se puede comprar con hasta un mes de anticipación."
MOTIVO_CERRADO = "El parque está cerrado ese día."
MOTIVO_HORARIO = "La compra para hoy se puede hacer hasta las 17:30."


def parque_abierto(fecha):
    if fecha.weekday() == LUNES:
        return False
    return (fecha.month, fecha.day) not in FERIADOS_CERRADO


def sumar_un_mes(fecha):
    mes = fecha.month % 12 + 1
    anio = fecha.year + (1 if fecha.month == 12 else 0)
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    return date(anio, mes, min(fecha.day, ultimo_dia))


def motivo_no_disponible(fecha, ahora):
    hoy = hoy_local(ahora)
    if fecha < hoy:
        return MOTIVO_PASADA
    if fecha > sumar_un_mes(hoy):
        return MOTIVO_LEJANA
    if not parque_abierto(fecha):
        return MOTIVO_CERRADO
    if fecha == hoy and hora_local(ahora) > HORA_LIMITE_COMPRA:
        return MOTIVO_HORARIO
    return None


def dias_no_disponibles(ahora):
    hoy = hoy_local(ahora)
    cantidad_de_dias = (sumar_un_mes(hoy) - hoy).days + 1
    fechas = (hoy + timedelta(days=n) for n in range(cantidad_de_dias))
    return [f for f in fechas if motivo_no_disponible(f, ahora)]
