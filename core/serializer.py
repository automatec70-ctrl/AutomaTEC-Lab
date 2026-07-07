"""
Módulo de Serialización

Funciones para serializar, deserializar y exportar autómatas
en diferentes formatos:
  - JSON (diccionario) usando to_dict/from_dict
  - CSV (tabla de transiciones)
  - Descripción formal (notación matemática)
"""

import json
from typing import Dict, Set, List, Optional

from .afd import AFD
from .afn import AFN
from .afn_lambda import AFNLambda, LAMBDA


# ================================================================
# Serialización / Deserialización JSON
# ================================================================

def serializar_afd(afd: AFD) -> dict:
    """
    Serializa un AFD a un diccionario listo para JSON.
    """
    return afd.to_dict()


def deserializar_afd(data: dict) -> AFD:
    """
    Deserializa un AFD desde un diccionario.
    """
    return AFD.from_dict(data)


def serializar_afn(afn: AFN) -> dict:
    """
    Serializa un AFN a un diccionario listo para JSON.
    """
    return afn.to_dict()


def deserializar_afn(data: dict) -> AFN:
    """
    Deserializa un AFN desde un diccionario.
    """
    return AFN.from_dict(data)


def serializar_afn_lambda(afn_lambda: AFNLambda) -> dict:
    """
    Serializa un AFN-λ a un diccionario listo para JSON.
    """
    return afn_lambda.to_dict()


def deserializar_afn_lambda(data: dict) -> AFNLambda:
    """
    Deserializa un AFN-λ desde un diccionario.
    """
    return AFNLambda.from_dict(data)


def serializar_generico(automata) -> dict:
    """
    Serializa cualquier tipo de autómata, detectando su tipo automáticamente.
    """
    if isinstance(automata, AFNLambda):
        return serializar_afn_lambda(automata)
    elif isinstance(automata, AFN):
        return serializar_afn(automata)
    elif isinstance(automata, AFD):
        return serializar_afd(automata)
    else:
        raise TypeError(f"Tipo de autómata no soportado: {type(automata)}")


def deserializar_generico(data: dict):
    """
    Deserializa un autómata desde un diccionario, detectando
    su tipo por el campo 'tipo'.
    """
    tipo = data.get('tipo', '')
    if tipo == 'AFD':
        return deserializar_afd(data)
    elif tipo == 'AFN':
        return deserializar_afn(data)
    elif tipo == 'AFNLambda':
        return deserializar_afn_lambda(data)
    else:
        raise ValueError(f"Tipo de autómata desconocido: {tipo}")


