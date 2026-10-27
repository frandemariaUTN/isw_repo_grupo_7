"""Pruebas de la API web con Flask (API-01 a API-24)."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from ecoharmony.dominio.errores import ErrorDeNotificacion
from ecoharmony.dominio.pagos import EstadoCompra
from ecoharmony.dominio.pasarela import EstadoSesion, PasarelaSimulada
from ecoharmony.dominio.repositorio import RepositorioEnMemoria
from ecoharmony.dominio.usuarios import usuario_mock
from ecoharmony.notificaciones.notificador_simulado import (
    NotificadorSimulado,
)
from ecoharmony.web.app import crear_app

ART = timezone(timedelta(hours=-3))
AHORA = datetime(2026, 10, 14, 10, 0, tzinfo=ART)


def datos_compra(forma="tarjeta", **cambios):
    datos = {
        "fecha_visita": "2026-10-20",
        "cantidad": 2,
        "visitantes": [
            {"edad": 30, "pase": "COMUN"},
            {"edad": 10, "pase": "COMUN"},
        ],
        "forma_de_pago": forma,
    }
    datos.update(cambios)
    return datos


def tarjeta(titular="APRO", **cambios):
    datos = {
        "numero": "4509 9535 6623 3704",
        "titular": titular,
        "vencimiento": "11/30",
        "codigo": "123",
        "dni": "12345678",
    }
    datos.update(cambios)
    return datos


@pytest.fixture
def repositorio():
    return RepositorioEnMemoria()


@pytest.fixture
def pasarela():
    return PasarelaSimulada()


@pytest.fixture
def notificador():
    return NotificadorSimulado()


@pytest.fixture
def cliente(repositorio, pasarela, notificador):
    app = crear_app(
        repositorio=repositorio,
        pasarela=pasarela,
        notificador=notificador,
        reloj=lambda: AHORA,
    )
    return app.test_client()


@pytest.fixture
def token(cliente):
    respuesta = cliente.post("/api/compras", json=datos_compra())
    return respuesta.get_json()["url_pago"].rsplit("/", 1)[-1]


def errores(respuesta):
    return {error["campo"] for error in respuesta.get_json()["errores"]}


def test_api_01_inicio_muestra_el_formulario_de_compra(cliente):
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert "Comprar entradas" in respuesta.get_data(as_text=True)


def test_api_02_dias_no_disponibles_y_rango_de_compra(cliente):
    datos = cliente.get("/api/dias-no-disponibles").get_json()
    assert datos["dias"] == [
        "2026-10-19", "2026-10-26", "2026-11-02", "2026-11-09",
    ]
    assert (datos["desde"], datos["hasta"]) == ("2026-10-14", "2026-11-14")


def test_api_03_precios_y_reglas_de_descuento(cliente):
    datos = cliente.get("/api/precios").get_json()
    assert datos["precios"] == {"COMUN": 10000, "VIP": 20000}
    assert datos["edad_max_gratis"] == 3
    assert datos["edad_max_menor_con_descuento"] == 15
    assert datos["edad_min_mayor_con_descuento"] == 60


def test_api_04_compra_en_efectivo(cliente):
    respuesta = cliente.post("/api/compras", json=datos_compra("efectivo"))
    datos = respuesta.get_json()
    assert respuesta.status_code == 201
    assert (datos["numero_orden"], datos["cantidad"]) == (1, 2)
    assert datos["fecha_visita"] == "20/10/2026"
    assert datos["mensaje"] == "Compraste 2 entradas para el 20/10/2026."
    assert datos["mail_enviado_a"] == "danogamer987654321@gmail.com"


def test_api_05_compra_con_tarjeta_devuelve_url_de_la_pasarela(cliente):
    respuesta = cliente.post("/api/compras", json=datos_compra())
    assert respuesta.status_code == 201
    assert respuesta.get_json()["url_pago"].startswith("/pasarela/")


@pytest.mark.parametrize(
    "cambios, campo",
    [
        pytest.param(
            {"forma_de_pago": ""}, "forma_de_pago", id="API-06"
        ),
        pytest.param(
            {"fecha_visita": "2026-10-19"}, "fecha_visita", id="API-07"
        ),
        pytest.param(
            {
                "cantidad": 11,
                "visitantes": [{"edad": 30, "pase": "COMUN"}] * 11,
            },
            "cantidad",
            id="API-08",
        ),
        pytest.param(
            {
                "visitantes": [
                    {"edad": 30, "pase": "COMUN"},
                    {"pase": "COMUN"},
                ]
            },
            "visitantes.2.edad",
            id="API-09",
        ),
    ],
)
def test_compra_invalida_devuelve_400_con_el_campo(cliente, cambios, campo):
    respuesta = cliente.post("/api/compras", json=datos_compra(**cambios))
    assert respuesta.status_code == 400
    assert campo in errores(respuesta)


def test_api_10_json_invalido_devuelve_400(cliente):
    respuesta = cliente.post(
        "/api/compras", data="{no es json", content_type="application/json"
    )
    assert respuesta.status_code == 400
    assert respuesta.get_json()["errores"]


def test_api_11_los_errores_tienen_formato_consistente(cliente):
    datos = datos_compra(forma_de_pago="", fecha_visita="2026-10-19")
    respuesta = cliente.post("/api/compras", json=datos)
    for error in respuesta.get_json()["errores"]:
        assert set(error) == {"campo", "mensaje"}


def test_api_12_la_pasarela_muestra_resumen_y_formulario(cliente, token):
    html = cliente.get(f"/pasarela/{token}").get_data(as_text=True)
    assert "2 entradas" in html
    assert "$15.000" in html
    assert 'name="numero"' in html


def test_api_13_pasarela_con_token_inexistente_devuelve_404(cliente):
    assert cliente.get("/pasarela/no-existe").status_code == 404


def test_api_14_pago_aprobado_redirige_al_resultado(
    cliente, token, repositorio
):
    respuesta = cliente.post(f"/pasarela/{token}/pagar", data=tarjeta())
    assert respuesta.status_code in (302, 303)
    assert respuesta.location.startswith("/compras/1/resultado")
    assert repositorio.buscar(1).estado == EstadoCompra.PAGADA


def test_api_15_tarjeta_invalida_muestra_errores_y_sigue_abierta(
    cliente, token, pasarela
):
    respuesta = cliente.post(
        f"/pasarela/{token}/pagar", data=tarjeta(codigo="12")
    )
    assert respuesta.status_code == 400
    assert "código de seguridad" in respuesta.get_data(as_text=True)
    assert pasarela.buscar(token).estado == EstadoSesion.ABIERTA


def test_api_16_pago_rechazado_redirige_y_deja_la_compra_fallida(
    cliente, token, repositorio
):
    respuesta = cliente.post(
        f"/pasarela/{token}/pagar", data=tarjeta("OTHE")
    )
    assert respuesta.location.startswith("/compras/1/resultado")
    assert repositorio.buscar(1).estado == EstadoCompra.FALLIDA


def test_api_17_cancelar_vuelve_a_la_app_con_aviso_y_compra_fallida(
    cliente, token, repositorio
):
    respuesta = cliente.post(f"/pasarela/{token}/cancelar")
    assert respuesta.location.startswith("/compras/1/resultado")
    assert repositorio.buscar(1).estado == EstadoCompra.FALLIDA
    html = cliente.get(respuesta.location).get_data(as_text=True)
    assert 'id="modal-pago"' in html
    assert "El pago fue cancelado." in html


def test_api_18_pagar_una_sesion_cerrada_no_reprocesa(
    cliente, token, repositorio, notificador
):
    cliente.post(f"/pasarela/{token}/pagar", data=tarjeta())
    respuesta = cliente.post(
        f"/pasarela/{token}/pagar", data=tarjeta("OTHE")
    )
    assert respuesta.location.startswith("/compras/1/resultado")
    assert repositorio.buscar(1).estado == EstadoCompra.PAGADA
    assert len(notificador.enviados) == 1


def test_api_19_resultado_aprobado_informa_cantidad_fecha_y_mail(
    cliente, token
):
    respuesta = cliente.post(
        f"/pasarela/{token}/pagar", data=tarjeta(), follow_redirects=True
    )
    html = respuesta.get_data(as_text=True)
    assert "Compraste 2 entradas para el 20/10/2026." in html
    assert (
        "Te enviamos la confirmación con tu QR a "
        "danogamer987654321@gmail.com"
    ) in html
    assert 'id="modal-mail"' not in html


@pytest.mark.parametrize(
    "titular, mensaje, con_pop_up",
    [
        pytest.param(
            "OTHE", "El pago fue rechazado.", True, id="API-20-rechazo"
        ),
        pytest.param(
            "CONT", "Tu pago está pendiente de acreditación.", False,
            id="API-20-pendiente",
        ),
    ],
)
def test_resultado_rechazado_o_pendiente_informa_el_motivo(
    cliente, token, titular, mensaje, con_pop_up
):
    respuesta = cliente.post(
        f"/pasarela/{token}/pagar",
        data=tarjeta(titular),
        follow_redirects=True,
    )
    html = respuesta.get_data(as_text=True)
    assert mensaje in html
    assert ('id="modal-pago"' in html) == con_pop_up


def test_api_21_resultado_de_otro_usuario_o_inexistente_devuelve_404(
    cliente, token, repositorio
):
    ajena = replace(repositorio.buscar(1), usuario_id="otro-usuario")
    repositorio.guardar(ajena)
    assert cliente.get("/compras/1/resultado").status_code == 404
    assert cliente.get("/compras/999/resultado").status_code == 404


def test_api_22_la_compra_queda_a_nombre_del_usuario_mockeado(
    cliente, repositorio
):
    cliente.post("/api/compras", json=datos_compra("efectivo"))
    assert repositorio.buscar(1).usuario_id == usuario_mock().id


class NotificadorQueFalla:
    def enviar(self, mail):
        raise ErrorDeNotificacion("sin conexion")


@pytest.fixture
def cliente_sin_mail(repositorio, pasarela):
    app = crear_app(
        repositorio=repositorio,
        pasarela=pasarela,
        notificador=NotificadorQueFalla(),
        reloj=lambda: AHORA,
    )
    return app.test_client()


def test_api_23_compra_en_efectivo_con_mail_fallido_devuelve_aviso(
    cliente_sin_mail,
):
    respuesta = cliente_sin_mail.post(
        "/api/compras", json=datos_compra("efectivo")
    )
    datos = respuesta.get_json()
    assert respuesta.status_code == 201
    assert datos["mail_enviado_a"] is None
    assert datos["aviso_mail"].startswith("No pudimos enviar el mail")


def test_api_24_pago_aprobado_con_mail_fallido_muestra_aviso(
    cliente_sin_mail,
):
    respuesta = cliente_sin_mail.post("/api/compras", json=datos_compra())
    token = respuesta.get_json()["url_pago"].rsplit("/", 1)[-1]
    html = cliente_sin_mail.post(
        f"/pasarela/{token}/pagar", data=tarjeta(), follow_redirects=True
    ).get_data(as_text=True)
    assert "Compraste 2 entradas para el 20/10/2026." in html
    assert "No pudimos enviar el mail de confirmación." in html
