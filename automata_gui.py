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


# ==========================================
# CLASES DE AUTÓMATAS (no modificadas)
# ==========================================

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
                    nuevo.update(afnd.trans[(q, simbolo)])

            S_prime = sumidero if len(nuevo) == 0 else frozenset(nuevo)
            trans_afd[(S, simbolo)] = S_prime

            if S_prime not in procesados:
                por_procesar.append(S_prime)

    # Transiciones sumidero
    estados_afd.add(sumidero)
    for simbolo in afnd.alfabeto:
        trans_afd[(sumidero, simbolo)] = sumidero

    return AFD(estados_afd, afnd.alfabeto, trans_afd, inicial_afd, acept_afd)

# ==========================================
# NUEVA GUI SOLO INPUT + EXPORTACIÓN TXT
# ==========================================


class AutomataGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de AFND a AFD - Exportación TXT/JFLAP")
        self.root.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0")
        self.style.configure("TButton", font=("Arial", 10))

        frame = ttk.Frame(root, padding="10")
        frame.pack(fill="both", expand=True)

        # Campo de texto grande
        ttk.Label(frame, text="Autómata (1 elemento por línea):").pack(
            anchor="w")

        self.automata_text = tk.Text(frame, font=("Consolas", 11), height=15)
        self.automata_text.pack(fill="both", expand=True, pady=10)

        footer = (
            "Línea 1: Estados (ejemplo: q1,q2,q3)\n"
            "Línea 2: Alfabeto (ejemplo: 0,1)\n"
            "Línea 3: Estado inicial\n"
            "Línea 4: Estados de aceptación\n"
            "Línea 5: Transiciones (ejemplo: q1,0->q1|q2; q2,1->q3)\n"
        )
        ttk.Label(frame, text=footer, font=("Arial", 8),
                  foreground="gray").pack(anchor="w")

        # Botones
        ttk.Button(frame, text="Generar AFND",
                   command=self.generar_afnd).pack(fill="x", pady=5)
        ttk.Button(frame, text="Convertir a AFD",
                   command=self.convertir_a_afd).pack(fill="x", pady=5)
        ttk.Button(frame, text="Exportar JFLAP",
                   command=self.exportar_jflap).pack(fill="x", pady=5)

        self.afnd = None
        self.afd = None

        # Datos por defecto
        texto_defecto = (
            "q1,q2,q3\n"
            "0,1\n"
            "q1\n"
            "q1,q3\n"
            "q1,0->q1|q2; q2,0->q1|q2; q2,1->q3; q3,0->q2; q3,1->q3\n"
        )
        self.automata_text.insert("1.0", texto_defecto)

    # =====================================================
    # Parser y generación de AFND (igual que antes)
    # =====================================================
    def generar_afnd(self):
        try:
            lineas = self.automata_text.get("1.0", tk.END).strip().split("\n")
            if len(lineas) < 5:
                raise ValueError("Debes ingresar al menos 5 líneas.")

            estados = [e.strip() for e in lineas[0].split(",") if e.strip()]
            alfabeto = [a.strip() for a in lineas[1].split(",") if a.strip()]
            inicial = lineas[2].strip()
            aceptacion = {x.strip() for x in lineas[3].split(",") if x.strip()}

            trans = {}
            trans_raw = [t.strip() for t in lineas[4].split(";") if t.strip()]

            for t in trans_raw:
                izq, der = t.split("->")
                estado, simb = [x.strip() for x in izq.split(",")]
                destinos = {d.strip() for d in der.split("|")}
                trans[(estado, simb)] = destinos

            self.afnd = AFND(estados, alfabeto, trans, inicial, aceptacion)
            self.exportar_afnd()  # mantiene el comportamiento anterior
            messagebox.showinfo("Éxito", "Archivo AFND.txt generado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =====================================================
    # Conversión a AFD (igual que antes)
    # =====================================================
    def convertir_a_afd(self):
        if not self.afnd:
            return messagebox.showerror("Error", "Primero genera un AFND.")
        self.afd = convertir_a_afd(self.afnd)
        self.exportar_afd()
        messagebox.showinfo("Éxito", "Archivo AFD.txt generado.")

    # =====================================================
    # Exportar AFND a .txt (igual que antes)
    # =====================================================
    def exportar_afnd(self, archivo="AFND.txt"):
        with open(archivo, "w", encoding="utf-8") as f:
            f.write("===========================\n")
            f.write("        AFND GENERADO\n")
            f.write("===========================\n\n")

            f.write(f"Estados: {', '.join(self.afnd.estados)}\n")
            f.write(f"Alfabeto: {', '.join(self.afnd.alfabeto)}\n")
            f.write(f"Estado inicial: {self.afnd.inicial}\n")
            f.write(
                f"Estados de aceptación: {', '.join(self.afnd.aceptacion)}\n\n")

            f.write("TABLA DE TRANSICIONES\n")
            f.write("-------------------------------------------------------------\n")
            f.write("| ESTADO | SÍMBOLO |              DESTINOS                  |\n")
            f.write("-------------------------------------------------------------\n")

            for (estado, simbolo), destinos in self.afnd.trans.items():
                dests = ", ".join(sorted(destinos))
                f.write(f"| {estado:<7}| {simbolo:^7}| {dests:<30} |\n")

            f.write("-------------------------------------------------------------\n")

    # =====================================================
    # Exportar AFD a .txt (igual que antes)
    # =====================================================
    def exportar_afd(self, archivo="AFD.txt"):
        with open(archivo, "w", encoding="utf-8") as f:
            f.write("===========================\n")
            f.write("        AFD GENERADO\n")
            f.write("===========================\n\n")

            f.write(
                f"Estado inicial: {self.label_estado(self.afd.inicial)}\n\n")
            f.write("Estados de aceptación:\n")
            for a in sorted(self.afd.aceptacion, key=lambda x: str(x)):
                f.write(f" - {self.label_estado(a)}\n")
            f.write("\n")

            f.write("TABLA DE TRANSICIONES\n")
            f.write("-------------------------------------------------------------\n")
            f.write("|       ESTADO       | SÍMBOLO |        DESTINO            |\n")
            f.write("-------------------------------------------------------------\n")

            for (S, simbolo), destino in self.afd.trans.items():
                s_label = self.label_estado(S)
                d_label = self.label_estado(destino)
                f.write(
                    f"| {s_label:<17} |   {simbolo:^5}  | {d_label:<22} |\n")

            f.write("-------------------------------------------------------------\n")

    # =====================================================
    # Helper para representar estados del AFD
    # =====================================================
    def label_estado(self, S):
        if isinstance(S, frozenset):
            if "⊥" in S:
                return "⊥"
            return "{" + ",".join(sorted(S)) + "}"
        return str(S)

    # =====================================================
    # EXPORTAR A JFLAP 7 (.jff)
    # - guarda en la misma carpeta del script: AFND.jff y/o AFD.jff
    # - para AFD renombra estados como q0,q1,... y agrega <label>{...}</label>
    # =====================================================
    def exportar_jflap(self):
        """Exporta AFND.jff y/o AFD.jff en la carpeta del script según qué exista."""
        try:
            # importar aquí para no requerirlos globalmente
            import xml.etree.ElementTree as ET
            from xml.dom import minidom
            import math
            import os

            def prettify(elem):
                """Return a pretty-printed XML string for the Element."""
                rough_string = ET.tostring(elem, 'utf-8')
                reparsed = minidom.parseString(rough_string)
                return reparsed.toprettyxml(indent="  ", encoding='utf-8')

            # ---------- Export AFND ----------
            if self.afnd:
                root = ET.Element('structure')
                t = ET.SubElement(root, 'type')
                t.text = 'fa'
                automaton = ET.SubElement(root, 'automaton')

                # assign numeric ids for AFND states
                states = list(self.afnd.estados)
                ids = {s: i for i, s in enumerate(states)}

                # positions in a circle for visibility
                cx, cy = 200, 200
                R = min(150, 30 * len(states))
                for i, s in enumerate(states):
                    ang = 2 * math.pi * i / len(states)
                    x = cx + R * math.cos(ang)
                    y = cy + R * math.sin(ang)
                    st = ET.SubElement(automaton, 'state',
                                       id=str(ids[s]), name=str(s))
                    ET.SubElement(st, 'x').text = str(int(x))
                    ET.SubElement(st, 'y').text = str(int(y))
                    # label optional (keep original name visible)
                    ET.SubElement(st, 'label').text = str(s)
                    if s == self.afnd.inicial:
                        ET.SubElement(st, 'initial')
                    if s in self.afnd.aceptacion:
                        ET.SubElement(st, 'final')

                # transitions
                for (src, sym), dests in self.afnd.trans.items():
                    for d in dests:
                        tr = ET.SubElement(automaton, 'transition')
                        ET.SubElement(tr, 'from').text = str(ids[src])
                        ET.SubElement(tr, 'to').text = str(ids[d])
                        # empty read element if symbol is empty (shouldn't happen here)
                        ET.SubElement(
                            tr, 'read').text = sym if sym != '' else ''

                # write file
                bytes_xml = prettify(root)
                path = os.path.join(os.getcwd(), "AFND.jff")
                with open(path, 'wb') as fh:
                    fh.write(bytes_xml)

            # ---------- Export AFD ----------
            if self.afd:
                root = ET.Element('structure')
                t = ET.SubElement(root, 'type')
                t.text = 'fa'
                automaton = ET.SubElement(root, 'automaton')

                # renombrar estados (frozenset -> q0, q1, ...)
                estados_afd = list(self.afd.estados)
                # deterministically sort by string representation for stable naming
                estados_afd_sorted = sorted(
                    estados_afd, key=lambda s: self.label_estado(s))
                name_map = {}
                for i, s in enumerate(estados_afd_sorted):
                    name_map[s] = f"q{i}"

                # positions
                cx, cy = 200, 200
                R = min(150, 30 * len(estados_afd_sorted))
                for i, s in enumerate(estados_afd_sorted):
                    ang = 2 * math.pi * i / len(estados_afd_sorted)
                    x = cx + R * math.cos(ang)
                    y = cy + R * math.sin(ang)
                    st = ET.SubElement(automaton, 'state',
                                       id=str(i), name=name_map[s])
                    ET.SubElement(st, 'x').text = str(int(x))
                    ET.SubElement(st, 'y').text = str(int(y))
                    # label contains the original set (use label element)
                    ET.SubElement(st, 'label').text = self.label_estado(s)
                    if s == self.afd.inicial:
                        ET.SubElement(st, 'initial')
                    if s in self.afd.aceptacion:
                        ET.SubElement(st, 'final')

                # transitions
                # we need to map (S, simbolo) keys to numeric ids for from/to
                inv_map = {s: i for i, s in enumerate(estados_afd_sorted)}
                for (S, simbolo), destino in self.afd.trans.items():
                    if S not in inv_map or destino not in inv_map:
                        # skip silently if something unexpected
                        continue
                    tr = ET.SubElement(automaton, 'transition')
                    ET.SubElement(tr, 'from').text = str(inv_map[S])
                    ET.SubElement(tr, 'to').text = str(inv_map[destino])
                    ET.SubElement(
                        tr, 'read').text = simbolo if simbolo != '' else ''

                # write file
                bytes_xml = prettify(root)
                path = os.path.join(os.getcwd(), "AFD.jff")
                with open(path, 'wb') as fh:
                    fh.write(bytes_xml)

            # Notify success
            if self.afnd and self.afd:
                messagebox.showinfo(
                    "Éxito", "AFND.jff y AFD.jff generados en la carpeta del script.")
            elif self.afnd:
                messagebox.showinfo(
                    "Éxito", "AFND.jff generado en la carpeta del script.")
            elif self.afd:
                messagebox.showinfo(
                    "Éxito", "AFD.jff generado en la carpeta del script.")
            else:
                messagebox.showwarning(
                    "Nada que exportar", "No hay AFND ni AFD para exportar. Genéralos primero.")

        except Exception as e:
            messagebox.showerror("Error exportando JFLAP", str(e))

# =======================================================
#  MAIN
# =======================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = AutomataGUI(root)
    root.mainloop()
