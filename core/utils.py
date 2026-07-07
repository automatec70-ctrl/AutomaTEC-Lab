"""
Funciones utilitarias compartidas por los módulos del motor de autómatas.

Incluye:
  - bfs_reachable: BFS para calcular estados alcanzables
  - rename_states: Renombrar estados con un prefijo uniforme
  - validate_automata: Validar la consistencia de un autómata
"""

from collections import deque
from typing import Set, Dict, List, Optional, Any


def bfs_reachable(estados: Set[str], delta: Dict[str, Dict[str, Any]],
                  estado_inicial: str, alfabeto: Optional[Set[str]] = None) -> Set[str]:
    """
    Calcula el conjunto de estados alcanzables desde estado_inicial usando BFS.

    Fundamento teórico:
      Un estado q es alcanzable si existe un camino desde q0 hasta q
      en el grafo de transiciones del autómata. Esto es:
        q ∈ alcanzables ⟺ ∃w ∈ Σ* tal que δ*(q0, w) = q

    Args:
        estados: Conjunto de estados Q
        delta: Función de transición δ (AFD: dict[str]->str, AFN: dict[str]->list)
        estado_inicial: Estado inicial q0
        alfabeto: Si se proporciona, solo se consideran transiciones con estos símbolos.
                  Si es None, se consideran todos los símbolos (incluyendo λ).

    Returns:
        Conjunto de estados alcanzables desde estado_inicial
    """
    if estado_inicial not in estados:
        return set()

    visitados = set()
    cola = deque([estado_inicial])
    visitados.add(estado_inicial)

    while cola:
        estado_actual = cola.popleft()

        # Obtener transiciones desde el estado actual
        transiciones = delta.get(estado_actual, {})
        for simbolo, destinos in transiciones.items():
            # Si se especificó alfabeto, ignorar símbolos fuera de él
            if alfabeto is not None and simbolo not in alfabeto:
                continue

            # Normalizar destinos: puede ser un string (AFD) o una lista/set (AFN)
            if isinstance(destinos, str):
                destinos_lista = [destinos]
            elif isinstance(destinos, (list, set, frozenset)):
                destinos_lista = list(destinos)
            else:
                destinos_lista = [destinos]

            for destino in destinos_lista:
                if destino in estados and destino not in visitados:
                    visitados.add(destino)
                    cola.append(destino)

    return visitados


def rename_states(automata: Any, prefix: str = 'q') -> Any:
    """
    Renombra los estados de un autómata usando el prefijo dado.

    Fundamento teórico:
      El nombre de los estados es irrelevante para el lenguaje reconocido;
      solo importa la estructura de la función de transición δ y la
      partición en estados finales y no finales. Dos autómatas isomorfos
      reconocen el mismo lenguaje.

    El nuevo nombre de cada estado será: prefix + índice (ej: q0, q1, q2, ...).
    El estado inicial siempre será prefix + '0'.

    Args:
        automata: Un objeto AFD, AFN o AFNLambda
        prefix: Prefijo para los nuevos nombres de estados

    Returns:
        Un nuevo autómata del mismo tipo con estados renombrados
    """
    # Crear mapeo de nombres antiguos a nuevos
    estados_ordenados = sorted(automata.estados)

    # Asegurar que el estado inicial sea el primero
    if automata.estado_inicial in estados_ordenados:
        estados_ordenados.remove(automata.estado_inicial)
        estados_ordenados.insert(0, automata.estado_inicial)

    mapeo = {}
    for i, estado in enumerate(estados_ordenados):
        mapeo[estado] = f"{prefix}{i}"

    # Determinar el tipo de autómata para crear la instancia correcta
    from .afn_lambda import AFNLambda
    from .afn import AFN

    if isinstance(automata, AFNLambda):
        nuevo = AFNLambda()
    elif isinstance(automata, AFN):
        nuevo = AFN()
    else:
        from .afd import AFD
        nuevo = AFD()

    # Copiar alfabeto
    for simbolo in automata.alfabeto:
        nuevo.agregar_simbolo(simbolo)

    # Copiar estados con nuevos nombres
    for estado in automata.estados:
        nuevo.agregar_estado(mapeo[estado])

    # Estado inicial
    nuevo.definir_estado_inicial(mapeo[automata.estado_inicial])

    # Estados finales
    for estado in automata.estados_finales:
        nuevo.agregar_estado_final(mapeo[estado])

    # Transiciones
    for estado in automata.estados:
        transiciones = automata.delta.get(estado, {})
        for simbolo, destinos in transiciones.items():
            if isinstance(destinos, str):
                # AFD: delta[estado][simbolo] = str
                nuevo.definir_transicion(mapeo[estado], simbolo, mapeo[destinos])
            elif isinstance(destinos, (list, set, frozenset)):
                # AFN/AFN-λ: delta[estado][simbolo] = set/list
                nuevos_destinos = [mapeo[d] for d in destinos if d in mapeo]
                if nuevos_destinos:
                    nuevo.definir_transicion(mapeo[estado], simbolo, nuevos_destinos)

    return nuevo


