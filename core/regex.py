"""
Módulo de Expresiones Regulares

Contiene:
1. RegexParser — Parser de expresiones regulares con precedencia: * > . > |
2. ThompsonConstruction — Construcción de Thompson: ER → AFN-λ
3. ArdenConversion — AFD → ER por eliminación de estados / lema de Arden

Operadores soportados:
  |  — unión (alternancia)
  .  — concatenación (se puede omitir: ab = a.b)
  *  — clausura de Kleene (cero o más)
  +  — clausura positiva (uno o más)
  ?  — opcional (cero o uno)
  () — agrupación

Precedencia (de mayor a menor): *, +, ? > . > |
"""

from typing import Dict, Set, List, Tuple, Optional, Any
import copy
from collections import deque

from .afn_lambda import AFNLambda, LAMBDA


# ================================================================
# AST (Árbol de Sintaxis Abstracta) para Expresiones Regulares
# ================================================================

class ASTNode:
    """Nodo base del AST de una expresión regular."""
    pass


class SimboloNode(ASTNode):
    """Hoja: un símbolo del alfabeto."""
    def __init__(self, simbolo: str):
        self.simbolo = simbolo

    def __repr__(self):
        return f"Sym({self.simbolo})"


class EpsilonNode(ASTNode):
    """Hoja: ε (cadena vacía)."""
    def __repr__(self):
        return "ε"


class UnionNode(ASTNode):
    """Nodo unión: left | right."""
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Union({self.left}, {self.right})"


class ConcatNode(ASTNode):
    """Nodo concatenación: left . right."""
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Concat({self.left}, {self.right})"


class KleeneNode(ASTNode):
    """Nodo clausura de Kleene: child*."""
    def __init__(self, child: ASTNode):
        self.child = child

    def __repr__(self):
        return f"Kleene({self.child})"


class PlusNode(ASTNode):
    """Nodo clausura positiva: child+."""
    def __init__(self, child: ASTNode):
        self.child = child

    def __repr__(self):
        return f"Plus({self.child})"


class OptionalNode(ASTNode):
    """Nodo opcional: child?."""
    def __init__(self, child: ASTNode):
        self.child = child

    def __repr__(self):
        return f"Optional({self.child})"


# ================================================================
# RegexParser — Parser de Expresiones Regulares
# ================================================================

