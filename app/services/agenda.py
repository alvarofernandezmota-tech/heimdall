"""Casos de uso de la agenda: crear, mover y consultar eventos."""

from datetime import date, datetime
from uuid import UUID

from app.domain.schedule import Evento, Horario
from app.domain.user import Usuario
from app.repositories.interfaces import RepositorioEventos, RepositorioUsuarios
from app.schemas.schedule import EventoSchema
from app.services.errores import ConflictoDeHorario, EventoNoEncontrado, UsuarioNoEncontrado


class ServicioAgenda:
    """Gestión de la agenda de un usuario.

    Valida los datos con los esquemas, impide solapes entre eventos activos del
    mismo usuario y delega el almacenamiento en los repositorios. No hace
    ``commit``: de eso se encarga quien abre la conexión.
    """

    def __init__(self, usuarios: RepositorioUsuarios, eventos: RepositorioEventos) -> None:
        """Crea el servicio sobre los repositorios de usuarios y de eventos."""
        self._usuarios = usuarios
        self._eventos = eventos

    def crear_evento(
        self,
        usuario_id: UUID,
        titulo: str,
        comienza: datetime,
        termina: datetime,
        descripcion: str | None = None,
        ubicacion: str | None = None,
    ) -> Evento:
        """Crea y guarda un evento si no choca con ninguno activo del usuario.

        Raises:
            UsuarioNoEncontrado: Si el usuario no existe.
            ValueError: Si ``termina`` no es posterior a ``comienza``.
            pydantic.ValidationError: Si el título está vacío o las fechas no
                llevan zona horaria.
            ConflictoDeHorario: Si se solapa con otro evento activo.
        """
        self._exigir_usuario(usuario_id)
        evento = Evento(
            usuario_id,
            titulo.strip(),
            comienza,
            termina,
            descripcion=descripcion,
            ubicacion=ubicacion,
        )
        EventoSchema.model_validate(evento)
        self._exigir_sin_conflicto(evento)
        self._eventos.guardar(evento)
        return evento

    def obtener_evento(self, evento_id: UUID) -> Evento:
        """Devuelve el evento indicado.

        Raises:
            EventoNoEncontrado: Si no existe.
        """
        evento = self._eventos.obtener(evento_id)
        if evento is None:
            raise EventoNoEncontrado(evento_id)
        return evento

    def cancelar_evento(self, evento_id: UUID) -> Evento:
        """Cancela el evento y guarda el cambio.

        Raises:
            EventoNoEncontrado: Si no existe.
        """
        evento = self.obtener_evento(evento_id)
        evento.cancelar()
        self._eventos.guardar(evento)
        return evento

    def completar_evento(self, evento_id: UUID) -> Evento:
        """Marca el evento como completado y guarda el cambio.

        Raises:
            EventoNoEncontrado: Si no existe.
        """
        evento = self.obtener_evento(evento_id)
        evento.completar()
        self._eventos.guardar(evento)
        return evento

    def reprogramar_evento(
        self, evento_id: UUID, comienza: datetime, termina: datetime
    ) -> Evento:
        """Cambia las horas de un evento comprobando que no choque con otros.

        El evento no se considera en conflicto consigo mismo. Si el evento está
        cancelado o completado, no se comprueban solapes.

        Raises:
            EventoNoEncontrado: Si no existe.
            ValueError: Si ``termina`` no es posterior a ``comienza``.
            pydantic.ValidationError: Si las fechas no llevan zona horaria.
            ConflictoDeHorario: Si las nuevas horas se solapan con otro evento activo.
        """
        actual = self.obtener_evento(evento_id)
        candidato = Evento(
            actual.usuario_id,
            actual.titulo,
            comienza,
            termina,
            id=actual.id,
            descripcion=actual.descripcion,
            ubicacion=actual.ubicacion,
            estado=actual.estado,
        )
        EventoSchema.model_validate(candidato)
        self._exigir_sin_conflicto(candidato)
        self._eventos.guardar(candidato)
        return candidato

    def eventos_del_dia(self, usuario_id: UUID, dia: date) -> list[Evento]:
        """Devuelve los eventos programados del usuario que empiezan ese día.

        El día se calcula en la zona horaria del usuario.

        Raises:
            UsuarioNoEncontrado: Si el usuario no existe.
        """
        usuario = self._exigir_usuario(usuario_id)
        return self._eventos.listar_activos_del_dia(usuario_id, dia, usuario.zona())

    def celdas_del_dia(
        self, usuario_id: UUID, dia: date, minutos: int = 15
    ) -> list[bool]:
        """Devuelve los tramos del día marcados como ocupados (``True``) o libres.

        El día se calcula en la zona horaria del usuario.

        Raises:
            UsuarioNoEncontrado: Si el usuario no existe.
        """
        usuario = self._exigir_usuario(usuario_id)
        horario = Horario(self._eventos.listar_por_usuario(usuario_id))
        return horario.celdas_del_dia(dia, usuario.zona(), minutos)

    def _exigir_usuario(self, usuario_id: UUID) -> Usuario:
        """Devuelve el usuario o lanza ``UsuarioNoEncontrado``."""
        usuario = self._usuarios.obtener(usuario_id)
        if usuario is None:
            raise UsuarioNoEncontrado(usuario_id)
        return usuario

    def _exigir_sin_conflicto(self, evento: Evento) -> None:
        """Lanza ``ConflictoDeHorario`` si un evento activo choca con otro."""
        if not evento.esta_activo():
            return
        horario = Horario(self._eventos.listar_por_usuario(evento.usuario_id))
        if horario.hay_conflicto(evento):
            raise ConflictoDeHorario(evento.titulo)
