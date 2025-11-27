import sys
import os
from collections import defaultdict

# ==========================================
# 1. Definición de Clases
#    Orden: estados, alfabeto, inicial, aceptacion, trans
# ==========================================

class AFND:
    def __init__(self, estados, alfabeto, inicial, aceptacion, trans):
        self.estados = set(estados)
        self.alfabeto = set(alfabeto)
        self.inicial = inicial
        self.aceptacion = set(aceptacion)
        self.trans = dict(trans)

    def __str__(self):
        return (f"--- AFND LEÍDO ---\n"
                f"Estados: {sorted(list(self.estados))}\n"
                f"Alfabeto: {sorted(list(self.alfabeto))}\n"
                f"Inicial: {self.inicial}\n"
                f"Aceptación: {sorted(list(self.aceptacion))}\n"
                f"Transiciones: {len(self.trans)} definidas")

class AFD:
    def __init__(self, estados, alfabeto, inicial, aceptacion, transiciones):
        self.estados = estados
        self.alfabeto = alfabeto
        self.inicial = inicial
        self.aceptacion = aceptacion
        self.trans = transiciones

    def __str__(self):
        # Esta función define cómo se verá el texto dentro de resultadoAFD.txt
        def formatear_estado(s):
            if not s: return "{}"
            elementos = sorted(list(s))
            return "{" + ",".join(elementos) + "}"

        res = "=== AFD GENERADO ===\n"
        res += f"Estado Inicial: {formatear_estado(self.inicial)}\n"
        res += f"Estados de Aceptación: {[formatear_estado(s) for s in self.aceptacion]}\n"
        res += "\nTABLA DE TRANSICIONES:\n"
        res += f"{'ESTADO':<20} | {'SIMB':<5} | {'DESTINO':<20}\n"
        res += "-" * 50 + "\n"
        
        # Ordenar transiciones para que el archivo de texto sea ordenado
        sorted_keys = sorted(self.trans.keys(), key=lambda k: (str(k[0]), k[1]))
        
        for (estado, simbolo) in sorted_keys:
            destino = self.trans[(estado, simbolo)]
            res += f"{formatear_estado(estado):<20} | {simbolo:<5} | {formatear_estado(destino):<20}\n"
        
        return res

# ==========================================
# 2. Lógica de Conversión (AFND -> AFD)
# ==========================================

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
        if S in procesados: continue
        
        procesados.add(S)
        estados_afd.add(S)

        if any(q in afnd.aceptacion for q in S):
            acept_afd.add(S)

        for simbolo in afnd.alfabeto:
            nuevo = set()
            for q in S:
                if q == "⊥": continue
                if (q, simbolo) in afnd.trans:
                    nuevo.update(afnd.trans[(q, simbolo)])

            if len(nuevo) == 0:
                S_prime = sumidero
            else:
                S_prime = frozenset(nuevo)

            trans_afd[(S, simbolo)] = S_prime

            if S_prime not in procesados and S_prime not in por_procesar:
                por_procesar.append(S_prime)

    if sumidero in estados_afd:
        for simbolo in afnd.alfabeto:
            if (sumidero, simbolo) not in trans_afd:
                trans_afd[(sumidero, simbolo)] = sumidero

    return AFD(estados_afd, afnd.alfabeto, inicial_afd, acept_afd, trans_afd)

# ==========================================
# 3. Lectura de Archivo
# ==========================================

def leer_archivo_y_crear_afnd(ruta_archivo):
    print(f"Leyendo archivo: {ruta_archivo} ...")
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            lineas = [l.strip() for l in f.readlines() if l.strip()]
        
        if len(lineas) < 5:
            raise ValueError("El archivo no tiene el formato correcto (mínimo 5 líneas).")

        # Parseo según formato especificado
        estados = [e.strip() for e in lineas[0].split(',')]
        alfabeto = [s.strip() for s in lineas[1].split(',')]
        inicial = lineas[2].strip()
        aceptacion = [a.strip() for a in lineas[3].split(',')]

        trans_dict = defaultdict(set)
        for linea in lineas[4:]:
            partes = linea.split(',')
            if len(partes) == 3:
                origen, simbolo, destino = partes[0].strip(), partes[1].strip(), partes[2].strip()
                trans_dict[(origen, simbolo)].add(destino)

        trans = dict(trans_dict)
        
        return AFND(estados, alfabeto, inicial, aceptacion, trans)

    except FileNotFoundError:
        print(f"ERROR CRÍTICO: No se encontró el archivo '{ruta_archivo}'.")
        print("Por favor sube el archivo o créalo antes de ejecutar.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR procesando el archivo: {e}")
        sys.exit(1)

# ==========================================
# 4. Generador de Archivo de Ejemplo (Opcional)
# ==========================================
def generar_archivo_si_no_existe(nombre):
    if not os.path.exists(nombre):
        print(f" El archivo '{nombre}' no existía. Creando uno de ejemplo...")
        contenido = """q0,q1,q2
a,b
q0
q2
q0,a,q0
q0,b,q0
q0,a,q1
q1,b,q2"""
        with open(nombre, "w", encoding="utf-8") as f:
            f.write(contenido)

# ==========================================
# 5. Bloque Principal (Main)
# ==========================================

if __name__ == "__main__":
    archivo_entrada = "lecturaAFND.txt"
    archivo_salida = "resultadoAFD.txt"

    # PASO 0: (Solo para que no falle en Colab si olvidaste subir el archivo)
    # Si ya tienes tu archivo, el programa usará el tuyo.
    generar_archivo_si_no_existe(archivo_entrada)

    # PASO 1: Leer AFND
    afnd = leer_archivo_y_crear_afnd(archivo_entrada)
    print(" Archivo leído correctamente.")

    # PASO 2: Convertir
    print("  Convirtiendo AFND a AFD...")
    afd = convertir_a_afd(afnd)

    # PASO 3: Guardar Resultado en TXT
    try:
        with open(archivo_salida, "w", encoding="utf-8") as f:
            f.write(str(afd))
        
        print(f"\n ÉXITO: El resultado se ha guardado en '{archivo_salida}'")
        
        # Opcional: Mostrar en consola también para verificar rápido
        print("\n--- Vista previa del resultado ---")
        print(str(afd))

    except IOError as e:
        print(f"Error al escribir el archivo de salida: {e}")