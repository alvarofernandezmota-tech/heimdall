"""Interfaces abstractas de los repositorios.

Un repositorio es el único lugar que sabe cómo se guardan y se leen los objetos
del dominio. Estas interfaces solo describen qué operaciones ofrece cada uno;
la implementación concreta (SQLite hoy, otra base mañana) vive en otro archivo.
El resto de la aplicación depende de las interfaces, no de SQLite.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from app.domain.goal import EstadoObjetivo, Objetivo
from app.domain.goal import EstadoObjetivo, Objetivo
from app.domain.habit import Habito, RegistroHabito
from app.domain.reminder import Recordatorio
from app.domain.reminder import Recordatorio
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


class RepositorioHabitos(ABC):
    """Operaciones de almacenamiento de hábitos."""

    @abstractmethod
    def guardar(self, habito: Habito) -> None:
        """Inserta el hábito o, si ya existe su ``id``, actualiza sus datos."""

    @abstractmethod
    def obtener(self, habito_id: UUID) -> Habito | None:
        """Devuelve el hábito con ese ``id`` o ``None`` si no existe."""

    @abstractmethod
    def listar_por_usuario(
        self, usuario_id: UUID, solo_activos: bool = False
    ) -> list[Habito]:
        """Devuelve los hábitos de un usuario ordenados por nombre.

        Con ``solo_activos=True`` se omiten los hábitos desactivados.
        """

    @abstractmethod
    def eliminar(self, habito_id: UUID) -> bool:
        """Elimina el hábito y sus registros. Devuelve ``True`` si existía."""


class RepositorioRegistrosHabito(ABC):
    """Operaciones de almacenamiento de registros de hábitos."""

    @abstractmethod
    def guardar(self, registro: RegistroHabito) -> None:
        """Inserta el registro o, si ya existe su ``id``, actualiza sus datos."""

    @abstractmethod
    def obtener(self, registro_id: UUID) -> RegistroHabito | None:
        """Devuelve el registro con ese ``id`` o ``None`` si no existe."""

    @abstractmethod
    def listar_por_habito(self, habito_id: UUID) -> list[RegistroHabito]:
        """Devuelve todos los registros de un hábito, del más antiguo al más reciente."""

    @abstractmethod
    def listar_por_rango(
        self, habito_id: UUID, desde: datetime, hasta: datetime
    ) -> list[RegistroHabito]:
        """Devuelve los registros con ``desde <= fecha < hasta``, ordenados por fecha.

        Ambas fechas deben llevar zona horaria.
        """

    @abstractmethod
    def eliminar(self, registro_id: UUID) -> bool:
        """Elimina el registro. Devuelve ``True`` si existía."""


class RepositorioObjetivos(ABC):
    """Operaciones de almacenamiento de objetivos."""

    @abstractmethod
    def guardar(self, objetivo: Objetivo) -> None:
        """Inserta el objetivo o, si ya existe su ``id``, actualiza sus datos."""

    @abstractmethod
    def obtener(self, objetivo_id: UUID) -> Objetivo | None:
        """Devuelve el objetivo con ese ``id`` o ``None`` si no existe."""

    @abstractmethod
    def listar_por_usuario(
        self, usuario_id: UUID, estado: EstadoObjetivo | None = None
    ) -> list[Objetivo]:
        """Devuelve los objetivos de un usuario, los más próximos a vencer primero.

        Los objetivos sin fecha límite van al final. Con ``estado`` se devuelven
        solo los que están en esa situación.
        """

    @abstractmethod
    def eliminar(self, objetivo_id: UUID) -> bool:
        """Elimina el objetivo. Devuelve ``True`` si existía."""


class RepositorioRecordatorios(ABC):
    """Operaciones de almacenamiento de recordatorios."""

    @abstractmethod
    def guardar(self, recordatorio: Recordatorio) -> None:
        """Inserta el recordatorio o, si ya existe su ``id``, actualiza sus datos."""

    @abstractmethod
    def obtener(self, recordatorio_id: UUID) -> Recordatorio | None:
        """Devuelve el recordatorio con ese ``id`` o ``None`` si no existe."""

    @abstractmethod
    def listar_por_usuario(self, usuario_id: UUID) -> list[Recordatorio]:
        """Devuelve los recordatorios de un usuario ordenados por hora programada."""

    @abstractmethod
    def listar_de_evento(self, evento_id: UUID) -> list[Recordatorio]:
        """Devuelve los recordatorios asociados a un evento, por hora programada."""

    @abstractmethod
    def listar_pendientes_del_dia(
        self, usuario_id: UUID, dia: date, zona: ZoneInfo
    ) -> list[Recordatorio]:
        """Devuelve los recordatorios pendientes de un usuario programados ese día.

        El día se calcula en la zona horaria indicada.
        """

    @abstractmethod
    def listar_vencidos(self, ahora: datetime) -> list[Recordatorio]:
        """Devuelve los recordatorios pendientes de todos los usuarios ya vencidos.

        Son los que tienen ``programado_para <= ahora``, del más antiguo al más
        reciente. ``ahora`` debe llevar zona horaria.
        """

    @abstractmethod
    def eliminar(self, recordatorio_id: UUID) -> bool:
        """Elimina el recordatorio. Devuelve ``True`` si existía."""


class RepositorioObjetivos(ABC):
    """Operaciones de almacenamiento de objetivos."""

    @abstractmethod
    def guardar(self, objetivo: Objetivo) -> None:
        """Inserta el objetivo o, si ya existe su ``id``, actualiza sus datos."""

    @abstractmethod
    def obtener(self, objetivo_id: UUID) -> Objetivo | None:
        """Devuelve el objetivo con ese ``id`` o ``None`` si no existe."""

    @abstractmethod
    def listar_por_usuario(
        self, usuario_id: UUID, estado: EstadoObjetivo | None = None
    ) -> list[Objetivo]:
        """Devuelve los objetivos de un usuario, los más próximos a vencer primero.

        Los objetivos sin fecha límite van al final. Con ``estado`` se devuelven
        solo los que están en esa situación.
        """

    @abstractmethod
    def eliminar(self, objetivo_id: UUID) -> bool:
        """Elimina el objetivo. Devuelve ``True`` si existía."""


class RepositorioRecordatorios(ABC):
    """Operaciones de almacenamiento de recordatorios."""

    @abstractmethod
    def guardar(self, recordatorio: Recordatorio) -> None:
        """Inserta el recordatorio o, si ya existe su ``id``, actualiza sus datos."""

    @abstractmethod
    def obtener(self, recordatorio_id: UUID) -> Recordatorio | None:
        """Devuelve el recordatorio con ese ``id`` o ``None`` si no existe."""

    @abstractmethod
    def listar_por_usuario(self, usuario_id: UUID) -> list[Recordatorio]:
        """Devuelve los recordatorios de un usuario ordenados por hora programada."""

    @abstractmethod
    def listar_de_evento(self, evento_id: UUID) -> list[Recordatorio]:
        """Devuelve los recordatorios asociados a un evento, por hora programada."""

    @abstractmethod
    def listar_pendientes_del_dia(
        self, usuario_id: UUID, dia: date, zona: ZoneInfo
    ) -> list[Recordatorio]:
        """Devuelve los recordatorios pendientes de un usuario programados ese día.

        El día se calcula en la zona horaria indicada.
        """

    @abstractmethod
    def listar_vencidos(self, ahora: datetime) -> list[Recordatorio]:
        """Devuelve los recordatorios pendientes de todos los usuarios ya vencidos.

        Son los que tienen ``programado_para <= ahora``, del más antiguo al más
        reciente. ``ahora`` debe llevar zona horaria.
        """

    @abstractmethod
    def eliminar(self, recordatorio_id: UUID) -> bool:
        """Elimina el recordatorio. Devuelve ``True`` si existía."""
