from pathlib import Path


def reemplazar(ruta, viejo, nuevo):
    archivo = Path(ruta)
    texto = archivo.read_text(encoding="utf-8")
    if texto.count(viejo) != 1:
        raise SystemExit(f"NO APLICADO en {ruta}: no encuentro exactamente una vez:\n{viejo}")
    archivo.write_text(texto.replace(viejo, nuevo), encoding="utf-8")
    print(f"ok  {ruta}")


reemplazar(
    "app/domain/schedule.py",
    "            e.usuario_id == nuevo.usuario_id and e.esta_activo() and e.se_solapa_con(nuevo)\n",
    "            e.id != nuevo.id\n"
    "            and e.usuario_id == nuevo.usuario_id\n"
    "            and e.esta_activo()\n"
    "            and e.se_solapa_con(nuevo)\n",
)
reemplazar(
    "app/domain/schedule.py",
    "        Solo se comparan los eventos activos del mismo usuario.\n",
    "        Solo se comparan los eventos activos del mismo usuario y se ignora el propio\n"
    "        evento (mismo ``id``), de modo que editar un evento no choca consigo mismo.\n",
)

reemplazar("app/schemas/schedule.py",
           "from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator\n",
           "from pydantic import AwareDatetime, BaseModel, ConfigDict, model_validator\n")
reemplazar("app/schemas/schedule.py",
           "from app.domain.schedule import EstadoEvento, Evento\n",
           "from app.domain.schedule import EstadoEvento, Evento\nfrom app.schemas.comunes import TextoNoVacio\n")
reemplazar("app/schemas/schedule.py",
           "    titulo: str = Field(min_length=1)\n", "    titulo: TextoNoVacio\n")

reemplazar("app/schemas/goal.py",
           "from app.domain.goal import EstadoObjetivo, Objetivo\n",
           "from app.domain.goal import EstadoObjetivo, Objetivo\nfrom app.schemas.comunes import TextoNoVacio\n")
reemplazar("app/schemas/goal.py",
           "    nombre: str = Field(min_length=1)\n", "    nombre: TextoNoVacio\n")

reemplazar("app/schemas/reminder.py",
           "from pydantic import AwareDatetime, BaseModel, ConfigDict, Field\n",
           "from pydantic import AwareDatetime, BaseModel, ConfigDict\n")
reemplazar("app/schemas/reminder.py",
           "from app.domain.reminder import EstadoRecordatorio, Recordatorio\n",
           "from app.domain.reminder import EstadoRecordatorio, Recordatorio\nfrom app.schemas.comunes import TextoNoVacio\n")
reemplazar("app/schemas/reminder.py",
           "    mensaje: str = Field(min_length=1)\n", "    mensaje: TextoNoVacio\n")

reemplazar("app/schemas/message.py",
           "from app.domain.message import Conversacion, Mensaje, RolMensaje\n",
           "from app.domain.message import Conversacion, Mensaje, RolMensaje\nfrom app.schemas.comunes import TextoNoVacio\n")
reemplazar("app/schemas/message.py",
           "    titulo: str = Field(min_length=1)\n", "    titulo: TextoNoVacio\n")

reemplazar("docs/README.md", "Total: 62 tests en verde.", "Total: 73 tests en verde.")
reemplazar("docs/pruebas.md", "Esperado hoy: 62 tests en verde.", "Esperado hoy: 73 tests en verde.")
reemplazar("docs/pruebas.md", "| test_horario_usuarios.py | 1 |",
           "| test_horario_usuarios.py | 2 |\n| test_schemas_texto.py | 10 |")
reemplazar("README.md", "dominio y esquemas listos, 62 tests.", "dominio y esquemas listos, 73 tests.")
