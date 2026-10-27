"""Pruebas del envio real de mails por SMTP (MAIL-04 a MAIL-12).

Salvo MAIL-11, usan un servidor SMTP falso: no se envia nada de verdad.
"""
import os
import smtplib
from pathlib import Path

import pytest

from ecoharmony.configuracion import cargar_env
from ecoharmony.dominio.errores import ErrorDeValidacion
from ecoharmony.dominio.mails import Mail
from ecoharmony.notificaciones import elegir_notificador
from ecoharmony.notificaciones.notificador_simulado import (
    NotificadorSimulado,
)
from ecoharmony.notificaciones.notificador_smtp import (
    ConfiguracionSMTP,
    NotificadorError,
    NotificadorSMTP,
    armar_mensaje,
)

CONFIGURACION = ConfiguracionSMTP(
    host="smtp.ejemplo.test",
    puerto=587,
    usuario="parque@ejemplo.test",
    clave="clave-de-prueba",
    remitente="EcoHarmony Park <parque@ejemplo.test>",
)


def mail(destinatario="danogamer987654321@gmail.com"):
    return Mail(
        destinatario=destinatario,
        asunto="EcoHarmony Park: confirmación de compra, orden 7",
        cuerpo="¡Gracias por tu compra!\nNúmero de orden: 7",
        codigo_qr="EcoHarmony Park\nOrden N° 7 - 20/10/2026",
    )


class ServidorFalso:
    def __init__(self):
        self.conexiones = []
        self.pasos = []
        self.enviado = None

    def __call__(self, host, puerto, timeout=None):
        self.conexiones.append((host, puerto))
        return self

    def __enter__(self):
        return self

    def __exit__(self, *excepcion):
        return False

    def starttls(self):
        self.pasos.append("starttls")

    def login(self, usuario, clave):
        self.pasos.append(("login", usuario, clave))

    def send_message(self, mensaje):
        self.pasos.append("enviar")
        self.enviado = mensaje


def partes(mensaje):
    return {
        parte.get_content_type(): parte for parte in mensaje.walk()
    }


def test_mail_04_el_mensaje_tiene_remitente_destinatario_y_asunto():
    mensaje = armar_mensaje(mail(), CONFIGURACION.remitente)
    assert mensaje["From"] == "EcoHarmony Park <parque@ejemplo.test>"
    assert mensaje["To"] == "danogamer987654321@gmail.com"
    assert mensaje["Subject"] == (
        "EcoHarmony Park: confirmación de compra, orden 7"
    )


def test_mail_05_el_mensaje_tiene_version_de_texto_y_html():
    encontradas = partes(armar_mensaje(mail(), CONFIGURACION.remitente))
    assert "Número de orden: 7" in encontradas["text/plain"].get_content()
    assert "Número de orden: 7" in encontradas["text/html"].get_content()


def test_mail_06_el_qr_va_dentro_del_html_y_como_adjunto():
    mensaje = armar_mensaje(mail(), CONFIGURACION.remitente)
    imagenes = [
        p for p in mensaje.walk() if p.get_content_type() == "image/png"
    ]
    html = partes(mensaje)["text/html"].get_content()
    identificador = imagenes[0]["Content-ID"].strip("<>")
    assert f'src="cid:{identificador}"' in html
    adjuntos = [p.get_filename() for p in imagenes if p.get_filename()]
    assert adjuntos == ["qr-entradas.png"]


def test_mail_07_envia_con_conexion_segura_e_inicio_de_sesion():
    servidor = ServidorFalso()
    notificador = NotificadorSMTP(CONFIGURACION, conectar=servidor)
    assert notificador.enviar(mail()) == "danogamer987654321@gmail.com"
    assert servidor.conexiones == [("smtp.ejemplo.test", 587)]
    assert servidor.pasos == [
        "starttls",
        ("login", "parque@ejemplo.test", "clave-de-prueba"),
        "enviar",
    ]


@pytest.mark.parametrize(
    "falla",
    [
        pytest.param(OSError("sin red"), id="MAIL-08-sin-conexion"),
        pytest.param(
            smtplib.SMTPAuthenticationError(535, b"clave incorrecta"),
            id="MAIL-08-clave-incorrecta",
        ),
    ],
)
def test_una_falla_del_servidor_lanza_error_controlado(falla):
    def conectar(host, puerto, timeout=None):
        raise falla

    notificador = NotificadorSMTP(CONFIGURACION, conectar=conectar)
    with pytest.raises(NotificadorError):
        notificador.enviar(mail())


def test_mail_09_destinatario_invalido_no_intenta_conectarse():
    servidor = ServidorFalso()
    notificador = NotificadorSMTP(CONFIGURACION, conectar=servidor)
    with pytest.raises(ErrorDeValidacion):
        notificador.enviar(mail("no-es-un-mail"))
    assert servidor.conexiones == []


@pytest.mark.parametrize(
    "entorno, esperado",
    [
        pytest.param(
            {
                "SMTP_HOST": "smtp.gmail.com",
                "SMTP_PUERTO": "587",
                "SMTP_USUARIO": "cuenta@gmail.com",
                "SMTP_CLAVE": "abcd efgh ijkl mnop",
            },
            ConfiguracionSMTP(
                host="smtp.gmail.com",
                puerto=587,
                usuario="cuenta@gmail.com",
                clave="abcd efgh ijkl mnop",
                remitente="EcoHarmony Park <cuenta@gmail.com>",
            ),
            id="MAIL-10-completa",
        ),
        pytest.param(
            {"SMTP_HOST": "smtp.gmail.com"}, None, id="MAIL-10-incompleta"
        ),
    ],
)
def test_la_configuracion_se_lee_del_entorno(entorno, esperado):
    assert ConfiguracionSMTP.desde_entorno(entorno) == esperado


@pytest.mark.smtp_real
def test_mail_11_envio_real_a_la_casilla_de_pruebas():
    cargar_env(Path(__file__).parents[2] / ".env")
    configuracion = ConfiguracionSMTP.desde_entorno(os.environ)
    if configuracion is None:
        pytest.skip("Falta la configuracion SMTP en el .env")
    destino = os.environ.get(
        "SMTP_DESTINO_PRUEBAS", "danogamer987654321@gmail.com"
    )
    enviado = NotificadorSMTP(configuracion).enviar(mail(destino))
    assert enviado == destino


@pytest.mark.parametrize(
    "entorno, tipo",
    [
        pytest.param(
            {
                "SMTP_HOST": "smtp.gmail.com",
                "SMTP_PUERTO": "587",
                "SMTP_USUARIO": "cuenta@gmail.com",
                "SMTP_CLAVE": "clave",
            },
            NotificadorSMTP,
            id="MAIL-12-con-configuracion",
        ),
        pytest.param({}, NotificadorSimulado, id="MAIL-12-sin-configuracion"),
    ],
)
def test_se_elige_el_envio_real_solo_si_hay_configuracion(entorno, tipo):
    assert isinstance(elegir_notificador(entorno), tipo)
