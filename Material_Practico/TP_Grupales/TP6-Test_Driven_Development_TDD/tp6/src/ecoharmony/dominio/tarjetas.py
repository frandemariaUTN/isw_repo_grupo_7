"""Validacion de la tarjeta de credito o debito de la pasarela simulada."""
import re
from dataclasses import dataclass

from ecoharmony.dominio.errores import ErrorDeValidacion, ErroresDeValidacion
from ecoharmony.dominio.reloj import hoy_local

LARGO_MINIMO = 13
LARGO_MAXIMO = 19

# Letras (con acentos) separadas por espacios, apostrofos o guiones.
_LETRAS = r"[^\W\d_]+"
_PATRON_TITULAR = re.compile(rf"{_LETRAS}(?:[ '\-]+{_LETRAS})*")
_PATRON_VENCIMIENTO = re.compile(r"(\d{2})/(\d{2})")


@dataclass(frozen=True)
class TarjetaValidada:
    marca: str
    ultimos_digitos: str
    titular: str


def validar_numero(valor):
    numero = re.sub(r"[ \-]", "", _texto(valor))
    if (
        not numero.isdigit()
        or not LARGO_MINIMO <= len(numero) <= LARGO_MAXIMO
        or not _cumple_luhn(numero)
    ):
        raise ErrorDeValidacion("numero", "Revisá el número de tarjeta.")
    return numero


def marca_de(numero):
    if numero.startswith("4"):
        return "Visa"
    if numero.startswith("5"):
        return "Mastercard"
    return "Tarjeta"


def validar_vencimiento(valor, ahora):
    coincidencia = _PATRON_VENCIMIENTO.fullmatch(_texto(valor))
    if not coincidencia or not 1 <= int(coincidencia.group(1)) <= 12:
        raise ErrorDeValidacion(
            "vencimiento", "Ingresá el vencimiento como MM/AA."
        )
    mes = int(coincidencia.group(1))
    anio = 2000 + int(coincidencia.group(2))
    hoy = hoy_local(ahora)
    if (anio, mes) < (hoy.year, hoy.month):
        raise ErrorDeValidacion("vencimiento", "La tarjeta está vencida.")
    return mes, anio


def validar_codigo(valor):
    codigo = _texto(valor)
    if not re.fullmatch(r"\d{3}", codigo):
        raise ErrorDeValidacion(
            "codigo", "Ingresá los 3 dígitos del código de seguridad."
        )
    return codigo


def validar_titular(valor):
    titular = _texto(valor)
    if not _PATRON_TITULAR.fullmatch(titular):
        raise ErrorDeValidacion(
            "titular", "Ingresá el nombre tal como figura en la tarjeta."
        )
    return titular


def validar_dni(valor):
    dni = _texto(valor)
    if not re.fullmatch(r"\d{7,8}", dni):
        raise ErrorDeValidacion("dni", "Ingresá un DNI de 7 u 8 dígitos.")
    return dni


def validar_tarjeta(datos, ahora):
    validadores = {
        "numero": validar_numero,
        "titular": validar_titular,
        "vencimiento": lambda valor: validar_vencimiento(valor, ahora),
        "codigo": validar_codigo,
        "dni": validar_dni,
    }
    validos = {}
    errores = []
    for campo, validar in validadores.items():
        try:
            validos[campo] = validar(datos.get(campo))
        except ErrorDeValidacion as error:
            errores.append(error)
    if errores:
        raise ErroresDeValidacion(errores)
    numero = validos["numero"]
    return TarjetaValidada(
        marca=marca_de(numero),
        ultimos_digitos=numero[-4:],
        titular=validos["titular"],
    )


def _texto(valor):
    return "" if valor is None else str(valor).strip()


def _cumple_luhn(numero):
    suma = 0
    for posicion, caracter in enumerate(reversed(numero)):
        digito = int(caracter)
        if posicion % 2 == 1:
            digito *= 2
            if digito > 9:
                digito -= 9
        suma += digito
    return suma % 10 == 0
