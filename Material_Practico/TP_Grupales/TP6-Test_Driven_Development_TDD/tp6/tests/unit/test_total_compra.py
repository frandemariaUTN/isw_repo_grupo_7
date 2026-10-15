"""Pruebas unitarias del total de una compra (casos PRE-14 a PRE-16)."""
from ecoharmony.dominio.pases import Pase
from ecoharmony.dominio.precios import calcular_precio, calcular_total
from ecoharmony.dominio.visitantes import Visitante


def test_pre_14_total_de_compra_mixta_suma_los_precios_individuales():
    visitantes = [
        Visitante(edad=30, pase=Pase.VIP),
        Visitante(edad=10, pase=Pase.COMUN),
        Visitante(edad=2, pase=Pase.COMUN),
        Visitante(edad=65, pase=Pase.VIP),
    ]
    assert calcular_total(visitantes) == 35000
    
    

def test_pre_15_total_es_cero_si_todos_los_visitantes_son_menores_de_3():
    visitantes = [
        Visitante(edad=0, pase=Pase.COMUN),
        Visitante(edad=2, pase=Pase.VIP),
        Visitante(edad=3, pase=Pase.COMUN),
    ]
    assert calcular_total(visitantes) == 0
    
    

PRECIOS_PRUEBA = {Pase.COMUN: 10000, Pase.VIP: 25000}


def test_pre_16_calcular_precio_usa_la_tabla_de_precios_recibida():
    precio = calcular_precio(edad=30, pase=Pase.VIP, precios=PRECIOS_PRUEBA)
    assert precio == 25000


def test_pre_16_calcular_total_usa_la_tabla_de_precios_recibida():
    visitantes = [
        Visitante(edad=30, pase=Pase.VIP),
        Visitante(edad=10, pase=Pase.VIP),
    ]
    assert calcular_total(visitantes, precios=PRECIOS_PRUEBA) == 37500