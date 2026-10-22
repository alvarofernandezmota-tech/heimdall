from datetime import UTC, datetime

import pytest

from app.domain.errores import TransicionNoPermitida
from app.domain.reminder import EstadoRecordatorio, Recordatorio
from app.domain.schedule import EstadoEvento, Evento
from app.domain.user import Usuario


def hora(h):
    return datetime(2026, 10, 23, h, 0, tzinfo=UTC)


def un_evento(estado=EstadoEvento.PROGRAMADO):
    return Evento(Usuario(nombre="A").id, "Reunión", hora(10), hora(11), estado=estado)


def un_recordatorio(estado=EstadoRecordatorio.PENDIENTE):
    return Recordatorio(Usuario(nombre="A").id, "Llamar", hora(9), estado=estado)


@pytest.mark.parametrize(
    "accion,destino",
    [("cancelar", EstadoEvento.CANCELADO), ("completar", EstadoEvento.COMPLETADO)],
)
def test_un_evento_programado_puede_cambiar_de_estado(accion, destino):
    evento = un_evento()
    getattr(evento, accion)()
    assert evento.estado == destino


@pytest.mark.parametrize("accion", ["cancelar", "completar"])
@pytest.mark.parametrize("estado", [EstadoEvento.COMPLETADO, EstadoEvento.CANCELADO])
def test_un_evento_cerrado_no_puede_cambiar_de_estado(estado, accion):
    evento = un_evento(estado)
    with pytest.raises(TransicionNoPermitida):
        getattr(evento, accion)()
    assert evento.estado == estado


@pytest.mark.parametrize("estado", [EstadoEvento.COMPLETADO, EstadoEvento.CANCELADO])
def test_restablecer_devuelve_el_evento_a_programado(estado):
    evento = un_evento(estado)
    evento.restablecer()
    assert evento.estado == EstadoEvento.PROGRAMADO
    evento.cancelar()
    assert evento.estado == EstadoEvento.CANCELADO


def test_el_error_de_un_evento_indica_los_dos_estados():
    evento = un_evento(EstadoEvento.CANCELADO)
    with pytest.raises(TransicionNoPermitida) as info:
        evento.completar()
    assert "cancelado" in str(info.value)
    assert "completado" in str(info.value)
    assert info.value.actual == EstadoEvento.CANCELADO
    assert info.value.destino == EstadoEvento.COMPLETADO


def test_la_transicion_no_permitida_es_un_value_error():
    with pytest.raises(ValueError):
        un_evento(EstadoEvento.COMPLETADO).cancelar()


@pytest.mark.parametrize(
    "accion,destino",
    [("marcar_enviado", EstadoRecordatorio.ENVIADO), ("cancelar", EstadoRecordatorio.CANCELADO)],
)
def test_un_recordatorio_pendiente_puede_cambiar_de_estado(accion, destino):
    recordatorio = un_recordatorio()
    getattr(recordatorio, accion)()
    assert recordatorio.estado == destino


@pytest.mark.parametrize("accion", ["marcar_enviado", "cancelar"])
@pytest.mark.parametrize("estado", [EstadoRecordatorio.ENVIADO, EstadoRecordatorio.CANCELADO])
def test_un_recordatorio_cerrado_no_puede_cambiar_de_estado(estado, accion):
    recordatorio = un_recordatorio(estado)
    with pytest.raises(TransicionNoPermitida):
        getattr(recordatorio, accion)()
    assert recordatorio.estado == estado


@pytest.mark.parametrize("estado", [EstadoRecordatorio.ENVIADO, EstadoRecordatorio.CANCELADO])
def test_restablecer_devuelve_el_recordatorio_a_pendiente(estado):
    recordatorio = un_recordatorio(estado)
    recordatorio.restablecer()
    assert recordatorio.estado == EstadoRecordatorio.PENDIENTE
    recordatorio.marcar_enviado()
    assert recordatorio.estado == EstadoRecordatorio.ENVIADO
