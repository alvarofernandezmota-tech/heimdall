from app.domain.user import Usuario


def test_valores_por_defecto():
    u = Usuario(nombre="Álvaro")
    assert u.idioma == "es-ES"
    assert u.zona_horaria == "Europe/Madrid"
    assert u.activo is True
    assert u.fecha_creacion.tzinfo is not None


def test_cambiar_preferencia():
    u = Usuario(nombre="Álvaro")
    u.cambiar_preferencia("tema", "oscuro")
    assert u.preferencias["tema"] == "oscuro"


def test_desactivar():
    u = Usuario(nombre="Álvaro")
    u.desactivar()
    assert u.activo is False


def test_ids_distintos():
    assert Usuario(nombre="A").id != Usuario(nombre="B").id
