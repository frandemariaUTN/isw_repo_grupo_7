"""Pruebas unitarias de forma de pago y estados (PAG-01 a PAG-12)."""
import pytest

from ecoharmony.dominio.errores import ErrorDeValidacion
from ecoharmony.dominio.pagos import (
    EstadoCompra,
    FormaDePago,
    ResultadoDePago,
    aplicar_resultado_de_pago,
    validar_forma_de_pago,
)


@pytest.mark.parametrize(
    "valor",
    [
        pytest.param(None, id="PAG-01-none"),
        pytest.param("", id="PAG-01-vacia"),
        pytest.param("cheque", id="PAG-04"),
    ],
)
def test_forma_de_pago_invalida_es_rechazada(valor):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_forma_de_pago(valor)
    assert error.value.campo == "forma_de_pago"


@pytest.mark.parametrize(
    "valor, esperado",
    [
        pytest.param("efectivo", FormaDePago.EFECTIVO, id="PAG-02"),
        pytest.param("tarjeta", FormaDePago.TARJETA, id="PAG-03"),
        pytest.param(" Tarjeta ", FormaDePago.TARJETA, id="PAG-05"),
    ],
)
def test_forma_de_pago_valida_es_aceptada_y_normalizada(valor, esperado):
    assert validar_forma_de_pago(valor) == esperado


@pytest.mark.parametrize(
    "estado, resultado, esperado",
    [
        pytest.param(
            EstadoCompra.PENDIENTE_PAGO_ONLINE,
            ResultadoDePago.APROBADO,
            EstadoCompra.PAGADA,
            id="PAG-08",
        ),
        pytest.param(
            EstadoCompra.PENDIENTE_PAGO_ONLINE,
            ResultadoDePago.RECHAZADO,
            EstadoCompra.FALLIDA,
            id="PAG-09",
        ),
        pytest.param(
            EstadoCompra.PENDIENTE_PAGO_ONLINE,
            ResultadoDePago.PENDIENTE,
            EstadoCompra.PENDIENTE_PAGO_ONLINE,
            id="PAG-10",
        ),
        pytest.param(
            EstadoCompra.PAGADA,
            ResultadoDePago.RECHAZADO,
            EstadoCompra.PAGADA,
            id="PAG-11",
        ),
        pytest.param(
            EstadoCompra.FALLIDA,
            ResultadoDePago.APROBADO,
            EstadoCompra.FALLIDA,
            id="PAG-12",
        ),
    ],
)
def test_resultado_de_pago_actualiza_el_estado(estado, resultado, esperado):
    assert aplicar_resultado_de_pago(estado, resultado) == esperado
