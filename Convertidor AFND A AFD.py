import xml.etree.ElementTree as ET
from xml.dom import minidom

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

        if sumidero in estados_afd or any(dest == sumidero for dest in trans_afd.values()):
            estados_afd.add(sumidero)
            for simbolo in afnd.alfabeto:
                if (sumidero, simbolo) not in trans_afd:
                    trans_afd[(sumidero, simbolo)] = sumidero

        return AFD(estados_afd, afnd.alfabeto, trans_afd, inicial_afd, acept_afd)

def formatear_estado(estado_set):
        if isinstance(estado_set, str):
            return estado_set
        if list(estado_set) == ["⊥"]:
            return "⊥"
        sorted_states = sorted(list(estado_set))
        return "{" + ",".join(sorted_states) + "}"

def leer_afnd_desde_txt(ruta_archivo):
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            lineas = [l.strip() for l in f.readlines() if l.strip()]

        estados = lineas[0].split(',')
        alfabeto = lineas[1].split(',')
        inicial = lineas[2]
        aceptacion = lineas[3].split(',')

        trans = {}
        for linea in lineas[4:]:
            partes = linea.split(',')
            if len(partes) >= 3:
                origen = partes[0]
                simbolo = partes[1]
                destino = partes[2]

                clave = (origen, simbolo)
                if clave not in trans:
                    trans[clave] = set()
                trans[clave].add(destino)

        return AFND(estados, alfabeto, trans, inicial, aceptacion)

def escribir_afd_en_txt(afd, ruta_archivo):
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            lista_estados = [formatear_estado(e) for e in afd.estados]
            f.write(",".join(lista_estados) + "\n")

            f.write(",".join(sorted(list(afd.alfabeto))) + "\n")

            f.write(formatear_estado(afd.inicial) + "\n")

            lista_aceptacion = [formatear_estado(e) for e in afd.aceptacion]
            f.write(",".join(lista_aceptacion) + "\n")

            for (origen, simbolo), destino in afd.trans.items():
                linea = f"{formatear_estado(origen)},{simbolo},{formatear_estado(destino)}\n"
                f.write(linea)

def generar_jff(automata, ruta_salida, es_afd=False):
        root = ET.Element("structure")
        ET.SubElement(root, "type").text = "fa"
        automaton_elem = ET.SubElement(root, "automaton")

        state_to_id = {}
        lista_estados = list(automata.estados)

        for i, estado in enumerate(lista_estados):
            state_id = str(i)
            state_to_id[estado] = state_id

            nombre_legible = formatear_estado(estado) if es_afd else estado

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

def main():
        try:
            print("Leyendo 'lectura.txt'...")
            afnd = leer_afnd_desde_txt("lectura.txt")

            print("Generando 'afnd.jff'...")
            generar_jff(afnd, "afnd.jff", es_afd=False)

            print("Convirtiendo AFND a AFD...")
            afd = convertir_a_afd(afnd)

            print("Generando 'resultado.txt'...")
            escribir_afd_en_txt(afd, "resultado.txt")

            print("Generando 'afd.jff'...")
            generar_jff(afd, "afd.jff", es_afd=True)

            print("¡Proceso completado!")
        except FileNotFoundError:
            print("Error: No se encontró 'lectura.txt'.")
        except Exception as e:
            print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
        main()