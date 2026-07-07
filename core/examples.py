"""
Módulo de Ejemplos Pre-cargados

Contiene 7 ejemplos de autómatas para práctica y demostración:
1. afd_termina_en_1() — Cadenas binarias que terminan en 1
2. afd_par_de_ceros() — Cadenas con número par de ceros
3. afd_a_or_b_star_abb() — Lenguaje (a|b)*abb
4. afn_contiene_01() — Cadenas que contienen "01"
5. afn_lambda_a_star_b_plus() — Lenguaje a*b+ (con ε-transiciones)
6. afd_no_minimo() — AFD no mínimo para práctica de minimización
7. afds_equivalentes() — Par de AFDs equivalentes
"""

from typing import Dict, List, Tuple, Any

from .afd import AFD
from .afn import AFN
from .afn_lambda import AFNLambda


def afd_termina_en_1() -> AFD:
    """
    AFD que acepta cadenas binarias que terminan en 1.
    
    Lenguaje: L = {w ∈ {0,1}* : w termina con 1}
    
    Estados:
      q0 — estado inicial (último dígito leído fue 0, o no se ha leído nada)
      q1 — estado final (último dígito leído fue 1)
    
    Transiciones:
      δ(q0, 0) = q0  — leer 0 mantiene en q0
      δ(q0, 1) = q1  — leer 1 cambia a q1
      δ(q1, 0) = q0  — leer 0 cambia a q0
      δ(q1, 1) = q1  — leer 1 mantiene en q1
    """
    afd = AFD()
    
    # Estados
    afd.agregar_estado('q0')
    afd.agregar_estado('q1')
    
    # Alfabeto
    afd.agregar_simbolo('0')
    afd.agregar_simbolo('1')
    
    # Estado inicial
    afd.definir_estado_inicial('q0')
    
    # Estado final
    afd.agregar_estado_final('q1')
    
    # Transiciones
    afd.definir_transicion('q0', '0', 'q0')
    afd.definir_transicion('q0', '1', 'q1')
    afd.definir_transicion('q1', '0', 'q0')
    afd.definir_transicion('q1', '1', 'q1')
    
    return afd


def afd_par_de_ceros() -> AFD:
    """
    AFD que acepta cadenas con un número par de ceros.
    
    Lenguaje: L = {w ∈ {0,1}* : |w|₀ es par}
    
    Estados:
      q_par — estado inicial/final (número par de ceros leídos)
      q_impar — estado no final (número impar de ceros leídos)
    
    Transiciones:
      δ(q_par, 0) = q_impar   — leer 0 cambia paridad
      δ(q_par, 1) = q_par     — leer 1 no afecta paridad
      δ(q_impar, 0) = q_par   — leer 0 cambia paridad
      δ(q_impar, 1) = q_impar — leer 1 no afecta paridad
    """
    afd = AFD()
    
    # Estados
    afd.agregar_estado('q_par')
    afd.agregar_estado('q_impar')
    
    # Alfabeto
    afd.agregar_simbolo('0')
    afd.agregar_simbolo('1')
    
    # Estado inicial
    afd.definir_estado_inicial('q_par')
    
    # Estado final (0 ceros = par)
    afd.agregar_estado_final('q_par')
    
    # Transiciones
    afd.definir_transicion('q_par', '0', 'q_impar')
    afd.definir_transicion('q_par', '1', 'q_par')
    afd.definir_transicion('q_impar', '0', 'q_par')
    afd.definir_transicion('q_impar', '1', 'q_impar')
    
    return afd


def afd_a_or_b_star_abb() -> AFD:
    """
    AFD que acepta el lenguaje (a|b)*abb.
    
    Lenguaje: L = {w ∈ {a,b}* : w termina con "abb"}
    
    Estados:
      q0 — estado inicial (no se ha comenzado a formar "abb")
      q1 — se ha leído 'a' (posible inicio de "abb")
      q2 — se ha leído 'ab' (dos caracteres de "abb")
      q3 — estado final (se ha leído "abb")
    
    Transiciones:
      δ(q0, a) = q1  — 'a' podría iniciar "abb"
      δ(q0, b) = q0  — 'b' no inicia "abb"
      δ(q1, a) = q1  — otro 'a' reinicia el patrón
      δ(q1, b) = q2  — 'ab' — segundo carácter del patrón
      δ(q2, a) = q1  — 'a' reinicia desde este punto
      δ(q2, b) = q3  — "abb" completo
      δ(q3, a) = q1  — 'a' podría iniciar nuevo "abb"
      δ(q3, b) = q0  — 'b' no puede iniciar "abb"
    """
    afd = AFD()
    
    # Estados
    afd.agregar_estado('q0')
    afd.agregar_estado('q1')
    afd.agregar_estado('q2')
    afd.agregar_estado('q3')
    
    # Alfabeto
    afd.agregar_simbolo('a')
    afd.agregar_simbolo('b')
    
    # Estado inicial
    afd.definir_estado_inicial('q0')
    
    # Estado final
    afd.agregar_estado_final('q3')
    
    # Transiciones
    afd.definir_transicion('q0', 'a', 'q1')
    afd.definir_transicion('q0', 'b', 'q0')
    afd.definir_transicion('q1', 'a', 'q1')
    afd.definir_transicion('q1', 'b', 'q2')
    afd.definir_transicion('q2', 'a', 'q1')
    afd.definir_transicion('q2', 'b', 'q3')
    afd.definir_transicion('q3', 'a', 'q1')
    afd.definir_transicion('q3', 'b', 'q0')
    
    return afd


