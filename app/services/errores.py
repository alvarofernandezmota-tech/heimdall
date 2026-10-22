"""Errores previstos al usar los servicios de aplicación."""

from uuid import UUID


class ErrorDeServicio(Exception):
    """Clase base de los errores previstos de los servicios."""


class UsuarioNoEncontrado(ErrorDeServicio):
    """No existe el usuario solicitado."""

    def __init__(self, usuario_id: UUID) -> None:
        """Guarda el identificador buscado y construye el mensaje."""
        super().__init__(f"No existe el usuario {usuario_id}.")
        self.usuario_id = usuario_id


class EventoNoEncontrado(ErrorDeServicio):
    """No existe el evento solicitado."""

    def __init__(self, evento_id: UUID) -> None:
        """Guarda el identificador buscado y construye el mensaje."""
        super().__init__(f"No existe el evento {evento_id}.")
        self.evento_id = evento_id


class ConflictoDeHorario(ErrorDeServicio):
    """El evento choca con otro ya programado del mismo usuario."""

    def __init__(self, titulo: str) -> None:
        """Guarda el título del evento y construye el mensaje."""
        super().__init__(f"El evento «{titulo}» choca con otro ya programado.")
        self.titulo = titulo
