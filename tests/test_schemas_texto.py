from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.domain.goal import Objetivo
from app.domain.message import Conversacion, Mensaje, RolMensaje
from app.domain.reminder import Recordatorio
from app.domain.schedule import Evento
from app.domain.user import Usuario
from app.schemas.goal import objetivo_a_dict, objetivo_desde_dict
from app.schemas.message import (
    conversacion_a_dict,
    conversacion_desde_dict,
    mensaje_a_dict,
    mensaje_desde_dict,
)
from app.schemas.reminder import recordatorio_a_dict, recordatorio_desde_dict
from app.schemas.schedule import evento_a_dict, evento_desde_dict

VACIOS = ["", "   "]


def hora(h):
    return datetime(2026, 10, 23, h, tzinfo=UTC)


@pytest.mark.parametrize("texto", VACIOS)
def test_evento_rechaza_titulo_vacio(texto):
    u = Usuario(nombre="A")
    datos = evento_a_dict(Evento(u.id, "X", hora(10), hora(11)))
    with pytest.raises(ValidationError):
        evento_desde_dict({**datos, "titulo": texto})


@pytest.mark.parametrize("texto", VACIOS)
def test_objetivo_rechaza_nombre_vacio(texto):
    u = Usuario(nombre="A")
    datos = objetivo_a_dict(Objetivo(u.id, "X"))
    with pytest.raises(ValidationError):
        objetivo_desde_dict({**datos, "nombre": texto})


@pytest.mark.parametrize("texto", VACIOS)
def test_recordatorio_rechaza_mensaje_vacio(texto):
    u = Usuario(nombre="A")
    datos = recordatorio_a_dict(Recordatorio(u.id, "x", hora(9)))
    with pytest.raises(ValidationError):
        recordatorio_desde_dict({**datos, "mensaje": texto})


@pytest.mark.parametrize("texto", VACIOS)
def test_conversacion_rechaza_titulo_vacio(texto):
    u = Usuario(nombre="A")
    datos = conversacion_a_dict(Conversacion(u.id, "t"))
    with pytest.raises(ValidationError):
        conversacion_desde_dict({**datos, "titulo": texto})


def test_los_textos_obligatorios_se_recortan():
    u = Usuario(nombre="A")
    datos = objetivo_a_dict(Objetivo(u.id, "X"))
    assert objetivo_desde_dict({**datos, "nombre": "  Aprender Python  "}).nombre == "Aprender Python"


def test_mensaje_con_contenido_vacio_se_admite():
    # Un mensaje de herramienta o un asistente que solo llama a una herramienta
    # puede venir sin texto; historial_para_modelo ya descarta los vacíos.
    c = Conversacion(Usuario(nombre="A").id, "t")
    m = Mensaje(c.id, RolMensaje.ASISTENTE, "")
    assert mensaje_desde_dict(mensaje_a_dict(m)) == m
