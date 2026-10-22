"""Esquemas de validación y conversión de los hábitos y sus registros."""

from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

from app.domain.habit import FrecuenciaHabito, Habito, RegistroHabito


class HabitoSchema(BaseModel):
    """Forma válida de un hábito cuando entra o sale del sistema.

    El objetivo debe ser mayor que cero y el nombre no puede estar vacío.
    """

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
        """Rechaza nombres formados solo por espacios y recorta los extremos."""
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        return valor.strip()


class RegistroHabitoSchema(BaseModel):
    """Forma válida de un registro de hábito: valor no negativo y fecha con zona."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    habito_id: UUID
    valor: float = Field(ge=0)
    completado: bool
    fecha: AwareDatetime
    notas: str | None = None


def habito_a_dict(habito: Habito) -> dict:
    """Convierte un ``Habito`` en un diccionario listo para JSON."""
    return HabitoSchema.model_validate(habito).model_dump(mode="json")


def habito_desde_dict(datos: dict) -> Habito:
    """Crea un ``Habito`` a partir de un diccionario, validándolo antes.

    Raises:
        pydantic.ValidationError: Si algún dato no cumple las reglas del esquema.
    """
    return Habito(**HabitoSchema.model_validate(datos).model_dump())


def registro_a_dict(registro: RegistroHabito) -> dict:
    """Convierte un ``RegistroHabito`` en un diccionario listo para JSON."""
    return RegistroHabitoSchema.model_validate(registro).model_dump(mode="json")


def registro_desde_dict(datos: dict) -> RegistroHabito:
    """Crea un ``RegistroHabito`` a partir de un diccionario, validándolo antes.

    Raises:
        pydantic.ValidationError: Si algún dato no cumple las reglas del esquema.
    """
    return RegistroHabito(**RegistroHabitoSchema.model_validate(datos).model_dump())
