from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.schedule import EstadoEvento, Evento


class EventoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usuario_id: UUID
    titulo: str = Field(min_length=1)
    comienza: datetime
    termina: datetime
    descripcion: str | None = None
    ubicacion: str | None = None
    estado: EstadoEvento = EstadoEvento.PROGRAMADO

    @model_validator(mode="after")
    def termina_despues_de_empezar(self):
        if self.termina <= self.comienza:
            raise ValueError("termina debe ser posterior a comienza.")
        return self


def evento_a_dict(evento: Evento) -> dict:
    return EventoSchema.model_validate(evento).model_dump(mode="json")


def evento_desde_dict(datos: dict) -> Evento:
    esquema = EventoSchema.model_validate(datos)
    return Evento(**esquema.model_dump())
