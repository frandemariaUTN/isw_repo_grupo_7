"""Repositorio de compras en memoria (contrato que seguira el CSV)."""


class RepositorioEnMemoria:
    def __init__(self):
        self._compras = {}
        self._ultimo_numero = 0

    def siguiente_numero_de_orden(self):
        self._ultimo_numero += 1
        return self._ultimo_numero

    def guardar(self, compra):
        self._compras[compra.numero_orden] = compra

    def buscar(self, numero_orden):
        return self._compras.get(numero_orden)

    def compras_de(self, usuario_id, fecha):
        return [
            compra
            for compra in self._compras.values()
            if compra.usuario_id == usuario_id
            and compra.fecha_visita == fecha
        ]
