"""Repositorio de objetivos sobre SQLite."""

import sqlite3
from datetime import date
from uuid import UUID

from app.domain.goal import EstadoObjetivo, Objetivo
from app.repositories.interfaces import RepositorioObjetivos


class RepositorioObjetivosSQLite(RepositorioObjetivos):
    """Guarda y lee objetivos en la tabla ``objetivos``.

    La fecha límite se guarda como texto ``AAAA-MM-DD`` (sin hora ni zona).
    No hace ``commit``: de eso se encarga quien abre la conexión.
    """

    def __init__(self, conexion: sqlite3.Connection) -> None:
        """Crea el repositorio sobre una conexión ya abierta."""
        self._conexion = conexion

    def guardar(self, objetivo: Objetivo) -> None:
        """Inserta o actualiza el objetivo.

        Raises:
            sqlite3.IntegrityError: Si el usuario del objetivo no existe o el
                progreso queda fuera de 0-100.
        """
        self._conexion.execute(
            """
            INSERT INTO objetivos (
                id, usuario_id, nombre, descripcion,
                fecha_limite, progreso, estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                usuario_id = excluded.usuario_id,
                nombre = excluded.nombre,
                descripcion = excluded.descripcion,
                fecha_limite = excluded.fecha_limite,
                progreso = excluded.progreso,
                estado = excluded.estado
            """,
            (
                str(objetivo.id),
                str(objetivo.usuario_id),
                objetivo.nombre,
                objetivo.descripcion,
                None if objetivo.fecha_limite is None else objetivo.fecha_limite.isoformat(),
                objetivo.progreso,
                objetivo.estado.value,
            ),
        )

    def obtener(self, objetivo_id: UUID) -> Objetivo | None:
        """Devuelve el objetivo con ese ``id`` o ``None`` si no existe."""
        fila = self._conexion.execute(
            "SELECT * FROM objetivos WHERE id = ?", (str(objetivo_id),)
        ).fetchone()
        return None if fila is None else _a_objetivo(fila)

    def listar_por_usuario(
        self, usuario_id: UUID, estado: EstadoObjetivo | None = None
    ) -> list[Objetivo]:
        """Devuelve los objetivos de un usuario, los más próximos a vencer primero.

        Los objetivos sin fecha límite van al final. Con ``estado`` se devuelven
        solo los que están en esa situación.
        """
        consulta = "SELECT * FROM objetivos WHERE usuario_id = ?"
        parametros: list[str] = [str(usuario_id)]
        if estado is not None:
            consulta += " AND estado = ?"
            parametros.append(estado.value)
        consulta += " ORDER BY fecha_limite IS NULL, fecha_limite, nombre, id"
        filas = self._conexion.execute(consulta, parametros).fetchall()
        return [_a_objetivo(fila) for fila in filas]

    def eliminar(self, objetivo_id: UUID) -> bool:
        """Elimina el objetivo. Devuelve ``True`` si existía."""
        cursor = self._conexion.execute(
            "DELETE FROM objetivos WHERE id = ?", (str(objetivo_id),)
        )
        return cursor.rowcount > 0


def _a_objetivo(fila: sqlite3.Row) -> Objetivo:
    """Convierte una fila de la tabla ``objetivos`` en un ``Objetivo``."""
    texto_fecha = fila["fecha_limite"]
    return Objetivo(
        id=UUID(fila["id"]),
        usuario_id=UUID(fila["usuario_id"]),
        nombre=fila["nombre"],
        descripcion=fila["descripcion"],
        fecha_limite=None if texto_fecha is None else date.fromisoformat(texto_fecha),
        progreso=fila["progreso"],
        estado=EstadoObjetivo(fila["estado"]),
    )
