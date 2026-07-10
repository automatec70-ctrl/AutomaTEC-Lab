"""
ExamplesDialog — Diálogo para cargar ejemplos predefinidos.
Muestra lista de ejemplos con nombre, tipo y descripción.
"""

import tkinter as tk
from tkinter import ttk
from core.examples import ALL_EXAMPLES
from ui.i18n import lang, t
from core.afd import AFD
from core.afn import AFN
from core.afn_lambda import AFNLambda
from ui.theme import theme


class ExamplesDialog(tk.Toplevel):
    """Diálogo para seleccionar y cargar ejemplos predefinidos."""

    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.theme = theme
        self.app = app_ref
        self.title(t('examples.title'))
        self.geometry("550x420")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        c = self.theme.colors
        self.configure(bg=c['bg_main'])

        self._build_ui()
        self.theme.on_change(self._on_theme_change)

    def _build_ui(self):
        c = self.theme.colors

        # Título
        tk.Label(
            self, text=t('examples.heading'),
            bg=c['bg_main'], fg=c['accent'],
            font=('Segoe UI', 13, 'bold')
        ).pack(anchor='w', padx=12, pady=(10, 4))

        tk.Label(
            self, text=t('examples.subtitle'),
            bg=c['bg_main'], fg=c['text_secondary'],
            font=('Segoe UI', 9)
        ).pack(anchor='w', padx=12, pady=(0, 6))

        # Lista de ejemplos
        list_frame = tk.Frame(self, bg=c['bg_panel'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        # Treeview
        columns = ('nombre', 'tipo', 'descripcion')
        self.tree = ttk.Treeview(
            list_frame, columns=columns, show='headings', height=10
        )

        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('tipo', text='Tipo')
        self.tree.heading('descripcion', text='Descripción')

        self.tree.column('nombre', width=160, minwidth=120)
        self.tree.column('tipo', width=70, minwidth=60)
        self.tree.column('descripcion', width=280, minwidth=200)

        scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Llenar la lista
        for i, ejemplo in enumerate(ALL_EXAMPLES):
            tipo_display = ejemplo['tipo']
            if tipo_display == 'AFNLambda':
                tipo_display = 'AFN-λ'
            elif tipo_display == 'AFD_par':
                tipo_display = 'AFD×2'

            self.tree.insert('', tk.END, iid=str(i), values=(
                ejemplo['nombre'],
                tipo_display,
                ejemplo['descripcion']
            ))

        # Doble click para cargar
        self.tree.bind('<Double-1>', lambda e: self._cargar_ejemplo())

        # Botones
        btn_frame = tk.Frame(self, bg=c['bg_main'])
        btn_frame.pack(fill=tk.X, padx=12, pady=(6, 10))

        self.btn_cargar = tk.Button(
            btn_frame, text=t('examples.btn_load'),
            command=self._cargar_ejemplo,
            bg=c['accent'], fg=c['text_on_accent'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            relief='flat', font=('Segoe UI', 10, 'bold'),
            padx=16, pady=4, cursor='hand2'
        )
        self.btn_cargar.pack(side=tk.LEFT, padx=4)

        self.btn_cerrar = tk.Button(
            btn_frame, text=t('examples.btn_close'), command=self.destroy,
            bg=c['bg_surface'], fg=c['text'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            relief='flat', font=('Segoe UI', 10),
            padx=16, pady=4, cursor='hand2'
        )
        self.btn_cerrar.pack(side=tk.RIGHT, padx=4)

    def _cargar_ejemplo(self):
        """Carga el ejemplo seleccionado."""
        seleccion = self.tree.selection()
        if not seleccion:
            return

        idx = int(seleccion[0])
        if idx < 0 or idx >= len(ALL_EXAMPLES):
            return

        ejemplo = ALL_EXAMPLES[idx]
        funcion = ejemplo['funcion']
        tipo = ejemplo['tipo']

        try:
            resultado = funcion()

            # Caso especial: par de AFDs equivalentes
            if tipo == 'AFD_par':
                # Cargar el primer AFD del par
                afd1 = resultado[0]
                self.app.current_automaton = afd1
                self.app.current_tipo = 'AFD'
                self.app.add_log(f"Ejemplo cargado: {ejemplo['nombre']} (primer AFD del par)", "success")
            else:
                self.app.current_automaton = resultado
                if tipo == 'AFD':
                    self.app.current_tipo = 'AFD'
                elif tipo == 'AFN':
                    self.app.current_tipo = 'AFN'
                elif tipo == 'AFNLambda':
                    self.app.current_tipo = 'AFN-λ'
                self.app.add_log(f"Ejemplo cargado: {ejemplo['nombre']}", "success")

            self.app.on_automaton_changed()
            self.destroy()

        except Exception as e:
            self.app.add_log(f"Error al cargar ejemplo: {str(e)}", "error")

    def _on_theme_change(self):
        c = self.theme.colors
        self.configure(bg=c['bg_main'])
        self.btn_cargar.configure(bg=c['accent'], fg=c['text_on_accent'])
        self.btn_cerrar.configure(bg=c['bg_surface'], fg=c['text'])
