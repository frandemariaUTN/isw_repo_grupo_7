"""Calculo del precio de una entrada."""

from ecoharmony.dominio.pases import Pase

PRECIO_POR_PASE = {
    Pase.COMUN: 10000,
    Pase.VIP: 20000,
}


def calcular_precio(edad, pase):
    precio = PRECIO_POR_PASE[pase]
    if edad <= 3:
        return 0
    if edad <= 15:
        return precio // 2
    return precio