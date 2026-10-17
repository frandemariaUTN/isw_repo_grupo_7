"""Pruebas unitarias de la tarjeta de credito o debito (TAR-01 a TAR-25)."""
from dataclasses import fields

import pytest

from ecoharmony.dominio.errores import ErrorDeValidacion, ErroresDeValidacion
from ecoharmony.dominio.tarjetas import (
    TarjetaValidada,
    marca_de,
    validar_codigo,
    validar_dni,
    validar_numero,
    validar_tarjeta,
    validar_titular,
    validar_vencimiento,
)

MASTERCARD = "5031755734530604"
VISA = "4509953566233704"


@pytest.fixture
def datos_tarjeta():
    return {
        "numero": "5031 7557 3453 0604",
        "titular": "APRO",
        "vencimiento": "11/30",
        "codigo": "123",
        "dni": "12345678",
    }


@pytest.mark.parametrize(
    "valor, esperado",
    [
        pytest.param("5031 7557 3453 0604", MASTERCARD, id="TAR-01"),
        pytest.param("4509 9535 6623 3704", VISA, id="TAR-02"),
        pytest.param("5031-7557-3453-0604", MASTERCARD, id="TAR-03"),
    ],
)
def test_numero_valido_es_aceptado_y_normalizado(valor, esperado):
    assert validar_numero(valor) == esperado


@pytest.mark.parametrize(
    "valor",
    [
        pytest.param(None, id="TAR-04-none"),
        pytest.param("", id="TAR-04-vacio"),
        pytest.param("5031 7557 3453 06AB", id="TAR-05"),
        pytest.param("5031 7557 3453 0605", id="TAR-06"),
        # Los dos siguientes cumplen Luhn: se rechazan solo por el largo.
        pytest.param("450995356620", id="TAR-07"),
        pytest.param("45099535662337041230", id="TAR-08"),
    ],
)
def test_numero_invalido_es_rechazado(valor):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_numero(valor)
    assert error.value.campo == "numero"


@pytest.mark.parametrize(
    "numero, esperada",
    [
        pytest.param(VISA, "Visa", id="TAR-09"),
        pytest.param(MASTERCARD, "Mastercard", id="TAR-10"),
        pytest.param("371449635398431", "Tarjeta", id="TAR-11"),
    ],
)
def test_marca_se_detecta_por_el_primer_digito(numero, esperada):
    assert marca_de(numero) == esperada


@pytest.mark.parametrize(
    "valor, esperado",
    [
        pytest.param("11/30", (11, 2030), id="TAR-12"),
        pytest.param("10/26", (10, 2026), id="TAR-13"),
    ],
)
def test_vencimiento_vigente_es_aceptado(valor, esperado, ahora):
    assert validar_vencimiento(valor, ahora) == esperado


def test_vencimiento_pasado_es_rechazado_por_vencida(ahora):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_vencimiento("09/26", ahora)  # TAR-14
    assert error.value.campo == "vencimiento"
    assert "vencida" in error.value.mensaje


@pytest.mark.parametrize(
    "valor",
    [
        pytest.param("13/30", id="TAR-15-mes-13"),
        pytest.param("00/30", id="TAR-15-mes-00"),
        pytest.param("1130", id="TAR-16-sin-barra"),
        pytest.param("11/2030", id="TAR-16-anio-largo"),
        pytest.param("ab/cd", id="TAR-16-letras"),
        pytest.param("", id="TAR-16-vacio"),
        pytest.param(None, id="TAR-16-none"),
    ],
)
def test_vencimiento_con_formato_invalido_es_rechazado(valor, ahora):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_vencimiento(valor, ahora)
    assert error.value.campo == "vencimiento"
    assert "MM/AA" in error.value.mensaje


def test_codigo_de_tres_digitos_es_aceptado():
    assert validar_codigo("123") == "123"  # TAR-17


@pytest.mark.parametrize(
    "valor",
    [
        pytest.param("12", id="TAR-18-corto"),
        pytest.param("1234", id="TAR-18-largo"),
        pytest.param("abc", id="TAR-18-letras"),
        pytest.param("", id="TAR-18-vacio"),
        pytest.param(None, id="TAR-18-none"),
    ],
)
def test_codigo_invalido_es_rechazado(valor):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_codigo(valor)
    assert error.value.campo == "codigo"


@pytest.mark.parametrize(
    "valor",
    [
        pytest.param("APRO", id="TAR-19-codigo-de-prueba"),
        pytest.param("Facundo Pérez", id="TAR-19-con-acento"),
    ],
)
def test_titular_valido_es_aceptado(valor):
    assert validar_titular(valor) == valor


@pytest.mark.parametrize(
    "valor",
    [
        pytest.param("", id="TAR-20-vacio"),
        pytest.param("   ", id="TAR-20-espacios"),
        pytest.param(None, id="TAR-20-none"),
        pytest.param("Juan 3", id="TAR-21"),
    ],
)
def test_titular_invalido_es_rechazado(valor):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_titular(valor)
    assert error.value.campo == "titular"


@pytest.mark.parametrize(
    "valor",
    [
        pytest.param("12345678", id="TAR-22-ocho-digitos"),
        pytest.param("1234567", id="TAR-22-siete-digitos"),
    ],
)
def test_dni_de_siete_u_ocho_digitos_es_aceptado(valor):
    assert validar_dni(valor) == valor


@pytest.mark.parametrize(
    "valor",
    [
        pytest.param("123", id="TAR-23-corto"),
        pytest.param("abc", id="TAR-23-letras"),
        pytest.param("123456789", id="TAR-23-largo"),
        pytest.param("", id="TAR-23-vacio"),
        pytest.param(None, id="TAR-23-none"),
    ],
)
def test_dni_invalido_es_rechazado(valor):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_dni(valor)
    assert error.value.campo == "dni"


def test_tarjeta_con_varios_errores_los_informa_todos(datos_tarjeta, ahora):
    datos = {**datos_tarjeta, "numero": "123", "codigo": "", "dni": "abc"}
    with pytest.raises(ErroresDeValidacion) as error:
        validar_tarjeta(datos, ahora)  # TAR-24
    campos = {e.campo for e in error.value.errores}
    assert campos == {"numero", "codigo", "dni"}


def test_tarjeta_valida_conserva_solo_marca_ultimos_digitos_y_titular(
    datos_tarjeta, ahora
):
    tarjeta = validar_tarjeta(datos_tarjeta, ahora)  # TAR-25
    assert tarjeta == TarjetaValidada(
        marca="Mastercard", ultimos_digitos="0604", titular="APRO"
    )
    assert [campo.name for campo in fields(tarjeta)] == [
        "marca",
        "ultimos_digitos",
        "titular",
    ]
