"""Armado del mail de confirmacion de compra."""
from collections import Counter
from dataclasses import dataclass

from ecoharmony.dominio.formatos import formatear_fecha, formatear_monto
from ecoharmony.dominio.pagos import FormaDePago
from ecoharmony.dominio.pases import Pase
from ecoharmony.dominio.precios import (
    EDAD_MAX_MENOR_CON_DESCUENTO,
    EDAD_MIN_MAYOR_CON_DESCUENTO,
    calcular_precio,
)

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


NOMBRE_DE_PASE = {Pase.VIP: "VIP", Pase.COMUN: "Común"}
CATEGORIAS_DE_EDAD = ("menor", "adulto", "adulto mayor")


def categoria_de_edad(edad):
    # Mismos cortes que los descuentos por edad (FAQ 7).
    if edad <= EDAD_MAX_MENOR_CON_DESCUENTO:
        return "menor"
    if edad >= EDAD_MIN_MAYOR_CON_DESCUENTO:
        return "adulto mayor"
    return "adulto"


def contenido_qr(compra):
    # Texto legible que se lee en la entrada del parque (respuesta del PO
    # al S5): orden, fecha, total y detalle por pase y edad.
    cantidad = compra.cantidad_de_entradas
    lineas = [
        "EcoHarmony Park",
        f"Orden N° {compra.numero_orden} - "
        f"{formatear_fecha(compra.fecha_visita)}",
        f"Total: {cantidad} {'entrada' if cantidad == 1 else 'entradas'}",
    ]
    grupos = Counter(
        (v.pase, categoria_de_edad(v.edad)) for v in compra.visitantes
    )
    for pase in (Pase.VIP, Pase.COMUN):
        for categoria in CATEGORIAS_DE_EDAD:
            if grupos[(pase, categoria)]:
                lineas.append(
                    f"{grupos[(pase, categoria)]} "
                    f"{NOMBRE_DE_PASE[pase]} {categoria}"
                )
    return "\n".join(lineas)


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
    codigo_qr = contenido_qr(compra)
    lineas += [
        "",
        "Tu código QR de ingreso (adjunto) contiene:",
        # Se omiten las dos primeras lineas (nombre del parque y orden),
        # que ya figuran arriba.
        *codigo_qr.split("\n")[2:],
    ]
    return Mail(
        destinatario=compra.email_usuario,
        asunto=(
            "EcoHarmony Park: confirmación de compra, "
            f"orden {compra.numero_orden}"
        ),
        cuerpo="\n".join(lineas),
        codigo_qr=codigo_qr,
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
