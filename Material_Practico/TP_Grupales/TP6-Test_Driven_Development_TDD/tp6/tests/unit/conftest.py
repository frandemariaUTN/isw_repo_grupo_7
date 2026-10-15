"""Fixtures compartidas de las pruebas unitarias."""
from datetime import date, datetime, timedelta, timezone

import pytest

ART = timezone(timedelta(hours=-3))
FECHA_DE_VISITA = date(2026, 10, 20)


@pytest.fixture
def ahora():
    return datetime(2026, 10, 14, 10, 0, tzinfo=ART)


@pytest.fixture
def usuario():
    from ecoharmony.dominio.usuarios import usuario_mock
    return usuario_mock()


@pytest.fixture
def repositorio():
    from ecoharmony.dominio.repositorio import RepositorioEnMemoria
    return RepositorioEnMemoria()


@pytest.fixture
def datos_validos():
    return {
        "fecha_visita": "2026-10-20",
        "cantidad": 2,
        "visitantes": [
            {"edad": 30, "pase": "VIP"},
            {"edad": 10, "pase": "COMUN"},
        ],
        "forma_de_pago": "efectivo",
    }


@pytest.fixture
def comprar(datos_validos, usuario, ahora, repositorio):
    from ecoharmony.dominio.compras import crear_compra

    def _comprar(**cambios):
        datos = {**datos_validos, **cambios}
        return crear_compra(datos, usuario, ahora, repositorio)

    return _comprar


@pytest.fixture
def compra_previa(repositorio, usuario, ahora):
    from ecoharmony.dominio.compras import Compra
    from ecoharmony.dominio.pagos import EstadoCompra, FormaDePago
    from ecoharmony.dominio.pases import Pase
    from ecoharmony.dominio.visitantes import Visitante

    def _crear(cantidad=1, estado=None, usuario_id=None,
               fecha=FECHA_DE_VISITA, edad=30):
        visitantes = tuple(
            Visitante(edad=edad, pase=Pase.COMUN) for _ in range(cantidad)
        )
        compra = Compra(
            numero_orden=repositorio.siguiente_numero_de_orden(),
            usuario_id=usuario_id or usuario.id,
            email_usuario="previa@ecoharmony.test",
            fecha_visita=fecha,
            forma_de_pago=FormaDePago.TARJETA,
            visitantes=visitantes,
            total=0,
            estado=estado or EstadoCompra.PAGADA,
            creada_en=ahora,
        )
        repositorio.guardar(compra)
        return compra

    return _crear
