"""Servicio de compra: une la compra, el repositorio, la pasarela y el mail."""
from dataclasses import dataclass, replace

from ecoharmony.dominio.compras import crear_compra, mensaje_final
from ecoharmony.dominio.errores import ErrorDeNotificacion
from ecoharmony.dominio.mails import armar_mail
from ecoharmony.dominio.pagos import (
    EstadoCompra,
    ResultadoDePago,
    aplicar_resultado_de_pago,
)
from ecoharmony.dominio.pasarela import EstadoSesion

AVISO_SIN_MAIL = (
    "No pudimos enviar el mail de confirmación. "
    "Tu compra quedó registrada igual."
)


@dataclass(frozen=True)
class ResultadoDeCompra:
    compra: object
    url_pago: str = None
    mail_enviado_a: str = None
    mensaje: str = None
    motivo: str = None
    aviso_mail: str = None


class ServicioDeCompra:
    def __init__(self, repositorio, pasarela, notificador):
        self._repositorio = repositorio
        self._pasarela = pasarela
        self._notificador = notificador

    def comprar(self, datos, usuario, ahora):
        compra = crear_compra(datos, usuario, ahora, self._repositorio)
        if compra.estado == EstadoCompra.PENDIENTE_PAGO_ONLINE:
            sesion = self._pasarela.crear_sesion(
                compra.numero_orden, compra.total
            )
            return ResultadoDeCompra(
                compra, url_pago=f"/pasarela/{sesion.token}"
            )
        return self._confirmar(compra)

    def pagar(self, token, datos_tarjeta, ahora):
        sesion = self._pasarela.buscar(token)
        if sesion is not None and sesion.estado != EstadoSesion.ABIERTA:
            # Doble clic o recarga: se devuelve lo ya resuelto.
            return self._resultado_actual(sesion)
        sesion = self._pasarela.pagar(token, datos_tarjeta, ahora)
        compra = self._aplicar(sesion.numero_orden, sesion.resultado)
        if compra.estado == EstadoCompra.PAGADA:
            return self._confirmar(compra)
        return ResultadoDeCompra(compra, motivo=sesion.motivo)

    def cancelar(self, token):
        sesion = self._pasarela.cancelar(token)
        compra = self._aplicar(sesion.numero_orden, ResultadoDePago.RECHAZADO)
        return ResultadoDeCompra(compra)

    def _aplicar(self, numero_orden, resultado):
        compra = self._repositorio.buscar(numero_orden)
        estado = aplicar_resultado_de_pago(compra.estado, resultado)
        if estado != compra.estado:
            compra = replace(compra, estado=estado)
            self._repositorio.guardar(compra)
        return compra

    def _confirmar(self, compra):
        try:
            destinatario = self._notificador.enviar(armar_mail(compra))
        except ErrorDeNotificacion:
            # La compra ya quedo guardada: no se pierde por un problema
            # con el servidor de mail.
            return ResultadoDeCompra(
                compra,
                mensaje=mensaje_final(compra),
                aviso_mail=AVISO_SIN_MAIL,
            )
        return ResultadoDeCompra(
            compra,
            mail_enviado_a=destinatario,
            mensaje=mensaje_final(compra),
        )

    def _resultado_actual(self, sesion):
        compra = self._repositorio.buscar(sesion.numero_orden)
        if compra.estado == EstadoCompra.PAGADA:
            return ResultadoDeCompra(
                compra,
                mail_enviado_a=compra.email_usuario,
                mensaje=mensaje_final(compra),
            )
        return ResultadoDeCompra(compra, motivo=sesion.motivo)
