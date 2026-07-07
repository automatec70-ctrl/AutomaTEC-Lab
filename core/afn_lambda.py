"""
AFN-λ - Autómata Finito No Determinista con Transiciones Lambda (ε)

Definición formal: M = (Q, Σ, δ, q0, F)
  Q  = conjunto finito de estados
  Σ  = alfabeto de entrada
  δ  = Q × (Σ ∪ {λ}) → 2^Q (función de transición con ε-transiciones)
  q0 = estado inicial
  F  = conjunto de estados finales

La diferencia con el AFN es que δ puede usar el símbolo especial λ (epsilon)
para transiciones que no consumen ningún carácter de la entrada.

Implementación con:
  - Clausura lambda (ε-clausura) por DFS
  - Tabla de clausuras lambda
  - Procesamiento de cadenas con ε-clausura
  - Construcción de subconjuntos con ε-clausura (AFN-λ → AFD)
  - Eliminación de ε-transiciones (AFN-λ → AFN)
  - Operaciones regulares (unión, concatenación, clausura de Kleene)
"""

from typing import Dict, Set, List, Tuple, Optional
import copy
from collections import deque

from .afn import AFN


# Símbolo especial para transiciones lambda/epsilon
LAMBDA = 'λ'


class AFNLambda(AFN):
    """Autómata Finito No Determinista con transiciones Lambda (ε)"""

    def __init__(self):
        super().__init__()
        # El símbolo LAMBDA no se agrega al alfabeto de entrada
        # pero se usa como clave especial en delta

    # ================================================================
    # Transiciones Lambda
    # ================================================================

    def agregar_transicion_lambda(self, desde: str, hacia: str) -> None:
        """
        Agrega una transición λ: δ(desde, λ) ∋ hacia.
        Esta transición no consume ningún símbolo de la entrada.
        """
        self.agregar_estado(desde)
        self.agregar_estado(hacia)
        if LAMBDA not in self.delta[desde]:
            self.delta[desde][LAMBDA] = set()
        self.delta[desde][LAMBDA].add(hacia)

    def eliminar_transicion_lambda(self, desde: str, hacia: str) -> None:
        """
        Elimina una transición λ específica.
        """
        if desde in self.delta and LAMBDA in self.delta[desde]:
            self.delta[desde][LAMBDA].discard(hacia)
            if not self.delta[desde][LAMBDA]:
                del self.delta[desde][LAMBDA]

    def tiene_transiciones_lambda(self) -> bool:
        """
        Verifica si el AFN-λ tiene alguna transición λ.
        """
        for estado in self.delta:
            if LAMBDA in self.delta[estado] and self.delta[estado][LAMBDA]:
                return True
        return False

    # ================================================================
    # Clausura Lambda (ε-Clausura)
    # ================================================================

    def clausura_lambda(self, estado: str) -> Set[str]:
        """
        Calcula la ε-clausura de un estado.
        
        Definición: CL_ε(q) = {q} ∪ {q' : existe camino de q a q'
        usando solo transiciones λ}
        
        Implementación: DFS sobre transiciones λ.
        La clausura siempre incluye al estado mismo.
        """
        clausura = set()
        pila = [estado]

        while pila:
            e = pila.pop()
            if e in clausura:
                continue
            clausura.add(e)
            # Seguir todas las transiciones λ desde e
            if e in self.delta and LAMBDA in self.delta[e]:
                for destino in self.delta[e][LAMBDA]:
                    if destino not in clausura:
                        pila.append(destino)

        return clausura

    def clausura_lambda_conjunto(self, estados: Set[str]) -> Set[str]:
        """
        Calcula la ε-clausura de un conjunto de estados.
        
        CL_ε(S) = ∪{CL_ε(q) : q ∈ S}
        """
        resultado = set()
        for estado in estados:
            resultado.update(self.clausura_lambda(estado))
        return resultado

    def tabla_clausuras_lambda(self) -> Dict[str, List[str]]:
        """
        Calcula la ε-clausura para todos los estados del AFN-λ.
        
        Retorna un diccionario: estado → lista ordenada de estados en su clausura.
        Útil para visualización y para la construcción de subconjuntos.
        """
        tabla = {}
        for estado in sorted(self.estados):
            tabla[estado] = sorted(self.clausura_lambda(estado))
        return tabla

    # ================================================================
    # Procesamiento de Cadenas
    # ================================================================

    def procesar_cadena(self, cadena: str) -> dict:
        """
        Simula el AFN-λ sobre la cadena w, aplicando la ε-clausura
        en cada paso.
        
        Definición: δ*(q, λ) = CL_ε(q)
                    δ*(q, wa) = CL_ε(∪{δ(q', a) : q' ∈ δ*(q, w)})
        
        La cadena es aceptada si δ*(q0, w) ∩ F ≠ ∅.
        
        Retorna: {
          'aceptada': bool,
          'estados_finales_alcanzados': set,
          'traza': lista de pasos con estados activos y clausuras
        }
        """
        if not self.estado_inicial:
            return {
                'aceptada': False,
                'estados_finales_alcanzados': set(),
                'traza': [{'estados_activos': set(), 'clausura_lambda': set(),
                           'cadena_restante': cadena, 'simbolo_leido': ''}]
            }

        # Estado inicial: CL_ε({q0})
        estados_activos = self.clausura_lambda(self.estado_inicial)
        traza = []

        # Registrar estado inicial con clausura
        traza.append({
            'estados_activos': set(estados_activos),
            'clausura_lambda': set(estados_activos),
            'cadena_restante': cadena,
            'simbolo_leido': ''
        })

        for i, simbolo in enumerate(cadena):
            # Verificar que el símbolo pertenezca al alfabeto
            if simbolo not in self.alfabeto:
                traza.append({
                    'estados_activos': set(estados_activos),
                    'clausura_lambda': set(estados_activos),
                    'cadena_restante': cadena[i:],
                    'simbolo_leido': simbolo
                })
                return {
                    'aceptada': False,
                    'estados_finales_alcanzados': set(),
                    'traza': traza
                }

            # Paso 1: Para cada estado activo, obtener δ(q', simbolo)
            nuevos_estados: Set[str] = set()
            for estado in estados_activos:
                destinos = self.delta.get(estado, {}).get(simbolo, set())
                nuevos_estados.update(destinos)

            # Paso 2: Aplicar ε-clausura al resultado
            estados_activos = self.clausura_lambda_conjunto(nuevos_estados)
            cadena_restante = cadena[i + 1:]

            traza.append({
                'estados_activos': set(estados_activos),
                'clausura_lambda': set(estados_activos),
                'cadena_restante': cadena_restante,
                'simbolo_leido': simbolo
            })

            # Si no hay estados activos, no se puede continuar
            if not estados_activos:
                break

        # La cadena es aceptada si algún estado activo es final
        finales_alcanzados = estados_activos & self.estados_finales
        aceptada = len(finales_alcanzados) > 0

        return {
            'aceptada': aceptada,
            'estados_finales_alcanzados': finales_alcanzados,
            'traza': traza
        }

    # ================================================================
    # Construcción de Subconjuntos con ε-Clausura (AFN-λ → AFD)
    # ================================================================

    def construccion_subconjuntos(self) -> dict:
        """
        Construcción de subconjuntos: AFN-λ → AFD.
        
        Extiende la construcción de subconjuntos del AFN usando
        ε-clausuras en cada paso.
        
        Algoritmo:
        1. Estado inicial del AFD = CL_ε({q0})
        2. Para cada estado del AFD T y cada a ∈ Σ:
           T' = CL_ε(∪{δ(q, a) : q ∈ T})
        3. Estados finales = {T : T ∩ F ≠ ∅}
        
        Retorna: {
          'afd': AFD,
          'pasos': lista de pasos para visualización,
          'mapeo': dict de nombres de estados del AFD a conjuntos
        }
        """
        from .afd import AFD

        pasos = []
        afd = AFD()
        afd.alfabeto = set(self.alfabeto)

        # Paso 1: Estado inicial = CL_ε({q0})
        clausura_inicial = self.clausura_lambda(self.estado_inicial) if self.estado_inicial else set()
        estado_inicial_afd = frozenset(clausura_inicial)
        nombre_inicial = self._nombre_estado_subconjunto(estado_inicial_afd)

        # Mapeos
        mapeo: Dict[str, frozenset] = {}
        mapeo_inverso: Dict[frozenset, str] = {}

        mapeo[nombre_inicial] = estado_inicial_afd
        mapeo_inverso[estado_inicial_afd] = nombre_inicial

        # Agregar estado inicial al AFD
        afd.agregar_estado(nombre_inicial)
        afd.definir_estado_inicial(nombre_inicial)

        # Verificar si es estado final
        if estado_inicial_afd & self.estados_finales:
            afd.agregar_estado_final(nombre_inicial)

        # BFS sobre conjuntos de estados
        cola = deque([estado_inicial_afd])
        procesados: Set[frozenset] = set()

        # Paso inicial
        pasos.append({
            'descripcion': f'Paso 0: Estado inicial del AFD = CL_ε({{{self.estado_inicial}}}) = {sorted(clausura_inicial)}',
            'estado_actual': nombre_inicial,
            'conjunto': sorted(estado_inicial_afd),
            'clausura_lambda': sorted(clausura_inicial),
            'transiciones_generadas': []
        })

        paso_num = 0

        while cola:
            conjunto_actual = cola.popleft()
            if conjunto_actual in procesados:
                continue
            procesados.add(conjunto_actual)

            nombre_actual = mapeo_inverso[conjunto_actual]
            transiciones_generadas = []

            for simbolo in sorted(self.alfabeto):
                # Calcular ∪{δ(q, simbolo) : q ∈ conjunto_actual}
                movimientos: Set[str] = set()
                for estado in conjunto_actual:
                    destinos = self.delta.get(estado, {}).get(simbolo, set())
                    movimientos.update(destinos)

                # Aplicar ε-clausura
                nuevo_conjunto = self.clausura_lambda_conjunto(movimientos)
                nuevo_frozen = frozenset(nuevo_conjunto)

                # Si el conjunto está vacío, no hay transición
                if not nuevo_frozen:
                    continue

                # Crear nombre para el nuevo estado si no existe
                if nuevo_frozen not in mapeo_inverso:
                    nombre_nuevo = self._nombre_estado_subconjunto(nuevo_frozen)
                    mapeo[nombre_nuevo] = nuevo_frozen
                    mapeo_inverso[nuevo_frozen] = nombre_nuevo
                    afd.agregar_estado(nombre_nuevo)

                    # Verificar si es estado final
                    if nuevo_frozen & self.estados_finales:
                        afd.agregar_estado_final(nombre_nuevo)

                    cola.append(nuevo_frozen)

                nombre_nuevo = mapeo_inverso[nuevo_frozen]
                afd.definir_transicion(nombre_actual, simbolo, nombre_nuevo)

                transiciones_generadas.append({
                    'simbolo': simbolo,
                    'movimientos_sin_clausura': sorted(movimientos),
                    'clausura_lambda': sorted(nuevo_conjunto),
                    'nombre_destino': nombre_nuevo
                })

            if transiciones_generadas:
                paso_num += 1
                pasos.append({
                    'descripcion': f'Paso {paso_num}: Procesar {nombre_actual} = {sorted(conjunto_actual)}',
                    'estado_actual': nombre_actual,
                    'conjunto': sorted(conjunto_actual),
                    'clausura_lambda': sorted(conjunto_actual),
                    'transiciones_generadas': transiciones_generadas
                })

        # Serializar mapeo
        mapeo_serializable = {nombre: sorted(conj) for nombre, conj in mapeo.items()}

        return {
            'afd': afd,
            'pasos': pasos,
            'mapeo': mapeo_serializable
        }

    # ================================================================
    # Eliminación de ε-Transiciones (AFN-λ → AFN)
    # ================================================================

    def eliminar_lambda_transiciones(self) -> AFN:
        """
        Elimina las ε-transiciones, convirtiendo el AFN-λ en un AFN equivalente.
        
        Teorema: Para todo AFN-λ M, existe un AFN M' tal que L(M') = L(M).
        
        Algoritmo:
        1. Calcular CL_ε(q) para todo q ∈ Q
        2. Nuevas transiciones: δ'(q, a) = CL_ε(∪{δ(q', a) : q' ∈ CL_ε(q)})
        3. Nuevos estados finales: F' = {q : CL_ε(q) ∩ F ≠ ∅}
        4. Eliminar todas las transiciones λ
        
        Retorna un AFN (sin transiciones λ).
        """
        afn = AFN()
        afn.alfabeto = set(self.alfabeto)
        afn.estado_inicial = self.estado_inicial

        # Copiar estados
        for estado in self.estados:
            afn.agregar_estado(estado)

        # Paso 1: Calcular nuevas transiciones
        # δ'(q, a) = CL_ε(∪{δ(q', a) : q' ∈ CL_ε(q)})
        for estado in self.estados:
            clausura = self.clausura_lambda(estado)
            for simbolo in self.alfabeto:
                # Recopilar destinos de todos los estados en la clausura
                destinos: Set[str] = set()
                for q in clausura:
                    destinos.update(self.delta.get(q, {}).get(simbolo, set()))

                # Aplicar ε-clausura a los destinos
                destinos_con_clausura = self.clausura_lambda_conjunto(destinos)

                # Agregar transiciones al AFN resultante
                for d in destinos_con_clausura:
                    afn.definir_transicion(estado, simbolo, d)

        # Paso 2: Nuevos estados finales
        # F' = {q : CL_ε(q) ∩ F ≠ ∅}
        for estado in self.estados:
            clausura = self.clausura_lambda(estado)
            if clausura & self.estados_finales:
                afn.agregar_estado_final(estado)

        return afn

    # ================================================================
    # Operaciones Regulares sobre AFN-λ
    # ================================================================

    def union(self, otro: 'AFNLambda') -> 'AFNLambda':
        """
        Unión de dos AFN-λ: L(M1) ∪ L(M2).
        
        Construcción con ε-transiciones: Nuevo estado inicial q0 con
        ε-transiciones a los estados iniciales de M1 y M2.
        
        Formalmente: M = (Q1 ∪ Q2 ∪ {q0}, Σ1 ∪ Σ2, δ, q0, F1 ∪ F2)
        donde δ(q0, λ) = {q01, q02}
        """
        resultado = AFNLambda()
        resultado.alfabeto = self.alfabeto | otro.alfabeto

        # Crear nuevo estado inicial
        nuevo_inicial = self._nombre_unico('q0_union', resultado.estados)
        resultado.definir_estado_inicial(nuevo_inicial)

        # Copiar estados de M1
        prefijo1 = 'M1_'
        for estado in self.estados:
            resultado.agregar_estado(prefijo1 + estado)
        for estado in self.delta:
            for simbolo in self.delta[estado]:
                for destino in self.delta[estado][simbolo]:
                    resultado.definir_transicion(prefijo1 + estado, simbolo, prefijo1 + destino)

        # Copiar estados de M2
        prefijo2 = 'M2_'
        for estado in otro.estados:
            resultado.agregar_estado(prefijo2 + estado)
        for estado in otro.delta:
            for simbolo in otro.delta[estado]:
                for destino in otro.delta[estado][simbolo]:
                    resultado.definir_transicion(prefijo2 + estado, simbolo, prefijo2 + destino)

        # Agregar ε-transiciones desde q0 a los estados iniciales
        resultado.agregar_transicion_lambda(nuevo_inicial, prefijo1 + self.estado_inicial)
        resultado.agregar_transicion_lambda(nuevo_inicial, prefijo2 + otro.estado_inicial)

        # Estados finales
        for ef in self.estados_finales:
            resultado.agregar_estado_final(prefijo1 + ef)
        for ef in otro.estados_finales:
            resultado.agregar_estado_final(prefijo2 + ef)

        return resultado

    def concatenacion(self, otro: 'AFNLambda') -> 'AFNLambda':
        """
        Concatenación de dos AFN-λ: L(M1) · L(M2).
        
        Construcción con ε-transiciones: Los estados finales de M1
        tienen ε-transiciones al estado inicial de M2.
        
        Formalmente: M = (Q1 ∪ Q2, Σ1 ∪ Σ2, δ, q01, F2)
        donde δ(qf, λ) ∋ q02 para cada qf ∈ F1
        """
        resultado = AFNLambda()
        resultado.alfabeto = self.alfabeto | otro.alfabeto

        # Copiar estados de M1
        prefijo1 = 'M1_'
        for estado in self.estados:
            resultado.agregar_estado(prefijo1 + estado)
        for estado in self.delta:
            for simbolo in self.delta[estado]:
                for destino in self.delta[estado][simbolo]:
                    resultado.definir_transicion(prefijo1 + estado, simbolo, prefijo1 + destino)

        # Copiar estados de M2
        prefijo2 = 'M2_'
        for estado in otro.estados:
            resultado.agregar_estado(prefijo2 + estado)
        for estado in otro.delta:
            for simbolo in otro.delta[estado]:
                for destino in otro.delta[estado][simbolo]:
                    resultado.definir_transicion(prefijo2 + estado, simbolo, prefijo2 + destino)

        # Estado inicial es el de M1
        resultado.definir_estado_inicial(prefijo1 + self.estado_inicial)

        # Agregar ε-transiciones de los estados finales de M1 al inicial de M2
        for ef in self.estados_finales:
            resultado.agregar_transicion_lambda(prefijo1 + ef, prefijo2 + otro.estado_inicial)

        # Estados finales son los de M2
        for ef in otro.estados_finales:
            resultado.agregar_estado_final(prefijo2 + ef)

        # Si λ ∈ L(M1), entonces los finales de M2 son alcanzables
        # directamente, lo cual ya está cubierto por la ε-transición
        # desde los finales de M1 al inicial de M2

        return resultado

    def clausura_kleene(self) -> 'AFNLambda':
        """
        Clausura de Kleene: L(M)* = ∪{L(M)^n : n ≥ 0}.
        
        Construcción con ε-transiciones:
        - Nuevo estado inicial q0 que es también final (λ ∈ L(M)*)
        - ε-transición de q0 a q0_old (estado inicial original)
        - ε-transiciones de los estados finales de M a q0_old
        
        Formalmente: M* = (Q ∪ {q0}, Σ, δ', q0, F ∪ {q0})
        donde δ' incluye:
          - δ'(q0, λ) = {q0_old}
          - δ'(qf, λ) ∋ q0_old para cada qf ∈ F
        """
        resultado = AFNLambda()
        resultado.alfabeto = set(self.alfabeto)

        # Crear nuevo estado inicial (también final por λ ∈ L(M)*)
        nuevo_inicial = self._nombre_unico('q0_kleene', resultado.estados)
        resultado.definir_estado_inicial(nuevo_inicial)
        resultado.agregar_estado_final(nuevo_inicial)

        # Copiar estados de M
        prefijo = 'K_'
        for estado in self.estados:
            resultado.agregar_estado(prefijo + estado)
        for estado in self.delta:
            for simbolo in self.delta[estado]:
                for destino in self.delta[estado][simbolo]:
                    resultado.definir_transicion(prefijo + estado, simbolo, prefijo + destino)

        # ε-transición del nuevo inicial al inicial original
        resultado.agregar_transicion_lambda(nuevo_inicial, prefijo + self.estado_inicial)

        # ε-transiciones de los estados finales al inicial original (iteración)
        for ef in self.estados_finales:
            resultado.agregar_transicion_lambda(prefijo + ef, prefijo + self.estado_inicial)

        # Estados finales de M también son finales en M*
        for ef in self.estados_finales:
            resultado.agregar_estado_final(prefijo + ef)

        return resultado

    def clausura_positiva(self) -> 'AFNLambda':
        """
        Clausura positiva: L(M)+ = ∪{L(M)^n : n ≥ 1}.
        
        L(M)+ = L(M) · L(M)*
        El nuevo estado inicial NO es final (λ ∉ L(M)+ salvo que λ ∈ L(M)).
        """
        resultado = AFNLambda()
        resultado.alfabeto = set(self.alfabeto)

        # Crear nuevo estado inicial (NO es final por defecto)
        nuevo_inicial = self._nombre_unico('q0_plus', resultado.estados)
        resultado.definir_estado_inicial(nuevo_inicial)

        # Copiar estados de M
        prefijo = 'P_'
        for estado in self.estados:
            resultado.agregar_estado(prefijo + estado)
        for estado in self.delta:
            for simbolo in self.delta[estado]:
                for destino in self.delta[estado][simbolo]:
                    resultado.definir_transicion(prefijo + estado, simbolo, prefijo + destino)

        # ε-transición del nuevo inicial al inicial original
        resultado.agregar_transicion_lambda(nuevo_inicial, prefijo + self.estado_inicial)

        # ε-transiciones de los estados finales al inicial original (iteración)
        for ef in self.estados_finales:
            resultado.agregar_transicion_lambda(prefijo + ef, prefijo + self.estado_inicial)

        # Estados finales de M son finales en M+
        for ef in self.estados_finales:
            resultado.agregar_estado_final(prefijo + ef)

        return resultado

    # ================================================================
    # Utilidades
    # ================================================================

    def to_dict(self) -> dict:
        """
        Serializa el AFN-λ a un diccionario (para JSON).
        Las transiciones λ se marcan con el símbolo 'λ'.
        """
        delta_list = []
        for estado in sorted(self.delta.keys()):
            for simbolo in sorted(self.delta[estado].keys()):
                for destino in sorted(self.delta[estado][simbolo]):
                    delta_list.append({
                        'desde': estado,
                        'simbolo': simbolo,
                        'hacia': destino
                    })

        return {
            'tipo': 'AFNLambda',
            'estados': sorted(self.estados),
            'alfabeto': sorted(self.alfabeto),
            'estado_inicial': self.estado_inicial,
            'estados_finales': sorted(self.estados_finales),
            'transiciones': delta_list
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AFNLambda':
        """
        Deserializa un AFN-λ desde un diccionario.
        Las transiciones con símbolo 'λ' se agregan como λ-transiciones (sin añadir λ al alfabeto).
        """
        afn_lambda = cls()
        for estado in data.get('estados', []):
            afn_lambda.agregar_estado(estado)
        for simbolo in data.get('alfabeto', []):
            afn_lambda.agregar_simbolo(simbolo)
        afn_lambda.definir_estado_inicial(data.get('estado_inicial', ''))
        for ef in data.get('estados_finales', []):
            afn_lambda.agregar_estado_final(ef)
        for t in data.get('transiciones', []):
            if t['simbolo'] == LAMBDA:
                # Lambda transition — must NOT add λ to the alphabet
                afn_lambda.agregar_transicion_lambda(t['desde'], t['hacia'])
            else:
                afn_lambda.definir_transicion(t['desde'], t['simbolo'], t['hacia'])
        return afn_lambda

    def clonar(self) -> 'AFNLambda':
        """
        Retorna una copia profunda del AFN-λ.
        """
        return copy.deepcopy(self)

    def __repr__(self) -> str:
        tiene_lambda = self.tiene_transiciones_lambda()
        return (f"AFNLambda(Q={self.estados}, Σ={self.alfabeto}, "
                f"q0='{self.estado_inicial}', F={self.estados_finales}, "
                f"tiene_λ={tiene_lambda})")
