"""Pruebas unitarias del usuario de sesion mockeado (USR-01)."""
from ecoharmony.dominio.usuarios import usuario_mock


def test_usr_01_el_usuario_mock_tiene_identificador_y_email_valido():
    usuario = usuario_mock()
    assert usuario.id
    assert "@" in usuario.email
