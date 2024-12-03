import tkinter as tk
from tkinter import messagebox
import json
import os

# Archivo para guardar los datos
DATA_FILE = "notas_estudiante.json"

# Función para cargar datos del archivo JSON
def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Función para guardar datos en el archivo JSON
def guardar_datos(datos):
    with open(DATA_FILE, "w") as file:
        json.dump(datos, file, indent=4)

# Clase principal de la aplicación
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Notas Universitarias")
        self.datos = cargar_datos()

        # Pantalla principal
        self.frame_principal = tk.Frame(root)
        self.frame_principal.pack(fill="both", expand=True)
        self.crear_pantalla_principal()

    def limpiar_frame(self):
        """Elimina todos los widgets del frame actual."""
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

    def crear_pantalla_principal(self):
        self.limpiar_frame()
        self.frame_principal.pack(fill="both", expand=True)

        # Botón para añadir una materia
        btn_anadir_materia = tk.Button(
            self.frame_principal, text="+ Añadir Materia", command=self.anadir_materia
        )
        btn_anadir_materia.pack(pady=20)

        # Mostrar materias existentes
        for materia, datos in self.datos.items():
            btn_materia = tk.Button(
                self.frame_principal,
                text=f"{materia} (Semestre {datos['semestre']})",
                command=lambda m=materia: self.ver_materia(m),
            )
            btn_materia.pack(pady=5)

    def anadir_materia(self):
        def guardar_materia():
            nombre = entry_nombre.get().strip()
            semestre = entry_semestre.get().strip()
            examen = entry_examen.get().strip()
            practicas = entry_practicas.get().strip()

            if not nombre or not semestre or not examen or not practicas:
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return

            if nombre in self.datos:
                messagebox.showerror("Error", "La materia ya existe")
                return

            self.datos[nombre] = {
                "semestre": semestre,
                "peso_examen": int(examen),
                "peso_practicas": int(practicas),
                "competencias": [],
            }
            guardar_datos(self.datos)
            self.crear_pantalla_principal()

        self.limpiar_frame()
        tk.Label(self.frame_principal, text="Nombre de la materia:").pack()
        entry_nombre = tk.Entry(self.frame_principal)
        entry_nombre.pack()

        tk.Label(self.frame_principal, text="Semestre:").pack()
        entry_semestre = tk.Entry(self.frame_principal)
        entry_semestre.pack()

        tk.Label(self.frame_principal, text="Peso (%) Examen:").pack()
        entry_examen = tk.Entry(self.frame_principal)
        entry_examen.pack()

        tk.Label(self.frame_principal, text="Peso (%) Prácticas:").pack()
        entry_practicas = tk.Entry(self.frame_principal)
        entry_practicas.pack()

        tk.Button(self.frame_principal, text="Guardar", command=guardar_materia).pack(pady=10)
        tk.Button(self.frame_principal, text="Volver", command=self.crear_pantalla_principal).pack(pady=10)

    def ver_materia(self, materia):
        def anadir_competencia():
            self.limpiar_frame()

            def definir_tareas():
                try:
                    cantidad_tareas = int(entry_tareas.get())
                    if cantidad_tareas <= 0:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Error", "Ingresa un número válido de tareas")
                    return
                self.registrar_notas_competencia(materia, cantidad_tareas)

            tk.Label(self.frame_principal, text="Cantidad de tareas:").pack()
            entry_tareas = tk.Entry(self.frame_principal)
            entry_tareas.pack()

            tk.Button(self.frame_principal, text="Siguiente", command=definir_tareas).pack(pady=10)
            tk.Button(self.frame_principal, text="Volver", command=lambda: self.ver_materia(materia)).pack(pady=10)

        def editar_competencia(idx):
            self.editar_notas_competencia(materia, idx)

        def eliminar_competencia(idx):
            del self.datos[materia]["competencias"][idx]
            guardar_datos(self.datos)
            self.ver_materia(materia)

        self.limpiar_frame()
        tk.Label(self.frame_principal, text=f"Materia: {materia}").pack()
        tk.Label(self.frame_principal, text=f"Semestre: {self.datos[materia]['semestre']}").pack()
        tk.Label(self.frame_principal, text=f"Peso Examen: {self.datos[materia]['peso_examen']}%").pack()
        tk.Label(self.frame_principal, text=f"Peso Prácticas: {self.datos[materia]['peso_practicas']}%").pack()

        tk.Button(self.frame_principal, text="+ Añadir Competencia", command=anadir_competencia).pack(pady=10)

        promedio_materia = 0
        if self.datos[materia]["competencias"]:
            promedio_materia = sum(
                c["promedio_final"] for c in self.datos[materia]["competencias"]
            ) / len(self.datos[materia]["competencias"])

        for idx, comp in enumerate(self.datos[materia]["competencias"], start=1):
            frame_competencia = tk.Frame(self.frame_principal)
            frame_competencia.pack(fill="x", pady=5)

            tk.Label(frame_competencia, text=f"Competencia {idx}: Promedio Final = {comp['promedio_final']:.2f}").pack(side="left")
            tk.Button(frame_competencia, text="Editar", command=lambda idx=idx-1: editar_competencia(idx)).pack(side="right")
            tk.Button(frame_competencia, text="Eliminar", command=lambda idx=idx-1: eliminar_competencia(idx)).pack(side="right")

        tk.Label(self.frame_principal, text=f"Promedio de la materia: {promedio_materia:.2f}").pack(pady=10)
        tk.Button(self.frame_principal, text="Volver", command=self.crear_pantalla_principal).pack(pady=10)

    def registrar_notas_competencia(self, materia, cantidad_tareas):
        def guardar_notas():
            try:
                nota_examen = float(entry_examen.get())
                if nota_examen < 0 or nota_examen > 100:
                    raise ValueError

                notas_tareas = []
                for i in range(cantidad_tareas):
                    nota_tarea = float(entries_tareas[i].get())
                    if nota_tarea < 0 or nota_tarea > 100:
                        raise ValueError
                    notas_tareas.append(nota_tarea)

                promedio_practicas = sum(notas_tareas) / len(notas_tareas)
                promedio_final = (
                    (nota_examen * self.datos[materia]["peso_examen"] / 100)
                    + (promedio_practicas * self.datos[materia]["peso_practicas"] / 100)
                )

                self.datos[materia]["competencias"].append({
                    "nota_examen": nota_examen,
                    "notas_tareas": notas_tareas,
                    "promedio_final": promedio_final,
                })
                guardar_datos(self.datos)
                self.ver_materia(materia)

            except ValueError:
                messagebox.showerror("Error", "Ingresa notas válidas entre 0 y 100")

        self.limpiar_frame()
        tk.Label(self.frame_principal, text="Ingresa la nota del examen:").pack()
        entry_examen = tk.Entry(self.frame_principal)
        entry_examen.pack()

        entries_tareas = []
        for i in range(cantidad_tareas):
            tk.Label(self.frame_principal, text=f"Nota de la tarea {i + 1}:").pack()
            entry = tk.Entry(self.frame_principal)
            entry.pack()
            entries_tareas.append(entry)

        tk.Button(self.frame_principal, text="Guardar", command=guardar_notas).pack(pady=10)
        tk.Button(self.frame_principal, text="Volver", command=lambda: self.ver_materia(materia)).pack(pady=10)

    def editar_notas_competencia(self, materia, idx):
        competencia = self.datos[materia]["competencias"][idx]
        cantidad_tareas = len(competencia["notas_tareas"])

        def guardar_cambios():
            try:
                nota_examen = float(entry_examen.get())
                if nota_examen < 0 or nota_examen > 100:
                    raise ValueError

                notas_tareas = []
                for i in range(cantidad_tareas):
                    nota_tarea = float(entries_tareas[i].get())
                    if nota_tarea < 0 or nota_tarea > 100:
                        raise ValueError
                    notas_tareas.append(nota_tarea)

                promedio_practicas = sum(notas_tareas) / len(notas_tareas)
                promedio_final = (
                    (nota_examen * self.datos[materia]["peso_examen"] / 100)
                    + (promedio_practicas * self.datos[materia]["peso_practicas"] / 100)
                )

                self.datos[materia]["competencias"][idx] = {
                    "nota_examen": nota_examen,
                    "notas_tareas": notas_tareas,
                    "promedio_final": promedio_final,
                }
                guardar_datos(self.datos)
                self.ver_materia(materia)

            except ValueError:
                messagebox.showerror("Error", "Ingresa notas válidas entre 0 y 100")

        self.limpiar_frame()
        tk.Label(self.frame_principal, text="Editar nota del examen:").pack()
        entry_examen = tk.Entry(self.frame_principal)
        entry_examen.insert(0, competencia["nota_examen"])
        entry_examen.pack()

        entries_tareas = []
        for i in range(cantidad_tareas):
            tk.Label(self.frame_principal, text=f"Editar nota de la tarea {i + 1}:").pack()
            entry = tk.Entry(self.frame_principal)
            entry.insert(0, competencia["notas_tareas"][i])
            entry.pack()
            entries_tareas.append(entry)

        tk.Button(self.frame_principal, text="Guardar cambios", command=guardar_cambios).pack(pady=10)
        tk.Button(self.frame_principal, text="Volver", command=lambda: self.ver_materia(materia)).pack(pady=10)

# Inicializar aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    