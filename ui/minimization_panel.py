"""
MinimizationPanel — Panel para minimización de AFD.

Contiene:
  - [Minimizar Todo] button: ejecuta la minimización completa
  - [Minimizar Paso a Paso] button: avanza un paso del algoritmo
  - Tabla de distinguibilidad: grilla con ✗ (distinguible, rojo) o ≡ (equivalente, verde)
  - Clases de equivalencia: muestra grupos de estados
  - Resultado: AFD mínimo con número de estados
  - Mensaje "El AFD ya es mínimo" cuando corresponde
  - Opción de ver el AFD minimizado en el canvas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict

from ui.theme import theme
from ui.i18n import lang, t
from core.afd import AFD


class MinimizationPanel(tk.Frame):
    """Panel para minimización de AFD por tabla de distinguibilidad."""

    def __init__(self, parent, app_ref, **kwargs):
        c = theme.colors
        super().__init__(parent, bg=c['bg_panel'], **kwargs)
        self.app = app_ref

        self._pasos: List[Dict] = []
        self._paso_actual: int = -1
        self._resultado_completo: Optional[Dict] = None
        self._afd_minimo: Optional[AFD] = None

        self._build_ui()
        theme.on_change(self._on_theme_change)

    # ── Construcción de la UI ────────────────────────────────────

    def _build_ui(self):
        c = theme.colors

        # Título
        self._title = tk.Label(self, text=t('min.title'), bg=c['bg_panel'],
                               fg=c['accent'], font=('Segoe UI', 12, 'bold'))
        self._title.pack(anchor='w', padx=12, pady=(10, 4))

        # Botones
        self._btn_frame = tk.Frame(self, bg=c['bg_panel'])
        self._btn_frame.pack(fill=tk.X, padx=12, pady=(0, 4))

        self._btn_minimizar = tk.Button(
            self._btn_frame, text=t('min.btn_all'),
            command=self._minimizar_todo,
            bg=c['accent'], fg=c['text_on_accent'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            font=('Segoe UI', 9, 'bold'), relief='flat', cursor='hand2', padx=10
        )
        self._btn_minimizar.pack(side=tk.LEFT, padx=(0, 4))

        self._btn_paso = tk.Button(
            self._btn_frame, text=t('min.btn_step'),
            command=self._minimizar_paso,
            bg=c['bg_surface'], fg=c['text'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            font=('Segoe UI', 9), relief='flat', cursor='hand2', padx=10
        )
        self._btn_paso.pack(side=tk.LEFT, padx=(0, 4))

        self._btn_reiniciar = tk.Button(
            self._btn_frame, text=t('min.btn_reset'), command=self._reiniciar,
            bg=c['bg_surface'], fg=c['text'], activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'], font=('Segoe UI', 9),
            relief='flat', cursor='hand2', padx=10
        )
        self._btn_reiniciar.pack(side=tk.LEFT)

        # Descripción del paso actual
        self._desc_label = tk.Label(
            self, text='', bg=c['bg_panel'], fg=c['text_secondary'],
            font=('Segoe UI', 9, 'italic'), wraplength=500, justify='left'
        )
        self._desc_label.pack(anchor='w', padx=12, pady=(0, 4))

        # Scrollable content area
        self._content_outer = tk.Frame(self, bg=c['bg_panel'])
        self._content_outer.pack(fill=tk.BOTH, expand=True)

        self._content_canvas = tk.Canvas(self._content_outer, bg=c['bg_panel'],
                                          highlightthickness=0)
        self._content_scrollbar = ttk.Scrollbar(
            self._content_outer, orient=tk.VERTICAL,
            command=self._content_canvas.yview)
        self._content_inner = tk.Frame(self._content_canvas, bg=c['bg_panel'])

        self._content_inner.bind(
            '<Configure>',
            lambda e: self._content_canvas.configure(
                scrollregion=self._content_canvas.bbox('all')))
        self._cw = self._content_canvas.create_window(
            (0, 0), window=self._content_inner, anchor='nw')
        self._content_canvas.configure(
            yscrollcommand=self._content_scrollbar.set)

        self._content_canvas.bind('<Configure>',
            lambda e: self._content_canvas.itemconfig(self._cw, width=e.width))
        self._content_canvas.bind('<Enter>', lambda e: self._content_canvas.bind_all(
            '<MouseWheel>',
            lambda ev: self._content_canvas.yview_scroll(
                int(-1 * (ev.delta / 120)), 'units')))
        self._content_canvas.bind('<Leave>', lambda e: self._content_canvas.unbind_all(
            '<MouseWheel>'))

        self._content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._content_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = self._content_inner

        # Tabla de distinguibilidad
        self._table_section_label = tk.Label(
            inner, text=t('min.table_title'), bg=c['bg_panel'],
            fg=c['text'], font=('Segoe UI', 10, 'bold'))
        self._table_section_label.pack(anchor='w', pady=(4, 2))

        self._table_frame = tk.Frame(inner, bg=c['bg_panel'])
        self._table_frame.pack(fill=tk.X, pady=(0, 8))

        self._table_placeholder = tk.Label(
            self._table_frame,
            text=t('min.table_placeholder'),
            bg=c['bg_panel'], fg=c['text_secondary'],
            font=('Segoe UI', 9, 'italic'))
        self._table_placeholder.pack(anchor='w')
        self._active_table_placeholder = self._table_placeholder

        # Clases de equivalencia
        self._classes_section_label = tk.Label(
            inner, text=t('min.classes_title'), bg=c['bg_panel'],
            fg=c['text'], font=('Segoe UI', 10, 'bold'))
        self._classes_section_label.pack(anchor='w', pady=(4, 2))

        self._classes_frame = tk.Frame(inner, bg=c['bg_panel'])
        self._classes_frame.pack(fill=tk.X, pady=(0, 8))

        self._classes_placeholder = tk.Label(
            self._classes_frame,
            text=t('min.classes_placeholder'),
            bg=c['bg_panel'], fg=c['text_secondary'],
            font=('Segoe UI', 9, 'italic'))
        self._classes_placeholder.pack(anchor='w')
        self._active_classes_placeholder = self._classes_placeholder

        # Resultado
        self._result_frame = tk.Frame(inner, bg=c['bg_panel'])
        self._result_frame.pack(fill=tk.X, pady=(0, 4))

        self._result_label = tk.Label(
            self._result_frame, text='', bg=c['bg_panel'],
            font=('Segoe UI', 11, 'bold'), wraplength=500, justify='left')
        self._result_label.pack(anchor='w')

        # Botón ver AFD mínimo
        self._btn_ver_minimo = tk.Button(
            inner, text=t('min.btn_view'),
            command=self._ver_afd_minimo,
            bg=c['green'], fg='#FFFFFF', activebackground='#059669',
            activeforeground='#FFFFFF', font=('Segoe UI', 9, 'bold'),
            relief='flat', cursor='hand2', padx=10)

    # ── Lógica de minimización ───────────────────────────────────

    def _get_afd(self) -> Optional[AFD]:
        automaton = self.app.current_automaton
        if not automaton:
            messagebox.showwarning(t('dlg.no_automaton'), t('msg.no_automaton'))
            return None
        if not isinstance(automaton, AFD):
            messagebox.showwarning(t('dlg.not_afd'), t('msg.min_not_afd'))
            return None
        if not automaton.estado_inicial:
            messagebox.showwarning(t('dlg.no_initial'), t('msg.no_initial'))
            return None
        if not automaton.estados:
            messagebox.showwarning(t('dlg.no_states'), t('msg.no_states'))
            return None
        return automaton

    def _minimizar_todo(self):
        afd = self._get_afd()
        if afd is None:
            return

        try:
            resultado = afd.minimizar()
        except Exception as e:
            messagebox.showerror('Error', f'Error en minimización:\n{str(e)}')
            self.app.add_log(f'Error en minimización: {str(e)}', 'error')
            return

        self._resultado_completo = resultado
        self._pasos = resultado.get('pasos', [])
        self._afd_minimo = resultado.get('afd_minimo', None)
        self._paso_actual = len(self._pasos) - 1

        if self._pasos:
            self._mostrar_paso(self._pasos[-1])

        self._mostrar_resultado()
        self._btn_ver_minimo.pack(fill=tk.X, pady=(4, 8))
        self.app.add_log(
            t('log.min_complete', n=len(self._afd_minimo.estados)), 'success')

    def _minimizar_paso(self):
        afd = self._get_afd()
        if afd is None:
            return

        if not self._pasos:
            try:
                resultado = afd.minimizar()
            except Exception as e:
                messagebox.showerror('Error',
                                     f'Error en minimización:\n{str(e)}')
                self.app.add_log(f'Error en minimización: {str(e)}', 'error')
                return

            self._resultado_completo = resultado
            self._pasos = resultado.get('pasos', [])
            self._afd_minimo = resultado.get('afd_minimo', None)
            self._paso_actual = -1

        if self._paso_actual < len(self._pasos) - 1:
            self._paso_actual += 1
            self._mostrar_paso(self._pasos[self._paso_actual])

            if self._paso_actual >= len(self._pasos) - 1:
                self._btn_paso.configure(text=t('min.btn_completed'),
                                         state=tk.DISABLED)
                self._mostrar_resultado()
                self._btn_ver_minimo.pack(fill=tk.X, pady=(4, 8))
                self.app.add_log(
                    t('log.min_step_complete', n=len(self._afd_minimo.estados)),
                    'success')
            else:
                self.app.add_log(
                    t('log.min_step', n=self._paso_actual),
                    'info')
        else:
            messagebox.showinfo(t('dlg.min_complete'), t('msg.min_complete'))

    def _reiniciar(self):
        self._pasos = []
        self._paso_actual = -1
        self._resultado_completo = None
        self._afd_minimo = None

        self._desc_label.configure(text='')
        self._result_label.configure(text='')
        self._btn_paso.configure(text=t('min.btn_step'),
                                 state=tk.NORMAL)
        self._btn_ver_minimo.pack_forget()

        for w in self._table_frame.winfo_children():
            w.destroy()
        c = theme.colors
        self._table_placeholder = tk.Label(
            self._table_frame,
            text=t('min.table_placeholder'),
            bg=c['bg_panel'], fg=c['text_secondary'],
            font=('Segoe UI', 9, 'italic'))
        self._table_placeholder.pack(anchor='w')
        self._active_table_placeholder = self._table_placeholder

        for w in self._classes_frame.winfo_children():
            w.destroy()
        self._classes_placeholder = tk.Label(
            self._classes_frame,
            text=t('min.classes_placeholder'),
            bg=c['bg_panel'], fg=c['text_secondary'],
            font=('Segoe UI', 9, 'italic'))
        self._classes_placeholder.pack(anchor='w')
        self._active_classes_placeholder = self._classes_placeholder

    # ── Mostrar resultados ───────────────────────────────────────

    def _mostrar_paso(self, paso: Dict):
        desc = paso.get('descripcion', '')
        self._desc_label.configure(text=desc)

        tabla = paso.get('tabla', {})
        self._dibujar_tabla(tabla)

        clases = paso.get('clases', [])
        self._dibujar_clases(clases)

    def _dibujar_tabla(self, tabla: Dict):
        c = theme.colors

        for w in self._table_frame.winfo_children():
            w.destroy()

        if not tabla:
            lbl = tk.Label(self._table_frame, text='(tabla vacía)',
                           bg=c['bg_panel'], fg=c['text_secondary'],
                           font=('Segoe UI', 9, 'italic'))
            lbl.pack(anchor='w')
            return

        # Parse tabla keys: "(p,q)" -> (p, q)
        pares = []
        for key, val in tabla.items():
            key_clean = key.strip('()')
            parts = key_clean.split(',')
            if len(parts) == 2:
                pares.append((parts[0].strip(), parts[1].strip(), val))

        if not pares:
            lbl = tk.Label(self._table_frame, text='(sin pares)',
                           bg=c['bg_panel'], fg=c['text_secondary'],
                           font=('Segoe UI', 9, 'italic'))
            lbl.pack(anchor='w')
            return

        all_states = set()
        for p, q, _ in pares:
            all_states.add(p)
            all_states.add(q)
        estados = sorted(all_states)

        if len(estados) < 2:
            lbl = tk.Label(self._table_frame,
                           text='Menos de 2 estados — tabla vacía',
                           bg=c['bg_panel'], fg=c['text_secondary'],
                           font=('Segoe UI', 9, 'italic'))
            lbl.pack(anchor='w')
            return

        tabla_lookup = {}
        for p, q, val in pares:
            tabla_lookup[(p, q)] = val

        col_states = estados[:-1]
        row_states = estados[1:]

        # Header
        corner = tk.Label(self._table_frame, text='δ', bg=c['bg_surface'],
                          fg=c['text'], font=('Segoe UI', 9, 'bold'),
                          padx=6, pady=3, relief='flat')
        corner.grid(row=0, column=0, padx=1, pady=1, sticky='nsew')

        for j, estado_col in enumerate(col_states):
            hdr = tk.Label(self._table_frame, text=estado_col,
                           bg=c['bg_surface'], fg=c['text'],
                           font=('Consolas', 9, 'bold'), padx=6, pady=3,
                           relief='flat')
            hdr.grid(row=0, column=j + 1, padx=1, pady=1, sticky='nsew')

        # Data rows
        for i, estado_row in enumerate(row_states):
            rhdr = tk.Label(self._table_frame, text=estado_row,
                            bg=c['bg_surface'], fg=c['text'],
                            font=('Consolas', 9, 'bold'), padx=6, pady=3,
                            relief='flat')
            rhdr.grid(row=i + 1, column=0, padx=1, pady=1, sticky='nsew')

            for j, estado_col in enumerate(col_states):
                if j >= i + 1:
                    cell = tk.Label(self._table_frame, text='', bg=c['bg_panel'],
                                    padx=6, pady=3, relief='flat')
                    cell.grid(row=i + 1, column=j + 1, padx=1, pady=1,
                              sticky='nsew')
                    continue

                par = (min(estado_col, estado_row), max(estado_col, estado_row))
                val = tabla_lookup.get(par, False)

                if val:
                    cell_text = '✗'
                    cell_bg = '#5A2222'
                    cell_fg = c['red']
                else:
                    cell_text = '≡'
                    cell_bg = '#1A4A2E'
                    cell_fg = c['green']

                cell = tk.Label(self._table_frame, text=cell_text,
                                bg=cell_bg, fg=cell_fg,
                                font=('Consolas', 11, 'bold'),
                                padx=8, pady=3, relief='flat')
                cell.grid(row=i + 1, column=j + 1, padx=1, pady=1,
                          sticky='nsew')

        for j in range(len(col_states) + 1):
            self._table_frame.columnconfigure(j, weight=1)

    def _dibujar_clases(self, clases: List[List[str]]):
        c = theme.colors

        for w in self._classes_frame.winfo_children():
            w.destroy()

        if not clases:
            lbl = tk.Label(self._classes_frame, text='(sin clases)',
                           bg=c['bg_panel'], fg=c['text_secondary'],
                           font=('Segoe UI', 9, 'italic'))
            lbl.pack(anchor='w')
            return

        for i, clase in enumerate(clases):
            clase_frame = tk.Frame(self._classes_frame, bg=c['bg_surface'],
                                   highlightbackground=c['border'],
                                   highlightthickness=1)
            clase_frame.pack(fill=tk.X, pady=2)

            class_label = f'C{i} = ' + '{'
            tk.Label(clase_frame, text=class_label, bg=c['bg_surface'],
                     fg=c['accent'], font=('Consolas', 10)).pack(
                         side=tk.LEFT, padx=(6, 0))

            for j, estado in enumerate(clase):
                badge_bg = '#1A3A2E' if j == 0 else c['bg_input']
                tk.Label(clase_frame, text=estado, bg=badge_bg,
                         fg=c['text'], font=('Consolas', 10, 'bold'),
                         padx=4, pady=2).pack(side=tk.LEFT, padx=2, pady=3)
                if j < len(clase) - 1:
                    tk.Label(clase_frame, text=',', bg=c['bg_surface'],
                             fg=c['text_secondary'],
                             font=('Consolas', 10)).pack(side=tk.LEFT)

            tk.Label(clase_frame, text='}', bg=c['bg_surface'],
                     fg=c['accent'],
                     font=('Consolas', 10)).pack(side=tk.LEFT, padx=(0, 6))

    def _mostrar_resultado(self):
        c = theme.colors
        if self._afd_minimo is None:
            return

        afd_original = self.app.current_automaton
        n_original = len(afd_original.estados) if afd_original else 0
        n_minimo = len(self._afd_minimo.estados)

        if n_original == n_minimo:
            self._result_label.configure(
                text=t('min.result_already', n=n_minimo),
                fg=c['green'])
        else:
            self._result_label.configure(
                text=t('min.result_reduced', n=n_minimo, orig=n_original),
                fg=c['green'])

    def _ver_afd_minimo(self):
        if self._afd_minimo is None:
            messagebox.showwarning(t('dlg.no_result'), t('msg.no_result_min'))
            return
        if not hasattr(self.app, 'canvas_widget') or not self.app.canvas_widget:
            return
        self.app.canvas_widget.dibujar_automata(self._afd_minimo, tipo='AFD')
        self.app.add_log(t('log.canvas_min'), 'info')

    # ── Tema ─────────────────────────────────────────────────────

    def _on_theme_change(self):
        c = theme.colors
        self.configure(bg=c['bg_panel'])
        self._title.configure(bg=c['bg_panel'], fg=c['accent'])
        self._btn_frame.configure(bg=c['bg_panel'])
        self._desc_label.configure(bg=c['bg_panel'], fg=c['text_secondary'])
        self._result_label.configure(bg=c['bg_panel'])
        self._content_canvas.configure(bg=c['bg_panel'])
        self._content_inner.configure(bg=c['bg_panel'])
        self._table_section_label.configure(bg=c['bg_panel'], fg=c['text'])
        self._classes_section_label.configure(bg=c['bg_panel'], fg=c['text'])

        if self._pasos and self._paso_actual >= 0:
            self._mostrar_paso(self._pasos[self._paso_actual])

    def refresh_lang(self):
        """Refresh all UI text after language change."""
        try:
            self._title.configure(text=t('min.title'))
            self._btn_minimizar.configure(text=t('min.btn_all'))
            # Only update step btn if not in completed state
            if self._btn_paso['state'] != 'disabled':
                self._btn_paso.configure(text=t('min.btn_step'))
            self._btn_reiniciar.configure(text=t('min.btn_reset'))
            self._btn_ver_minimo.configure(text=t('min.btn_view'))
            self._table_section_label.configure(text=t('min.table_title'))
            self._classes_section_label.configure(text=t('min.classes_title'))
            # Update dynamic placeholders if active
            for attr in ('_table_placeholder', '_active_table_placeholder'):
                ph = getattr(self, attr, None)
                if ph and ph.winfo_exists():
                    try: ph.configure(text=t('min.table_placeholder'))
                    except Exception: pass
            for attr in ('_classes_placeholder', '_active_classes_placeholder'):
                ph = getattr(self, attr, None)
                if ph and ph.winfo_exists():
                    try: ph.configure(text=t('min.classes_placeholder'))
                    except Exception: pass
        except Exception:
            pass
