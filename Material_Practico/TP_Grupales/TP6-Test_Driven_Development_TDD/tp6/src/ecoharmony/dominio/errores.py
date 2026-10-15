"""Errores de validacion del dominio."""


class ErrorDeValidacion(Exception):
    def __init__(self, campo, mensaje):
        super().__init__(mensaje)
        self.campo = campo
        self.mensaje = mensaje


def crear_error(campo, mensaje, posicion=None):
    if posicion is None:
        return ErrorDeValidacion(campo, mensaje)
    return ErrorDeValidacion(
        f"visitantes.{posicion}.{campo}",
        f"Visitante {posicion}: {mensaje}",
    )


class ErroresDeValidacion(Exception):
    def __init__(self, errores):
        super().__init__("; ".join(e.mensaje for e in errores))
        self.errores = list(errores)
