"""Pruebas unitarias de la fecha de visita (casos FEC y DIA-10)."""
from datetime import date, datetime, timedelta, timezone

import pytest

from ecoharmony.dominio.errores import ErrorDeValidacion
from ecoharmony.dominio.fechas import validar_fecha_visita
from ecoharmony.dominio.reloj import hoy_local

ART = timezone(timedelta(hours=-3))


def ahora_art(anio, mes, dia, hora=10, minuto=0):
    return datetime(anio, mes, dia, hora, minuto, tzinfo=ART)


HOY = ahora_art(2026, 10, 14)
FIN_DE_ANIO = ahora_art(2026, 12, 20)


@pytest.mark.parametrize(
    "fecha, ahora, fragmento",
    [
        pytest.param("2026-10-13", HOY, "ya pasó", id="FEC-01"),
        pytest.param(
            "2026-10-14", ahora_art(2026, 10, 14, 17, 31), "17:30",
            id="FEC-04",
        ),
        pytest.param(
            "2026-10-14", ahora_art(2026, 10, 14, 19, 0), "17:30",
            id="FEC-05",
        ),
        pytest.param("2026-11-15", HOY, "un mes", id="FEC-09"),
        pytest.param(
            "2026-10-19", ahora_art(2026, 10, 19), "cerrado",
            id="FEC-10",
        ),
        pytest.param("2026-10-26", HOY, "cerrado", id="DIA-10"),
        pytest.param(None, HOY, "obligatoria", id="FEC-11-none"),
        pytest.param("", HOY, "obligatoria", id="FEC-11-vacia"),
        pytest.param("31/02/2026", HOY, "formato", id="FEC-12-invalida"),
        pytest.param("mañana", HOY, "formato", id="FEC-12-texto"),
        pytest.param("2027-01-01", FIN_DE_ANIO, "cerrado", id="FEC-15"),
    ],
)
def test_fecha_no_permitida_es_rechazada(fecha, ahora, fragmento):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_fecha_visita(fecha, ahora)
    assert error.value.campo == "fecha_visita"
    assert fragmento in error.value.mensaje


@pytest.mark.parametrize(
    "fecha, ahora",
    [
        pytest.param(date(2026, 10, 14), HOY, id="FEC-02"),
        pytest.param(
            date(2026, 10, 14), ahora_art(2026, 10, 14, 17, 30),
            id="FEC-03",
        ),
        pytest.param(
            date(2026, 10, 14), ahora_art(2026, 10, 14, 8, 0),
            id="FEC-06",
        ),
        pytest.param(
            date(2026, 10, 15), ahora_art(2026, 10, 14, 18, 0),
            id="FEC-07",
        ),
        pytest.param(date(2026, 11, 14), HOY, id="FEC-08"),
        pytest.param(
            date(2027, 2, 28), ahora_art(2027, 1, 31), id="FEC-13"
        ),
        pytest.param(date(2027, 1, 2), FIN_DE_ANIO, id="FEC-14"),
    ],
)
def test_fecha_permitida_es_aceptada(fecha, ahora):
    assert validar_fecha_visita(fecha, ahora) == fecha


def test_fec_16_hoy_se_calcula_en_hora_argentina():
    instante_utc = datetime(2026, 10, 15, 2, 30, tzinfo=timezone.utc)
    assert hoy_local(instante_utc) == date(2026, 10, 14)


def test_fec_17_un_instante_sin_zona_horaria_es_rechazado():
    with pytest.raises(ValueError):
        hoy_local(datetime(2026, 10, 14, 10, 0))
