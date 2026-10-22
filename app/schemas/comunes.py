"""Tipos reutilizables para los esquemas."""

from typing import Annotated

from pydantic import StringConstraints

# Texto obligatorio: se recortan los espacios de los extremos y no puede quedar vacío.
TextoNoVacio = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
