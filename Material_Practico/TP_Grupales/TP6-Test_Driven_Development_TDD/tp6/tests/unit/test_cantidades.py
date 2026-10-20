"""Pruebas unitarias de la cantidad de entradas (CAN-01 a CAN-07 y CAN-19)."""
import pytest

from ecoharmony.dominio.cantidades import validar_cantidad
from ecoharmony.dominio.errores import ErrorDeValidacion


@pytest.mark.parametrize(
    "valor",
    [
        pytest.param(0, id="CAN-01"),
        pytest.param(-3, id="CAN-02"),
        pytest.param(11, id="CAN-05"),
        pytest.param("dos", id="CAN-06"),
        pytest.param(2.5, id="CAN-07"),
        pytest.param(None, id="CAN-19-none"),
        pytest.param("", id="CAN-19-vacia"),
        pytest.param("   ", id="CAN-19-espacios"),
    ],
)
def test_cantidad_invalida_es_rechazada(valor):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_cantidad(valor)
    assert error.value.campo == "cantidad"


@pytest.mark.parametrize(
    "valor, esperado",
    [
        pytest.param(1, 1, id="CAN-03"),
        pytest.param(10, 10, id="CAN-04"),
    ],
)
def test_cantidad_valida_es_aceptada(valor, esperado):
    assert validar_cantidad(valor) == esperado
