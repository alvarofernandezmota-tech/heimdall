from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from uuid import UUID, uuid4


class EstadoObjetivo(StrEnum):
    ACTIVO = "activo"
    COMPLETADO = "completado"
    PAUSADO = "pausado"
    CANCELADO = "cancelado"


@dataclass
class Objetivo:
    usuario_id: UUID
    nombre: str
    id: UUID = field(default_factory=uuid4)
    descripcion: str | None = None
    fecha_limite: date | None = None
    progreso: float = 0.0
    estado: EstadoObjetivo = EstadoObjetivo.ACTIVO

    def actualizar_progreso(self, progreso: float) -> None:
        if not 0 <= progreso <= 100:
            raise ValueError("El progreso debe estar entre 0 y 100.")
        self.progreso = progreso
        if progreso == 100:
            self.estado = EstadoObjetivo.COMPLETADO

    def pausar(self) -> None:
        self.estado = EstadoObjetivo.PAUSADO

    def cancelar(self) -> None:
        self.estado = EstadoObjetivo.CANCELADO

    def dias_restantes(self, hoy: date) -> int | None:
        if self.fecha_limite is None:
            return None
        return (self.fecha_limite - hoy).days

    def esta_vencido(self, hoy: date) -> bool:
        return (
            self.estado == EstadoObjetivo.ACTIVO
            and self.fecha_limite is not None
            and hoy > self.fecha_limite
        )
