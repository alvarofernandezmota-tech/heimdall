import pytest

from app.domain.habit import FrecuenciaHabito, Habito, RegistroHabito
from app.domain.user import Usuario


def test_habito_valores_por_defecto():
    u = Usuario(nombre="Álvaro")
    h = Habito(u.id, "Beber agua", FrecuenciaHabito.DIARIA)
    assert h.objetivo == 1.0
    assert h.unidad == "veces"
    assert h.activo is True


def test_habito_con_objetivo_y_unidad():
    u = Usuario(nombre="Álvaro")
    h = Habito(u.id, "Beber agua", FrecuenciaHabito.DIARIA, objetivo=2.0, unidad="litros")
    assert h.objetivo == 2.0
    assert h.unidad == "litros"


def test_habito_objetivo_no_valido():
    u = Usuario(nombre="Álvaro")
    with pytest.raises(ValueError):
        Habito(u.id, "Mal", FrecuenciaHabito.DIARIA, objetivo=0)


def test_desactivar_habito():
    u = Usuario(nombre="Álvaro")
    h = Habito(u.id, "Leer", FrecuenciaHabito.DIARIA)
    h.desactivar()
    assert h.activo is False


def test_registro_enlaza_con_habito():
    u = Usuario(nombre="Álvaro")
    h = Habito(u.id, "Correr", FrecuenciaHabito.SEMANAL, objetivo=3)
    r = RegistroHabito(habito_id=h.id, valor=2, completado=False)
    assert r.habito_id == h.id
    assert r.completado is False
    assert r.fecha.tzinfo is not None
