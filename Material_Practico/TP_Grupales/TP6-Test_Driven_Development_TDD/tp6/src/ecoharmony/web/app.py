"""Aplicacion Flask de compra de entradas y pasarela simulada."""
import os
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, url_for

from ecoharmony.aplicacion.servicio_de_compra import (
    AVISO_SIN_MAIL,
    ServicioDeCompra,
)
from ecoharmony.dominio.calendario import dias_no_disponibles, sumar_un_mes
from ecoharmony.dominio.compras import mensaje_final
from ecoharmony.dominio.errores import ErrorDeValidacion, ErroresDeValidacion
from ecoharmony.dominio.formatos import formatear_fecha, formatear_monto
from ecoharmony.dominio.pagos import EstadoCompra
from ecoharmony.dominio.pasarela import (
    ErrorDePasarela,
    EstadoSesion,
    PasarelaSimulada,
)
from ecoharmony.dominio.precios import (
    EDAD_MAX_GRATIS,
    EDAD_MAX_MENOR_CON_DESCUENTO,
    EDAD_MIN_MAYOR_CON_DESCUENTO,
    PRECIO_POR_PASE,
)
from ecoharmony.dominio.reloj import ZONA_PARQUE, hoy_local
from ecoharmony.dominio.usuarios import usuario_mock
from ecoharmony.notificaciones import elegir_notificador
from ecoharmony.persistencia.repositorio_sqlite import RepositorioSQLite

RUTA_BASE_DE_DATOS = Path(__file__).parents[3] / "data" / "ecoharmony.db"

# Datos de la tarjeta que se vuelven a mostrar si hay errores.
# El numero y el codigo de seguridad nunca se devuelven a la pantalla.
CAMPOS_QUE_SE_CONSERVAN = ("titular", "vencimiento", "dni")


