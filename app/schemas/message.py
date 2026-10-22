from typing import Any
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.domain.message import Conversacion, Mensaje, RolMensaje


class ConversacionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usuario_id: UUID
    titulo: str = Field(min_length=1)
    fecha_creacion: AwareDatetime
    activa: bool = True


class MensajeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversacion_id: UUID
    rol: RolMensaje
    contenido: str
    fecha_creacion: AwareDatetime
    metadatos: dict[str, Any] = Field(default_factory=dict)


def conversacion_a_dict(conversacion: Conversacion) -> dict:
    return ConversacionSchema.model_validate(conversacion).model_dump(mode="json")


def conversacion_desde_dict(datos: dict) -> Conversacion:
    return Conversacion(**ConversacionSchema.model_validate(datos).model_dump())


def mensaje_a_dict(mensaje: Mensaje) -> dict:
    return MensajeSchema.model_validate(mensaje).model_dump(mode="json")


def mensaje_desde_dict(datos: dict) -> Mensaje:
    return Mensaje(**MensajeSchema.model_validate(datos).model_dump())
