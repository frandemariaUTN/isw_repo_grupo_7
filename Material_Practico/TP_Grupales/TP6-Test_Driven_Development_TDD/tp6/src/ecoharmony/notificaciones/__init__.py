"""Adaptadores de notificacion (envio del mail de confirmacion)."""
from ecoharmony.notificaciones.notificador_simulado import NotificadorSimulado
from ecoharmony.notificaciones.notificador_smtp import (
    ConfiguracionSMTP,
    NotificadorSMTP,
)


def elegir_notificador(entorno):
    """Envio real si el .env tiene la cuenta de mail; si no, simulado."""
    configuracion = ConfiguracionSMTP.desde_entorno(entorno)
    if configuracion is None:
        return NotificadorSimulado()
    return NotificadorSMTP(configuracion)
