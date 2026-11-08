"""Notificador de mail simulado: registra el mail sin enviarlo.

Se usa en los tests y cuando la app no tiene configurado el envio real.
"""
from ecoharmony.notificaciones.destinatarios import validar_destinatario


class NotificadorSimulado:
    def __init__(self):
        self.enviados = []

    def enviar(self, mail):
        validar_destinatario(mail.destinatario)
        self.enviados.append(mail)
        return mail.destinatario
