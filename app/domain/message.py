"""Modelo de dominio de las conversaciones y sus mensajes."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class RolMensaje(StrEnum):
    """Quién emite un mensaje dentro de una conversación."""

    USUARIO = "usuario"
    ASISTENTE = "asistente"
    SISTEMA = "sistema"
    HERRAMIENTA = "herramienta"


@dataclass
class Conversacion:
    """Hilo de mensajes entre un usuario y el asistente.

    Attributes:
        usuario_id: Identificador del usuario propietario.
        titulo: Título descriptivo de la conversación.
        id: Identificador único (UUID), generado automáticamente.
        fecha_creacion: Momento de creación, con zona horaria UTC.
        activa: ``False`` si la conversación está cerrada.
    """

    usuario_id: UUID
    titulo: str
    id: UUID = field(default_factory=uuid4)
    fecha_creacion: datetime = field(default_factory=lambda: datetime.now(UTC))
    activa: bool = True


@dataclass
class Mensaje:
    """Mensaje individual dentro de una conversación.

    Attributes:
        conversacion_id: Identificador de la conversación a la que pertenece.
        rol: Quién lo emite (usuario, asistente, sistema o herramienta).
        contenido: Texto del mensaje.
        id: Identificador único (UUID), generado automáticamente.
        fecha_creacion: Momento de creación, con zona horaria UTC.
        metadatos: Datos extra libres (modelo usado, herramienta llamada, etc.).
    """

    conversacion_id: UUID
    rol: RolMensaje
    contenido: str
    id: UUID = field(default_factory=uuid4)
    fecha_creacion: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadatos: dict[str, Any] = field(default_factory=dict)

    def esta_vacio(self) -> bool:
        """Indica si el contenido está vacío o solo tiene espacios en blanco."""
        return not self.contenido.strip()