class RegexParser:
    """
    Parser de expresiones regulares con precedencia: * > . > |
    
    Gramática:
      regex    → union
      union    → concat ('|' concat)*
      concat   → unary (unary)*            (concatenación implícita)
      unary    → primary ('*' | '+' | '?')*
      primary  → '(' regex ')' | simbolo
    
    La concatenación es implícita: ab significa a.b.
    Se insertan operadores '.' implícitamente entre:
      - simbolo seguido de simbolo: ab → a.b
      - simbolo seguido de '(': a(b) → a.(b)
      - ')' seguido de simbolo: (a)b → (a).b
      - ')' seguido de '(': (a)(b) → (a).(b)
      - '*'/'+'/'?' seguido de simbolo o '(': a*b → a*.b
    """

    # Operadores
    OP_UNION = '|'
    OP_CONCAT = '.'
    OP_KLEENE = '*'
    OP_PLUS = '+'
    OP_OPTIONAL = '?'
    OP_LPAREN = '('
    OP_RPAREN = ')'

    def __init__(self):
        self.tokens: List[str] = []
        self.pos: int = 0

    def parse(self, regex: str) -> ASTNode:
        """
        Parsea una expresión regular y retorna su AST.
        
        Args:
            regex: Expresión regular en notación infija.
                   Ej: "(a|b)*abb"
        
        Returns:
            ASTNode: Raíz del AST.
        
        Raises:
            ValueError: Si la expresión es sintácticamente inválida.
        """
        self.tokens = self.tokenize(regex)
        self.pos = 0

        if not self.tokens:
            return EpsilonNode()

        ast = self._parse_union()

        if self.pos < len(self.tokens):
            raise ValueError(
                f"Error de parsing: token inesperado '{self.tokens[self.pos]}' "
                f"en posición {self.pos}"
            )

        return ast

    def tokenize(self, regex: str) -> List[str]:
        """
        Tokeniza la expresión regular, insertando operadores de
        concatenación implícitos ('.') donde corresponda.
        
        Reglas de inserción de '.':
          Si t[i] es operando o ')' o '*' o '+' o '?'
          y t[i+1] es operando o '(',
          entonces insertar '.' entre t[i] y t[i+1].
        """
        # Primero: separar caracteres individuales
        caracteres = list(regex)

        # Filtrar espacios
        caracteres = [c for c in caracteres if c != ' ']

        if not caracteres:
            return []

        # Insertar operadores de concatenación implícitos
        tokens = [caracteres[0]]
        operadores_finales = {self.OP_KLEENE, self.OP_PLUS, self.OP_OPTIONAL, self.OP_RPAREN}
        operandos_iniciales = set()  # Cualquier cosa que no sea operador

        for i in range(1, len(caracteres)):
            anterior = caracteres[i - 1]
            actual = caracteres[i]

            # Insertar '.' si:
            # - El anterior es: operando, ')', '*', '+', '?'
            # - Y el actual es: operando, '('
            necesita_concat = False

            # El anterior cierra una subexpresión (operando, ), *, +, ?)
            ant_cierra = (anterior not in {self.OP_UNION, self.OP_LPAREN, self.OP_CONCAT})
            # El actual abre una subexpresión (operando, ()
            act_abre = (actual not in {self.OP_UNION, self.OP_RPAREN, self.OP_KLEENE,
                                       self.OP_PLUS, self.OP_OPTIONAL, self.OP_CONCAT})

            if ant_cierra and act_abre:
                tokens.append(self.OP_CONCAT)

            tokens.append(actual)

        return tokens

    def _parse_union(self) -> ASTNode:
        """
        union → concat ('|' concat)*
        Operador de menor precedencia.
        """
        left = self._parse_concat()

        while self.pos < len(self.tokens) and self.tokens[self.pos] == self.OP_UNION:
            self.pos += 1  # Consumir '|'
            right = self._parse_concat()
            left = UnionNode(left, right)

        return left

    def _parse_concat(self) -> ASTNode:
        """
        concat → unary (unary)*
        La concatenación se forma por yuxtaposición.
        El token '.' (concatenación explícita) se consume aquí.
        """
        left = self._parse_unary()

        while self.pos < len(self.tokens) and self.tokens[self.pos] not in {
            self.OP_UNION, self.OP_RPAREN
        }:
            # Consumir el operador de concatenación explícito si existe
            if self.tokens[self.pos] == self.OP_CONCAT:
                self.pos += 1  # Consumir '.'
            right = self._parse_unary()
            left = ConcatNode(left, right)

        return left

    def _parse_unary(self) -> ASTNode:
        """
        unary → primary ('*' | '+' | '?')*
        Operadores unarios de mayor precedencia.
        Se aplican de izquierda a derecha (asociatividad izquierda).
        """
        node = self._parse_primary()

        while self.pos < len(self.tokens) and self.tokens[self.pos] in {
            self.OP_KLEENE, self.OP_PLUS, self.OP_OPTIONAL
        }:
            op = self.tokens[self.pos]
            self.pos += 1  # Consumir operador

            if op == self.OP_KLEENE:
                node = KleeneNode(node)
            elif op == self.OP_PLUS:
                node = PlusNode(node)
            elif op == self.OP_OPTIONAL:
                node = OptionalNode(node)

        return node

    def _parse_primary(self) -> ASTNode:
        """
        primary → '(' regex ')' | simbolo
        Caso base: paréntesis o símbolo terminal.
        """
        if self.pos >= len(self.tokens):
            raise ValueError("Error de parsing: expresión incompleta")

        token = self.tokens[self.pos]

        if token == self.OP_LPAREN:
            self.pos += 1  # Consumir '('
            node = self._parse_union()

            if self.pos >= len(self.tokens) or self.tokens[self.pos] != self.OP_RPAREN:
                raise ValueError("Error de parsing: se esperaba ')'")

            self.pos += 1  # Consumir ')'
            return node

        elif token == self.OP_RPAREN:
            raise ValueError(f"Error de parsing: ')' inesperado en posición {self.pos}")

        elif token in {self.OP_UNION, self.OP_KLEENE, self.OP_PLUS, self.OP_OPTIONAL, self.OP_CONCAT}:
            raise ValueError(
                f"Error de parsing: operador '{token}' inesperado en posición {self.pos}"
            )

        else:
            # Es un símbolo del alfabeto
            self.pos += 1
            return SimboloNode(token)


