from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from app.database.connection import crear_conexion
from app.database.esquema import aplicar_schema
from app.domain.reminder import EstadoRecordatorio
from app.domain.user import Usuario
from app.repositories.sqlite_eventos import RepositorioEventosSQLite
from app.repositories.sqlite_recordatorios import RepositorioRecordatoriosSQLite
from app.repositories.sqlite_usuarios import RepositorioUsuariosSQLite
from app.services.agenda import ServicioAgenda
from app.services.recordatorios import ServicioRecordatorios

MAD = ZoneInfo("Europe/Madrid")
AHORA = datetime(2026, 10, 23, 8, 0, tzinfo=UTC)


@pytest.fixture
def entorno():
    conexion = crear_conexion(":memory:")
    aplicar_schema(conexion)
    usuarios = RepositorioUsuariosSQLite(conexion)
    eventos = RepositorioEventosSQLite(conexion)
    repo = RepositorioRecordatoriosSQLite(conexion)
    usuario = Usuario(nombre="A")
    usuarios.guardar(usuario)
    agenda = ServicioAgenda(usuarios, eventos, repo)
    avisos = ServicioRecordatorios(usuarios, eventos, repo, reloj=lambda: AHORA)
    try:
        yield agenda, avisos, repo, usuario
    finally:
        conexion.close()


def madrid(dia, hora, minuto=0):
    return datetime(2026, 10, dia, hora, minuto, tzinfo=MAD)


def test_cancelar_un_evento_cancela_sus_recordatorios_pendientes(entorno):
    agenda, avisos, repo, u = entorno
    e = agenda.crear_evento(u.id, "Gimnasio", madrid(23, 18), madrid(23, 19))
    r = avisos.programar_para_evento(u.id, e.id, timedelta(minutes=30))
    agenda.cancelar_evento(u.id, e.id)
    assert repo.obtener(r.id).estado == EstadoRecordatorio.CANCELADO


def test_cancelar_un_evento_no_toca_los_recordatorios_ya_enviados(entorno):
    agenda, avisos, repo, u = entorno
    e = agenda.crear_evento(u.id, "Gimnasio", madrid(23, 18), madrid(23, 19))
    r = avisos.programar_para_evento(u.id, e.id, timedelta(minutes=30))
    avisos.marcar_enviado(r.id)
    agenda.cancelar_evento(u.id, e.id)
    assert repo.obtener(r.id).estado == EstadoRecordatorio.ENVIADO


def test_completar_un_evento_cancela_sus_recordatorios_pendientes(entorno):
    agenda, avisos, repo, u = entorno
    e = agenda.crear_evento(u.id, "Reunión", madrid(23, 18), madrid(23, 19))
    r = avisos.programar_para_evento(u.id, e.id, timedelta(minutes=10))
    agenda.completar_evento(u.id, e.id)
    assert repo.obtener(r.id).estado == EstadoRecordatorio.CANCELADO


def test_reprogramar_un_evento_desplaza_sus_recordatorios_pendientes(entorno):
    agenda, avisos, repo, u = entorno
    e = agenda.crear_evento(u.id, "Reunión", madrid(23, 18), madrid(23, 19))
    r = avisos.programar_para_evento(u.id, e.id, timedelta(minutes=30))
    agenda.reprogramar_evento(u.id, e.id, madrid(23, 20), madrid(23, 21))
    assert repo.obtener(r.id).programado_para == madrid(23, 19, 30)
    assert repo.obtener(r.id).estado == EstadoRecordatorio.PENDIENTE


def test_reprogramar_no_mueve_los_recordatorios_ya_enviados(entorno):
    agenda, avisos, repo, u = entorno
    e = agenda.crear_evento(u.id, "Reunión", madrid(23, 18), madrid(23, 19))
    r = avisos.programar_para_evento(u.id, e.id, timedelta(minutes=30))
    avisos.marcar_enviado(r.id)
    agenda.reprogramar_evento(u.id, e.id, madrid(23, 20), madrid(23, 21))
    assert repo.obtener(r.id).programado_para == madrid(23, 17, 30)


def test_la_agenda_sin_repositorio_de_recordatorios_sigue_funcionando(entorno):
    _, _, _, u = entorno
    conexion = crear_conexion(":memory:")
    aplicar_schema(conexion)
    usuarios = RepositorioUsuariosSQLite(conexion)
    eventos = RepositorioEventosSQLite(conexion)
    usuarios.guardar(u)
    agenda = ServicioAgenda(usuarios, eventos)
    e = agenda.crear_evento(u.id, "X", madrid(23, 10), madrid(23, 11))
    agenda.reprogramar_evento(u.id, e.id, madrid(23, 12), madrid(23, 13))
    agenda.cancelar_evento(u.id, e.id)
    conexion.close()
