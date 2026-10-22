"""Esquema de validación y conversión de los recordatorios."""

from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict

from app.domain.reminder import EstadoRecordatorio, Recordatorio
from app.schemas.comunes import TextoNoVacio


class RecordatorioSchema(BaseModel):
    """Forma válida de un recordatorio cuando entra o sale del sistema.

    El mensaje debe tener texto y la hora programada, zona horaria.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usuario_id: UUID
    mensaje: TextoNoVacio
    programado_para: AwareDatetime
    evento_id: UUID | None = None
    habito_id: UUID | None = None
    estado: EstadoRecordatorio = EstadoRecordatorio.PENDIENTE


def recordatorio_a_dict(recordatorio: Recordatorio) -> dict:
    """Convierte un ``Recordatorio`` en un diccionario listo para JSON."""
    return RecordatorioSchema.model_validate(recordatorio).model_dump(mode="json")


def recordatorio_desde_dict(datos: dict) -> Recordatorio:
    """Crea un ``Recordatorio`` a partir de un diccionario, validándolo antes.

    Raises:
        pydantic.ValidationError: Si algún dato no cumple las reglas del esquema.
    """
    return Recordatorio(**RecordatorioSchema.model_validate(datos).model_dump())
