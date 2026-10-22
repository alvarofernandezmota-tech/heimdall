# Pruebas

Se ejecutan con `pytest -q` (configuración en `pytest.ini`, `pythonpath = .`).
Esperado hoy: 62 tests en verde.

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
| test_schemas.py | 7 |
| test_schemas_resto.py | 15 |
| test_horario_usuarios.py | 1 |
| test_schemas_resto.py | 15 |
| test_horario_usuarios.py | 1 |


## Convenciones
- Un archivo de test por módulo de dominio.
- Cada clase o función nueva entra con su test.
- Los datetimes de los tests llevan zona (UTC o Europe/Madrid).
- Se prueban casos de error con `pytest.raises`.
