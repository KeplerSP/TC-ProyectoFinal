import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os

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

# =======================================================
#  LÓGICA DE CONVERSIÓN
# =======================================================
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

    # Manejo del estado sumidero si fue generado
    if sumidero in estados_afd or any(dest == sumidero for dest in trans_afd.values()):
        estados_afd.add(sumidero)
        for simbolo in afnd.alfabeto:
            if (sumidero, simbolo) not in trans_afd:
                trans_afd[(sumidero, simbolo)] = sumidero

    return AFD(estados_afd, afnd.alfabeto, trans_afd, inicial_afd, acept_afd)

# =======================================================
#  UTILIDADES PARA FORMATO
# =======================================================
def formatear_estado_jflap(estado_set):
    """
    Convierte un frozenset de estados en un string legible (ej. '{q0,q1}').
    """
    if isinstance(estado_set, str):
        return estado_set
    
    lista_estados = list(estado_set)
    if not lista_estados:
        return "{}"
    if "⊥" in lista_estados:
        return "⊥"
    
    sorted_states = sorted(lista_estados)
    return "{" + ",".join(sorted_states) + "}"

# =======================================================
#  INTERFAZ GRÁFICA (GUI)
# =======================================================
class AutomataGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor AFND a AFD")
        self.root.configure(bg="#f0f0f0")

        # -----------------------------------------------------------
        # DETECTAR CARPETA DEL SCRIPT ACTUAL
        # -----------------------------------------------------------
        # Esto asegura que los archivos se guarden donde está el .py
        # y no en C:\Users\... ni en system32
        self.directorio_base = os.path.dirname(os.path.abspath(__file__))

        # Estilos
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0")
        self.style.configure("TButton", font=("Arial", 10))

        frame = ttk.Frame(root, padding="10")
        frame.pack(fill="both", expand=True)

        # Mostrar ruta detectada al usuario (solo informativo)
        lbl_info = ttk.Label(frame, text=f"Carpeta de salida: {self.directorio_base}", 
                             font=("Arial", 8), foreground="blue", wraplength=480)
        lbl_info.pack(anchor="w", pady=(0, 10))

        # --- SECCIÓN DE ENTRADA ---
        ttk.Label(frame, text="Definición del Autómata:").pack(anchor="w")

        self.automata_text = tk.Text(frame, font=("Consolas", 11), height=15)
        self.automata_text.pack(fill="both", expand=True, pady=5)

        # Footer con instrucciones
        footer = (
            "Línea 1: Conjunto de Estados (ej: q0,q1,q2)\n"
            "Línea 2: Alfabeto (ej: a,b)\n"
            "Línea 3: Estado inicial (ej: q0)\n"
            "Línea 4: Estados finales (ej: q2)\n"
            "Línea 5+: Transiciones (origen,símbolo,destino)\n"
        )
        ttk.Label(frame, text=footer, font=("Arial", 9), foreground="#555555").pack(anchor="w", pady=(0, 10))

        # --- BOTONES DE ACCIÓN ---
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="1. Generar AFND y TXT", command=self.generar_afnd).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(btn_frame, text="2. Convertir a AFD y TXT", command=self.convertir_a_afd).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(btn_frame, text="3. Exportar JFLAP (.jff)", command=self.exportar_jflap).pack(side="left", expand=True, fill="x", padx=2)

        self.afnd = None
        self.afd = None

        # Datos por defecto
        texto_defecto = (
            "q0,q1,q2\n"
            "a,b\n"
            "q0\n"
            "q2\n"
            "q0,a,q0\n"
            "q0,b,q0\n"
            "q0,a,q1\n"
            "q1,b,q2"
        )
        self.automata_text.insert("1.0", texto_defecto)

    # -----------------------------------------------------
    # 1. PARSER Y GENERACIÓN DE AFND
    # -----------------------------------------------------
    def generar_afnd(self):
        try:
            contenido = self.automata_text.get("1.0", tk.END).strip()
            if not contenido: raise ValueError("El campo de texto está vacío.")
            lineas = [l.strip() for l in contenido.split("\n") if l.strip()]
            if len(lineas) < 5: raise ValueError("Faltan líneas. Se requieren mínimo 5 líneas.")

            estados = [e.strip() for e in lineas[0].split(",") if e.strip()]
            alfabeto = [a.strip() for a in lineas[1].split(",") if a.strip()]
            inicial = lineas[2].strip()
            aceptacion = {x.strip() for x in lineas[3].split(",") if x.strip()}

            trans = {}
            for i in range(4, len(lineas)):
                partes = [p.strip() for p in lineas[i].split(",")]
                if len(partes) != 3: continue 
                
                origen, simbolo, destino = partes
                if (origen, simbolo) not in trans:
                    trans[(origen, simbolo)] = set()
                trans[(origen, simbolo)].add(destino)

            self.afnd = AFND(estados, alfabeto, trans, inicial, aceptacion)
            self.exportar_afnd_txt()
            messagebox.showinfo("Éxito", f"Archivo 'AFND.txt' generado en:\n{self.directorio_base}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # -----------------------------------------------------
    # 2. CONVERSIÓN A AFD
    # -----------------------------------------------------
    def convertir_a_afd(self):
        if not self.afnd: return messagebox.showerror("Error", "Primero genera el AFND.")
        try:
            self.afd = convertir_a_afd(self.afnd)
            self.exportar_afd_txt()
            messagebox.showinfo("Éxito", f"Archivo 'AFD.txt' generado en:\n{self.directorio_base}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # -----------------------------------------------------
    # EXPORTACIÓN TXT (Usando os.path.join con directorio_base)
    # -----------------------------------------------------
    def exportar_afnd_txt(self):
        ruta = os.path.join(self.directorio_base, "AFND.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(",".join(sorted(list(self.afnd.estados))) + "\n")
            f.write(",".join(sorted(list(self.afnd.alfabeto))) + "\n")
            f.write(self.afnd.inicial + "\n")
            f.write(",".join(sorted(list(self.afnd.aceptacion))) + "\n")
            
            claves = sorted(self.afnd.trans.keys())
            for (ori, sim) in claves:
                destinos = sorted(list(self.afnd.trans[(ori, sim)]))
                for dest in destinos:
                    f.write(f"{ori},{sim},{dest}\n")

    def exportar_afd_txt(self):
        ruta = os.path.join(self.directorio_base, "AFD.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            estados_str = [formatear_estado_jflap(e) for e in sorted(list(self.afd.estados), key=lambda x: formatear_estado_jflap(x))]
            alfabeto_str = sorted(list(self.afd.alfabeto))
            inicial_str = formatear_estado_jflap(self.afd.inicial)
            finales_str = [formatear_estado_jflap(e) for e in sorted(list(self.afd.aceptacion), key=lambda x: formatear_estado_jflap(x))]

            f.write(",".join(estados_str) + "\n")
            f.write(",".join(alfabeto_str) + "\n")
            f.write(inicial_str + "\n")
            f.write(",".join(finales_str) + "\n")

            claves = sorted(self.afd.trans.keys(), key=lambda x: (formatear_estado_jflap(x[0]), x[1]))
            for (ori, sim) in claves:
                dest = self.afd.trans[(ori, sim)]
                f.write(f"{formatear_estado_jflap(ori)},{sim},{formatear_estado_jflap(dest)}\n")

    # -----------------------------------------------------
    # 3. EXPORTACIÓN JFLAP
    # -----------------------------------------------------
    def exportar_jflap(self):
        try:
            msgs = []
            if self.afnd:
                ruta_afnd = os.path.join(self.directorio_base, "AFND.jff")
                self.generar_jff_archivo(self.afnd, ruta_afnd, es_afd=False)
                msgs.append("AFND.jff")
            
            if self.afd:
                ruta_afd = os.path.join(self.directorio_base, "AFD.jff")
                self.generar_jff_archivo(self.afd, ruta_afd, es_afd=True)
                msgs.append("AFD.jff")

            if msgs:
                messagebox.showinfo("JFLAP", f"Archivos generados en {self.directorio_base}:\n{', '.join(msgs)}")
            else:
                messagebox.showwarning("Atención", "No hay autómatas para exportar.")
        except Exception as e:
            messagebox.showerror("Error JFLAP", str(e))

    def generar_jff_archivo(self, automata, ruta_salida, es_afd=False):
        root = ET.Element("structure")
        ET.SubElement(root, "type").text = "fa"
        automaton_elem = ET.SubElement(root, "automaton")

        state_to_id = {}
        
        if es_afd:
            lista_estados = sorted(list(automata.estados), key=lambda x: formatear_estado_jflap(x))
        else:
            lista_estados = sorted(list(automata.estados))

        for i, estado in enumerate(lista_estados):
            state_id = str(i)
            state_to_id[estado] = state_id
            
            nombre_legible = formatear_estado_jflap(estado)
            
            state_elem = ET.SubElement(automaton_elem, "state", id=state_id, name=nombre_legible)
            ET.SubElement(state_elem, "x").text = str(100 + (i * 120))
            ET.SubElement(state_elem, "y").text = str(100 + (i % 2) * 100)
            
            if estado == automata.inicial:
                ET.SubElement(state_elem, "initial")
            if estado in automata.aceptacion:
                ET.SubElement(state_elem, "final")

        if es_afd:
            for (origen, simbolo), destino in automata.trans.items():
                if origen in state_to_id and destino in state_to_id:
                    trans_elem = ET.SubElement(automaton_elem, "transition")
                    ET.SubElement(trans_elem, "from").text = state_to_id[origen]
                    ET.SubElement(trans_elem, "to").text = state_to_id[destino]
                    ET.SubElement(trans_elem, "read").text = simbolo
        else:
            for (origen, simbolo), destinos in automata.trans.items():
                for destino in destinos:
                    if origen in state_to_id and destino in state_to_id:
                        trans_elem = ET.SubElement(automaton_elem, "transition")
                        ET.SubElement(trans_elem, "from").text = state_to_id[origen]
                        ET.SubElement(trans_elem, "to").text = state_to_id[destino]
                        ET.SubElement(trans_elem, "read").text = simbolo

        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(xmlstr)

# =======================================================
#  MAIN
# =======================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = AutomataGUI(root)
    root.geometry("500x600")
    root.mainloop()
