"""Modelo de dominio del usuario."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo


@dataclass
class Usuario:
    """Persona que usa el asistente.

    Attributes:
        nombre: Nombre con el que el asistente se dirige al usuario.
        id: Identificador único (UUID), generado automáticamente.
        idioma: Código de idioma preferido, por ejemplo ``es-ES``.
        zona_horaria: Nombre IANA de la zona horaria, por ejemplo ``Europe/Madrid``.
            Sirve para mostrar fechas y para decidir a qué día pertenece cada hora.
        preferencias: Ajustes libres en formato clave-valor.
        fecha_creacion: Momento del alta, con zona horaria UTC.
        activo: ``False`` si el usuario ha sido desactivado.
    """

    nombre: str
    id: UUID = field(default_factory=uuid4)
    idioma: str = "es-ES"
    zona_horaria: str = "Europe/Madrid"
    preferencias: dict[str, Any] = field(default_factory=dict)
    fecha_creacion: datetime = field(default_factory=lambda: datetime.now(UTC))
    activo: bool = True

    def cambiar_preferencia(self, clave: str, valor: Any) -> None:
        """Guarda una preferencia; si la clave ya existe, la sobrescribe."""
        self.preferencias[clave] = valor

    def desactivar(self) -> None:
        """Marca al usuario como inactivo. No borra ningún dato."""
        self.activo = False

    def zona(self) -> ZoneInfo:
        """Devuelve la zona horaria del usuario como objeto ``ZoneInfo``.

        Raises:
            ZoneInfoNotFoundError: Si ``zona_horaria`` no es un nombre IANA válido.
        """
        return ZoneInfo(self.zona_horaria)