def guardar_json(automata, filepath: str) -> None:
    """
    Guarda un autómata en un archivo JSON.
    """
    data = serializar_generico(automata)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def cargar_json(filepath: str):
    """
    Carga un autómata desde un archivo JSON.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return deserializar_generico(data)


# ================================================================
# Exportación a CSV
# ================================================================

def exportar_csv(automata) -> str:
    """
    Exporta la tabla de transiciones de un autómata en formato CSV.
    
    Para AFD: cada celda contiene exactamente un estado destino.
    Para AFN/AFN-λ: cada celda puede contener múltiples estados
    separados por ';'. Las transiciones λ se indican con la columna 'λ'.
    
    Formato:
      Estado, a, b, ... [, λ]
      q0,     q1, q2, ... [, q3;q4]
      ...
    
    La primera columna marca el estado inicial con → y los
    estados finales con *.
    """
    # Determinar tipo de autómata
    es_afd = isinstance(automata, AFD) and not isinstance(automata, AFNLambda)
    es_afn_lambda = isinstance(automata, AFNLambda)

    # Preparar columnas del alfabeto
    simbolos = sorted(automata.alfabeto)

    # Agregar columna λ si tiene transiciones lambda
    tiene_lambda = False
    if es_afn_lambda:
        tiene_lambda = automata.tiene_transiciones_lambda()
        if tiene_lambda:
            simbolos = simbolos + [LAMBDA]

    # Encabezado
    lineas = ['Estado,' + ','.join(simbolos)]

    # Filas (estados ordenados)
    for estado in sorted(automata.estados):
        # Marcadores de estado inicial y final
        marca = ''
        if estado == automata.estado_inicial:
            marca = '→'
        if estado in automata.estados_finales:
            marca += '*'

        fila = [marca + estado]

        for simbolo in simbolos:
            if simbolo == LAMBDA:
                # Transiciones lambda
                destinos = automata.delta.get(estado, {}).get(LAMBDA, set())
                if es_afd:
                    fila.append('')
                else:
                    if destinos:
                        fila.append(';'.join(sorted(destinos)))
                    else:
                        fila.append('—')
            else:
                # Transiciones normales
                if es_afd:
                    destino = automata.delta.get(estado, {}).get(simbolo, '')
                    fila.append(destino if destino else '—')
                else:
                    destinos = automata.delta.get(estado, {}).get(simbolo, set())
                    if destinos:
                        fila.append(';'.join(sorted(destinos)))
                    else:
                        fila.append('—')

        lineas.append(','.join(fila))

    return '\n'.join(lineas)


# ================================================================
# Descripción Formal
# ================================================================

def exportar_descripcion_formal(automata) -> str:
    """
    Genera la descripción formal del autómata en notación matemática.
    
    Formato:
      M = (Q, Σ, δ, q0, F)
      donde:
        Q  = {q0, q1, q2, ...}
        Σ  = {a, b, c, ...}
        q0 = estado_inicial
        F  = {qf1, qf2, ...}
        δ:
          δ(q0, a) = q1
          δ(q0, b) = q2
          ...
    
    Para AFN/AFN-λ:
      δ(q0, a) = {q1, q2}
      δ(q0, λ) = {q3}
    """
    es_afd = isinstance(automata, AFD) and not isinstance(automata, AFNLambda)
    es_afn_lambda = isinstance(automata, AFNLambda)

    # Tipo de autómata
    if es_afd:
        tipo = "AFD"
    elif es_afn_lambda:
        tipo = "AFN-λ"
    else:
        tipo = "AFN"

    lineas = []

    # Encabezado
    if es_afn_lambda:
        lineas.append(f"{tipo} M = (Q, Σ, δ, q0, F)")
    else:
        lineas.append(f"{tipo} M = (Q, Σ, δ, q0, F)")

    lineas.append("donde:")

    # Q
    estados_str = ', '.join(sorted(automata.estados))
    lineas.append(f"  Q  = {{{estados_str}}}")

    # Σ
    alfabeto_str = ', '.join(sorted(automata.alfabeto))
    if es_afn_lambda:
        lineas.append(f"  Σ  = {{{alfabeto_str}}}  (λ ∉ Σ)")
    else:
        lineas.append(f"  Σ  = {{{alfabeto_str}}}")

    # q0
    lineas.append(f"  q0 = {automata.estado_inicial}")

    # F
    finales_str = ', '.join(sorted(automata.estados_finales))
    lineas.append(f"  F  = {{{finales_str}}}")

    # δ
    lineas.append("  δ:")

    simbolos_a_mostrar = sorted(automata.alfabeto)
    if es_afn_lambda and automata.tiene_transiciones_lambda():
        simbolos_a_mostrar = simbolos_a_mostrar + [LAMBDA]

    for estado in sorted(automata.estados):
        for simbolo in simbolos_a_mostrar:
            if es_afd:
                destino = automata.delta.get(estado, {}).get(simbolo, '')
                if destino:
                    lineas.append(f"    δ({estado}, {simbolo}) = {destino}")
            else:
                destinos = automata.delta.get(estado, {}).get(simbolo, set())
                if destinos:
                    destinos_str = ', '.join(sorted(destinos))
                    lineas.append(f"    δ({estado}, {simbolo}) = {{{destinos_str}}}")

    return '\n'.join(lineas)
