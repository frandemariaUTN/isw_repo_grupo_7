"""Pruebas unitarias del mail de confirmacion (MAI-01 a MAI-12)."""
import pytest

from ecoharmony.dominio.formatos import formatear_monto
from ecoharmony.dominio.mails import armar_mail


def test_mai_01_el_asunto_incluye_el_numero_de_orden(comprar):
    mail = armar_mail(comprar())
    assert "orden 1" in mail.asunto


def test_mai_02_el_destinatario_es_el_email_del_usuario(comprar, usuario):
    assert armar_mail(comprar()).destinatario == usuario.email


def test_mai_03_el_cuerpo_incluye_el_numero_de_orden(comprar):
    assert "Número de orden: 1" in armar_mail(comprar()).cuerpo


def test_mai_04_el_cuerpo_incluye_la_fecha_de_visita(comprar):
    assert "Fecha de visita: 20/10/2026" in armar_mail(comprar()).cuerpo


def test_mai_05_el_cuerpo_detalla_cada_visitante(comprar):
    cuerpo = armar_mail(comprar()).cuerpo
    assert "Visitante 1: 30 años, pase VIP, $20.000" in cuerpo
    assert "Visitante 2: 10 años, pase COMUN, $5.000" in cuerpo


def test_mai_06_el_cuerpo_incluye_el_total(comprar):
    assert "Total: $25.000" in armar_mail(comprar()).cuerpo


@pytest.mark.parametrize(
    "forma_de_pago, esperado",
    [("efectivo", "Efectivo"), ("tarjeta", "Tarjeta")],
)
def test_mai_07_el_cuerpo_incluye_la_forma_de_pago(
    comprar, forma_de_pago, esperado
):
    cuerpo = armar_mail(comprar(forma_de_pago=forma_de_pago)).cuerpo
    assert f"Forma de pago: {esperado}" in cuerpo


def test_mai_08_en_efectivo_el_mail_indica_pagar_en_boleteria(comprar):
    en_efectivo = armar_mail(comprar(forma_de_pago="efectivo"))
    con_tarjeta = armar_mail(comprar(forma_de_pago="tarjeta"))
    assert "boletería" in en_efectivo.cuerpo
    assert "boletería" not in con_tarjeta.cuerpo


@pytest.mark.parametrize(
    "monto, esperado",
    [
        pytest.param(0, "$0", id="MAI-09-cero"),
        pytest.param(10000, "$10.000", id="MAI-09-diez-mil"),
        pytest.param(1500000, "$1.500.000", id="MAI-09-millones"),
    ],
)
def test_mai_09_los_montos_se_formatean_con_separador_de_miles(
    monto, esperado
):
    assert formatear_monto(monto) == esperado


def test_mai_10_el_visitante_gratuito_figura_con_subtotal_cero(comprar):
    visitantes = [
        {"edad": 30, "pase": "VIP"},
        {"edad": 10, "pase": "COMUN"},
        {"edad": 2, "pase": "COMUN"},
    ]
    cuerpo = armar_mail(comprar(cantidad=3, visitantes=visitantes)).cuerpo
    assert "Visitante 3: 2 años, pase COMUN, $0" in cuerpo


def test_mai_11_el_mail_lleva_el_codigo_qr_de_la_compra(comprar):
    mail = armar_mail(comprar())
    assert mail.codigo_qr == (
        "EcoHarmony Park\n"
        "Orden N° 1 - 20/10/2026\n"
        "Total: 2 entradas\n"
        "1 VIP adulto\n"
        "1 Común menor"
    )


def test_mai_12_el_qr_detalla_las_entradas_por_pase_y_edad(comprar):
    edades_y_pases = [
        (3, "VIP"), (15, "VIP"), (16, "VIP"), (59, "VIP"), (60, "VIP"),
        (30, "COMUN"), (40, "COMUN"), (25, "COMUN"), (18, "COMUN"),
        (50, "COMUN"),
    ]
    visitantes = [{"edad": e, "pase": p} for e, p in edades_y_pases]
    compra = comprar(cantidad=10, visitantes=visitantes)
    lineas = armar_mail(compra).codigo_qr.split("\n")
    assert lineas[2:] == [
        "Total: 10 entradas",
        "2 VIP menor",
        "2 VIP adulto",
        "1 VIP adulto mayor",
        "5 Común adulto",
    ]
