"""Repositorio de eventos sobre SQLite."""

import sqlite3
from datetime import date, datetime, time, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from app.database.fechas import a_texto, desde_texto
from app.domain.schedule import EstadoEvento, Evento
from app.repositories.interfaces import RepositorioEventos


class RepositorioEventosSQLite(RepositorioEventos):
    """Guarda y lee eventos en la tabla ``eventos``.

    No hace ``commit``: de eso se encarga quien abre la conexión.
    """

    def __init__(self, conexion: sqlite3.Connection) -> None:
        """Crea el repositorio sobre una conexión ya abierta."""
        self._conexion = conexion

    def guardar(self, evento: Evento) -> None:
        """Inserta o actualiza el evento.

        Raises:
            sqlite3.IntegrityError: Si el usuario del evento no existe.
        """
        self._conexion.execute(
            """
            INSERT INTO eventos (
                id, usuario_id, titulo, comienza, termina,
                descripcion, ubicacion, estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                usuario_id = excluded.usuario_id,
                titulo = excluded.titulo,
                comienza = excluded.comienza,
                termina = excluded.termina,
                descripcion = excluded.descripcion,
                ubicacion = excluded.ubicacion,
                estado = excluded.estado
            """,
            (
                str(evento.id),
                str(evento.usuario_id),
                evento.titulo,
                a_texto(evento.comienza),
                a_texto(evento.termina),
                evento.descripcion,
                evento.ubicacion,
                evento.estado.value,
            ),
        )

    def obtener(self, evento_id: UUID) -> Evento | None:
        """Devuelve el evento con ese ``id`` o ``None`` si no existe."""
        fila = self._conexion.execute(
            "SELECT * FROM eventos WHERE id = ?", (str(evento_id),)
        ).fetchone()
        return None if fila is None else _a_evento(fila)

    def listar_por_usuario(self, usuario_id: UUID) -> list[Evento]:
        """Devuelve todos los eventos de un usuario ordenados por hora de inicio."""
        filas = self._conexion.execute(
            "SELECT * FROM eventos WHERE usuario_id = ? ORDER BY comienza, id",
            (str(usuario_id),),
        ).fetchall()
        return [_a_evento(fila) for fila in filas]

    def listar_activos_del_dia(
        self, usuario_id: UUID, dia: date, zona: ZoneInfo
    ) -> list[Evento]:
        """Devuelve los eventos programados que empiezan en ``dia`` según ``zona``.

        Equivale a ``Horario.eventos_del_dia`` pero filtrando en la base de datos.
        El día va de las 00:00 locales (incluida) a las 00:00 del día siguiente
        (excluida), convertidas a UTC.
        """
        inicio = datetime.combine(dia, time.min, tzinfo=zona)
        fin = datetime.combine(dia + timedelta(days=1), time.min, tzinfo=zona)
        filas = self._conexion.execute(
            """
            SELECT * FROM eventos
            WHERE usuario_id = ?
              AND estado = ?
              AND comienza >= ?
              AND comienza < ?
            ORDER BY comienza, id
            """,
            (
                str(usuario_id),
                EstadoEvento.PROGRAMADO.value,
                a_texto(inicio),
                a_texto(fin),
            ),
        ).fetchall()
        return [_a_evento(fila) for fila in filas]

    def eliminar(self, evento_id: UUID) -> bool:
        """Elimina el evento. Devuelve ``True`` si existía."""
        cursor = self._conexion.execute(
            "DELETE FROM eventos WHERE id = ?", (str(evento_id),)
        )
        return cursor.rowcount > 0


def _a_evento(fila: sqlite3.Row) -> Evento:
    """Convierte una fila de la tabla ``eventos`` en un ``Evento``."""
    return Evento(
        id=UUID(fila["id"]),
        usuario_id=UUID(fila["usuario_id"]),
        titulo=fila["titulo"],
        comienza=desde_texto(fila["comienza"]),
        termina=desde_texto(fila["termina"]),
        descripcion=fila["descripcion"],
        ubicacion=fila["ubicacion"],
        estado=EstadoEvento(fila["estado"]),
    )
