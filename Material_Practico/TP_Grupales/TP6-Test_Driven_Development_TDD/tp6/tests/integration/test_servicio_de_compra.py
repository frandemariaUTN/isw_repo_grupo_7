"""Pruebas del servicio de compra (SRV-01 a SRV-14)."""
from datetime import date, datetime, timedelta, timezone

import pytest

from ecoharmony.aplicacion.servicio_de_compra import ServicioDeCompra
from ecoharmony.dominio.errores import ErroresDeValidacion
from ecoharmony.dominio.pagos import EstadoCompra
from ecoharmony.dominio.pasarela import PasarelaSimulada
from ecoharmony.dominio.repositorio import RepositorioEnMemoria
from ecoharmony.dominio.usuarios import usuario_mock
from ecoharmony.notificaciones.notificador_simulado import (
    NotificadorSimulado,
)
from ecoharmony.persistencia.repositorio_sqlite import RepositorioSQLite

ART = timezone(timedelta(hours=-3))
AHORA = datetime(2026, 10, 14, 10, 0, tzinfo=ART)
FECHA = date(2026, 10, 20)
USUARIO = usuario_mock()


def datos_compra(forma="tarjeta", edades=(30, 10), **cambios):
    datos = {
        "fecha_visita": "2026-10-20",
        "cantidad": len(edades),
        "visitantes": [{"edad": edad, "pase": "COMUN"} for edad in edades],
        "forma_de_pago": forma,
    }
    datos.update(cambios)
    return datos


def tarjeta(titular="APRO"):
    return {
        "numero": "4509 9535 6623 3704",
        "titular": titular,
        "vencimiento": "11/30",
        "codigo": "123",
        "dni": "12345678",
    }


@pytest.fixture
def repositorio():
    return RepositorioEnMemoria()


@pytest.fixture
def notificador():
    return NotificadorSimulado()


@pytest.fixture
def pasarela():
    return PasarelaSimulada()


@pytest.fixture
def servicio(repositorio, pasarela, notificador):
    return ServicioDeCompra(repositorio, pasarela, notificador)


def token_de(resultado):
    return resultado.url_pago.rsplit("/", 1)[-1]


def test_srv_01_efectivo_queda_pendiente_en_boleteria_y_envia_mail(
    servicio, repositorio, notificador
):
    resultado = servicio.comprar(datos_compra("efectivo"), USUARIO, AHORA)
    guardada = repositorio.buscar(resultado.compra.numero_orden)
    assert guardada.estado == EstadoCompra.PENDIENTE_BOLETERIA
    assert len(notificador.enviados) == 1
    assert resultado.url_pago is None


def test_srv_02_tarjeta_queda_pendiente_y_devuelve_url_de_la_pasarela(
    servicio, repositorio, notificador, pasarela
):
    resultado = servicio.comprar(datos_compra(), USUARIO, AHORA)
    guardada = repositorio.buscar(resultado.compra.numero_orden)
    assert guardada.estado == EstadoCompra.PENDIENTE_PAGO_ONLINE
    assert resultado.url_pago.startswith("/pasarela/")
    assert pasarela.buscar(token_de(resultado)) is not None
    assert notificador.enviados == []


def test_srv_03_datos_invalidos_no_crean_compra_ni_sesion(
    servicio, repositorio, notificador
):
    datos = datos_compra(fecha_visita="", cantidad=11)
    with pytest.raises(ErroresDeValidacion):
        servicio.comprar(datos, USUARIO, AHORA)
    assert repositorio.compras_de(USUARIO.id, FECHA) == []
    assert notificador.enviados == []


def test_srv_04_pago_aprobado_deja_la_compra_pagada_y_envia_mail(
    servicio, repositorio, notificador
):
    compra = servicio.comprar(datos_compra(), USUARIO, AHORA)
    servicio.pagar(token_de(compra), tarjeta("APRO"), AHORA)
    guardada = repositorio.buscar(compra.compra.numero_orden)
    assert guardada.estado == EstadoCompra.PAGADA
    assert len(notificador.enviados) == 1


def test_srv_05_pago_rechazado_deja_la_compra_fallida_sin_mail(
    servicio, repositorio, notificador
):
    compra = servicio.comprar(datos_compra(), USUARIO, AHORA)
    resultado = servicio.pagar(token_de(compra), tarjeta("OTHE"), AHORA)
    guardada = repositorio.buscar(compra.compra.numero_orden)
    assert guardada.estado == EstadoCompra.FALLIDA
    assert resultado.motivo == "El pago fue rechazado."
    assert notificador.enviados == []


