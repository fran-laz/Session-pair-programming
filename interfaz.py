"""
interfaz.py
-----------------------------------------------------------
Interfaz gráfica de Pair Programming con tkinter.
Incluye cronómetro de rotación de roles (15 o 30 minutos).
Importa la lógica desde logica.py.

Uso:
    python interfaz.py
-----------------------------------------------------------
"""
import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from logica import Programador, Tarea, Pareja, SesionPairProgramming


# Archivo donde se guarda el historial de sesiones
ARCHIVO_HISTORIAL = "historial_sesiones.txt"


class PairProgrammingApp:
    BG_CONDUCTOR_A = "#E6F1FB"   # Azul claro: Programador A es Conductor
    BG_CONDUCTOR_B = "#FAEEDA"   # Ámbar claro: Programador B es Conductor
    BG_BREAK       = "#F1EFE8"   # Gris: en pausa
    BG_CLOSED      = "#E1F5EE"   # Verde claro: sesión cerrada
    BG_DEFAULT     = "#FFFFFF"
    FG_DARK = "#2C2C2A"
    FG_GRAY = "#5F5E5A"

    def __init__(self, root):
        self.root = root
        self.root.title("Sesión de Pair Programming - XP")
        self.root.geometry("720x900")
        self.root.minsize(680, 820)

        # Estado de la sesión
        self.pareja = None
        self.sesion = None
        self.en_break = False
        self.bg_actual = self.BG_DEFAULT

        # Estado del cronómetro
        self.duracion_intervalo = 30 * 60   # segundos (por defecto 30 min)
        self.tiempo_restante = self.duracion_intervalo
        self.timer_id = None                # ID de root.after() para cancelar
        self.timer_activo = False

        self.root.configure(bg=self.bg_actual)

        self._crear_header()
        self._crear_frame_setup()
        self._crear_frame_activa()
        self._crear_frame_cerrada()
        self._mostrar_setup()

    # =======================================================
    # CONSTRUCCIÓN DE LA INTERFAZ
    # =======================================================

    def _crear_header(self):
        self.header = tk.Frame(self.root, bg=self.bg_actual)
        self.header.pack(fill="x", padx=20, pady=(20, 10))
        self.titulo = tk.Label(self.header, text="Sesión de Pair Programming",
                               font=("Arial", 16, "bold"),
                               bg=self.bg_actual, fg=self.FG_DARK)
        self.titulo.pack(side="left")
        self.status = tk.Label(self.header, text="No iniciada",
                               font=("Arial", 10), bg="#D3D1C7", fg="#444441",
                               padx=12, pady=4)
        self.status.pack(side="right")

    def _crear_frame_setup(self):
        self.frame_setup = tk.Frame(self.root, bg=self.bg_actual)
        self._etiqueta(self.frame_setup, "Programador A")
        self.entry_a = self._entry(self.frame_setup)
        self._etiqueta(self.frame_setup, "Programador B")
        self.entry_b = self._entry(self.frame_setup)
        self._etiqueta(self.frame_setup, "Tarea propuesta")
        self.entry_tarea = self._entry(self.frame_setup)

        # Selector de intervalo de rotación
        self._etiqueta(self.frame_setup, "Intervalo de rotación de roles")
        self.var_intervalo = tk.IntVar(value=30)
        self.frame_radios = tk.Frame(self.frame_setup, bg=self.bg_actual)
        self.frame_radios.pack(anchor="w", padx=20, pady=(0, 10))
        self.radio_15 = tk.Radiobutton(self.frame_radios, text="15 minutos",
                                       variable=self.var_intervalo, value=15,
                                       font=("Arial", 11),
                                       bg=self.bg_actual, fg=self.FG_DARK,
                                       activebackground=self.bg_actual,
                                       selectcolor="white")
        self.radio_15.pack(side="left", padx=(0, 20))
        self.radio_30 = tk.Radiobutton(self.frame_radios, text="30 minutos",
                                       variable=self.var_intervalo, value=30,
                                       font=("Arial", 11),
                                       bg=self.bg_actual, fg=self.FG_DARK,
                                       activebackground=self.bg_actual,
                                       selectcolor="white")
        self.radio_30.pack(side="left")

        self.btn_iniciar = tk.Button(self.frame_setup, text="Iniciar sesión",
                                     font=("Arial", 11, "bold"),
                                     bg=self.FG_DARK, fg="white",
                                     relief="flat", padx=20, pady=8,
                                     cursor="hand2", command=self._iniciar_sesion)
        self.btn_iniciar.pack(padx=20, pady=10, anchor="w")

    def _etiqueta(self, parent, texto):
        tk.Label(parent, text=texto, font=("Arial", 10),
                 bg=self.bg_actual, fg=self.FG_GRAY).pack(anchor="w", padx=20, pady=(10, 2))

    def _entry(self, parent):
        e = tk.Entry(parent, font=("Arial", 12), relief="solid", borderwidth=1)
        e.pack(fill="x", padx=20, pady=(0, 5), ipady=4)
        return e

    def _crear_frame_activa(self):
        self.frame_activa = tk.Frame(self.root, bg=self.bg_actual)

        # Tarea
        self.frame_tarea = tk.Frame(self.frame_activa, bg="white",
                                    relief="solid", borderwidth=1)
        self.frame_tarea.pack(fill="x", padx=20, pady=(10, 8))
        tk.Label(self.frame_tarea, text="Tarea", font=("Arial", 9),
                 bg="white", fg=self.FG_GRAY).pack(anchor="w", padx=12, pady=(8, 0))
        self.label_tarea = tk.Label(self.frame_tarea, text="",
                                    font=("Arial", 12, "bold"),
                                    bg="white", fg=self.FG_DARK)
        self.label_tarea.pack(anchor="w", padx=12, pady=(0, 8))

        # CRONÓMETRO
        self.frame_timer = tk.Frame(self.frame_activa, bg="white",
                                    relief="solid", borderwidth=1)
        self.frame_timer.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(self.frame_timer, text="Próxima rotación de roles en",
                 font=("Arial", 9), bg="white", fg=self.FG_GRAY).pack(pady=(8, 0))
        self.label_timer = tk.Label(self.frame_timer, text="30:00",
                                    font=("Arial", 28, "bold"),
                                    bg="white", fg=self.FG_DARK)
        self.label_timer.pack(pady=(0, 8))

        # Programadores (cards)
        self.frame_programadores = tk.Frame(self.frame_activa, bg=self.bg_actual)
        self.frame_programadores.pack(fill="x", padx=20, pady=5)

        self.card_a = tk.Frame(self.frame_programadores, bg="white",
                               relief="solid", borderwidth=1)
        self.card_a.pack(side="left", fill="both", expand=True,
                         padx=(0, 5), pady=5, ipadx=10, ipady=8)
        tk.Label(self.card_a, text="Programador A", font=("Arial", 9),
                 bg="white", fg=self.FG_GRAY).pack(anchor="w", padx=8, pady=(4, 0))
        self.label_nombre_a = tk.Label(self.card_a, text="",
                                       font=("Arial", 12, "bold"),
                                       bg="white", fg=self.FG_DARK)
        self.label_nombre_a.pack(anchor="w", padx=8)
        self.label_rol_a = tk.Label(self.card_a, text="Conductor",
                                    font=("Arial", 9, "bold"),
                                    bg="#0C447C", fg="#E6F1FB", padx=10, pady=3)
        self.label_rol_a.pack(anchor="w", padx=8, pady=(6, 4))

        self.card_b = tk.Frame(self.frame_programadores, bg="white",
                               relief="solid", borderwidth=1)
        self.card_b.pack(side="right", fill="both", expand=True,
                         padx=(5, 0), pady=5, ipadx=10, ipady=8)
        tk.Label(self.card_b, text="Programador B", font=("Arial", 9),
                 bg="white", fg=self.FG_GRAY).pack(anchor="w", padx=8, pady=(4, 0))
        self.label_nombre_b = tk.Label(self.card_b, text="",
                                       font=("Arial", 12, "bold"),
                                       bg="white", fg=self.FG_DARK)
        self.label_nombre_b.pack(anchor="w", padx=8)
        self.label_rol_b = tk.Label(self.card_b, text="Navegante",
                                    font=("Arial", 9, "bold"),
                                    bg="#444441", fg="#F1EFE8", padx=10, pady=3)
        self.label_rol_b.pack(anchor="w", padx=8, pady=(6, 4))

        # Controles
        self.frame_controles = tk.Frame(self.frame_activa, bg=self.bg_actual)
        self.frame_controles.pack(fill="x", padx=20, pady=10)
        self.btn_rotar = tk.Button(self.frame_controles, text="Cambiar roles",
                                   font=("Arial", 10), relief="solid", borderwidth=1,
                                   padx=15, pady=6, cursor="hand2", bg="white",
                                   command=self._rotar_roles)
        self.btn_rotar.pack(side="left", padx=(0, 8))
        self.btn_break = tk.Button(self.frame_controles, text="Tomar break",
                                   font=("Arial", 10), relief="solid", borderwidth=1,
                                   padx=15, pady=6, cursor="hand2", bg="white",
                                   command=self._toggle_break)
        self.btn_break.pack(side="left")

        # Comentarios
        self.lbl_coment = tk.Label(self.frame_activa, text="Comentarios de la pareja",
                                   font=("Arial", 9), bg=self.bg_actual, fg=self.FG_GRAY)
        self.lbl_coment.pack(anchor="w", padx=20, pady=(10, 2))

        self.lista_comentarios = tk.Listbox(self.frame_activa, font=("Arial", 10),
                                            height=4, relief="solid", borderwidth=1)
        self.lista_comentarios.pack(fill="x", padx=20, pady=(0, 5))

        self.frame_comment_input = tk.Frame(self.frame_activa, bg=self.bg_actual)
        self.frame_comment_input.pack(fill="x", padx=20, pady=(0, 10))
        self.entry_comentario = tk.Entry(self.frame_comment_input, font=("Arial", 10),
                                         relief="solid", borderwidth=1)
        self.entry_comentario.pack(side="left", fill="x", expand=True, ipady=4)
        self.entry_comentario.bind("<Return>", lambda e: self._agregar_comentario())
        self.btn_agregar = tk.Button(self.frame_comment_input, text="Agregar",
                                     font=("Arial", 10), relief="solid", borderwidth=1,
                                     padx=12, pady=4, cursor="hand2", bg="white",
                                     command=self._agregar_comentario)
        self.btn_agregar.pack(side="right", padx=(8, 0))

        # Integración
        self.lbl_integracion = tk.Label(self.frame_activa, text="Integración del código",
                                        font=("Arial", 9), bg=self.bg_actual, fg=self.FG_GRAY)
        self.lbl_integracion.pack(anchor="w", padx=20, pady=(5, 2))

        self.var_commit = tk.BooleanVar(value=False)
        self.var_push = tk.BooleanVar(value=False)
        self.check_commit = tk.Checkbutton(self.frame_activa, text="Commit realizado",
                                           variable=self.var_commit, font=("Arial", 10),
                                           bg=self.bg_actual, fg=self.FG_DARK,
                                           activebackground=self.bg_actual,
                                           command=self._actualizar_cierre)
        self.check_commit.pack(anchor="w", padx=20)
        self.check_push = tk.Checkbutton(self.frame_activa, text="Push al repositorio",
                                         variable=self.var_push, font=("Arial", 10),
                                         bg=self.bg_actual, fg=self.FG_DARK,
                                         activebackground=self.bg_actual,
                                         command=self._actualizar_cierre)
        self.check_push.pack(anchor="w", padx=20)

        self.btn_cerrar = tk.Button(self.frame_activa, text="Cerrar sesión",
                                    font=("Arial", 11, "bold"),
                                    bg="#E24B4A", fg="white", relief="flat",
                                    padx=20, pady=8, cursor="hand2",
                                    state="disabled", command=self._cerrar_sesion)
        self.btn_cerrar.pack(padx=20, pady=15, anchor="w")

    def _crear_frame_cerrada(self):
        self.frame_cerrada = tk.Frame(self.root, bg=self.bg_actual)
        self.label_cerrada = tk.Label(self.frame_cerrada,
                                      text="Sesión cerrada correctamente",
                                      font=("Arial", 16, "bold"),
                                      bg=self.bg_actual, fg="#0F6E56")
        self.label_cerrada.pack(pady=(50, 10))
        self.label_resumen = tk.Label(self.frame_cerrada, text="",
                                      font=("Arial", 10),
                                      bg=self.bg_actual, fg=self.FG_GRAY,
                                      wraplength=600, justify="left")
        self.label_resumen.pack(pady=10, padx=20)
        self.btn_nueva = tk.Button(self.frame_cerrada, text="Nueva sesión",
                                   font=("Arial", 11), relief="solid", borderwidth=1,
                                   padx=20, pady=8, cursor="hand2", bg="white",
                                   command=self._reiniciar)
        self.btn_nueva.pack(pady=15)

    # =======================================================
    # MANEJO DEL CRONÓMETRO
    # =======================================================

    def _iniciar_timer(self):
        """Inicia (o reanuda) el cronómetro."""
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.timer_activo = True
        self._tick_timer()

    def _pausar_timer(self):
        """Pausa el cronómetro sin reiniciarlo."""
        self.timer_activo = False
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def _reiniciar_timer(self):
        """Reinicia el cronómetro a su duración completa y lo arranca."""
        self._pausar_timer()
        self.tiempo_restante = self.duracion_intervalo
        self._actualizar_display_timer()
        self._iniciar_timer()

    def _tick_timer(self):
        """Se ejecuta cada segundo mientras el cronómetro está activo."""
        if not self.timer_activo:
            return
        self._actualizar_display_timer()
        if self.tiempo_restante <= 0:
            self._tiempo_terminado()
            return
        self.tiempo_restante -= 1
        self.timer_id = self.root.after(1000, self._tick_timer)

    def _actualizar_display_timer(self):
        """Actualiza el texto del cronómetro y cambia color si queda poco tiempo."""
        mins = self.tiempo_restante // 60
        secs = self.tiempo_restante % 60
        self.label_timer.configure(text=f"{mins:02d}:{secs:02d}")
        # Color de advertencia cuando queda poco
        if self.tiempo_restante <= 60:
            self.label_timer.configure(fg="#E24B4A")    # Rojo: último minuto
        elif self.tiempo_restante <= 180:
            self.label_timer.configure(fg="#BA7517")    # Ámbar: últimos 3 min
        else:
            self.label_timer.configure(fg=self.FG_DARK)

    def _tiempo_terminado(self):
        """Se llama cuando el cronómetro llega a 0."""
        self.timer_activo = False
        self.timer_id = None
        minutos = self.duracion_intervalo // 60
        messagebox.showinfo(
            "¡Tiempo de rotar!",
            f"Han pasado {minutos} minutos.\n"
            "Es momento de cambiar de roles."
        )
        # Rotación automática + reinicio del cronómetro
        self._rotar_roles()

    # =======================================================
    # GESTIÓN DE COLORES Y VISTAS
    # =======================================================

    def _aplicar_color(self, color):
        self.bg_actual = color
        self.root.configure(bg=color)
        for w in [self.header, self.frame_setup, self.frame_activa,
                  self.frame_cerrada, self.frame_programadores,
                  self.frame_controles, self.frame_comment_input,
                  self.frame_radios]:
            w.configure(bg=color)
        self.titulo.configure(bg=color)
        self.check_commit.configure(bg=color, activebackground=color)
        self.check_push.configure(bg=color, activebackground=color)
        self.radio_15.configure(bg=color, activebackground=color)
        self.radio_30.configure(bg=color, activebackground=color)
        self.label_cerrada.configure(bg=color)
        self.label_resumen.configure(bg=color)
        self.lbl_coment.configure(bg=color)
        self.lbl_integracion.configure(bg=color)
        for frame in [self.frame_setup, self.frame_cerrada]:
            for child in frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(bg=color)

    def _mostrar_setup(self):
        self.frame_activa.pack_forget()
        self.frame_cerrada.pack_forget()
        self.frame_setup.pack(fill="both", expand=True)

    def _mostrar_activa(self):
        self.frame_setup.pack_forget()
        self.frame_cerrada.pack_forget()
        self.frame_activa.pack(fill="both", expand=True)

    def _mostrar_cerrada(self):
        self.frame_setup.pack_forget()
        self.frame_activa.pack_forget()
        self.frame_cerrada.pack(fill="both", expand=True)

    # =======================================================
    # ACCIONES DE LA SESIÓN
    # =======================================================

    def _iniciar_sesion(self):
        a = self.entry_a.get().strip()
        b = self.entry_b.get().strip()
        t = self.entry_tarea.get().strip()
        if not a or not b or not t:
            messagebox.showwarning("Datos incompletos",
                                   "Debes completar los dos nombres y la tarea.")
            return

        prog_a = Programador(a, 1)
        prog_b = Programador(b, 2)
        self.pareja = Pareja(prog_a, prog_b)
        self.pareja.asignar_roles_iniciales()
        self.sesion = SesionPairProgramming(self.pareja, Tarea(t))

        # Configurar duración del cronómetro según el radio button
        self.duracion_intervalo = self.var_intervalo.get() * 60
        self.tiempo_restante = self.duracion_intervalo

        self.label_tarea.configure(text=t)
        self.label_nombre_a.configure(text=a)
        self.label_nombre_b.configure(text=b)
        self._actualizar_etiquetas_roles()
        self.status.configure(text="Sesión activa", bg="#B5D4F4", fg="#0C447C")
        self._aplicar_color(self.BG_CONDUCTOR_A)
        self._mostrar_activa()
        self._iniciar_timer()

    def _actualizar_etiquetas_roles(self):
        rol_a = self.pareja.miembros[0].rol
        rol_b = self.pareja.miembros[1].rol
        self.label_rol_a.configure(text=rol_a,
            bg="#0C447C" if rol_a == "Conductor" else "#444441",
            fg="#E6F1FB" if rol_a == "Conductor" else "#F1EFE8")
        self.label_rol_b.configure(text=rol_b,
            bg="#0C447C" if rol_b == "Conductor" else "#444441",
            fg="#E6F1FB" if rol_b == "Conductor" else "#F1EFE8")

    def _rotar_roles(self):
        if self.en_break or self.pareja is None:
            return
        self.pareja.rotar_roles()
        self._actualizar_etiquetas_roles()
        if self.pareja.miembros[0].rol == "Conductor":
            self._aplicar_color(self.BG_CONDUCTOR_A)
        else:
            self._aplicar_color(self.BG_CONDUCTOR_B)
        # Cada vez que se rota (manual o automático), reiniciar el cronómetro
        self._reiniciar_timer()

    def _toggle_break(self):
        self.en_break = not self.en_break
        if self.en_break:
            self.btn_break.configure(text="Reanudar")
            self.btn_rotar.configure(state="disabled")
            self.status.configure(text="En pausa", bg="#D3D1C7", fg="#444441")
            self._aplicar_color(self.BG_BREAK)
            self._pausar_timer()
        else:
            self.btn_break.configure(text="Tomar break")
            self.btn_rotar.configure(state="normal")
            self.status.configure(text="Sesión activa", bg="#B5D4F4", fg="#0C447C")
            if self.pareja.miembros[0].rol == "Conductor":
                self._aplicar_color(self.BG_CONDUCTOR_A)
            else:
                self._aplicar_color(self.BG_CONDUCTOR_B)
            self._iniciar_timer()

    def _agregar_comentario(self):
        texto = self.entry_comentario.get().strip()
        if not texto:
            return
        self.sesion.agregar_observacion(texto)
        self.lista_comentarios.insert("end", f"• {texto}")
        self.entry_comentario.delete(0, "end")

    def _actualizar_cierre(self):
        if self.var_commit.get():
            self.sesion.marcar_commit()
        else:
            self.sesion.commit_realizado = False
        if self.var_push.get():
            self.sesion.marcar_push()
        else:
            self.sesion.push_realizado = False
        if self.var_commit.get() and self.var_push.get():
            self.btn_cerrar.configure(state="normal")
        else:
            self.btn_cerrar.configure(state="disabled")

    def _cerrar_sesion(self):
        if self.sesion.cerrar():
            self._pausar_timer()
            resumen = (
                f"Pareja: {self.pareja.miembros[0].nombre} y "
                f"{self.pareja.miembros[1].nombre}\n"
                f"Tarea: {self.sesion.tarea.descripcion}\n"
                f"Comentarios registrados: {len(self.sesion.observaciones)}\n"
                f"Intervalo de rotación: {self.duracion_intervalo // 60} minutos\n"
                f"Inicio: {self.sesion.inicio.strftime('%H:%M:%S')}  "
                f"Fin: {self.sesion.fin.strftime('%H:%M:%S')}"
            )

            # Guardar la sesión en el archivo de historial
            guardado_ok, ruta = self._guardar_en_archivo()
            if guardado_ok:
                resumen += f"\n\nHistorial guardado en:\n{ruta}"
            else:
                resumen += f"\n\n(No se pudo guardar el historial: {ruta})"

            self.label_resumen.configure(text=resumen)
            self.status.configure(text="Cerrada", bg="#9FE1CB", fg="#0F6E56")
            self._aplicar_color(self.BG_CLOSED)
            self._mostrar_cerrada()

    def _guardar_en_archivo(self):
        """Guarda los datos de la sesión en historial_sesiones.txt.
        Si el archivo no existe, lo crea con un encabezado.
        Si ya existe, agrega la nueva sesión al final.
        Devuelve (True, ruta) si todo salió bien, (False, mensaje_error) si falló.
        """
        try:
            es_primera_vez = not os.path.exists(ARCHIVO_HISTORIAL)
            ruta_absoluta = os.path.abspath(ARCHIVO_HISTORIAL)

            # Armar el texto de la sesión que se va a escribir
            fecha = self.sesion.fin.strftime("%d/%m/%Y")
            hora_inicio = self.sesion.inicio.strftime("%H:%M:%S")
            hora_fin = self.sesion.fin.strftime("%H:%M:%S")
            duracion = (self.sesion.fin - self.sesion.inicio).total_seconds()
            duracion_min = int(duracion // 60)
            duracion_seg = int(duracion % 60)

            lineas = []
            lineas.append("=" * 60)
            lineas.append(f"SESIÓN DEL {fecha}")
            lineas.append("=" * 60)
            lineas.append(f"Pareja:                {self.pareja.miembros[0].nombre} "
                          f"y {self.pareja.miembros[1].nombre}")
            lineas.append(f"Tarea:                 {self.sesion.tarea.descripcion}")
            lineas.append(f"Intervalo de rotación: {self.duracion_intervalo // 60} minutos")
            lineas.append(f"Hora de inicio:        {hora_inicio}")
            lineas.append(f"Hora de cierre:        {hora_fin}")
            lineas.append(f"Duración total:        {duracion_min} min {duracion_seg} seg")
            lineas.append(f"Commit realizado:      {'Sí' if self.sesion.commit_realizado else 'No'}")
            lineas.append(f"Push al repositorio:   {'Sí' if self.sesion.push_realizado else 'No'}")
            lineas.append(f"Comentarios ({len(self.sesion.observaciones)}):")
            if self.sesion.observaciones:
                for i, obs in enumerate(self.sesion.observaciones, 1):
                    lineas.append(f"  {i}. {obs}")
            else:
                lineas.append("  (sin comentarios registrados)")
            lineas.append("")  # línea en blanco al final

            # Modo "a" (append) crea el archivo si no existe y agrega al final si existe
            with open(ARCHIVO_HISTORIAL, "a", encoding="utf-8") as f:
                if es_primera_vez:
                    f.write("HISTORIAL DE SESIONES DE PAIR PROGRAMMING\n")
                    f.write(f"Archivo creado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                f.write("\n".join(lineas) + "\n")

            return True, ruta_absoluta

        except Exception as e:
            return False, str(e)

    def _reiniciar(self):
        self._pausar_timer()
        self.entry_a.delete(0, "end")
        self.entry_b.delete(0, "end")
        self.entry_tarea.delete(0, "end")
        self.lista_comentarios.delete(0, "end")
        self.var_commit.set(False)
        self.var_push.set(False)
        self.var_intervalo.set(30)
        self.btn_cerrar.configure(state="disabled")
        self.btn_break.configure(text="Tomar break")
        self.btn_rotar.configure(state="normal")
        self.en_break = False
        self.pareja = None
        self.sesion = None
        self.duracion_intervalo = 30 * 60
        self.tiempo_restante = self.duracion_intervalo
        self.label_timer.configure(text="30:00", fg=self.FG_DARK)
        self.status.configure(text="No iniciada", bg="#D3D1C7", fg="#444441")
        self._aplicar_color(self.BG_DEFAULT)
        self._mostrar_setup()


def main():
    root = tk.Tk()
    PairProgrammingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()