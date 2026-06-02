"""
logica.py
-----------------------------------------------------------
Lógica de Pair Programming - Metodología XP
Contiene las 4 clases basadas en las tarjetas CRC:
    - Programador
    - Tarea
    - Pareja
    - SesionPairProgramming
-----------------------------------------------------------
"""
from datetime import datetime


class Programador:
    """Representa a un programador del equipo XP."""
    def __init__(self, nombre, programador_id):
        self.nombre = nombre
        self.id = programador_id
        self.activo = True
        self.rol = None  # "Conductor" o "Navegante"

    def asignar_rol(self, rol):
        self.rol = rol


class Tarea:
    """Historia de usuario tomada del backlog."""
    def __init__(self, descripcion):
        self.descripcion = descripcion
        self.estado = "pendiente"

    def marcar_hecha(self):
        self.estado = "hecha"


class Pareja:
    """Agrupa exactamente dos programadores."""
    def __init__(self, prog1, prog2):
        self.miembros = [prog1, prog2]
        self.fecha_formacion = datetime.now()

    def asignar_roles_iniciales(self):
        """Asigna Conductor al primer miembro y Navegante al segundo."""
        self.miembros[0].asignar_rol("Conductor")
        self.miembros[1].asignar_rol("Navegante")

    def rotar_roles(self):
        """Intercambia los roles de los dos miembros."""
        for p in self.miembros:
            p.rol = "Navegante" if p.rol == "Conductor" else "Conductor"


class SesionPairProgramming:
    """Coordina toda la sesión de pair programming."""
    def __init__(self, pareja, tarea):
        self.pareja = pareja
        self.tarea = tarea
        self.estado = "activa"
        self.observaciones = []
        self.permite_observaciones = True
        self.commit_realizado = False
        self.push_realizado = False
        self.inicio = datetime.now()
        self.fin = None

    def agregar_observacion(self, texto):
        if self.permite_observaciones:
            self.observaciones.append(texto)

    def marcar_commit(self):
        self.commit_realizado = True

    def marcar_push(self):
        self.push_realizado = True

    def cerrar(self):
        """Cierra la sesión sólo si commit y push fueron realizados."""
        if self.commit_realizado and self.push_realizado:
            self.estado = "cerrada"
            self.fin = datetime.now()
            return True
        return False