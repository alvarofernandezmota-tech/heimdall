from app.domain.message import Conversacion, Mensaje, RolMensaje
from app.domain.user import Usuario


def test_conversacion_activa_por_defecto():
    u = Usuario(nombre="Álvaro")
    c = Conversacion(usuario_id=u.id, titulo="Primera")
    assert c.activa is True
    assert c.usuario_id == u.id


def test_mensaje_enlaza_con_conversacion():
    u = Usuario(nombre="Álvaro")
    c = Conversacion(usuario_id=u.id, titulo="Primera")
    m = Mensaje(conversacion_id=c.id, rol=RolMensaje.USUARIO, contenido="Hola")
    assert m.conversacion_id == c.id
    assert m.rol == "usuario"


def test_mensaje_vacio():
    c = Conversacion(usuario_id=Usuario(nombre="A").id, titulo="t")
    assert Mensaje(c.id, RolMensaje.USUARIO, "   ").esta_vacio() is True
    assert Mensaje(c.id, RolMensaje.USUARIO, "hola").esta_vacio() is False
