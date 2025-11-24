import tkinter as tk
from tkinter import ttk, messagebox
import math


# =======================================================
#  CLASES DE AUTÓMATAS
# =======================================================
class AFND:
    def __init__(self, estados, alfabeto, trans, inicial, aceptacion):
        self.estados = set(estados)
        self.alfabeto = set(alfabeto)
        self.trans = dict(trans)
        self.inicial = inicial
        self.aceptacion = set(aceptacion)


class AFD:
    def __init__(self, estados, alfabeto, transiciones, inicial, aceptacion):
        self.estados = estados
        self.alfabeto = alfabeto
        self.trans = transiciones
        self.inicial = inicial
        self.aceptacion = aceptacion


def convertir_a_afd(afnd: AFND) -> AFD:
    inicial_afd = frozenset([afnd.inicial])
    por_procesar = [inicial_afd]
    procesados = set()

    trans_afd = {}
    estados_afd = set()
    acept_afd = set()

    sumidero = frozenset(["⊥"])

    while por_procesar:
        S = por_procesar.pop(0)

        if S in procesados:
            continue

        procesados.add(S)
        estados_afd.add(S)

        if any(q in afnd.aceptacion for q in S):
            acept_afd.add(S)

        for simbolo in afnd.alfabeto:
            nuevo = set()

            for q in S:
                if (q, simbolo) in afnd.trans:
                    destinos = afnd.trans[(q, simbolo)]
                    nuevo.update(destinos)

            S_prime = sumidero if len(nuevo) == 0 else frozenset(nuevo)
            trans_afd[(S, simbolo)] = S_prime

            if S_prime not in procesados:
                por_procesar.append(S_prime)

    if sumidero not in estados_afd:
        estados_afd.add(sumidero)
        for simbolo in afnd.alfabeto:
            trans_afd[(sumidero, simbolo)] = sumidero

    return AFD(estados_afd, afnd.alfabeto, trans_afd, inicial_afd, acept_afd)


