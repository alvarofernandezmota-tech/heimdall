import sqlite3
from datetime import UTC, date, datetime, timedelta
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest

from app.database.connection import crear_conexion
from app.database.esquema import aplicar_schema
from app.domain.habit import FrecuenciaHabito, Habito, RegistroHabito
from app.domain.relations import racha_diaria
from app.domain.user import Usuario
from app.repositories.interfaces import RepositorioHabitos, RepositorioRegistrosHabito
from app.repositories.sqlite_habitos import (
    RepositorioHabitosSQLite,
    RepositorioRegistrosHabitoSQLite,
)
from app.repositories.sqlite_usuarios import RepositorioUsuariosSQLite

MAD = ZoneInfo("Europe/Madrid")


@pytest.fixture
def repos():
    conexion = crear_conexion(":memory:")
    aplicar_schema(conexion)
    try:
        yield (
            RepositorioUsuariosSQLite(conexion),
            RepositorioHabitosSQLite(conexion),
            RepositorioRegistrosHabitoSQLite(conexion),
        )
    finally:
        conexion.close()


def crear_habito(usuarios, habitos, nombre="Leer", **extra):
    usuario = Usuario(nombre="A")
    usuarios.guardar(usuario)
    habito = Habito(usuario.id, nombre, FrecuenciaHabito.DIARIA, **extra)
    habitos.guardar(habito)
    return usuario, habito


def test_guardar_y_obtener_devuelve_el_mismo_habito(repos):
    usuarios, habitos, _ = repos
    usuario = Usuario(nombre="A")
    usuarios.guardar(usuario)
    h = Habito(usuario.id, "Beber agua", FrecuenciaHabito.DIARIA,
               descripcion="Agua", objetivo=2.5, unidad="litros")
    habitos.guardar(h)
    assert habitos.obtener(h.id) == h


def test_obtener_habito_inexistente_devuelve_none(repos):
    _, habitos, _ = repos
    assert habitos.obtener(uuid4()) is None


def test_guardar_de_nuevo_actualiza_el_habito(repos):
    usuarios, habitos, _ = repos
    _, h = crear_habito(usuarios, habitos)
    h.desactivar()
    habitos.guardar(h)
    assert habitos.obtener(h.id).activo is False


def test_habito_de_usuario_inexistente_falla(repos):
    _, habitos, _ = repos
    h = Habito(Usuario(nombre="A").id, "X", FrecuenciaHabito.DIARIA)
    with pytest.raises(sqlite3.IntegrityError):
        habitos.guardar(h)


def test_listar_por_usuario_ordena_filtra_y_admite_solo_activos(repos):
    usuarios, habitos, _ = repos
    a, b = Usuario(nombre="A"), Usuario(nombre="B")
    usuarios.guardar(a)
    usuarios.guardar(b)
    leer = Habito(a.id, "Leer", FrecuenciaHabito.DIARIA)
    agua = Habito(a.id, "Agua", FrecuenciaHabito.DIARIA)
    viejo = Habito(a.id, "Viejo", FrecuenciaHabito.SEMANAL)
    viejo.desactivar()
    ajeno = Habito(b.id, "Ajeno", FrecuenciaHabito.DIARIA)
    for h in (leer, viejo, ajeno, agua):
        habitos.guardar(h)
    assert [h.nombre for h in habitos.listar_por_usuario(a.id)] == ["Agua", "Leer", "Viejo"]
    assert [h.nombre for h in habitos.listar_por_usuario(a.id, solo_activos=True)] == ["Agua", "Leer"]


def test_eliminar_habito_indica_si_existia(repos):
    usuarios, habitos, _ = repos
    _, h = crear_habito(usuarios, habitos)
    assert habitos.eliminar(h.id) is True
    assert habitos.eliminar(h.id) is False


def test_eliminar_usuario_elimina_habitos_y_registros(repos):
    usuarios, habitos, registros = repos
    u, h = crear_habito(usuarios, habitos)
    r = RegistroHabito(h.id, 1, True)
    registros.guardar(r)
    usuarios.eliminar(u.id)
    assert habitos.obtener(h.id) is None
    assert registros.obtener(r.id) is None


