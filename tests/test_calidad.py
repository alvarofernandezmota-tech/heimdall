"""Comprobaciones de calidad del código fuente de ``app/``."""

import ast
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent / "app"


def _modulos():
    for archivo in sorted(RAIZ.rglob("*.py")):
        yield archivo, ast.parse(archivo.read_text(encoding="utf-8"))


def test_no_hay_clases_ni_funciones_duplicadas_en_un_modulo():
    duplicados = []
    for archivo, arbol in _modulos():
        vistos = set()
        for nodo in arbol.body:
            if isinstance(nodo, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if nodo.name in vistos:
                    duplicados.append(f"{archivo.name}: {nodo.name}")
                vistos.add(nodo.name)
    assert duplicados == []


def test_no_hay_imports_duplicados_en_un_modulo():
    duplicados = []
    for archivo, arbol in _modulos():
        vistos = set()
        for nodo in arbol.body:
            if isinstance(nodo, ast.ImportFrom):
                claves = [(nodo.module, a.name, a.asname) for a in nodo.names]
            elif isinstance(nodo, ast.Import):
                claves = [(None, a.name, a.asname) for a in nodo.names]
            else:
                continue
            for clave in claves:
                if clave in vistos:
                    duplicados.append(f"{archivo.name}: {clave[0] or ''} {clave[1]}".strip())
                vistos.add(clave)
    assert duplicados == []
