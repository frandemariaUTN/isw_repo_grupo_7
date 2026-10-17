"""Pruebas de integracion del repositorio SQLite (BD-01 a BD-15).

Los casos de contrato (BD-12) se corren contra el repositorio en memoria y
contra el SQLite: ambos deben comportarse igual.
"""
import sqlite3
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone

import pytest

from ecoharmony.dominio.compras import Compra, contar_entradas
from ecoharmony.dominio.pagos import EstadoCompra, FormaDePago
from ecoharmony.dominio.pases import Pase
from ecoharmony.dominio.repositorio import RepositorioEnMemoria
from ecoharmony.persistencia.repositorio_sqlite import RepositorioSQLite

ART = timezone(timedelta(hours=-3))
FECHA = date(2026, 10, 20)
OTRA_FECHA = date(2026, 10, 21)


def _visitantes(*datos):
    from ecoharmony.dominio.visitantes import Visitante
    return tuple(Visitante(edad=edad, pase=pase) for edad, pase in datos)


def nueva_compra(repositorio, **cambios):
    datos = {
        "numero_orden": repositorio.siguiente_numero_de_orden(),
        "usuario_id": "usuario-1",
        "email_usuario": "visitante@ecoharmony.test",
        "fecha_visita": FECHA,
        "forma_de_pago": FormaDePago.TARJETA,
        "visitantes": _visitantes((30, Pase.VIP), (10, Pase.COMUN)),
        "total": 25000,
        "estado": EstadoCompra.PENDIENTE_PAGO_ONLINE,
        "creada_en": datetime(2026, 10, 14, 10, 0, tzinfo=ART),
    }
    datos.update(cambios)
    return Compra(**datos)


@pytest.fixture
def ruta(tmp_path):
    return tmp_path / "data" / "ecoharmony.db"


@pytest.fixture
def sqlite(ruta):
    return RepositorioSQLite(ruta)


@pytest.fixture(
    params=[
        pytest.param("memoria", id="BD-12-memoria"),
        pytest.param("sqlite", id="BD-12-sqlite"),
    ]
)
def repositorio(request, ruta):
    if request.param == "memoria":
        return RepositorioEnMemoria()
    return RepositorioSQLite(ruta)


# --- Contrato comun (BD-12): memoria y SQLite ---


def test_guardar_y_recuperar_por_numero_de_orden(repositorio):
    compra = nueva_compra(repositorio)
    repositorio.guardar(compra)  # BD-02
    assert repositorio.buscar(compra.numero_orden) == compra


def test_dos_compras_no_se_pisan(repositorio):
    primera = nueva_compra(repositorio)
    segunda = nueva_compra(repositorio, usuario_id="usuario-2")
    repositorio.guardar(primera)  # BD-03
    repositorio.guardar(segunda)
    assert repositorio.buscar(primera.numero_orden) == primera
    assert repositorio.buscar(segunda.numero_orden) == segunda


def test_se_recuperan_los_visitantes_en_orden(repositorio):
    visitantes = _visitantes(
        (30, Pase.VIP), (2, Pase.COMUN), (65, Pase.COMUN), (10, Pase.VIP)
    )
    compra = nueva_compra(repositorio, visitantes=visitantes)
    repositorio.guardar(compra)  # BD-04
    assert repositorio.buscar(compra.numero_orden).visitantes == visitantes


def test_compras_de_devuelve_solo_las_del_usuario_y_la_fecha(repositorio):
    buscada = nueva_compra(repositorio)
    otra_fecha = nueva_compra(repositorio, fecha_visita=OTRA_FECHA)
    otro_usuario = nueva_compra(repositorio, usuario_id="usuario-2")
    for compra in (buscada, otra_fecha, otro_usuario):
        repositorio.guardar(compra)
    # BD-05
    assert repositorio.compras_de("usuario-1", FECHA) == [buscada]


def test_buscar_orden_inexistente_devuelve_none(repositorio):
    assert repositorio.buscar(999) is None  # BD-06


