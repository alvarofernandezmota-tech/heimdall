from datetime import UTC, date, datetime, timedelta
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from app.database.connection import crear_conexion
from app.database.esquema import aplicar_schema
from app.domain.reminder import EstadoRecordatorio, Recordatorio
from app.domain.user import Usuario
from app.repositories.sqlite_eventos import RepositorioEventosSQLite
from app.repositories.sqlite_recordatorios import RepositorioRecordatoriosSQLite
from app.repositories.sqlite_usuarios import RepositorioUsuariosSQLite
from app.services.agenda import ServicioAgenda
from app.services.errores import (
    EventoNoActivo,
    EventoNoEncontrado,
    RecordatorioEnElPasado,
    RecordatorioNoEncontrado,
    UsuarioNoEncontrado,
)
from app.services.recordatorios import ServicioRecordatorios

MAD = ZoneInfo("Europe/Madrid")
AHORA = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)


@pytest.fixture
def conexion():
    conexion = crear_conexion(":memory:")
    aplicar_schema(conexion)
    try:
        yield conexion
    finally:
        conexion.close()


@pytest.fixture
def entorno(conexion):
    usuarios = RepositorioUsuariosSQLite(conexion)
    eventos = RepositorioEventosSQLite(conexion)
    recordatorios = RepositorioRecordatoriosSQLite(conexion)
    usuario = Usuario(nombre="A")
    usuarios.guardar(usuario)
    return (
        ServicioRecordatorios(usuarios, eventos, recordatorios, reloj=lambda: AHORA),
        ServicioAgenda(usuarios, eventos),
        recordatorios,
        usuario,
    )


@pytest.fixture
def otro_usuario(conexion):
    usuario = Usuario(nombre="B")
    RepositorioUsuariosSQLite(conexion).guardar(usuario)
    return usuario


def madrid(dia, hora, minuto=0):
    return datetime(2026, 10, dia, hora, minuto, tzinfo=MAD)


def test_programar_guarda_un_aviso_libre(entorno):
    servicio, _, repo, u = entorno
    r = servicio.programar(u.id, "  Llamar al médico ", madrid(23, 18))
    assert r.mensaje == "Llamar al médico"
    assert r.evento_id is None
    assert repo.obtener(r.id) == r


def test_programar_en_el_pasado_lanza_error_y_no_guarda(entorno):
    servicio, _, repo, u = entorno
    with pytest.raises(RecordatorioEnElPasado):
        servicio.programar(u.id, "X", AHORA - timedelta(minutes=1))
    assert repo.listar_por_usuario(u.id) == []


def test_programar_rechaza_mensaje_vacio(entorno):
    servicio, _, _, u = entorno
    with pytest.raises(ValidationError):
        servicio.programar(u.id, "   ", madrid(23, 18))


def test_programar_de_usuario_inexistente_lanza_error(entorno):
    servicio, _, _, _ = entorno
    with pytest.raises(UsuarioNoEncontrado):
        servicio.programar(uuid4(), "X", madrid(23, 18))


def test_programar_para_evento_calcula_la_hora_y_el_mensaje(entorno):
    servicio, agenda, repo, u = entorno
    e = agenda.crear_evento(u.id, "Gimnasio", madrid(23, 18), madrid(23, 19))
    r = servicio.programar_para_evento(u.id, e.id, timedelta(minutes=30))
    assert r.evento_id == e.id
    assert r.programado_para == madrid(23, 17, 30)
    assert r.mensaje == "Gimnasio empieza a las 18:00"
    assert repo.obtener(r.id) == r


def test_programar_para_evento_acepta_mensaje_propio(entorno):
    servicio, agenda, _, u = entorno
    e = agenda.crear_evento(u.id, "Gimnasio", madrid(23, 18), madrid(23, 19))
    r = servicio.programar_para_evento(u.id, e.id, timedelta(hours=1), mensaje="Prepara la bolsa")
    assert r.mensaje == "Prepara la bolsa"


def test_programar_para_evento_inexistente_lanza_error(entorno):
    servicio, _, _, u = entorno
    with pytest.raises(EventoNoEncontrado):
        servicio.programar_para_evento(u.id, uuid4(), timedelta(minutes=10))


