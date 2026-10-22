"""Creación y comprobación del esquema SQLite."""

import sqlite3
from importlib.resources import files

TABLAS_REQUERIDAS = {
    "usuarios",
    "conversaciones",
    "mensajes",
    "eventos",
    "habitos",
    "registros_habito",
    "objetivos",
    "recordatorios",
}


def cargar_schema() -> str:
    """Devuelve el contenido del archivo ``schema.sql``."""
    return files("app.database").joinpath("schema.sql").read_text(encoding="utf-8")


def aplicar_schema(conexion: sqlite3.Connection) -> None:
    """Crea las tablas e índices que todavía no existan.

    Se puede ejecutar varias veces sin efectos secundarios.
    """
    conexion.executescript(cargar_schema())
    conexion.commit()


def tablas_existentes(conexion: sqlite3.Connection) -> set[str]:
    """Devuelve los nombres de las tablas de usuario presentes en la base."""
    filas = conexion.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        """
    ).fetchall()
    return {fila["name"] for fila in filas}


def esquema_completo(conexion: sqlite3.Connection) -> bool:
    """Indica si existen todas las tablas de ``TABLAS_REQUERIDAS``."""
    return TABLAS_REQUERIDAS.issubset(tablas_existentes(conexion))
