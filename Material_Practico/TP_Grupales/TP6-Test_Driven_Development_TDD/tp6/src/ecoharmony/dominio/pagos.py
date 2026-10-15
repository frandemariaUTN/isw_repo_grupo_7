"""Formas de pago y estados de una compra."""
from enum import Enum

from ecoharmony.dominio.errores import ErrorDeValidacion


class FormaDePago(Enum):
    EFECTIVO = "EFECTIVO"
    TARJETA = "TARJETA"


class EstadoCompra(Enum):
    PENDIENTE_BOLETERIA = "PENDIENTE_BOLETERIA"
    PENDIENTE_PAGO_ONLINE = "PENDIENTE_PAGO_ONLINE"
    PAGADA = "PAGADA"
    FALLIDA = "FALLIDA"


class ResultadoDePago(Enum):
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    PENDIENTE = "PENDIENTE"


def validar_forma_de_pago(valor):
    if isinstance(valor, FormaDePago):
        return valor
    if valor is None or not str(valor).strip():
        raise ErrorDeValidacion(
            "forma_de_pago", "Debe seleccionar la forma de pago."
        )
    try:
        return FormaDePago(str(valor).strip().upper())
    except ValueError:
        raise ErrorDeValidacion(
            "forma_de_pago", "La forma de pago no es válida."
        ) from None


def estado_inicial(forma_de_pago, total):
    if forma_de_pago == FormaDePago.EFECTIVO:
        return EstadoCompra.PENDIENTE_BOLETERIA
    if total == 0:
        return EstadoCompra.PAGADA
    return EstadoCompra.PENDIENTE_PAGO_ONLINE


def aplicar_resultado_de_pago(estado, resultado):
    if estado != EstadoCompra.PENDIENTE_PAGO_ONLINE:
        return estado
    if resultado == ResultadoDePago.APROBADO:
        return EstadoCompra.PAGADA
    if resultado == ResultadoDePago.RECHAZADO:
        return EstadoCompra.FALLIDA
    return estado
