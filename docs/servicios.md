# Servicios de aplicación (`app/services/`)

Capa entre los agentes y los repositorios. Cada servicio es un caso de uso:
valida con los esquemas, aplica las reglas del dominio y guarda con los repositorios.

## Reglas
- Reciben los repositorios (interfaces) por el constructor; no conocen SQL.
- Lanzan errores propios (`app/services/errores.py`), no errores de base de datos.
- No hacen `commit`: lo hace quien abre la conexión (`sesion_sqlite`).

## Servicios
| Servicio | Casos de uso |
|---|---|
| `ServicioUsuarios` | registrar, obtener, cambiar zona horaria, desactivar |
| `ServicioAgenda` | crear, cancelar, completar y reprogramar eventos; eventos y celdas del día |

## Errores
| Error | Cuándo |
|---|---|
| `UsuarioNoEncontrado` | El usuario no existe |
| `EventoNoEncontrado` | El evento no existe |
| `ConflictoDeHorario` | El evento choca con otro activo del mismo usuario |

Los datos mal formados (nombre vacío, zona inexistente, fechas sin zona) siguen
lanzando `pydantic.ValidationError` o `ValueError`.

## Ejemplo de uso

    with sesion_sqlite() as conexion:
        usuarios = RepositorioUsuariosSQLite(conexion)
        eventos = RepositorioEventosSQLite(conexion)
        agenda = ServicioAgenda(usuarios, eventos)
        agenda.crear_evento(usuario_id, "Gimnasio", comienza, termina)
