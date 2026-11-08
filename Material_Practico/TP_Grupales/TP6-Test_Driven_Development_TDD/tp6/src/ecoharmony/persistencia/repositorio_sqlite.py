"""Repositorio de compras sobre SQLite (mismo contrato que el de memoria)."""
import sqlite3
from contextlib import closing, contextmanager
from datetime import date, datetime
from pathlib import Path

from ecoharmony.dominio.compras import Compra
from ecoharmony.dominio.pagos import EstadoCompra, FormaDePago
from ecoharmony.dominio.pases import Pase
from ecoharmony.dominio.visitantes import Visitante

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS secuencia (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    ultimo INTEGER NOT NULL
);
INSERT OR IGNORE INTO secuencia (id, ultimo) VALUES (1, 0);
CREATE TABLE IF NOT EXISTS compras (
    numero_orden INTEGER PRIMARY KEY,
    usuario_id TEXT NOT NULL,
    email_usuario TEXT NOT NULL,
    fecha_visita TEXT NOT NULL,
    forma_de_pago TEXT NOT NULL,
    total INTEGER NOT NULL,
    estado TEXT NOT NULL,
    creada_en TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS visitantes (
    numero_orden INTEGER NOT NULL REFERENCES compras (numero_orden),
    posicion INTEGER NOT NULL,
    edad INTEGER NOT NULL,
    pase TEXT NOT NULL,
    PRIMARY KEY (numero_orden, posicion)
);
"""


class RepositorioSQLite:
    def __init__(self, ruta):
        self._ruta = Path(ruta)
        self._ruta.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self._ruta)) as conexion:
            conexion.executescript(_ESQUEMA)

    def siguiente_numero_de_orden(self):
        with self._transaccion() as conexion:
            fila = conexion.execute(
                "UPDATE secuencia SET ultimo = ultimo + 1 RETURNING ultimo"
            ).fetchone()
        return fila[0]

    def guardar(self, compra):
        with self._transaccion() as conexion:
            conexion.execute(
                "INSERT OR REPLACE INTO compras"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    compra.numero_orden,
                    compra.usuario_id,
                    compra.email_usuario,
                    compra.fecha_visita.isoformat(),
                    compra.forma_de_pago.value,
                    compra.total,
                    compra.estado.value,
                    compra.creada_en.isoformat(),
                ),
            )
            conexion.execute(
                "DELETE FROM visitantes WHERE numero_orden = ?",
                (compra.numero_orden,),
            )
            conexion.executemany(
                "INSERT INTO visitantes VALUES (?, ?, ?, ?)",
                (
                    (compra.numero_orden, posicion, v.edad, v.pase.value)
                    for posicion, v in enumerate(compra.visitantes)
                ),
            )

    def buscar(self, numero_orden):
        with self._transaccion() as conexion:
            return _leer_compra(conexion, numero_orden)

    def compras_de(self, usuario_id, fecha):
        with self._transaccion() as conexion:
            numeros = conexion.execute(
                "SELECT numero_orden FROM compras"
                " WHERE usuario_id = ? AND fecha_visita = ?"
                " ORDER BY numero_orden",
                (usuario_id, fecha.isoformat()),
            ).fetchall()
            return [_leer_compra(conexion, numero) for (numero,) in numeros]

    @contextmanager
    def _transaccion(self):
        # Una conexion por operacion: confirma si todo sale bien y
        # deshace todo si algo falla (no quedan compras a medias).
        with closing(sqlite3.connect(self._ruta)) as conexion:
            with conexion:
                yield conexion


def _leer_compra(conexion, numero_orden):
    fila = conexion.execute(
        "SELECT * FROM compras WHERE numero_orden = ?", (numero_orden,)
    ).fetchone()
    if fila is None:
        return None
    visitantes = conexion.execute(
        "SELECT edad, pase FROM visitantes"
        " WHERE numero_orden = ? ORDER BY posicion",
        (numero_orden,),
    ).fetchall()
    numero, usuario_id, email, fecha, forma, total, estado, creada = fila
    return Compra(
        numero_orden=numero,
        usuario_id=usuario_id,
        email_usuario=email,
        fecha_visita=date.fromisoformat(fecha),
        forma_de_pago=FormaDePago(forma),
        visitantes=tuple(
            Visitante(edad=edad, pase=Pase(pase)) for edad, pase in visitantes
        ),
        total=total,
        estado=EstadoCompra(estado),
        creada_en=datetime.fromisoformat(creada),
    )
