"""Pruebas unitarias de la creacion de compras.

Casos: ORD-01 a ORD-09, USR-02, USR-03, PAG-06, PAG-07, PAG-13,
CAN-08, CAN-10 a CAN-18.
"""
from datetime import date

import pytest

from ecoharmony.dominio.compras import (
    contar_entradas,
    crear_compra,
    mensaje_final,
)
from ecoharmony.dominio.errores import ErrorDeValidacion, ErroresDeValidacion
from ecoharmony.dominio.pagos import EstadoCompra, FormaDePago
from ecoharmony.dominio.pases import Pase
from ecoharmony.dominio.visitantes import Visitante


def visitantes_de(cantidad, edad=30):
    return [{"edad": edad, "pase": "COMUN"} for _ in range(cantidad)]


def campos_con_error(error):
    return {e.campo for e in error.value.errores}


def mensajes_de_error(error):
    return [e.mensaje for e in error.value.errores]


# ---- ORD: orden de compra -------------------------------------------

def test_ord_01_dos_compras_consecutivas_tienen_numeros_distintos(comprar):
    primera = comprar()
    segunda = comprar()
    assert primera.numero_orden != segunda.numero_orden


def test_ord_02_la_orden_guarda_los_datos_de_la_compra(comprar, usuario):
    compra = comprar()
    assert compra.usuario_id == usuario.id
    assert compra.fecha_visita == date(2026, 10, 20)
    assert compra.forma_de_pago == FormaDePago.EFECTIVO
    assert compra.visitantes == (
        Visitante(edad=30, pase=Pase.VIP),
        Visitante(edad=10, pase=Pase.COMUN),
    )
    assert compra.total == 25000


def test_ord_03_el_total_es_la_suma_de_los_subtotales(comprar):
    visitantes = [
        {"edad": 30, "pase": "COMUN"},
        {"edad": 65, "pase": "VIP"},
        {"edad": 2, "pase": "COMUN"},
    ]
    compra = comprar(cantidad=3, visitantes=visitantes)
    assert compra.total == 10000 + 10000 + 0


def test_ord_04_la_fecha_de_creacion_sale_del_reloj_inyectado(
    comprar, ahora
):
    assert comprar().creada_en == ahora


def test_ord_05_el_mensaje_final_informa_cantidad_y_fecha(comprar):
    compra = comprar(cantidad=3, visitantes=visitantes_de(3))
    assert mensaje_final(compra) == (
        "Compraste 3 entradas para el 20/10/2026."
    )


def test_ord_06_el_mensaje_final_usa_singular_con_una_entrada(comprar):
    compra = comprar(cantidad=1, visitantes=visitantes_de(1))
    assert mensaje_final(compra) == "Compraste 1 entrada para el 20/10/2026."


def test_ord_07_la_fecha_del_mensaje_final_es_dd_mm_aaaa(comprar):
    compra = comprar(fecha_visita="2026-11-05")
    assert "05/11/2026" in mensaje_final(compra)


def test_ord_08_si_falla_una_validacion_no_se_crea_ni_consume_orden(
    datos_validos, usuario, ahora, repositorio
):
    datos = {**datos_validos, "forma_de_pago": None}
    with pytest.raises(ErroresDeValidacion):
        crear_compra(datos, usuario, ahora, repositorio)
    assert repositorio.buscar(1) is None
    assert repositorio.siguiente_numero_de_orden() == 1


def test_ord_09_los_errores_se_informan_todos_juntos(
    datos_validos, usuario, ahora, repositorio
):
    datos = {**datos_validos, "fecha_visita": "2026-10-19", "cantidad": 11}
    with pytest.raises(ErroresDeValidacion) as error:
        crear_compra(datos, usuario, ahora, repositorio)
    assert campos_con_error(error) == {"fecha_visita", "cantidad"}


# ---- USR: usuario de sesion -----------------------------------------

def test_usr_02_la_compra_queda_asociada_al_usuario_de_la_sesion(
    comprar, usuario
):
    compra = comprar()
    assert compra.usuario_id == usuario.id
    assert compra.email_usuario == usuario.email


