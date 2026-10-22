"""Comando para inicializar la base de datos local.

Uso: ``python -m app.database.init_db [--database RUTA]``
"""

from argparse import ArgumentParser
from pathlib import Path

from app.database.connection import DEFAULT_DATABASE_PATH, crear_conexion
from app.database.esquema import aplicar_schema, esquema_completo


def inicializar_base_datos(ruta: str | Path = DEFAULT_DATABASE_PATH) -> None:
    """Crea o actualiza la base de datos indicada.

    Raises:
        RuntimeError: Si tras aplicar el esquema falta alguna tabla.
    """
    conexion = crear_conexion(ruta)
    try:
        aplicar_schema(conexion)
        if not esquema_completo(conexion):
            raise RuntimeError("El esquema SQLite no quedó completamente creado.")
    finally:
        conexion.close()


def main() -> None:
    """Punto de entrada de la línea de comandos."""
    parser = ArgumentParser(description="Inicializa la base de datos de Heimdall.")
    parser.add_argument(
        "--database",
        default=str(DEFAULT_DATABASE_PATH),
        help="Ruta del archivo SQLite.",
    )
    argumentos = parser.parse_args()
    inicializar_base_datos(argumentos.database)
    print("Base de datos inicializada:", argumentos.database)


if __name__ == "__main__":
    main()
