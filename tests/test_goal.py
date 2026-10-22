from datetime import date

import pytest

from app.domain.goal import EstadoObjetivo, Objetivo
from app.domain.user import Usuario


def test_objetivo_por_defecto():
    u = Usuario(nombre="Álvaro")
    o = Objetivo(u.id, "Aprender Python")
    assert o.progreso == 0.0
    assert o.estado == EstadoObjetivo.ACTIVO


def test_actualizar_progreso():
    u = Usuario(nombre="Álvaro")
    o = Objetivo(u.id, "Aprender Python", fecha_limite=date(2026, 12, 31))
    o.actualizar_progreso(40)
    assert o.progreso == 40
    assert o.estado == EstadoObjetivo.ACTIVO


def test_progreso_100_completa():
    u = Usuario(nombre="Álvaro")
    o = Objetivo(u.id, "Aprender Python")
    o.actualizar_progreso(100)
    assert o.estado == EstadoObjetivo.COMPLETADO


@pytest.mark.parametrize("valor", [-1, 101])
def test_progreso_fuera_de_rango(valor):
    u = Usuario(nombre="Álvaro")
    o = Objetivo(u.id, "Aprender Python")
    with pytest.raises(ValueError):
        o.actualizar_progreso(valor)
