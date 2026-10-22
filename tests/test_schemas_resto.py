import json
from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from app.domain.goal import EstadoObjetivo, Objetivo
from app.domain.habit import FrecuenciaHabito, Habito, RegistroHabito
from app.domain.message import Conversacion, Mensaje, RolMensaje
from app.domain.reminder import Recordatorio
from app.domain.schedule import Evento
from app.domain.user import Usuario
from app.schemas.goal import objetivo_a_dict, objetivo_desde_dict
from app.schemas.habit import (
    habito_a_dict,
    habito_desde_dict,
    registro_a_dict,
    registro_desde_dict,
)
from app.schemas.message import (
    conversacion_a_dict,
    conversacion_desde_dict,
    mensaje_a_dict,
    mensaje_desde_dict,
)
from app.schemas.reminder import recordatorio_a_dict, recordatorio_desde_dict
from app.schemas.schedule import evento_a_dict, evento_desde_dict
from app.schemas.user import usuario_a_dict, usuario_desde_dict


def test_habito_ida_y_vuelta():
    u = Usuario(nombre="A")
    h = Habito(u.id, "Beber agua", FrecuenciaHabito.DIARIA, objetivo=2, unidad="litros")
    datos = habito_a_dict(h)
    assert datos["frecuencia"] == "diaria"
    json.dumps(datos)
    assert habito_desde_dict(datos) == h


@pytest.mark.parametrize("objetivo", [0, -1])
def test_habito_objetivo_no_valido(objetivo):
    u = Usuario(nombre="A")
    datos = habito_a_dict(Habito(u.id, "X", FrecuenciaHabito.DIARIA))
    datos["objetivo"] = objetivo
    with pytest.raises(ValidationError):
        habito_desde_dict(datos)


def test_habito_frecuencia_desconocida():
    u = Usuario(nombre="A")
    datos = habito_a_dict(Habito(u.id, "X", FrecuenciaHabito.DIARIA))
    datos["frecuencia"] = "cada luna llena"
    with pytest.raises(ValidationError):
        habito_desde_dict(datos)


def test_registro_ida_y_vuelta_y_valor_negativo():
    u = Usuario(nombre="A")
    h = Habito(u.id, "Leer", FrecuenciaHabito.DIARIA)
    r = RegistroHabito(h.id, 1.5, True, notas="ok")
    datos = registro_a_dict(r)
    json.dumps(datos)
    assert registro_desde_dict(datos) == r
    datos["valor"] = -1
    with pytest.raises(ValidationError):
        registro_desde_dict(datos)


def test_registro_rechaza_fecha_sin_zona():
    u = Usuario(nombre="A")
    h = Habito(u.id, "Leer", FrecuenciaHabito.DIARIA)
    datos = registro_a_dict(RegistroHabito(h.id, 1, True))
    datos["fecha"] = "2026-10-23T09:00:00"
    with pytest.raises(ValidationError):
        registro_desde_dict(datos)


def test_objetivo_ida_y_vuelta():
    u = Usuario(nombre="A")
    o = Objetivo(u.id, "Aprender Python", fecha_limite=date(2026, 12, 31))
    o.actualizar_progreso(40)
    datos = objetivo_a_dict(o)
    assert datos["fecha_limite"] == "2026-12-31"
    json.dumps(datos)
    asi = objetivo_desde_dict(datos)
    assert asi == o
    assert asi.estado == EstadoObjetivo.ACTIVO


@pytest.mark.parametrize("progreso", [-1, 100.5])
def test_objetivo_progreso_fuera_de_rango(progreso):
    u = Usuario(nombre="A")
    datos = objetivo_a_dict(Objetivo(u.id, "X"))
    datos["progreso"] = progreso
    with pytest.raises(ValidationError):
        objetivo_desde_dict(datos)


def test_recordatorio_ida_y_vuelta():
    u = Usuario(nombre="A")
    r = Recordatorio(u.id, "Llamar", datetime(2026, 10, 23, 9, tzinfo=UTC))
    r.marcar_enviado()
    datos = recordatorio_a_dict(r)
    assert datos["estado"] == "enviado"
    json.dumps(datos)
    assert recordatorio_desde_dict(datos) == r


def test_recordatorio_mensaje_vacio_y_sin_zona():
    u = Usuario(nombre="A")
    datos = recordatorio_a_dict(Recordatorio(u.id, "x", datetime(2026, 10, 23, 9, tzinfo=UTC)))
    with pytest.raises(ValidationError):
        recordatorio_desde_dict({**datos, "mensaje": ""})
    with pytest.raises(ValidationError):
        recordatorio_desde_dict({**datos, "programado_para": "2026-10-23T09:00:00"})


def test_conversacion_y_mensaje_ida_y_vuelta():
    u = Usuario(nombre="A")
    c = Conversacion(u.id, "Planes")
    m = Mensaje(c.id, RolMensaje.ASISTENTE, "Hola", metadatos={"modelo": "x"})
    dc, dm = conversacion_a_dict(c), mensaje_a_dict(m)
    assert dm["rol"] == "asistente"
    json.dumps([dc, dm])
    assert conversacion_desde_dict(dc) == c
    assert mensaje_desde_dict(dm) == m


def test_mensaje_rol_desconocido():
    u = Usuario(nombre="A")
    c = Conversacion(u.id, "t")
    datos = mensaje_a_dict(Mensaje(c.id, RolMensaje.USUARIO, "hola"))
    datos["rol"] = "robot"
    with pytest.raises(ValidationError):
        mensaje_desde_dict(datos)


def test_usuario_rechaza_fecha_sin_zona():
    datos = usuario_a_dict(Usuario(nombre="A"))
    datos["fecha_creacion"] = "2026-10-23T09:00:00"
    with pytest.raises(ValidationError):
        usuario_desde_dict(datos)


def test_evento_rechaza_fechas_sin_zona():
    u = Usuario(nombre="A")
    e = Evento(u.id, "X", datetime(2026, 10, 23, 18, tzinfo=UTC), datetime(2026, 10, 23, 19, tzinfo=UTC))
    datos = evento_a_dict(e)
    assert evento_desde_dict(datos) == e
    with pytest.raises(ValidationError):
        evento_desde_dict({**datos, "comienza": "2026-10-23T18:00:00", "termina": "2026-10-23T19:00:00"})
