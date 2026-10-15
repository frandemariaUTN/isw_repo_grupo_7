"""Conversiones de datos de formulario a tipos del dominio."""
from ecoharmony.dominio.errores import crear_error


def a_entero(valor, campo, etiqueta, posicion=None):
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise crear_error(campo, f"{etiqueta} es obligatoria.", posicion)
    if isinstance(valor, (bool, float)):
        raise crear_error(campo, f"{etiqueta} debe ser un entero.", posicion)
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise crear_error(
            campo, f"{etiqueta} debe ser un entero.", posicion
        ) from None
