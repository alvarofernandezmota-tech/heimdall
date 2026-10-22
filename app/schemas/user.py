"""Esquema de validación y conversión del usuario."""

from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

from app.domain.user import Usuario


class UsuarioSchema(BaseModel):
    """Forma válida de un usuario cuando entra o sale del sistema (JSON, API, base de datos).

    Valida los datos antes de crear un ``Usuario`` de dominio. ``from_attributes``
    permite construir el esquema directamente a partir de un objeto ``Usuario``.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nombre: str = Field(min_length=1)
    idioma: str = "es-ES"
    zona_horaria: str = "Europe/Madrid"
    preferencias: dict[str, Any] = Field(default_factory=dict)
    fecha_creacion: AwareDatetime
    activo: bool = True

    @field_validator("nombre")
    @classmethod
    def nombre_sin_espacios_vacios(cls, valor: str) -> str:
        """Rechaza nombres formados solo por espacios y recorta los extremos."""
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        return valor.strip()

    @field_validator("zona_horaria")
    @classmethod
    def zona_valida(cls, valor: str) -> str:
        """Comprueba que la zona horaria sea un nombre IANA reconocido."""
        try:
            ZoneInfo(valor)
        except (ZoneInfoNotFoundError, ValueError) as error:
            raise ValueError(f"Zona horaria desconocida: {valor}") from error
        return valor


def usuario_a_dict(usuario: Usuario) -> dict:
    """Convierte un ``Usuario`` en un diccionario listo para JSON.

    Los UUID y las fechas se transforman en texto.
    """
    return UsuarioSchema.model_validate(usuario).model_dump(mode="json")


def usuario_desde_dict(datos: dict) -> Usuario:
    """Crea un ``Usuario`` a partir de un diccionario, validándolo antes.

    Raises:
        pydantic.ValidationError: Si algún dato no cumple las reglas del esquema.
    """
    esquema = UsuarioSchema.model_validate(datos)
    return Usuario(**esquema.model_dump())
