"""Errores propios del dominio."""

from enum import StrEnum


class TransicionNoPermitida(ValueError):
    """Se intentó un cambio de estado que las reglas del dominio no permiten."""

    def __init__(self, actual: StrEnum, destino: StrEnum) -> None:
        """Guarda los estados implicados y construye el mensaje."""
        super().__init__(f"No se puede pasar de «{actual.value}» a «{destino.value}».")
        self.actual = actual
        self.destino = destino
