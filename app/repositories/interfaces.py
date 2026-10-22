"""Interfaces abstractas de los repositorios.

Un repositorio es el único lugar que sabe cómo se guardan y se leen los objetos
del dominio. Estas interfaces solo describen qué operaciones ofrece cada uno;
la implementación concreta (SQLite hoy, otra base mañana) vive en otro archivo.
El resto de la aplicación depende de las interfaces, no de SQLite.
"""

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID
from zoneinfo import ZoneInfo

from app.domain.schedule import Evento
from app.domain.user import Usuario


class RepositorioUsuarios(ABC):
    """Operaciones de almacenamiento de usuarios."""

    @abstractmethod
    def guardar(self, usuario: Usuario) -> None:
        """Inserta el usuario o, si ya existe su ``id``, actualiza sus datos."""

    @abstractmethod
    def obtener(self, usuario_id: UUID) -> Usuario | None:
        """Devuelve el usuario con ese ``id`` o ``None`` si no existe."""

    @abstractmethod
    def listar(self) -> list[Usuario]:
        """Devuelve todos los usuarios, del más antiguo al más reciente."""

    @abstractmethod
    def eliminar(self, usuario_id: UUID) -> bool:
        """Elimina el usuario y sus datos. Devuelve ``True`` si existía."""


class RepositorioEventos(ABC):
    """Operaciones de almacenamiento de eventos."""

    @abstractmethod
    def guardar(self, evento: Evento) -> None:
        """Inserta el evento o, si ya existe su ``id``, actualiza sus datos."""

    @abstractmethod
    def obtener(self, evento_id: UUID) -> Evento | None:
        """Devuelve el evento con ese ``id`` o ``None`` si no existe."""

    @abstractmethod
    def listar_por_usuario(self, usuario_id: UUID) -> list[Evento]:
        """Devuelve todos los eventos de un usuario ordenados por hora de inicio."""

    @abstractmethod
    def listar_activos_del_dia(
        self, usuario_id: UUID, dia: date, zona: ZoneInfo
    ) -> list[Evento]:
        """Devuelve los eventos programados de un usuario que empiezan ese día.

        El día se calcula en la zona horaria indicada.
        """

    @abstractmethod
    def eliminar(self, evento_id: UUID) -> bool:
        """Elimina el evento. Devuelve ``True`` si existía."""
