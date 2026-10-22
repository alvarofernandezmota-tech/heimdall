from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from enum import StrEnum
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo


class EstadoEvento(StrEnum):
    PROGRAMADO = "programado"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"


@dataclass
class Evento:
    usuario_id: UUID
    titulo: str
    comienza: datetime
    termina: datetime
    id: UUID = field(default_factory=uuid4)
    descripcion: str | None = None
    ubicacion: str | None = None
    estado: EstadoEvento = EstadoEvento.PROGRAMADO

    def __post_init__(self) -> None:
        if self.termina <= self.comienza:
            raise ValueError(
                "La fecha de finalización debe ser posterior a la de inicio."
            )

    def cancelar(self) -> None:
        self.estado = EstadoEvento.CANCELADO

    def completar(self) -> None:
        self.estado = EstadoEvento.COMPLETADO

    def esta_activo(self) -> bool:
        return self.estado == EstadoEvento.PROGRAMADO

    def duracion(self) -> timedelta:
        return self.termina - self.comienza

    def se_solapa_con(self, otro: "Evento") -> bool:
        return self.comienza < otro.termina and otro.comienza < self.termina


class Horario:
    def __init__(self, eventos: list[Evento]) -> None:
        self.eventos = eventos

    def eventos_ordenados(self) -> list[Evento]:
        return sorted(self.eventos, key=lambda evento: evento.comienza)

    def eventos_del_dia(self, dia: date, zona: ZoneInfo) -> list[Evento]:
        del_dia = [
            e for e in self.eventos
            if e.esta_activo() and e.comienza.astimezone(zona).date() == dia
        ]
        return sorted(del_dia, key=lambda evento: evento.comienza)

    def hay_conflicto(self, nuevo: Evento) -> bool:
        return any(
            e.usuario_id == nuevo.usuario_id and e.esta_activo() and e.se_solapa_con(nuevo)
            for e in self.eventos
        )

    def celdas_del_dia(self, dia: date, zona: ZoneInfo, minutos: int = 15) -> list[bool]:
        inicio = datetime.combine(dia, time.min, tzinfo=zona).astimezone(UTC)
        fin = datetime.combine(dia + timedelta(days=1), time.min, tzinfo=zona).astimezone(UTC)
        paso = timedelta(minutes=minutos)
        total = int((fin - inicio) / paso)
        activos = [e for e in self.eventos if e.esta_activo()]
        celdas = []
        for i in range(total):
            desde = inicio + i * paso
            hasta = desde + paso
            celdas.append(any(e.comienza < hasta and desde < e.termina for e in activos))
        return celdas
