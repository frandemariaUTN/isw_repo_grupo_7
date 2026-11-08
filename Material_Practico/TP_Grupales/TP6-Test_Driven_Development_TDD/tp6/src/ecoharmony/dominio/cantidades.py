"""Validacion de la cantidad de entradas de una compra."""
from ecoharmony.dominio.conversiones import a_entero
from ecoharmony.dominio.errores import crear_error

LIMITE_POR_FECHA = 10


def validar_cantidad(valor):
    cantidad = a_entero(valor, "cantidad", "La cantidad de entradas")
    if cantidad < 1 or cantidad > LIMITE_POR_FECHA:
        raise crear_error(
            "cantidad",
            f"Se pueden comprar entre 1 y {LIMITE_POR_FECHA} entradas.",
        )
    return cantidad
