"""Usuario de la sesion (mockeado segun la FAQ 19)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    id: str
    email: str


def usuario_mock():
    return Usuario(id="usuario-1", email="visitante@ecoharmony.test")
