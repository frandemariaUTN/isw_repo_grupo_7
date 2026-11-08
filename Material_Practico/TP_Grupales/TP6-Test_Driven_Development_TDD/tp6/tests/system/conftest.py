"""Fixtures de las pruebas de sistema: app en un hilo y Edge con Playwright."""
import threading
from datetime import datetime, timedelta, timezone

import pytest
from werkzeug.serving import make_server

from ecoharmony.dominio.pasarela import PasarelaSimulada
from ecoharmony.dominio.repositorio import RepositorioEnMemoria
from ecoharmony.notificaciones.notificador_simulado import (
    NotificadorSimulado,
)
from ecoharmony.web.app import crear_app

sync_api = pytest.importorskip("playwright.sync_api")

ART = timezone(timedelta(hours=-3))
AHORA = datetime(2026, 10, 14, 10, 0, tzinfo=ART)
CELULAR = {"width": 390, "height": 844}


@pytest.fixture(scope="session")
def navegador():
    with sync_api.sync_playwright() as playwright:
        # Usa el Microsoft Edge instalado: no hace falta descargar Chromium.
        navegador = playwright.chromium.launch(channel="msedge")
        yield navegador
        navegador.close()


@pytest.fixture
def servidor():
    app = crear_app(
        repositorio=RepositorioEnMemoria(),
        pasarela=PasarelaSimulada(),
        notificador=NotificadorSimulado(),
        reloj=lambda: AHORA,
    )
    servidor = make_server("127.0.0.1", 0, app)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    yield f"http://127.0.0.1:{servidor.server_port}"
    servidor.shutdown()


@pytest.fixture
def abrir(navegador, servidor):
    contextos = []

    def _abrir(pantalla=CELULAR):
        contexto = navegador.new_context(
            base_url=servidor,
            viewport=pantalla,
            is_mobile=True,
            has_touch=True,
            reduced_motion="reduce",
        )
        contextos.append(contexto)
        pagina = contexto.new_page()
        pagina.goto("/")
        return pagina

    yield _abrir
    for contexto in contextos:
        contexto.close()


@pytest.fixture
def pagina(abrir):
    return abrir()
