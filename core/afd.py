"""
AFD - Autómata Finito Determinista

Definición formal: M = (Q, Σ, δ, q0, F)
  Q  = conjunto finito de estados
  Σ  = alfabeto de entrada
  δ  = Q × Σ → Q (función de transición determinista)
  q0 = estado inicial
  F  = conjunto de estados finales

Implementación completa con:
  - Construcción y modificación
  - Procesamiento de cadenas con traza
  - Minimización por tabla de distinguibilidad (Hopcroft-like)
  - Equivalencia por producto cartesiano
  - Operaciones booleanas (unión, intersección, diferencia, complemento)
  - Propiedades del lenguaje (vacío, finito, infinito)
  - Análisis de estados (accesibles, productivos, útiles)
"""

from typing import Dict, Set, List, Tuple, Optional
import copy
from collections import deque


class AFD:
    """Autómata Finito Determinista (AFD)"""

    def __init__(self):
        self.estados: Set[str] = set()
        self.alfabeto: Set[str] = set()
        # δ: Q × Σ → Q — función de transición determinista
        # Representación: delta[estado][simbolo] = estado_destino
        self.delta: Dict[str, Dict[str, str]] = {}
        self.estado_inicial: str = ''
        self.estados_finales: Set[str] = set()

    # ================================================================
    # 1.1 Construcción del AFD
    # ================================================================

    def agregar_estado(self, nombre: str) -> bool:
        """
        Agrega un estado al conjunto Q.
        Retorna True si el estado era nuevo, False si ya existía.
        """
        if nombre in self.estados:
            return False
        self.estados.add(nombre)
        # Inicializar diccionario de transiciones para el nuevo estado
        self.delta[nombre] = {}
        return True

    def eliminar_estado(self, nombre: str) -> None:
        """
        Elimina un estado del AFD.
        También elimina todas las transiciones que involucran al estado.
        """
        if nombre not in self.estados:
            return
        self.estados.discard(nombre)
        # Eliminar transiciones que salen de este estado
        self.delta.pop(nombre, None)
        # Eliminar transiciones que llegan a este estado
        for estado in self.delta:
            simbolos_a_eliminar = []
            for simbolo, destino in self.delta[estado].items():
                if destino == nombre:
                    simbolos_a_eliminar.append(simbolo)
            for s in simbolos_a_eliminar:
                del self.delta[estado][s]
        # Eliminar de estados finales si corresponde
        self.estados_finales.discard(nombre)
        # Limpiar estado inicial si era este
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
        # Eliminar todas las transiciones que usan este símbolo
        for estado in self.delta:
            self.delta[estado].pop(simbolo, None)

    def definir_transicion(self, desde: str, simbolo: str, hacia: str) -> None:
        """
        Define δ(desde, simbolo) = hacia.
        Agrega estados y símbolos automáticamente si no existen.
        """
        # Asegurar que los estados y el símbolo existan
        self.agregar_estado(desde)
        self.agregar_estado(hacia)
        self.agregar_simbolo(simbolo)
        # Definir la transición
        self.delta[desde][simbolo] = hacia

    def eliminar_transicion(self, desde: str, simbolo: str) -> None:
        """
        Elimina la transición δ(desde, simbolo).
        """
        if desde in self.delta:
            self.delta[desde].pop(simbolo, None)

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
        Agrega el estado a Q si no existe.
        """
        self.agregar_estado(estado)
        self.estados_finales.add(estado)

    def eliminar_estado_final(self, estado: str) -> None:
        """
        Elimina estado del conjunto F de estados finales.
        """
        self.estados_finales.discard(estado)

    # ================================================================
    # Completitud
    # ================================================================

    def es_completo(self) -> bool:
        """
        Verifica si δ está totalmente definida para todo q ∈ Q, a ∈ Σ.
        Un AFD es completo si ∀q ∈ Q, ∀a ∈ Σ: δ(q, a) está definida.
        """
        for estado in self.estados:
            for simbolo in self.alfabeto:
                if estado not in self.delta:
                    return False
                if simbolo not in self.delta[estado]:
                    return False
        return True

    def completar_con_estado_muerto(self) -> str:
        """
        Agrega un estado muerto (∅) para completar δ.
        El estado muerto tiene transiciones hacia sí mismo para todo símbolo.
        Retorna el nombre del estado muerto creado.
        
        Teorema: Todo AFD puede completarse agregando un estado trampa
        sin cambiar el lenguaje aceptado.
        """
        # Buscar un nombre único para el estado muerto
        nombre_muerto = '∅'
        contador = 0
        while nombre_muerto in self.estados:
            contador += 1
            nombre_muerto = f'muerto_{contador}'

        self.agregar_estado(nombre_muerto)

        # El estado muerto tiene transiciones hacia sí mismo para todo símbolo
        for simbolo in self.alfabeto:
            self.delta[nombre_muerto][simbolo] = nombre_muerto

        # Completar transiciones faltantes hacia el estado muerto
        for estado in self.estados:
            if estado == nombre_muerto:
                continue
            for simbolo in self.alfabeto:
                if simbolo not in self.delta.get(estado, {}):
                    self.delta[estado][simbolo] = nombre_muerto

        return nombre_muerto

    # ================================================================
    # 1.3 Procesamiento de Cadenas
    # ================================================================

    def procesar_cadena(self, cadena: str) -> dict:
        """
        Función de transición extendida δ*(q0, w).
        
        Simula el AFD sobre la cadena w, recorriendo estado a estado.
        Retorna un diccionario con:
          - 'aceptada': bool — si la cadena es aceptada
          - 'traza': lista de pasos, cada uno con:
              - 'estado': estado actual antes de leer el símbolo
              - 'cadena_restante': cadena que falta por procesar
              - 'simbolo_leido': símbolo que se lee en este paso (vacío al final)
        """
        estado_actual = self.estado_inicial
        traza = []

        # Si no hay estado inicial, la cadena no puede ser procesada
        if not self.estado_inicial:
            return {
                'aceptada': False,
                'traza': [{'estado': '', 'cadena_restante': cadena, 'simbolo_leido': ''}]
            }

        # Registro del estado inicial antes de procesar
        traza.append({
            'estado': estado_actual,
            'cadena_restante': cadena,
            'simbolo_leido': ''
        })

        for i, simbolo in enumerate(cadena):
            # Verificar que el símbolo pertenezca al alfabeto
            if simbolo not in self.alfabeto:
                traza.append({
                    'estado': estado_actual,
                    'cadena_restante': cadena[i:],
                    'simbolo_leido': simbolo
                })
                return {'aceptada': False, 'traza': traza}

            # Verificar que la transición exista
            if estado_actual not in self.delta or simbolo not in self.delta[estado_actual]:
                traza.append({
                    'estado': estado_actual,
                    'cadena_restante': cadena[i:],
                    'simbolo_leido': simbolo
                })
                return {'aceptada': False, 'traza': traza}

            # Aplicar δ(estado_actual, simbolo) = siguiente_estado
            estado_actual = self.delta[estado_actual][simbolo]
            cadena_restante = cadena[i + 1:]

            traza.append({
                'estado': estado_actual,
                'cadena_restante': cadena_restante,
                'simbolo_leido': simbolo
            })

        # La cadena es aceptada si el estado final está en F
        aceptada = estado_actual in self.estados_finales
        return {'aceptada': aceptada, 'traza': traza}

    # ================================================================
    # 1.4 Minimización (Tabla de Distinguibilidad)
    # ================================================================

    def minimizar(self) -> dict:
        """
        Algoritmo de minimización por tabla de distinguibilidad.
        
        Teorema de Myhill-Nerode: Para cada lenguaje regular L,
        existe un único AFD mínimo (salvo isomorfismo) que acepta L.
        
        Algoritmo:
        1. Construir tabla de pares de estados {(p, q) : p < q}
        2. Marcar pares (p, q) donde p ∈ F y q ∉ F (o viceversa) — base
        3. Para cada par no marcado (p, q) y cada a ∈ Σ:
           Si (δ(p,a), δ(q,a)) está marcado → marcar (p, q)
        4. Repetir paso 3 hasta que no haya cambios
        5. Los pares no marcados forman clases de equivalencia
        
        Retorna: {
          'afd_minimo': AFD,
          'pasos': lista de pasos con tabla y clases,
          'clases_finales': lista de clases de equivalencia
        }
        """
        pasos = []

        # Eliminar estados no accesibles primero
        afd_limpio = self.limpiar()
        estados = sorted(afd_limpio.estados)
        alfabeto = sorted(afd_limpio.alfabeto)

        # Paso 0: Casos especiales
        if len(estados) <= 1:
            clases = [list(estados)] if estados else []
            return {
                'afd_minimo': afd_limpio.clonar(),
                'pasos': [{
                    'tabla': {},
                    'clases': clases,
                    'descripcion': 'AFD con 0 o 1 estado ya es mínimo.'
                }],
                'clases_finales': clases
            }

        # Paso 1: Construir tabla de pares — todos los pares (p, q) con p < q
        # tabla[(p, q)] = True si son distinguibles, False si no se ha determinado
        tabla: Dict[Tuple[str, str], bool] = {}
        for i in range(len(estados)):
            for j in range(i + 1, len(estados)):
                tabla[(estados[i], estados[j])] = False

        # Paso 2: Marcar base — pares donde uno es final y el otro no
        # Esto se debe a que todo estado final qf ∈ F distingue cadenas
        # (acepta λ si es estado final), mientras que qn ∉ F no.
        for (p, q) in tabla:
            if (p in afd_limpio.estados_finales) != (q in afd_limpio.estados_finales):
                tabla[(p, q)] = True

        # Guardar paso inicial
        tabla_serializable = {f"({p},{q})": v for (p, q), v in tabla.items()}
        clases_iniciales = self._calcular_clases(tabla, estados)
        pasos.append({
            'tabla': tabla_serializable,
            'clases': clases_iniciales,
            'descripcion': 'Base: marcar pares (p,q) donde p∈F y q∉F (o viceversa). '
                          'Un estado final distingue λ mientras que uno no-final no la acepta.'
        })

        # Paso 3: Propagar marcas iterativamente
        # Si para algún a ∈ Σ, (δ(p,a), δ(q,a)) ya está marcado,
        # entonces (p,q) también es distinguible.
        cambio = True
        iteracion = 1
        while cambio:
            cambio = False
            for (p, q) in tabla:
                if tabla[(p, q)]:
                    continue  # Ya está marcado
                for a in alfabeto:
                    # Obtener δ(p, a) y δ(q, a)
                    dp = afd_limpio.delta.get(p, {}).get(a)
                    dq = afd_limpio.delta.get(q, {}).get(a)

                    # Tratar transición indefinida como transición al estado muerto
                    # implícito (no final, sin transiciones salientes).
                    # Un estado muerto es distinguible de cualquier estado final
                    # y es indistinguible de otro estado muerto.
                    DEAD = '__dead__'
                    dp_eff = dp if dp is not None else DEAD
                    dq_eff = dq if dq is not None else DEAD

                    if dp_eff == dq_eff:
                        continue  # Van al mismo destino efectivo, no distingue

                    # Si uno va al estado muerto (no final) y el otro es final → distinguibles
                    if dp_eff == DEAD and dq_eff in afd_limpio.estados_finales:
                        tabla[(p, q)] = True
                        cambio = True
                        break
                    if dq_eff == DEAD and dp_eff in afd_limpio.estados_finales:
                        tabla[(p, q)] = True
                        cambio = True
                        break

                    # Ambos van a estados reales distintos → propagar normalmente
                    if dp_eff == DEAD or dq_eff == DEAD:
                        # Uno va al muerto (no final), el otro a un estado real no final
                        # → indistinguibles en este símbolo por ahora (propagar no aplica)
                        continue

                    # Normalizar el par para buscar en la tabla
                    par_destino = (min(dp_eff, dq_eff), max(dp_eff, dq_eff))
                    if par_destino in tabla and tabla[par_destino]:
                        tabla[(p, q)] = True
                        cambio = True
                        break

            if cambio:
                tabla_serializable = {f"({p},{q})": v for (p, q), v in tabla.items()}
                clases_iter = self._calcular_clases(tabla, estados)
                pasos.append({
                    'tabla': tabla_serializable,
                    'clases': clases_iter,
                    'descripcion': f'Iteración {iteracion}: Si (δ(p,a), δ(q,a)) está marcado '
                                  f'para algún a ∈ Σ, entonces (p,q) es distinguible.'
                })
                iteracion += 1

        # Paso 4: Calcular clases de equivalencia finales
        clases_finales = self._calcular_clases(tabla, estados)

        # Paso 5: Construir AFD mínimo
        afd_minimo = afd_limpio.construir_afd_minimo(clases_finales)

        return {
            'afd_minimo': afd_minimo,
            'pasos': pasos,
            'clases_finales': clases_finales
        }

    def _calcular_clases(self, tabla: Dict[Tuple[str, str], bool], estados: List[str]) -> List[List[str]]:
        """
        Calcula las clases de equivalencia a partir de la tabla de distinguibilidad.
        Dos estados están en la misma clase si no están marcados como distinguibles.
        
        Usa Union-Find para agrupar estados equivalentes.
        """
        if not estados:
            return []

        # Inicialmente cada estado está en su propia clase
        padre = {e: e for e in estados}

        def encontrar(x):
            while padre[x] != x:
                padre[x] = padre[padre[x]]
                x = padre[x]
            return x

        def unir(x, y):
            rx, ry = encontrar(x), encontrar(y)
            if rx != ry:
                padre[rx] = ry

        # Unir estados que NO son distinguibles
        for (p, q), marcado in tabla.items():
            if not marcado:
                unir(p, q)

        # Agrupar por raíz
        clases_dict: Dict[str, List[str]] = {}
        for estado in estados:
            raiz = encontrar(estado)
            if raiz not in clases_dict:
                clases_dict[raiz] = []
            clases_dict[raiz].append(estado)

        # Retornar como lista de listas ordenadas
        return sorted([sorted(clase) for clase in clases_dict.values()], key=lambda c: c[0])

    def tabla_distinguibilidad(self) -> list:
        """
        Retorna los pasos del algoritmo de tabla de distinguibilidad
        para visualización.
        """
        resultado = self.minimizar()
        return resultado['pasos']

    def construir_afd_minimo(self, clases: list) -> 'AFD':
        """
        Construye el AFD mínimo a partir de las clases de equivalencia.
        
        Cada clase se convierte en un estado del AFD mínimo.
        La transición entre clases se hereda de cualquier estado representante.
        
        Teorema: El AFD resultante es el único AFD mínimo (salvo renombramiento)
        que acepta el mismo lenguaje.
        """
        afd_min = AFD()
        afd_min.alfabeto = set(self.alfabeto)

        # Mapear cada estado a su clase
        estado_a_clase: Dict[str, str] = {}
        for clase in clases:
            # Nombre de la clase: {q0, q1, q2} o nombre del representante
            nombre_clase = '{' + ','.join(sorted(clase)) + '}'
            for estado in clase:
                estado_a_clase[estado] = nombre_clase

        # Agregar estados (las clases)
        for clase in clases:
            nombre_clase = '{' + ','.join(sorted(clase)) + '}'
            afd_min.agregar_estado(nombre_clase)

            # Determinar si la clase contiene al estado inicial
            if self.estado_inicial in clase:
                afd_min.definir_estado_inicial(nombre_clase)

            # Determinar si la clase contiene algún estado final
            if any(e in self.estados_finales for e in clase):
                afd_min.agregar_estado_final(nombre_clase)

        # Definir transiciones
        # Para cada clase y cada símbolo, δ(clase, a) = clase de δ(representante, a)
        for clase in clases:
            nombre_clase = '{' + ','.join(sorted(clase)) + '}'
            representante = clase[0]  # Cualquier estado de la clase sirve
            for simbolo in self.alfabeto:
                destino = self.delta.get(representante, {}).get(simbolo)
                if destino is not None and destino in estado_a_clase:
                    afd_min.definir_transicion(
                        nombre_clase,
                        simbolo,
                        estado_a_clase[destino]
                    )

        return afd_min

    # ================================================================
    # 1.5 Equivalencia
    # ================================================================

    def son_equivalentes(self, otro: 'AFD') -> dict:
        """
        Determina si dos AFDs son equivalentes usando el producto cartesiano.
        
        L(M1) = L(M2) ⟺ L(M1) △ L(M2) = ∅
        
        Construimos el AFD producto M1 × M2 donde los estados finales son:
          - F_Δ = {(q1,q2) : q1∈F1 ⊕ q2∈F2}  (diferencia simétrica)
        
        Si M_Δ acepta alguna cadena → M1 y M2 NO son equivalentes.
        La cadena testigo se obtiene por BFS en M_Δ.
        
        Retorna: {
          'equivalentes': bool,
          'cadena_testigo': str|None,
          'afd_producto': AFD|None
        }
        """
        # Unificar alfabetos
        alfabeto = self.alfabeto | otro.alfabeto

        # Completar ambos AFDs con estado muerto si es necesario
        afd1 = self.clonar()
        afd2 = otro.clonar()

        # Agregar símbolos faltantes a cada AFD
        for s in alfabeto:
            afd1.agregar_simbolo(s)
            afd2.agregar_simbolo(s)

        # Completar con estado muerto
        afd1.completar_con_estado_muerto()
        afd2.completar_con_estado_muerto()

        # Construir AFD producto para la diferencia simétrica
        afd_producto = AFD()
        afd_producto.alfabeto = set(alfabeto)

        # Cola para BFS sobre el producto cartesiano
        cola = deque()
        visitados: Set[Tuple[str, str]] = set()

        # Estado inicial del producto
        estado_inicial_prod = (afd1.estado_inicial, afd2.estado_inicial)
        nombre_inicial = f'({afd1.estado_inicial},{afd2.estado_inicial})'
        afd_producto.agregar_estado(nombre_inicial)
        afd_producto.definir_estado_inicial(nombre_inicial)

        # Marcar como final si uno es final y el otro no (diferencia simétrica)
        q1_final = afd1.estado_inicial in afd1.estados_finales
        q2_final = afd2.estado_inicial in afd2.estados_finales
        if q1_final != q2_final:
            afd_producto.agregar_estado_final(nombre_inicial)

        cola.append((estado_inicial_prod, nombre_inicial))
        visitados.add(estado_inicial_prod)

        # Para rastrear la cadena testigo
        padre_estado: Dict[str, Tuple[str, str]] = {}  # nombre_hijo -> (nombre_padre, simbolo)

        cadena_testigo = None

        while cola:
            (q1, q2), nombre_actual = cola.popleft()

            for simbolo in sorted(alfabeto):
                # δ1(q1, a) y δ2(q2, a)
                d1 = afd1.delta.get(q1, {}).get(simbolo, q1)
                d2 = afd2.delta.get(q2, {}).get(simbolo, q2)

                par_destino = (d1, d2)
                nombre_destino = f'({d1},{d2})'

                # Agregar transición al producto
                afd_producto.agregar_estado(nombre_destino)
                afd_producto.definir_transicion(nombre_actual, simbolo, nombre_destino)

                # Verificar si es final (diferencia simétrica)
                d1_final = d1 in afd1.estados_finales
                d2_final = d2 in afd2.estados_finales
                if d1_final != d2_final:
                    afd_producto.agregar_estado_final(nombre_destino)
                    # Encontramos un estado final alcanzable → no son equivalentes
                    if cadena_testigo is None:
                        # Reconstruir la cadena testigo por BFS
                        cadena_testigo = self._reconstruir_cadena(
                            padre_estado, nombre_inicial, nombre_actual, simbolo, nombre_destino
                        )

                if par_destino not in visitados:
                    visitados.add(par_destino)
                    padre_estado[nombre_destino] = (nombre_actual, simbolo)
                    cola.append((par_destino, nombre_destino))

        equivalentes = len(afd_producto.estados_finales) == 0

        return {
            'equivalentes': equivalentes,
            'cadena_testigo': cadena_testigo if not equivalentes else None,
            'afd_producto': afd_producto if not equivalentes else None
        }

    def _reconstruir_cadena(self, padre_estado: Dict, inicio: str,
                            padre_actual: str, simbolo_final: str,
                            destino_final: str) -> str:
        """
        Reconstruye la cadena testigo recorriendo el camino BFS
        desde el estado inicial hasta el estado final encontrado.
        """
        cadena = [simbolo_final]
        actual = padre_actual

        while actual != inicio:
            if actual in padre_estado:
                padre, simb = padre_estado[actual]
                cadena.append(simb)
                actual = padre
            else:
                break

        return ''.join(reversed(cadena))

    # ================================================================
    # 1.6 Operaciones Booleanas
    # ================================================================

    def _producto_cartesiano(self, otro: 'AFD', condicion_final) -> 'AFD':
        """
        Construcción genérica de producto cartesiano.
        condicion_final(q1_final, q2_final) → bool determina si (q1,q2) es final.
        
        Sea M1 = (Q1, Σ, δ1, q01, F1) y M2 = (Q2, Σ, δ2, q02, F2).
        El producto M = (Q1 × Q2, Σ, δ, (q01,q02), F) donde:
          δ((q1,q2), a) = (δ1(q1,a), δ2(q2,a))
        """
        # Unificar alfabetos
        alfabeto = self.alfabeto | otro.alfabeto

        # Completar ambos AFDs
        afd1 = self.clonar()
        afd2 = otro.clonar()

        for s in alfabeto:
            afd1.agregar_simbolo(s)
            afd2.agregar_simbolo(s)
        afd1.completar_con_estado_muerto()
        afd2.completar_con_estado_muerto()

        # Construir AFD producto
        afd_prod = AFD()
        afd_prod.alfabeto = set(alfabeto)

        # BFS para construir todos los estados alcanzables del producto
        cola = deque()
        visitados: Set[Tuple[str, str]] = set()

        estado_inicial = (afd1.estado_inicial, afd2.estado_inicial)
        nombre_inicial = f'({afd1.estado_inicial},{afd2.estado_inicial})'

        afd_prod.agregar_estado(nombre_inicial)
        afd_prod.definir_estado_inicial(nombre_inicial)

        # Verificar si es estado final según la condición
        q1_final = afd1.estado_inicial in afd1.estados_finales
        q2_final = afd2.estado_inicial in afd2.estados_finales
        if condicion_final(q1_final, q2_final):
            afd_prod.agregar_estado_final(nombre_inicial)

        cola.append(estado_inicial)
        visitados.add(estado_inicial)

        # Mapeo de pares a nombres
        nombres = {estado_inicial: nombre_inicial}

        while cola:
            q1, q2 = cola.popleft()
            nombre_actual = nombres[(q1, q2)]

            for simbolo in sorted(alfabeto):
                d1 = afd1.delta.get(q1, {}).get(simbolo, q1)
                d2 = afd2.delta.get(q2, {}).get(simbolo, q2)

                par_destino = (d1, d2)

                if par_destino not in nombres:
                    nombre_destino = f'({d1},{d2})'
                    nombres[par_destino] = nombre_destino
                    afd_prod.agregar_estado(nombre_destino)

                    d1_final = d1 in afd1.estados_finales
                    d2_final = d2 in afd2.estados_finales
                    if condicion_final(d1_final, d2_final):
                        afd_prod.agregar_estado_final(nombre_destino)

                nombre_destino = nombres[par_destino]
                afd_prod.definir_transicion(nombre_actual, simbolo, nombre_destino)

                if par_destino not in visitados:
                    visitados.add(par_destino)
                    cola.append(par_destino)

        return afd_prod

    def union(self, otro: 'AFD') -> 'AFD':
        """
        Unión: L(M1) ∪ L(M2).
        Estados finales: F = {(q1,q2) : q1 ∈ F1 ∨ q2 ∈ F2}
        """
        return self._producto_cartesiano(otro, lambda f1, f2: f1 or f2)

    def interseccion(self, otro: 'AFD') -> 'AFD':
        """
        Intersección: L(M1) ∩ L(M2).
        Estados finales: F = {(q1,q2) : q1 ∈ F1 ∧ q2 ∈ F2}
        """
        return self._producto_cartesiano(otro, lambda f1, f2: f1 and f2)

    def diferencia(self, otro: 'AFD') -> 'AFD':
        """
        Diferencia: L(M1) - L(M2) = L(M1) ∩ L(M2)ᶜ.
        Estados finales: F = {(q1,q2) : q1 ∈ F1 ∧ q2 ∉ F2}
        """
        return self._producto_cartesiano(otro, lambda f1, f2: f1 and not f2)

    def complemento(self) -> 'AFD':
        """
        Complemento: L(M)ᶜ = Σ* - L(M).
        
        Teorema: Si M es un AFD completo, entonces intercambiando
        estados finales y no finales se obtiene el complemento.
        
        F' = Q - F
        """
        afd_comp = self.clonar()

        # Asegurar que el AFD esté completo
        if not afd_comp.es_completo():
            afd_comp.completar_con_estado_muerto()

        # Intercambiar estados finales y no finales
        afd_comp.estados_finales = afd_comp.estados - afd_comp.estados_finales
        return afd_comp

    # ================================================================
    # 1.7 Propiedades del Lenguaje
    # ================================================================

    def es_lenguaje_vacio(self) -> bool:
        """
        L(M) = ∅ ⟺ No existe camino de q0 a ningún qf ∈ F.
        
        Verificamos si algún estado final es alcanzable desde q0
        usando BFS.
        """
        if not self.estado_inicial:
            return True

        # BFS desde el estado inicial
        visitados = set()
        cola = deque([self.estado_inicial])
        visitados.add(self.estado_inicial)

        while cola:
            estado = cola.popleft()
            if estado in self.estados_finales:
                return False  # Encontramos un estado final alcanzable
            for simbolo in self.alfabeto:
                destino = self.delta.get(estado, {}).get(simbolo)
                if destino and destino not in visitados:
                    visitados.add(destino)
                    cola.append(destino)

        return True  # Ningún estado final es alcanzable

    def es_lenguaje_infinito(self) -> bool:
        """
        L(M) es infinito ⟺ Existe un ciclo en el camino de q0 a algún qf ∈ F.
        
        Por el lema de bombeo: si |w| ≥ |Q|, entonces w pasa por algún
        estado dos veces, creando un ciclo que puede bombearse.
        
        Algoritmo: L es infinito ⟺ ∃ estado q accesible y productivo
        que está en un ciclo (pertenece a un SCC no trivial).
        """
        if self.es_lenguaje_vacio():
            return False

        accesibles = self.estados_accesibles()
        productivos = self.estados_productivos()
        utiles = accesibles & productivos

        # Buscar ciclos entre estados útiles
        # Si hay un camino de longitud ≥ |utiles| que lleva a un estado final,
        # entonces hay un ciclo
        # Usamos DFS para detectar ciclos alcanzables desde q0 que llegan a F

        # Construir grafo de estados útiles
        # Verificar si existe algún ciclo entre estados útiles
        # Usamos la condición: L es infinito ⟺ ∃q ∈ Utiles tal que
        # existe un camino no trivial de q a q mismo (pasando por estados útiles)

        for estado in utiles:
            if self._hay_ciclo_desde(estado, utiles):
                return True

        return False

    def _hay_ciclo_desde(self, inicio: str, estados_validos: Set[str]) -> bool:
        """Verifica si hay un ciclo desde 'inicio' pasando por estados_validos."""
        for simbolo in self.alfabeto:
            destino = self.delta.get(inicio, {}).get(simbolo)
            if destino and destino in estados_validos:
                # BFS desde destino para ver si podemos volver a inicio
                visitados = set()
                cola = deque([destino])
                visitados.add(destino)
                while cola:
                    e = cola.popleft()
                    if e == inicio:
                        return True
                    for s in self.alfabeto:
                        d = self.delta.get(e, {}).get(s)
                        if d and d in estados_validos and d not in visitados:
                            visitados.add(d)
                            cola.append(d)
        return False

    def es_lenguaje_finito(self) -> bool:
        """L(M) es finito ⟺ L(M) no es infinito y L(M) no es vacío (o sí)."""
        return not self.es_lenguaje_infinito()

    def cadena_mas_corta(self) -> Optional[str]:
        """
        Encuentra la cadena más corta aceptada por el AFD usando BFS.
        
        BFS garantiza encontrar el camino más corto de q0 a cualquier qf ∈ F.
        Retorna None si el lenguaje es vacío.
        """
        if not self.estado_inicial:
            return None

        if self.estado_inicial in self.estados_finales:
            return ''  # λ es aceptada

        # BFS: cada nodo lleva (estado, cadena_acumulada)
        visitados = {self.estado_inicial}
        cola = deque([(self.estado_inicial, '')])

        while cola:
            estado, cadena = cola.popleft()

            for simbolo in sorted(self.alfabeto):
                destino = self.delta.get(estado, {}).get(simbolo)
                if destino is None:
                    continue
                nueva_cadena = cadena + simbolo

                if destino in self.estados_finales:
                    return nueva_cadena

                if destino not in visitados:
                    visitados.add(destino)
                    cola.append((destino, nueva_cadena))

        return None  # Lenguaje vacío

    def estados_accesibles(self) -> Set[str]:
        """
        Un estado q es accesible si existe un camino de q0 a q.
        Calculamos por BFS desde q0.
        """
        if not self.estado_inicial:
            return set()

        visitados = set()
        cola = deque([self.estado_inicial])
        visitados.add(self.estado_inicial)

        while cola:
            estado = cola.popleft()
            for simbolo in self.alfabeto:
                destino = self.delta.get(estado, {}).get(simbolo)
                if destino and destino not in visitados:
                    visitados.add(destino)
                    cola.append(destino)

        return visitados

    def estados_productivos(self) -> Set[str]:
        """
        Un estado q es productivo (o co-accesible) si existe un camino de q a algún qf ∈ F.
        Calculamos por BFS inverso desde F (siguiendo transiciones al revés).
        """
        if not self.estados_finales:
            return set()

        # Construir grafo inverso
        inverso: Dict[str, Set[str]] = {e: set() for e in self.estados}
        for estado in self.estados:
            for simbolo in self.alfabeto:
                destino = self.delta.get(estado, {}).get(simbolo)
                if destino and destino in self.estados:
                    inverso[destino].add(estado)

        # BFS inverso desde todos los estados finales
        visitados = set()
        cola = deque()
        for ef in self.estados_finales:
            if ef in self.estados:
                visitados.add(ef)
                cola.append(ef)

        while cola:
            estado = cola.popleft()
            for predecesor in inverso.get(estado, []):
                if predecesor not in visitados:
                    visitados.add(predecesor)
                    cola.append(predecesor)

        return visitados

    def estados_utiles(self) -> Set[str]:
        """
        Un estado q es útil si es accesible Y productivo.
        Es decir, existe un camino de q0 a q y de q a algún qf ∈ F.
        Los estados no útiles pueden eliminarse sin afectar L(M).
        """
        return self.estados_accesibles() & self.estados_productivos()

    def limpiar(self) -> 'AFD':
        """
        Retorna una copia del AFD sin estados no útiles.
        Elimina estados que no son accesibles o no son productivos.

        Caso especial: si no hay estados útiles pero existe estado inicial
        (DFA sin estados finales → lenguaje vacío ∅), se preserva el estado
        inicial como único estado del AFD limpio.  El AFD resultante es el
        representante canónico del lenguaje vacío: un único estado no final
        con ninguna transición saliente hacia estados útiles.
        """
        utiles = self.estados_utiles()

        # DFA sin estados finales: estados_productivos() devuelve set() vacío,
        # por lo que utiles queda vacío y limpiar() produciría un AFD sin
        # estado inicial (inválido).  En su lugar preservamos el estado inicial
        # como representación válida del lenguaje vacío ∅.
        if not utiles and self.estado_inicial:
            utiles = {self.estado_inicial}

        afd_limpio = AFD()
        afd_limpio.alfabeto = set(self.alfabeto)

        # Solo agregar estados útiles
        for estado in utiles:
            afd_limpio.agregar_estado(estado)

        # Estado inicial
        if self.estado_inicial in utiles:
            afd_limpio.definir_estado_inicial(self.estado_inicial)

        # Estados finales
        for ef in self.estados_finales:
            if ef in utiles:
                afd_limpio.agregar_estado_final(ef)

        # Transiciones entre estados útiles
        for estado in utiles:
            for simbolo in self.alfabeto:
                destino = self.delta.get(estado, {}).get(simbolo)
                if destino and destino in utiles:
                    afd_limpio.definir_transicion(estado, simbolo, destino)

        return afd_limpio

    # ================================================================
    # Utilidades
    # ================================================================

    def to_dict(self) -> dict:
        """
        Serializa el AFD a un diccionario (para JSON).
        Las conjuntos se convierten a listas ordenadas.
        """
        delta_list = []
        for estado in sorted(self.delta.keys()):
            for simbolo in sorted(self.delta[estado].keys()):
                delta_list.append({
                    'desde': estado,
                    'simbolo': simbolo,
                    'hacia': self.delta[estado][simbolo]
                })

        return {
            'tipo': 'AFD',
            'estados': sorted(self.estados),
            'alfabeto': sorted(self.alfabeto),
            'estado_inicial': self.estado_inicial,
            'estados_finales': sorted(self.estados_finales),
            'transiciones': delta_list
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AFD':
        """
        Deserializa un AFD desde un diccionario.
        """
        afd = cls()
        for estado in data.get('estados', []):
            afd.agregar_estado(estado)
        for simbolo in data.get('alfabeto', []):
            afd.agregar_simbolo(simbolo)
        afd.definir_estado_inicial(data.get('estado_inicial', ''))
        for ef in data.get('estados_finales', []):
            afd.agregar_estado_final(ef)
        for t in data.get('transiciones', []):
            afd.definir_transicion(t['desde'], t['simbolo'], t['hacia'])
        return afd

    def clonar(self) -> 'AFD':
        """
        Retorna una copia profunda del AFD.
        """
        return copy.deepcopy(self)

    def __repr__(self) -> str:
        return (f"AFD(Q={self.estados}, Σ={self.alfabeto}, "
                f"q0='{self.estado_inicial}', F={self.estados_finales})")

    def __eq__(self, other) -> bool:
        """Dos AFDs son iguales si tienen la misma estructura."""
        if not isinstance(other, AFD):
            return False
        return (self.estados == other.estados and
                self.alfabeto == other.alfabeto and
                self.estado_inicial == other.estado_inicial and
                self.estados_finales == other.estados_finales and
                self.delta == other.delta)
