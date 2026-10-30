"""
Pruebas del nucleo de teoria de conjuntos y de las dos proposiciones formales.
Ejecutar con: pytest --cov=permisos_engine
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from permisos_engine import (
    ConjuntoPermisos,
    Grupo,
    Usuario,
    revocar_permiso_de_grupo,
    comparar_usuarios,
    verificar_cota_inclusion_exclusion,
)


# --- Operaciones basicas de conjuntos -------------------------------------

def test_union_basica():
    a = ConjuntoPermisos(["leer", "escribir"])
    b = ConjuntoPermisos(["escribir", "borrar"])
    u = a.union(b)
    assert set(u) == {"leer", "escribir", "borrar"}


def test_interseccion_basica():
    a = ConjuntoPermisos(["leer", "escribir"])
    b = ConjuntoPermisos(["escribir", "borrar"])
    i = a.interseccion(b)
    assert set(i) == {"escribir"}


def test_diferencia_basica():
    a = ConjuntoPermisos(["leer", "escribir"])
    b = ConjuntoPermisos(["escribir"])
    d = a.diferencia(b)
    assert set(d) == {"leer"}


def test_diferencia_simetrica():
    a = ConjuntoPermisos(["leer", "escribir"])
    b = ConjuntoPermisos(["escribir", "borrar"])
    ds = a.diferencia_simetrica(b)
    assert set(ds) == {"leer", "borrar"}


# --- Proposicion 1: conmutatividad y asociatividad de la union -----------

def test_union_es_conmutativa():
    a = ConjuntoPermisos(["leer", "escribir"])
    b = ConjuntoPermisos(["borrar"])
    assert a.union(b) == b.union(a)


def test_union_es_asociativa():
    a = ConjuntoPermisos(["leer"])
    b = ConjuntoPermisos(["escribir"])
    c = ConjuntoPermisos(["borrar"])
    assert a.union(b).union(c) == a.union(b.union(c))


def test_orden_de_asignacion_de_roles_no_importa():
    """Consecuencia directa de la Proposicion 1 para el caso de uso real."""
    g1 = Grupo("Editor", ConjuntoPermisos(["leer", "escribir"]))
    g2 = Grupo("Soporte", ConjuntoPermisos(["leer", "responder_tickets"]))

    u_orden_1 = Usuario("ana", [g1, g2])
    u_orden_2 = Usuario("ana", [g2, g1])

    assert u_orden_1.permisos_efectivos_union() == u_orden_2.permisos_efectivos_union()


# --- Proposicion 2: cota por inclusion-exclusion --------------------------

def test_cota_inclusion_exclusion_con_solape():
    g1 = Grupo("Editor", ConjuntoPermisos(["leer", "escribir"]))
    g2 = Grupo("Soporte", ConjuntoPermisos(["leer", "responder_tickets"]))

    suma, tam_union, disjuntos = verificar_cota_inclusion_exclusion([g1, g2])

    assert tam_union <= suma
    assert disjuntos is False
    assert suma - tam_union == 1  # "leer" se cuenta doble en la suma


def test_cota_inclusion_exclusion_con_grupos_disjuntos():
    g1 = Grupo("Editor", ConjuntoPermisos(["leer", "escribir"]))
    g2 = Grupo("Finanzas", ConjuntoPermisos(["aprobar_pagos"]))

    suma, tam_union, disjuntos = verificar_cota_inclusion_exclusion([g1, g2])

    assert disjuntos is True
    assert suma == tam_union  # igualdad exacta cuando son disjuntos


# --- Casos de uso del sistema ---------------------------------------------

def test_politica_restrictiva_interseccion():
    g1 = Grupo("Editor", ConjuntoPermisos(["leer", "escribir", "publicar"]))
    g2 = Grupo("Junior", ConjuntoPermisos(["leer"]))

    u = Usuario("beto", [g1, g2])
    assert set(u.permisos_efectivos_interseccion()) == {"leer"}


def test_revocar_permiso_de_un_grupo_no_afecta_otros():
    g1 = Grupo("Editor", ConjuntoPermisos(["leer", "escribir"]))
    g2 = Grupo("Soporte", ConjuntoPermisos(["escribir"]))

    revocar_permiso_de_grupo(g1, "escribir")

    assert "escribir" not in g1.permisos
    assert "escribir" in g2.permisos  # el otro grupo no se ve afectado


def test_usuario_sin_grupos_no_tiene_permisos():
    u = Usuario("sin_grupos")
    assert len(u.permisos_efectivos_union()) == 0
    assert len(u.permisos_efectivos_interseccion()) == 0


def test_comparar_usuarios_detecta_diferencias():
    g1 = Grupo("Editor", ConjuntoPermisos(["leer", "escribir"]))
    g2 = Grupo("Admin", ConjuntoPermisos(["leer", "escribir", "eliminar_usuarios"]))

    u1 = Usuario("ana", [g1])
    u2 = Usuario("carlos", [g2])

    diff = comparar_usuarios(u1, u2)
    assert set(diff) == {"eliminar_usuarios"}


def test_asignar_grupo_duplicado_no_duplica():
    g1 = Grupo("Editor", ConjuntoPermisos(["leer"]))
    u = Usuario("ana")
    u.asignar_grupo(g1)
    u.asignar_grupo(g1)
    assert len(u.grupos) == 1
