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



### 3.1 Librerías Principales
```js

import xml.etree.ElementTree as ET
from xml.dom import minidom
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


### 3.3 Lógica de Conversión (Subconjuntos)
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

### 3.4 Simulador AFND
    
    Datos Iniciales (del archivo lectura.txt)
```js
afnd.inicial = 'q0'

afnd.trans=
            {

             ('q0', 'a'): {'q0', 'q1'}, 
  
             ('q0', 'b'): {'q0'}, 

             ('q1', 'b'): {'q2'}
             
             }
```


### Fase 1: Inicialización

```js
Lo que pasa en la Simulación (Datos),
##Paso 0: Calculamos el estado inicial del AFD.   inicial_afd = frozenset([afnd.inicial])



El estado inicial es el conjunto {q0}

## Preparamos la cola de trabajo.                 por_procesar = [inicial_afd]


Cola: [{q0}]

## Preparamos lista de visitados.                 procesados = set()
Procesados: ∅
```
### Fase 2: El Bucle while 
## Iteración 1 Analizando el estado {q0}
```js

## Sacamos {q0} de la cola.                       S = por_procesar.pop(0)

S = {'q0'}

## Lo marcamos como visto.                        procesados.add(S)

## Evaluando símbolo 'a'                          for simbolo in afnd.alfabeto:

## Buscamos a dónde va q0 con 'a'                 destinos = afnd.trans[(q, simbolo)]

## En el mapa trans encontramos {'q0', 'q1'}      nuevo.update(destinos)

S_prime = {'q0', 'q1'}

## Guardamos la transición:                       trans_afd[(S, simbolo)] = S_prime

{q0} --a--> {q0, q1}

## Como {q0, q1} es nuevo, lo metemos a la cola  
                                                  if S_prime not in procesados:                                                         
                                                  por_procesar.append(S_prime)

Cola: [{q0, q1}]


## Evaluando símbolo 'b'                          for simbolo in afnd.alfabeto:


## Buscamos a dónde va q0 con b                   nuevo.update(destinos)
Resultado: {'q0'}


## El destino es {q0}. Ya fue procesado (es S)    if S_prime not in procesados: (Falso)

No se añade a la cola.


```
## Iteración 2 Analizando el estado {q0,q1}
```js
## Sacamos {q0, q1} de la cola.                     S = por_procesar.pop(0)

S = {'q0', 'q1'}

## Evaluando símbolo 'a'                            for simbolo in afnd.alfabeto:

1. q0 con a -> {'q0', 'q1'}                         for q in S: ... nuevo.update(...)

2. q1 con a -> Nada (∅)

Unión: {'q0', 'q1'}

## Resultado: va a sí mismo.                       trans_afd[(S, simbolo)] = S_prime

Transición: {q0, q1} --a--> {q0, q1}

## Evaluando símbolo 'b'                            for simbolo in afnd.alfabeto:


1. q0 con b -> {'q0'}                              nuevo.update(destinos)


2. q1 con b -> {'q2'}


Unión: {'q0', 'q2'}

 Este estado {q0, q2} es nuevo.

##  Lo metemos a la cola.                         por_procesar.append(S_prime)

Cola: [{q0, q2}]

```

## Iteración 3 Analizando el estado {q0, q2}

```js
## Sacamos {q0, q2} de la cola.                     S = por_procesar.pop(0)

S = {'q0', 'q2'}


## Verificar Aceptación:                            if any(q in afnd.aceptacion for q in S):

¿Está q2 (final original) dentro de {q0, q2}?       acept_afd.add(S)

Sí. Este estado será final en el AFD.


## Evaluando símbolo 'a'                            for simbolo in afnd.alfabeto:

1. q0 con a -> {'q0', 'q1'}                         S_prime = frozenset(nuevo)

2. q2 con a -> Nada (∅)

Unión: {'q0', 'q1'} (ya existe)



## Evaluando símbolo 'b'                            for simbolo in afnd.alfabeto:


