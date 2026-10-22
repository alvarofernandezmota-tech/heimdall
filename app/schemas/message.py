"""Esquemas de validación y conversión de las conversaciones y sus mensajes."""

from typing import Any
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.domain.message import Conversacion, Mensaje, RolMensaje
from app.schemas.comunes import TextoNoVacio


class ConversacionSchema(BaseModel):
    """Forma válida de una conversación: título con texto y fecha con zona horaria."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usuario_id: UUID
    titulo: TextoNoVacio
    fecha_creacion: AwareDatetime
    activa: bool = True


class MensajeSchema(BaseModel):
    """Forma válida de un mensaje.

    ``contenido`` puede ser una cadena vacía a propósito: un mensaje de herramienta
    o un asistente que solo invoca una herramienta puede no llevar texto.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversacion_id: UUID
    rol: RolMensaje
    contenido: str
    fecha_creacion: AwareDatetime
    metadatos: dict[str, Any] = Field(default_factory=dict)


def conversacion_a_dict(conversacion: Conversacion) -> dict:
    """Convierte una ``Conversacion`` en un diccionario listo para JSON."""
    return ConversacionSchema.model_validate(conversacion).model_dump(mode="json")


def conversacion_desde_dict(datos: dict) -> Conversacion:
    """Crea una ``Conversacion`` a partir de un diccionario, validándolo antes.

    Raises:
        pydantic.ValidationError: Si algún dato no cumple las reglas del esquema.
    """
    return Conversacion(**ConversacionSchema.model_validate(datos).model_dump())


def mensaje_a_dict(mensaje: Mensaje) -> dict:
    """Convierte un ``Mensaje`` en un diccionario listo para JSON.

    El rol se transforma en su texto (``usuario``, ``asistente``...).
    """
    return MensajeSchema.model_validate(mensaje).model_dump(mode="json")


def mensaje_desde_dict(datos: dict) -> Mensaje:
    """Crea un ``Mensaje`` a partir de un diccionario, validándolo antes.

    Raises:
        pydantic.ValidationError: Si algún dato no cumple las reglas del esquema.
    """
    return Mensaje(**MensajeSchema.model_validate(datos).model_dump())
