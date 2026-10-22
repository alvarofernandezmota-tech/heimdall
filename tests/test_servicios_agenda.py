from datetime import date, datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from app.database.connection import crear_conexion
from app.database.esquema import aplicar_schema
from app.domain.schedule import EstadoEvento
from app.repositories.sqlite_eventos import RepositorioEventosSQLite
from app.repositories.sqlite_usuarios import RepositorioUsuariosSQLite
from app.services.agenda import ServicioAgenda
from app.services.errores import (
    CambioDeEstadoNoPermitido,
    ConflictoDeHorario,
    EventoNoActivo,
    EventoNoEncontrado,
    UsuarioNoEncontrado,
)
from app.services.usuarios import ServicioUsuarios

MAD = ZoneInfo("Europe/Madrid")


@pytest.fixture
def entorno():
    conexion = crear_conexion(":memory:")
    aplicar_schema(conexion)
    usuarios = RepositorioUsuariosSQLite(conexion)
    eventos = RepositorioEventosSQLite(conexion)
    try:
        yield ServicioAgenda(usuarios, eventos), ServicioUsuarios(usuarios), eventos
    finally:
        conexion.close()


def madrid(dia, hora, minuto=0):
    return datetime(2026, 10, dia, hora, minuto, tzinfo=MAD)


def test_crear_evento_lo_guarda(entorno):
    agenda, usuarios, eventos = entorno
    u = usuarios.registrar("A")
    e = agenda.crear_evento(u.id, "  Gimnasio ", madrid(23, 18), madrid(23, 19),
                            descripcion="Piernas", ubicacion="Casa")
    assert e.titulo == "Gimnasio"
    assert eventos.obtener(e.id) == e


def test_crear_evento_de_usuario_inexistente_lanza_error(entorno):
    agenda, _, _ = entorno
    with pytest.raises(UsuarioNoEncontrado):
        agenda.crear_evento(uuid4(), "X", madrid(23, 18), madrid(23, 19))


def test_crear_evento_que_choca_lanza_conflicto_y_no_guarda(entorno):
    agenda, usuarios, eventos = entorno
    u = usuarios.registrar("A")
    agenda.crear_evento(u.id, "Reunión", madrid(23, 10), madrid(23, 11))
    with pytest.raises(ConflictoDeHorario):
        agenda.crear_evento(u.id, "Otra", madrid(23, 10, 30), madrid(23, 11, 30))
    assert [e.titulo for e in eventos.listar_por_usuario(u.id)] == ["Reunión"]


def test_eventos_contiguos_no_chocan(entorno):
    agenda, usuarios, eventos = entorno
    u = usuarios.registrar("A")
    agenda.crear_evento(u.id, "Uno", madrid(23, 10), madrid(23, 11))
    agenda.crear_evento(u.id, "Dos", madrid(23, 11), madrid(23, 12))
    assert len(eventos.listar_por_usuario(u.id)) == 2


def test_un_evento_cancelado_no_bloquea_el_hueco(entorno):
    agenda, usuarios, _ = entorno
    u = usuarios.registrar("A")
    primero = agenda.crear_evento(u.id, "Uno", madrid(23, 10), madrid(23, 11))
    agenda.cancelar_evento(u.id, primero.id)
    agenda.crear_evento(u.id, "Dos", madrid(23, 10), madrid(23, 11))


def test_usuarios_distintos_pueden_tener_el_mismo_horario(entorno):
    agenda, usuarios, _ = entorno
    a, b = usuarios.registrar("A"), usuarios.registrar("B")
    agenda.crear_evento(a.id, "Uno", madrid(23, 10), madrid(23, 11))
    agenda.crear_evento(b.id, "Otro", madrid(23, 10), madrid(23, 11))


def test_crear_evento_rechaza_fechas_sin_zona(entorno):
    agenda, usuarios, _ = entorno
    u = usuarios.registrar("A")
    with pytest.raises(ValidationError):
        agenda.crear_evento(u.id, "X", datetime(2026, 10, 23, 10), datetime(2026, 10, 23, 11))


def test_crear_evento_rechaza_fin_anterior_al_inicio(entorno):
    agenda, usuarios, _ = entorno
    u = usuarios.registrar("A")
    with pytest.raises(ValueError):
        agenda.crear_evento(u.id, "X", madrid(23, 11), madrid(23, 10))


