"""Funciones que relacionan entre sí las clases del dominio.

Son funciones puras: reciben listas de objetos y devuelven resultados sin
modificar nada ni acceder a bases de datos. Los objetos se enlazan por
identificador (``usuario_id``, ``habito_id``, ``conversacion_id``...).
"""

from collections import defaultdict
from datetime import date, timedelta

from app.domain.habit import FrecuenciaHabito, Habito, RegistroHabito
from app.domain.message import Conversacion, Mensaje, RolMensaje
from app.domain.reminder import EstadoRecordatorio, Recordatorio
from app.domain.schedule import Evento, Horario
from app.domain.user import Usuario

# Traducción de nuestros roles a los nombres que esperan los modelos de lenguaje.
ROLES_MODELO = {
    RolMensaje.USUARIO: "user",
    RolMensaje.ASISTENTE: "assistant",
    RolMensaje.SISTEMA: "system",
    RolMensaje.HERRAMIENTA: "tool",
}


def de_usuario(usuario: Usuario, elementos: list) -> list:
    """Filtra los elementos que pertenecen a un usuario.

    Sirve para cualquier objeto con atributo ``usuario_id`` (eventos, hábitos,
    objetivos, recordatorios, conversaciones). No es válido para ``Mensaje`` ni
    ``RegistroHabito``, que se enlazan por otro identificador.
    """
    return [x for x in elementos if x.usuario_id == usuario.id]


def registros_de(habito: Habito, registros: list[RegistroHabito]) -> list[RegistroHabito]:
    """Devuelve los registros que pertenecen a un hábito."""
    return [r for r in registros if r.habito_id == habito.id]


def recordatorios_de_evento(evento: Evento, recordatorios: list[Recordatorio]) -> list[Recordatorio]:
    """Devuelve los recordatorios asociados a un evento."""
    return [r for r in recordatorios if r.evento_id == evento.id]


def mensajes_de(conversacion: Conversacion, mensajes: list[Mensaje]) -> list[Mensaje]:
    """Devuelve los mensajes de una conversación, del más antiguo al más reciente."""
    propios = [m for m in mensajes if m.conversacion_id == conversacion.id]
    return sorted(propios, key=lambda m: m.fecha_creacion)


def historial_para_modelo(mensajes: list[Mensaje], limite: int = 20) -> list[dict]:
    """Prepara el historial en el formato que consume un modelo de lenguaje.

    Descarta los mensajes vacíos, traduce cada rol (``ROLES_MODELO``) y se queda
    con los últimos ``limite`` mensajes.

    Args:
        mensajes: Mensajes ya ordenados de antiguo a reciente.
        limite: Máximo de mensajes a conservar; por defecto 20.

    Returns:
        Lista de diccionarios ``{"role": ..., "content": ...}``.
    """
    validos = [m for m in mensajes if not m.esta_vacio()]
    return [
        {"role": ROLES_MODELO[m.rol], "content": m.contenido}
        for m in validos[-limite:]
    ]


def total_del_dia(habito: Habito, registros: list[RegistroHabito], dia: date, zona) -> float:
    """Suma el ``valor`` registrado de un hábito durante un día.

    Args:
        habito: Hábito consultado.
        registros: Registros disponibles (se filtran por hábito).
        dia: Día a sumar.
        zona: ``ZoneInfo`` con la que se decide a qué día pertenece cada registro.
    """
    return sum(
        r.valor for r in registros_de(habito, registros)
        if r.fecha.astimezone(zona).date() == dia
    )


def racha_diaria(habito: Habito, registros: list[RegistroHabito], hoy: date, zona) -> int:
    """Cuenta los días seguidos en que se alcanzó el objetivo del hábito.

    Si hoy todavía no se cumple, la cuenta empieza en ayer, de modo que la racha
    no se rompe hasta que termina el día.

    Args:
        habito: Hábito consultado.
        registros: Registros disponibles (se filtran por hábito).
        hoy: Fecha de referencia.
        zona: ``ZoneInfo`` con la que se agrupan los registros por día.

    Returns:
        Número de días consecutivos cumplidos; 0 si no hay racha.
    """
    por_dia = defaultdict(float)
    for r in registros_de(habito, registros):
        por_dia[r.fecha.astimezone(zona).date()] += r.valor
    dia = hoy if habito.cumple(por_dia.get(hoy, 0)) else hoy - timedelta(days=1)
    racha = 0
    while habito.cumple(por_dia.get(dia, 0)):
        racha += 1
        dia -= timedelta(days=1)
    return racha


def resumen_del_dia(usuario, dia, eventos, habitos, registros, recordatorios) -> dict:
    """Resume la jornada de un usuario sin usar ningún modelo de lenguaje.

    Reúne los eventos activos del día, los hábitos diarios aún por cumplir y los
    recordatorios pendientes. Todas las horas se muestran en la zona del usuario.

    Args:
        usuario: Usuario del que se hace el resumen.
        dia: Día a resumir.
        eventos: Eventos disponibles (se filtran por usuario).
        habitos: Hábitos disponibles (se filtran por usuario).
        registros: Registros de hábitos disponibles.
        recordatorios: Recordatorios disponibles (se filtran por usuario).

    Returns:
        Diccionario con las claves ``dia`` (ISO), ``eventos`` (título, inicio y fin
        en formato HH:MM), ``habitos_pendientes`` (nombres) y ``recordatorios``
        (mensajes, ordenados por hora).
    """
    zona = usuario.zona()
    del_dia = Horario(de_usuario(usuario, eventos)).eventos_del_dia(dia, zona)
    pendientes = [
        h.nombre
        for h in de_usuario(usuario, habitos)
        if h.activo
        and h.frecuencia == FrecuenciaHabito.DIARIA
        and not h.cumple(total_del_dia(h, registros, dia, zona))
    ]
    avisos = sorted(
        (
            r for r in de_usuario(usuario, recordatorios)
            if r.estado == EstadoRecordatorio.PENDIENTE
            and r.programado_para.astimezone(zona).date() == dia
        ),
        key=lambda r: r.programado_para,
    )
    return {
        "dia": dia.isoformat(),
        "eventos": [
            {
                "titulo": e.titulo,
                "inicio": e.comienza.astimezone(zona).strftime("%H:%M"),
                "fin": e.termina.astimezone(zona).strftime("%H:%M"),
            }
            for e in del_dia
        ],
        "habitos_pendientes": pendientes,
        "recordatorios": [r.mensaje for r in avisos],
    }
