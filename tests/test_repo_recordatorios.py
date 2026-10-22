import sqlite3
from datetime import UTC, date, datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest

from app.database.connection import crear_conexion
from app.database.esquema import aplicar_schema
from app.domain.habit import FrecuenciaHabito, Habito
from app.domain.reminder import EstadoRecordatorio, Recordatorio
from app.domain.schedule import Evento
from app.domain.user import Usuario
from app.repositories.interfaces import RepositorioRecordatorios
from app.repositories.sqlite_eventos import RepositorioEventosSQLite
from app.repositories.sqlite_habitos import RepositorioHabitosSQLite
from app.repositories.sqlite_recordatorios import RepositorioRecordatoriosSQLite
from app.repositories.sqlite_usuarios import RepositorioUsuariosSQLite

MAD = ZoneInfo("Europe/Madrid")


@pytest.fixture
def repos():
    conexion = crear_conexion(":memory:")
    aplicar_schema(conexion)
    try:
        yield (
            RepositorioUsuariosSQLite(conexion),
            RepositorioEventosSQLite(conexion),
            RepositorioHabitosSQLite(conexion),
            RepositorioRecordatoriosSQLite(conexion),
        )
    finally:
        conexion.close()


def madrid(dia, hora, minuto=0):
    return datetime(2026, 10, dia, hora, minuto, tzinfo=MAD)


def crear_usuario(usuarios):
    usuario = Usuario(nombre="A")
    usuarios.guardar(usuario)
    return usuario


def test_guardar_y_obtener_devuelve_el_mismo_recordatorio(repos):
    usuarios, eventos, habitos, recordatorios = repos
    u = crear_usuario(usuarios)
    e = Evento(u.id, "Gimnasio", madrid(23, 18), madrid(23, 19))
    h = Habito(u.id, "Agua", FrecuenciaHabito.DIARIA)
    eventos.guardar(e)
    habitos.guardar(h)
    r = Recordatorio(u.id, "Es la hora", madrid(23, 17), evento_id=e.id, habito_id=h.id)
    recordatorios.guardar(r)
    assert recordatorios.obtener(r.id) == r


def test_obtener_recordatorio_inexistente_devuelve_none(repos):
    *_, recordatorios = repos
    assert recordatorios.obtener(uuid4()) is None


def test_recordatorio_de_usuario_inexistente_falla(repos):
    *_, recordatorios = repos
    r = Recordatorio(Usuario(nombre="A").id, "X", madrid(23, 9))
    with pytest.raises(sqlite3.IntegrityError):
        recordatorios.guardar(r)


def test_recordatorio_de_evento_inexistente_falla(repos):
    usuarios, _, _, recordatorios = repos
    u = crear_usuario(usuarios)
    r = Recordatorio(u.id, "X", madrid(23, 9), evento_id=uuid4())
    with pytest.raises(sqlite3.IntegrityError):
        recordatorios.guardar(r)


def test_guardar_de_nuevo_actualiza_el_estado(repos):
    usuarios, _, _, recordatorios = repos
    u = crear_usuario(usuarios)
    r = Recordatorio(u.id, "X", madrid(23, 9))
    recordatorios.guardar(r)
    r.marcar_enviado()
    recordatorios.guardar(r)
    assert recordatorios.obtener(r.id).estado == EstadoRecordatorio.ENVIADO
    assert len(recordatorios.listar_por_usuario(u.id)) == 1


def test_listar_por_usuario_ordena_y_filtra(repos):
    usuarios, _, _, recordatorios = repos
    a = crear_usuario(usuarios)
    b = crear_usuario(usuarios)
    tarde = Recordatorio(a.id, "Tarde", madrid(23, 18))
    pronto = Recordatorio(a.id, "Pronto", madrid(23, 8))
    ajeno = Recordatorio(b.id, "Ajeno", madrid(23, 7))
    for r in (tarde, ajeno, pronto):
        recordatorios.guardar(r)
    assert [r.mensaje for r in recordatorios.listar_por_usuario(a.id)] == ["Pronto", "Tarde"]


def test_listar_de_evento_devuelve_solo_los_de_ese_evento(repos):
    usuarios, eventos, _, recordatorios = repos
    u = crear_usuario(usuarios)
    e1 = Evento(u.id, "E1", madrid(23, 18), madrid(23, 19))
    e2 = Evento(u.id, "E2", madrid(23, 20), madrid(23, 21))
    eventos.guardar(e1)
    eventos.guardar(e2)
    r1 = Recordatorio(u.id, "Para E1", madrid(23, 17), evento_id=e1.id)
    r2 = Recordatorio(u.id, "Para E2", madrid(23, 19), evento_id=e2.id)
    suelto = Recordatorio(u.id, "Suelto", madrid(23, 9))
    for r in (r1, r2, suelto):
        recordatorios.guardar(r)
    assert [r.mensaje for r in recordatorios.listar_de_evento(e1.id)] == ["Para E1"]


