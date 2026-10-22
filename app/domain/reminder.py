"""Modelo de dominio de los recordatorios."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4


class EstadoRecordatorio(StrEnum):
    """Situación de un recordatorio."""

    PENDIENTE = "pendiente"
    ENVIADO = "enviado"
    CANCELADO = "cancelado"


@dataclass
class Recordatorio:
    """Aviso programado para un momento concreto.

    Attributes:
        usuario_id: Identificador del usuario destinatario.
        mensaje: Texto que se mostrará al usuario.
        programado_para: Momento del aviso, con zona horaria.
        id: Identificador único (UUID), generado automáticamente.
        evento_id: Evento asociado, si el aviso es de un evento.
        habito_id: Hábito asociado, si el aviso es de un hábito.
        estado: Situación actual; por defecto ``PENDIENTE``.
    """

    usuario_id: UUID
    mensaje: str
    programado_para: datetime
    id: UUID = field(default_factory=uuid4)
    evento_id: UUID | None = None
    habito_id: UUID | None = None
    estado: EstadoRecordatorio = EstadoRecordatorio.PENDIENTE

    def marcar_enviado(self) -> None:
        """Pasa el recordatorio a ``ENVIADO``."""
        self.estado = EstadoRecordatorio.ENVIADO

    def cancelar(self) -> None:
        """Pasa el recordatorio a ``CANCELADO``."""
        self.estado = EstadoRecordatorio.CANCELADO

    def esta_vencido(self, ahora: datetime) -> bool:
        """Indica si sigue pendiente y su hora ya ha llegado o pasado.

        Args:
            ahora: Momento de referencia, con zona horaria.
        """
        return self.estado == EstadoRecordatorio.PENDIENTE and self.programado_para <= ahora