def test_crear_evento_rechaza_titulo_vacio(entorno):
    agenda, usuarios, _ = entorno
    u = usuarios.registrar("A")
    with pytest.raises(ValidationError):
        agenda.crear_evento(u.id, "   ", madrid(23, 10), madrid(23, 11))


def test_cancelar_y_completar_se_guardan(entorno):
    agenda, usuarios, eventos = entorno
    u = usuarios.registrar("A")
    a = agenda.crear_evento(u.id, "A", madrid(23, 10), madrid(23, 11))
    b = agenda.crear_evento(u.id, "B", madrid(23, 12), madrid(23, 13))
    agenda.cancelar_evento(u.id, a.id)
    agenda.completar_evento(u.id, b.id)
    assert eventos.obtener(a.id).estado == EstadoEvento.CANCELADO
    assert eventos.obtener(b.id).estado == EstadoEvento.COMPLETADO


def test_operar_sobre_un_evento_inexistente_lanza_error(entorno):
    agenda, usuarios, _ = entorno
    u = usuarios.registrar("A")
    with pytest.raises(EventoNoEncontrado):
        agenda.cancelar_evento(u.id, uuid4())


def test_reprogramar_puede_solaparse_con_su_propio_hueco_anterior(entorno):
    agenda, usuarios, eventos = entorno
    u = usuarios.registrar("A")
    e = agenda.crear_evento(u.id, "Reunión", madrid(23, 10), madrid(23, 11))
    agenda.reprogramar_evento(u.id, e.id, madrid(23, 10, 30), madrid(23, 11, 30))
    guardado = eventos.obtener(e.id)
    assert (guardado.comienza, guardado.termina) == (madrid(23, 10, 30), madrid(23, 11, 30))
    assert len(eventos.listar_por_usuario(u.id)) == 1


def test_reprogramar_con_conflicto_lanza_error_y_no_cambia_nada(entorno):
    agenda, usuarios, eventos = entorno
    u = usuarios.registrar("A")
    agenda.crear_evento(u.id, "Fijo", madrid(23, 12), madrid(23, 13))
    e = agenda.crear_evento(u.id, "Móvil", madrid(23, 10), madrid(23, 11))
    with pytest.raises(ConflictoDeHorario):
        agenda.reprogramar_evento(u.id, e.id, madrid(23, 12, 30), madrid(23, 13, 30))
    assert eventos.obtener(e.id).comienza == madrid(23, 10)


def test_no_se_puede_reprogramar_un_evento_cancelado(entorno):
    agenda, usuarios, eventos = entorno
    u = usuarios.registrar("A")
    e = agenda.crear_evento(u.id, "Cancelado", madrid(23, 10), madrid(23, 11))
    agenda.cancelar_evento(u.id, e.id)
    with pytest.raises(EventoNoActivo):
        agenda.reprogramar_evento(u.id, e.id, madrid(23, 12), madrid(23, 13))
    assert eventos.obtener(e.id).comienza == madrid(23, 10)


def test_eventos_del_dia_usa_la_zona_del_usuario(entorno):
    agenda, usuarios, _ = entorno
    u = usuarios.registrar("A")
    agenda.crear_evento(u.id, "Ayer 23:30", madrid(22, 23, 30), madrid(23, 0, 15))
    agenda.crear_evento(u.id, "Hoy 00:30", madrid(23, 0, 30), madrid(23, 1, 0))
    agenda.crear_evento(u.id, "Hoy 18:00", madrid(23, 18), madrid(23, 19))
    del_dia = agenda.eventos_del_dia(u.id, date(2026, 10, 23))
    assert [e.titulo for e in del_dia] == ["Hoy 00:30", "Hoy 18:00"]


def test_eventos_del_dia_de_usuario_inexistente_lanza_error(entorno):
    agenda, _, _ = entorno
    with pytest.raises(UsuarioNoEncontrado):
        agenda.eventos_del_dia(uuid4(), date(2026, 10, 23))


def test_celdas_del_dia_marca_los_tramos_ocupados(entorno):
    agenda, usuarios, _ = entorno
    u = usuarios.registrar("A")
    agenda.crear_evento(u.id, "Gym", madrid(23, 18), madrid(23, 19))
    celdas = agenda.celdas_del_dia(u.id, date(2026, 10, 23))
    assert len(celdas) == 96
    assert sum(celdas) == 4
    assert celdas[72] and celdas[75] and not celdas[71] and not celdas[76]


