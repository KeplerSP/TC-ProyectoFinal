# Simulación de AFND y Conversión a AFD mediante Construcción de Subconjuntos

## Autores: 
###        - *Córdova García Leonardo Kepler*
###        - *Blas Sanca Hebert Gianmarco*    
###        - *Guevara Capulian Julio Ricardo*     
###        - *Rodriguez Claeyssen Isaac Aaron*      
###        - *Rojas Nazario Nathan Ray*
### Curso: *Teoria de la computación*  
### Profesor: *Victor Hugo Bustamante*


### 1. Introducción

Este proyecto implementa dos herramientas fundamentales dentro de la Teoría de la Computación:  
la simulación de autómatas finitos no deterministas (AFND) y la conversión sistemática de un AFND a un autómata finito determinista (AFD) mediante el método de construcción de subconjuntos.

Los AFND permiten múltiples posibles transiciones para un mismo símbolo, lo que los convierte en un modelo conceptual poderoso para describir lenguajes regulares. Sin embargo, los AFD son más adecuados para la implementación real en programas y hardware, debido a su comportamiento determinista. La teoría establece que todo lenguaje reconocido por un AFND puede ser reconocido por un AFD equivalente, y la transformación entre ambos es un proceso clave para demostrar esta equivalencia.

### **Objetivo del proyecto**

1. **Simular paso a paso la ejecución del AFND**, manteniendo en cada momento el conjunto de estados posibles.  
2. **Construir el AFD equivalente siguiendo el método de subconjuntos**, donde cada estado del AFD representa un conjunto de estados del AFND.

De esta manera, el proyecto no solo demuestra la equivalencia entre ambos modelos, sino que también introduce estructuras de datos como conjuntos y tablas de transición para la implementación de los autómatas.



## 2. Fundamentos Teóricos

### 2.1 Autómata Finito No Determinista (AFND)
Un Autómata Finito No Determinista es un modelo matemático utilizado para describir lenguajes formales.  
A diferencia de un autómata determinista, un AFND puede “ramificarse” durante la lectura de la cadena: para un mismo estado y un mismo símbolo puede haber varias transiciones posibles, una sola o incluso ninguna.

El AFND mantiene un **conjunto de estados posibles** durante el procesamiento.  
Una cadena es aceptada si **al menos uno** de los estados alcanzados al final pertenece al conjunto de estados de aceptación.



### 2.2 Autómata Finito Determinista (AFD)
Un AFD es un autómata donde **todas las transiciones están completamente definidas**:  
para cada estado y para cada símbolo existe exactamente **una** transición.

Aunque el AFD parece más restrictivo que un AFND, ambos reconocen la misma clase de lenguajes: los lenguajes regulares.



### 2.3 Equivalencia de Autómatas
La teoría de autómatas establece que **todo AFND tiene un AFD equivalente**.  
Es decir, cualquier comportamiento no determinista puede ser simulado mediante un modelo determinista.

Esta equivalencia permite:

- Diseñar autómatas de manera más flexible (AFND).
- Implementarlos de forma eficiente (AFD).



### 2.4 Construcción de Subconjuntos (Subset Construction)
El método de Construcción de Subconjuntos transforma un AFND en un AFD equivalente.

Idea principal:  
> Cada estado del AFD representa un **conjunto** de estados del AFND.

El proceso:
1. Se inicia con el conjunto `{q0}` como estado inicial del AFD.
2. Para cada conjunto de estados y cada símbolo del alfabeto:
   - Se unen todas las transiciones posibles.
   - El resultado es un **nuevo conjunto**, que se convierte en un nuevo estado del AFD.
3. Si un nuevo conjunto no ha sido procesado, se añade a la lista de pendientes.
4. Un conjunto del AFD será estado de aceptación si contiene al menos **un** estado de aceptación del AFND.



### 3. Diseño del Algoritmo 

El proyecto fue desarrollado en **Python** utilizando `tkinter` para la interfaz gráfica y librerías XML para la exportación a JFLAP.

### 3.1 Librerías Principales
```js
import tkinter as tk             # Interfaz Gráfica
import xml.etree.ElementTree as ET # Generación de XML para JFLAP
import os                        # Gestión de rutas de archivos
```
### 3.2 Representación del AFND y AFD

Se utilizan **clases** en Python:

