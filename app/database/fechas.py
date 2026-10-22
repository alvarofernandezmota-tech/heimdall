"""Conversión de fechas a texto para guardarlas en SQLite.

Las fechas con hora se guardan siempre en UTC y con un formato de ancho fijo
(``2026-10-23T18:00:00.000000+00:00``). Así, comparar o ordenar los textos
equivale a comparar o ordenar los instantes.
"""

from datetime import UTC, datetime


def a_texto(fecha: datetime) -> str:
    """Convierte una fecha con zona horaria en el texto UTC que guarda SQLite.

    Raises:
        ValueError: Si la fecha no tiene zona horaria.
    """
    if fecha.tzinfo is None or fecha.utcoffset() is None:
        raise ValueError("La fecha debe tener zona horaria.")
    return fecha.astimezone(UTC).isoformat(timespec="microseconds")


def desde_texto(texto: str) -> datetime:
    """Convierte un texto guardado en SQLite en una fecha con zona horaria UTC.

    Raises:
        ValueError: Si el texto no es una fecha ISO válida o no lleva zona horaria.
    """
    fecha = datetime.fromisoformat(texto)
    if fecha.tzinfo is None:
        raise ValueError("El texto debe incluir zona horaria.")
    return fecha.astimezone(UTC)
