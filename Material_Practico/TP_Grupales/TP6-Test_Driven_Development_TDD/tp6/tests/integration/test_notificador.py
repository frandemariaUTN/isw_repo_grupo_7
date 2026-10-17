"""Pruebas del notificador de mail simulado (MAIL-01 a MAIL-03)."""
import pytest

from ecoharmony.dominio.errores import ErrorDeValidacion
from ecoharmony.dominio.mails import Mail
from ecoharmony.notificaciones.notificador_simulado import (
    NotificadorSimulado,
)


def mail(destinatario="visitante@ecoharmony.test"):
    return Mail(
        destinatario=destinatario,
        asunto="EcoHarmony Park: confirmación de compra, orden 1",
        cuerpo="¡Gracias por tu compra!",
    )


def test_mail_01_registra_el_mail_enviado():
    notificador = NotificadorSimulado()
    enviado = mail()
    notificador.enviar(enviado)
    assert notificador.enviados == [enviado]


def test_mail_02_destinatario_invalido_no_se_envia():
    notificador = NotificadorSimulado()
    with pytest.raises(ErrorDeValidacion):
        notificador.enviar(mail("no-es-un-mail"))
    assert notificador.enviados == []


def test_mail_03_informa_la_direccion_a_la_que_se_envio():
    notificador = NotificadorSimulado()
    assert notificador.enviar(mail()) == "visitante@ecoharmony.test"