def afn_contiene_01() -> AFN:
    """
    AFN que acepta cadenas sobre {0,1} que contienen "01" como subcadena.
    
    Lenguaje: L = {w ∈ {0,1}* : "01" es subcadena de w}
    
    El AFN "adivina" dónde comienza el patrón "01" usando
    no determinismo.
    
    Estados:
      q0 — estado inicial (no se ha visto nada del patrón)
      q1 — se ha visto '0' (posible inicio de "01")
      q2 — estado final (se ha visto "01")
    
    Transiciones:
      δ(q0, 0) = {q0, q1}  — no determinismo: queda o avanza
      δ(q0, 1) = {q0}       — sigue esperando
      δ(q1, 1) = {q2}       — completa "01"
      δ(q2, 0) = {q2}       — ya aceptó, queda en final
      δ(q2, 1) = {q2}       — ya aceptó, queda en final
    """
    afn = AFN()
    
    # Estados
    afn.agregar_estado('q0')
    afn.agregar_estado('q1')
    afn.agregar_estado('q2')
    
    # Alfabeto
    afn.agregar_simbolo('0')
    afn.agregar_simbolo('1')
    
    # Estado inicial
    afn.definir_estado_inicial('q0')
    
    # Estado final
    afn.agregar_estado_final('q2')
    
    # Transiciones
    afn.definir_transicion('q0', '0', 'q0')
    afn.definir_transicion('q0', '0', 'q1')  # No determinismo
    afn.definir_transicion('q0', '1', 'q0')
    afn.definir_transicion('q1', '1', 'q2')
    afn.definir_transicion('q2', '0', 'q2')
    afn.definir_transicion('q2', '1', 'q2')
    
    return afn


def afn_lambda_a_star_b_plus() -> AFNLambda:
    """
    AFN-λ que acepta el lenguaje a*b+ (cero o más 'a' seguidas de una o más 'b').
    
    Lenguaje: L = {a^n b^m : n ≥ 0, m ≥ 1}
    
    Usa ε-transiciones para separar las dos partes del lenguaje.
    
    Estados:
      q0 — estado inicial (parte a*)
      q1 — transición (parte b+)
      q2 — estado final (después de leer al menos una 'b')
    
    Transiciones:
      δ(q0, a) = {q0}      — leer 'a' permanece en q0
      δ(q0, λ) = {q1}      — ε-transición a la parte b+
      δ(q1, b) = {q1, q2}  — leer 'b': puede seguir o aceptar
      δ(q2, b) = {q1, q2}  — leer más 'b's
    """
    afn_lambda = AFNLambda()
    
    # Estados
    afn_lambda.agregar_estado('q0')
    afn_lambda.agregar_estado('q1')
    afn_lambda.agregar_estado('q2')
    
    # Alfabeto
    afn_lambda.agregar_simbolo('a')
    afn_lambda.agregar_simbolo('b')
    
    # Estado inicial
    afn_lambda.definir_estado_inicial('q0')
    
    # Estado final
    afn_lambda.agregar_estado_final('q2')
    
    # Transiciones
    afn_lambda.definir_transicion('q0', 'a', 'q0')
    afn_lambda.agregar_transicion_lambda('q0', 'q1')  # ε-transición
    afn_lambda.definir_transicion('q1', 'b', 'q1')
    afn_lambda.definir_transicion('q1', 'b', 'q2')    # Primera 'b' → puede aceptar
    afn_lambda.definir_transicion('q2', 'b', 'q2')    # Más 'b's
    
    return afn_lambda


def afd_no_minimo() -> AFD:
    """
    AFD no mínimo que acepta cadenas binarias que terminan en "1".
    
    Este AFD tiene estados redundantes que pueden eliminarse
    mediante minimización. Es el mismo lenguaje que afd_termina_en_1()
    pero con estados adicionales que son equivalentes.
    
    Estados:
      q0 — estado inicial
      q1 — vio un '1'
      q2 — equivalente a q1 (redundante)
      q3 — vio un '0' después de '1'
    
    La minimización debería fusionar q1 y q2 (ambos son finales
    y tienen el mismo comportamiento).
    """
    afd = AFD()
    
    # Estados
    afd.agregar_estado('q0')
    afd.agregar_estado('q1')
    afd.agregar_estado('q2')  # Redundante con q1
    afd.agregar_estado('q3')
    
    # Alfabeto
    afd.agregar_simbolo('0')
    afd.agregar_simbolo('1')
    
    # Estado inicial
    afd.definir_estado_inicial('q0')
    
    # Estados finales
    afd.agregar_estado_final('q1')
    afd.agregar_estado_final('q2')  # q1 y q2 son equivalentes
    
    # Transiciones
    afd.definir_transicion('q0', '0', 'q0')
    afd.definir_transicion('q0', '1', 'q1')
    afd.definir_transicion('q1', '0', 'q3')
    afd.definir_transicion('q1', '1', 'q2')
    afd.definir_transicion('q2', '0', 'q3')  # Igual que q1
    afd.definir_transicion('q2', '1', 'q2')  # Igual que q1 (va a q2 en vez de q1, pero son equivalentes)
    afd.definir_transicion('q3', '0', 'q0')
    afd.definir_transicion('q3', '1', 'q1')
    
    return afd


