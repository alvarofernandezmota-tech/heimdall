"""Repositorio de usuarios sobre SQLite."""

import json
import sqlite3
from uuid import UUID

from app.database.fechas import a_texto, desde_texto
from app.domain.user import Usuario
from app.repositories.interfaces import RepositorioUsuarios


class RepositorioUsuariosSQLite(RepositorioUsuarios):
    """Guarda y lee usuarios en la tabla ``usuarios``.

    No hace ``commit``: de eso se encarga quien abre la conexión, por ejemplo
    ``sesion_sqlite``, para poder agrupar varias operaciones en una transacción.
    """

    def __init__(self, conexion: sqlite3.Connection) -> None:
        """Crea el repositorio sobre una conexión ya abierta."""
        self._conexion = conexion

    def guardar(self, usuario: Usuario) -> None:
        """Inserta o actualiza el usuario.

        Usa ``ON CONFLICT DO UPDATE`` y no ``INSERT OR REPLACE``: este último
        borraría la fila y, por la cascada, también todos los datos del usuario.
        """
        self._conexion.execute(
            """
            INSERT INTO usuarios (
                id, nombre, idioma, zona_horaria,
                preferencias_json, fecha_creacion, activo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                nombre = excluded.nombre,
                idioma = excluded.idioma,
                zona_horaria = excluded.zona_horaria,
                preferencias_json = excluded.preferencias_json,
                fecha_creacion = excluded.fecha_creacion,
                activo = excluded.activo
            """,
            (
                str(usuario.id),
                usuario.nombre,
                usuario.idioma,
                usuario.zona_horaria,
                json.dumps(usuario.preferencias, ensure_ascii=False),
                a_texto(usuario.fecha_creacion),
                int(usuario.activo),
            ),
        )

    def obtener(self, usuario_id: UUID) -> Usuario | None:
        """Devuelve el usuario con ese ``id`` o ``None`` si no existe."""
        fila = self._conexion.execute(
            "SELECT * FROM usuarios WHERE id = ?", (str(usuario_id),)
        ).fetchone()
        return None if fila is None else _a_usuario(fila)

    def listar(self) -> list[Usuario]:
        """Devuelve todos los usuarios, del más antiguo al más reciente."""
        filas = self._conexion.execute(
            "SELECT * FROM usuarios ORDER BY fecha_creacion, id"
        ).fetchall()
        return [_a_usuario(fila) for fila in filas]

    def eliminar(self, usuario_id: UUID) -> bool:
        """Elimina el usuario y, en cascada, sus datos. ``True`` si existía."""
        cursor = self._conexion.execute(
            "DELETE FROM usuarios WHERE id = ?", (str(usuario_id),)
        )
        return cursor.rowcount > 0


def _a_usuario(fila: sqlite3.Row) -> Usuario:
    """Convierte una fila de la tabla ``usuarios`` en un ``Usuario``."""
    return Usuario(
        id=UUID(fila["id"]),
        nombre=fila["nombre"],
        idioma=fila["idioma"],
        zona_horaria=fila["zona_horaria"],
        preferencias=json.loads(fila["preferencias_json"]),
        fecha_creacion=desde_texto(fila["fecha_creacion"]),
        activo=bool(fila["activo"]),
    )