def test_repositorio_nuevo_no_tiene_compras(repositorio):
    assert repositorio.compras_de("usuario-1", FECHA) == []  # BD-09


def test_conteo_de_entradas_excluye_las_fallidas(repositorio):
    pagada = nueva_compra(repositorio, estado=EstadoCompra.PAGADA)
    fallida = nueva_compra(repositorio, estado=EstadoCompra.FALLIDA)
    repositorio.guardar(pagada)  # BD-11
    repositorio.guardar(fallida)
    compras = repositorio.compras_de("usuario-1", FECHA)
    assert contar_entradas(compras) == 2


def test_guardar_una_compra_existente_actualiza_su_estado(repositorio):
    compra = nueva_compra(repositorio)
    repositorio.guardar(compra)
    pagada = replace(compra, estado=EstadoCompra.PAGADA)
    repositorio.guardar(pagada)  # BD-07
    assert repositorio.buscar(compra.numero_orden).estado == (
        EstadoCompra.PAGADA
    )
    assert repositorio.compras_de("usuario-1", FECHA) == [pagada]


# --- Propios de SQLite ---


def test_primer_uso_crea_el_archivo_de_la_base(ruta):
    assert not ruta.exists()
    RepositorioSQLite(ruta)  # BD-01
    assert ruta.exists()


def test_cambio_de_estado_persiste_al_reabrir(sqlite, ruta):
    compra = nueva_compra(sqlite)
    sqlite.guardar(compra)
    sqlite.guardar(replace(compra, estado=EstadoCompra.PAGADA))
    reabierto = RepositorioSQLite(ruta)  # BD-07
    assert reabierto.buscar(compra.numero_orden).estado == (
        EstadoCompra.PAGADA
    )


def test_acentos_enie_y_comillas_se_guardan_sin_alterarse(sqlite, ruta):
    compra = nueva_compra(
        sqlite,
        usuario_id="Ñandú 'el \"bueno\"', José",
        email_usuario="josé.ñandú@ecoharmony.test",
    )
    sqlite.guardar(compra)  # BD-08
    reabierto = RepositorioSQLite(ruta)
    assert reabierto.buscar(compra.numero_orden) == compra


def test_reabrir_continua_la_numeracion(sqlite, ruta):
    sqlite.guardar(nueva_compra(sqlite))
    ultimo = sqlite.siguiente_numero_de_orden()
    reabierto = RepositorioSQLite(ruta)  # BD-10
    assert reabierto.siguiente_numero_de_orden() == ultimo + 1


def test_la_base_no_contiene_datos_de_tarjeta(sqlite, ruta):
    compra = nueva_compra(sqlite, estado=EstadoCompra.PAGADA)
    sqlite.guardar(compra)  # BD-13
    contenido = _volcar_base(ruta)
    for dato in ("5031755734530604", "4509953566233704", "11/30"):
        assert dato not in contenido


def test_guardado_fallido_no_deja_compra_incompleta(sqlite):
    visitante_roto = object()
    compra = nueva_compra(
        sqlite, visitantes=(*_visitantes((30, Pase.VIP)), visitante_roto)
    )
    with pytest.raises(Exception):
        sqlite.guardar(compra)  # BD-14
    assert sqlite.buscar(compra.numero_orden) is None
    assert sqlite.compras_de("usuario-1", FECHA) == []


def test_dos_conexiones_obtienen_numeros_de_orden_distintos(sqlite, ruta):
    otra_conexion = RepositorioSQLite(ruta)  # BD-15
    numeros = {
        sqlite.siguiente_numero_de_orden(),
        otra_conexion.siguiente_numero_de_orden(),
        sqlite.siguiente_numero_de_orden(),
        otra_conexion.siguiente_numero_de_orden(),
    }
    assert len(numeros) == 4


def _volcar_base(ruta):
    conexion = sqlite3.connect(ruta)
    try:
        return "\n".join(conexion.iterdump())
    finally:
        conexion.close()
