"""Calculo del precio de una entrada."""

from ecoharmony.dominio.pases import Pase

PRECIO_POR_PASE = {
    Pase.COMUN: 10000,
    Pase.VIP: 20000,
}


def calcular_precio(edad, pase):
    return PRECIO_POR_PASE[pase]