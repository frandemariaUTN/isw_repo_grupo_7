"""Pruebas unitarias de la construccion de visitantes (EDA-09, PAS-06)."""
import pytest

from ecoharmony.dominio.errores import ErrorDeValidacion
from ecoharmony.dominio.pases import Pase
from ecoharmony.dominio.visitantes import Visitante, construir_visitantes


def test_can_09_lista_de_visitantes_vacia_es_rechazada():
    with pytest.raises(ErrorDeValidacion) as error:
        construir_visitantes([])
    assert error.value.campo == "visitantes"


def test_eda_09_el_error_identifica_al_visitante_sin_edad():
    datos = [
        {"edad": 30, "pase": "VIP"},
        {"edad": None, "pase": "COMUN"},
        {"edad": 5, "pase": "VIP"},
    ]
    with pytest.raises(ErrorDeValidacion) as error:
        construir_visitantes(datos)
    assert error.value.campo == "visitantes.2.edad"
    assert "Visitante 2" in error.value.mensaje


def test_pas_06_cada_visitante_conserva_su_propio_pase():
    datos = [
        {"edad": 30, "pase": "VIP"},
        {"edad": 10, "pase": "COMUN"},
    ]
    assert construir_visitantes(datos) == [
        Visitante(edad=30, pase=Pase.VIP),
        Visitante(edad=10, pase=Pase.COMUN),
    ]
