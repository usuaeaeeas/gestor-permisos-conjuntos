"""
Demo de consola: agrega o quita a un usuario de un grupo y observa en vivo
como cambian sus permisos efectivos. Pensado para el Sprint Review / Defensa.

Ejecutar: python demo_cli.py
"""

from permisos_engine import ConjuntoPermisos, Grupo, Usuario, verificar_cota_inclusion_exclusion


def construir_escenario_ejemplo():
    grupos = {
        "Editor": Grupo("Editor", ConjuntoPermisos(["leer", "escribir", "publicar"])),
        "Soporte": Grupo("Soporte", ConjuntoPermisos(["leer", "responder_tickets"])),
        "Admin-Junior": Grupo("Admin-Junior", ConjuntoPermisos(["leer", "escribir", "gestionar_usuarios"])),
    }
    usuarios = {
        "ana": Usuario("ana", [grupos["Editor"], grupos["Soporte"]]),
        "beto": Usuario("beto", [grupos["Admin-Junior"]]),
    }
    return grupos, usuarios


def mostrar_estado(usuario: Usuario):
    print(f"\n--- {usuario.nombre} ---")
    print("Grupos:", [g.nombre for g in usuario.grupos])
    print("Permisos efectivos (union, politica permisiva):",
          sorted(usuario.permisos_efectivos_union()))
    print("Permisos efectivos (interseccion, politica restrictiva):",
          sorted(usuario.permisos_efectivos_interseccion()))


def main():
    grupos, usuarios = construir_escenario_ejemplo()

    print("=== Gestor de Permisos de Acceso basado en Teoria de Conjuntos ===")
    for u in usuarios.values():
        mostrar_estado(u)

    suma, tam_union, disjuntos = verificar_cota_inclusion_exclusion(list(grupos.values()))
    print("\n--- Verificacion Proposicion 2 (inclusion-exclusion) sobre todos los grupos ---")
    print(f"Suma de |P(Gi)| individuales : {suma}")
    print(f"Tamano de la union real       : {tam_union}")
    print(f"Son disjuntos dos a dos       : {disjuntos}")
    print("La cota |union| <= suma se cumple:", tam_union <= suma)

    print("\n--- Simulacion: ana tambien entra a Admin-Junior ---")
    usuarios["ana"].asignar_grupo(grupos["Admin-Junior"])
    mostrar_estado(usuarios["ana"])

    print("\n--- Simulacion: se revoca 'publicar' del grupo Editor ---")
    from permisos_engine import revocar_permiso_de_grupo
    revocar_permiso_de_grupo(grupos["Editor"], "publicar")
    mostrar_estado(usuarios["ana"])


if __name__ == "__main__":
    main()
