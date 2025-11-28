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
    # --- 1. Estado inicial del AFD ---
    inicial_afd = frozenset([afnd.inicial])

    # --- 2. Estructuras necesarias: cola y set ---
    por_procesar = [inicial_afd]
    procesados = set()

    trans_afd = {}        # (estado_conjunto, simbolo) -> nuevo_conjunto
    estados_afd = set()   # todos los conjuntos generados
    acept_afd = set()     # subconjuntos que contienen estados finales AFND

    # --- Estado sumidero ---
    sumidero = frozenset(["⊥"])   # lo tratamos como un estado normal del AFD

    while por_procesar:
        S = por_procesar.pop(0)

        if S in procesados:
            continue

        procesados.add(S)
        estados_afd.add(S)

        # Un subconjunto es final si contiene al menos un estado final del AFND
        if any(q in afnd.aceptacion for q in S):
            acept_afd.add(S)

        # --- Para cada símbolo del alfabeto ---
        for simbolo in afnd.alfabeto:
            # generar el nuevo subconjunto S'
            nuevo = set()

            for q in S:
                # obtener transiciones del AFND
                if (q, simbolo) in afnd.trans:
                    destinos = afnd.trans[(q, simbolo)]
                    nuevo.update(destinos)

            # si no hay transiciones -> sumidero
            if len(nuevo) == 0:
                S_prime = sumidero
            else:
                S_prime = frozenset(nuevo)

            # registrar transición en el AFD
            trans_afd[(S, simbolo)] = S_prime

            # si el nuevo subconjunto no ha sido procesado, añádelo
            if S_prime not in procesados:
                por_procesar.append(S_prime)

    # --- El sumidero también necesita bucles para cada símbolo ---
    if sumidero not in estados_afd:
        estados_afd.add(sumidero)
        for simbolo in afnd.alfabeto:
            trans_afd[(sumidero, simbolo)] = sumidero

    # --- Crear y devolver el AFD ---
    return AFD(
        estados=estados_afd,
        alfabeto=afnd.alfabeto,
        transiciones=trans_afd,
        inicial=inicial_afd,
        aceptacion=acept_afd
    )


def imprimir_transiciones(trans):
    print("\nTransiciónes del AFND:")
    # Obtiene alfabeto y estados
    estados = sorted({tuple(s) for s, _ in trans.keys()}, key=len)
    simbolos = sorted({a for _, a in trans.keys()})

    # Cabecera
    print("Estado".ljust(20), "|", " | ".join(s.ljust(10) for s in simbolos))
    print("-"*50)

    # Filas
    for estado in estados:
        est_f = "{" + ", ".join(estado) + "}"
        fila = est_f.ljust(20) + " | "
        for s in simbolos:
            dest = "{" + ", ".join(trans[(frozenset(estado), s)]) + "}"
            fila += dest.ljust(10) + " | "
        print(fila)


def analizar_recorrido(afnd: AFND, cadena: str):
    print("\nSimulación de estados del AFND:")
    cola1 = []   # estados generados tras procesar un símbolo
    cola2 = []   # cola auxiliar

    # iniciar con el estado inicial del AFND
    cola1.append(afnd.inicial)

    # procesar cada símbolo de la cadena
    for simbolo in cadena:
        # vaciar cola1 dentro de cola2
        while cola1:
            cola2.append(cola1.pop())

        # conjunto para evitar duplicados
        nuevos_estados = set()

        # procesar cada estado activo antes de leer el símbolo
        for estado in cola2:
            if (estado, simbolo) in afnd.trans:
                destinos = afnd.trans[(estado, simbolo)]
                nuevos_estados.update(destinos)

        # actualizar cola1 con los estados nuevos
        for e in nuevos_estados:
            cola1.append(e)

        # limpiar cola2
        cola2.clear()

        # imprimir resultado
        print(f"Leo '{simbolo}':")
        print(f"\t{set(cola1)}\n")
        
    # Verificamos si llegamos a un estado final
    estados_finales = set(cola1)
    aceptados = estados_finales.intersection(afnd.aceptacion)

    if aceptados:
        print("--> cadena aceptada")
        print("Estados aceptadores: ", aceptados)
    else:
        print("--> cadena no aceptada")


if __name__ == "__main__":
    # Construimos un AFND de ejemplo
    estados = {"q1", "q2", "q3"}
    alfabeto = {"0", "1"}

    trans = {
        ("q1", "0"): {"q1", "q2"},
        ("q2", "0"): {"q1", "q2"},
        ("q2", "1"): {"q3"},
        ("q3", "0"): {"q2"},
        ("q3", "1"): {"q3"},
    }

    inicial = "q1"  # estado inicial
    aceptacion = {"q1", "q3"}   # estados finales

    afnd_ejemplo = AFND(estados, alfabeto, trans, inicial, aceptacion)

    afd = convertir_a_afd(afnd_ejemplo)
    imprimir_transiciones(afd.trans)

    analizar_recorrido(afnd=afnd_ejemplo, cadena="0011")
