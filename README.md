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

### 3.1 Representación del AFND y AFD

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