# =======================================================
#  GUI MEJORADA
# =======================================================
class AutomataGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AFND → AFD - Visualizador de Autómatas")
        self.root.configure(bg="#f0f0f0")

        # Configuración de estilos
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("TEntry", font=("Arial", 10))

        # Lado izquierdo - inputs
        input_frame = ttk.Frame(root, padding="10")
        input_frame.pack(side="left", fill="y", anchor="n")

        # Canvas para dibujo
        self.canvas = tk.Canvas(
            root,
            width=900,
            height=650,
            bg="white",
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        self.canvas.pack(side="right", padx=10, pady=10)

        # Inputs
        ttk.Label(input_frame, text="Estados (separados por coma):").pack(anchor="w", pady=(0, 5))
        self.estados_entry = ttk.Entry(input_frame, width=30)
        self.estados_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(input_frame, text="Alfabeto (separados por coma):").pack(anchor="w", pady=(0, 5))
        self.alfabeto_entry = ttk.Entry(input_frame, width=30)
        self.alfabeto_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(input_frame, text="Transiciones (formato: q,a->q1|q2):").pack(anchor="w", pady=(0, 5))
        self.trans_entry = ttk.Entry(input_frame, width=30)
        self.trans_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(input_frame, text="Estado inicial:").pack(anchor="w", pady=(0, 5))
        self.inicial_entry = ttk.Entry(input_frame, width=30)
        self.inicial_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(input_frame, text="Estados finales (separados por coma):").pack(anchor="w", pady=(0, 5))
        self.finales_entry = ttk.Entry(input_frame, width=30)
        self.finales_entry.pack(fill="x", pady=(0, 20))

        # Botones principales
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(button_frame, text="Generar AFND", command=self.generar_afnd).pack(fill="x", pady=(0, 5))
        ttk.Button(button_frame, text="Convertir a AFD", command=self.convertir_y_dibujar_afd).pack(fill="x", pady=5)

        ttk.Label(input_frame, text="Cadena a evaluar:").pack(anchor="w", pady=(10, 5))
        self.cadena_entry = ttk.Entry(input_frame, width=30)
        self.cadena_entry.pack(fill="x", pady=(0, 10))

        ttk.Button(input_frame, text="Simular AFND", command=self.simular).pack(fill="x", pady=5)

        self.status_label = ttk.Label(input_frame, text="Estado: listo.", foreground="blue")
        self.status_label.pack(anchor="w", pady=10)

        self.afnd = None
        self.afd = None

        # Valores por defecto
        self.estados_entry.insert(0, "q1,q2,q3")
        self.alfabeto_entry.insert(0, "0,1")
        self.trans_entry.insert(0, "q1,0->q1|q2; q2,0->q1|q2; q2,1->q3; q3,0->q2; q3,1->q3")
        self.inicial_entry.insert(0, "q1")
        self.finales_entry.insert(0, "q1,q3")
        self.cadena_entry.insert(0, "0011")

    # ---------------------------------------------------------
    #  Generar AFND
    # ---------------------------------------------------------
    def generar_afnd(self):
        try:
            estados_raw = [e.strip() for e in self.estados_entry.get().split(",") if e.strip()]
            alfabeto = [a.strip() for a in self.alfabeto_entry.get().split(",") if a.strip()]

            trans = {}
            tr_raw = [t.strip() for t in self.trans_entry.get().split(";") if t.strip()]

            for t in tr_raw:
                izq, der = t.split("->")
                estado, simb = [x.strip() for x in izq.split(",")]
                dests = {d.strip() for d in der.split("|")}
                trans[(estado, simb)] = dests

            inicial = self.inicial_entry.get().strip()
            finales = {x.strip() for x in self.finales_entry.get().split(",") if x.strip()}

            self.afnd = AFND(estados_raw, alfabeto, trans, inicial, finales)
            self.status_label.config(text="AFND generado correctamente.", foreground="green")
            self.dibujar_afnd()

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar AFND: {str(e)}")

    # ---------------------------------------------------------
    def convertir_y_dibujar_afd(self):
        if not self.afnd:
            return messagebox.showerror("Error", "Primero genera un AFND")
        self.afd = convertir_a_afd(self.afnd)
        self.status_label.config(text="AFD generado correctamente.", foreground="green")
        self.dibujar_afd()

    # ---------------------------------------------------------
    #  Dibujo del automáta
    # ---------------------------------------------------------
    def dibujar_afnd(self):
        estados_list = list(self.afnd.estados)
        self.dibujar_automata(
            estados_list,
            self.afnd.trans,
            self.afnd.inicial,
            self.afnd.aceptacion,
            "AFND"
        )

    def dibujar_afd(self):
        estados_list = []
        trans = {}

        def label(s):
            if isinstance(s, frozenset):
                return "⊥" if "⊥" in s else "{" + ",".join(sorted(s)) + "}"
            return str(s)

        for e in self.afd.estados:
            estados_list.append(label(e))

        for (q, a), d in self.afd.trans.items():
            qs = label(q)
            ds = label(d)
            trans.setdefault((qs, a), set()).add(ds)

        inicial = label(self.afd.inicial)
        finales = {label(f) for f in self.afd.aceptacion}

        self.dibujar_automata(estados_list, trans, inicial, finales, "AFD")

    # ---------------------------------------------------------
    def dibujar_automata(self, estados, trans, inicial, finales, tipo):
        self.canvas.delete("all")

        # Título
        self.canvas.create_text(
            450, 20,
            text=f"Autómata: {tipo}",
            font=("Arial", 14, "bold"),
            fill="#333333"
        )

        cx, cy = 450, 300
        r = min(200, 2000 / len(estados))
        coords = {}

        # Colocar estados en un círculo
        for i, e in enumerate(estados):
            ang = 2 * math.pi * i / len(estados)
            x = cx + r * math.cos(ang)
            y = cy + r * math.sin(ang)
            coords[e] = (x, y)

        # Flecha inicial
        if inicial in coords:
            x, y = coords[inicial]
            ang = math.atan2(y - cy, x - cx)

            start_x = x - 35 * math.cos(ang)
            start_y = y - 35 * math.sin(ang)

            self.canvas.create_line(
                start_x - 30 * math.cos(ang),
                start_y - 30 * math.sin(ang),
                start_x,
                start_y,
                width=2,
                arrow=tk.LAST,
                fill="#2E86AB"
            )

        # Transiciones
        for (q, a), dests in trans.items():
            if q not in coords:
                continue

            x1, y1 = coords[q]

            for d in dests:
                if d not in coords:
                    continue

                x2, y2 = coords[d]

                if q == d:
                    self.dibujar_loop(x1, y1, a, 35)
                else:
                    self.dibujar_transicion(x1, y1, x2, y2, a)

        # Dibujar estados
        for e, (x, y) in coords.items():
            color = "#A23B72" if e in finales else "#2E86AB"
            grosor = 3 if e in finales else 2

            self.canvas.create_oval(
                x - 30, y - 30,
                x + 30, y + 30,
                width=grosor,
                outline=color,
                fill="#F8F9FA"
            )

            if e == inicial:
                self.canvas.create_oval(
                    x - 25, y - 25,
                    x + 25, y + 25,
                    width=1,
                    outline=color,
                    dash=(4, 2)
                )

            self.canvas.create_text(
                x, y,
                text=e,
                font=("Arial", 10, "bold"),
                fill="#333333"
            )

    def dibujar_loop(self, x, y, etiqueta, radio):
        """Dibuja un loop mejorado para transiciones al mismo estado."""
        self.canvas.create_arc(
            x - radio, y - radio * 2,
            x + radio, y,
            start=200,
            extent=140,
            style="arc",
            width=2,
            outline="#18A558"
        )

        ang = math.radians(320)
        fx = x + radio * 0.7 * math.cos(ang)
        fy = y - radio * 1.3 * math.sin(ang)

        px = x + radio * 0.6 * math.cos(ang - 0.1)
        py = y - radio * 1.2 * math.sin(ang - 0.1)

        self.canvas.create_line(
            px, py, fx, fy,
            width=2,
            arrow=tk.LAST,
            fill="#18A558"
        )

        self.canvas.create_text(
            x, y - radio * 1.7,
            text=etiqueta,
            font=("Arial", 9),
            fill="#18A558"
        )

    def dibujar_transicion(self, x1, y1, x2, y2, etiqueta):
        """Dibuja una transición curva entre dos estados."""
        dx = x2 - x1
        dy = y2 - y1
        dist = math.sqrt(dx * dx + dy * dy)

        if dist == 0:
            return

        factor = 0.3
        ctrl_x = (x1 + x2) / 2 - dy * factor
        ctrl_y = (y1 + y2) / 2 + dx * factor

        self.canvas.create_line(
            x1, y1, ctrl_x, ctrl_y, x2, y2,
            smooth=True,
            width=2,
            arrow=tk.LAST,
            fill="#F18F01"
        )

        label_x = (x1 + x2 + ctrl_x) / 3
        label_y = (y1 + y2 + ctrl_y) / 3

        self.canvas.create_text(
            label_x, label_y - 10,
            text=etiqueta,
            font=("Arial", 9),
            fill="#F18F01"
        )

    # ---------------------------------------------------------
    #  Simulación AFND
    # ---------------------------------------------------------
    def simular(self):
        if not self.afnd:
            return messagebox.showerror("Error", "Primero genera un AFND.")

        cadena = self.cadena_entry.get().strip()
        if not cadena:
            return messagebox.showerror("Error", "Ingresa una cadena para simular.")

        estados = {self.afnd.inicial}

        for c in cadena:
            nuevos = set()
            for e in estados:
                if (e, c) in self.afnd.trans:
                    nuevos.update(self.afnd.trans[(e, c)])
            estados = nuevos

        if estados & self.afnd.aceptacion:
            messagebox.showinfo("Resultado", f"Cadena '{cadena}' ACEPTADA por el AFND")
        else:
            messagebox.showinfo("Resultado", f"Cadena '{cadena}' RECHAZADA por el AFND")


# =======================================================
#  MAIN
# =======================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = AutomataGUI(root)
    root.mainloop()