def test_listar_pendientes_del_dia_usa_zona_estado_y_usuario(repos):
    usuarios, _, _, recordatorios = repos
    a = crear_usuario(usuarios)
    b = crear_usuario(usuarios)
    ayer_noche = Recordatorio(a.id, "Ayer 23:30", madrid(22, 23, 30))
    madrugada = Recordatorio(a.id, "Hoy 00:30", madrid(23, 0, 30))
    tarde = Recordatorio(a.id, "Hoy 18:00", madrid(23, 18))
    manana = Recordatorio(a.id, "Mañana 00:00", madrid(24, 0))
    enviado = Recordatorio(a.id, "Enviado", madrid(23, 10))
    enviado.marcar_enviado()
    cancelado = Recordatorio(a.id, "Cancelado", madrid(23, 11))
    cancelado.cancelar()
    ajeno = Recordatorio(b.id, "Ajeno", madrid(23, 12))
    for r in (ayer_noche, madrugada, tarde, manana, enviado, cancelado, ajeno):
        recordatorios.guardar(r)
    del_dia = recordatorios.listar_pendientes_del_dia(a.id, date(2026, 10, 23), MAD)
    assert [r.mensaje for r in del_dia] == ["Hoy 00:30", "Hoy 18:00"]


def test_listar_vencidos_incluye_todos_los_usuarios_y_solo_pendientes(repos):
    usuarios, _, _, recordatorios = repos
    a = crear_usuario(usuarios)
    b = crear_usuario(usuarios)
    ahora = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)
    vencido_a = Recordatorio(a.id, "Vencido A", datetime(2026, 10, 23, 9, tzinfo=UTC))
    vencido_b = Recordatorio(b.id, "Vencido B", datetime(2026, 10, 23, 10, tzinfo=UTC))
    justo_ahora = Recordatorio(a.id, "Justo ahora", ahora)
    futuro = Recordatorio(a.id, "Futuro", datetime(2026, 10, 23, 13, tzinfo=UTC))
    enviado = Recordatorio(a.id, "Enviado", datetime(2026, 10, 23, 8, tzinfo=UTC))
    enviado.marcar_enviado()
    for r in (futuro, vencido_b, enviado, justo_ahora, vencido_a):
        recordatorios.guardar(r)
    mensajes = [r.mensaje for r in recordatorios.listar_vencidos(ahora)]
    assert mensajes == ["Vencido A", "Vencido B", "Justo ahora"]


def test_listar_vencidos_coincide_con_la_regla_del_dominio(repos):
    usuarios, _, _, recordatorios = repos
    u = crear_usuario(usuarios)
    ahora = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)
    todos = [
        Recordatorio(u.id, f"R{hora}", datetime(2026, 10, 23, hora, tzinfo=UTC))
        for hora in (6, 12, 18)
    ]
    todos[0].cancelar()
    for r in todos:
        recordatorios.guardar(r)
    esperados = sorted(r.mensaje for r in todos if r.esta_vencido(ahora))
    assert sorted(r.mensaje for r in recordatorios.listar_vencidos(ahora)) == esperados


def test_eliminar_indica_si_existia(repos):
    usuarios, _, _, recordatorios = repos
    u = crear_usuario(usuarios)
    r = Recordatorio(u.id, "X", madrid(23, 9))
    recordatorios.guardar(r)
    assert recordatorios.eliminar(r.id) is True
    assert recordatorios.eliminar(r.id) is False


def test_eliminar_evento_elimina_sus_recordatorios(repos):
    usuarios, eventos, _, recordatorios = repos
    u = crear_usuario(usuarios)
    e = Evento(u.id, "E", madrid(23, 18), madrid(23, 19))
    eventos.guardar(e)
    r = Recordatorio(u.id, "Para E", madrid(23, 17), evento_id=e.id)
    recordatorios.guardar(r)
    eventos.eliminar(e.id)
    assert recordatorios.obtener(r.id) is None


def test_eliminar_habito_elimina_sus_recordatorios(repos):
    usuarios, _, habitos, recordatorios = repos
    u = crear_usuario(usuarios)
    h = Habito(u.id, "Agua", FrecuenciaHabito.DIARIA)
    habitos.guardar(h)
    r = Recordatorio(u.id, "Beber", madrid(23, 9), habito_id=h.id)
    recordatorios.guardar(r)
    habitos.eliminar(h.id)
    assert recordatorios.obtener(r.id) is None


def test_la_interfaz_no_se_puede_instanciar():
    with pytest.raises(TypeError):
        RepositorioRecordatorios()