def test_un_usuario_no_puede_ver_el_evento_de_otro(entorno):
    agenda, usuarios, _ = entorno
    a, b = usuarios.registrar("A"), usuarios.registrar("B")
    e = agenda.crear_evento(a.id, "Privado", madrid(23, 10), madrid(23, 11))
    assert agenda.obtener_evento(a.id, e.id) == e
    with pytest.raises(EventoNoEncontrado):
        agenda.obtener_evento(b.id, e.id)


def test_un_usuario_no_puede_cancelar_el_evento_de_otro(entorno):
    agenda, usuarios, eventos = entorno
    a, b = usuarios.registrar("A"), usuarios.registrar("B")
    e = agenda.crear_evento(a.id, "Privado", madrid(23, 10), madrid(23, 11))
    with pytest.raises(EventoNoEncontrado):
        agenda.cancelar_evento(b.id, e.id)
    assert eventos.obtener(e.id).estado == EstadoEvento.PROGRAMADO


def test_un_usuario_no_puede_completar_el_evento_de_otro(entorno):
    agenda, usuarios, eventos = entorno
    a, b = usuarios.registrar("A"), usuarios.registrar("B")
    e = agenda.crear_evento(a.id, "Privado", madrid(23, 10), madrid(23, 11))
    with pytest.raises(EventoNoEncontrado):
        agenda.completar_evento(b.id, e.id)
    assert eventos.obtener(e.id).estado == EstadoEvento.PROGRAMADO


def test_un_usuario_no_puede_reprogramar_el_evento_de_otro(entorno):
    agenda, usuarios, eventos = entorno
    a, b = usuarios.registrar("A"), usuarios.registrar("B")
    e = agenda.crear_evento(a.id, "Privado", madrid(23, 10), madrid(23, 11))
    with pytest.raises(EventoNoEncontrado):
        agenda.reprogramar_evento(b.id, e.id, madrid(23, 15), madrid(23, 16))
    assert eventos.obtener(e.id).comienza == madrid(23, 10)


def test_no_se_puede_cancelar_dos_veces_un_evento(entorno):
    agenda, usuarios, eventos = entorno
    u = usuarios.registrar("A")
    e = agenda.crear_evento(u.id, "Reunión", madrid(23, 10), madrid(23, 11))
    agenda.cancelar_evento(u.id, e.id)
    with pytest.raises(CambioDeEstadoNoPermitido):
        agenda.cancelar_evento(u.id, e.id)
    assert eventos.obtener(e.id).estado == EstadoEvento.CANCELADO


def test_no_se_puede_completar_un_evento_cancelado(entorno):
    agenda, usuarios, eventos = entorno
    u = usuarios.registrar("A")
    e = agenda.crear_evento(u.id, "Reunión", madrid(23, 10), madrid(23, 11))
    agenda.cancelar_evento(u.id, e.id)
    with pytest.raises(CambioDeEstadoNoPermitido):
        agenda.completar_evento(u.id, e.id)
    assert eventos.obtener(e.id).estado == EstadoEvento.CANCELADO


def test_no_se_puede_cancelar_un_evento_completado(entorno):
    agenda, usuarios, eventos = entorno
    u = usuarios.registrar("A")
    e = agenda.crear_evento(u.id, "Reunión", madrid(23, 10), madrid(23, 11))
    agenda.completar_evento(u.id, e.id)
    with pytest.raises(CambioDeEstadoNoPermitido):
        agenda.cancelar_evento(u.id, e.id)
    assert eventos.obtener(e.id).estado == EstadoEvento.COMPLETADO


def test_no_se_puede_reprogramar_un_evento_completado(entorno):
    agenda, usuarios, eventos = entorno
    u = usuarios.registrar("A")
    e = agenda.crear_evento(u.id, "Reunión", madrid(23, 10), madrid(23, 11))
    agenda.completar_evento(u.id, e.id)
    with pytest.raises(EventoNoActivo):
        agenda.reprogramar_evento(u.id, e.id, madrid(23, 12), madrid(23, 13))
    assert eventos.obtener(e.id).comienza == madrid(23, 10)
