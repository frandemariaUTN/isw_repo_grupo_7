"""Pruebas unitarias del calculo de precios (casos PRE)."""
import pytest

from ecoharmony.dominio.pases import Pase
from ecoharmony.dominio.precios import calcular_precio


def test_pre_01_pase_comun_adulto_cuesta_10000():
    assert calcular_precio(edad=30, pase=Pase.COMUN) == 10000


def test_pre_02_pase_vip_adulto_cuesta_20000():
    assert calcular_precio(edad=30, pase=Pase.VIP) == 20000


@pytest.mark.parametrize(
    "edad",
    [pytest.param(0, id="PRE-03"), pytest.param(3, id="PRE-04")],
)
def test_menores_o_iguales_a_3_anios_no_pagan_pase_comun(edad):
    assert calcular_precio(edad=edad, pase=Pase.COMUN) == 0


@pytest.mark.parametrize(
    "edad, esperado",
    [
        pytest.param(4, 5000, id="PRE-05"),
        pytest.param(15, 5000, id="PRE-06"),
        pytest.param(16, 10000, id="PRE-07"),
    ],
)
def test_menores_o_iguales_a_15_anios_pagan_mitad_pase_comun(edad, esperado):
    assert calcular_precio(edad=edad, pase=Pase.COMUN) == esperado


@pytest.mark.parametrize(
    "edad, esperado",
    [
        pytest.param(59, 10000, id="PRE-08"),
        pytest.param(60, 5000, id="PRE-09"),
        pytest.param(85, 5000, id="PRE-10"),
    ],
)
def test_mayores_o_iguales_a_60_anios_pagan_mitad_pase_comun(edad, esperado):
    assert calcular_precio(edad=edad, pase=Pase.COMUN) == esperado


@pytest.mark.parametrize(
    "edad, esperado",
    [
        pytest.param(3, 0, id="PRE-11"),
        pytest.param(10, 10000, id="PRE-12"),
        pytest.param(70, 10000, id="PRE-13"),
    ],
)
def test_descuentos_por_edad_se_aplican_sobre_pase_vip(edad, esperado):
    assert calcular_precio(edad=edad, pase=Pase.VIP) == esperado
