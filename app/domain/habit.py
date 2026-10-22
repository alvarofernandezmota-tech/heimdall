from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class FrecuenciaHabito(StrEnum):
    DIARIA = "diaria"
    SEMANAL = "semanal"
    MENSUAL = "mensual"


@dataclass
class Habito:
    usuario_id: UUID
    nombre: str
    frecuencia: FrecuenciaHabito
    id: UUID = field(default_factory=uuid4)
    descripcion: str | None = None
    objetivo: float = 1.0
    unidad: str = "veces"
    activo: bool = True

    def __post_init__(self) -> None:
        if self.objetivo <= 0:
            raise ValueError("El objetivo del hábito debe ser mayor que cero.")

    def desactivar(self) -> None:
        self.activo = False


@dataclass
class RegistroHabito:
    habito_id: UUID
    valor: float
    completado: bool
    id: UUID = field(default_factory=uuid4)
    fecha: datetime = field(default_factory=lambda: datetime.now(UTC))
    notas: str | None = None
