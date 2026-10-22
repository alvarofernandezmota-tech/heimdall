import sqlite3
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from app.database.connection import crear_conexion
from app.database.esquema import aplicar_schema
from app.domain.schedule import EstadoEvento, Evento
from app.domain.user import Usuario
from app.repositories.interfaces import RepositorioEventos
from app.repositories.sqlite_eventos import RepositorioEventosSQLite
from app.repositories.sqlite_usuarios import RepositorioUsuariosSQLite

MAD = ZoneInfo("Europe/Madrid")


@pytest.fixture
def repos():
    conexion = crear_conexion(":memory:")
    aplicar_schema(conexion)
    try:
        yield RepositorioUsuariosSQLite(conexion), RepositorioEventosSQLite(conexion)
    finally:
        conexion.close()


def madrid(dia, hora, minuto=0):
    return datetime(2026, 10, dia, hora, minuto, tzinfo=MAD)


def test_guardar_y_obtener_devuelve_el_mismo_evento(repos):
    usuarios, eventos = repos
    u = Usuario(nombre="A")
    usuarios.guardar(u)
    e = Evento(u.id, "Gimnasio", madrid(23, 18), madrid(23, 19),
               descripcion="Piernas", ubicacion="Casa")
    eventos.guardar(e)
    assert eventos.obtener(e.id) == e


def test_evento_de_usuario_inexistente_falla(repos):
    _, eventos = repos
    e = Evento(Usuario(nombre="A").id, "X", madrid(23, 18), madrid(23, 19))
    with pytest.raises(sqlite3.IntegrityError):
        eventos.guardar(e)


def test_guardar_de_nuevo_actualiza_el_estado(repos):
    usuarios, eventos = repos
    u = Usuario(nombre="A")
    usuarios.guardar(u)
    e = Evento(u.id, "X", madrid(23, 18), madrid(23, 19))
    eventos.guardar(e)
    e.cancelar()
    eventos.guardar(e)
    assert eventos.obtener(e.id).estado == EstadoEvento.CANCELADO
    assert len(eventos.listar_por_usuario(u.id)) == 1


def test_actualizar_usuario_no_borra_sus_eventos(repos):
    usuarios, eventos = repos
    u = Usuario(nombre="A")
    usuarios.guardar(u)
    e = Evento(u.id, "X", madrid(23, 18), madrid(23, 19))
    eventos.guardar(e)
    u.nombre = "A2"
    usuarios.guardar(u)
    assert eventos.obtener(e.id) == e


def test_listar_por_usuario_ordena_y_filtra(repos):
    usuarios, eventos = repos
    a, b = Usuario(nombre="A"), Usuario(nombre="B")
    usuarios.guardar(a)
    usuarios.guardar(b)
    tarde = Evento(a.id, "Tarde", madrid(23, 18), madrid(23, 19))
    pronto = Evento(a.id, "Pronto", madrid(23, 9), madrid(23, 10))
    ajeno = Evento(b.id, "Ajeno", madrid(23, 9), madrid(23, 10))
    for e in (tarde, ajeno, pronto):
        eventos.guardar(e)
    assert [e.titulo for e in eventos.listar_por_usuario(a.id)] == ["Pronto", "Tarde"]


def test_listar_activos_del_dia_usa_la_zona_del_usuario(repos):
    usuarios, eventos = repos
    a, b = Usuario(nombre="A"), Usuario(nombre="B")
    usuarios.guardar(a)
    usuarios.guardar(b)
    noche_anterior = Evento(a.id, "Ayer 23:30", madrid(22, 23, 30), madrid(23, 0, 15))
    madrugada = Evento(a.id, "Hoy 00:30", madrid(23, 0, 30), madrid(23, 1, 0))
    tarde = Evento(a.id, "Hoy 18:00", madrid(23, 18), madrid(23, 19))
    manana = Evento(a.id, "Mañana 00:00", madrid(24, 0), madrid(24, 1))
    cancelado = Evento(a.id, "Cancelado", madrid(23, 12), madrid(23, 13))
    cancelado.cancelar()
    ajeno = Evento(b.id, "Ajeno", madrid(23, 10), madrid(23, 11))
    for e in (noche_anterior, madrugada, tarde, manana, cancelado, ajeno):
        eventos.guardar(e)
    del_dia = eventos.listar_activos_del_dia(a.id, date(2026, 10, 23), MAD)
    assert [e.titulo for e in del_dia] == ["Hoy 00:30", "Hoy 18:00"]


def test_eliminar_indica_si_existia(repos):
    usuarios, eventos = repos
    u = Usuario(nombre="A")
    usuarios.guardar(u)
    e = Evento(u.id, "X", madrid(23, 18), madrid(23, 19))
    eventos.guardar(e)
    assert eventos.eliminar(e.id) is True
    assert eventos.eliminar(e.id) is False


def test_eliminar_usuario_elimina_sus_eventos(repos):
    usuarios, eventos = repos
    u = Usuario(nombre="A")
    usuarios.guardar(u)
    e = Evento(u.id, "X", madrid(23, 18), madrid(23, 19))
    eventos.guardar(e)
    usuarios.eliminar(u.id)
    assert eventos.obtener(e.id) is None


def test_la_interfaz_no_se_puede_instanciar():
    with pytest.raises(TypeError):
        RepositorioEventos()
