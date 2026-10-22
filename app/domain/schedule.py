from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4


class EstadoEvento(StrEnum):
    PROGRAMADO = "programado"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"


@dataclass
class Evento:
    usuario_id: UUID
    titulo: str
    comienza: datetime
    termina: datetime
    id: UUID = field(default_factory=uuid4)
    descripcion: str | None = None
    ubicacion: str | None = None
    estado: EstadoEvento = EstadoEvento.PROGRAMADO

    def __post_init__(self) -> None:
        if self.termina <= self.comienza:
            raise ValueError(
                "La fecha de finalización debe ser posterior a la de inicio."
            )

    def cancelar(self) -> None:
        self.estado = EstadoEvento.CANCELADO

    def completar(self) -> None:
        self.estado = EstadoEvento.COMPLETADO


class Horario:
    def __init__(self, eventos: list[Evento]) -> None:
        self.eventos = eventos

    def eventos_ordenados(self) -> list[Evento]:
        return sorted(self.eventos, key=lambda evento: evento.comienza)