def test_srv_06_pago_pendiente_no_cambia_la_compra_ni_envia_mail(
    servicio, repositorio, notificador
):
    compra = servicio.comprar(datos_compra(), USUARIO, AHORA)
    servicio.pagar(token_de(compra), tarjeta("CONT"), AHORA)
    guardada = repositorio.buscar(compra.compra.numero_orden)
    assert guardada.estado == EstadoCompra.PENDIENTE_PAGO_ONLINE
    assert notificador.enviados == []


def test_srv_07_pagar_dos_veces_es_idempotente(servicio, notificador):
    compra = servicio.comprar(datos_compra(), USUARIO, AHORA)
    primero = servicio.pagar(token_de(compra), tarjeta("APRO"), AHORA)
    segundo = servicio.pagar(token_de(compra), tarjeta("OTHE"), AHORA)
    assert segundo.compra.estado == EstadoCompra.PAGADA
    assert segundo.compra == primero.compra
    assert len(notificador.enviados) == 1


def test_srv_08_cancelar_el_pago_deja_la_compra_fallida(
    servicio, repositorio
):
    compra = servicio.comprar(datos_compra(), USUARIO, AHORA)
    servicio.cancelar(token_de(compra))
    guardada = repositorio.buscar(compra.compra.numero_orden)
    assert guardada.estado == EstadoCompra.FALLIDA


def test_srv_09_con_sqlite_el_limite_suma_compras_previas(
    tmp_path, pasarela, notificador
):
    repositorio = RepositorioSQLite(tmp_path / "ecoharmony.db")
    servicio = ServicioDeCompra(repositorio, pasarela, notificador)
    cinco = datos_compra("efectivo", edades=(30,) * 5)
    servicio.comprar(cinco, USUARIO, AHORA)
    servicio.comprar(cinco, USUARIO, AHORA)
    with pytest.raises(ErroresDeValidacion):
        servicio.comprar(
            datos_compra("efectivo", edades=(30,)), USUARIO, AHORA
        )


def test_srv_10_validacion_fallida_no_cambia_la_base(
    tmp_path, pasarela, notificador
):
    repositorio = RepositorioSQLite(tmp_path / "ecoharmony.db")
    servicio = ServicioDeCompra(repositorio, pasarela, notificador)
    with pytest.raises(ErroresDeValidacion):
        servicio.comprar(datos_compra(forma_de_pago=""), USUARIO, AHORA)
    assert repositorio.compras_de(USUARIO.id, FECHA) == []


def test_srv_11_una_compra_fallida_libera_el_cupo(servicio):
    diez = datos_compra(edades=(30,) * 10)
    fallida = servicio.comprar(diez, USUARIO, AHORA)
    servicio.cancelar(token_de(fallida))
    nueva = servicio.comprar(diez, USUARIO, AHORA)
    assert nueva.compra.cantidad_de_entradas == 10


@pytest.mark.parametrize(
    "forma",
    [
        pytest.param("efectivo", id="SRV-12-efectivo"),
        pytest.param("tarjeta", id="SRV-12-tarjeta-aprobada"),
    ],
)
def test_compra_confirmada_informa_el_mail_para_el_modal(servicio, forma):
    resultado = servicio.comprar(datos_compra(forma), USUARIO, AHORA)
    if forma == "tarjeta":
        resultado = servicio.pagar(token_de(resultado), tarjeta(), AHORA)
    assert resultado.mail_enviado_a == USUARIO.email


def test_srv_13_tarjeta_con_total_cero_no_pasa_por_la_pasarela(
    servicio, notificador
):
    resultado = servicio.comprar(
        datos_compra(edades=(2, 3)), USUARIO, AHORA
    )
    assert resultado.compra.estado == EstadoCompra.PAGADA
    assert resultado.url_pago is None
    assert len(notificador.enviados) == 1


def test_srv_14_pago_aprobado_informa_cantidad_y_fecha(servicio):
    compra = servicio.comprar(datos_compra(), USUARIO, AHORA)
    resultado = servicio.pagar(token_de(compra), tarjeta(), AHORA)
    assert resultado.mensaje == "Compraste 2 entradas para el 20/10/2026."
