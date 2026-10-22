"""Modelo de dominio de los hábitos y sus registros."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class FrecuenciaHabito(StrEnum):
    """Cada cuánto tiempo se espera cumplir un hábito."""

    DIARIA = "diaria"
    SEMANAL = "semanal"
    MENSUAL = "mensual"


@dataclass
class Habito:
    """Conducta que el usuario quiere repetir con una frecuencia dada.

    Attributes:
        usuario_id: Identificador del usuario propietario.
        nombre: Nombre del hábito, por ejemplo "Beber agua".
        frecuencia: Cada cuánto debe cumplirse.
        id: Identificador único (UUID), generado automáticamente.
        descripcion: Detalles opcionales.
        objetivo: Cantidad a alcanzar en cada periodo; debe ser mayor que cero.
        unidad: Unidad del objetivo ("veces", "litros", "minutos"...).
        activo: ``False`` si el hábito está desactivado.
    """

    usuario_id: UUID
    nombre: str
    frecuencia: FrecuenciaHabito
    id: UUID = field(default_factory=uuid4)
    descripcion: str | None = None
    objetivo: float = 1.0
    unidad: str = "veces"
    activo: bool = True

    def __post_init__(self) -> None:
        """Valida el hábito al crearlo.

        Raises:
            ValueError: Si ``objetivo`` no es mayor que cero.
        """
        if self.objetivo <= 0:
            raise ValueError("El objetivo del hábito debe ser mayor que cero.")

    def desactivar(self) -> None:
        """Marca el hábito como inactivo. Conserva sus registros."""
        self.activo = False

    def cumple(self, valor: float) -> bool:
        """Indica si una cantidad alcanza el objetivo del hábito."""
        return valor >= self.objetivo


@dataclass
class RegistroHabito:
    """Anotación de cuánto se ha hecho de un hábito en un momento dado.

    Attributes:
        habito_id: Identificador del hábito al que pertenece.
        valor: Cantidad realizada, en la unidad del hábito.
        completado: Marca informativa de si se dio por cumplido en ese momento.
            Los cálculos de ``relations.py`` usan ``valor``, no este campo.
        id: Identificador único (UUID), generado automáticamente.
        fecha: Momento del registro, con zona horaria UTC.
        notas: Comentario opcional.
    """

    habito_id: UUID
    valor: float
    completado: bool
    id: UUID = field(default_factory=uuid4)
    fecha: datetime = field(default_factory=lambda: datetime.now(UTC))
    notas: str | None = None
