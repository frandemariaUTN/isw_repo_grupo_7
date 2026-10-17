"""Notificador de mail simulado (FAQ 5): registra el mail sin enviarlo.

La app muestra un modal "Mail enviado a ..." con la direccion devuelta.
"""
import re

from ecoharmony.dominio.errores import ErrorDeValidacion

_PATRON_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


class NotificadorSimulado:
    def __init__(self):
        self.enviados = []

    def enviar(self, mail):
        if not _PATRON_EMAIL.fullmatch(mail.destinatario or ""):
            raise ErrorDeValidacion(
                "email", "La dirección de mail no es válida."
            )
        self.enviados.append(mail)
        return mail.destinatario
