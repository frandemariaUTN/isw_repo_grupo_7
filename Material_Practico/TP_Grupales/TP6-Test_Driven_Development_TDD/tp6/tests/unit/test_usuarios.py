"""Pruebas unitarias del usuario de sesion mockeado (USR-01)."""
from ecoharmony.dominio.usuarios import usuario_mock


def test_usr_01_el_usuario_mock_es_salva_con_su_email():
    usuario = usuario_mock()
    assert usuario.id
    assert usuario.nombre == "Salva"
    assert usuario.email == "danogamer987654321@gmail.com"
