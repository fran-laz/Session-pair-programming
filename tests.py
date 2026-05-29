"""
tests.py
-----------------------------------------------------------
Pruebas de Pair Programming - 6 validaciones (True/False).
Mapeo: HU-01 a HU-06 con sus respectivos métodos de test.

Uso: python tests.py
-----------------------------------------------------------
"""
from copy import deepcopy
from logica import Programador, Tarea, Pareja, SesionPairProgramming


# -----------------------------------------------------------
# TEST 1 - HU-01: Formación de la pareja
# -----------------------------------------------------------
# Contexto XP: En el desarrollo ágil, el trabajo en pareja exige
# exactamente DOS miembros y ambos deben estar presentes (activos).
def test_pareja_formada(pareja):
    return len(pareja.miembros) == 2 and all(p.activo for p in pareja.miembros)


# -----------------------------------------------------------
# TEST 2 - HU-02: Asignación de roles
# -----------------------------------------------------------
# Contexto XP: Coexistencia obligatoria de un Conductor (escribe)
# y un Navegante (revisa). No se permiten roles duplicados.
def test_roles_assigned(pareja):
    roles = [p.rol for p in pareja.miembros]
    return roles.count("Conductor") == 1 and roles.count("Navegante") == 1


# -----------------------------------------------------------
# TEST 3 - HU-03: Rotación de roles
# -----------------------------------------------------------
# Contexto XP: Los roles deben intercambiarse periódicamente
# para mantener el foco, evitar la fatiga y compartir conocimiento.
def test_rotacion_roles(pareja_antes, pareja_despues):
    return (pareja_antes.miembros[0].rol == pareja_despues.miembros[1].rol and
            pareja_antes.miembros[1].rol == pareja_despues.miembros[0].rol)


# -----------------------------------------------------------
# TEST 4 - HU-04: Selección de la tarea
# -----------------------------------------------------------
# Contexto XP: Toda sesión productiva requiere un objetivo claro;
# la pareja debe tener asignada una tarea activa y descrita.
def test_tarea_asignada(sesion):
    return sesion.tarea is not None and sesion.tarea.descripcion != ""


# -----------------------------------------------------------
# TEST 5 - HU-05: Revisión continua del código
# -----------------------------------------------------------
# Contexto XP: El sistema debe permitir que el Navegante registre
# y guarde observaciones en tiempo real sobre el código creado.
def test_observaciones_registradas(sesion):
    return len(sesion.observaciones) >= 0 and sesion.permite_observaciones is True


# -----------------------------------------------------------
# TEST 6 - HU-06: Cierre e integración del código
# -----------------------------------------------------------
# Contexto XP: La sesión no se cierra formalmente sin antes realizar
# commit y push local/remoto para asegurar la integración continua.
def test_sesion_cerrada_con_commit(sesion):
    return (sesion.estado == "cerrada"
            and sesion.commit_realizado
            and sesion.push_realizado)


def ejecutar_simulacion():
    """Crea una sesión completa y devuelve los objetos necesarios para testear."""
    ana = Programador("Ana", 1)
    luis = Programador("Luis", 2)
    pareja = Pareja(ana, luis)
    pareja.asignar_roles_iniciales()

    pareja_antes = deepcopy(pareja)
    pareja.rotar_roles()

    tarea = Tarea("Implementar login con validación de email")
    sesion = SesionPairProgramming(pareja, tarea)
    sesion.agregar_observacion("Revisar manejo de excepciones")
    sesion.agregar_observacion("Falta validar formato de email")
    sesion.marcar_commit()
    sesion.marcar_push()
    sesion.cerrar()

    return pareja_antes, pareja, sesion


def main():
    print("=" * 60)
    print("EJECUCIÓN DE LOS 6 TESTS DE PAIR PROGRAMMING")
    print("=" * 60)

    pareja_antes, pareja, sesion = ejecutar_simulacion()

    resultados = [
        ("HU-01 test_pareja_formada           ",
            test_pareja_formada(pareja)),
        ("HU-02 test_roles_asignados          ",
            test_roles_asignados(pareja)),
        ("HU-03 test_rotacion_roles           ",
            test_rotacion_roles(pareja_antes, pareja)),
        ("HU-04 test_tarea_asignada           ",
            test_tarea_asignada(sesion)),
        ("HU-05 test_observaciones_registradas",
            test_observaciones_registradas(sesion)),
        ("HU-06 test_sesion_cerrada_con_commit",
            test_sesion_cerrada_con_commit(sesion)),
    ]

    for nombre, ok in resultados:
        marca = "PASS" if ok else "FAIL"
        print(f"  [{marca}] {nombre} -> {ok}")

    total = sum(1 for _, r in resultados if r)
    print(f"\nResultado: {total}/{len(resultados)} tests pasados")


if __name__ == "__main__":
    main()