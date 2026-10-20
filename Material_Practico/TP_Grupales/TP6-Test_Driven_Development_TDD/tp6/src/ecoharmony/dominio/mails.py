"""Armado del mail de confirmacion de compra."""
from dataclasses import dataclass

from ecoharmony.dominio.formatos import formatear_fecha, formatear_monto
from ecoharmony.dominio.pagos import FormaDePago
from ecoharmony.dominio.precios import calcular_precio

NOMBRE_DE_FORMA_DE_PAGO = {
    FormaDePago.EFECTIVO: "Efectivo",
    FormaDePago.TARJETA: "Tarjeta",
}


@dataclass(frozen=True)
class Mail:
    destinatario: str
    asunto: str
    cuerpo: str
    codigo_qr: str = ""


def contenido_qr(compra):
    # Lo que se lee en la entrada del parque (respuesta del PO al S5).
    return (
        f"ECOHARMONY|ORDEN:{compra.numero_orden}"
        f"|FECHA:{compra.fecha_visita.isoformat()}"
        f"|ENTRADAS:{compra.cantidad_de_entradas}"
    )


def armar_mail(compra):
    forma = NOMBRE_DE_FORMA_DE_PAGO[compra.forma_de_pago]
    lineas = [
        "¡Gracias por tu compra en EcoHarmony Park!",
        "",
        f"Número de orden: {compra.numero_orden}",
        f"Fecha de visita: {formatear_fecha(compra.fecha_visita)}",
        f"Forma de pago: {forma}",
        "",
        "Visitantes:",
        *_detalle_de_visitantes(compra),
        "",
        f"Total: {formatear_monto(compra.total)}",
    ]
    if compra.forma_de_pago == FormaDePago.EFECTIVO:
        lineas += [
            "",
            "Recordá abonar en boletería antes de ingresar al parque.",
        ]
    return Mail(
        destinatario=compra.email_usuario,
        asunto=(
            "EcoHarmony Park: confirmación de compra, "
            f"orden {compra.numero_orden}"
        ),
        cuerpo="\n".join(lineas),
        codigo_qr=contenido_qr(compra),
    )


def _detalle_de_visitantes(compra):
    for posicion, visitante in enumerate(compra.visitantes, start=1):
        subtotal = formatear_monto(
            calcular_precio(visitante.edad, visitante.pase)
        )
        yield (
            f"- Visitante {posicion}: {visitante.edad} años, "
            f"pase {visitante.pase.value}, {subtotal}"
        )
