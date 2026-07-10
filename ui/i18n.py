"""
i18n — Internationalization module for AutomaTEC-Lab.

Usage:
    from ui.i18n import t, lang
    lang.set('en')   # or 'es'
    label_text = t('sidebar.states')

All UI strings are defined here in both Spanish (es) and English (en).
"""

from typing import Callable, List

# ─────────────────────────────────────────────────────────────────
# Translation tables
# ─────────────────────────────────────────────────────────────────

_TRANSLATIONS = {

    # ── App / Window ──────────────────────────────────────────────
    'app.title':                        {'es': 'AutomaTEC-Lab — Autómatas Finitos',
                                         'en': 'AutomaTEC-Lab — Finite Automata'},

    # ── Menu: Archivo / File ──────────────────────────────────────
    'menu.file':                        {'es': 'Archivo',      'en': 'File'},
    'menu.file.new':                    {'es': 'Nuevo',        'en': 'New'},
    'menu.file.new_afd':                {'es': 'Nuevo AFD',    'en': 'New DFA'},
    'menu.file.new_afn':                {'es': 'Nuevo AFN',    'en': 'New NFA'},
    'menu.file.new_afnl':               {'es': 'Nuevo AFN-λ',  'en': 'New NFA-λ'},
    'menu.file.open':                   {'es': 'Abrir...        Ctrl+O',
                                         'en': 'Open...         Ctrl+O'},
    'menu.file.save':                   {'es': 'Guardar         Ctrl+S',
                                         'en': 'Save            Ctrl+S'},
    'menu.file.save_as':                {'es': 'Guardar como...','en': 'Save as...'},
    'menu.file.examples':               {'es': 'Ejemplos...',   'en': 'Examples...'},
    'menu.file.exit':                   {'es': 'Salir           Ctrl+Q',
                                         'en': 'Exit            Ctrl+Q'},

    # ── Menu: Editar / Edit ───────────────────────────────────────
    'menu.edit':                        {'es': 'Editar',       'en': 'Edit'},
    'menu.edit.clear':                  {'es': 'Limpiar todo', 'en': 'Clear all'},

    # ── Menu: Ver / View ──────────────────────────────────────────
    'menu.view':                        {'es': 'Ver',          'en': 'View'},
    'menu.view.theme':                  {'es': 'Alternar Tema Claro/Oscuro  Ctrl+T',
                                         'en': 'Toggle Light/Dark Theme    Ctrl+T'},
    'menu.view.language':               {'es': 'Idioma',       'en': 'Language'},
    'menu.view.lang_es':                {'es': 'Español',      'en': 'Spanish'},
    'menu.view.lang_en':                {'es': 'Inglés',       'en': 'English'},

    # ── Menu: Herramientas / Tools ────────────────────────────────
    'menu.tools':                       {'es': 'Herramientas', 'en': 'Tools'},
    'menu.tools.completeness':          {'es': 'Verificar completitud',
                                         'en': 'Check completeness'},
    'menu.tools.remove_useless':        {'es': 'Eliminar estados no útiles',
                                         'en': 'Remove useless states'},

    # ── Menu: Ayuda / Help ────────────────────────────────────────
    'menu.help':                        {'es': 'Ayuda',        'en': 'Help'},
    'menu.help.tutorial':               {'es': 'Tutorial y Ayuda    F1',
                                         'en': 'Tutorial & Help     F1'},
    'menu.help.about':                  {'es': 'Acerca de AutomaTEC-Lab',
                                         'en': 'About AutomaTEC-Lab'},

    # ── Status bar ────────────────────────────────────────────────
    'status.default':                   {'es': 'AFD  |Q|=0  |Σ|=0  q₀=—  |F|=0',
                                         'en': 'DFA  |Q|=0  |Σ|=0  q₀=—  |F|=0'},

    # ── Sidebar ───────────────────────────────────────────────────
    'sidebar.title':                    {'es': 'Definir Autómata',   'en': 'Define Automaton'},
    'sidebar.type':                     {'es': 'Tipo de Autómata',   'en': 'Automaton Type'},
    'sidebar.states':                   {'es': 'Estados',            'en': 'States'},
    'sidebar.alphabet':                 {'es': 'Alfabeto',           'en': 'Alphabet'},
    'sidebar.initial':                  {'es': 'Estado Inicial',     'en': 'Initial State'},
    'sidebar.finals':                   {'es': 'Estados Finales',    'en': 'Final States'},
    'sidebar.actions':                  {'es': 'Acciones',           'en': 'Actions'},
    'sidebar.add':                      {'es': 'Agregar',            'en': 'Add'},
    'sidebar.load_example':             {'es': '📋 Cargar Ejemplo',  'en': '📋 Load Example'},
    'sidebar.import_json':              {'es': '📥 Importar JSON',   'en': '📥 Import JSON'},
    'sidebar.export_json':              {'es': '📤 Exportar JSON',   'en': '📤 Export JSON'},
    'sidebar.clear_all':                {'es': '🗑️ Limpiar Todo',   'en': '🗑️ Clear All'},
    'sidebar.no_states':                {'es': '(agregue estados primero)',
                                         'en': '(add states first)'},

    # ── Canvas toolbar ────────────────────────────────────────────
    'canvas.zoom_in':                   {'es': 'Zoom +',         'en': 'Zoom +'},
    'canvas.zoom_out':                  {'es': 'Zoom -',         'en': 'Zoom -'},
    'canvas.fit':                       {'es': 'Ajustar',        'en': 'Fit'},
    'canvas.save_image':                {'es': 'Guardar imagen', 'en': 'Save image'},
    'canvas.no_automaton':              {'es': 'Define un autómata para ver su diagrama',
                                         'en': 'Define an automaton to see its diagram'},
    'canvas.graphviz_missing':          {'es': 'Graphviz (dot) no encontrado.\n\nInstala Graphviz para ver el diagrama.\nDescarga en: graphviz.org',
                                         'en': 'Graphviz (dot) not found.\n\nInstall Graphviz to view the diagram.\nDownload at: graphviz.org'},

    # ── Notebook tabs ─────────────────────────────────────────────
    'tab.table':                        {'es': '  Tabla  ',              'en': '  Table  '},
    'tab.process':                      {'es': '  Procesar  ',           'en': '  Process  '},
    'tab.minimize':                     {'es': '  Minimizar  ',          'en': '  Minimize  '},
    'tab.equivalence':                  {'es': '  Equivalencia  ',       'en': '  Equivalence  '},
    'tab.operations':                   {'es': '  Operaciones  ',        'en': '  Operations  '},
    'tab.properties':                   {'es': '  Propiedades  ',        'en': '  Properties  '},
    'tab.subsets':                      {'es': '  Subconjuntos  ',       'en': '  Subsets  '},
    'tab.eliminate_lambda':             {'es': '  Eliminar λ  ',         'en': '  Eliminate λ  '},
    'tab.afn_operations':               {'es': '  Operaciones AFN  ',    'en': '  NFA Operations  '},
    'tab.conversion':                   {'es': '  Conversión  ',         'en': '  Conversion  '},
    'tab.regex':                        {'es': '  Expr. Regulares  ',    'en': '  Regular Expr.  '},

    # ── Log panel ─────────────────────────────────────────────────
    'log.title':                        {'es': '📋 Registro',   'en': '📋 Log'},
    'log.clear':                        {'es': 'Limpiar',       'en': 'Clear'},

    # ── Table widget ──────────────────────────────────────────────
    'table.placeholder':                {'es': 'Define estados y alfabeto para crear la tabla',
                                         'en': 'Define states and alphabet to create the table'},

    # ── String Processor ──────────────────────────────────────────
    'proc.string_w':                    {'es': 'Cadena w:',          'en': 'String w:'},
    'proc.hint':                        {'es': 'Ingrese la cadena w','en': 'Enter string w'},
    'proc.verify':                      {'es': '✓ Verificar',        'en': '✓ Verify'},
    'proc.step_mode':                   {'es': '▶ Modo Paso a Paso', 'en': '▶ Step-by-Step'},
    'proc.reset':                       {'es': '↺ Reiniciar',        'en': '↺ Reset'},
    'proc.prev':                        {'es': '◀ Anterior',         'en': '◀ Previous'},
    'proc.next':                        {'es': 'Siguiente ▶',        'en': 'Next ▶'},
    'proc.trace':                       {'es': 'Traza de ejecución:','en': 'Execution trace:'},
    'proc.accepted':                    {'es': '✓ ACEPTADA',         'en': '✓ ACCEPTED'},
    'proc.rejected':                    {'es': '✗ RECHAZADA',        'en': '✗ REJECTED'},
    'proc.step_label':                  {'es': 'Paso {cur} / {tot}', 'en': 'Step {cur} / {tot}'},
    'proc.no_trace':                    {'es': '(sin traza)',         'en': '(no trace)'},

    # ── Minimization Panel ────────────────────────────────────────
    'min.title':                        {'es': 'Minimización de AFD',    'en': 'DFA Minimization'},
    'min.btn_all':                      {'es': '⚡ Minimizar Todo',       'en': '⚡ Minimize All'},
    'min.btn_step':                     {'es': '▶ Minimizar Paso a Paso','en': '▶ Step-by-Step'},
    'min.btn_reset':                    {'es': '↺ Reiniciar',             'en': '↺ Reset'},
    'min.btn_completed':                {'es': '✓ Completado',            'en': '✓ Completed'},
    'min.table_title':                  {'es': 'Tabla de Distinguibilidad','en': 'Distinguishability Table'},
    'min.classes_title':                {'es': 'Clases de Equivalencia',  'en': 'Equivalence Classes'},
    'min.table_placeholder':            {'es': 'Ejecute la minimización para ver la tabla',
                                         'en': 'Run minimization to see the table'},
    'min.classes_placeholder':          {'es': 'Ejecute la minimización para ver las clases',
                                         'en': 'Run minimization to see the classes'},
    'min.btn_view':                     {'es': '👁 Ver AFD Mínimo en Canvas',
                                         'en': '👁 View Minimal DFA on Canvas'},
    'min.result_already':               {'es': '✓ El AFD ya es mínimo ({n} estados)',
                                         'en': '✓ DFA is already minimal ({n} states)'},
    'min.result_reduced':               {'es': '✓ AFD mínimo: {n} estados (original: {orig})',
                                         'en': '✓ Minimal DFA: {n} states (original: {orig})'},

    # ── Equivalence Panel ─────────────────────────────────────────
    'eq.title':                         {'es': 'Equivalencia de AFDs',    'en': 'DFA Equivalence'},
    'eq.afd1_info':                     {'es': 'AFD₁: (autómata actual del panel lateral)',
                                         'en': 'DFA₁: (current automaton from side panel)'},
    'eq.afd2_title':                    {'es': 'AFD₂ (segundo autómata):','en': 'DFA₂ (second automaton):'},
    'eq.states_label':                  {'es': 'Estados (coma):',  'en': 'States (comma):'},
    'eq.alphabet_label':                {'es': 'Alfabeto (coma):', 'en': 'Alphabet (comma):'},
    'eq.gen_table':                     {'es': '📋 Generar Tabla de Transiciones',
                                         'en': '📋 Generate Transition Table'},
    'eq.table_title':                   {'es': 'Tabla de Transiciones AFD₂:',
                                         'en': 'Transition Table DFA₂:'},
    'eq.table_placeholder':             {'es': 'Ingrese estados y alfabeto, luego genere la tabla',
                                         'en': 'Enter states and alphabet, then generate the table'},
    'eq.initial_state':                 {'es': 'Estado inicial:',  'en': 'Initial state:'},
    'eq.finals_title':                  {'es': 'Estados finales AFD₂:','en': 'Final states DFA₂:'},
    'eq.finals_placeholder':            {'es': '(genere la tabla primero)',
                                         'en': '(generate the table first)'},
    'eq.btn_verify':                    {'es': '⚡ Verificar Equivalencia',
                                         'en': '⚡ Verify Equivalence'},
    'eq.equivalent':                    {'es': '✓ EQUIVALENTES',  'en': '✓ EQUIVALENT'},
    'eq.different':                     {'es': '✗ DISTINTOS',     'en': '✗ DIFFERENT'},
    'eq.witness':                       {'es': 'Cadena testigo (contraejemplo): "{w}"\nEsta cadena es aceptada por un AFD pero no por el otro.',
                                         'en': 'Witness string (counterexample): "{w}"\nThis string is accepted by one DFA but not the other.'},
    'eq.no_witness':                    {'es': 'No se encontró cadena testigo.',
                                         'en': 'No witness string found.'},

    # ── Operations Panel ──────────────────────────────────────────
    'ops.title':                        {'es': 'Operaciones con AFDs',  'en': 'DFA Operations'},
    'ops.afd1_info':                    {'es': 'AFD₁: (autómata actual del panel lateral)',
                                         'en': 'DFA₁: (current automaton from side panel)'},
    'ops.afd2_title':                   {'es': 'AFD₂ (segundo autómata):',
                                         'en': 'DFA₂ (second automaton):'},
    'ops.states_label':                 {'es': 'Estados (coma):',  'en': 'States (comma):'},
    'ops.alphabet_label':               {'es': 'Alfabeto (coma):', 'en': 'Alphabet (comma):'},
    'ops.gen_table':                    {'es': '📋 Generar Tabla de Transiciones',
                                         'en': '📋 Generate Transition Table'},
    'ops.table_title':                  {'es': 'Tabla de Transiciones AFD₂:',
                                         'en': 'Transition Table DFA₂:'},
    'ops.table_placeholder':            {'es': 'Ingrese estados y alfabeto, luego genere la tabla',
                                         'en': 'Enter states and alphabet, then generate the table'},
    'ops.initial_state':                {'es': 'Estado inicial:',  'en': 'Initial state:'},
    'ops.finals_title':                 {'es': 'Estados finales AFD₂:','en': 'Final states DFA₂:'},
    'ops.finals_placeholder':           {'es': '(genere la tabla primero)',
                                         'en': '(generate the table first)'},
    'ops.operations_label':             {'es': 'Operaciones:',     'en': 'Operations:'},
    'ops.union':                        {'es': '∪  Unión',         'en': '∪  Union'},
    'ops.intersection':                 {'es': '∩  Intersección',  'en': '∩  Intersection'},
    'ops.difference':                   {'es': '−  Diferencia',    'en': '−  Difference'},
    'ops.complement':                   {'es': '̄  Complemento',   'en': '̄  Complement'},
    'ops.result_title':                 {'es': 'Resultado:',       'en': 'Result:'},
    'ops.btn_view':                     {'es': '👁 Ver Resultado en Canvas',
                                         'en': '👁 View Result on Canvas'},

    # ── Properties Panel ──────────────────────────────────────────
    'prop.title':                       {'es': 'Propiedades del Lenguaje', 'en': 'Language Properties'},
    'prop.empty':                       {'es': '🔍 ¿Lenguaje vacío?',      'en': '🔍 Empty language?'},
    'prop.infinite':                    {'es': '🔍 ¿Lenguaje infinito?',   'en': '🔍 Infinite language?'},
    'prop.finite':                      {'es': '🔍 ¿Lenguaje finito?',     'en': '🔍 Finite language?'},
    'prop.shortest':                    {'es': '🔍 Cadena más corta aceptada',
                                         'en': '🔍 Shortest accepted string'},
    'prop.accessible':                  {'es': '🔍 Estados accesibles',    'en': '🔍 Accessible states'},
    'prop.productive':                  {'es': '🔍 Estados productivos',   'en': '🔍 Productive states'},
    'prop.useful':                      {'es': '🔍 Estados útiles',        'en': '🔍 Useful states'},
    'prop.clean':                       {'es': '🗑️ Limpiar AFD (eliminar estados no útiles)',
                                         'en': '🗑️ Clean DFA (remove useless states)'},
    'prop.verify_all':                  {'es': '⚡ Verificar Todas las Propiedades',
                                         'en': '⚡ Verify All Properties'},
    'prop.empty_yes':                   {'es': '✓ SÍ — L(M) = ∅',  'en': '✓ YES — L(M) = ∅'},
    'prop.empty_no':                    {'es': '✗ NO — L(M) ≠ ∅',  'en': '✗ NO — L(M) ≠ ∅'},
    'prop.infinite_yes':                {'es': '✓ SÍ — |L(M)| = ∞','en': '✓ YES — |L(M)| = ∞'},
    'prop.infinite_no':                 {'es': '✗ NO — |L(M)| < ∞','en': '✗ NO — |L(M)| < ∞'},
    'prop.finite_yes':                  {'es': '✓ SÍ — |L(M)| < ∞','en': '✓ YES — |L(M)| < ∞'},
    'prop.finite_no':                   {'es': '✗ NO — |L(M)| = ∞','en': '✗ NO — |L(M)| = ∞'},
    'prop.shortest_none':               {'es': 'No existe (L = ∅)', 'en': 'None (L = ∅)'},
    'prop.shortest_lambda':             {'es': 'λ (cadena vacía)',   'en': 'λ (empty string)'},
    'prop.shortest_val':                {'es': '"{w}" (|w|={n})',    'en': '"{w}" (|w|={n})'},
    'prop.no_accessible':               {'es': '∅ (ningún estado accesible)',
                                         'en': '∅ (no accessible state)'},
    'prop.no_productive':               {'es': '∅ (ningún estado productivo)',
                                         'en': '∅ (no productive state)'},
    'prop.no_useful':                   {'es': '∅ (ningún estado útil)',
                                         'en': '∅ (no useful state)'},

    # ── AFN Panels ────────────────────────────────────────────────
    'afn.subset.btn_convert':           {'es': '🔄 Convertir AFN → AFD',
                                         'en': '🔄 Convert NFA → DFA'},
    'afn.subset.btn_step':              {'es': '📝 Paso a Paso',     'en': '📝 Step-by-Step'},
    'afn.subset.btn_next':              {'es': '▶ Siguiente paso',   'en': '▶ Next step'},
    'afn.subset.btn_use':               {'es': '✅ Usar como actual', 'en': '✅ Use as current'},
    'afn.subset.completed':             {'es': '\n✓ Construcción completada.\n',
                                         'en': '\n✓ Construction completed.\n'},

    'afn.epsilon.btn_eliminate':        {'es': '🔄 Eliminar λ-transiciones',
                                         'en': '🔄 Eliminate λ-transitions'},
    'afn.epsilon.btn_use':              {'es': '✅ Usar AFN como actual',
                                         'en': '✅ Use NFA as current'},

    'afn.ops.btn_kleene':               {'es': '* Clausura de Kleene (L*)',
                                         'en': '* Kleene Closure (L*)'},
    'afn.ops.btn_positive':             {'es': '+ Clausura Positiva (L+)',
                                         'en': '+ Positive Closure (L+)'},
    'afn.ops.btn_reverse':              {'es': 'R Reverso (Lᴿ)',    'en': 'R Reverse (Lᴿ)'},
    'afn.ops.btn_use':                  {'es': '✅ Usar resultado como actual',
                                         'en': '✅ Use result as current'},

    'afn.chain.btn_run':                {'es': '🔄 Ejecutar cadena completa',
                                         'en': '🔄 Run full conversion chain'},
    'afn.chain.btn_next':               {'es': '▶ Siguiente etapa',  'en': '▶ Next stage'},
    'afn.chain.btn_use':                {'es': '✅ Usar AFD mínimo como actual',
                                         'en': '✅ Use minimal DFA as current'},

    # ── Regex Panel ───────────────────────────────────────────────
    'regex.er_title':                   {'es': ' ER → AFN-λ (Construcción de Thompson) ',
                                         'en': ' RE → NFA-λ (Thompson Construction) '},
    'regex.er_label':                   {'es': 'ER:',               'en': 'RE:'},
    'regex.btn_thompson':               {'es': 'Convertir ER → AFN-λ',
                                         'en': 'Convert RE → NFA-λ'},
    'regex.operators':                  {'es': 'Operadores: | (unión)  . (concat)  * (Kleene)  + (positiva)  ? (opcional)  () (agrupación)',
                                         'en': 'Operators: | (union)  . (concat)  * (Kleene)  + (positive)  ? (optional)  () (grouping)'},
    'regex.valid':                      {'es': '✓ Expresión válida', 'en': '✓ Valid expression'},
    'regex.btn_use_afnl':               {'es': '✅ Usar AFN-λ como actual',
                                         'en': '✅ Use NFA-λ as current'},
    'regex.afd_title':                  {'es': ' AFD → ER (Lema de Arden) ',
                                         'en': ' DFA → RE (Arden\'s Lemma) '},
    'regex.btn_arden':                  {'es': 'AFD → ER',          'en': 'DFA → RE'},

    # ── Examples Dialog ───────────────────────────────────────────
    'examples.title':                   {'es': 'AutomaTEC-Lab — Ejemplos',
                                         'en': 'AutomaTEC-Lab — Examples'},
    'examples.heading':                 {'es': '📋 Ejemplos Predefinidos',
                                         'en': '📋 Predefined Examples'},
    'examples.subtitle':                {'es': 'Selecciona un ejemplo para cargarlo como autómata actual.',
                                         'en': 'Select an example to load it as the current automaton.'},
    'examples.col_name':                {'es': 'Nombre',            'en': 'Name'},
    'examples.col_type':                {'es': 'Tipo',              'en': 'Type'},
    'examples.col_desc':                {'es': 'Descripción',       'en': 'Description'},
    'examples.btn_load':                {'es': '✅ Cargar',         'en': '✅ Load'},
    'examples.btn_close':               {'es': 'Cerrar',            'en': 'Close'},

    # ── Help Dialog ───────────────────────────────────────────────
    'help.title':                       {'es': 'AutomaTEC-Lab — Ayuda','en': 'AutomaTEC-Lab — Help'},
    'help.tab_guide':                   {'es': '📖 Guía de Uso',    'en': '📖 User Guide'},
    'help.tab_shortcuts':               {'es': '⌨️ Atajos',         'en': '⌨️ Shortcuts'},
    'help.tab_reference':               {'es': '📚 Referencia',     'en': '📚 Reference'},
    'help.btn_close':                   {'es': 'Cerrar',            'en': 'Close'},

    # ── Dialogs / Messages ────────────────────────────────────────
    'msg.no_automaton':                 {'es': 'No hay un autómata definido.',
                                         'en': 'No automaton is defined.'},
    'msg.no_initial':                   {'es': 'Defina un estado inicial para el autómata.',
                                         'en': 'Define an initial state for the automaton.'},
    'msg.no_states':                    {'es': 'El autómata no tiene estados.',
                                         'en': 'The automaton has no states.'},
    'msg.not_afd':                      {'es': 'El autómata actual debe ser un AFD.',
                                         'en': 'The current automaton must be a DFA.'},
    'msg.not_afn':                      {'es': 'Se requiere un AFN o AFN-λ.',
                                         'en': 'An NFA or NFA-λ is required.'},
    'msg.not_afn_lambda':               {'es': 'Se requiere un AFN-λ.',
                                         'en': 'An NFA-λ is required.'},
    'msg.afd_incomplete':               {'es': 'El AFD actual debe tener estados y estado inicial.',
                                         'en': 'The current DFA must have states and an initial state.'},
    'msg.min_not_afd':                  {'es': 'La minimización solo aplica a AFD.\nConvierta el autómata a AFD primero.',
                                         'en': 'Minimization only applies to DFA.\nConvert the automaton to DFA first.'},
    'msg.prop_not_afd':                 {'es': 'Las propiedades solo aplican a AFD.\nConvierta el autómata a AFD primero.',
                                         'en': 'Properties only apply to DFA.\nConvert the automaton to DFA first.'},
    'msg.diff_alphabets':               {'es': 'Para operaciones binarias, ambos AFDs deben tener el mismo alfabeto.\nAFD₁: Σ={a1}\nAFD₂: Σ={a2}',
                                         'en': 'For binary operations, both DFAs must share the same alphabet.\nDFA₁: Σ={a1}\nDFA₂: Σ={a2}'},
    'msg.invalid_trans':                {'es': 'δ₂({q}, {s}) = "{v}" no es un estado válido.',
                                         'en': 'δ₂({q}, {s}) = "{v}" is not a valid state.'},
    'msg.dup_state':                    {'es': 'El estado "{s}" ya existe.',
                                         'en': 'State "{s}" already exists.'},
    'msg.sym_too_long':                 {'es': 'Los símbolos del alfabeto deben ser un solo carácter.',
                                         'en': 'Alphabet symbols must be a single character.'},
    'msg.dup_sym':                      {'es': 'El símbolo "{s}" ya está en el alfabeto.',
                                         'en': 'Symbol "{s}" is already in the alphabet.'},
    'msg.no_export':                    {'es': 'No hay un autómata para exportar.',
                                         'en': 'No automaton to export.'},
    'msg.clean_already':                {'es': 'El AFD no tiene estados no útiles.',
                                         'en': 'The DFA has no useless states.'},
    'msg.clean_confirm':                {'es': 'Se eliminarán {n} estados no útiles:\n{states}\n\n¿Desea continuar?',
                                         'en': 'Will remove {n} useless states:\n{states}\n\nDo you want to continue?'},
    'msg.completeness_yes':             {'es': '✓ El AFD es completo.',
                                         'en': '✓ The DFA is complete.'},
    'msg.completeness_no':              {'es': '✗ El AFD NO es completo. Faltan transiciones.',
                                         'en': '✗ The DFA is NOT complete. Transitions are missing.'},
    'msg.no_regex':                     {'es': 'Ingrese una expresión regular.',
                                         'en': 'Enter a regular expression.'},
    'msg.no_selection':                 {'es': 'Seleccione un ejemplo.',
                                         'en': 'Select an example.'},
    'msg.min_complete':                 {'es': 'La minimización ya está completa.',
                                         'en': 'Minimization is already complete.'},
    'msg.no_result':                    {'es': 'Ejecute una operación primero.',
                                         'en': 'Run an operation first.'},
    'msg.no_result_min':                {'es': 'Ejecute la minimización primero.',
                                         'en': 'Run minimization first.'},
    'msg.data_incomplete':              {'es': 'Ingrese estados y alfabeto para AFD₂.',
                                         'en': 'Enter states and alphabet for DFA₂.'},
    'msg.data_invalid':                 {'es': 'Estados y alfabeto no pueden estar vacíos.',
                                         'en': 'States and alphabet cannot be empty.'},
    'msg.no_initial2':                  {'es': 'Seleccione un estado inicial para AFD₂.',
                                         'en': 'Select an initial state for DFA₂.'},
    'msg.data_incomplete2':             {'es': 'Complete los estados y alfabeto de AFD₂.',
                                         'en': 'Complete the states and alphabet for DFA₂.'},

    # ── Window titles for dialogs ─────────────────────────────────
    'dlg.no_automaton':                 {'es': 'Sin autómata',       'en': 'No automaton'},
    'dlg.no_initial':                   {'es': 'Sin estado inicial', 'en': 'No initial state'},
    'dlg.no_states':                    {'es': 'Sin estados',        'en': 'No states'},
    'dlg.error':                        {'es': 'Error',              'en': 'Error'},
    'dlg.invalid_afd':                  {'es': 'AFD₁ inválido',     'en': 'Invalid DFA₁'},
    'dlg.incomplete_afd':               {'es': 'AFD₁ incompleto',   'en': 'Incomplete DFA₁'},
    'dlg.not_afd':                      {'es': 'No es AFD',         'en': 'Not a DFA'},
    'dlg.not_afn':                      {'es': 'Tipo incorrecto',   'en': 'Wrong type'},
    'dlg.diff_alphabets':               {'es': 'Alfabetos diferentes','en': 'Different alphabets'},
    'dlg.invalid_trans':                {'es': 'Transición inválida','en': 'Invalid transition'},
    'dlg.dup_state':                    {'es': 'Estado duplicado',  'en': 'Duplicate state'},
    'dlg.invalid_sym':                  {'es': 'Símbolo inválido',  'en': 'Invalid symbol'},
    'dlg.dup_sym':                      {'es': 'Símbolo duplicado', 'en': 'Duplicate symbol'},
    'dlg.no_export':                    {'es': 'Sin autómata',      'en': 'No automaton'},
    'dlg.clean_title':                  {'es': 'Ya limpio',         'en': 'Already clean'},
    'dlg.clean_confirm':                {'es': 'Confirmar limpieza','en': 'Confirm cleanup'},
    'dlg.completeness':                 {'es': 'Completitud',       'en': 'Completeness'},
    'dlg.no_regex':                     {'es': 'Sin expresión',     'en': 'No expression'},
    'dlg.no_selection':                 {'es': 'Sin selección',     'en': 'No selection'},
    'dlg.min_complete':                 {'es': 'Completado',        'en': 'Completed'},
    'dlg.no_result':                    {'es': 'Sin resultado',     'en': 'No result'},
    'dlg.data_incomplete':              {'es': 'Datos incompletos', 'en': 'Incomplete data'},
    'dlg.data_invalid':                 {'es': 'Datos inválidos',   'en': 'Invalid data'},

    # ── About dialog ──────────────────────────────────────────────
    'about.text':   {
        'es': (
            "AutomaTEC-Lab v1.0\n\n"
            "Aplicación de Autómatas Finitos\n"
            "AFD · AFN · AFN-λ · Expresiones Regulares\n\n"
            "Características:\n"
            "• Visualización con Graphviz\n"
            "• Procesamiento de cadenas con traza\n"
            "• Minimización de AFD\n"
            "• Construcción de subconjuntos\n"
            "• Construcción de Thompson (ER → AFN-λ)\n"
            "• Lema de Arden (AFD → ER)\n"
            "• Operaciones booleanas\n"
            "• Verificación de equivalencia\n"
            "• Análisis de propiedades\n\n"
            "Tema oscuro/claro · Import/Export JSON"
        ),
        'en': (
            "AutomaTEC-Lab v1.0\n\n"
            "Finite Automata Application\n"
            "DFA · NFA · NFA-λ · Regular Expressions\n\n"
            "Features:\n"
            "• Visualization with Graphviz\n"
            "• String processing with execution trace\n"
            "• DFA Minimization\n"
            "• Subset construction\n"
            "• Thompson Construction (RE → NFA-λ)\n"
            "• Arden's Lemma (DFA → RE)\n"
            "• Boolean operations\n"
            "• Equivalence verification\n"
            "• Language property analysis\n\n"
            "Dark/Light theme · Import/Export JSON"
        ),
    },

    # ── Log messages ──────────────────────────────────────────────
    'log.started':                      {'es': 'AutomaTEC-Lab iniciado. Define un autómata o carga un ejemplo.',
                                         'en': 'AutomaTEC-Lab started. Define an automaton or load an example.'},
    'log.type_changed':                 {'es': 'Tipo cambiado a: {t}',   'en': 'Type changed to: {t}'},
    'log.new_automaton':                {'es': 'Nuevo {t} creado.',       'en': 'New {t} created.'},
    'log.state_added':                  {'es': 'Estado agregado: {s}',    'en': 'State added: {s}'},
    'log.state_removed':                {'es': 'Estado eliminado: {s}',   'en': 'State removed: {s}'},
    'log.initial_set':                  {'es': 'Estado inicial: {s}',     'en': 'Initial state: {s}'},
    'log.final_added':                  {'es': 'Estado final agregado: {s}',  'en': 'Final state added: {s}'},
    'log.final_removed':                {'es': 'Estado final eliminado: {s}', 'en': 'Final state removed: {s}'},
    'log.transition_updated':           {'es': 'Transición actualizada: delta({q}, {s})',
                                         'en': 'Transition updated: delta({q}, {s})'},
    'log.example_loaded':               {'es': 'Ejemplo cargado: {name}', 'en': 'Example loaded: {name}'},
    'log.imported':                     {'es': 'Autómata importado desde {f}',
                                         'en': 'Automaton imported from {f}'},
    'log.exported':                     {'es': 'Autómata exportado a {f}', 'en': 'Automaton exported to {f}'},
    'log.cleared':                      {'es': 'Autómata limpiado.',       'en': 'Automaton cleared.'},
    'log.accepted':                     {'es': 'Cadena "{w}": ACEPTADA',   'en': 'String "{w}": ACCEPTED'},
    'log.rejected':                     {'es': 'Cadena "{w}": RECHAZADA',  'en': 'String "{w}": REJECTED'},
    'log.step_started':                 {'es': 'Modo paso a paso iniciado para "{w}"',
                                         'en': 'Step-by-step mode started for "{w}"'},
    'log.min_complete':                 {'es': 'Minimización completa: AFD mínimo con {n} estados',
                                         'en': 'Minimization complete: minimal DFA with {n} states'},
    'log.min_step':                     {'es': 'Paso {n} de minimización ejecutado',
                                         'en': 'Minimization step {n} executed'},
    'log.min_step_complete':            {'es': 'Minimización paso a paso completada: AFD mínimo con {n} estados',
                                         'en': 'Step-by-step minimization completed: minimal DFA with {n} states'},
    'log.canvas_min':                   {'es': 'Mostrando AFD mínimo en el canvas',
                                         'en': 'Showing minimal DFA on canvas'},
    'log.canvas_result':                {'es': 'Mostrando resultado de operación en el canvas',
                                         'en': 'Showing operation result on canvas'},
    'log.equiv_yes':                    {'es': 'Los AFDs son equivalentes',
                                         'en': 'The DFAs are equivalent'},
    'log.equiv_no':                     {'es': 'Los AFDs NO son equivalentes. Cadena testigo: "{w}"',
                                         'en': 'The DFAs are NOT equivalent. Witness string: "{w}"'},
    'log.equiv_no_witness':             {'es': 'Los AFDs NO son equivalentes',
                                         'en': 'The DFAs are NOT equivalent'},
    'log.union':                        {'es': 'Unión: AFD con {n} estados',
                                         'en': 'Union: DFA with {n} states'},
    'log.intersection':                 {'es': 'Intersección: AFD con {n} estados',
                                         'en': 'Intersection: DFA with {n} states'},
    'log.difference':                   {'es': 'Diferencia: AFD con {n} estados',
                                         'en': 'Difference: DFA with {n} states'},
    'log.complement':                   {'es': 'Complemento: AFD con {n} estados',
                                         'en': 'Complement: DFA with {n} states'},
    'log.prop_empty_yes':               {'es': 'Lenguaje vacío: SÍ',   'en': 'Empty language: YES'},
    'log.prop_empty_no':                {'es': 'Lenguaje vacío: NO',   'en': 'Empty language: NO'},
    'log.prop_infinite_yes':            {'es': 'Lenguaje infinito: SÍ','en': 'Infinite language: YES'},
    'log.prop_infinite_no':             {'es': 'Lenguaje infinito: NO','en': 'Infinite language: NO'},
    'log.prop_finite_yes':              {'es': 'Lenguaje finito: SÍ', 'en': 'Finite language: YES'},
    'log.prop_finite_no':               {'es': 'Lenguaje finito: NO', 'en': 'Finite language: NO'},
    'log.prop_shortest':                {'es': 'Cadena más corta: "{w}"','en': 'Shortest string: "{w}"'},
    'log.prop_shortest_empty':          {'es': 'Cadena más corta: λ', 'en': 'Shortest string: λ'},
    'log.prop_shortest_none':           {'es': 'Cadena más corta: L = ∅','en': 'Shortest string: L = ∅'},
    'log.prop_accessible':              {'es': 'Estados accesibles: {n}/{total}',
                                         'en': 'Accessible states: {n}/{total}'},
    'log.prop_not_accessible':          {'es': 'Estados NO accesibles: {states}',
                                         'en': 'NON-accessible states: {states}'},
    'log.prop_productive':              {'es': 'Estados productivos: {n}/{total}',
                                         'en': 'Productive states: {n}/{total}'},
    'log.prop_not_productive':          {'es': 'Estados NO productivos: {states}',
                                         'en': 'NON-productive states: {states}'},
    'log.prop_useful':                  {'es': 'Estados útiles: {n}/{total}',
                                         'en': 'Useful states: {n}/{total}'},
    'log.prop_not_useful':              {'es': 'Estados no útiles: {states} (puede limpiar el AFD)',
                                         'en': 'Useless states: {states} (you can clean the DFA)'},
    'log.prop_all':                     {'es': 'Todas las propiedades verificadas',
                                         'en': 'All properties verified'},
    'log.clean_done':                   {'es': 'AFD limpiado: eliminados {n} estados no útiles. Quedan {r} estados.',
                                         'en': 'DFA cleaned: removed {n} useless states. {r} states remain.'},
    'log.useless_removed':              {'es': 'Estados inútiles eliminados: {orig} → {new}',
                                         'en': 'Useless states removed: {orig} → {new}'},
    'log.complete_yes':                 {'es': 'AFD completo: Sí',  'en': 'DFA complete: Yes'},
    'log.complete_no':                  {'es': 'AFD completo: No',  'en': 'DFA complete: No'},
    'log.subset_done':                  {'es': 'Construcción de subconjuntos completada.',
                                         'en': 'Subset construction completed.'},
    'log.subset_started':               {'es': "Modo paso a paso iniciado. Presiona 'Siguiente paso'.",
                                         'en': "Step-by-step mode started. Press 'Next step'."},
    'log.subset_step_done':             {'es': 'Construcción de subconjuntos completada (paso a paso).',
                                         'en': 'Subset construction completed (step-by-step).'},
    'log.epsilon_done':                 {'es': 'λ-transiciones eliminadas correctamente.',
                                         'en': 'λ-transitions successfully eliminated.'},
    'log.afn_op_done':                  {'es': "Operación '{op}' aplicada.",
                                         'en': "Operation '{op}' applied."},
    'log.thompson_done':                {'es': "Construcción de Thompson: ER '{r}' → AFN-λ ({n} estados)",
                                         'en': "Thompson Construction: RE '{r}' → NFA-λ ({n} states)"},
    'log.arden_done':                   {'es': 'AFD → ER completada: {r}',
                                         'en': 'DFA → RE completed: {r}'},
    'log.afnl_set':                     {'es': 'AFN-λ de Thompson establecido como autómata actual.',
                                         'en': 'Thompson NFA-λ set as current automaton.'},
    'log.afn_set':                      {'es': 'AFN sin λ establecido como autómata actual.',
                                         'en': 'NFA without λ set as current automaton.'},
    'log.result_set':                   {'es': '{t} resultante establecido como autómata actual.',
                                         'en': 'Resulting {t} set as current automaton.'},
    'log.afd_result_set':               {'es': 'AFD resultante establecido como autómata actual.',
                                         'en': 'Resulting DFA set as current automaton.'},
    'log.min_afd_set':                  {'es': 'AFD mínimo establecido como autómata actual.',
                                         'en': 'Minimal DFA set as current automaton.'},
    'log.import_error':                 {'es': 'Error al importar: {e}', 'en': 'Import error: {e}'},
    'log.export_error':                 {'es': 'Error al exportar: {e}', 'en': 'Export error: {e}'},
    'log.example_error':                {'es': 'Error al cargar ejemplo: {e}',
                                         'en': 'Error loading example: {e}'},
    'log.example_pair':                 {'es': 'Ejemplo con par de AFDs: se cargó el primer AFD.',
                                         'en': 'Example with DFA pair: first DFA loaded.'},
    'log.example_loaded_type':          {'es': 'Ejemplo cargado: {t}', 'en': 'Example loaded: {t}'},
    'log.imported_from':                {'es': 'Autómata importado desde {f}',
                                         'en': 'Automaton imported from {f}'},
    # ── Operations result display ─────────────────────────────────
    'ops.result.operation':             {'es': 'Operación: {op}',      'en': 'Operation: {op}'},
    'ops.result.states':                {'es': 'Estados: {s}',         'en': 'States: {s}'},
    'ops.result.alphabet':              {'es': 'Alfabeto: {s}',        'en': 'Alphabet: {s}'},
    'ops.result.initial':               {'es': 'Estado inicial: {s}',  'en': 'Initial state: {s}'},
    'ops.result.finals':                {'es': 'Estados finales: {s}', 'en': 'Final states: {s}'},
    'ops.result.total':                 {'es': 'Total de estados: {n}','en': 'Total states: {n}'},
    'ops.result.transitions':           {'es': 'Transiciones:',        'en': 'Transitions:'},

    # ── Subset construction panel ─────────────────────────────────
    'afn.subset.type_error':            {'es': 'Se requiere un AFN o AFN-λ para la construcción de subconjuntos.',
                                         'en': 'An NFA or NFA-λ is required for subset construction.'},
    'afn.subset.no_automaton':          {'es': 'El autómata no tiene estados o estado inicial definido.',
                                         'en': 'The automaton has no states or initial state defined.'},
    'afn.subset.step_hint':             {'es': "Modo paso a paso iniciado. Presiona 'Siguiente paso'.",
                                         'en': "Step-by-step mode started. Press 'Next step'."},

    # ── String w label ────────────────────────────────────────────
    'proc.string_w_label':              {'es': 'Cadena w:',            'en': 'String w:'},

    # ── Minimization placeholders (dynamic) ───────────────────────
    'min.table_placeholder_dynamic':    {'es': 'Ejecute la minimización para ver la tabla',
                                         'en': 'Run minimization to see the table'},
    'min.classes_placeholder_dynamic':  {'es': 'Ejecute la minimización para ver las clases',
                                         'en': 'Run minimization to see the classes'},

    # ── AFD/DFA type labels in radio buttons ──────────────────────
    'type.afd':   {'es': 'AFD',   'en': 'DFA'},
    'type.afn':   {'es': 'AFN',   'en': 'NFA'},
    'type.afnl':  {'es': 'AFN-λ', 'en': 'NFA-λ'},

    # ── equivalence / operations shared anon label keys ──────────
    'eq.afd2_subtitle':                 {'es': 'AFD₂ (segundo autómata):', 'en': 'DFA₂ (second automaton):'},
    'ops.afd2_subtitle':                {'es': 'AFD₂ (segundo autómata):', 'en': 'DFA₂ (second automaton):'},
    'shared.states_comma':              {'es': 'Estados (coma):',      'en': 'States (comma):'},
    'shared.alphabet_comma':            {'es': 'Alfabeto (coma):',     'en': 'Alphabet (comma):'},
    'shared.initial_state':             {'es': 'Estado inicial:',      'en': 'Initial state:'},
    'shared.finals_title_afd2':         {'es': 'Estados finales AFD₂:','en': 'Final states DFA₂:'},
    'shared.operations_label':          {'es': 'Operaciones:',         'en': 'Operations:'},
    'shared.result_label':              {'es': 'Resultado:',           'en': 'Result:'},
    'shared.table_title_afd2':          {'es': 'Tabla de Transiciones AFD₂:',
                                         'en': 'Transition Table DFA₂:'},
    'shared.gen_table':                 {'es': '📋 Generar Tabla de Transiciones',
                                         'en': '📋 Generate Transition Table'},
    'shared.finals_placeholder':        {'es': '(genere la tabla primero)',
                                         'en': '(generate the table first)'},
    'shared.table_placeholder':         {'es': 'Ingrese estados y alfabeto, luego genere la tabla',
                                         'en': 'Enter states and alphabet, then generate the table'},

    # ── AFN panel labels ──────────────────────────────────────────
    'afn.ops.title':        {'es': 'Operaciones sobre AFN/AFN-λ:',
                             'en': 'NFA/NFA-λ Operations:'},
    'afn.ops.btn_kleene':   {'es': 'A* (Kleene)',    'en': 'A* (Kleene)'},
    'afn.ops.btn_positive': {'es': 'A+ (Positiva)',  'en': 'A+ (Positive)'},
    'afn.ops.btn_usar':     {'es': '✅ Usar como actual', 'en': '✅ Use as current'},

    # ── Conversion chain ──────────────────────────────────────────
    'afn.chain.btn_prev':   {'es': '◀ Anterior',    'en': '◀ Previous'},
    'afn.chain.step_label': {'es': 'Paso: —',        'en': 'Step: —'},
    'afn.chain.step_fmt':   {'es': 'Paso: {n}',      'en': 'Step: {n}'},

    # ── Regex panel LabelFrame titles ─────────────────────────────
    'regex.er_frame':       {'es': ' ER → AFN-λ (Construcción de Thompson) ',
                             'en': ' RE → NFA-λ (Thompson Construction) '},
    'regex.afd_frame':      {'es': ' AFD → ER (Lema de Arden) ',
                             'en': " DFA → RE (Arden's Lemma) "},

    # ── Properties panel button labels ────────────────────────────
    'prop.btn.empty':       {'es': '🔍 ¿Lenguaje vacío?',         'en': '🔍 Empty language?'},
    'prop.btn.infinite':    {'es': '🔍 ¿Lenguaje infinito?',      'en': '🔍 Infinite language?'},
    'prop.btn.finite':      {'es': '🔍 ¿Lenguaje finito?',        'en': '🔍 Finite language?'},
    'prop.btn.shortest':    {'es': '🔍 Cadena más corta aceptada','en': '🔍 Shortest accepted string'},
    'prop.btn.accessible':  {'es': '🔍 Estados accesibles',       'en': '🔍 Accessible states'},
    'prop.btn.productive':  {'es': '🔍 Estados productivos',      'en': '🔍 Productive states'},
    'prop.btn.useful':      {'es': '🔍 Estados útiles',           'en': '🔍 Useful states'},

    # ── Sidebar finals placeholder ─────────────────────────────────
    'sidebar.no_states_ph': {'es': '(agregue estados primero)',
                             'en': '(add states first)'},

}