def test_las_interfaces_no_se_pueden_instanciar():
    with pytest.raises(TypeError):
        RepositorioHabitos()
    with pytest.raises(TypeError):
        RepositorioRegistrosHabito()


def test_registro_guardar_y_obtener_devuelve_el_mismo_registro(repos):
    usuarios, habitos, registros = repos
    _, h = crear_habito(usuarios, habitos)
    r = RegistroHabito(h.id, 1.5, True, notas="Capítulo 3")
    registros.guardar(r)
    assert registros.obtener(r.id) == r


def test_registro_de_habito_inexistente_falla(repos):
    _, _, registros = repos
    with pytest.raises(sqlite3.IntegrityError):
        registros.guardar(RegistroHabito(uuid4(), 1, True))


def test_registro_guardar_de_nuevo_actualiza(repos):
    usuarios, habitos, registros = repos
    _, h = crear_habito(usuarios, habitos)
    r = RegistroHabito(h.id, 1, False)
    registros.guardar(r)
    r.valor = 3
    r.completado = True
    registros.guardar(r)
    guardado = registros.obtener(r.id)
    assert (guardado.valor, guardado.completado) == (3, True)
    assert len(registros.listar_por_habito(h.id)) == 1


def test_registro_listar_por_habito_ordena_por_fecha(repos):
    usuarios, habitos, registros = repos
    _, h = crear_habito(usuarios, habitos)
    tarde = RegistroHabito(h.id, 1, True, fecha=datetime(2026, 10, 23, 20, tzinfo=UTC))
    pronto = RegistroHabito(h.id, 1, True, fecha=datetime(2026, 10, 23, 8, tzinfo=UTC))
    for r in (tarde, pronto):
        registros.guardar(r)
    assert [r.id for r in registros.listar_por_habito(h.id)] == [pronto.id, tarde.id]


def test_registro_listar_por_rango_incluye_desde_y_excluye_hasta(repos):
    usuarios, habitos, registros = repos
    _, h = crear_habito(usuarios, habitos)
    desde = datetime(2026, 10, 23, 0, 0, tzinfo=MAD)
    hasta = desde + timedelta(days=1)
    antes = RegistroHabito(h.id, 1, True, fecha=desde - timedelta(minutes=1))
    justo_desde = RegistroHabito(h.id, 1, True, fecha=desde)
    dentro = RegistroHabito(h.id, 1, True, fecha=desde + timedelta(hours=12))
    justo_hasta = RegistroHabito(h.id, 1, True, fecha=hasta)
    for r in (antes, justo_desde, dentro, justo_hasta):
        registros.guardar(r)
    ids = [r.id for r in registros.listar_por_rango(h.id, desde, hasta)]
    assert ids == [justo_desde.id, dentro.id]


def test_registro_eliminar_indica_si_existia(repos):
    usuarios, habitos, registros = repos
    _, h = crear_habito(usuarios, habitos)
    r = RegistroHabito(h.id, 1, True)
    registros.guardar(r)
    assert registros.eliminar(r.id) is True
    assert registros.eliminar(r.id) is False


def test_eliminar_habito_elimina_sus_registros(repos):
    usuarios, habitos, registros = repos
    _, h = crear_habito(usuarios, habitos)
    r = RegistroHabito(h.id, 1, True)
    registros.guardar(r)
    habitos.eliminar(h.id)
    assert registros.obtener(r.id) is None


def test_los_registros_leidos_sirven_para_calcular_la_racha(repos):
    usuarios, habitos, registros = repos
    _, h = crear_habito(usuarios, habitos, nombre="Leer")
    for dia in (21, 22, 23):
        registros.guardar(
            RegistroHabito(h.id, 1, True, fecha=datetime(2026, 10, dia, 20, tzinfo=MAD))
        )
    guardados = registros.listar_por_habito(h.id)
    assert racha_diaria(habitos.obtener(h.id), guardados, date(2026, 10, 23), MAD) == 3
