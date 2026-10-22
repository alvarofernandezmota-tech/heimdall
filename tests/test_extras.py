from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

from app.domain.goal import Objetivo
from app.domain.reminder import Recordatorio
from app.domain.schedule import Evento, Horario
from app.domain.user import Usuario

MAD = ZoneInfo("Europe/Madrid")


def mad(h, m=0):
    return datetime(2026, 10, 23, h, m, tzinfo=MAD)


def test_usuario_zona():
    assert Usuario(nombre="A").zona().key == "Europe/Madrid"


def test_duracion_y_solape():
    u = Usuario(nombre="A")
    a = Evento(u.id, "A", mad(10), mad(11))
    b = Evento(u.id, "B", mad(10, 30), mad(11, 30))
    c = Evento(u.id, "C", mad(11), mad(12))
    assert a.duracion().total_seconds() == 3600
    assert a.se_solapa_con(b)
    assert not a.se_solapa_con(c)


def test_hay_conflicto_ignora_cancelados():
    u = Usuario(nombre="A")
    a = Evento(u.id, "A", mad(10), mad(11))
    nuevo = Evento(u.id, "N", mad(10, 30), mad(11, 30))
    h = Horario([a])
    assert h.hay_conflicto(nuevo)
    a.cancelar()
    assert not h.hay_conflicto(nuevo)


def test_eventos_del_dia():
    u = Usuario(nombre="A")
    hoy = Evento(u.id, "Hoy", mad(18), mad(19))
    otro = Evento(u.id, "Otro", datetime(2026, 10, 24, 9, tzinfo=MAD), datetime(2026, 10, 24, 10, tzinfo=MAD))
    h = Horario([otro, hoy])
    assert [e.titulo for e in h.eventos_del_dia(date(2026, 10, 23), MAD)] == ["Hoy"]


def test_celdas_del_dia():
    u = Usuario(nombre="A")
    e = Evento(u.id, "Gym", mad(18), mad(19))
    celdas = Horario([e]).celdas_del_dia(date(2026, 10, 23), MAD, 15)
    assert len(celdas) == 96
    assert sum(celdas) == 4
    assert celdas[72] and celdas[75]
    assert not celdas[71] and not celdas[76]


def test_celdas_de_30_minutos():
    assert len(Horario([]).celdas_del_dia(date(2026, 10, 23), MAD, 30)) == 48


def test_celdas_dia_cambio_de_hora():
    assert len(Horario([]).celdas_del_dia(date(2026, 10, 25), MAD, 60)) == 25


def test_objetivo_vencido():
    u = Usuario(nombre="A")
    o = Objetivo(u.id, "Meta", fecha_limite=date(2026, 10, 20))
    assert o.dias_restantes(date(2026, 10, 18)) == 2
    assert o.esta_vencido(date(2026, 10, 22))
    o.pausar()
    assert not o.esta_vencido(date(2026, 10, 22))
    assert Objetivo(u.id, "Sin fecha").dias_restantes(date(2026, 10, 22)) is None


def test_recordatorio_vencido():
    u = Usuario(nombre="A")
    r = Recordatorio(u.id, "x", datetime(2026, 10, 23, 9, tzinfo=UTC))
    assert r.esta_vencido(datetime(2026, 10, 23, 10, tzinfo=UTC))
    assert not r.esta_vencido(datetime(2026, 10, 23, 8, tzinfo=UTC))
    r.marcar_enviado()
    assert not r.esta_vencido(datetime(2026, 10, 23, 10, tzinfo=UTC))
