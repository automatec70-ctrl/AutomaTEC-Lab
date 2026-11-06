#!/usr/bin/env python3
"""TablaTransiciones — Tabla de transiciones editable tipo grid.
Filas = estados, Columnas = símbolos del alfabeto.
Para AFD: un estado por celda.
Para AFN/AFN-λ: múltiples estados separados por coma."""

from ui.i18n import lang, t
import tkinter as tk
from tkinter import ttk
from typing import Dict, Set, Optional


class TablaTransiciones(tk.Frame):
    """Tabla de transiciones editable tipo grid."""

    def __init__(self, parent, theme_ref, app_ref=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme_ref
        self.app = app_ref
        self.entries = {}  # (estado, simbolo) -> Entry widget
        self.tipo = 'AFD'
        self._estado_inicial = ''
        self._estados_finales = set()
        self._setup_ui()
        self.theme.on_change(self._on_theme_change)

    def _setup_ui(self):
        """Crea el contenedor base para la tabla"""
        c = self.theme.colors
        self.configure(bg=c['bg_panel'])

        # Canvas con scroll para la tabla
        self._outer_frame = tk.Frame(self, bg=c['bg_panel'])
        self._outer_frame.pack(fill='both', expand=True)

        self._canvas = tk.Canvas(self._outer_frame, bg=c['bg_panel'],
                                  highlightthickness=0)
        v_scroll = ttk.Scrollbar(self._outer_frame, orient='vertical',
                                  command=self._canvas.yview)
        h_scroll = ttk.Scrollbar(self, orient='horizontal',
                                  command=self._canvas.xview)

        self._canvas.configure(yscrollcommand=v_scroll.set,
                                xscrollcommand=h_scroll.set)

        v_scroll.pack(side='right', fill='y')
        self._canvas.pack(side='left', fill='both', expand=True)
        h_scroll.pack(side='bottom', fill='x')

        self._table_frame = tk.Frame(self._canvas, bg=c['bg_panel'])
        self._canvas_window = self._canvas.create_window((0, 0), window=self._table_frame,
                                                          anchor='nw')

        self._table_frame.bind('<Configure>', self._on_table_configure)

        # Placeholder
        self._placeholder = tk.Label(
            self._table_frame,
            text='Define estados y alfabeto para crear la tabla',
            bg=c['bg_panel'], fg=c['text_secondary'],
            font=('Segoe UI', 11)
        )
        self._placeholder.grid(row=0, column=0, padx=20, pady=20)

    def _on_table_configure(self, event=None):
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))

    def configurar(self, estados, alfabeto, estado_inicial, estados_finales,
                   delta, tipo='AFD'):
        """Construye/reconstruye la tabla con los datos del autómata"""
        self.tipo = tipo
        self._estado_inicial = estado_inicial
        self._estados_finales = set(estados_finales)
        self.entries = {}

        # Limpiar tabla existente
        for widget in self._table_frame.winfo_children():
            widget.destroy()

        c = self.theme.colors

        if not estados or not alfabeto:
            self._placeholder = tk.Label(
                self._table_frame,
                text='Define estados y alfabeto para crear la tabla',
                bg=c['bg_panel'], fg=c['text_secondary'],
                font=('Segoe UI', 11)
            )
            self._placeholder.grid(row=0, column=0, padx=20, pady=20)
            return

        estados_list = sorted(estados)
        alfabeto_list = sorted(alfabeto)

        # Para AFN-λ, agregar columna λ
        columnas = alfabeto_list[:]
        if tipo == 'AFN-λ':
            columnas.append('λ')

        # ── Encabezados ──────────────────────────────────────────
        # Esquina superior izquierda
        hdr = tk.Label(self._table_frame, text='δ', bg=c['bg_surface'],
                       fg=c['text'], font=('Segoe UI', 10, 'bold'),
                       padx=8, pady=4, relief='flat')
        hdr.grid(row=0, column=0, sticky='nsew', padx=1, pady=1)

        # Encabezados de símbolos
        for j, simbolo in enumerate(columnas):
            lbl_text = 'λ' if simbolo == 'λ' else simbolo
            lbl = tk.Label(self._table_frame, text=lbl_text,
                           bg=c['bg_surface'], fg=c['text'],
                           font=('Segoe UI', 10, 'bold'),
                           padx=10, pady=4, relief='flat')
            lbl.grid(row=0, column=j + 1, sticky='nsew', padx=1, pady=1)

        # ── Filas de estados ─────────────────────────────────────
        for i, estado in enumerate(estados_list):
            # Etiqueta del estado
            prefix = ''
            if estado == estado_inicial:
                prefix += '→ '
            if estado in estados_finales:
                prefix += '* '
            label_text = f'{prefix}{estado}'

            lbl_bg = '#3A2A5A' if estado in estados_finales else c['bg_surface']
            lbl_fg = c['accent'] if estado in estados_finales else c['text']

            row_label = tk.Label(self._table_frame, text=label_text,
                                 bg=lbl_bg, fg=lbl_fg,
                                 font=('Segoe UI', 10, 'bold'),
                                 padx=8, pady=4, relief='flat', anchor='e')
            row_label.grid(row=i + 1, column=0, sticky='nsew', padx=1, pady=1)

            # Celdas de transiciones
            for j, simbolo in enumerate(columnas):
                # Obtener valor de delta
                val = ''
                if estado in delta:
                    dest = delta[estado].get(simbolo)
                    if dest is not None:
                        if isinstance(dest, set):
                            val = ', '.join(sorted(dest))
                        elif isinstance(dest, list):
                            val = ', '.join(sorted(dest))
                        elif isinstance(dest, str):
                            val = dest
                        else:
                            val = str(dest)

                entry = tk.Entry(self._table_frame, width=10,
                                 bg=c['bg_panel'], fg=c['text'],
                                 insertbackground=c['text'],
                                 selectbackground=c['accent'],
                                 selectforeground=c['text_on_accent'],
                                 font=('Segoe UI', 10),
                                 relief='flat', bd=0,
                                 highlightthickness=1,
                                 highlightcolor=c['accent'],
                                 highlightbackground=c['border'])
                entry.insert(0, val)
                entry.grid(row=i + 1, column=j + 1, sticky='nsew',
                          padx=1, pady=1, ipadx=4, ipady=2)

                # Guardar referencia
                self.entries[(estado, simbolo)] = entry

                # Bind para cambios
                entry.bind('<FocusOut>',
                          lambda e, est=estado, sim=simbolo: self._on_cell_change(est, sim))
                entry.bind('<Return>',
                          lambda e, est=estado, sim=simbolo: self._on_cell_change(est, sim))

        # Configurar expansión de columnas
        for j in range(len(columnas) + 1):
            self._table_frame.columnconfigure(j, weight=1)

    def get_delta(self) -> dict:
        """Extrae el diccionario de transiciones de las entradas de la tabla"""
        delta = {}
        for (estado, simbolo), entry in self.entries.items():
            val = entry.get().strip()
            if not val:
                continue

            if estado not in delta:
                delta[estado] = {}

            if self.tipo == 'AFD':
                # AFD: un solo estado destino
                destinos = [d.strip() for d in val.split(',') if d.strip()]
                if destinos:
                    delta[estado][simbolo] = destinos[0]
            else:
                # AFN/AFN-λ: multiples estados separados por coma — store as set (required by AFN.delta)
                destinos = set(d.strip() for d in val.split(',') if d.strip())
                if destinos:
                    delta[estado][simbolo] = destinos

        return delta

    def set_delta(self, delta):
        """Llena la tabla desde un diccionario de transiciones"""
        for (estado, simbolo), entry in self.entries.items():
            entry.delete(0, tk.END)
            if estado in delta:
                dest = delta[estado].get(simbolo)
                if dest is not None:
                    if isinstance(dest, set):
                        entry.insert(0, ', '.join(sorted(dest)))
                    elif isinstance(dest, list):
                        entry.insert(0, ', '.join(sorted(dest)))
                    elif isinstance(dest, str):
                        entry.insert(0, dest)
                    else:
                        entry.insert(0, str(dest))

    def _on_cell_change(self, estado, simbolo, event=None):
        """Maneja la edicion de una celda: actualiza el automata y el canvas."""
        try:
            entry = self.entries.get((estado, simbolo))
            val = entry.get().strip() if entry else ''
            c = self.theme.colors

            if self.app and hasattr(self.app, 'current_automaton'):
                auto = self.app.current_automaton

                # Validar que el estado destino esté declarado (solo AFD y AFN)
                if val and self.tipo != 'AFN-λ':
                    destinos = [d.strip() for d in val.split(',') if d.strip()]
                    estados_validos = auto.estados if hasattr(auto, 'estados') else set()
                    invalidos = [d for d in destinos if d not in estados_validos]
                    if invalidos:
                        if entry:
                            entry.configure(highlightbackground='#CC3333',
                                            highlightcolor='#CC3333')
                        if hasattr(self.app, 'add_log'):
                            self.app.add_log(
                                f'Transición inválida: δ({estado}, {simbolo}) → '
                                f'{", ".join(invalidos)} no declarado(s)', 'error')
                        return
                elif val and self.tipo == 'AFN-λ':
                    destinos = [d.strip() for d in val.split(',') if d.strip()]
                    estados_validos = auto.estados if hasattr(auto, 'estados') else set()
                    invalidos = [d for d in destinos if d not in estados_validos]
                    if invalidos:
                        if entry:
                            entry.configure(highlightbackground='#CC3333',
                                            highlightcolor='#CC3333')
                        if hasattr(self.app, 'add_log'):
                            self.app.add_log(
                                f'Transición inválida: δ({estado}, {simbolo}) → '
                                f'{", ".join(invalidos)} no declarado(s)', 'error')
                        return

                # Restaurar color normal si el valor es válido o vacío
                if entry:
                    entry.configure(highlightbackground=c['border'],
                                    highlightcolor=c['accent'])

                # Actualizar el delta del automata
                new_delta = self.get_delta()
                auto.delta = new_delta
                # Redibujar el canvas
                if hasattr(self.app, 'canvas_widget'):
                    self.app.canvas_widget.dibujar_automata(auto, self.app.current_tipo)
                # Actualizar barra de estado
                if hasattr(self.app, '_update_status_bar'):
                    self.app._update_status_bar()
                # Log
                if hasattr(self.app, 'add_log'):
                    self.app.add_log(f'Transicion actualizada: delta({estado}, {simbolo})', 'info')
        except Exception:
            pass

    def _on_theme_change(self):
        """Actualiza colores del tema cuando cambia"""
        self.refresh_theme()

    def refresh_theme(self):
        """Actualiza colores del tema"""
        c = self.theme.colors
        self.configure(bg=c['bg_panel'])
        self._canvas.configure(bg=c['bg_panel'])
        self._outer_frame.configure(bg=c['bg_panel'])
        self._table_frame.configure(bg=c['bg_panel'])

        # Actualizar entries
        for (estado, simbolo), entry in self.entries.items():
            entry.configure(
                bg=c['bg_panel'], fg=c['text'],
                insertbackground=c['text'],
                selectbackground=c['accent'],
                selectforeground=c['text_on_accent'],
                highlightcolor=c['accent'],
                highlightbackground=c['border'],
            )

    def refresh_lang(self):
        """Update placeholder text if it still exists."""
        try:
            if hasattr(self, '_placeholder') and self._placeholder.winfo_exists():
                self._placeholder.configure(text=t('table.placeholder'))
        except Exception:
            pass
