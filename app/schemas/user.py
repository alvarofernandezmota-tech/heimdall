from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

from app.domain.user import Usuario


class UsuarioSchema(BaseModel):
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
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        return valor.strip()

    @field_validator("zona_horaria")
    @classmethod
    def zona_valida(cls, valor: str) -> str:
        try:
            ZoneInfo(valor)
        except (ZoneInfoNotFoundError, ValueError) as error:
            raise ValueError(f"Zona horaria desconocida: {valor}") from error
        return valor


def usuario_a_dict(usuario: Usuario) -> dict:
    return UsuarioSchema.model_validate(usuario).model_dump(mode="json")


def usuario_desde_dict(datos: dict) -> Usuario:
    esquema = UsuarioSchema.model_validate(datos)
    return Usuario(**esquema.model_dump())
