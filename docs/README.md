# heimdall — documentación

Chatbot-agente en Python con dos áreas: asistente personal (horarios, hábitos,
objetivos, recordatorios) y módulo NBA. Principio central: el modelo de
lenguaje interpreta y explica; Python calcula; SQLite conserva los datos.

## Índice
| Documento | Contenido |
|---|---|
| [arquitectura.md](arquitectura.md) | Capas, flujo de una petición, reglas |
| [dominio.md](dominio.md) | Clases, campos y métodos |
| [decisiones.md](decisiones.md) | Decisiones de diseño y motivos |
| [base-de-datos.md](base-de-datos.md) | Tablas SQLite y formatos |
| [pruebas.md](pruebas.md) | Tests y convenciones |
| [hoja-de-ruta.md](hoja-de-ruta.md) | Qué falta y qué revisar |

## Estado (22 oct 2026)
- Dominio y relaciones: hecho, 39 tests en verde.
- Esquemas Pydantic: hechos para todas las clases. Total: 120 tests en verde.
- Base de datos SQLite (esquema y conexión): hecha.
- Repositorios: Usuario, Evento y Hábito (con registros) hechos; faltan los demás.
- Servicios, agentes y chatbot: pendientes.
- `app/domain/nba/` está vacío a propósito.

## Ejecutar
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```
Requiere Python 3.11 o superior (`StrEnum`, `datetime.UTC`). Probado con 3.14.
