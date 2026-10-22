from datetime import UTC, datetime

from app.domain.schedule import Evento, Horario
from app.domain.user import Usuario


def hora(h):
    return datetime(2026, 10, 23, h, 0, tzinfo=UTC)


def test_conflicto_solo_dentro_del_mismo_usuario():
    a, b = Usuario(nombre="A"), Usuario(nombre="B")
    de_a = Evento(a.id, "Reunión", hora(10), hora(11))
    de_b = Evento(b.id, "Médico", hora(10), hora(11))
    assert not Horario([de_a]).hay_conflicto(de_b)
    assert Horario([de_a]).hay_conflicto(Evento(a.id, "Otra", hora(10), hora(11)))


def test_evento_no_entra_en_conflicto_consigo_mismo():
    usuario = Usuario(nombre="A")
    evento = Evento(usuario.id, "Reunión", hora(10), hora(11))
    assert not Horario([evento]).hay_conflicto(evento)
