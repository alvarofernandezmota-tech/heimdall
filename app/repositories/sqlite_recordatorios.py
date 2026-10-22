"""Repositorio de recordatorios sobre SQLite."""

import sqlite3
from datetime import date, datetime, time, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from app.database.fechas import a_texto, desde_texto
from app.domain.reminder import EstadoRecordatorio, Recordatorio
from app.repositories.interfaces import RepositorioRecordatorios


class RepositorioRecordatoriosSQLite(RepositorioRecordatorios):
    """Guarda y lee recordatorios en la tabla ``recordatorios``.

    No hace ``commit``: de eso se encarga quien abre la conexión.
    """

    def __init__(self, conexion: sqlite3.Connection) -> None:
        """Crea el repositorio sobre una conexión ya abierta."""
        self._conexion = conexion

    def guardar(self, recordatorio: Recordatorio) -> None:
        """Inserta o actualiza el recordatorio.

        Raises:
            sqlite3.IntegrityError: Si el usuario, el evento o el hábito
                indicados no existen.
        """
        self._conexion.execute(
            """
            INSERT INTO recordatorios (
                id, usuario_id, mensaje, programado_para,
                evento_id, habito_id, estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                usuario_id = excluded.usuario_id,
                mensaje = excluded.mensaje,
                programado_para = excluded.programado_para,
                evento_id = excluded.evento_id,
                habito_id = excluded.habito_id,
                estado = excluded.estado
            """,
            (
                str(recordatorio.id),
                str(recordatorio.usuario_id),
                recordatorio.mensaje,
                a_texto(recordatorio.programado_para),
                None if recordatorio.evento_id is None else str(recordatorio.evento_id),
                None if recordatorio.habito_id is None else str(recordatorio.habito_id),
                recordatorio.estado.value,
            ),
        )

    def obtener(self, recordatorio_id: UUID) -> Recordatorio | None:
        """Devuelve el recordatorio con ese ``id`` o ``None`` si no existe."""
        fila = self._conexion.execute(
            "SELECT * FROM recordatorios WHERE id = ?", (str(recordatorio_id),)
        ).fetchone()
        return None if fila is None else _a_recordatorio(fila)

    def listar_por_usuario(self, usuario_id: UUID) -> list[Recordatorio]:
        """Devuelve los recordatorios de un usuario ordenados por hora programada."""
        filas = self._conexion.execute(
            "SELECT * FROM recordatorios WHERE usuario_id = ? ORDER BY programado_para, id",
            (str(usuario_id),),
        ).fetchall()
        return [_a_recordatorio(fila) for fila in filas]

    def listar_de_evento(self, evento_id: UUID) -> list[Recordatorio]:
        """Devuelve los recordatorios asociados a un evento, por hora programada."""
        filas = self._conexion.execute(
            "SELECT * FROM recordatorios WHERE evento_id = ? ORDER BY programado_para, id",
            (str(evento_id),),
        ).fetchall()
        return [_a_recordatorio(fila) for fila in filas]

    def listar_pendientes_del_dia(
        self, usuario_id: UUID, dia: date, zona: ZoneInfo
    ) -> list[Recordatorio]:
        """Devuelve los recordatorios pendientes de un usuario programados ese día.

        El día va de las 00:00 locales (incluida) a las 00:00 del día siguiente
        (excluida), según ``zona``.
        """
        inicio = datetime.combine(dia, time.min, tzinfo=zona)
        fin = datetime.combine(dia + timedelta(days=1), time.min, tzinfo=zona)
        filas = self._conexion.execute(
            """
            SELECT * FROM recordatorios
            WHERE usuario_id = ?
              AND estado = ?
              AND programado_para >= ?
              AND programado_para < ?
            ORDER BY programado_para, id
            """,
            (
                str(usuario_id),
                EstadoRecordatorio.PENDIENTE.value,
                a_texto(inicio),
                a_texto(fin),
            ),
        ).fetchall()
        return [_a_recordatorio(fila) for fila in filas]

    def listar_vencidos(self, ahora: datetime) -> list[Recordatorio]:
        """Devuelve los recordatorios pendientes de todos los usuarios ya vencidos.

        Coincide con ``Recordatorio.esta_vencido``: estado pendiente y
        ``programado_para <= ahora``. Salen del más antiguo al más reciente.
        """
        filas = self._conexion.execute(
            """
            SELECT * FROM recordatorios
            WHERE estado = ?
              AND programado_para <= ?
            ORDER BY programado_para, id
            """,
            (EstadoRecordatorio.PENDIENTE.value, a_texto(ahora)),
        ).fetchall()
        return [_a_recordatorio(fila) for fila in filas]

    def eliminar(self, recordatorio_id: UUID) -> bool:
        """Elimina el recordatorio. Devuelve ``True`` si existía."""
        cursor = self._conexion.execute(
            "DELETE FROM recordatorios WHERE id = ?", (str(recordatorio_id),)
        )
        return cursor.rowcount > 0


def _a_recordatorio(fila: sqlite3.Row) -> Recordatorio:
    """Convierte una fila de la tabla ``recordatorios`` en un ``Recordatorio``."""
    return Recordatorio(
        id=UUID(fila["id"]),
        usuario_id=UUID(fila["usuario_id"]),
        mensaje=fila["mensaje"],
        programado_para=desde_texto(fila["programado_para"]),
        evento_id=None if fila["evento_id"] is None else UUID(fila["evento_id"]),
        habito_id=None if fila["habito_id"] is None else UUID(fila["habito_id"]),
        estado=EstadoRecordatorio(fila["estado"]),
    )