#### Clase `AFND`
- `estados`: conjunto de nombres
- `alfabeto`: símbolos
- `trans`: diccionario con la forma  
  `(estado, símbolo) -> {estados destino}`
- `inicial`: estado inicial
- `aceptacion`: estados aceptadores
```js
class AFND:
    def __init__(self, estados, alfabeto, trans, inicial, aceptacion):
        self.estados = set(estados)
        self.alfabeto = set(alfabeto)
        self.trans = dict(trans)  
        self.inicial = inicial
        self.aceptacion = set(aceptacion)
```

#### Clase   AFD: 
Se crea en la conversión:  
- Estados representados como `frozenset`
- Transiciones deterministas
- Aceptación basada en subconjuntos que contienen estados aceptadores
```js
class AFD:
    def __init__(self, estados, alfabeto, transiciones, inicial, aceptacion):
        self.estados = estados
        self.alfabeto = alfabeto
        self.trans = transiciones
        self.inicial = inicial
        self.aceptacion = aceptacion
```


### 3.4 Lógica de Conversión (Subconjuntos)
La función convertir_a_afd implementa el núcleo del algoritmo:

Inicia con el conjunto {q0}.

Usa una cola (por_procesar) para explorar nuevos estados compuestos.

Calcula la unión de transiciones para cada símbolo.

Maneja el estado sumidero (⊥) para transiciones vacías.

```js
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

```

```js
    if sumidero in estados_afd or any(dest == sumidero for dest in trans_afd.values()):
        estados_afd.add(sumidero)
        for simbolo in afnd.alfabeto:
            if (sumidero, simbolo) not in trans_afd:
                trans_afd[(sumidero, simbolo)] = sumidero

    return AFD(estados_afd, afnd.alfabeto, trans_afd, inicial_afd, acept_afd)
```


### 4. Instrucciones de Uso
### 4.1 Requisitos
Tener instalado Python .

No se requieren librerías externas (se usan solo las estándar).
### 4.2 Ejecución
Abre el archivo directamente o desde la terminal, navega a la carpeta del proyecto y ejecuta:
```js
python CONVERSOR.py
```

### 4.3 Formato de Entrada
En la interfaz gráfica, ingresa la definición del autómata línea por línea siguiendo este formato:

Línea 1: Estados (separados por comas).

Línea 2: Alfabeto (separado por comas).

Línea 3: Estado inicial.

Línea 4: Estados finales (separados por comas).

Línea 5+: Transiciones (origen,símbolo,destino)

```js
q0,q1,q2
a,b
q0
q2
q0,a,q0
q0,b,q0
q0,a,q1
q1,b,q2
```

La forma de lectura del formato es la siguiente :
```js
def generar_afnd(self):
        try:
            contenido = self.automata_text.get("1.0", tk.END).strip()
            # ... (Validaciones de vacío) ...
            lineas = [l.strip() for l in contenido.split("\n") if l.strip()]

            # Extracción de la definición formal
            estados = [e.strip() for e in lineas[0].split(",") if e.strip()]      # Línea 1: Q
            alfabeto = [a.strip() for a in lineas[1].split(",") if a.strip()]     # Línea 2: Σ
            inicial = lineas[2].strip()                                           # Línea 3: q0
            aceptacion = {x.strip() for x in lineas[3].split(",") if x.strip()}   # Línea 4: F

            trans = {}
            # Línea 5 en adelante: Función de transición δ
            for i in range(4, len(lineas)):
                partes = [p.strip() for p in lineas[i].split(",")]
                if len(partes) != 3: continue 
                
                origen, simbolo, destino = partes
                # Construcción del grafo: (q, a) -> {destinos}
                if (origen, simbolo) not in trans:
                    trans[(origen, simbolo)] = set()
                trans[(origen, simbolo)].add(destino)

            self.afnd = AFND(estados, alfabeto, trans, inicial, aceptacion)
            self.exportar_afnd_txt()
            messagebox.showinfo("Éxito", f"Archivo 'AFND.txt' generado en:\n{self.directorio_base}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
```

### 5. Resultados y Salida

El programa genera los siguientes archivos en el mismo directorio del script:

AFND.txt y AFD.txt: Definición formal de los autómatas en texto plano.
```js

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
```
```js
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
```
AFND.jff y AFD.jff: Archivos compatibles con el software JFLAP.
```js
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
```