"""Pruebas unitarias del calendario del parque (casos DIA)."""
from datetime import date, datetime, timedelta, timezone

import pytest

from ecoharmony.dominio.calendario import dias_no_disponibles, parque_abierto

ART = timezone(timedelta(hours=-3))


def ahora_art(anio, mes, dia, hora=10, minuto=0):
    return datetime(anio, mes, dia, hora, minuto, tzinfo=ART)


HOY = ahora_art(2026, 10, 14)


@pytest.mark.parametrize(
    "fecha",
    [
        pytest.param(date(2026, 10, 20), id="DIA-01-martes"),
        pytest.param(date(2026, 10, 21), id="DIA-01-miercoles"),
        pytest.param(date(2026, 10, 22), id="DIA-01-jueves"),
        pytest.param(date(2026, 10, 23), id="DIA-01-viernes"),
        pytest.param(date(2026, 10, 24), id="DIA-01-sabado"),
        pytest.param(date(2026, 10, 25), id="DIA-01-domingo"),
        pytest.param(date(2026, 12, 24), id="DIA-05"),
        pytest.param(date(2026, 12, 31), id="DIA-06"),
        pytest.param(date(2027, 1, 2), id="DIA-07"),
    ],
)
def test_parque_abre_los_dias_habituales(fecha):
    assert parque_abierto(fecha) is True


@pytest.mark.parametrize(
    "fecha",
    [
        pytest.param(date(2026, 10, 19), id="DIA-02-lunes"),
        pytest.param(date(2026, 12, 25), id="DIA-03-navidad"),
        pytest.param(date(2027, 1, 1), id="DIA-04-anio-nuevo"),
    ],
)
def test_parque_cierra_lunes_y_feriados(fecha):
    assert parque_abierto(fecha) is False


def test_dia_08_dias_no_disponibles_del_rango_son_los_lunes():
    assert dias_no_disponibles(HOY) == [
        date(2026, 10, 19),
        date(2026, 10, 26),
        date(2026, 11, 2),
        date(2026, 11, 9),
    ]


def test_dia_09_dias_no_disponibles_incluyen_los_feriados_del_rango():
    ahora = ahora_art(2026, 12, 20)
    assert dias_no_disponibles(ahora) == [
        date(2026, 12, 21),
        date(2026, 12, 25),
        date(2026, 12, 28),
        date(2027, 1, 1),
        date(2027, 1, 4),
        date(2027, 1, 11),
        date(2027, 1, 18),
    ]


def test_dia_11_hoy_no_esta_disponible_pasadas_las_1730():
    ahora = ahora_art(2026, 10, 14, hora=17, minuto=45)
    assert dias_no_disponibles(ahora)[0] == date(2026, 10, 14)
