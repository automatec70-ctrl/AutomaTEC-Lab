"""
AFN - Autómata Finito No Determinista

Definición formal: M = (Q, Σ, δ, q0, F)
  Q  = conjunto finito de estados
  Σ  = alfabeto de entrada
  δ  = Q × Σ → 2^Q (función de transición no determinista)
  q0 = estado inicial
  F  = conjunto de estados finales

Diferencia con AFD: δ(q, a) puede retornar un CONJUNTO de estados,
no uno solo. Esto permite que el autómata "explore" múltiples caminos.

Implementación con:
  - Construcción y modificación
  - Procesamiento de cadenas con conjunto de estados activos
  - Construcción de subconjuntos (AFN → AFD) con seguimiento de pasos
  - Operaciones regulares (unión, concatenación, clausura de Kleene, etc.)
  - Reverso del lenguaje
"""

from typing import Dict, Set, List, Tuple, Optional
import copy
from collections import deque


class AFN:
    """Autómata Finito No Determinista (AFN)"""

    def __init__(self):
        self.estados: Set[str] = set()
        self.alfabeto: Set[str] = set()
        # δ: Q × Σ → 2^Q — función de transición no determinista
        # Representación: delta[estado][simbolo] = conjunto de estados destino
        self.delta: Dict[str, Dict[str, Set[str]]] = {}
        self.estado_inicial: str = ''
        self.estados_finales: Set[str] = set()

    # ================================================================
    # Construcción del AFN
    # ================================================================

    def agregar_estado(self, nombre: str) -> bool:
        """
        Agrega un estado al conjunto Q.
        Retorna True si el estado era nuevo, False si ya existía.
        """
        if nombre in self.estados:
            return False
        self.estados.add(nombre)
        self.delta[nombre] = {}
        return True

    def eliminar_estado(self, nombre: str) -> None:
        """
        Elimina un estado del AFN.
        También elimina todas las transiciones que involucran al estado.
        """
        if nombre not in self.estados:
            return
        self.estados.discard(nombre)
        self.delta.pop(nombre, None)
        # Eliminar transiciones que llegan a este estado
        for estado in self.delta:
            for simbolo in list(self.delta[estado].keys()):
                self.delta[estado][simbolo].discard(nombre)
                # Limpiar conjuntos vacíos
                if not self.delta[estado][simbolo]:
                    del self.delta[estado][simbolo]
        self.estados_finales.discard(nombre)
        if self.estado_inicial == nombre:
            self.estado_inicial = ''

    def agregar_simbolo(self, simbolo: str) -> bool:
        """
        Agrega un símbolo al alfabeto Σ.
        Retorna True si era nuevo, False si ya existía.
        """
        if simbolo in self.alfabeto:
            return False
        self.alfabeto.add(simbolo)
        return True

    def eliminar_simbolo(self, simbolo: str) -> None:
        """
        Elimina un símbolo del alfabeto Σ.
        También elimina todas las transiciones que usan este símbolo.
        """
        if simbolo not in self.alfabeto:
            return
        self.alfabeto.discard(simbolo)
        for estado in self.delta:
            self.delta[estado].pop(simbolo, None)

    def definir_transicion(self, desde: str, simbolo: str, hacia: str) -> None:
        """
        Define δ(desde, simbolo) ∋ hacia.
        Agrega estados y símbolos automáticamente si no existen.
        A diferencia del AFD, puede haber múltiples transiciones
        para el mismo (estado, símbolo).
        """
        self.agregar_estado(desde)
        self.agregar_estado(hacia)
        self.agregar_simbolo(simbolo)
        if simbolo not in self.delta[desde]:
            self.delta[desde][simbolo] = set()
        self.delta[desde][simbolo].add(hacia)

    def eliminar_transicion(self, desde: str, simbolo: str, hacia: str = None) -> None:
        """
        Elimina una transición específica δ(desde, simbolo) ∋ hacia.
        Si hacia es None, elimina todas las transiciones δ(desde, simbolo).
        """
        if desde not in self.delta:
            return
        if simbolo not in self.delta[desde]:
            return
        if hacia is None:
            del self.delta[desde][simbolo]
        else:
            self.delta[desde][simbolo].discard(hacia)
            if not self.delta[desde][simbolo]:
                del self.delta[desde][simbolo]

    def definir_estado_inicial(self, estado: str) -> None:
        """
        Define q0 = estado.
        Agrega el estado a Q si no existe.
        """
        self.agregar_estado(estado)
        self.estado_inicial = estado

    def agregar_estado_final(self, estado: str) -> None:
        """
        Agrega estado al conjunto F de estados finales.
        """
        self.agregar_estado(estado)
        self.estados_finales.add(estado)

    def eliminar_estado_final(self, estado: str) -> None:
        """
        Elimina estado del conjunto F.
        """
        self.estados_finales.discard(estado)

    # ================================================================
    # Procesamiento de Cadenas
    # ================================================================

    def procesar_cadena(self, cadena: str) -> dict:
        """
        Simula el AFN sobre la cadena w, manteniendo el conjunto de
        estados activos en cada paso.
        
        Definición: δ*(q, wa) = ∪{δ(q', a) : q' ∈ δ*(q, w)}
        
        La cadena es aceptada si δ*(q0, w) ∩ F ≠ ∅.
        
        Retorna: {
          'aceptada': bool,
          'estados_finales_alcanzados': set de estados,
          'traza': lista de pasos con estados activos
        }
        """
        if not self.estado_inicial:
            return {
                'aceptada': False,
                'estados_finales_alcanzados': set(),
                'traza': [{'estados_activos': set(), 'cadena_restante': cadena, 'simbolo_leido': ''}]
            }

        # Estado inicial: {q0}
        estados_activos = {self.estado_inicial}
        traza = []

        # Registrar estado inicial
        traza.append({
            'estados_activos': set(estados_activos),
            'cadena_restante': cadena,
            'simbolo_leido': ''
        })

        for i, simbolo in enumerate(cadena):
            # Verificar que el símbolo pertenezca al alfabeto
            if simbolo not in self.alfabeto:
                traza.append({
                    'estados_activos': set(estados_activos),
                    'cadena_restante': cadena[i:],
                    'simbolo_leido': simbolo
                })
                return {
                    'aceptada': False,
                    'estados_finales_alcanzados': set(),
                    'traza': traza
                }

            # Aplicar δ a cada estado activo y unir los resultados
            # δ*(q, wa) = ∪{δ(q', a) : q' ∈ estados_activos}
            nuevos_estados: Set[str] = set()
            for estado in estados_activos:
                destinos = self.delta.get(estado, {}).get(simbolo, set())
                nuevos_estados.update(destinos)

            estados_activos = nuevos_estados
            cadena_restante = cadena[i + 1:]

            traza.append({
                'estados_activos': set(estados_activos),
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
    # Construcción de Subconjuntos (AFN → AFD)
    # ================================================================

    def construccion_subconjuntos(self) -> dict:
        """
        Construcción de subconjuntos: AFN → AFD.
        
        Teorema: Para todo AFN M, existe un AFD M' tal que L(M) = L(M').
        
        Algoritmo:
        1. Estado inicial del AFD = ε-clausura({q0}) (para AFN-λ) o {q0} (para AFN)
        2. Para cada estado del AFD T y cada a ∈ Σ:
           T' = δ(T, a) = ∪{δ(q, a) : q ∈ T}
           Si T' es nuevo, agregarlo como estado del AFD
        3. Estados finales del AFD = {T : T ∩ F ≠ ∅}
        
        Retorna: {
          'afd': AFD,
          'pasos': lista de pasos para visualización,
          'mapeo': dict de nombres de estados del AFD a conjuntos de estados del AFN
        }
        """
        from .afd import AFD

        pasos = []
        afd = AFD()
        afd.alfabeto = set(self.alfabeto)

        # Mapeo de conjuntos de estados a nombres
        # Para AFN sin epsilon: el estado inicial del AFD es {q0}
        estado_inicial_afd = frozenset({self.estado_inicial}) if self.estado_inicial else frozenset()
        nombre_inicial = self._nombre_estado_subconjunto(estado_inicial_afd)

        # Registro del mapeo
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

        paso_num = 0
        pasos.append({
            'descripcion': f'Paso 0: Estado inicial del AFD = {{{self.estado_inicial}}}',
            'estado_actual': nombre_inicial,
            'conjunto': sorted(estado_inicial_afd),
            'transiciones_generadas': []
        })

        while cola:
            conjunto_actual = cola.popleft()
            if conjunto_actual in procesados:
                continue
            procesados.add(conjunto_actual)

            nombre_actual = mapeo_inverso[conjunto_actual]
            transiciones_generadas = []

            for simbolo in sorted(self.alfabeto):
                # Calcular δ(conjunto_actual, simbolo) = ∪{δ(q, simbolo) : q ∈ conjunto_actual}
                nuevo_conjunto: Set[str] = set()
                for estado in conjunto_actual:
                    destinos = self.delta.get(estado, {}).get(simbolo, set())
                    nuevo_conjunto.update(destinos)

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
                    'conjunto_destino': sorted(nuevo_frozen),
                    'nombre_destino': nombre_nuevo
                })

            if transiciones_generadas:
                paso_num += 1
                pasos.append({
                    'descripcion': f'Paso {paso_num}: Procesar {nombre_actual} = {sorted(conjunto_actual)}',
                    'estado_actual': nombre_actual,
                    'conjunto': sorted(conjunto_actual),
                    'transiciones_generadas': transiciones_generadas
                })

        # Serializar mapeo para retorno
        mapeo_serializable = {nombre: sorted(conj) for nombre, conj in mapeo.items()}

        return {
            'afd': afd,
            'pasos': pasos,
            'mapeo': mapeo_serializable
        }

    def _nombre_estado_subconjunto(self, conjunto: frozenset) -> str:
        """
        Genera un nombre legible para un conjunto de estados.
        Ej: {q0, q1, q2} → "{q0,q1,q2}"
        """
        if not conjunto:
            return '∅'
        return '{' + ','.join(sorted(conjunto)) + '}'

    # ================================================================
    # Operaciones Regulares sobre AFN
    # ================================================================

    def union_afn(self, otro: 'AFN') -> 'AFN':
        """
        Unión de dos AFN: L(M1) ∪ L(M2).
        
        Construcción: Nuevo estado inicial q0 que tiene transiciones-ε
        a los estados iniciales de M1 y M2.
        
        Nota: Sin epsilon, usamos un nuevo estado inicial con transiciones
        por cada símbolo a los destinos de ambos estados iniciales.
        
        Formalmente: M = (Q1 ∪ Q2 ∪ {q0}, Σ1 ∪ Σ2, δ, q0, F1 ∪ F2)
        donde δ(q0, a) = δ1(q01, a) ∪ δ2(q02, a) para todo a ∈ Σ
        """
        resultado = AFN()
        resultado.alfabeto = self.alfabeto | otro.alfabeto

        # Crear nuevo estado inicial con nombre único
        nuevo_inicial = self._nombre_unico('q0_union', resultado.estados)
        resultado.definir_estado_inicial(nuevo_inicial)

        # Copiar estados y transiciones de self con prefijo
        prefijo1 = 'M1_'
        for estado in self.estados:
            nombre = prefijo1 + estado
            resultado.agregar_estado(nombre)

        for estado in self.delta:
            for simbolo in self.delta[estado]:
                for destino in self.delta[estado][simbolo]:
                    resultado.definir_transicion(prefijo1 + estado, simbolo, prefijo1 + destino)

        # Copiar estados y transiciones de otro con prefijo
        prefijo2 = 'M2_'
        for estado in otro.estados:
            nombre = prefijo2 + estado
            resultado.agregar_estado(nombre)

        for estado in otro.delta:
            for simbolo in otro.delta[estado]:
                for destino in otro.delta[estado][simbolo]:
                    resultado.definir_transicion(prefijo2 + estado, simbolo, prefijo2 + destino)

        # Agregar transiciones del nuevo estado inicial
        # δ(q0_nuevo, a) = δ1(q01, a) ∪ δ2(q02, a)
        for simbolo in resultado.alfabeto:
            destinos = set()
            # Transiciones desde el estado inicial de self
            for d in self.delta.get(self.estado_inicial, {}).get(simbolo, set()):
                destinos.add(prefijo1 + d)
            # Transiciones desde el estado inicial de otro
            for d in otro.delta.get(otro.estado_inicial, {}).get(simbolo, set()):
                destinos.add(prefijo2 + d)
            for destino in destinos:
                resultado.definir_transicion(nuevo_inicial, simbolo, destino)

        # Estados finales
        for ef in self.estados_finales:
            resultado.agregar_estado_final(prefijo1 + ef)
        for ef in otro.estados_finales:
            resultado.agregar_estado_final(prefijo2 + ef)

        # Si el estado inicial de alguno era final, el nuevo también
        if self.estado_inicial in self.estados_finales or otro.estado_inicial in otro.estados_finales:
            resultado.agregar_estado_final(nuevo_inicial)

        return resultado

    def concatenacion_afn(self, otro: 'AFN') -> 'AFN':
        """
        Concatenación de dos AFN: L(M1) · L(M2).
        
        Construcción: Los estados finales de M1 se conectan con
        transiciones al estado inicial de M2.
        
        Formalmente: M = (Q1 ∪ Q2, Σ1 ∪ Σ2, δ, q01, F2)
        donde δ se extiende: para cada qf ∈ F1 y a ∈ Σ:
          δ(qf, a) incluye δ2(q02, a)
        """
        resultado = AFN()
        resultado.alfabeto = self.alfabeto | otro.alfabeto

        # Copiar estados de M1
        prefijo1 = 'M1_'
        for estado in self.estados:
            resultado.agregar_estado(prefijo1 + estado)

        for estado in self.delta:
            for simbolo in self.delta[estado]:
                for destino in self.delta[estado][simbolo]:
                    resultado.definir_transicion(prefijo1 + estado, simbolo, prefijo1 + destino)

        # Estado inicial es el de M1
        resultado.definir_estado_inicial(prefijo1 + self.estado_inicial)

        # Copiar estados de M2
        prefijo2 = 'M2_'
        for estado in otro.estados:
            resultado.agregar_estado(prefijo2 + estado)

        for estado in otro.delta:
            for simbolo in otro.delta[estado]:
                for destino in otro.delta[estado][simbolo]:
                    resultado.definir_transicion(prefijo2 + estado, simbolo, prefijo2 + destino)

        # Conectar estados finales de M1 con el estado inicial de M2
        # Para cada estado final de M1 y cada símbolo:
        # δ(qf_M1, a) incluye δ2(q02_M2, a)
        for ef in self.estados_finales:
            for simbolo in resultado.alfabeto:
                destinos_m2 = otro.delta.get(otro.estado_inicial, {}).get(simbolo, set())
                for d in destinos_m2:
                    resultado.definir_transicion(prefijo1 + ef, simbolo, prefijo2 + d)

        # Estados finales son los de M2
        for ef in otro.estados_finales:
            resultado.agregar_estado_final(prefijo2 + ef)

        # Caso especial: si λ ∈ L(M1) (estado inicial de M1 es final),
        # entonces los finales de M2 son alcanzables directamente.
        if self.estado_inicial in self.estados_finales:
            for ef in otro.estados_finales:
                resultado.agregar_estado_final(prefijo2 + ef)

        # Caso especial: si λ ∈ L(M2) (estado inicial de M2 es final),
        # entonces los finales de M1 son también finales del resultado
        # (concatenar con la cadena vacía de M2).
        if otro.estado_inicial in otro.estados_finales:
            for ef in self.estados_finales:
                resultado.agregar_estado_final(prefijo1 + ef)

        return resultado

    def clausura_kleene(self) -> 'AFN':
        """
        Clausura de Kleene: L(M)* = ∪{L(M)^n : n ≥ 0}.
        
        Construcción: Nuevo estado inicial q0 que es también final.
        Los estados finales de M tienen transiciones al estado inicial original.
        
        Formalmente: M* = (Q ∪ {q0}, Σ, δ', q0, F ∪ {q0})
        donde δ' extiende δ con:
          - δ'(qf, a) incluye δ(q0_old, a) para cada qf ∈ F
        """
        resultado = AFN()
        resultado.alfabeto = set(self.alfabeto)

        # Crear nuevo estado inicial (también final por λ ∈ L(M)*)
        nuevo_inicial = self._nombre_unico('q0_kleene', resultado.estados)
        resultado.definir_estado_inicial(nuevo_inicial)
        resultado.agregar_estado_final(nuevo_inicial)  # λ ∈ L(M)*

        # Copiar estados de M
        prefijo = 'K_'
        for estado in self.estados:
            resultado.agregar_estado(prefijo + estado)

        for estado in self.delta:
            for simbolo in self.delta[estado]:
                for destino in self.delta[estado][simbolo]:
                    resultado.definir_transicion(prefijo + estado, simbolo, prefijo + destino)

        # Transiciones desde el nuevo estado inicial
        # δ(q0_nuevo, a) = δ(q0_viejo, a)
        for simbolo in resultado.alfabeto:
            destinos = self.delta.get(self.estado_inicial, {}).get(simbolo, set())
            for d in destinos:
                resultado.definir_transicion(nuevo_inicial, simbolo, prefijo + d)

        # Conectar estados finales de M al estado inicial original (para iteración)
        # δ(qf, a) incluye δ(q0_old, a) para cada qf ∈ F
        for ef in self.estados_finales:
            for simbolo in resultado.alfabeto:
                destinos = self.delta.get(self.estado_inicial, {}).get(simbolo, set())
                for d in destinos:
                    resultado.definir_transicion(prefijo + ef, simbolo, prefijo + d)

        # Estados finales de M también son finales en M*
        for ef in self.estados_finales:
            resultado.agregar_estado_final(prefijo + ef)

        return resultado

    def clausura_positiva(self) -> 'AFN':
        """
        Clausura positiva: L(M)+ = ∪{L(M)^n : n ≥ 1}.
        
        L(M)+ = L(M) · L(M)* = L(M) · M*
        No incluye λ a menos que λ ∈ L(M).
        """
        # L(M)+ = L(M) · L(M)*
        estrella = self.clausura_kleene()
        return self.concatenacion_afn(estrella)

    def reverso(self) -> 'AFN':
        """
        Reverso del lenguaje: L^R = {w^R : w ∈ L}.
        
        Construcción: Invertir todas las transiciones.
        El estado inicial original se convierte en final.
        Los estados finales se convierten en iniciales.
        
        Formalmente: M^R = (Q, Σ, δ^R, {q : q ∈ F}, {q0})
        donde δ^R(q', a) = {q : δ(q, a) ∋ q'}
        """
        resultado = AFN()
        resultado.alfabeto = set(self.alfabeto)

        # Copiar estados
        for estado in self.estados:
            resultado.agregar_estado(estado)

        # Invertir transiciones
        for estado in self.delta:
            for simbolo in self.delta[estado]:
                for destino in self.delta[estado][simbolo]:
                    resultado.definir_transicion(destino, simbolo, estado)

        # Nuevo estado inicial: los finales del original
        # Si hay múltiples finales, necesitamos un nuevo estado inicial
        if len(self.estados_finales) == 1:
            resultado.definir_estado_inicial(list(self.estados_finales)[0])
        else:
            nuevo_inicial = self._nombre_unico('q0_rev', resultado.estados)
            resultado.definir_estado_inicial(nuevo_inicial)
            # Agregar transiciones desde el nuevo estado inicial
            for ef in self.estados_finales:
                for simbolo in resultado.alfabeto:
                    # Invertir: buscar transiciones que llegaban a ef
                    for estado in self.delta:
                        if simbolo in self.delta[estado] and ef in self.delta[estado][simbolo]:
                            resultado.definir_transicion(nuevo_inicial, simbolo, estado)

        # Nuevo estado final: el inicial del original
        if self.estado_inicial:
            resultado.agregar_estado_final(self.estado_inicial)

        return resultado

    def _nombre_unico(self, base: str, existentes: Set[str]) -> str:
        """Genera un nombre único que no esté en existentes."""
        nombre = base
        contador = 0
        while nombre in existentes:
            contador += 1
            nombre = f'{base}_{contador}'
        return nombre

    # ================================================================
    # Utilidades
    # ================================================================

    def to_dict(self) -> dict:
        """
        Serializa el AFN a un diccionario (para JSON).
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
            'tipo': 'AFN',
            'estados': sorted(self.estados),
            'alfabeto': sorted(self.alfabeto),
            'estado_inicial': self.estado_inicial,
            'estados_finales': sorted(self.estados_finales),
            'transiciones': delta_list
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AFN':
        """
        Deserializa un AFN desde un diccionario.
        """
        afn = cls()
        for estado in data.get('estados', []):
            afn.agregar_estado(estado)
        for simbolo in data.get('alfabeto', []):
            afn.agregar_simbolo(simbolo)
        afn.definir_estado_inicial(data.get('estado_inicial', ''))
        for ef in data.get('estados_finales', []):
            afn.agregar_estado_final(ef)
        for t in data.get('transiciones', []):
            afn.definir_transicion(t['desde'], t['simbolo'], t['hacia'])
        return afn

    def clonar(self) -> 'AFN':
        """
        Retorna una copia profunda del AFN.
        """
        return copy.deepcopy(self)

    def __repr__(self) -> str:
        return (f"AFN(Q={self.estados}, Σ={self.alfabeto}, "
                f"q0='{self.estado_inicial}', F={self.estados_finales})")
