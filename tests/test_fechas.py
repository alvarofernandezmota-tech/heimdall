from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest

from app.database.fechas import a_texto, desde_texto

MAD = ZoneInfo("Europe/Madrid")


def test_a_texto_convierte_a_utc_con_formato_fijo():
    fecha = datetime(2026, 10, 23, 20, 0, tzinfo=MAD)
    assert a_texto(fecha) == "2026-10-23T18:00:00.000000+00:00"


def test_a_texto_rechaza_fecha_sin_zona():
    with pytest.raises(ValueError):
        a_texto(datetime(2026, 10, 23, 20, 0))


def test_ida_y_vuelta_conserva_el_instante():
    fecha = datetime(2026, 10, 23, 20, 15, 30, 123456, tzinfo=MAD)
    assert desde_texto(a_texto(fecha)) == fecha


def test_el_orden_del_texto_es_el_orden_cronologico():
    fechas = [
        datetime(2026, 10, 23, 20, 0, tzinfo=MAD),
        datetime(2026, 10, 23, 18, 0, 0, 500000, tzinfo=UTC),
        datetime(2026, 10, 23, 18, 0, tzinfo=UTC),
        datetime(2026, 10, 24, 0, 30, tzinfo=MAD),
    ]
    por_texto = sorted(fechas, key=a_texto)
    assert por_texto == sorted(fechas)
