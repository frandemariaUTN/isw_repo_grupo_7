"""Pruebas unitarias de la validacion de edad (casos EDA)."""
import pytest

from ecoharmony.dominio.edades import validar_edad
from ecoharmony.dominio.errores import ErrorDeValidacion


@pytest.mark.parametrize(
    "valor",
    [
        pytest.param(-1, id="EDA-01"),
        pytest.param("abc", id="EDA-02"),
        pytest.param(None, id="EDA-03-none"),
        pytest.param("", id="EDA-03-vacia"),
        pytest.param("  ", id="EDA-03-espacios"),
        pytest.param(3.5, id="EDA-04"),
        pytest.param(121, id="EDA-07"),
    ],
)
def test_edad_invalida_es_rechazada(valor):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_edad(valor)
    assert error.value.campo == "edad"


@pytest.mark.parametrize(
    "valor, esperado",
    [
        pytest.param(0, 0, id="EDA-05"),
        pytest.param("25", 25, id="EDA-06"),
        pytest.param(120, 120, id="EDA-08"),
    ],
)
def test_edad_valida_es_aceptada_y_normalizada(valor, esperado):
    assert validar_edad(valor) == esperado
