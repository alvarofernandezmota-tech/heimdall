from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class RolMensaje(StrEnum):
    USUARIO = "usuario"
    ASISTENTE = "asistente"
    SISTEMA = "sistema"
    HERRAMIENTA = "herramienta"


@dataclass
class Conversacion:
    usuario_id: UUID
    titulo: str
    id: UUID = field(default_factory=uuid4)
    fecha_creacion: datetime = field(default_factory=lambda: datetime.now(UTC))
    activa: bool = True


@dataclass
class Mensaje:
    conversacion_id: UUID
    rol: RolMensaje
    contenido: str
    id: UUID = field(default_factory=uuid4)
    fecha_creacion: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadatos: dict[str, Any] = field(default_factory=dict)

    def esta_vacio(self) -> bool:
        return not self.contenido.strip()
