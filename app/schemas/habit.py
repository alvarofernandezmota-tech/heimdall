from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

from app.domain.habit import FrecuenciaHabito, Habito, RegistroHabito


class HabitoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usuario_id: UUID
    nombre: str = Field(min_length=1)
    frecuencia: FrecuenciaHabito
    descripcion: str | None = None
    objetivo: float = Field(default=1.0, gt=0)
    unidad: str = "veces"
    activo: bool = True

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        return valor.strip()


class RegistroHabitoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    habito_id: UUID
    valor: float = Field(ge=0)
    completado: bool
    fecha: AwareDatetime
    notas: str | None = None


def habito_a_dict(habito: Habito) -> dict:
    return HabitoSchema.model_validate(habito).model_dump(mode="json")


def habito_desde_dict(datos: dict) -> Habito:
    return Habito(**HabitoSchema.model_validate(datos).model_dump())


def registro_a_dict(registro: RegistroHabito) -> dict:
    return RegistroHabitoSchema.model_validate(registro).model_dump(mode="json")


def registro_desde_dict(datos: dict) -> RegistroHabito:
    return RegistroHabito(**RegistroHabitoSchema.model_validate(datos).model_dump())
