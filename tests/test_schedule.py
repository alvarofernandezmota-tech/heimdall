from datetime import UTC, datetime

import pytest

from app.domain.schedule import EstadoEvento, Evento, Horario
from app.domain.user import Usuario


def hora(h, m=0):
    return datetime(2026, 10, 23, h, m, tzinfo=UTC)


def test_evento_valido():
    u = Usuario(nombre="Álvaro")
    e = Evento(u.id, "Gimnasio", hora(18), hora(19))
    assert e.estado == EstadoEvento.PROGRAMADO


def test_evento_que_termina_antes_de_empezar():
    u = Usuario(nombre="Álvaro")
    with pytest.raises(ValueError):
        Evento(u.id, "Mal", hora(19), hora(18))


def test_evento_de_duracion_cero():
    u = Usuario(nombre="Álvaro")
    with pytest.raises(ValueError):
        Evento(u.id, "Cero", hora(18), hora(18))


def test_cancelar():
    u = Usuario(nombre="Álvaro")
    e = Evento(u.id, "Reunión", hora(10), hora(11))
    e.cancelar()
    assert e.estado == EstadoEvento.CANCELADO


def test_completar():
    u = Usuario(nombre="Álvaro")
    e = Evento(u.id, "Reunión", hora(10), hora(11))
    e.completar()
    assert e.estado == EstadoEvento.COMPLETADO


def test_horario_ordena_por_inicio():
    u = Usuario(nombre="Álvaro")
    tarde = Evento(u.id, "Gimnasio", hora(18), hora(19))
    manana = Evento(u.id, "Reunión", hora(10, 30), hora(11, 15))
    h = Horario([tarde, manana])
    assert [e.titulo for e in h.eventos_ordenados()] == ["Reunión", "Gimnasio"]