# ================================================================
# ThompsonConstruction — Construcción de Thompson: ER → AFN-λ
# ================================================================

class ThompsonConstruction:
    """
    Construcción de Thompson: ER → AFN-λ
    
    Algoritmo recursivo que construye un AFN-λ a partir del AST
    de una expresión regular. Cada nodo del AST se convierte en
    un sub-AFN-λ con exactamente un estado inicial y un estado final.
    
    Propiedades del AFN-λ de Thompson:
    - No tiene transiciones que no sean ε-transiciones, excepto
      las que salen de estados con transiciones por símbolo
    - Cada sub-AFN-λ tiene exactamente un estado de entrada y uno de salida
    - El número de estados es O(|ER|)
    
    Casos base:
    - ε: q0 --λ--> qf
    - a: q0 --a--> qf
    
    Casos inductivos:
    - R1|R2: nuevo q0 --λ--> q0_R1, q0_R2; qf_R1 --λ--> nuevo qf, qf_R2 --λ--> nuevo qf
    - R1.R2: qf_R1 --λ--> q0_R2
    - R*: nuevo q0 --λ--> q0_R, nuevo qf; qf_R --λ--> q0_R, nuevo qf
    - R+: R.R* (usando clausura_kleene del AFN-λ)
    - R?: nuevo q0 --λ--> q0_R, nuevo qf; qf_R --λ--> nuevo qf
    """

    def __init__(self):
        self._contador = 0  # Contador para nombres únicos de estados

    def _nuevo_estado(self) -> str:
        """Genera un nombre de estado único."""
        self._contador += 1
        return f'q{self._contador}'

    def thompson(self, ast: ASTNode, alphabet: Set[str]) -> AFNLambda:
        """
        Construye el AFN-λ de Thompson a partir del AST.
        
        Args:
            ast: AST de la expresión regular.
            alphabet: Alfabeto de entrada.
        
        Returns:
            AFNLambda con el lenguaje de la expresión regular.
        """
        self._contador = 0
        afn_lambda = self._build(ast, alphabet)
        afn_lambda.alfabeto = set(alphabet)
        return afn_lambda

    def _build(self, node: ASTNode, alphabet: Set[str]) -> AFNLambda:
        """Construcción recursiva del AFN-λ de Thompson."""

        if isinstance(node, EpsilonNode):
            return self._build_epsilon()

        elif isinstance(node, SimboloNode):
            return self._build_symbol(node.simbolo)

        elif isinstance(node, UnionNode):
            return self._build_union(
                self._build(node.left, alphabet),
                self._build(node.right, alphabet)
            )

        elif isinstance(node, ConcatNode):
            return self._build_concat(
                self._build(node.left, alphabet),
                self._build(node.right, alphabet)
            )

        elif isinstance(node, KleeneNode):
            return self._build_kleene(self._build(node.child, alphabet))

        elif isinstance(node, PlusNode):
            return self._build_plus(self._build(node.child, alphabet))

        elif isinstance(node, OptionalNode):
            return self._build_optional(self._build(node.child, alphabet))

        else:
            raise ValueError(f"Tipo de nodo AST desconocido: {type(node)}")

    def _build_epsilon(self) -> AFNLambda:
        """
        Caso base ε: q0 --λ--> qf
        Acepta la cadena vacía.
        """
        afn = AFNLambda()
        q0 = self._nuevo_estado()
        qf = self._nuevo_estado()
        afn.definir_estado_inicial(q0)
        afn.agregar_estado_final(qf)
        afn.agregar_transicion_lambda(q0, qf)
        return afn

    def _build_symbol(self, simbolo: str) -> AFNLambda:
        """
        Caso base a: q0 --a--> qf
        Acepta la cadena "a".
        """
        afn = AFNLambda()
        afn.agregar_simbolo(simbolo)
        q0 = self._nuevo_estado()
        qf = self._nuevo_estado()
        afn.definir_estado_inicial(q0)
        afn.agregar_estado_final(qf)
        afn.definir_transicion(q0, simbolo, qf)
        return afn

    def _build_union(self, afn1: AFNLambda, afn2: AFNLambda) -> AFNLambda:
        """
        Unión R1|R2:
          q0 --λ--> q0_R1 ... qf_R1 --λ--> qf
          q0 --λ--> q0_R2 ... qf_R2 --λ--> qf
        
        Acepta L(R1) ∪ L(R2).
        """
        resultado = AFNLambda()

        # Nuevo estado inicial
        q0 = self._nuevo_estado()
        qf = self._nuevo_estado()
        resultado.definir_estado_inicial(q0)
        resultado.agregar_estado_final(qf)

        # Copiar estados y transiciones de afn1
        for estado in afn1.estados:
            resultado.agregar_estado(estado)
        for estado in afn1.delta:
            for simbolo in afn1.delta[estado]:
                for destino in afn1.delta[estado][simbolo]:
                    resultado.definir_transicion(estado, simbolo, destino)

        # Copiar estados y transiciones de afn2
        for estado in afn2.estados:
            resultado.agregar_estado(estado)
        for estado in afn2.delta:
            for simbolo in afn2.delta[estado]:
                for destino in afn2.delta[estado][simbolo]:
                    resultado.definir_transicion(estado, simbolo, destino)

        # ε-transiciones desde q0 a los estados iniciales de ambos
        resultado.agregar_transicion_lambda(q0, afn1.estado_inicial)
        resultado.agregar_transicion_lambda(q0, afn2.estado_inicial)

        # ε-transiciones desde los estados finales de ambos a qf
        for ef in afn1.estados_finales:
            resultado.agregar_transicion_lambda(ef, qf)
        for ef in afn2.estados_finales:
            resultado.agregar_transicion_lambda(ef, qf)

        return resultado

    def _build_concat(self, afn1: AFNLambda, afn2: AFNLambda) -> AFNLambda:
        """
        Concatenación R1.R2:
          q0_R1 ... qf_R1 --λ--> q0_R2 ... qf_R2
        
        Acepta L(R1) · L(R2).
        Los estados finales de R1 se conectan con ε-transiciones
        al estado inicial de R2.
        """
        resultado = AFNLambda()

        # Copiar estados y transiciones de afn1
        for estado in afn1.estados:
            resultado.agregar_estado(estado)
        for estado in afn1.delta:
            for simbolo in afn1.delta[estado]:
                for destino in afn1.delta[estado][simbolo]:
                    resultado.definir_transicion(estado, simbolo, destino)

        # Copiar estados y transiciones de afn2
        for estado in afn2.estados:
            resultado.agregar_estado(estado)
        for estado in afn2.delta:
            for simbolo in afn2.delta[estado]:
                for destino in afn2.delta[estado][simbolo]:
                    resultado.definir_transicion(estado, simbolo, destino)

        # Estado inicial es el de R1
        resultado.definir_estado_inicial(afn1.estado_inicial)

        # ε-transiciones de los finales de R1 al inicial de R2
        for ef in afn1.estados_finales:
            resultado.agregar_transicion_lambda(ef, afn2.estado_inicial)

        # Estados finales son los de R2
        for ef in afn2.estados_finales:
            resultado.agregar_estado_final(ef)

        return resultado

    def _build_kleene(self, afn: AFNLambda) -> AFNLambda:
        """
        Clausura de Kleene R*:
          q0 --λ--> q0_R ... qf_R --λ--> qf
          q0 --λ--> qf           (λ ∈ L(R*))
          qf_R --λ--> q0_R      (iteración)
        
        Acepta L(R)* = ∪{L(R)^n : n ≥ 0}.
        """
        resultado = AFNLambda()

        # Nuevo estado inicial (también es estado de entrada)
        q0 = self._nuevo_estado()
        qf = self._nuevo_estado()
        resultado.definir_estado_inicial(q0)
        resultado.agregar_estado_final(qf)

        # Copiar estados y transiciones del AFN original
        for estado in afn.estados:
            resultado.agregar_estado(estado)
        for estado in afn.delta:
            for simbolo in afn.delta[estado]:
                for destino in afn.delta[estado][simbolo]:
                    resultado.definir_transicion(estado, simbolo, destino)

        # ε-transición: q0 → q0_R (entrar al sub-AFN)
        resultado.agregar_transicion_lambda(q0, afn.estado_inicial)

        # ε-transición: q0 → qf (λ ∈ L(R*))
        resultado.agregar_transicion_lambda(q0, qf)

        # ε-transiciones: qf_R → q0_R (iteración: volver a procesar R)
        for ef in afn.estados_finales:
            resultado.agregar_transicion_lambda(ef, afn.estado_inicial)

        # ε-transiciones: qf_R → qf (salir después de procesar R)
        for ef in afn.estados_finales:
            resultado.agregar_transicion_lambda(ef, qf)

        return resultado

    def _build_plus(self, afn: AFNLambda) -> AFNLambda:
        """
        Clausura positiva R+ = R · R*:
        
        Misma construcción que Kleene pero SIN la transición
        q0 → qf (λ ∉ L(R+) salvo que λ ∈ L(R)).
        
          q0 --λ--> q0_R ... qf_R --λ--> qf
          qf_R --λ--> q0_R      (iteración)
        """
        resultado = AFNLambda()

        q0 = self._nuevo_estado()
        qf = self._nuevo_estado()
        resultado.definir_estado_inicial(q0)
        resultado.agregar_estado_final(qf)

        # Copiar estados y transiciones del AFN original
        for estado in afn.estados:
            resultado.agregar_estado(estado)
        for estado in afn.delta:
            for simbolo in afn.delta[estado]:
                for destino in afn.delta[estado][simbolo]:
                    resultado.definir_transicion(estado, simbolo, destino)

        # ε-transición: q0 → q0_R (entrar al sub-AFN)
        resultado.agregar_transicion_lambda(q0, afn.estado_inicial)

        # ε-transiciones: qf_R → q0_R (iteración)
        for ef in afn.estados_finales:
            resultado.agregar_transicion_lambda(ef, afn.estado_inicial)

        # ε-transiciones: qf_R → qf (salir)
        for ef in afn.estados_finales:
            resultado.agregar_transicion_lambda(ef, qf)

        return resultado

    def _build_optional(self, afn: AFNLambda) -> AFNLambda:
        """
        Opcional R? = R | ε:
        
          q0 --λ--> q0_R ... qf_R --λ--> qf
          q0 --λ--> qf           (λ ∈ L(R?))
        
        Acepta L(R) ∪ {λ}.
        """
        resultado = AFNLambda()

        q0 = self._nuevo_estado()
        qf = self._nuevo_estado()
        resultado.definir_estado_inicial(q0)
        resultado.agregar_estado_final(qf)

        # Copiar estados y transiciones del AFN original
        for estado in afn.estados:
            resultado.agregar_estado(estado)
        for estado in afn.delta:
            for simbolo in afn.delta[estado]:
                for destino in afn.delta[estado][simbolo]:
                    resultado.definir_transicion(estado, simbolo, destino)

        # ε-transición: q0 → q0_R (entrar al sub-AFN)
        resultado.agregar_transicion_lambda(q0, afn.estado_inicial)

        # ε-transición: q0 → qf (opción de no tomar R)
        resultado.agregar_transicion_lambda(q0, qf)

        # ε-transiciones: qf_R → qf
        for ef in afn.estados_finales:
            resultado.agregar_transicion_lambda(ef, qf)

        return resultado


