"""Formato de montos y fechas para mostrar al visitante."""


def formatear_monto(monto):
    return "$" + f"{monto:,}".replace(",", ".")


def formatear_fecha(fecha):
    return fecha.strftime("%d/%m/%Y")
