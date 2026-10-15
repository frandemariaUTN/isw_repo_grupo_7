"""Calculo del precio de una entrada."""
from ecoharmony.dominio.pases import Pase

PRECIO_POR_PASE = {
    Pase.COMUN: 10000,
    Pase.VIP: 20000,
}

EDAD_MAX_GRATIS = 3
EDAD_MAX_MENOR_CON_DESCUENTO = 15
EDAD_MIN_MAYOR_CON_DESCUENTO = 60


def tiene_descuento_por_edad(edad):
    es_menor = edad <= EDAD_MAX_MENOR_CON_DESCUENTO
    es_mayor = edad >= EDAD_MIN_MAYOR_CON_DESCUENTO
    return es_menor or es_mayor


def calcular_precio(edad, pase):
    precio = PRECIO_POR_PASE[pase]
    if edad <= EDAD_MAX_GRATIS:
        return 0
    if tiene_descuento_por_edad(edad):
        return precio // 2
    return precio



def calcular_total(visitantes):
    return sum(calcular_precio(v.edad, v.pase) for v in visitantes)