def validate_automata(automata: Any) -> List[str]:
    """
    Valida la consistencia de un autómata y retorna una lista de errores.

    Fundamento teórico:
      Para que un autómata M = (Q, Σ, δ, q0, F) esté bien definido:
        1. q0 ∈ Q (el estado inicial debe ser un estado del autómata)
        2. F ⊆ Q (todos los estados finales deben ser estados del autómata)
        3. Para AFD: δ(q, a) ∈ Q para todo q ∈ Q, a ∈ Σ donde δ(q,a) esté definida
        4. Para AFN/AFN-λ: δ(q, a) ⊆ Q para todo q ∈ Q, a ∈ Σ

    Args:
        automata: Un objeto AFD, AFN o AFNLambda

    Returns:
        Lista de cadenas describiendo los errores encontrados (vacía si es válido)
    """
    errores = []

    # Verificar que existe estado inicial
    if not automata.estado_inicial:
        errores.append("No se ha definido estado inicial (q0).")
    elif automata.estado_inicial not in automata.estados:
        errores.append(
            f"El estado inicial '{automata.estado_inicial}' no pertenece al conjunto de estados Q."
        )

    # Verificar que los estados finales pertenecen a Q
    for estado in automata.estados_finales:
        if estado not in automata.estados:
            errores.append(
                f"El estado final '{estado}' no pertenece al conjunto de estados Q."
            )

    # Verificar transiciones: destinos deben ser estados válidos
    from .afd import AFD
    es_afd = isinstance(automata, AFD)

    for estado, transiciones in automata.delta.items():
        # El estado de origen debe estar en Q
        if estado not in automata.estados:
            errores.append(
                f"El estado de origen '{estado}' en delta no pertenece a Q."
            )
            continue

        for simbolo, destinos in transiciones.items():
            if es_afd:
                # AFD: destino debe ser un estado válido
                if isinstance(destinos, str):
                    if destinos not in automata.estados:
                        errores.append(
                            f"δ('{estado}', '{simbolo}') = '{destinos}' pero "
                            f"'{destinos}' no pertenece a Q."
                        )
            else:
                # AFN/AFN-λ: cada destino debe ser un estado válido
                if isinstance(destinos, (list, set, frozenset)):
                    for destino in destinos:
                        if destino not in automata.estados:
                            errores.append(
                                f"δ('{estado}', '{simbolo}') contiene '{destino}' "
                                f"pero '{destino}' no pertenece a Q."
                            )

    # Para AFD: verificar completitud
    if es_afd:
        for estado in automata.estados:
            for simbolo in automata.alfabeto:
                if automata.delta.get(estado, {}).get(simbolo) is None:
                    errores.append(
                        f"AFD incompleto: δ('{estado}', '{simbolo}') no está definida."
                    )

    # Verificar que los estados no estén vacíos
    if not automata.estados:
        errores.append("El conjunto de estados Q está vacío.")

    # Verificar que el alfabeto no esté vacío
    if not automata.alfabeto:
        errores.append("El alfabeto Σ está vacío.")

    return errores
