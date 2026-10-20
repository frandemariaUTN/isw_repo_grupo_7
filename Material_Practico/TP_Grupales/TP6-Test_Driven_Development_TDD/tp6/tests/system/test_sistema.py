"""Pruebas de sistema en el navegador (SIS-01 a SIS-08)."""
import re

import pytest

expect = pytest.importorskip("playwright.sync_api").expect

FECHA = "2026-10-20"


def elegir_fecha(pagina, fecha=FECHA):
    pagina.click(f'[data-fecha="{fecha}"]')


def cargar_edades(pagina, *edades):
    for _ in edades[1:]:
        pagina.click("#mas")
    campos = pagina.locator("#visitantes input")
    for indice, edad in enumerate(edades):
        campos.nth(indice).fill(str(edad))


def elegir_forma(pagina, forma):
    pagina.click(f'[data-forma="{forma}"]')


def pagar_con_tarjeta(pagina, titular):
    expect(pagina).to_have_url(re.compile(r"/pasarela/"))
    pagina.fill("#numero", "4509 9535 6623 3704")
    pagina.fill("#titular", titular)
    pagina.fill("#vencimiento", "11/30")
    pagina.fill("#codigo", "123")
    pagina.fill("#dni", "12345678")
    pagina.click("#pagar")


def test_sis_01_compra_con_tarjeta_aprobada(pagina):
    elegir_fecha(pagina)
    cargar_edades(pagina, 30, 10)
    elegir_forma(pagina, "tarjeta")
    pagina.click("#confirmar")
    pagar_con_tarjeta(pagina, "APRO")
    expect(pagina.get_by_text(
        "Compraste 2 entradas para el 20/10/2026."
    )).to_be_visible()
    expect(pagina.locator("#modal-mail")).to_contain_text(
        "jsbarbera4@gmail.com"
    )


def test_sis_02_sin_forma_de_pago_muestra_error_junto_al_campo(pagina):
    elegir_fecha(pagina)
    cargar_edades(pagina, 30)
    pagina.click("#confirmar")
    expect(pagina.locator('[data-error="forma_de_pago"]')).to_have_text(
        "Debe seleccionar la forma de pago."
    )
    expect(pagina).not_to_have_url(re.compile(r"/pasarela/"))


def test_sis_03_los_lunes_no_se_pueden_elegir(pagina):
    expect(pagina.locator('[data-fecha="2026-10-19"]')).to_be_disabled()
    expect(pagina.locator('[data-fecha="2026-10-26"]')).to_be_disabled()


def test_sis_04_no_se_pueden_cargar_mas_de_10_entradas(pagina):
    for _ in range(9):
        pagina.click("#mas")
    expect(pagina.locator("#cantidad-valor")).to_have_text("10")
    expect(pagina.locator("#mas")).to_be_disabled()
    expect(pagina.locator("#aviso-maximo")).to_be_visible()
    expect(pagina.locator("#visitantes .visitante")).to_have_count(10)


def test_sis_05_compra_en_efectivo(pagina):
    elegir_fecha(pagina)
    cargar_edades(pagina, 30)
    elegir_forma(pagina, "efectivo")
    pagina.click("#confirmar")
    expect(pagina.locator("#exito-mensaje")).to_have_text(
        "Compraste 1 entrada para el 20/10/2026."
    )
    expect(pagina.locator("#exito-boleteria")).to_be_visible()
    expect(pagina.locator("#modal-mail")).to_be_visible()


def test_sis_06_pago_rechazado_muestra_el_motivo_en_un_pop_up(pagina):
    elegir_fecha(pagina)
    cargar_edades(pagina, 30)
    elegir_forma(pagina, "tarjeta")
    pagina.click("#confirmar")
    pagar_con_tarjeta(pagina, "OTHE")
    expect(pagina.locator("#modal-pago")).to_be_visible()
    expect(pagina.locator("#modal-pago")).to_contain_text(
        "El pago fue rechazado."
    )


def test_sis_07_los_subtotales_muestran_el_descuento_por_edad(pagina):
    cargar_edades(pagina, 2, 10, 65)
    subtotales = pagina.locator("#visitantes [data-subtotal]")
    expect(subtotales).to_have_text(["$0", "$5.000", "$5.000"])
    expect(pagina.locator("#total")).to_have_text("$10.000")


def test_sis_08_en_un_celular_chico_no_hay_scroll_horizontal(abrir):
    pagina = abrir({"width": 375, "height": 667})
    expect(pagina.locator('[data-fecha="2026-10-20"]')).to_be_visible()
    ancho = pagina.evaluate("document.documentElement.scrollWidth")
    assert ancho <= 375
    for boton in ("#mas", "#confirmar", '[data-forma="tarjeta"]'):
        assert pagina.locator(boton).bounding_box()["height"] >= 44