# ================================================================
# ArdenConversion — AFD → ER por Lema de Arden
# ================================================================

class ArdenConversion:
    """
    Conversión AFD → ER por eliminación de estados usando el Lema de Arden.
    
    Lema de Arden:
      Si X = A·X ∪ B y ε ∉ A, entonces X = A*·B
    
    Algoritmo:
    1. Para cada estado qi, establecer la ecuación:
       X_i = ∪{a_j · X_j : δ(qi, a_j) = qj} ∪ {ε si qi ∈ F}
    2. Eliminar estados uno por uno, sustituyendo sus ecuaciones
       en las demás (usando el Lema de Arden)
    3. La ER final es el valor de X_{q0} después de todas las sustituciones
    """

    def afd_to_regex(self, afd) -> dict:
        """
        Convierte un AFD en una expresión regular.
        
        Args:
            afd: Instancia de AFD.
        
        Returns:
            {
              'regex': str — expresión regular equivalente,
              'pasos': list — pasos de la eliminación de estados
            }
        """
        from .afd import AFD

        pasos = []

        # Caso especial: lenguaje vacío
        if afd.es_lenguaje_vacio():
            pasos.append({
                'descripcion': 'El lenguaje es vacío. La ER es ∅.',
                'ecuaciones': {},
                'estado_eliminado': None
            })
            return {'regex': '∅', 'pasos': pasos}

        # Paso 1: Construir sistema de ecuaciones
        # Para cada estado qi:
        # X_i = a1·X_j1 ∪ a2·X_j2 ∪ ... ∪ {ε si qi ∈ F}
        #
        # Representación: ecuaciones[qi] = {
        #   'coeficientes': {qj: [a1, a2, ...]},  # términos a·X_j
        #   'constante': bool                       # ε (si qi ∈ F)
        # }
        estados = sorted(afd.estados)
        ecuaciones: Dict[str, Dict] = {}

        for qi in estados:
            ecuaciones[qi] = {'coeficientes': {}, 'constante': False}

            # Términos de transición: a·X_j donde δ(qi, a) = qj
            for simbolo in sorted(afd.alfabeto):
                qj = afd.delta.get(qi, {}).get(simbolo)
                if qj is not None:
                    if qj not in ecuaciones[qi]['coeficientes']:
                        ecuaciones[qi]['coeficientes'][qj] = []
                    ecuaciones[qi]['coeficientes'][qj].append(simbolo)

            # Constante ε si qi es estado final
            if qi in afd.estados_finales:
                ecuaciones[qi]['constante'] = True

        # Guardar ecuaciones iniciales
        pasos.append({
            'descripcion': 'Paso 1: Sistema de ecuaciones inicial (Ecuaciones de Arden)',
            'ecuaciones': self._serializar_ecuaciones(ecuaciones),
            'estado_eliminado': None
        })

        # Paso 2: Eliminar estados (excepto q0)
        # Orden: eliminar estados que no son el inicial
        estados_a_eliminar = [q for q in estados if q != afd.estado_inicial]

        for qi in estados_a_eliminar:
            # Obtener la ecuación de qi: X_i = A·X_i ∪ B
            # donde A = unión de coeficientes de X_i en su propia ecuación
            # B = resto de la ecuación

            eq_i = ecuaciones[qi]
            A = eq_i['coeficientes'].get(qi, [])  # Coeficientes de X_i en su ecuación (bucle)
            B_terminos = {}  # Otros términos
            for qj, coef in eq_i['coeficientes'].items():
                if qj != qi:
                    B_terminos[qj] = coef
            # B_constante: True si qi es estado final, O si tiene caminos a aceptación
            # acumulados en iteraciones previas via constante_extra
            B_constante = eq_i['constante']
            extras = eq_i.get('constante_extra', [])
            # extras son expresiones de la forma C·A* que ya son caminos a aceptación;
            # se tratan como términos constantes adicionales en B
            if extras:
                B_constante_exprs = extras  # expresiones concretas
            else:
                B_constante_exprs = []

            # Por el Lema de Arden: X_i = A*·B
            # Sustituir X_i en todas las demás ecuaciones
            for qk in ecuaciones:
                if qk == qi:
                    continue

                # Buscar coeficientes de X_i en la ecuación de qk
                C = ecuaciones[qk]['coeficientes'].get(qi, [])
                if not C:
                    continue

                # Sustituir: C·X_i = C·A*·B
                # Nuevo término: para cada qj en B_terminos, agregar C·A*·(B_qj)
                # Nuevo constante: C·A*·B_constante

                # Construir la expresión A*
                A_expr = self._combinar_alternativas(A)
                if A_expr:
                    A_star = f'({A_expr})*'
                else:
                    A_star = ''  # No hay bucle propio

                # Para cada término en B
                for qj, B_coef in B_terminos.items():
                    B_expr = self._combinar_alternativas(B_coef)
                    C_expr = self._combinar_alternativas(C)

                    # Nuevo coeficiente: C · A* · B_coef
                    nuevo_coef = self._concat_expr(C_expr, A_star, B_expr)

                    if qj not in ecuaciones[qk]['coeficientes']:
                        ecuaciones[qk]['coeficientes'][qj] = []
                    ecuaciones[qk]['coeficientes'][qj].append(nuevo_coef)

                # Si B tiene constante (ε simple) o expresiones constantes
                # acumuladas (B_constante_exprs), propagar como constante en qk.
                C_expr = self._combinar_alternativas(C)
                if B_constante:
                    # C · A* · ε = C · A*  → camino de qk a aceptación
                    nuevo_termino = self._concat_expr(C_expr, A_star)
                    if 'constante_extra' not in ecuaciones[qk]:
                        ecuaciones[qk]['constante_extra'] = []
                    ecuaciones[qk]['constante_extra'].append(nuevo_termino)
                for b_extra in B_constante_exprs:
                    # C · A* · b_extra → camino de qk a aceptación
                    nuevo_termino = self._concat_expr(C_expr, A_star, b_extra)
                    if 'constante_extra' not in ecuaciones[qk]:
                        ecuaciones[qk]['constante_extra'] = []
                    ecuaciones[qk]['constante_extra'].append(nuevo_termino)

                # Eliminar X_i de la ecuación de qk
                del ecuaciones[qk]['coeficientes'][qi]

            # Eliminar la ecuación de qi
            del ecuaciones[qi]

            pasos.append({
                'descripcion': f'Eliminar estado {qi} usando Lema de Arden: X_{qi} = {self._combinar_alternativas(A)}*·B',
                'ecuaciones': self._serializar_ecuaciones(ecuaciones),
                'estado_eliminado': qi
            })

        # Paso 3: La ecuación restante es X_{q0}
        # X_{q0} = A·X_{q0} ∪ B
        # Por Arden: X_{q0} = A*·B
        q0 = afd.estado_inicial
        if q0 not in ecuaciones:
            # No debería pasar, pero por seguridad
            return {'regex': '∅', 'pasos': pasos}

        eq_q0 = ecuaciones[q0]
        A = eq_q0['coeficientes'].get(q0, [])
        B_constante = eq_q0['constante']

        # Construir B (términos que no son X_{q0})
        B_partes = []
        for qj, coef in eq_q0['coeficientes'].items():
            if qj != q0:
                B_partes.extend(coef)

        if B_constante:
            B_partes.append('ε')

        # Incluir caminos a aceptación acumulados desde eliminaciones previas
        for expr in eq_q0.get('constante_extra', []):
            B_partes.append(expr)

        A_expr = self._combinar_alternativas(A)
        B_expr = self._combinar_alternativas(B_partes)

        # Aplicar Arden: X = A*·B
        if A_expr and B_expr:
            regex = f'({A_expr})*({B_expr})'
        elif A_expr:
            # Solo bucle propio sin camino a aceptación: lenguaje vacío
            # (q0 no es estado final y no hay ningún camino a un estado final)
            regex = '∅'
        elif B_expr:
            # No hay bucle propio
            regex = B_expr
        else:
            regex = '∅'

        # Simplificaciones básicas
        regex = self._simplificar_regex(regex)

        pasos.append({
            'descripcion': f'Aplicar Lema de Arden: X_{q0} = A*·B = {regex}',
            'ecuaciones': {},
            'estado_eliminado': q0,
            'regex_final': regex
        })

        return {'regex': regex, 'pasos': pasos}

    def _combinar_alternativas(self, terminos: List[str]) -> str:
        """
        Combina una lista de términos con el operador '|'.
        Si hay un solo término, lo retorna sin '|'.
        """
        if not terminos:
            return ''
        terminos_filtrados = [t for t in terminos if t]
        if not terminos_filtrados:
            return ''
        if len(terminos_filtrados) == 1:
            return terminos_filtrados[0]
        return '(' + '|'.join(terminos_filtrados) + ')'

    def _concat_expr(self, *partes: str) -> str:
        """
        Concatena expresiones, omitiendo partes vacías.
        """
        resultado = ''
        for p in partes:
            if p:
                resultado += p
        return resultado

    def _simplificar_regex(self, regex: str) -> str:
        """
        Aplica simplificaciones básicas a la expresión regular.
        """
        # Remover paréntesis innecesarios alrededor de toda la expresión
        while regex.startswith('(') and regex.endswith(')'):
            # Verificar si los paréntesis están balanceados correctamente
            nivel = 0
            balanceado = True
            for i, c in enumerate(regex):
                if c == '(':
                    nivel += 1
                elif c == ')':
                    nivel -= 1
                if nivel == 0 and i < len(regex) - 1:
                    balanceado = False
                    break
            if balanceado:
                regex = regex[1:-1]
            else:
                break

        # Simplificaciones adicionales
        # ε·X → X
        regex = regex.replace('ε(', '(')
        # ()* → ε (paréntesis vacío con Kleene)
        regex = regex.replace('()*', '')

        return regex

    def _serializar_ecuaciones(self, ecuaciones: Dict) -> Dict:
        """Serializa las ecuaciones para visualización."""
        resultado = {}
        for qi, eq in ecuaciones.items():
            terminos = []
            for qj, coef in eq['coeficientes'].items():
                for c in coef:
                    terminos.append(f'{c}·X_{qj}')
            if eq['constante']:
                terminos.append('ε')
            resultado[f'X_{qi}'] = ' ∪ '.join(terminos) if terminos else '∅'
        return resultado


