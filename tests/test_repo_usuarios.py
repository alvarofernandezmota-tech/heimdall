from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.database.connection import crear_conexion
from app.database.esquema import aplicar_schema
from app.domain.user import Usuario
from app.repositories.interfaces import RepositorioUsuarios
from app.repositories.sqlite_usuarios import RepositorioUsuariosSQLite


@pytest.fixture
def repo():
    conexion = crear_conexion(":memory:")
    aplicar_schema(conexion)
    try:
        yield RepositorioUsuariosSQLite(conexion)
    finally:
        conexion.close()


def test_guardar_y_obtener_devuelve_el_mismo_usuario(repo):
    usuario = Usuario(nombre="Álvaro", preferencias={"tema": "oscuro", "tamaño": 3})
    repo.guardar(usuario)
    assert repo.obtener(usuario.id) == usuario


def test_obtener_usuario_inexistente_devuelve_none(repo):
    assert repo.obtener(uuid4()) is None


def test_guardar_dos_veces_actualiza_sin_duplicar(repo):
    usuario = Usuario(nombre="Álvaro")
    repo.guardar(usuario)
    usuario.nombre = "Álvaro F."
    usuario.desactivar()
    repo.guardar(usuario)
    assert len(repo.listar()) == 1
    guardado = repo.obtener(usuario.id)
    assert guardado.nombre == "Álvaro F."
    assert guardado.activo is False


def test_listar_ordena_por_fecha_de_creacion(repo):
    antiguo = Usuario(nombre="A", fecha_creacion=datetime(2026, 1, 1, tzinfo=UTC))
    reciente = Usuario(nombre="B", fecha_creacion=datetime(2026, 6, 1, tzinfo=UTC))
    repo.guardar(reciente)
    repo.guardar(antiguo)
    assert [u.nombre for u in repo.listar()] == ["A", "B"]


def test_eliminar_indica_si_existia(repo):
    usuario = Usuario(nombre="A")
    repo.guardar(usuario)
    assert repo.eliminar(usuario.id) is True
    assert repo.eliminar(usuario.id) is False
    assert repo.obtener(usuario.id) is None


def test_la_interfaz_no_se_puede_instanciar():
    with pytest.raises(TypeError):
        RepositorioUsuarios()
