"""
HelpDialog — Diálogo de ayuda y tutorial.
Muestra guía de uso, atajos de teclado y referencia teórica.
"""

from ui.i18n import lang, t
import tkinter as tk
from tkinter import ttk
from ui.theme import theme


class HelpDialog(tk.Toplevel):
    """Diálogo de ayuda con tutorial, atajos y referencia teórica."""

    def __init__(self, parent):
        super().__init__(parent)
        self.theme = theme
        self.title(t('help.title'))
        self.geometry("640x520")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        c = self.theme.colors
        self.configure(bg=c['bg_main'])

        self._build_ui()
        self.theme.on_change(self._on_theme_change)

    def _build_ui(self):
        c = self.theme.colors

        # Notebook con pestañas
        style = ttk.Style(self)
        style.configure('Help.TNotebook', background=c['bg_main'])
        style.configure('Help.TNotebook.Tab', padding=[12, 4])

        self.notebook = ttk.Notebook(self, style='Help.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Pestaña 1: Guía de uso
        self._build_guide_tab()

        # Pestaña 2: Atajos
        self._build_shortcuts_tab()

        # Pestaña 3: Referencia teórica
        self._build_reference_tab()

        # Botón cerrar
        btn_frame = tk.Frame(self, bg=c['bg_main'])
        btn_frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        self.btn_cerrar = tk.Button(
            btn_frame, text=t('help.btn_close'), command=self.destroy,
            bg=c['accent'], fg=c['text_on_accent'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            relief='flat', font=('Segoe UI', 10, 'bold'),
            padx=20, pady=4, cursor='hand2'
        )
        self.btn_cerrar.pack(side=tk.RIGHT)

    def _build_guide_tab(self):
        c = self.theme.colors

        frame = tk.Frame(self.notebook, bg=c['bg_panel'])
        self.notebook.add(frame, text=t('help.tab_guide'))

        text = tk.Text(
            frame, wrap=tk.WORD, bg=c['bg_input'], fg=c['text'],
            font=('Segoe UI', 10), relief='flat', padx=12, pady=10
        )
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(fill=tk.BOTH, expand=True)

        text.tag_configure('h1', font=('Segoe UI', 14, 'bold'), foreground=c['accent'])
        text.tag_configure('h2', font=('Segoe UI', 11, 'bold'), foreground=c['accent'])
        text.tag_configure('bold', font=('Segoe UI', 10, 'bold'))

        guide_text = """AutomaTEC-Lab — Guía de Uso

"""
        text.insert(tk.END, guide_text, 'h1')

        sections = [
            ("Primeros pasos\n", 'h2',
             "1. Selecciona el tipo de autómata (AFD, AFN o AFN-λ) desde la barra lateral.\n"
             "2. Define los estados, alfabeto, estado inicial y estados finales.\n"
             "3. Completa la tabla de transiciones.\n"
             "4. El diagrama se actualizará automáticamente.\n\n"),

            ("Procesar cadenas\n", 'h2',
             "1. Ve a la pestaña 'Procesar'.\n"
             "2. Ingresa una cadena en el campo de texto.\n"
             "3. Presiona 'Procesar' o Enter para verificar si la cadena es aceptada.\n"
             "4. Activa 'Paso a Paso' para ver la traza de ejecución.\n\n"),

            ("Conversiones\n", 'h2',
             "• AFN/AFN-λ → AFD: Pestaña 'Subconjuntos' (construcción de subconjuntos).\n"
             "• AFN-λ → AFN: Pestaña 'Eliminar λ' (eliminación de ε-transiciones).\n"
             "• AFN-λ → AFN → AFD → AFD mín: Pestaña 'Conversión' (cadena completa).\n"
             "• ER → AFN-λ: Pestaña 'Expr. Regulares' (construcción de Thompson).\n"
             "• AFD → ER: Pestaña 'Expr. Regulares' (lema de Arden).\n\n"),

            ("Operaciones\n", 'h2',
             "• AFD: Unión, intersección, diferencia, complemento — pestaña 'Operaciones'.\n"
             "• AFD: Minimización — pestaña 'Minimizar'.\n"
             "• AFD: Equivalencia — pestaña 'Equivalencia'.\n"
             "• AFN: Kleene (A*), Positiva (A+), Reverso (Aᴿ) — pestaña 'Operaciones AFN'.\n\n"),

            ("Propiedades\n", 'h2',
             "En la pestaña 'Propiedades' puedes verificar:\n"
             "• Lenguaje vacío, finito, infinito\n"
             "• Cadena más corta\n"
             "• Estados accesibles, productivos, útiles\n"
             "• Completitud del AFD\n\n"),

            ("Importar/Exportar\n", 'h2',
             "• Archivo → Abrir: Cargar autómata desde archivo JSON.\n"
             "• Archivo → Guardar/Guardar como: Exportar autómata a JSON.\n"
             "• El diagrama se puede guardar como PNG, SVG, PDF o EPS.\n\n"),

            ("Ejemplos\n", 'h2',
             "Usa Archivo → Ejemplos para cargar autómatas predefinidos:\n"
             "• AFD: Termina en 1, Par de ceros, (a|b)*abb\n"
             "• AFN: Contiene 01\n"
             "• AFN-λ: a*b+\n"
             "• AFD no mínimo (para minimización)\n"
             "• AFDs equivalentes\n"),
        ]

        for title, tag, content in sections:
            text.insert(tk.END, title, tag)
            text.insert(tk.END, content)

        text.configure(state=tk.DISABLED)

    def _build_shortcuts_tab(self):
        c = self.theme.colors

        frame = tk.Frame(self.notebook, bg=c['bg_panel'])
        self.notebook.add(frame, text=t('help.tab_shortcuts'))

        text = tk.Text(
            frame, wrap=tk.WORD, bg=c['bg_input'], fg=c['text'],
            font=('Consolas', 10), relief='flat', padx=12, pady=10
        )
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(fill=tk.BOTH, expand=True)

        text.tag_configure('h1', font=('Segoe UI', 14, 'bold'), foreground=c['accent'])
        text.tag_configure('key', font=('Consolas', 10, 'bold'), foreground=c['yellow'])
        text.tag_configure('desc', foreground=c['text_secondary'])

        shortcuts = [
            ("Atajos de Teclado\n\n", 'h1'),
            ("Ctrl+N       ", 'key', "Nuevo autómata\n", 'desc'),
            ("Ctrl+O       ", 'key', "Abrir archivo JSON\n", 'desc'),
            ("Ctrl+S       ", 'key', "Guardar autómata\n", 'desc'),
            ("Ctrl+T       ", 'key', "Alternar tema claro/oscuro\n", 'desc'),
            ("Ctrl+P       ", 'key', "Procesar cadena\n", 'desc'),
            ("F1           ", 'key', "Mostrar ayuda\n", 'desc'),
            ("Ctrl+Q       ", 'key', "Salir\n", 'desc'),
            ("\nNavegación del Canvas\n\n", 'h1'),
            ("Rueda mouse  ", 'key', "Zoom in/out\n", 'desc'),
            ("Click+drag   ", 'key', "Desplazar canvas\n", 'desc'),
            ("\nTabla de Transiciones\n\n", 'h1'),
            ("Tab          ", 'key', "Siguiente celda\n", 'desc'),
            ("Enter        ", 'key', "Confirmar cambio de celda\n", 'desc'),
        ]

        for item in shortcuts:
            if len(item) == 2:
                text.insert(tk.END, item[0], item[1])
            elif len(item) == 4:
                text.insert(tk.END, item[0], item[1])
                text.insert(tk.END, item[2], item[3])

        text.configure(state=tk.DISABLED)

    def _build_reference_tab(self):
        c = self.theme.colors

        frame = tk.Frame(self.notebook, bg=c['bg_panel'])
        self.notebook.add(frame, text=t('help.tab_reference'))

        text = tk.Text(
            frame, wrap=tk.WORD, bg=c['bg_input'], fg=c['text'],
            font=('Segoe UI', 10), relief='flat', padx=12, pady=10
        )
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(fill=tk.BOTH, expand=True)

        text.tag_configure('h1', font=('Segoe UI', 14, 'bold'), foreground=c['accent'])
        text.tag_configure('h2', font=('Segoe UI', 11, 'bold'), foreground=c['accent'])
        text.tag_configure('math', font=('Consolas', 10), foreground=c['yellow'])

        reference = [
            ("Referencia Teórica\n\n", 'h1'),

            ("Autómata Finito Determinista (AFD)\n", 'h2',
             "M = (Q, Σ, δ, q₀, F)\n"
             "  Q  = conjunto finito de estados\n"
             "  Σ  = alfabeto de entrada\n"
             "  δ  = Q × Σ → Q (función de transición)\n"
             "  q₀ = estado inicial\n"
             "  F  = conjunto de estados finales\n\n"),

            ("Autómata Finito No Determinista (AFN)\n", 'h2',
             "M = (Q, Σ, δ, q₀, F)\n"
             "  δ  = Q × Σ → 2^Q (función no determinista)\n"
             "  Puede tener múltiples transiciones para (q, a).\n\n"),

            ("AFN con λ-transiciones (AFN-λ)\n", 'h2',
             "  δ  = Q × (Σ ∪ {λ}) → 2^Q\n"
             "  λ-transiciones no consumen entrada.\n"
             "  ε-Clausura: CL_ε(q) = {q} ∪ {q' : ∃ camino λ de q a q'}\n\n"),

            ("Construcción de Subconjuntos\n", 'h2',
             "Teorema: Para todo AFN existe un AFD equivalente.\n"
             "Algoritmo:\n"
             "  1. Estado inicial AFD = CL_ε({q₀}) o {q₀}\n"
             "  2. Para cada T y a ∈ Σ: T' = CL_ε(δ(T, a))\n"
             "  3. Finales = {T : T ∩ F ≠ ∅}\n\n"),

            ("Eliminación de λ-transiciones\n", 'h2',
             "  1. δ'(q, a) = CL_ε(∪{δ(q', a) : q' ∈ CL_ε(q)})\n"
             "  2. F' = {q : CL_ε(q) ∩ F ≠ ∅}\n"
             "  3. Eliminar todas las transiciones λ.\n\n"),

            ("Minimización de AFD\n", 'h2',
             "Algoritmo de tabla de distinguibilidad:\n"
             "  1. Marcar pares (final, no-final).\n"
             "  2. Para cada par (p, q) y a ∈ Σ:\n"
             "     Si (δ(p,a), δ(q,a)) está marcado → marcar (p,q).\n"
             "  3. Los pares no marcados son equivalentes.\n\n"),

            ("Expresiones Regulares\n", 'h2',
             "Operadores: | (unión), . (concat), * (Kleene), + (positiva), ? (opcional)\n"
             "Precedencia: * + ? > . > |\n\n"
             "Construcción de Thompson: ER → AFN-λ\n"
             "  Cada operador se traduce a un fragmento AFN-λ con ε-transiciones.\n\n"
             "Lema de Arden: X = AX ∪ B ⟹ X = A*B\n"
             "  Se usa para AFD → ER por eliminación de estados.\n"),

            ("Equivalencia de AFDs\n", 'h2',
             "Producto cartesiano M₁ × M₂:\n"
             "  L(M₁) = L(M₂) ↔ no hay estado (f₁, nf₂) o (nf₁, f₂) accesible.\n\n"),

            ("Operaciones Booleanas\n", 'h2',
             "  Unión: L₁ ∪ L₂ — producto con finales (f₁ ∨ f₂)\n"
             "  Intersección: L₁ ∩ L₂ — producto con finales (f₁ ∧ f₂)\n"
             "  Diferencia: L₁ \\ L₂ — producto con finales (f₁ ∧ ¬f₂)\n"
             "  Complemento: Σ* \\ L — invertir estados finales.\n"),
        ]

        for item in reference:
            if len(item) == 2:
                text.insert(tk.END, item[0], item[1])
            elif len(item) == 3:
                text.insert(tk.END, item[0], item[1])
                text.insert(tk.END, item[2])

        text.configure(state=tk.DISABLED)

    def _on_theme_change(self):
        c = self.theme.colors
        self.configure(bg=c['bg_main'])
        self.btn_cerrar.configure(bg=c['accent'], fg=c['text_on_accent'])
