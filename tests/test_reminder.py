from datetime import UTC, datetime

from app.domain.reminder import EstadoRecordatorio, Recordatorio
from app.domain.schedule import Evento
from app.domain.user import Usuario


def cuando(h):
    return datetime(2026, 10, 23, h, 0, tzinfo=UTC)


def test_recordatorio_pendiente_por_defecto():
    u = Usuario(nombre="Álvaro")
    r = Recordatorio(u.id, "Beber agua", cuando(9))
    assert r.estado == EstadoRecordatorio.PENDIENTE
    assert r.evento_id is None
    assert r.habito_id is None


def test_recordatorio_de_un_evento():
    u = Usuario(nombre="Álvaro")
    e = Evento(u.id, "Gimnasio", cuando(18), cuando(19))
    r = Recordatorio(u.id, "Es hora del gimnasio", cuando(17), evento_id=e.id)
    assert r.evento_id == e.id


def test_enviar_y_cancelar():
    u = Usuario(nombre="Álvaro")
    r = Recordatorio(u.id, "Llamar", cuando(12))
    r.marcar_enviado()
    assert r.estado == EstadoRecordatorio.ENVIADO
    r.cancelar()
    assert r.estado == EstadoRecordatorio.CANCELADO
