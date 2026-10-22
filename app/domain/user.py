from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo


@dataclass
class Usuario:
    nombre: str
    id: UUID = field(default_factory=uuid4)
    idioma: str = "es-ES"
    zona_horaria: str = "Europe/Madrid"
    preferencias: dict[str, Any] = field(default_factory=dict)
    fecha_creacion: datetime = field(default_factory=lambda: datetime.now(UTC))
    activo: bool = True

    def cambiar_preferencia(self, clave: str, valor: Any) -> None:
        self.preferencias[clave] = valor

    def desactivar(self) -> None:
        self.activo = False

    def zona(self) -> ZoneInfo:
        return ZoneInfo(self.zona_horaria)
