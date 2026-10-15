"""Pruebas unitarias del total de una compra (casos PRE-14 a PRE-16)."""
from ecoharmony.dominio.pases import Pase
from ecoharmony.dominio.precios import calcular_total
from ecoharmony.dominio.visitantes import Visitante


def test_pre_14_total_de_compra_mixta_suma_los_precios_individuales():
    visitantes = [
        Visitante(edad=30, pase=Pase.VIP),
        Visitante(edad=10, pase=Pase.COMUN),
        Visitante(edad=2, pase=Pase.COMUN),
        Visitante(edad=65, pase=Pase.VIP),
    ]
    assert calcular_total(visitantes) == 35000