1. q0 con b -> {'q0'}                              trans_afd[(S, simbolo)] = S_prime


2. q2 con b -> Nada (∅)


Unión: {'q0'} (Ya existe).


```


## Fase 3: Finalización

```js
## La cola por_procesar está vacía. El bucle termina.   while por_procesar: (Termina)

## Se crea el objeto AFD con:                           return AFD(estados_afd, ...)

- Estados: {q0}, {q0,q1}, {q0,q2}


- Transiciones calculadas


- Aceptación: {q0,q2}

```

### 4. Instrucciones de Uso
### 4.1 Requisitos
Tener instalado Python 3.6 o superior.

No se requieren librerías externas (solo librerías estándar).


### 4.2 Ejecución
Sigue los pasos correspondientes a tu sistema operativo:
1. Windows (CMD o PowerShell)
```js
 1. Primero entra a la carpeta donde guardaste los archivos
cd ruta\de\tu\carpeta
 

 2. Ejecuta el script
python CONVERTOR_AFND_AFD.py
```

2. Linux (Terminal)
```js
# 1. Primero entra a la carpeta donde guardaste los archivos
cd /ruta/de/tu/carpeta


# 2. Ejecuta el script
python3 CONVERTOR_AFND_AFD.py
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

El algoritmo  de lectura del formato es el  siguiente :
```js
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
```

### 5. Resultados y Salida


Una vez ejecutado el programa, se generarán los siguientes archivos en el directorio:

### resultado.txt:
 Contiene la definición formal del AFD resultante (Estados, Alfabeto, Inicial, Finales y funciones de  Transicion).
```js
{q0,q2},{q0,q1},{q0}
a,b
{q0}
{q0,q2}
{q0},a,{q0,q1}
{q0},b,{q0}
{q0,q1},a,{q0,q1}
{q0,q1},b,{q0,q2}
{q0,q2},a,{q0,q1}
{q0,q2},b,{q0}
```
### afnd.jff:
 Archivo XML compatible con JFLAP que representa el autómata original ingresado.

```js
<?xml version="1.0" ?>
<structure>
   <type>fa</type>
   <automaton>
      <state id="0" name="q2">
         <x>100</x>
         <y>100</y>
         <final/>
      </state>
      <state id="1" name="q0">
         <x>220</x>
         <y>200</y>
         <initial/>
      </state>
      <state id="2" name="q1">
         <x>340</x>
         <y>100</y>
      </state>
      <transition>
         <from>1</from>
         <to>1</to>
         <read>a</read>
      </transition>
      <transition>
         <from>1</from>
         <to>2</to>
         <read>a</read>
      </transition>
      <transition>
         <from>1</from>
         <to>1</to>
         <read>b</read>
      </transition>
      <transition>
         <from>2</from>
         <to>0</to>
         <read>b</read>
      </transition>
   </automaton>
</structure>

```
<img width="772" height="456" alt="image" src="https://github.com/user-attachments/assets/1cc4e272-74f6-4fc1-b5b1-dd9b58922d89" />



### afd.jff: 
Archivo XML compatible con JFLAP que representa el autómata convertido.
```js

       <transition>
         <from>2</from>
         <to>1</to>
         <read>a</read>
      </transition>
      <transition>
         <from>2</from>
         <to>2</to>
         <read>b</read>
      </transition>
      <transition>
         <from>1</from>
         <to>1</to>
         <read>a</read>
      </transition>
      <transition>
         <from>1</from>
         <to>0</to>
         <read>b</read>
      </transition>
      <transition>
         <from>0</from>
         <to>1</to>
         <read>a</read>
      </transition>
      <transition>
         <from>0</from>
         <to>2</to>
         <read>b</read>
      </transition>
   </automaton>
</structure>

```
<img width="663" height="418" alt="image" src="https://github.com/user-attachments/assets/ea7baa60-a924-4153-8c19-96126c5a55aa" />


