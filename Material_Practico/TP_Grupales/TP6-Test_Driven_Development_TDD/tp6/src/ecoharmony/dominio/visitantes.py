"""Visitante de una compra de entradas."""
from dataclasses import dataclass

from ecoharmony.dominio.pases import Pase


@dataclass(frozen=True)
class Visitante:
    edad: int
    pase: Pase