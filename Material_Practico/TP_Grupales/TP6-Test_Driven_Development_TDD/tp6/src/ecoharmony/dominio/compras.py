"""Compra de entradas: creacion, conteo de entradas y mensaje final."""
from dataclasses import dataclass
from datetime import date, datetime

from ecoharmony.dominio.cantidades import LIMITE_POR_FECHA, validar_cantidad
from ecoharmony.dominio.errores import ErrorDeValidacion, ErroresDeValidacion
from ecoharmony.dominio.fechas import validar_fecha_visita
from ecoharmony.dominio.formatos import formatear_fecha
from ecoharmony.dominio.pagos import (
    EstadoCompra,
    FormaDePago,
    estado_inicial,
    validar_forma_de_pago,
)
from ecoharmony.dominio.precios import calcular_total
from ecoharmony.dominio.visitantes import construir_visitantes


@dataclass(frozen=True)
class Compra:
    numero_orden: int
    usuario_id: str
    email_usuario: str
    fecha_visita: date
    forma_de_pago: FormaDePago
    visitantes: tuple
    total: int
    estado: EstadoCompra
    creada_en: datetime

    @property
    def cantidad_de_entradas(self):
        return len(self.visitantes)


def contar_entradas(compras):
    return sum(
        compra.cantidad_de_entradas
        for compra in compras
        if compra.estado != EstadoCompra.FALLIDA
    )


def mensaje_final(compra):
    cantidad = compra.cantidad_de_entradas
    sustantivo = "entrada" if cantidad == 1 else "entradas"
    fecha = formatear_fecha(compra.fecha_visita)
    return f"Compraste {cantidad} {sustantivo} para el {fecha}."


def crear_compra(datos, usuario, ahora, repositorio):
    if usuario is None:
        raise ErrorDeValidacion(
            "usuario", "Debe iniciar sesión para comprar entradas."
        )
    errores = []
    fecha = _intentar(
        errores, validar_fecha_visita, datos.get("fecha_visita"), ahora
    )
    cantidad = _intentar(errores, validar_cantidad, datos.get("cantidad"))
    forma = _intentar(
        errores, validar_forma_de_pago, datos.get("forma_de_pago")
    )
    visitantes = _intentar(
        errores, construir_visitantes, datos.get("visitantes")
    )
    _validar_coincidencia(errores, cantidad, visitantes)
    _validar_limite(errores, repositorio, usuario, fecha, cantidad)
    if errores:
        raise ErroresDeValidacion(errores)

    total = calcular_total(visitantes)
    compra = Compra(
        numero_orden=repositorio.siguiente_numero_de_orden(),
        usuario_id=usuario.id,
        email_usuario=usuario.email,
        fecha_visita=fecha,
        forma_de_pago=forma,
        visitantes=tuple(visitantes),
        total=total,
        estado=estado_inicial(forma),
        creada_en=ahora,
    )
    repositorio.guardar(compra)
    return compra


def _intentar(errores, funcion, *argumentos):
    try:
        return funcion(*argumentos)
    except ErrorDeValidacion as error:
        errores.append(error)
        return None


def _validar_coincidencia(errores, cantidad, visitantes):
    if cantidad is None or visitantes is None:
        return
    if cantidad != len(visitantes):
        errores.append(
            ErrorDeValidacion(
                "cantidad",
                "La cantidad no coincide con los visitantes cargados.",
            )
        )


def _validar_limite(errores, repositorio, usuario, fecha, cantidad):
    if fecha is None or cantidad is None:
        return
    previas = contar_entradas(repositorio.compras_de(usuario.id, fecha))
    if previas + cantidad > LIMITE_POR_FECHA:
        restantes = max(LIMITE_POR_FECHA - previas, 0)
        errores.append(
            ErrorDeValidacion(
                "cantidad",
                f"Ya tenés {previas} entradas para esa fecha. "
                f"Podés comprar {restantes} más.",
            )
        )
