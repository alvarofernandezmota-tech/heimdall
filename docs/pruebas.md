# Pruebas

Se ejecutan con `pytest -q` (configuración en `pytest.ini`, `pythonpath = .`).
Esperado hoy: 39 tests en verde.

| Archivo | Tests |
|---|---|
| test_user.py | 4 |
| test_message.py | 3 |
| test_schedule.py | 5 |
| test_habit.py | 5 |
| test_goal.py | 5 (uno parametrizado) |
| test_reminder.py | 3 |
| test_extras.py | 9 |
| test_relations.py | 5 |

Al subir los esquemas se añaden 7 en `test_schemas.py` (total 46).

## Convenciones
- Un archivo de test por módulo de dominio.
- Cada clase o función nueva entra con su test.
- Los datetimes de los tests llevan zona (UTC o Europe/Madrid).
- Se prueban casos de error con `pytest.raises`.
