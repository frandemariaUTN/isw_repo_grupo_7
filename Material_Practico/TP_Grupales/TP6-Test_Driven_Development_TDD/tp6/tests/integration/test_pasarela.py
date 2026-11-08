"""Pruebas de la pasarela de pago simulada (PSM-01 a PSM-19)."""
from datetime import datetime, timedelta, timezone

import pytest

from ecoharmony.dominio.errores import ErroresDeValidacion
from ecoharmony.dominio.pagos import ResultadoDePago
from ecoharmony.dominio.pasarela import (
    ErrorDePasarela,
    EstadoSesion,
    PasarelaSimulada,
)
from ecoharmony.dominio.tarjetas import TarjetaValidada

ART = timezone(timedelta(hours=-3))
AHORA = datetime(2026, 10, 14, 10, 0, tzinfo=ART)


@pytest.fixture
def pasarela():
    return PasarelaSimulada()


@pytest.fixture
def sesion(pasarela):
    return pasarela.crear_sesion(numero_orden=7, monto=25000)


def tarjeta(titular="APRO", **cambios):
    datos = {
        "numero": "5031 7557 3453 0604",
        "titular": titular,
        "vencimiento": "11/30",
        "codigo": "123",
        "dni": "12345678",
    }
    datos.update(cambios)
    return datos


def test_psm_01_crear_sesion_la_deja_abierta_con_token(sesion):
    assert sesion.estado == EstadoSesion.ABIERTA
    assert sesion.token


def test_psm_02_la_sesion_guarda_orden_y_monto(pasarela, sesion):
    guardada = pasarela.buscar(sesion.token)
    assert (guardada.numero_orden, guardada.monto) == (7, 25000)


def test_psm_03_los_tokens_son_distintos_y_largos(pasarela, sesion):
    otra = pasarela.crear_sesion(numero_orden=8, monto=10000)
    assert sesion.token != otra.token
    assert len(sesion.token) >= 32


def test_psm_04_buscar_token_inexistente_devuelve_none(pasarela):
    assert pasarela.buscar("no-existe") is None


@pytest.mark.parametrize(
    "titular",
    [
        pytest.param("APRO", id="PSM-05"),
        pytest.param("Facundo Pérez", id="PSM-06"),
    ],
)
def test_titular_valido_aprueba_el_pago_y_cierra_la_sesion(
    pasarela, sesion, titular
):
    pagada = pasarela.pagar(sesion.token, tarjeta(titular), AHORA)
    assert pagada.resultado == ResultadoDePago.APROBADO
    assert pagada.estado == EstadoSesion.CERRADA
    assert pagada.numero_operacion is not None


@pytest.mark.parametrize(
    "titular, resultado, motivo",
    [
        pytest.param(
            "OTHE", ResultadoDePago.RECHAZADO,
            "El pago fue rechazado.", id="PSM-07",
        ),
        pytest.param(
            "FUND", ResultadoDePago.RECHAZADO,
            "La tarjeta no tiene fondos suficientes.", id="PSM-08",
        ),
        pytest.param(
            "SECU", ResultadoDePago.RECHAZADO,
            "El código de seguridad es inválido.", id="PSM-09",
        ),
        pytest.param(
            "EXPI", ResultadoDePago.RECHAZADO,
            "Hay un problema con la fecha de vencimiento.", id="PSM-10",
        ),
        pytest.param(
            "CONT", ResultadoDePago.PENDIENTE,
            "Tu pago está pendiente de acreditación.", id="PSM-11",
        ),
    ],
)
def test_titular_de_prueba_elige_el_resultado(
    pasarela, sesion, titular, resultado, motivo
):
    pagada = pasarela.pagar(sesion.token, tarjeta(titular), AHORA)
    assert (pagada.resultado, pagada.motivo) == (resultado, motivo)


def test_psm_12_tarjeta_invalida_deja_la_sesion_abierta(pasarela, sesion):
    with pytest.raises(ErroresDeValidacion):
        pasarela.pagar(sesion.token, tarjeta(codigo="12"), AHORA)
    assert pasarela.buscar(sesion.token).estado == EstadoSesion.ABIERTA


def test_psm_13_pagar_sesion_cerrada_falla_sin_cambiar_resultado(
    pasarela, sesion
):
    pasarela.pagar(sesion.token, tarjeta("APRO"), AHORA)
    with pytest.raises(ErrorDePasarela):
        pasarela.pagar(sesion.token, tarjeta("OTHE"), AHORA)
    assert pasarela.buscar(sesion.token).resultado == (
        ResultadoDePago.APROBADO
    )


def test_psm_14_cancelar_sesion_abierta(pasarela, sesion):
    cancelada = pasarela.cancelar(sesion.token)
    assert cancelada.estado == EstadoSesion.CANCELADA


def test_psm_15_pagar_sesion_cancelada_falla(pasarela, sesion):
    pasarela.cancelar(sesion.token)
    with pytest.raises(ErrorDePasarela):
        pasarela.pagar(sesion.token, tarjeta(), AHORA)


def test_psm_16_cancelar_sesion_cerrada_falla_sin_cambiar_resultado(
    pasarela, sesion
):
    pasarela.pagar(sesion.token, tarjeta("APRO"), AHORA)
    with pytest.raises(ErrorDePasarela):
        pasarela.cancelar(sesion.token)
    assert pasarela.buscar(sesion.token).estado == EstadoSesion.CERRADA


def test_psm_17_dos_pagos_tienen_numeros_de_operacion_distintos(pasarela):
    primera = pasarela.crear_sesion(numero_orden=1, monto=10000)
    segunda = pasarela.crear_sesion(numero_orden=2, monto=10000)
    a = pasarela.pagar(primera.token, tarjeta(), AHORA)
    b = pasarela.pagar(segunda.token, tarjeta(), AHORA)
    assert a.numero_operacion != b.numero_operacion


def test_psm_18_se_crea_sesion_con_monto_cero(pasarela):
    sesion = pasarela.crear_sesion(numero_orden=1, monto=0)
    assert (sesion.estado, sesion.monto) == (EstadoSesion.ABIERTA, 0)


def test_psm_19_la_sesion_pagada_solo_guarda_la_tarjeta_validada(
    pasarela, sesion
):
    pagada = pasarela.pagar(sesion.token, tarjeta(), AHORA)
    assert pagada.tarjeta == TarjetaValidada(
        marca="Mastercard", ultimos_digitos="0604", titular="APRO"
    )
