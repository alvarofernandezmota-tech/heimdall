from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4


class EstadoRecordatorio(StrEnum):
    PENDIENTE = "pendiente"
    ENVIADO = "enviado"
    CANCELADO = "cancelado"


@dataclass
class Recordatorio:
    usuario_id: UUID
    mensaje: str
    programado_para: datetime
    id: UUID = field(default_factory=uuid4)
    evento_id: UUID | None = None
    habito_id: UUID | None = None
    estado: EstadoRecordatorio = EstadoRecordatorio.PENDIENTE

    def marcar_enviado(self) -> None:
        self.estado = EstadoRecordatorio.ENVIADO

    def cancelar(self) -> None:
        self.estado = EstadoRecordatorio.CANCELADO

    def esta_vencido(self, ahora: datetime) -> bool:
        return self.estado == EstadoRecordatorio.PENDIENTE and self.programado_para <= ahora
