import json
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.domain.schedule import EstadoEvento, Evento
from app.domain.user import Usuario
from app.schemas.schedule import evento_a_dict, evento_desde_dict
from app.schemas.user import usuario_a_dict, usuario_desde_dict


def test_usuario_ida_y_vuelta():
    u = Usuario(nombre="Álvaro")
    u.cambiar_preferencia("tema", "oscuro")
    datos = usuario_a_dict(u)
    assert isinstance(datos["id"], str)
    assert isinstance(datos["fecha_creacion"], str)
    json.dumps(datos)
    assert usuario_desde_dict(datos) == u


def test_usuario_nombre_vacio():
    datos = usuario_a_dict(Usuario(nombre="A"))
    datos["nombre"] = "   "
    with pytest.raises(ValidationError):
        usuario_desde_dict(datos)


def test_usuario_zona_desconocida():
    datos = usuario_a_dict(Usuario(nombre="A"))
    datos["zona_horaria"] = "Marte/Olimpo"
    with pytest.raises(ValidationError):
        usuario_desde_dict(datos)


def test_usuario_falta_un_campo():
    datos = usuario_a_dict(Usuario(nombre="A"))
    del datos["id"]
    with pytest.raises(ValidationError):
        usuario_desde_dict(datos)


def test_evento_ida_y_vuelta():
    u = Usuario(nombre="A")
    e = Evento(u.id, "Gimnasio",
               datetime(2026, 10, 23, 18, tzinfo=UTC),
               datetime(2026, 10, 23, 19, tzinfo=UTC),
               ubicacion="Casa")
    e.cancelar()
    datos = evento_a_dict(e)
    assert datos["estado"] == "cancelado"
    json.dumps(datos)
    asi = evento_desde_dict(datos)
    assert asi == e
    assert asi.estado == EstadoEvento.CANCELADO


def test_evento_fechas_incoherentes():
    u = Usuario(nombre="A")
    e = Evento(u.id, "X",
               datetime(2026, 10, 23, 18, tzinfo=UTC),
               datetime(2026, 10, 23, 19, tzinfo=UTC))
    datos = evento_a_dict(e)
    datos["termina"] = "2026-10-23T17:00:00Z"
    with pytest.raises(ValidationError):
        evento_desde_dict(datos)


def test_evento_estado_desconocido():
    u = Usuario(nombre="A")
    e = Evento(u.id, "X",
               datetime(2026, 10, 23, 18, tzinfo=UTC),
               datetime(2026, 10, 23, 19, tzinfo=UTC))
    datos = evento_a_dict(e)
    datos["estado"] = "volando"
    with pytest.raises(ValidationError):
        evento_desde_dict(datos)
