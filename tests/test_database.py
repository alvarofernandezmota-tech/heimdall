import sqlite3

import pytest

from app.database.connection import crear_conexion, sesion_sqlite
from app.database.esquema import (
    TABLAS_REQUERIDAS,
    aplicar_schema,
    esquema_completo,
    tablas_existentes,
)
from app.database.init_db import inicializar_base_datos

T0 = "2026-10-21T20:00:00.000000+00:00"
T1 = "2026-10-21T21:00:00.000000+00:00"


@pytest.fixture
def conexion():
    conexion = crear_conexion(":memory:")
    aplicar_schema(conexion)
    try:
        yield conexion
    finally:
        conexion.close()


def insertar_usuario(conexion, usuario_id="usuario-1", preferencias="{}"):
    conexion.execute(
        """
        INSERT INTO usuarios (
            id, nombre, idioma, zona_horaria,
            preferencias_json, fecha_creacion, activo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (usuario_id, "Álvaro", "es-ES", "Europe/Madrid", preferencias, T0, 1),
    )


def insertar_evento(conexion, comienza=T0, termina=T1):
    conexion.execute(
        """
        INSERT INTO eventos (id, usuario_id, titulo, comienza, termina, estado)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("evento-1", "usuario-1", "Reunión", comienza, termina, "programado"),
    )


def contar(conexion, tabla):
    return conexion.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]


def test_crea_todas_las_tablas(conexion):
    assert esquema_completo(conexion)
    assert TABLAS_REQUERIDAS.issubset(tablas_existentes(conexion))


def test_aplicar_schema_es_idempotente(conexion):
    aplicar_schema(conexion)
    aplicar_schema(conexion)
    assert esquema_completo(conexion)


def test_claves_foraneas_estan_activadas(conexion):
    assert conexion.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_no_permite_conversacion_sin_usuario(conexion):
    with pytest.raises(sqlite3.IntegrityError):
        conexion.execute(
            """
            INSERT INTO conversaciones (id, usuario_id, titulo, fecha_creacion, activa)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("conversacion-1", "usuario-inexistente", "Prueba", T0, 1),
        )


def test_eliminar_usuario_elimina_sus_datos(conexion):
    insertar_usuario(conexion)
    conexion.execute(
        """
        INSERT INTO conversaciones (id, usuario_id, titulo, fecha_creacion, activa)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("conversacion-1", "usuario-1", "Prueba", T0, 1),
    )
    conexion.execute(
        """
        INSERT INTO mensajes (
            id, conversacion_id, rol, contenido, fecha_creacion, metadatos_json
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("mensaje-1", "conversacion-1", "usuario", "Hola", T1, "{}"),
    )
    conexion.execute("DELETE FROM usuarios WHERE id = ?", ("usuario-1",))
    assert contar(conexion, "conversaciones") == 0
    assert contar(conexion, "mensajes") == 0


def test_rechaza_json_invalido(conexion):
    with pytest.raises(sqlite3.IntegrityError):
        insertar_usuario(conexion, preferencias="{json roto}")


def test_rechaza_enum_invalido(conexion):
    insertar_usuario(conexion)
    with pytest.raises(sqlite3.IntegrityError):
        conexion.execute(
            """
            INSERT INTO eventos (id, usuario_id, titulo, comienza, termina, estado)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("evento-1", "usuario-1", "Reunión", T0, T1, "desconocido"),
        )


def test_rechaza_evento_que_termina_antes_de_empezar(conexion):
    insertar_usuario(conexion)
    with pytest.raises(sqlite3.IntegrityError):
        insertar_evento(conexion, comienza=T1, termina=T0)


def test_rechaza_fecha_con_formato_no_canonico(conexion):
    insertar_usuario(conexion)
    with pytest.raises(sqlite3.IntegrityError):
        insertar_evento(conexion, comienza="2026-10-21T20:00:00Z", termina=T1)


def test_sesion_hace_commit(tmp_path):
    ruta = tmp_path / "commit.sqlite3"
    with sesion_sqlite(ruta) as conexion:
        aplicar_schema(conexion)
        insertar_usuario(conexion)
    conexion = crear_conexion(ruta)
    try:
        assert contar(conexion, "usuarios") == 1
    finally:
        conexion.close()


def test_sesion_hace_rollback(tmp_path):
    ruta = tmp_path / "rollback.sqlite3"
    with pytest.raises(RuntimeError):
        with sesion_sqlite(ruta) as conexion:
            aplicar_schema(conexion)
            insertar_usuario(conexion)
            raise RuntimeError("fallo simulado")
    conexion = crear_conexion(ruta)
    try:
        assert contar(conexion, "usuarios") == 0
    finally:
        conexion.close()


def test_inicializar_base_datos_crea_carpeta_y_tablas(tmp_path):
    ruta = tmp_path / "datos" / "nueva.sqlite3"
    inicializar_base_datos(ruta)
    assert ruta.exists()
    conexion = crear_conexion(ruta)
    try:
        assert esquema_completo(conexion)
    finally:
        conexion.close()
