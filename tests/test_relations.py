from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

from app.domain.habit import FrecuenciaHabito, Habito, RegistroHabito
from app.domain.message import Conversacion, Mensaje, RolMensaje
from app.domain.reminder import Recordatorio
from app.domain.relations import (
    de_usuario,
    historial_para_modelo,
    mensajes_de,
    racha_diaria,
    registros_de,
    resumen_del_dia,
)
from app.domain.schedule import Evento
from app.domain.user import Usuario

MAD = ZoneInfo("Europe/Madrid")


def mad(dia, h, m=0):
    return datetime(2026, 10, dia, h, m, tzinfo=MAD)


def test_de_usuario_filtra():
    a, b = Usuario(nombre="A"), Usuario(nombre="B")
    ea = Evento(a.id, "A", mad(23, 10), mad(23, 11))
    eb = Evento(b.id, "B", mad(23, 10), mad(23, 11))
    assert de_usuario(a, [ea, eb]) == [ea]


def test_registros_de_un_habito():
    u = Usuario(nombre="A")
    h1 = Habito(u.id, "H1", FrecuenciaHabito.DIARIA)
    h2 = Habito(u.id, "H2", FrecuenciaHabito.DIARIA)
    r1 = RegistroHabito(h1.id, 1, True)
    r2 = RegistroHabito(h2.id, 1, True)
    assert registros_de(h1, [r1, r2]) == [r1]


def test_mensajes_ordenados_e_historial():
    u = Usuario(nombre="A")
    c = Conversacion(u.id, "t")
    otra = Conversacion(u.id, "otra")
    m1 = Mensaje(c.id, RolMensaje.USUARIO, "hola", fecha_creacion=datetime(2026, 10, 23, 9, tzinfo=UTC))
    m2 = Mensaje(c.id, RolMensaje.ASISTENTE, "buenas", fecha_creacion=datetime(2026, 10, 23, 10, tzinfo=UTC))
    vacio = Mensaje(c.id, RolMensaje.USUARIO, "  ", fecha_creacion=datetime(2026, 10, 23, 11, tzinfo=UTC))
    ajeno = Mensaje(otra.id, RolMensaje.USUARIO, "no", fecha_creacion=datetime(2026, 10, 23, 8, tzinfo=UTC))
    msgs = mensajes_de(c, [m2, ajeno, vacio, m1])
    assert [m.contenido for m in msgs] == ["hola", "buenas", "  "]
    assert historial_para_modelo(msgs) == [
        {"role": "user", "content": "hola"},
        {"role": "assistant", "content": "buenas"},
    ]
    assert len(historial_para_modelo(msgs, limite=1)) == 1


def test_racha_diaria():
    u = Usuario(nombre="A")
    h = Habito(u.id, "Leer", FrecuenciaHabito.DIARIA)
    regs = [RegistroHabito(h.id, 1, True, fecha=mad(d, 20)) for d in (21, 22, 23)]
    assert racha_diaria(h, regs, date(2026, 10, 23), MAD) == 3
    assert racha_diaria(h, regs, date(2026, 10, 24), MAD) == 3
    assert racha_diaria(h, regs, date(2026, 10, 25), MAD) == 0


def test_resumen_del_dia():
    u = Usuario(nombre="A")
    otro = Usuario(nombre="B")
    dia = date(2026, 10, 23)
    ev = Evento(u.id, "Gimnasio", mad(23, 18), mad(23, 19))
    ev_ajeno = Evento(otro.id, "Ajeno", mad(23, 10), mad(23, 11))
    agua = Habito(u.id, "Beber agua", FrecuenciaHabito.DIARIA, objetivo=2)
    leer = Habito(u.id, "Leer", FrecuenciaHabito.DIARIA)
    regs = [
        RegistroHabito(agua.id, 1, False, fecha=mad(23, 9)),
        RegistroHabito(leer.id, 1, True, fecha=mad(23, 8)),
    ]
    rec = Recordatorio(u.id, "Llamar al médico", mad(23, 9, 30))
    res = resumen_del_dia(u, dia, [ev, ev_ajeno], [agua, leer], regs, [rec])
    assert res["eventos"] == [{"titulo": "Gimnasio", "inicio": "18:00", "fin": "19:00"}]
    assert res["habitos_pendientes"] == ["Beber agua"]
    assert res["recordatorios"] == ["Llamar al médico"]