def test_programar_para_evento_cancelado_lanza_error(entorno):
    servicio, agenda, _, u = entorno
    e = agenda.crear_evento(u.id, "X", madrid(23, 18), madrid(23, 19))
    agenda.cancelar_evento(u.id, e.id)
    with pytest.raises(EventoNoActivo):
        servicio.programar_para_evento(u.id, e.id, timedelta(minutes=10))


def test_programar_para_evento_con_antelacion_negativa_lanza_error(entorno):
    servicio, agenda, _, u = entorno
    e = agenda.crear_evento(u.id, "X", madrid(23, 18), madrid(23, 19))
    with pytest.raises(ValueError):
        servicio.programar_para_evento(u.id, e.id, timedelta(minutes=-5))


def test_aviso_de_evento_que_caeria_en_el_pasado_lanza_error(entorno):
    servicio, agenda, _, u = entorno
    e = agenda.crear_evento(u.id, "Pronto", madrid(23, 14, 30), madrid(23, 15))
    with pytest.raises(RecordatorioEnElPasado):
        servicio.programar_para_evento(u.id, e.id, timedelta(hours=3))


def test_cancelar_y_marcar_enviado_se_guardan(entorno):
    servicio, _, repo, u = entorno
    a = servicio.programar(u.id, "A", madrid(23, 18))
    b = servicio.programar(u.id, "B", madrid(23, 19))
    servicio.cancelar(u.id, a.id)
    servicio.marcar_enviado(b.id)
    assert repo.obtener(a.id).estado == EstadoRecordatorio.CANCELADO
    assert repo.obtener(b.id).estado == EstadoRecordatorio.ENVIADO


def test_operar_sobre_un_recordatorio_inexistente_lanza_error(entorno):
    servicio, _, _, u = entorno
    with pytest.raises(RecordatorioNoEncontrado):
        servicio.cancelar(u.id, uuid4())
    with pytest.raises(RecordatorioNoEncontrado):
        servicio.marcar_enviado(uuid4())


def test_pendientes_del_dia_usa_la_zona_del_usuario(entorno):
    servicio, _, _, u = entorno
    servicio.programar(u.id, "Hoy 00:30", madrid(24, 0, 30))
    servicio.programar(u.id, "Hoy 18:00", madrid(24, 18))
    servicio.programar(u.id, "Mañana", madrid(25, 9))
    enviado = servicio.programar(u.id, "Enviado", madrid(24, 10))
    servicio.marcar_enviado(enviado.id)
    del_dia = servicio.pendientes_del_dia(u.id, date(2026, 10, 24))
    assert [r.mensaje for r in del_dia] == ["Hoy 00:30", "Hoy 18:00"]


def test_vencidos_usa_el_reloj_y_deja_fuera_los_enviados(entorno):
    servicio, _, repo, u = entorno
    viejo = Recordatorio(u.id, "Viejo", AHORA - timedelta(hours=1))
    justo = Recordatorio(u.id, "Justo", AHORA)
    futuro = Recordatorio(u.id, "Futuro", AHORA + timedelta(hours=1))
    enviado = Recordatorio(u.id, "Enviado", AHORA - timedelta(hours=2))
    enviado.marcar_enviado()
    for r in (futuro, enviado, justo, viejo):
        repo.guardar(r)
    assert [r.mensaje for r in servicio.vencidos()] == ["Viejo", "Justo"]


def test_no_se_puede_programar_un_aviso_para_el_evento_de_otro_usuario(entorno, otro_usuario):
    servicio, agenda, repo, u = entorno
    e = agenda.crear_evento(u.id, "Privado", madrid(23, 18), madrid(23, 19))
    with pytest.raises(EventoNoEncontrado):
        servicio.programar_para_evento(otro_usuario.id, e.id, timedelta(minutes=30))
    assert repo.listar_por_usuario(u.id) == []
    assert repo.listar_por_usuario(otro_usuario.id) == []


def test_un_usuario_no_puede_cancelar_el_recordatorio_de_otro(entorno, otro_usuario):
    servicio, _, repo, u = entorno
    r = servicio.programar(u.id, "Privado", madrid(23, 18))
    with pytest.raises(RecordatorioNoEncontrado):
        servicio.cancelar(otro_usuario.id, r.id)
    assert repo.obtener(r.id).estado == EstadoRecordatorio.PENDIENTE
