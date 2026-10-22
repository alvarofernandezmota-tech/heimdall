"""Esquema de validación y conversión de los objetivos."""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.goal import EstadoObjetivo, Objetivo
from app.schemas.comunes import TextoNoVacio


class ObjetivoSchema(BaseModel):
    """Forma válida de un objetivo cuando entra o sale del sistema.

    El nombre debe tener texto y el progreso estar entre 0 y 100.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usuario_id: UUID
    nombre: TextoNoVacio
    descripcion: str | None = None
    fecha_limite: date | None = None
    progreso: float = Field(default=0.0, ge=0, le=100)
    estado: EstadoObjetivo = EstadoObjetivo.ACTIVO


def objetivo_a_dict(objetivo: Objetivo) -> dict:
    """Convierte un ``Objetivo`` en un diccionario listo para JSON.

    La fecha límite se transforma en texto con formato ISO (``2026-12-31``).
    """
    return ObjetivoSchema.model_validate(objetivo).model_dump(mode="json")


def objetivo_desde_dict(datos: dict) -> Objetivo:
    """Crea un ``Objetivo`` a partir de un diccionario, validándolo antes.

    Raises:
        pydantic.ValidationError: Si algún dato no cumple las reglas del esquema.
    """
    return Objetivo(**ObjetivoSchema.model_validate(datos).model_dump())
