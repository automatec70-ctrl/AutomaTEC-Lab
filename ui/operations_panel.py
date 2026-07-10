"""
OperationsPanel — Panel para operaciones de lenguajes en AFDs.

Contiene:
  - Misma entrada de segundo AFD que EquivalencePanel
  - Botones de operación: Unión (∪), Intersección (∩), Diferencia (−), Complemento (̄)
  - Cada operación muestra el resultado en un Text widget
  - Validación: ambos AFDs deben tener el mismo alfabeto para operaciones binarias
  - Opción de ver el resultado en el canvas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict

from ui.i18n import lang, t
from ui.theme import theme
from core.afd import AFD


class OperationsPanel(tk.Frame):
    """Panel para operaciones booleanas en AFDs."""

    def __init__(self, parent, app_ref, **kwargs):
        c = theme.colors
        super().__init__(parent, bg=c['bg_panel'], **kwargs)
        self.app = app_ref

        self._afd2_entries: Dict = {}
        self._afd2_finales_vars: Dict = {}
        self._afd2_estado_inicial_var = tk.StringVar()
        self._separators = []
        self._resultado_afd: Optional[AFD] = None

        self._build_ui()
        theme.on_change(self._on_theme_change)

    # ── Construcción de la UI ────────────────────────────────────

    def _build_ui(self):
        c = theme.colors

        # Título
        self._title = tk.Label(self, text=t('ops.title'), bg=c['bg_panel'],
                               fg=c['accent'], font=('Segoe UI', 12, 'bold'))
        self._title.pack(anchor='w', padx=12, pady=(10, 4))

        # Scrollable
        outer = tk.Frame(self, bg=c['bg_panel'])
        outer.pack(fill=tk.BOTH, expand=True)

        self._scroll_canvas = tk.Canvas(outer, bg=c['bg_panel'],
                                         highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient=tk.VERTICAL,
                                  command=self._scroll_canvas.yview)
        self._scroll_inner = tk.Frame(self._scroll_canvas, bg=c['bg_panel'])

        self._scroll_inner.bind('<Configure>',
            lambda e: self._scroll_canvas.configure(
                scrollregion=self._scroll_canvas.bbox('all')))
        self._cw = self._scroll_canvas.create_window(
            (0, 0), window=self._scroll_inner, anchor='nw')
        self._scroll_canvas.configure(yscrollcommand=scrollbar.set)

        self._scroll_canvas.bind('<Configure>',
            lambda e: self._scroll_canvas.itemconfig(self._cw, width=e.width))
        self._scroll_canvas.bind('<Enter>', lambda e: self._scroll_canvas.bind_all(
            '<MouseWheel>',
            lambda ev: self._scroll_canvas.yview_scroll(
                int(-1 * (ev.delta / 120)), 'units')))
        self._scroll_canvas.bind('<Leave>', lambda e: self._scroll_canvas.unbind_all(
            '<MouseWheel>'))

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = self._scroll_inner

        # AFD1 info
        info_frame = tk.Frame(inner, bg=c['bg_panel'])
        info_frame.pack(fill=tk.X, padx=12, pady=(0, 4))

        self._lbl_afd1_desc = tk.Label(info_frame, text=t('ops.afd1_info'),
                 bg=c['bg_panel'], fg=c['text_secondary'],
                 font=('Segoe UI', 9, 'italic'))
        self._lbl_afd1_desc.pack(anchor='w')
        self._afd1_info = tk.Label(info_frame, text='', bg=c['bg_panel'],
                                   fg=c['text'], font=('Consolas', 9))
        self._afd1_info.pack(anchor='w')

        self._separator(inner)

        # AFD2 definición
        self._lbl_afd2_title = tk.Label(inner, text=t('ops.afd2_title'), bg=c['bg_panel'],
                 fg=c['text'], font=('Segoe UI', 10, 'bold'))
        self._lbl_afd2_title.pack(anchor='w', padx=12, pady=(4, 2))

        # Estados
        est_frame = tk.Frame(inner, bg=c['bg_panel'])
        est_frame.pack(fill=tk.X, padx=12, pady=(0, 2))
        self._lbl_states = tk.Label(est_frame, text=t('ops.states_label'), bg=c['bg_panel'],
                 fg=c['text_secondary'], font=('Segoe UI', 9))
        self._lbl_states.pack(side=tk.LEFT, padx=(0, 4))

        self._estados_var = tk.StringVar()
        self._estados_entry = tk.Entry(
            est_frame, textvariable=self._estados_var,
            bg=c['bg_input'], fg=c['text'], insertbackground=c['text'],
            font=('Consolas', 10), width=30, relief='flat',
            highlightthickness=1, highlightcolor=c['accent'],
            highlightbackground=c['border'])
        self._estados_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Alfabeto
        alf_frame = tk.Frame(inner, bg=c['bg_panel'])
        alf_frame.pack(fill=tk.X, padx=12, pady=(0, 2))
        self._lbl_alphabet = tk.Label(alf_frame, text=t('ops.alphabet_label'), bg=c['bg_panel'],
                 fg=c['text_secondary'], font=('Segoe UI', 9))
        self._lbl_alphabet.pack(side=tk.LEFT, padx=(0, 4))

        self._alfabeto_var = tk.StringVar()
        self._alfabeto_entry = tk.Entry(
            alf_frame, textvariable=self._alfabeto_var,
            bg=c['bg_input'], fg=c['text'], insertbackground=c['text'],
            font=('Consolas', 10), width=30, relief='flat',
            highlightthickness=1, highlightcolor=c['accent'],
            highlightbackground=c['border'])
        self._alfabeto_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Botón generar tabla
        self._btn_gen_table = tk.Button(
            inner, text=t('ops.gen_table'),
            command=self._generar_tabla,
            bg=c['bg_surface'], fg=c['text'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            font=('Segoe UI', 9), relief='flat', cursor='hand2', padx=8)
        self._btn_gen_table.pack(anchor='w', padx=12, pady=(4, 4))

        # Mini tabla de transiciones
        self._table_label = tk.Label(
            inner, text=t('ops.table_title'),
            bg=c['bg_panel'], fg=c['text'],
            font=('Segoe UI', 10, 'bold'))
        self._table_label.pack(anchor='w', padx=12, pady=(4, 2))

        self._table_outer = tk.Frame(inner, bg=c['bg_panel'])
        self._table_outer.pack(fill=tk.X, padx=12, pady=(0, 4))

        self._table_placeholder = tk.Label(
            self._table_outer,
            text=t('ops.table_placeholder'),
            bg=c['bg_panel'], fg=c['text_secondary'],
            font=('Segoe UI', 9, 'italic'))
        self._table_placeholder.pack(anchor='w')

        # Estado inicial AFD2
        init_frame = tk.Frame(inner, bg=c['bg_panel'])
        init_frame.pack(fill=tk.X, padx=12, pady=(0, 2))
        self._lbl_initial = tk.Label(init_frame, text=t('ops.initial_state'), bg=c['bg_panel'],
                 fg=c['text_secondary'], font=('Segoe UI', 9))
        self._lbl_initial.pack(side=tk.LEFT, padx=(0, 4))

        self._init_combo = ttk.Combobox(
            init_frame, textvariable=self._afd2_estado_inicial_var,
            state='readonly', width=20, font=('Consolas', 10))
        self._init_combo.pack(side=tk.LEFT)

        # Estados finales AFD2
        self._lbl_finals_title = tk.Label(inner, text=t('ops.finals_title'), bg=c['bg_panel'],
                 fg=c['text'], font=('Segoe UI', 10, 'bold'))
        self._lbl_finals_title.pack(anchor='w', padx=12, pady=(4, 2))

        self._finales_frame = tk.Frame(inner, bg=c['bg_panel'])
        self._finales_frame.pack(fill=tk.X, padx=12, pady=(0, 4))

        self._finales_placeholder = tk.Label(
            self._finales_frame, text=t('ops.finals_placeholder'),
            bg=c['bg_panel'], fg=c['text_secondary'],
            font=('Segoe UI', 9, 'italic'))
        self._finales_placeholder.pack(anchor='w')

        self._separator(inner)

        # Botones de operaciones
        self._lbl_operations = tk.Label(inner, text=t('ops.operations_label'), bg=c['bg_panel'],
                 fg=c['text'], font=('Segoe UI', 10, 'bold'))
        self._lbl_operations.pack(anchor='w', padx=12, pady=(4, 4))

        self._ops_frame = tk.Frame(inner, bg=c['bg_panel'])
        self._ops_frame.pack(fill=tk.X, padx=12, pady=(0, 4))

        btn_ops = [
            (t('ops.union'), self._op_union, c['accent']),
            (t('ops.intersection'), self._op_interseccion, c['accent']),
            (t('ops.difference'), self._op_diferencia, c['accent']),
            (t('ops.complement'), self._op_complemento, c['yellow']),
        ]

        self._op_buttons = []
        for i, (text, cmd, color) in enumerate(btn_ops):
            fg_color = (c['text_on_accent'] if color != c['yellow']
                        else c['bg_main'])
            btn = tk.Button(
                self._ops_frame, text=text, command=cmd,
                bg=color, fg=fg_color,
                activebackground=c['accent_hover'],
                activeforeground=c['text_on_accent'],
                font=('Segoe UI', 9, 'bold'), relief='flat',
                cursor='hand2', padx=8, pady=4)
            btn.grid(row=i // 2, column=i % 2, padx=2, pady=2, sticky='nsew')
            self._op_buttons.append(btn)

        self._ops_frame.columnconfigure(0, weight=1)
        self._ops_frame.columnconfigure(1, weight=1)

        # Resultado
        self._lbl_result_title = tk.Label(inner, text=t('ops.result_title'), bg=c['bg_panel'],
                 fg=c['text'], font=('Segoe UI', 10, 'bold'))
        self._lbl_result_title.pack(anchor='w', padx=12, pady=(8, 2))

        self._result_frame = tk.Frame(inner, bg=c['bg_panel'])
        self._result_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 4))

        self._result_text = tk.Text(
            self._result_frame, bg=c['bg_input'], fg=c['text'],
            insertbackground=c['text'], selectbackground=c['accent'],
            selectforeground=c['text_on_accent'],
            font=('Consolas', 9), relief='flat', bd=0,
            height=8, wrap=tk.WORD, state=tk.DISABLED,
            highlightthickness=1, highlightcolor=c['accent'],
            highlightbackground=c['border'])

        result_scroll = ttk.Scrollbar(self._result_frame, orient=tk.VERTICAL,
                                      command=self._result_text.yview)
        self._result_text.configure(yscrollcommand=result_scroll.set)
        result_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._result_text.pack(fill=tk.BOTH, expand=True)

        self._result_text.tag_configure('title', foreground=c['accent'],
                                        font=('Consolas', 10, 'bold'))
        self._result_text.tag_configure('success', foreground=c['green'])
        self._result_text.tag_configure('error', foreground=c['red'])

        # Botón ver resultado en canvas
        self._btn_ver_resultado = tk.Button(
            inner, text=t('ops.btn_view'),
            command=self._ver_resultado_canvas,
            bg=c['green'], fg='#FFFFFF', activebackground='#059669',
            activeforeground='#FFFFFF', font=('Segoe UI', 9, 'bold'),
            relief='flat', cursor='hand2', padx=10)

    def _separator(self, parent):
        c = theme.colors
        sep = tk.Frame(parent, bg=c['border'], height=1)
        sep.pack(fill=tk.X, padx=12, pady=6)
        self._separators.append(sep)

    # ── Generar tabla ────────────────────────────────────────────

    def _generar_tabla(self):
        c = theme.colors

        estados_text = self._estados_var.get().strip()
        alfabeto_text = self._alfabeto_var.get().strip()

        if not estados_text or not alfabeto_text:
            messagebox.showwarning(t('dlg.data_incomplete'), t('msg.data_incomplete'))
            return

        estados = [e.strip() for e in estados_text.split(',') if e.strip()]
        alfabeto = [a.strip() for a in alfabeto_text.split(',') if a.strip()]

        if not estados or not alfabeto:
            messagebox.showwarning(t('dlg.data_invalid'), t('msg.data_invalid'))
            return

        for w in self._table_outer.winfo_children():
            w.destroy()
        self._afd2_entries = {}

        table_frame = tk.Frame(self._table_outer, bg=c['bg_panel'])
        table_frame.pack(fill=tk.X)

        tk.Label(table_frame, text='δ₂', bg=c['bg_surface'], fg=c['text'],
                 font=('Segoe UI', 9, 'bold'), padx=6, pady=3,
                 relief='flat').grid(row=0, column=0, padx=1, pady=1,
                                     sticky='nsew')

        for j, simbolo in enumerate(alfabeto):
            tk.Label(table_frame, text=simbolo, bg=c['bg_surface'],
                     fg=c['text'], font=('Consolas', 9, 'bold'), padx=6,
                     pady=3, relief='flat').grid(row=0, column=j + 1, padx=1,
                                                  pady=1, sticky='nsew')

        for i, estado in enumerate(estados):
            tk.Label(table_frame, text=estado, bg=c['bg_surface'],
                     fg=c['text'], font=('Consolas', 9, 'bold'), padx=6,
                     pady=3, relief='flat').grid(row=i + 1, column=0, padx=1,
                                                  pady=1, sticky='nsew')

            for j, simbolo in enumerate(alfabeto):
                entry = tk.Entry(table_frame, width=8,
                                 bg=c['bg_input'], fg=c['text'],
                                 insertbackground=c['text'],
                                 font=('Consolas', 9), relief='flat', bd=0,
                                 highlightthickness=1,
                                 highlightcolor=c['accent'],
                                 highlightbackground=c['border'])
                entry.grid(row=i + 1, column=j + 1, padx=1, pady=1,
                          ipadx=2, ipady=1, sticky='nsew')
                self._afd2_entries[(estado, simbolo)] = entry

        for j in range(len(alfabeto) + 1):
            table_frame.columnconfigure(j, weight=1)

        self._init_combo['values'] = estados
        self._afd2_estado_inicial_var.set('')

        for w in self._finales_frame.winfo_children():
            w.destroy()

        self._afd2_finales_vars = {}
        for estado in estados:
            var = tk.BooleanVar(value=False)
            self._afd2_finales_vars[estado] = var
            cb = tk.Checkbutton(
                self._finales_frame, text=estado, variable=var,
                bg=c['bg_panel'], fg=c['text'],
                activebackground=c['bg_panel'], activeforeground=c['text'],
                selectcolor=c['bg_input'], font=('Consolas', 10))
            cb.pack(side=tk.LEFT, padx=4)

    # ── Construir AFD2 ───────────────────────────────────────────

    def _construir_afd2(self) -> Optional[AFD]:
        estados_text = self._estados_var.get().strip()
        alfabeto_text = self._alfabeto_var.get().strip()

        if not estados_text or not alfabeto_text:
            messagebox.showwarning(t('dlg.data_incomplete'), t('msg.data_incomplete2'))
            return None

        estados = [e.strip() for e in estados_text.split(',') if e.strip()]
        alfabeto = [a.strip() for a in alfabeto_text.split(',') if a.strip()]

        if not estados or not alfabeto:
            messagebox.showwarning('Datos inválidos',
                                   'Estados y alfabeto no pueden estar vacíos.')
            return None

        estado_inicial = self._afd2_estado_inicial_var.get()
        if not estado_inicial:
            messagebox.showwarning(t('dlg.no_initial'), t('msg.no_initial2'))
            return None

        estados_finales = set()
        for est, var in self._afd2_finales_vars.items():
            if var.get():
                estados_finales.add(est)

        afd2 = AFD()
        for estado in estados:
            afd2.agregar_estado(estado)
        for simbolo in alfabeto:
            afd2.agregar_simbolo(simbolo)
        afd2.definir_estado_inicial(estado_inicial)
        for ef in estados_finales:
            afd2.agregar_estado_final(ef)

        for (estado, simbolo), entry in self._afd2_entries.items():
            val = entry.get().strip()
            if val:
                if val not in estados:
                    messagebox.showwarning(
                        t('dlg.invalid_trans'),
                        t('msg.invalid_trans', q=estado, s=simbolo, v=val))
                    return None
                afd2.definir_transicion(estado, simbolo, val)

        return afd2

    # ── Operaciones ──────────────────────────────────────────────

    def _validate_binary(self) -> Optional[tuple]:
        afd1 = self.app.current_automaton
        if not afd1 or not isinstance(afd1, AFD):
            messagebox.showwarning(t('dlg.invalid_afd'), t('msg.not_afd'))
            return None
        if not afd1.estado_inicial or not afd1.estados:
            messagebox.showwarning(t('dlg.incomplete_afd'), t('msg.afd_incomplete'))
            return None

        afd2 = self._construir_afd2()
        if afd2 is None:
            return None

        if afd1.alfabeto != afd2.alfabeto:
            messagebox.showwarning(
                t('dlg.diff_alphabets'),
                t('msg.diff_alphabets', a1=sorted(afd1.alfabeto), a2=sorted(afd2.alfabeto)))
            return None

        return (afd1, afd2)

    def _op_union(self):
        result = self._validate_binary()
        if result is None:
            return
        afd1, afd2 = result

        try:
            resultado = afd1.union(afd2)
            self._mostrar_resultado('Unión (∪)', resultado, afd1, afd2)
            self.app.add_log(
                t('log.union', n=len(resultado.estados)),
                'success')
        except Exception as e:
            self._mostrar_error(f'Error en unión: {str(e)}')

    def _op_interseccion(self):
        result = self._validate_binary()
        if result is None:
            return
        afd1, afd2 = result

        try:
            resultado = afd1.interseccion(afd2)
            self._mostrar_resultado('Intersección (∩)', resultado, afd1, afd2)
            self.app.add_log(
                t('log.intersection', n=len(resultado.estados)),
                'success')
        except Exception as e:
            self._mostrar_error(f'Error en intersección: {str(e)}')

    def _op_diferencia(self):
        result = self._validate_binary()
        if result is None:
            return
        afd1, afd2 = result

        try:
            resultado = afd1.diferencia(afd2)
            self._mostrar_resultado('Diferencia (−)', resultado, afd1, afd2)
            self.app.add_log(
                t('log.difference', n=len(resultado.estados)),
                'success')
        except Exception as e:
            self._mostrar_error(f'Error en diferencia: {str(e)}')

    def _op_complemento(self):
        afd1 = self.app.current_automaton
        if not afd1 or not isinstance(afd1, AFD):
            messagebox.showwarning('AFD₁ inválido',
                                   'El autómata actual debe ser un AFD.')
            return
        if not afd1.estado_inicial or not afd1.estados:
            messagebox.showwarning('AFD₁ incompleto',
                                   'El AFD actual debe tener estados y '
                                   'estado inicial.')
            return

        try:
            resultado = afd1.complemento()
            self._mostrar_resultado('Complemento (̄)', resultado, afd1, None)
            self.app.add_log(
                t('log.complement', n=len(resultado.estados)),
                'success')
        except Exception as e:
            self._mostrar_error(f'Error en complemento: {str(e)}')

    # ── Mostrar resultados ───────────────────────────────────────

    def _mostrar_resultado(self, operacion: str, resultado: AFD,
                           afd1: AFD, afd2: Optional[AFD]):
        c = theme.colors
        self._resultado_afd = resultado

        self._result_text.configure(state=tk.NORMAL)
        self._result_text.delete('1.0', tk.END)

        self._result_text.insert(tk.END, t('ops.result.operation', op=operacion) + '\n', 'title')
        self._result_text.insert(tk.END, '─' * 40 + '\n')
        self._result_text.insert(tk.END, t('ops.result.states', s=sorted(resultado.estados)) + '\n')
        self._result_text.insert(tk.END, t('ops.result.alphabet', s=sorted(resultado.alfabeto)) + '\n')
        self._result_text.insert(tk.END, t('ops.result.initial', s=resultado.estado_inicial) + '\n')
        self._result_text.insert(tk.END, t('ops.result.finals', s=sorted(resultado.estados_finales)) + '\n')
        self._result_text.insert(tk.END, t('ops.result.total', n=len(resultado.estados)) + '\n')
        self._result_text.insert(tk.END, '─' * 40 + '\n')

        self._result_text.insert(tk.END, t('ops.result.transitions') + '\n', 'title')
        for estado in sorted(resultado.delta):
            for simbolo in sorted(resultado.delta[estado]):
                hacia = resultado.delta[estado][simbolo]
                self._result_text.insert(tk.END,
                    f'  δ({estado}, {simbolo}) = {hacia}\n')

        self._result_text.configure(state=tk.DISABLED)
        self._btn_ver_resultado.pack(fill=tk.X, padx=12, pady=(4, 10))

    def _mostrar_error(self, msg: str):
        self._result_text.configure(state=tk.NORMAL)
        self._result_text.delete('1.0', tk.END)
        self._result_text.insert(tk.END, msg, 'error')
        self._result_text.configure(state=tk.DISABLED)
        self.app.add_log(msg, 'error')

    def _ver_resultado_canvas(self):
        if self._resultado_afd is None:
            messagebox.showwarning(t('dlg.no_result'), t('msg.no_result'))
            return
        if not hasattr(self.app, 'canvas_widget') or not self.app.canvas_widget:
            return
        self.app.canvas_widget.dibujar_automata(self._resultado_afd, tipo='AFD')
        self.app.add_log(t('log.canvas_result'),
                         'info')

    # ── Actualizar info ──────────────────────────────────────────

    def update_afd1_info(self):
        automaton = self.app.current_automaton
        if automaton and isinstance(automaton, AFD):
            info = (f'Q={sorted(automaton.estados)}, '
                    f'Σ={sorted(automaton.alfabeto)}, '
                    f'q0={automaton.estado_inicial}, '
                    f'F={sorted(automaton.estados_finales)}')
            self._afd1_info.configure(text=info)
        else:
            self._afd1_info.configure(text='(no hay AFD definido)')

    # ── Tema ─────────────────────────────────────────────────────

    def _on_theme_change(self):
        c = theme.colors
        self.configure(bg=c['bg_panel'])
        self._title.configure(bg=c['bg_panel'], fg=c['accent'])
        self._scroll_canvas.configure(bg=c['bg_panel'])
        self._scroll_inner.configure(bg=c['bg_panel'])
        self._result_frame.configure(bg=c['bg_panel'])
        self._afd1_info.configure(bg=c['bg_panel'], fg=c['text'])
        self._ops_frame.configure(bg=c['bg_panel'])

        self._result_text.tag_configure('title', foreground=c['accent'],
                                        font=('Consolas', 10, 'bold'))
        self._result_text.tag_configure('success', foreground=c['green'])
        self._result_text.tag_configure('error', foreground=c['red'])

        for sep in self._separators:
            sep.configure(bg=c['border'])

        if self._afd2_entries:
            for (estado, simbolo), entry in self._afd2_entries.items():
                entry.configure(
                    bg=c['bg_input'], fg=c['text'],
                    insertbackground=c['text'],
                    highlightcolor=c['accent'],
                    highlightbackground=c['border'])

    def refresh_lang(self):
        try:
            self._title.configure(text=t('ops.title'))
            self._lbl_afd1_desc.configure(text=t('ops.afd1_info'))
            self._lbl_afd2_title.configure(text=t('ops.afd2_title'))
            self._lbl_states.configure(text=t('ops.states_label'))
            self._lbl_alphabet.configure(text=t('ops.alphabet_label'))
            self._lbl_initial.configure(text=t('ops.initial_state'))
            self._lbl_finals_title.configure(text=t('ops.finals_title'))
            self._lbl_operations.configure(text=t('ops.operations_label'))
            self._lbl_result_title.configure(text=t('ops.result_title'))
            self._btn_gen_table.configure(text=t('ops.gen_table'))
            self._table_label.configure(text=t('ops.table_title'))
            self._btn_ver_resultado.configure(text=t('ops.btn_view'))
            # Update operation button labels
            op_labels = [t('ops.union'),t('ops.intersection'),t('ops.difference'),t('ops.complement')]
            for i, btn in enumerate(self._op_buttons):
                if i < len(op_labels): btn.configure(text=op_labels[i])
            # placeholders
            if hasattr(self,'_table_placeholder') and self._table_placeholder.winfo_exists():
                self._table_placeholder.configure(text=t('ops.table_placeholder'))
            if hasattr(self,'_finales_placeholder') and self._finales_placeholder.winfo_exists():
                self._finales_placeholder.configure(text=t('ops.finals_placeholder'))
        except Exception:
            pass
