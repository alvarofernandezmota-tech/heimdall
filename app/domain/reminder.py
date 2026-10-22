"""Modelo de dominio de los recordatorios."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.errores import TransicionNoPermitida


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
        """Pasa el recordatorio de ``PENDIENTE`` a ``ENVIADO``.

        Raises:
            TransicionNoPermitida: Si el recordatorio ya está enviado o cancelado.
        """
        self._cambiar_desde_pendiente(EstadoRecordatorio.ENVIADO)

    def cancelar(self) -> None:
        """Pasa el recordatorio de ``PENDIENTE`` a ``CANCELADO``.

        Raises:
            TransicionNoPermitida: Si el recordatorio ya está enviado o cancelado.
        """
        self._cambiar_desde_pendiente(EstadoRecordatorio.CANCELADO)

    def restablecer(self) -> None:
        """Devuelve el recordatorio a ``PENDIENTE`` desde cualquier estado.

        Es la corrección manual explícita de un cambio hecho por error; los
        métodos normales no permiten volver atrás.
        """
        self.estado = EstadoRecordatorio.PENDIENTE

    def _cambiar_desde_pendiente(self, destino: EstadoRecordatorio) -> None:
        """Cambia el estado solo si el recordatorio está pendiente."""
        if self.estado != EstadoRecordatorio.PENDIENTE:
            raise TransicionNoPermitida(self.estado, destino)
        self.estado = destino

    def esta_vencido(self, ahora: datetime) -> bool:
        """Indica si sigue pendiente y su hora ya ha llegado o pasado.

        Args:
            ahora: Momento de referencia, con zona horaria.
        """
        return self.estado == EstadoRecordatorio.PENDIENTE and self.programado_para <= ahora
