from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.goal import EstadoObjetivo, Objetivo


class ObjetivoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usuario_id: UUID
    nombre: str = Field(min_length=1)
    descripcion: str | None = None
    fecha_limite: date | None = None
    progreso: float = Field(default=0.0, ge=0, le=100)
    estado: EstadoObjetivo = EstadoObjetivo.ACTIVO


def objetivo_a_dict(objetivo: Objetivo) -> dict:
    return ObjetivoSchema.model_validate(objetivo).model_dump(mode="json")


def objetivo_desde_dict(datos: dict) -> Objetivo:
    return Objetivo(**ObjetivoSchema.model_validate(datos).model_dump())