# ================================================================
# Funciones de conveniencia
# ================================================================

def regex_to_afn_lambda(regex: str, alphabet: Set[str] = None) -> AFNLambda:
    """
    Convierte una expresión regular en un AFN-λ usando la
    construcción de Thompson.
    
    Args:
        regex: Expresión regular en notación infija.
        alphabet: Alfabeto (opcional, se infiere si no se proporciona).
    
    Returns:
        AFNLambda que acepta el lenguaje de la expresión regular.
    """
    # Inferir alfabeto si no se proporciona
    if alphabet is None:
        alphabet = infer_alphabet(regex)

    # Parsear la expresión regular
    parser = RegexParser()
    ast = parser.parse(regex)

    # Construir AFN-λ con Thompson
    constructor = ThompsonConstruction()
    return constructor.thompson(ast, alphabet)


def afd_to_regex(afd) -> dict:
    """
    Convierte un AFD en una expresión regular usando el
    Lema de Arden (eliminación de estados).
    
    Args:
        afd: Instancia de AFD.
    
    Returns:
        {'regex': str, 'pasos': list}
    """
    converter = ArdenConversion()
    return converter.afd_to_regex(afd)


def infer_alphabet(regex: str) -> Set[str]:
    """
    Infiere el alfabeto a partir de una expresión regular,
    extrayendo todos los símbolos que no son operadores.
    
    Operadores: | . * + ? ( )
    """
    operadores = {'|', '.', '*', '+', '?', '(', ')', ' '}
    alfabeto = set()
    for c in regex:
        if c not in operadores:
            alfabeto.add(c)
    return alfabeto