def afds_equivalentes() -> Tuple[AFD, AFD]:
    """
    Retorna un par de AFDs que son equivalentes (aceptan el mismo lenguaje)
    pero tienen diferente número de estados.
    
    Ambos aceptan el lenguaje: cadenas sobre {0,1} con número impar de 1s.
    
    AFD1: Versión directa con 2 estados.
    AFD2: Versión con estado redundante (3 estados, minimizable a 2).
    """
    # AFD1: Versión mínima — número impar de 1s
    afd1 = AFD()
    afd1.agregar_estado('A')
    afd1.agregar_estado('B')
    afd1.agregar_simbolo('0')
    afd1.agregar_simbolo('1')
    afd1.definir_estado_inicial('A')
    afd1.agregar_estado_final('B')  # Impar de 1s
    afd1.definir_transicion('A', '0', 'A')
    afd1.definir_transicion('A', '1', 'B')
    afd1.definir_transicion('B', '0', 'B')
    afd1.definir_transicion('B', '1', 'A')
    
    # AFD2: Versión con estado redundante
    # También acepta cadenas con número impar de 1s, pero con 3 estados
    # p1 y p2 son equivalentes: ambos representan "número impar de 1s"
    # y ambos van a "par" (p0) al leer 1, y se intercambian al leer 0
    afd2 = AFD()
    afd2.agregar_estado('p0')
    afd2.agregar_estado('p1')
    afd2.agregar_estado('p2')  # Redundante con p1
    afd2.agregar_simbolo('0')
    afd2.agregar_simbolo('1')
    afd2.definir_estado_inicial('p0')
    afd2.agregar_estado_final('p1')
    afd2.agregar_estado_final('p2')  # p1 y p2 son equivalentes
    afd2.definir_transicion('p0', '0', 'p0')
    afd2.definir_transicion('p0', '1', 'p1')
    afd2.definir_transicion('p1', '0', 'p2')  # impar + 0 → impar (va a p2)
    afd2.definir_transicion('p1', '1', 'p0')  # impar + 1 → par
    afd2.definir_transicion('p2', '0', 'p1')  # impar + 0 → impar (va a p1)
    afd2.definir_transicion('p2', '1', 'p0')  # impar + 1 → par
    
    return afd1, afd2


# ================================================================
# Registro de todos los ejemplos
# ================================================================

ALL_EXAMPLES: List[Dict[str, Any]] = [
    {
        'nombre': 'AFD: Termina en 1',
        'descripcion': 'Cadenas binarias que terminan en 1. L = {w ∈ {0,1}* : w termina con 1}',
        'tipo': 'AFD',
        'funcion': afd_termina_en_1
    },
    {
        'nombre': 'AFD: Par de ceros',
        'descripcion': 'Cadenas binarias con número par de ceros. L = {w ∈ {0,1}* : |w|₀ es par}',
        'tipo': 'AFD',
        'funcion': afd_par_de_ceros
    },
    {
        'nombre': 'AFD: (a|b)*abb',
        'descripcion': 'Cadenas sobre {a,b} que terminan con "abb". L = (a|b)*abb',
        'tipo': 'AFD',
        'funcion': afd_a_or_b_star_abb
    },
    {
        'nombre': 'AFN: Contiene 01',
        'descripcion': 'Cadenas binarias que contienen "01" como subcadena. L = {w : "01" ⊑ w}',
        'tipo': 'AFN',
        'funcion': afn_contiene_01
    },
    {
        'nombre': 'AFN-λ: a*b+',
        'descripcion': 'Cero o más "a" seguidas de una o más "b". L = {a^n b^m : n ≥ 0, m ≥ 1}',
        'tipo': 'AFNLambda',
        'funcion': afn_lambda_a_star_b_plus
    },
    {
        'nombre': 'AFD: No mínimo',
        'descripcion': 'AFD no mínimo para práctica de minimización. Acepta cadenas que terminan en 1.',
        'tipo': 'AFD',
        'funcion': afd_no_minimo
    },
    {
        'nombre': 'AFDs: Equivalentes',
        'descripcion': 'Par de AFDs equivalentes que aceptan cadenas con número impar de 1s.',
        'tipo': 'AFD_par',
        'funcion': afds_equivalentes
    }
]