# ─────────────────────────────────────────────────────────────────
# Language manager
# ─────────────────────────────────────────────────────────────────

class LanguageManager:
    """Manages the current language and notifies listeners on change."""

    def __init__(self, default: str = 'es'):
        self._lang = default
        self._listeners: List[Callable] = []

    @property
    def current(self) -> str:
        return self._lang

    def set(self, lang: str) -> None:
        if lang not in ('es', 'en'):
            raise ValueError(f"Unsupported language: {lang}")
        if lang != self._lang:
            self._lang = lang
            for cb in self._listeners:
                try:
                    cb()
                except Exception:
                    pass

    def on_change(self, callback: Callable) -> None:
        """Register a callback to be called when the language changes."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def translate(self, key: str, **kwargs) -> str:
        """
        Return the translation for *key* in the current language.
        Keyword arguments are used for simple format substitutions.
        Missing keys fall back to the key itself.
        """
        entry = _TRANSLATIONS.get(key)
        if entry is None:
            return key
        text = entry.get(self._lang, entry.get('es', key))
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, IndexError):
                pass
        return text


# Singleton instances (imported by all modules)
lang = LanguageManager(default='es')


def t(key: str, **kwargs) -> str:
    """Shorthand for lang.translate(key, **kwargs)."""
    return lang.translate(key, **kwargs)


def tipo_display(tipo_interno: str) -> str:
    """
    Translate an internal automaton type code ('AFD','AFN','AFN-λ')
    to the display label for the current language.
    """
    mapping = {
        'AFD':   'type.afd',
        'AFN':   'type.afn',
        'AFN-λ': 'type.afnl',
    }
    key = mapping.get(tipo_interno)
    return t(key) if key else tipo_interno