def crear_app(
    repositorio=None, pasarela=None, notificador=None, reloj=None,
    usuario=None,
):
    if repositorio is None:
        repositorio = RepositorioSQLite(RUTA_BASE_DE_DATOS)
    if pasarela is None:
        pasarela = PasarelaSimulada()
    if notificador is None:
        notificador = elegir_notificador(os.environ)
    if reloj is None:
        def reloj():
            return datetime.now(ZONA_PARQUE)
    if usuario is None:
        usuario = usuario_mock()
    servicio = ServicioDeCompra(repositorio, pasarela, notificador)

    app = Flask(__name__)
    app.add_template_filter(formatear_monto, "monto")

    @app.get("/")
    def inicio():
        return render_template("compra.html", usuario=usuario)

    @app.get("/api/dias-no-disponibles")
    def api_dias_no_disponibles():
        ahora = reloj()
        hoy = hoy_local(ahora)
        return jsonify(
            dias=[dia.isoformat() for dia in dias_no_disponibles(ahora)],
            desde=hoy.isoformat(),
            hasta=sumar_un_mes(hoy).isoformat(),
        )

    @app.get("/api/precios")
    def api_precios():
        return jsonify(
            precios={pase.value: p for pase, p in PRECIO_POR_PASE.items()},
            edad_max_gratis=EDAD_MAX_GRATIS,
            edad_max_menor_con_descuento=EDAD_MAX_MENOR_CON_DESCUENTO,
            edad_min_mayor_con_descuento=EDAD_MIN_MAYOR_CON_DESCUENTO,
        )

    @app.post("/api/compras")
    def api_crear_compra():
        datos = request.get_json(silent=True)
        if not isinstance(datos, dict):
            return _respuesta_de_errores([
                ErrorDeValidacion(
                    "general", "Los datos enviados no son válidos."
                )
            ])
        try:
            resultado = servicio.comprar(datos, usuario, reloj())
        except ErroresDeValidacion as error:
            return _respuesta_de_errores(error.errores)
        compra = resultado.compra
        return jsonify(
            numero_orden=compra.numero_orden,
            cantidad=compra.cantidad_de_entradas,
            fecha_visita=formatear_fecha(compra.fecha_visita),
            estado=compra.estado.value,
            total=compra.total,
            url_pago=resultado.url_pago,
            mensaje=resultado.mensaje,
            mail_enviado_a=resultado.mail_enviado_a,
            aviso_mail=resultado.aviso_mail,
        ), 201

    @app.get("/pasarela/<token>")
    def pasarela_pantalla(token):
        sesion = pasarela.buscar(token)
        if sesion is None:
            return _no_encontrado()
        if sesion.estado != EstadoSesion.ABIERTA:
            return _ir_al_resultado(sesion)
        return _pantalla_de_pago(sesion)

    @app.post("/pasarela/<token>/pagar")
    def pasarela_pagar(token):
        sesion = pasarela.buscar(token)
        if sesion is None:
            return _no_encontrado()
        try:
            pagado = servicio.pagar(token, request.form.to_dict(), reloj())
        except ErroresDeValidacion as error:
            errores = {e.campo: e.mensaje for e in error.errores}
            return _pantalla_de_pago(sesion, errores, request.form), 400
        return _ir_al_resultado(sesion, sin_mail=bool(pagado.aviso_mail))

    @app.post("/pasarela/<token>/cancelar")
    def pasarela_cancelar(token):
        sesion = pasarela.buscar(token)
        if sesion is None:
            return _no_encontrado()
        try:
            servicio.cancelar(token)
        except ErrorDePasarela:
            pass  # Ya estaba resuelta: se muestra el resultado anterior.
        return _ir_al_resultado(sesion)

    @app.get("/compras/<int:numero_orden>/resultado")
    def resultado(numero_orden):
        compra = repositorio.buscar(numero_orden)
        if compra is None or compra.usuario_id != usuario.id:
            return _no_encontrado()
        sesion = pasarela.buscar(request.args.get("token", ""))
        motivo = None
        if sesion is not None and sesion.numero_orden == numero_orden:
            motivo = sesion.motivo
        sin_mail = request.args.get("mail") == "no"
        return render_template(
            "resultado.html",
            usuario=usuario,
            **_resultado(compra, motivo, sin_mail),
        )

    def _pantalla_de_pago(sesion, errores=None, datos=None):
        compra = repositorio.buscar(sesion.numero_orden)
        conservados = {
            campo: (datos or {}).get(campo, "")
            for campo in CAMPOS_QUE_SE_CONSERVAN
        }
        return render_template(
            "pasarela.html",
            sesion=sesion,
            cantidad=compra.cantidad_de_entradas,
            errores=errores or {},
            datos=conservados,
        )

    return app


def _ir_al_resultado(sesion, sin_mail=False):
    parametros = {"mail": "no"} if sin_mail else {}
    destino = url_for(
        "resultado",
        numero_orden=sesion.numero_orden,
        token=sesion.token,
        **parametros,
    )
    return redirect(destino, 303)


def _respuesta_de_errores(errores):
    cuerpo = [{"campo": e.campo, "mensaje": e.mensaje} for e in errores]
    return jsonify(errores=cuerpo), 400


def _no_encontrado():
    return render_template("error.html"), 404


def _resultado(compra, motivo, sin_mail=False):
    if compra.estado in (
        EstadoCompra.PAGADA, EstadoCompra.PENDIENTE_BOLETERIA
    ):
        return {
            "exito": True,
            "titulo": "¡Compra confirmada!",
            "mensaje": mensaje_final(compra),
            "en_boleteria": compra.estado == EstadoCompra.PENDIENTE_BOLETERIA,
            "mail": None if sin_mail else compra.email_usuario,
            "aviso_mail": AVISO_SIN_MAIL if sin_mail else None,
        }
    if compra.estado == EstadoCompra.FALLIDA:
        # El PO pide informar el rechazo o la cancelacion con un pop-up.
        return {
            "exito": False,
            "pop_up": True,
            "titulo": "Pago rechazado" if motivo else "Compra cancelada",
            "mensaje": motivo or "El pago fue cancelado.",
        }
    return {
        "exito": False,
        "titulo": "Pago pendiente",
        "mensaje": motivo or "Tu pago está pendiente de acreditación.",
    }
