"""Pruebas unitarias de la validacion del tipo de pase (casos PAS)."""
import pytest

from ecoharmony.dominio.errores import ErrorDeValidacion
from ecoharmony.dominio.pases import Pase, validar_pase


@pytest.mark.parametrize(
    "valor, esperado",
    [
        pytest.param("VIP", Pase.VIP, id="PAS-01"),
        pytest.param("COMUN", Pase.COMUN, id="PAS-02"),
        pytest.param(" vip ", Pase.VIP, id="PAS-05"),
    ],
)
def test_pase_valido_es_aceptado_y_normalizado(valor, esperado):
    assert validar_pase(valor) == esperado


@pytest.mark.parametrize(
    "valor",
    [
        pytest.param(None, id="PAS-03-none"),
        pytest.param("", id="PAS-03-vacio"),
        pytest.param("PLATINO", id="PAS-04"),
    ],
)
def test_pase_invalido_es_rechazado(valor):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_pase(valor)
    assert error.value.campo == "pase"
