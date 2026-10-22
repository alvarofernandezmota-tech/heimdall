# Base de datos (SQLite)

Archivos en `app/database/`:

| Archivo | Función |
|---|---|
| `schema.sql` | Tablas, restricciones e índices |
| `connection.py` | Conexión y sesión con commit/rollback |
| `esquema.py` | Aplicar y comprobar el esquema |
| `fechas.py` | Conversión de fechas a texto UTC |
| `init_db.py` | Comando `python -m app.database.init_db` |

La carpeta `migrations/` queda reservada para cambios futuros del esquema.

## Tablas
usuarios, conversaciones, mensajes, eventos, habitos, registros_habito,
objetivos, recordatorios. Al borrar un usuario se borran en cascada sus datos.

## Formatos
- UUID como texto; booleanos como 0/1; preferencias y metadatos como JSON.
- Fechas con hora: UTC con formato fijo `2026-10-23T18:00:00.000000+00:00`.
  Se generan siempre con `a_texto()`; la base rechaza cualquier otro formato.
- `fecha_limite` de objetivos: fecha simple `2026-12-31`.
- `registros_habito.completado` es informativo; los cálculos usan `valor`.
- `mensajes.contenido` puede estar vacío (llamadas a herramientas).

## Base local
El archivo `data/heimdall.sqlite3` no se sube a Git (ver `.gitignore`).

## Repositorios (`app/repositories/`)
- `interfaces.py`: operaciones que ofrece cada repositorio (clases abstractas).
- `sqlite_usuarios.py`, `sqlite_eventos.py` y `sqlite_habitos.py`: implementación sobre SQLite.
- `guardar` inserta o actualiza con `ON CONFLICT DO UPDATE`; nunca `INSERT OR REPLACE`,
  porque borraría la fila y, por la cascada, los datos que dependen de ella.
- Los repositorios no hacen `commit`; lo hace quien abre la conexión (`sesion_sqlite`).
