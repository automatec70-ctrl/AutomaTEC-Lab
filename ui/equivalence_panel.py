"""
EquivalencePanel — Panel para verificar equivalencia entre dos AFDs.

Contiene:
  - Sección para definir un segundo AFD:
    - Entry para estados (separados por coma)
    - Entry para alfabeto (separados por coma)
    - Mini tabla de transiciones
    - Select para estado inicial
    - Checkboxes para estados finales
  - Botón [Verificar Equivalencia]
  - Resultado: "EQUIVALENTES" (verde) o "DISTINTOS" (rojo)
  - Si son distintos: cadena testigo (contraejemplo)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict

from ui.i18n import lang, t
from ui.theme import theme
from core.afd import AFD


class EquivalencePanel(tk.Frame):
    """Panel para verificar equivalencia entre dos AFDs."""

    def __init__(self, parent, app_ref, **kwargs):
        c = theme.colors
        super().__init__(parent, bg=c['bg_panel'], **kwargs)
        self.app = app_ref

        self._afd2_entries: Dict = {}
        self._afd2_finales_vars: Dict = {}
        self._afd2_estado_inicial_var = tk.StringVar()
        self._separators = []

        self._build_ui()
        theme.on_change(self._on_theme_change)

    # ── Construcción de la UI ────────────────────────────────────

    def _build_ui(self):
        c = theme.colors

        # Título
        self._title = tk.Label(self, text=t('eq.title'), bg=c['bg_panel'],
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

        self._lbl_afd1_desc = tk.Label(info_frame, text=t('eq.afd1_info'),
                 bg=c['bg_panel'], fg=c['text_secondary'],
                 font=('Segoe UI', 9, 'italic'))
        self._lbl_afd1_desc.pack(anchor='w')
        self._afd1_info = tk.Label(info_frame, text='', bg=c['bg_panel'],
                                   fg=c['text'], font=('Consolas', 9))
        self._afd1_info.pack(anchor='w')

        self._separator(inner)

        # AFD2 definición
        self._lbl_afd2_title = tk.Label(inner, text=t('eq.afd2_title'), bg=c['bg_panel'],
                 fg=c['text'], font=('Segoe UI', 10, 'bold'))
        self._lbl_afd2_title.pack(anchor='w', padx=12, pady=(4, 2))

        # Estados
        est_frame = tk.Frame(inner, bg=c['bg_panel'])
        est_frame.pack(fill=tk.X, padx=12, pady=(0, 2))
        self._lbl_states = tk.Label(est_frame, text=t('eq.states_label'), bg=c['bg_panel'],
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
        self._lbl_alphabet = tk.Label(alf_frame, text=t('eq.alphabet_label'), bg=c['bg_panel'],
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
            inner, text=t('eq.gen_table'),
            command=self._generar_tabla,
            bg=c['bg_surface'], fg=c['text'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            font=('Segoe UI', 9), relief='flat', cursor='hand2', padx=8)
        self._btn_gen_table.pack(anchor='w', padx=12, pady=(4, 4))

        # Mini tabla de transiciones
        self._table_label = tk.Label(
            inner, text=t('eq.table_title'),
            bg=c['bg_panel'], fg=c['text'],
            font=('Segoe UI', 10, 'bold'))
        self._table_label.pack(anchor='w', padx=12, pady=(4, 2))

        self._table_outer = tk.Frame(inner, bg=c['bg_panel'])
        self._table_outer.pack(fill=tk.X, padx=12, pady=(0, 4))

        self._table_placeholder = tk.Label(
            self._table_outer,
            text=t('eq.table_placeholder'),
            bg=c['bg_panel'], fg=c['text_secondary'],
            font=('Segoe UI', 9, 'italic'))
        self._table_placeholder.pack(anchor='w')

        # Estado inicial AFD2
        init_frame = tk.Frame(inner, bg=c['bg_panel'])
        init_frame.pack(fill=tk.X, padx=12, pady=(0, 2))
        self._lbl_initial = tk.Label(init_frame, text=t('eq.initial_state'), bg=c['bg_panel'],
                 fg=c['text_secondary'], font=('Segoe UI', 9))
        self._lbl_initial.pack(side=tk.LEFT, padx=(0, 4))

        self._init_combo = ttk.Combobox(
            init_frame, textvariable=self._afd2_estado_inicial_var,
            state='readonly', width=20, font=('Consolas', 10))
        self._init_combo.pack(side=tk.LEFT)

        # Estados finales AFD2
        self._lbl_finals_title = tk.Label(inner, text=t('eq.finals_title'), bg=c['bg_panel'],
                 fg=c['text'], font=('Segoe UI', 10, 'bold'))
        self._lbl_finals_title.pack(anchor='w', padx=12, pady=(4, 2))

        self._finales_frame = tk.Frame(inner, bg=c['bg_panel'])
        self._finales_frame.pack(fill=tk.X, padx=12, pady=(0, 4))

        self._finales_placeholder = tk.Label(
            self._finales_frame, text=t('eq.finals_placeholder'),
            bg=c['bg_panel'], fg=c['text_secondary'],
            font=('Segoe UI', 9, 'italic'))
        self._finales_placeholder.pack(anchor='w')

        self._separator(inner)

        # Botón verificar
        self._btn_verificar = tk.Button(
            inner, text=t('eq.btn_verify'),
            command=self._verificar_equivalencia,
            bg=c['accent'], fg=c['text_on_accent'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            font=('Segoe UI', 10, 'bold'), relief='flat', cursor='hand2',
            padx=12, pady=4)
        self._btn_verificar.pack(anchor='w', padx=12, pady=(4, 4))

        # Resultado
        self._result_frame = tk.Frame(inner, bg=c['bg_panel'])
        self._result_frame.pack(fill=tk.X, padx=12, pady=(0, 4))

        self._result_label = tk.Label(
            self._result_frame, text='', bg=c['bg_panel'],
            font=('Segoe UI', 14, 'bold'), anchor='center')
        self._result_label.pack(fill=tk.X)

        self._witness_label = tk.Label(
            self._result_frame, text='', bg=c['bg_panel'],
            fg=c['text'], font=('Consolas', 10), wraplength=500,
            justify='left')
        self._witness_label.pack(fill=tk.X, pady=(4, 0))

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

        # Header
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
                        'Transición inválida',
                        t('msg.invalid_trans', q=estado, s=simbolo, v=val))
                    return None
                afd2.definir_transicion(estado, simbolo, val)

        return afd2

    # ── Verificar equivalencia ───────────────────────────────────

    def _verificar_equivalencia(self):
        c = theme.colors

        afd1 = self.app.current_automaton
        if not afd1 or not isinstance(afd1, AFD):
            messagebox.showwarning(t('dlg.invalid_afd'), t('msg.not_afd'))
            return
        if not afd1.estado_inicial or not afd1.estados:
            messagebox.showwarning(t('dlg.incomplete_afd'), t('msg.afd_incomplete'))
            return

        afd2 = self._construir_afd2()
        if afd2 is None:
            return

        try:
            resultado = afd1.son_equivalentes(afd2)
        except Exception as e:
            messagebox.showerror('Error',
                                 f'Error al verificar equivalencia:\n{str(e)}')
            self.app.add_log(f'Error en equivalencia: {str(e)}', 'error')
            return

        equivalentes = resultado.get('equivalentes', False)
        cadena_testigo = resultado.get('cadena_testigo', None)

        if equivalentes:
            self._result_label.configure(text=t('eq.equivalent'), fg=c['green'])
            self._witness_label.configure(text='')
            self.app.add_log(t('log.equiv_yes'), 'success')
        else:
            self._result_label.configure(text=t('eq.different'), fg=c['red'])
            if cadena_testigo is not None:
                self._witness_label.configure(
                    text=t('eq.witness', w=cadena_testigo),
                    fg=c['red'])
                self.app.add_log(
                    t('log.equiv_no', w=cadena_testigo), 'error')
            else:
                self._witness_label.configure(
                    text=t('eq.no_witness'), fg=c['text'])
                self.app.add_log(t('log.equiv_no_witness'), 'error')

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
        self._result_label.configure(bg=c['bg_panel'])
        self._witness_label.configure(bg=c['bg_panel'])
        self._afd1_info.configure(bg=c['bg_panel'], fg=c['text'])

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
            self._title.configure(text=t('eq.title'))
            self._lbl_afd1_desc.configure(text=t('eq.afd1_info'))
            self._lbl_afd2_title.configure(text=t('eq.afd2_title'))
            self._lbl_states.configure(text=t('eq.states_label'))
            self._lbl_alphabet.configure(text=t('eq.alphabet_label'))
            self._lbl_initial.configure(text=t('eq.initial_state'))
            self._lbl_finals_title.configure(text=t('eq.finals_title'))
            self._btn_gen_table.configure(text=t('eq.gen_table'))
            self._table_label.configure(text=t('eq.table_title'))
            self._btn_verificar.configure(text=t('eq.btn_verify'))
            # table_placeholder if visible
            if hasattr(self,'_table_placeholder') and self._table_placeholder.winfo_exists():
                self._table_placeholder.configure(text=t('eq.table_placeholder'))
            # finals placeholder if visible
            if hasattr(self,'_finales_placeholder') and self._finales_placeholder.winfo_exists():
                self._finales_placeholder.configure(text=t('eq.finals_placeholder'))
        except Exception:
            pass
