"""Pasarela de pago simulada con el comportamiento de la de Mercado Pago.

El resultado del pago se elige con el nombre del titular, como en las
tarjetas de prueba de Mercado Pago (supuesto S12).
"""
import secrets
from dataclasses import dataclass, replace
from enum import Enum
from itertools import count

from ecoharmony.dominio.pagos import ResultadoDePago
from ecoharmony.dominio.tarjetas import validar_tarjeta

# Titular de prueba: (resultado, motivo). Cualquier otro titular aprueba.
RESULTADOS_POR_TITULAR = {
    "OTHE": (ResultadoDePago.RECHAZADO, "El pago fue rechazado."),
    "FUND": (
        ResultadoDePago.RECHAZADO,
        "La tarjeta no tiene fondos suficientes.",
    ),
    "SECU": (
        ResultadoDePago.RECHAZADO,
        "El código de seguridad es inválido.",
    ),
    "EXPI": (
        ResultadoDePago.RECHAZADO,
        "Hay un problema con la fecha de vencimiento.",
    ),
    "CONT": (
        ResultadoDePago.PENDIENTE,
        "Tu pago está pendiente de acreditación.",
    ),
}


class ErrorDePasarela(Exception):
    pass


class EstadoSesion(Enum):
    ABIERTA = "ABIERTA"
    CERRADA = "CERRADA"
    CANCELADA = "CANCELADA"


@dataclass(frozen=True)
class SesionDePago:
    token: str
    numero_orden: int
    monto: int
    estado: EstadoSesion = EstadoSesion.ABIERTA
    resultado: ResultadoDePago = None
    motivo: str = None
    numero_operacion: int = None
    tarjeta: object = None


class PasarelaSimulada:
    def __init__(self):
        self._sesiones = {}
        self._operaciones = count(1)

    def crear_sesion(self, numero_orden, monto):
        if monto < 0:
            raise ErrorDePasarela("El monto no puede ser negativo.")
        sesion = SesionDePago(
            token=secrets.token_urlsafe(32),
            numero_orden=numero_orden,
            monto=monto,
        )
        self._sesiones[sesion.token] = sesion
        return sesion

    def buscar(self, token):
        return self._sesiones.get(token)

    def pagar(self, token, datos_tarjeta, ahora):
        sesion = self._abierta(token)
        tarjeta = validar_tarjeta(datos_tarjeta, ahora)
        resultado, motivo = RESULTADOS_POR_TITULAR.get(
            tarjeta.titular.upper(), (ResultadoDePago.APROBADO, None)
        )
        return self._actualizar(
            sesion,
            estado=EstadoSesion.CERRADA,
            resultado=resultado,
            motivo=motivo,
            numero_operacion=next(self._operaciones),
            tarjeta=tarjeta,
        )

    def cancelar(self, token):
        sesion = self._abierta(token)
        return self._actualizar(sesion, estado=EstadoSesion.CANCELADA)

    def _abierta(self, token):
        sesion = self.buscar(token)
        if sesion is None or sesion.estado != EstadoSesion.ABIERTA:
            raise ErrorDePasarela("La sesión de pago no está disponible.")
        return sesion

    def _actualizar(self, sesion, **cambios):
        actualizada = replace(sesion, **cambios)
        self._sesiones[sesion.token] = actualizada
        return actualizada
