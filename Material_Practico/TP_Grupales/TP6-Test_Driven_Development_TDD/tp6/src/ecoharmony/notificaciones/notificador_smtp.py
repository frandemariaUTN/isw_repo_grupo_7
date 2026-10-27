"""Envio real del mail de confirmacion por SMTP (por ejemplo, Gmail).

El mail lleva una version de texto, una version HTML con la imagen del QR
y el QR como adjunto. Los datos de la cuenta salen del archivo .env.
"""
import html
import io
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import make_msgid

import segno

from ecoharmony.notificaciones.destinatarios import validar_destinatario

ESPERA_MAXIMA_EN_SEGUNDOS = 15


class NotificadorError(Exception):
    pass


@dataclass(frozen=True)
class ConfiguracionSMTP:
    host: str
    puerto: int
    usuario: str
    clave: str
    remitente: str

    @classmethod
    def desde_entorno(cls, entorno):
        datos = {
            clave: entorno.get(clave, "").strip()
            for clave in ("SMTP_HOST", "SMTP_PUERTO", "SMTP_USUARIO",
                          "SMTP_CLAVE")
        }
        if not all(datos.values()):
            return None
        usuario = datos["SMTP_USUARIO"]
        return cls(
            host=datos["SMTP_HOST"],
            puerto=int(datos["SMTP_PUERTO"]),
            usuario=usuario,
            clave=datos["SMTP_CLAVE"],
            remitente=entorno.get("SMTP_REMITENTE", "").strip()
            or f"EcoHarmony Park <{usuario}>",
        )


class NotificadorSMTP:
    def __init__(self, configuracion, conectar=smtplib.SMTP):
        self._configuracion = configuracion
        self._conectar = conectar

    def enviar(self, mail):
        validar_destinatario(mail.destinatario)
        mensaje = armar_mensaje(mail, self._configuracion.remitente)
        configuracion = self._configuracion
        try:
            with self._conectar(
                configuracion.host,
                configuracion.puerto,
                timeout=ESPERA_MAXIMA_EN_SEGUNDOS,
            ) as servidor:
                servidor.starttls()
                servidor.login(configuracion.usuario, configuracion.clave)
                servidor.send_message(mensaje)
        except (smtplib.SMTPException, OSError) as error:
            raise NotificadorError("No pudimos enviar el mail.") from error
        return mail.destinatario


def armar_mensaje(mail, remitente):
    mensaje = EmailMessage()
    mensaje["From"] = remitente
    mensaje["To"] = mail.destinatario
    mensaje["Subject"] = mail.asunto
    mensaje.set_content(mail.cuerpo)

    imagen_qr = _qr_en_png(mail.codigo_qr)
    identificador = make_msgid(domain="ecoharmony.park")
    mensaje.add_alternative(
        _cuerpo_html(mail.cuerpo, identificador[1:-1]), subtype="html"
    )
    parte_html = mensaje.get_payload()[1]
    parte_html.add_related(
        imagen_qr, maintype="image", subtype="png", cid=identificador
    )
    mensaje.add_attachment(
        imagen_qr, maintype="image", subtype="png",
        filename="qr-entradas.png",
    )
    return mensaje


def _qr_en_png(contenido):
    imagen = io.BytesIO()
    segno.make(contenido).save(imagen, kind="png", scale=8, border=2)
    return imagen.getvalue()


def _cuerpo_html(cuerpo, identificador_qr):
    parrafos = "<br>".join(html.escape(linea) for linea in cuerpo.split("\n"))
    return (
        '<div style="font-family: Arial, sans-serif; color: #1d2b1f">'
        '<h2 style="color: #386641">EcoHarmony Park</h2>'
        f"<p>{parrafos}</p>"
        f'<p><img src="cid:{identificador_qr}" alt="Código QR" '
        'width="220" height="220"></p>'
        "<p>Presentá este código en la entrada del parque.</p>"
        "</div>"
    )
