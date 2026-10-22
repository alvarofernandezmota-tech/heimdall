from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.domain.reminder import EstadoRecordatorio, Recordatorio


class RecordatorioSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usuario_id: UUID
    mensaje: str = Field(min_length=1)
    programado_para: AwareDatetime
    evento_id: UUID | None = None
    habito_id: UUID | None = None
    estado: EstadoRecordatorio = EstadoRecordatorio.PENDIENTE


def recordatorio_a_dict(recordatorio: Recordatorio) -> dict:
    return RecordatorioSchema.model_validate(recordatorio).model_dump(mode="json")


def recordatorio_desde_dict(datos: dict) -> Recordatorio:
    return Recordatorio(**RecordatorioSchema.model_validate(datos).model_dump())
