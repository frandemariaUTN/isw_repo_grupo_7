"""Pruebas unitarias del calculo de precios (casos PRE)."""
from ecoharmony.dominio.pases import Pase
from ecoharmony.dominio.precios import calcular_precio


def test_pre_01_pase_comun_adulto_cuesta_10000():
    assert calcular_precio(edad=30, pase=Pase.COMUN) == 10000