def test_usr_03_sin_sesion_la_compra_es_rechazada(
    datos_validos, ahora, repositorio
):
    with pytest.raises(ErrorDeValidacion) as error:
        crear_compra(datos_validos, None, ahora, repositorio)
    assert error.value.campo == "usuario"


# ---- PAG: estado inicial segun la forma de pago -----------------------

def test_pag_06_compra_en_efectivo_queda_pendiente_en_boleteria(comprar):
    compra = comprar(forma_de_pago="efectivo")
    assert compra.estado == EstadoCompra.PENDIENTE_BOLETERIA


def test_pag_07_compra_con_tarjeta_queda_pendiente_de_pago_online(comprar):
    compra = comprar(forma_de_pago="tarjeta")
    assert compra.estado == EstadoCompra.PENDIENTE_PAGO_ONLINE


def test_pag_13_tarjeta_con_total_cero_queda_pendiente_de_pago(comprar):
    compra = comprar(
        forma_de_pago="tarjeta",
        cantidad=2,
        visitantes=visitantes_de(2, edad=2),
    )
    assert compra.total == 0
    assert compra.estado == EstadoCompra.PENDIENTE_PAGO_ONLINE


# ---- CAN: cantidad y limite de 10 entradas por fecha ------------------

def test_can_08_la_cantidad_debe_coincidir_con_los_visitantes(comprar):
    with pytest.raises(ErroresDeValidacion) as error:
        comprar(cantidad=3)
    assert campos_con_error(error) == {"cantidad"}


def test_can_10_seis_previas_y_cuatro_nuevas_llegan_al_limite(
    comprar, compra_previa
):
    compra_previa(cantidad=6)
    compra = comprar(cantidad=4, visitantes=visitantes_de(4))
    assert compra.cantidad_de_entradas == 4


def test_can_11_seis_previas_y_cinco_nuevas_superan_el_limite(
    comprar, compra_previa
):
    compra_previa(cantidad=6)
    with pytest.raises(ErroresDeValidacion) as error:
        comprar(cantidad=5, visitantes=visitantes_de(5))
    assert campos_con_error(error) == {"cantidad"}


def test_can_12_con_diez_previas_no_se_puede_comprar_ninguna_mas(
    comprar, compra_previa
):
    compra_previa(cantidad=10)
    with pytest.raises(ErroresDeValidacion):
        comprar(cantidad=1, visitantes=visitantes_de(1))


def test_can_13_las_previas_de_otra_fecha_no_cuentan(
    comprar, compra_previa
):
    compra_previa(cantidad=10, fecha=date(2026, 10, 21))
    assert comprar().cantidad_de_entradas == 2


def test_can_14_las_previas_de_otro_usuario_no_cuentan(
    comprar, compra_previa
):
    compra_previa(cantidad=10, usuario_id="otro-usuario")
    assert comprar().cantidad_de_entradas == 2


def test_can_15_las_entradas_gratuitas_cuentan_para_el_limite(
    compra_previa
):
    compras = [
        compra_previa(cantidad=2, edad=2),
        compra_previa(cantidad=1, edad=30),
    ]
    assert contar_entradas(compras) == 3


def test_can_16_las_compras_fallidas_no_cuentan_para_el_limite(
    compra_previa
):
    compras = [
        compra_previa(cantidad=2, estado=EstadoCompra.PAGADA),
        compra_previa(cantidad=5, estado=EstadoCompra.FALLIDA),
    ]
    assert contar_entradas(compras) == 2


def test_can_17_las_compras_pendientes_cuentan_para_el_limite(
    compra_previa
):
    compras = [
        compra_previa(cantidad=3, estado=EstadoCompra.PENDIENTE_BOLETERIA),
        compra_previa(cantidad=2, estado=EstadoCompra.PENDIENTE_PAGO_ONLINE),
    ]
    assert contar_entradas(compras) == 5


def test_can_18_el_error_informa_cuantas_entradas_quedan(
    comprar, compra_previa
):
    compra_previa(cantidad=7)
    with pytest.raises(ErroresDeValidacion) as error:
        comprar(cantidad=5, visitantes=visitantes_de(5))
    assert any("Podés comprar 3 más" in m for m in mensajes_de_error(error))
