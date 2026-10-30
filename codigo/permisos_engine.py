"""
Motor de permisos de acceso basado en operaciones de Teoria de Conjuntos.

Nucleo discreto: cada rol/grupo tiene asociado un conjunto de permisos
P(G) subconjunto de un universo U. Los permisos efectivos de un usuario
que pertenece a varios grupos se calculan combinando esos conjuntos con
union, interseccion, diferencia y diferencia simetrica.

Las operaciones de conjuntos se implementan de forma explicita sobre una
tabla hash propia (no se delega en el operador `|`/`&` de Python ni en una
libreria externa), para que el nucleo matematico sea codigo propio del
grupo y pueda analizarse en complejidad.
"""

from dataclasses import dataclass, field
from typing import Iterable, List


class ConjuntoPermisos:
    """Conjunto de permisos (cadenas) implementado sobre una tabla hash propia."""

    def __init__(self, elementos: Iterable[str] = None):
        self._tabla = {}
        for e in elementos or []:
            self._tabla[e] = True

    def __contains__(self, permiso: str) -> bool:
        return permiso in self._tabla

    def __len__(self) -> int:
        return len(self._tabla)

    def __iter__(self):
        return iter(self._tabla)

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, ConjuntoPermisos):
            return NotImplemented
        return set(self._tabla) == set(otro._tabla)

    def __hash__(self):
        return hash(frozenset(self._tabla))

    def agregar(self, permiso: str) -> None:
        self._tabla[permiso] = True

    def quitar(self, permiso: str) -> None:
        self._tabla.pop(permiso, None)

    def union(self, otro: "ConjuntoPermisos") -> "ConjuntoPermisos":
        """A U B. Complejidad: O(|A| + |B|)."""
        resultado = ConjuntoPermisos(self._tabla.keys())
        for p in otro:
            resultado.agregar(p)
        return resultado

    def interseccion(self, otro: "ConjuntoPermisos") -> "ConjuntoPermisos":
        """A ^ B. Complejidad: O(min(|A|, |B|)) recorriendo el conjunto menor."""
        menor, mayor = (self, otro) if len(self) <= len(otro) else (otro, self)
        return ConjuntoPermisos(p for p in menor if p in mayor)

    def diferencia(self, otro: "ConjuntoPermisos") -> "ConjuntoPermisos":
        """A - B. Complejidad: O(|A|)."""
        return ConjuntoPermisos(p for p in self if p not in otro)

    def diferencia_simetrica(self, otro: "ConjuntoPermisos") -> "ConjuntoPermisos":
        """(A - B) U (B - A). Complejidad: O(|A| + |B|)."""
        return self.diferencia(otro).union(otro.diferencia(self))

    def es_subconjunto(self, otro: "ConjuntoPermisos") -> bool:
        return all(p in otro for p in self)

    def __repr__(self) -> str:
        return f"ConjuntoPermisos({sorted(self._tabla)})"


@dataclass
class Grupo:
    nombre: str
    permisos: ConjuntoPermisos


@dataclass
class Usuario:
    nombre: str
    grupos: List[Grupo] = field(default_factory=list)

    def asignar_grupo(self, grupo: Grupo) -> None:
        if grupo not in self.grupos:
            self.grupos.append(grupo)

    def quitar_grupo(self, grupo: Grupo) -> None:
        self.grupos = [g for g in self.grupos if g.nombre != grupo.nombre]

    def permisos_efectivos_union(self) -> ConjuntoPermisos:
        """Politica permisiva: permisos de CUALQUIER grupo al que pertenezca."""
        resultado = ConjuntoPermisos()
        for g in self.grupos:
            resultado = resultado.union(g.permisos)
        return resultado

    def permisos_efectivos_interseccion(self) -> ConjuntoPermisos:
        """Politica restrictiva: solo permisos que TODOS sus grupos otorgan."""
        if not self.grupos:
            return ConjuntoPermisos()
        resultado = self.grupos[0].permisos
        for g in self.grupos[1:]:
            resultado = resultado.interseccion(g.permisos)
        return resultado


def revocar_permiso_de_grupo(grupo: Grupo, permiso: str) -> None:
    """Revocacion puntual: diferencia de conjuntos sobre un solo grupo."""
    grupo.permisos = grupo.permisos.diferencia(ConjuntoPermisos([permiso]))


def comparar_usuarios(u1: Usuario, u2: Usuario) -> ConjuntoPermisos:
    """Permisos en los que u1 y u2 difieren (diferencia simetrica)."""
    return u1.permisos_efectivos_union().diferencia_simetrica(u2.permisos_efectivos_union())


def verificar_cota_inclusion_exclusion(grupos: List[Grupo]):
    """
    Verifica numericamente la Proposicion 2 (cota superior por inclusion-exclusion):
    |union de P(Gi)| <= suma |P(Gi)|, con igualdad si y solo si son disjuntos dos a dos.
    Devuelve (suma_individual, tamano_union_real, son_disjuntos).
    """
    suma = sum(len(g.permisos) for g in grupos)
    union_real = ConjuntoPermisos()
    for g in grupos:
        union_real = union_real.union(g.permisos)

    disjuntos = True
    for i in range(len(grupos)):
        for j in range(i + 1, len(grupos)):
            if len(grupos[i].permisos.interseccion(grupos[j].permisos)) > 0:
                disjuntos = False
                break
        if not disjuntos:
            break

    return suma, len(union_real), disjuntos
