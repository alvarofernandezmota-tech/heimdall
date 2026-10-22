from collections import defaultdict
from datetime import date, timedelta

from app.domain.habit import FrecuenciaHabito, Habito, RegistroHabito
from app.domain.message import Conversacion, Mensaje, RolMensaje
from app.domain.reminder import EstadoRecordatorio, Recordatorio
from app.domain.schedule import Evento, Horario
from app.domain.user import Usuario

ROLES_MODELO = {
    RolMensaje.USUARIO: "user",
    RolMensaje.ASISTENTE: "assistant",
    RolMensaje.SISTEMA: "system",
    RolMensaje.HERRAMIENTA: "tool",
}


def de_usuario(usuario: Usuario, elementos: list) -> list:
    return [x for x in elementos if x.usuario_id == usuario.id]


def registros_de(habito: Habito, registros: list[RegistroHabito]) -> list[RegistroHabito]:
    return [r for r in registros if r.habito_id == habito.id]


def recordatorios_de_evento(evento: Evento, recordatorios: list[Recordatorio]) -> list[Recordatorio]:
    return [r for r in recordatorios if r.evento_id == evento.id]


def mensajes_de(conversacion: Conversacion, mensajes: list[Mensaje]) -> list[Mensaje]:
    propios = [m for m in mensajes if m.conversacion_id == conversacion.id]
    return sorted(propios, key=lambda m: m.fecha_creacion)


def historial_para_modelo(mensajes: list[Mensaje], limite: int = 20) -> list[dict]:
    validos = [m for m in mensajes if not m.esta_vacio()]
    return [
        {"role": ROLES_MODELO[m.rol], "content": m.contenido}
        for m in validos[-limite:]
    ]


def total_del_dia(habito: Habito, registros: list[RegistroHabito], dia: date, zona) -> float:
    return sum(
        r.valor for r in registros_de(habito, registros)
        if r.fecha.astimezone(zona).date() == dia
    )


def racha_diaria(habito: Habito, registros: list[RegistroHabito], hoy: date, zona) -> int:
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
