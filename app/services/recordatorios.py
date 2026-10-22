"""Casos de uso de los recordatorios: programarlos, enviarlos y cancelarlos."""

from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from app.domain.reminder import Recordatorio
from app.domain.user import Usuario
from app.repositories.interfaces import (
    RepositorioEventos,
    RepositorioRecordatorios,
    RepositorioUsuarios,
)
from app.schemas.reminder import RecordatorioSchema
from app.services.errores import (
    EventoNoActivo,
    EventoNoEncontrado,
    RecordatorioEnElPasado,
    RecordatorioNoEncontrado,
    UsuarioNoEncontrado,
)


class ServicioRecordatorios:
    """Gestión de los recordatorios de un usuario.

    Recibe un reloj (una función que devuelve la hora actual con zona horaria)
    para poder fijar la hora en las pruebas. No hace ``commit``: de eso se
    encarga quien abre la conexión.
    """

    def __init__(
        self,
        usuarios: RepositorioUsuarios,
        eventos: RepositorioEventos,
        recordatorios: RepositorioRecordatorios,
        reloj: Callable[[], datetime] | None = None,
    ) -> None:
        """Crea el servicio; si no se indica reloj, usa la hora actual en UTC."""
        self._usuarios = usuarios
        self._eventos = eventos
        self._recordatorios = recordatorios
        self._reloj = reloj or (lambda: datetime.now(UTC))

    def programar(self, usuario_id: UUID, mensaje: str, cuando: datetime) -> Recordatorio:
        """Programa un aviso libre, no ligado a ningún evento.

        Raises:
            UsuarioNoEncontrado: Si el usuario no existe.
            pydantic.ValidationError: Si el mensaje está vacío o ``cuando`` no
                lleva zona horaria.
            RecordatorioEnElPasado: Si ``cuando`` ya ha pasado.
        """
        self._exigir_usuario(usuario_id)
        recordatorio = Recordatorio(usuario_id, mensaje.strip(), cuando)
        return self._guardar_si_es_futuro(recordatorio)

    def programar_para_evento(
        self,
        evento_id: UUID,
        antelacion: timedelta,
        mensaje: str | None = None,
    ) -> Recordatorio:
        """Programa un aviso un tiempo antes de que empiece un evento.

        Si no se indica ``mensaje``, se usa "<título> empieza a las HH:MM", con la
        hora en la zona del usuario.

        Raises:
            EventoNoEncontrado: Si el evento no existe.
            EventoNoActivo: Si el evento está cancelado o completado.
            ValueError: Si ``antelacion`` es negativa.
            pydantic.ValidationError: Si el mensaje está vacío.
            RecordatorioEnElPasado: Si el aviso caería en un momento ya pasado.
        """
        if antelacion < timedelta(0):
            raise ValueError("La antelación no puede ser negativa.")
        evento = self._eventos.obtener(evento_id)
        if evento is None:
            raise EventoNoEncontrado(evento_id)
        if not evento.esta_activo():
            raise EventoNoActivo(evento.titulo)
        usuario = self._exigir_usuario(evento.usuario_id)
        if mensaje is None:
            hora = evento.comienza.astimezone(usuario.zona())
            mensaje = f"{evento.titulo} empieza a las {hora:%H:%M}"
        recordatorio = Recordatorio(
            evento.usuario_id,
            mensaje.strip(),
            evento.comienza - antelacion,
            evento_id=evento.id,
        )
        return self._guardar_si_es_futuro(recordatorio)

    def cancelar(self, recordatorio_id: UUID) -> Recordatorio:
        """Cancela el recordatorio y guarda el cambio.

        Raises:
            RecordatorioNoEncontrado: Si no existe.
        """
        recordatorio = self._obtener(recordatorio_id)
        recordatorio.cancelar()
        self._recordatorios.guardar(recordatorio)
        return recordatorio

    def marcar_enviado(self, recordatorio_id: UUID) -> Recordatorio:
        """Marca el recordatorio como enviado y guarda el cambio.

        Raises:
            RecordatorioNoEncontrado: Si no existe.
        """
        recordatorio = self._obtener(recordatorio_id)
        recordatorio.marcar_enviado()
        self._recordatorios.guardar(recordatorio)
        return recordatorio

    def pendientes_del_dia(self, usuario_id: UUID, dia: date) -> list[Recordatorio]:
        """Devuelve los recordatorios pendientes del usuario programados ese día.

        El día se calcula en la zona horaria del usuario.

        Raises:
            UsuarioNoEncontrado: Si el usuario no existe.
        """
        usuario = self._exigir_usuario(usuario_id)
        return self._recordatorios.listar_pendientes_del_dia(usuario_id, dia, usuario.zona())

    def vencidos(self) -> list[Recordatorio]:
        """Devuelve los recordatorios pendientes de todos los usuarios que ya tocan.

        Es lo que un programador de avisos debe enviar ahora; después de enviar
        cada uno debe llamar a ``marcar_enviado``.
        """
        return self._recordatorios.listar_vencidos(self._reloj())

    def _guardar_si_es_futuro(self, recordatorio: Recordatorio) -> Recordatorio:
        """Valida el recordatorio, comprueba que no esté en el pasado y lo guarda."""
        RecordatorioSchema.model_validate(recordatorio)
        if recordatorio.programado_para <= self._reloj():
            raise RecordatorioEnElPasado(recordatorio.programado_para)
        self._recordatorios.guardar(recordatorio)
        return recordatorio

    def _obtener(self, recordatorio_id: UUID) -> Recordatorio:
        """Devuelve el recordatorio o lanza ``RecordatorioNoEncontrado``."""
        recordatorio = self._recordatorios.obtener(recordatorio_id)
        if recordatorio is None:
            raise RecordatorioNoEncontrado(recordatorio_id)
        return recordatorio

    def _exigir_usuario(self, usuario_id: UUID) -> Usuario:
        """Devuelve el usuario o lanza ``UsuarioNoEncontrado``."""
        usuario = self._usuarios.obtener(usuario_id)
        if usuario is None:
            raise UsuarioNoEncontrado(usuario_id)
        return usuario
