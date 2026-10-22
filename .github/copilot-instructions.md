# Instrucciones para Copilot — heimdall

Lee `docs/README.md` y los documentos que enlaza antes de revisar o proponer cambios.

- Responde y comenta en español.
- `app/domain` es puro: sin SQL, FastAPI ni librerías de IA.
- Fechas con zona horaria; guardar en UTC.
- Validaciones en `__post_init__`; datos externos con Pydantic en `app/schemas`.
- El modelo de lenguaje nunca accede a la base de datos.
- Cada cambio lleva su test; verifica con `pytest -q`.
- No añadir FastAPI, Telegram ni NBA hasta terminar dominio, esquemas, SQL, repositorios y servicios.
- Cambios pequeños: un archivo y su test por vez.
