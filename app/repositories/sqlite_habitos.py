"""Repositorios de hábitos y de sus registros sobre SQLite."""

import sqlite3
from datetime import datetime
from uuid import UUID

from app.database.fechas import a_texto, desde_texto
from app.domain.habit import FrecuenciaHabito, Habito, RegistroHabito
from app.repositories.interfaces import RepositorioHabitos, RepositorioRegistrosHabito


class RepositorioHabitosSQLite(RepositorioHabitos):
    """Guarda y lee hábitos en la tabla ``habitos``.

    No hace ``commit``: de eso se encarga quien abre la conexión.
    """

    def __init__(self, conexion: sqlite3.Connection) -> None:
        """Crea el repositorio sobre una conexión ya abierta."""
        self._conexion = conexion

    def guardar(self, habito: Habito) -> None:
        """Inserta o actualiza el hábito.

        Raises:
            sqlite3.IntegrityError: Si el usuario del hábito no existe.
        """
        self._conexion.execute(
            """
            INSERT INTO habitos (
                id, usuario_id, nombre, frecuencia,
                descripcion, objetivo, unidad, activo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                usuario_id = excluded.usuario_id,
                nombre = excluded.nombre,
                frecuencia = excluded.frecuencia,
                descripcion = excluded.descripcion,
                objetivo = excluded.objetivo,
                unidad = excluded.unidad,
                activo = excluded.activo
            """,
            (
                str(habito.id),
                str(habito.usuario_id),
                habito.nombre,
                habito.frecuencia.value,
                habito.descripcion,
                habito.objetivo,
                habito.unidad,
                int(habito.activo),
            ),
        )

    def obtener(self, habito_id: UUID) -> Habito | None:
        """Devuelve el hábito con ese ``id`` o ``None`` si no existe."""
        fila = self._conexion.execute(
            "SELECT * FROM habitos WHERE id = ?", (str(habito_id),)
        ).fetchone()
        return None if fila is None else _a_habito(fila)

    def listar_por_usuario(
        self, usuario_id: UUID, solo_activos: bool = False
    ) -> list[Habito]:
        """Devuelve los hábitos de un usuario ordenados por nombre.

        Con ``solo_activos=True`` se omiten los hábitos desactivados.
        """
        consulta = "SELECT * FROM habitos WHERE usuario_id = ?"
        if solo_activos:
            consulta += " AND activo = 1"
        consulta += " ORDER BY nombre, id"
        filas = self._conexion.execute(consulta, (str(usuario_id),)).fetchall()
        return [_a_habito(fila) for fila in filas]

    def eliminar(self, habito_id: UUID) -> bool:
        """Elimina el hábito y, en cascada, sus registros. ``True`` si existía."""
        cursor = self._conexion.execute(
            "DELETE FROM habitos WHERE id = ?", (str(habito_id),)
        )
        return cursor.rowcount > 0


class RepositorioRegistrosHabitoSQLite(RepositorioRegistrosHabito):
    """Guarda y lee registros de hábitos en la tabla ``registros_habito``.

    No hace ``commit``: de eso se encarga quien abre la conexión.
    """

    def __init__(self, conexion: sqlite3.Connection) -> None:
        """Crea el repositorio sobre una conexión ya abierta."""
        self._conexion = conexion

    def guardar(self, registro: RegistroHabito) -> None:
        """Inserta o actualiza el registro.

        Raises:
            sqlite3.IntegrityError: Si el hábito del registro no existe.
        """
        self._conexion.execute(
            """
            INSERT INTO registros_habito (
                id, habito_id, valor, completado, fecha, notas
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                habito_id = excluded.habito_id,
                valor = excluded.valor,
                completado = excluded.completado,
                fecha = excluded.fecha,
                notas = excluded.notas
            """,
            (
                str(registro.id),
                str(registro.habito_id),
                registro.valor,
                int(registro.completado),
                a_texto(registro.fecha),
                registro.notas,
            ),
        )

    def obtener(self, registro_id: UUID) -> RegistroHabito | None:
        """Devuelve el registro con ese ``id`` o ``None`` si no existe."""
        fila = self._conexion.execute(
            "SELECT * FROM registros_habito WHERE id = ?", (str(registro_id),)
        ).fetchone()
        return None if fila is None else _a_registro(fila)

    def listar_por_habito(self, habito_id: UUID) -> list[RegistroHabito]:
        """Devuelve todos los registros de un hábito, del más antiguo al más reciente."""
        filas = self._conexion.execute(
            "SELECT * FROM registros_habito WHERE habito_id = ? ORDER BY fecha, id",
            (str(habito_id),),
        ).fetchall()
        return [_a_registro(fila) for fila in filas]

    def listar_por_rango(
        self, habito_id: UUID, desde: datetime, hasta: datetime
    ) -> list[RegistroHabito]:
        """Devuelve los registros con ``desde <= fecha < hasta``, ordenados por fecha.

        Ambas fechas deben llevar zona horaria.
        """
        filas = self._conexion.execute(
            """
            SELECT * FROM registros_habito
            WHERE habito_id = ?
              AND fecha >= ?
              AND fecha < ?
            ORDER BY fecha, id
            """,
            (str(habito_id), a_texto(desde), a_texto(hasta)),
        ).fetchall()
        return [_a_registro(fila) for fila in filas]

    def eliminar(self, registro_id: UUID) -> bool:
        """Elimina el registro. Devuelve ``True`` si existía."""
        cursor = self._conexion.execute(
            "DELETE FROM registros_habito WHERE id = ?", (str(registro_id),)
        )
        return cursor.rowcount > 0


def _a_habito(fila: sqlite3.Row) -> Habito:
    """Convierte una fila de la tabla ``habitos`` en un ``Habito``."""
    return Habito(
        id=UUID(fila["id"]),
        usuario_id=UUID(fila["usuario_id"]),
        nombre=fila["nombre"],
        frecuencia=FrecuenciaHabito(fila["frecuencia"]),
        descripcion=fila["descripcion"],
        objetivo=fila["objetivo"],
        unidad=fila["unidad"],
        activo=bool(fila["activo"]),
    )


def _a_registro(fila: sqlite3.Row) -> RegistroHabito:
    """Convierte una fila de la tabla ``registros_habito`` en un ``RegistroHabito``."""
    return RegistroHabito(
        id=UUID(fila["id"]),
        habito_id=UUID(fila["habito_id"]),
        valor=fila["valor"],
        completado=bool(fila["completado"]),
        fecha=desde_texto(fila["fecha"]),
        notas=fila["notas"],
    )
