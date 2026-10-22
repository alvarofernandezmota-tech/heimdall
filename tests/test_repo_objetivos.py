import sqlite3
from datetime import date
from uuid import uuid4

import pytest

from app.database.connection import crear_conexion
from app.database.esquema import aplicar_schema
from app.domain.goal import EstadoObjetivo, Objetivo
from app.domain.user import Usuario
from app.repositories.interfaces import RepositorioObjetivos
from app.repositories.sqlite_objetivos import RepositorioObjetivosSQLite
from app.repositories.sqlite_usuarios import RepositorioUsuariosSQLite


@pytest.fixture
def repos():
    conexion = crear_conexion(":memory:")
    aplicar_schema(conexion)
    try:
        yield RepositorioUsuariosSQLite(conexion), RepositorioObjetivosSQLite(conexion)
    finally:
        conexion.close()


def crear_usuario(usuarios):
    usuario = Usuario(nombre="A")
    usuarios.guardar(usuario)
    return usuario


def test_guardar_y_obtener_devuelve_el_mismo_objetivo(repos):
    usuarios, objetivos = repos
    u = crear_usuario(usuarios)
    o = Objetivo(u.id, "Aprender Python", descripcion="Con proyectos",
                 fecha_limite=date(2026, 12, 31), progreso=40)
    objetivos.guardar(o)
    assert objetivos.obtener(o.id) == o


def test_objetivo_sin_fecha_limite_se_guarda_como_none(repos):
    usuarios, objetivos = repos
    u = crear_usuario(usuarios)
    o = Objetivo(u.id, "Sin fecha")
    objetivos.guardar(o)
    assert objetivos.obtener(o.id).fecha_limite is None


def test_obtener_objetivo_inexistente_devuelve_none(repos):
    _, objetivos = repos
    assert objetivos.obtener(uuid4()) is None


def test_objetivo_de_usuario_inexistente_falla(repos):
    _, objetivos = repos
    with pytest.raises(sqlite3.IntegrityError):
        objetivos.guardar(Objetivo(Usuario(nombre="A").id, "X"))


def test_guardar_de_nuevo_actualiza_progreso_y_estado(repos):
    usuarios, objetivos = repos
    u = crear_usuario(usuarios)
    o = Objetivo(u.id, "Meta")
    objetivos.guardar(o)
    o.actualizar_progreso(100)
    objetivos.guardar(o)
    guardado = objetivos.obtener(o.id)
    assert (guardado.progreso, guardado.estado) == (100, EstadoObjetivo.COMPLETADO)
    assert len(objetivos.listar_por_usuario(u.id)) == 1


def test_listar_ordena_por_fecha_limite_y_deja_sin_fecha_al_final(repos):
    usuarios, objetivos = repos
    u = crear_usuario(usuarios)
    otro = Usuario(nombre="B")
    usuarios.guardar(otro)
    lejano = Objetivo(u.id, "Lejano", fecha_limite=date(2027, 6, 1))
    cercano = Objetivo(u.id, "Cercano", fecha_limite=date(2026, 11, 1))
    sin_fecha = Objetivo(u.id, "Aaa sin fecha")
    ajeno = Objetivo(otro.id, "Ajeno", fecha_limite=date(2026, 1, 1))
    for o in (lejano, sin_fecha, ajeno, cercano):
        objetivos.guardar(o)
    nombres = [o.nombre for o in objetivos.listar_por_usuario(u.id)]
    assert nombres == ["Cercano", "Lejano", "Aaa sin fecha"]


def test_listar_filtra_por_estado(repos):
    usuarios, objetivos = repos
    u = crear_usuario(usuarios)
    activo = Objetivo(u.id, "Activo")
    pausado = Objetivo(u.id, "Pausado")
    pausado.pausar()
    for o in (activo, pausado):
        objetivos.guardar(o)
    solo_pausados = objetivos.listar_por_usuario(u.id, estado=EstadoObjetivo.PAUSADO)
    assert [o.nombre for o in solo_pausados] == ["Pausado"]


def test_eliminar_indica_si_existia(repos):
    usuarios, objetivos = repos
    u = crear_usuario(usuarios)
    o = Objetivo(u.id, "X")
    objetivos.guardar(o)
    assert objetivos.eliminar(o.id) is True
    assert objetivos.eliminar(o.id) is False


def test_eliminar_usuario_elimina_sus_objetivos(repos):
    usuarios, objetivos = repos
    u = crear_usuario(usuarios)
    o = Objetivo(u.id, "X")
    objetivos.guardar(o)
    usuarios.eliminar(u.id)
    assert objetivos.obtener(o.id) is None


def test_la_interfaz_no_se_puede_instanciar():
    with pytest.raises(TypeError):
        RepositorioObjetivos()
