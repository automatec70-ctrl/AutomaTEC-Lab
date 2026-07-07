"""
StringProcessor — Panel para procesar cadenas a través del autómata.

Contiene:
  - Campo de entrada para la cadena w
  - Botón Verificar: procesa la cadena y muestra la traza completa
  - Botón Modo Paso a Paso: habilita la ejecución paso a paso
  - Visualización de traza: cada paso (estado, cadena restante, símbolo leído)
  - Controles Paso a Paso: ◀ Anterior / Siguiente ▶
  - Resultado: ACEPTADA (verde) o RECHAZADA (rojo)
  - Resaltado del estado actual en el canvas durante paso a paso
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict

from ui.theme import theme
from ui.i18n import lang, t
from core.afd import AFD
from core.afn import AFN
from core.afn_lambda import AFNLambda


class StringProcessor(tk.Frame):
    """Panel para procesar cadenas a través del autómata."""

    def __init__(self, parent, app_ref, **kwargs):
        c = theme.colors
        super().__init__(parent, bg=c['bg_panel'], **kwargs)
        self.app = app_ref

        # State for step-by-step
        self._traza: List[Dict] = []
        self._traza_aceptada: bool = False
        self._paso_actual: int = -1
        self._modo_paso: bool = False
        self._cadena_var = tk.StringVar()

        self._build_ui()
        theme.on_change(self._on_theme_change)

    # ── Construcción de la UI ────────────────────────────────────

    def _build_ui(self):
        c = theme.colors

        # ── Sección de entrada ───────────────────────────────────
        self._input_frame = tk.Frame(self, bg=c['bg_panel'])
        self._input_frame.pack(fill=tk.X, padx=12, pady=(10, 4))

        self._string_w_label = tk.Label(self._input_frame, text=t('proc.string_w'), bg=c['bg_panel'], fg=c['text'],
                 font=('Segoe UI', 10))
        self._string_w_label.pack(side=tk.LEFT, padx=(0, 6))

        self._entry = tk.Entry(
            self._input_frame, textvariable=self._cadena_var,
            bg=c['bg_input'], fg=c['text'], insertbackground=c['text'],
            font=('Consolas', 11), relief='flat', width=20,
            highlightthickness=1, highlightcolor=c['accent'],
            highlightbackground=c['border']
        )
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        self._entry.bind('<Return>', lambda e: self._verificar())

        # Placeholder hint
        self._hint_label = tk.Label(
            self, text=t('proc.hint'), bg=c['bg_panel'],
            fg=c['text_secondary'], font=('Segoe UI', 9, 'italic')
        )
        self._hint_label.place(in_=self._entry, x=8, y=0, relheight=1.0, anchor='w')
        self._cadena_var.trace_add('write', self._on_entry_change)

        # ── Botones ──────────────────────────────────────────────
        self._btn_frame = tk.Frame(self, bg=c['bg_panel'])
        self._btn_frame.pack(fill=tk.X, padx=12, pady=(0, 4))

        self._btn_verificar = tk.Button(
            self._btn_frame, text=t('proc.verify'), command=self._verificar,
            bg=c['green'], fg='#FFFFFF', activebackground='#059669',
            activeforeground='#FFFFFF', font=('Segoe UI', 9, 'bold'),
            relief='flat', cursor='hand2', padx=10
        )
        self._btn_verificar.pack(side=tk.LEFT, padx=(0, 4))

        self._btn_paso = tk.Button(
            self._btn_frame, text=t('proc.step_mode'),
            command=self._iniciar_paso_a_paso,
            bg=c['accent'], fg=c['text_on_accent'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            font=('Segoe UI', 9), relief='flat', cursor='hand2', padx=10
        )
        self._btn_paso.pack(side=tk.LEFT, padx=(0, 4))

        self._btn_reset = tk.Button(
            self._btn_frame, text=t('proc.reset'), command=self._reset,
            bg=c['bg_surface'], fg=c['text'], activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'], font=('Segoe UI', 9),
            relief='flat', cursor='hand2', padx=10
        )
        self._btn_reset.pack(side=tk.LEFT)

        # ── Controles paso a paso ────────────────────────────────
        self._step_controls = tk.Frame(self, bg=c['bg_panel'])
        # Not packed initially

        self._btn_prev = tk.Button(
            self._step_controls, text=t('proc.prev'),
            command=self._paso_anterior,
            bg=c['bg_surface'], fg=c['text'], activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'], font=('Segoe UI', 9),
            relief='flat', cursor='hand2', padx=8, state=tk.DISABLED
        )
        self._btn_prev.pack(side=tk.LEFT, padx=(0, 4))

        self._step_label = tk.Label(
            self._step_controls, text='', bg=c['bg_panel'],
            fg=c['text_secondary'], font=('Consolas', 9)
        )
        self._step_label.pack(side=tk.LEFT, padx=6)

        self._btn_next = tk.Button(
            self._step_controls, text=t('proc.next'),
            command=self._paso_siguiente,
            bg=c['bg_surface'], fg=c['text'], activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'], font=('Segoe UI', 9),
            relief='flat', cursor='hand2', padx=8, state=tk.DISABLED
        )
        self._btn_next.pack(side=tk.LEFT)

        # ── Resultado ────────────────────────────────────────────
        self._result_frame = tk.Frame(self, bg=c['bg_panel'])
        self._result_frame.pack(fill=tk.X, padx=12, pady=(0, 4))

        self._result_label = tk.Label(
            self._result_frame, text='', bg=c['bg_panel'],
            font=('Segoe UI', 14, 'bold'), anchor='center'
        )
        self._result_label.pack(fill=tk.X)

        # ── Traza ───────────────────────────────────────────────
        self._trace_label_ref = tk.Label(
            self, text=t('proc.trace'), bg=c['bg_panel'],
            fg=c['text_secondary'], font=('Segoe UI', 10, 'bold')
        )
        self._trace_label_ref.pack(anchor='w', padx=12, pady=(6, 2))

        self._trace_frame = tk.Frame(self, bg=c['bg_panel'])
        self._trace_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))

        self._trace_text = tk.Text(
            self._trace_frame, bg=c['bg_input'], fg=c['text'],
            insertbackground=c['text'], selectbackground=c['accent'],
            selectforeground=c['text_on_accent'],
            font=('Consolas', 10), relief='flat', bd=0,
            height=10, wrap=tk.WORD, state=tk.DISABLED,
            highlightthickness=1, highlightcolor=c['accent'],
            highlightbackground=c['border']
        )

        trace_scroll = ttk.Scrollbar(self._trace_frame, orient=tk.VERTICAL,
                                     command=self._trace_text.yview)
        self._trace_text.configure(yscrollcommand=trace_scroll.set)
        trace_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._trace_text.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for coloring
        self._trace_text.tag_configure('step_number', foreground=c['accent'],
                                       font=('Consolas', 10, 'bold'))
        self._trace_text.tag_configure('estado', foreground=c['yellow'],
                                       font=('Consolas', 10, 'bold'))
        self._trace_text.tag_configure('simbolo', foreground=c['green'],
                                       font=('Consolas', 10, 'bold'))
        self._trace_text.tag_configure('cadena', foreground=c['text_secondary'])
        self._trace_text.tag_configure('error', foreground=c['red'],
                                       font=('Consolas', 10, 'bold'))
        self._trace_text.tag_configure('highlight_step',
                                       background='#4A2A7A',
                                       font=('Consolas', 10, 'bold'))

    # ── Lógica ───────────────────────────────────────────────────

    def _on_entry_change(self, *args):
        if self._cadena_var.get():
            self._hint_label.place_forget()
        else:
            c = theme.colors
            self._hint_label.place(in_=self._entry, x=8, y=0,
                                   relheight=1.0, anchor='w')

    def _verificar(self):
        """Procesa la cadena y muestra la traza completa."""
        automaton = self.app.current_automaton
        if not automaton:
            messagebox.showwarning(t('dlg.no_automaton'), t('msg.no_automaton'))
            return

        cadena = self._cadena_var.get()
        if not automaton.estado_inicial:
            messagebox.showwarning(t('dlg.no_initial'), t('msg.no_initial'))
            return

        try:
            resultado = automaton.procesar_cadena(cadena)
        except Exception as e:
            messagebox.showerror('Error',
                                 f'Error al procesar la cadena:\n{str(e)}')
            self.app.add_log(f'Error procesando "{cadena}": {str(e)}', 'error')
            return

        self._traza = resultado.get('traza', [])
        self._traza_aceptada = resultado.get('aceptada', False)
        self._modo_paso = False
        self._paso_actual = -1

        # Hide step controls in normal mode
        self._step_controls.pack_forget()

        # Show trace
        self._mostrar_traza_completa()

        # Show result
        self._mostrar_resultado()

        # Clear canvas highlights
        if hasattr(self.app, 'canvas_widget') and self.app.canvas_widget:
            self.app.canvas_widget.clear_highlights()

        # Log
        if self._traza_aceptada:
            self.app.add_log(t('log.accepted', w=cadena), 'success')
        else:
            self.app.add_log(t('log.rejected', w=cadena), 'error')

    def _iniciar_paso_a_paso(self):
        """Inicia el modo paso a paso."""
        automaton = self.app.current_automaton
        if not automaton:
            messagebox.showwarning('Sin autómata', 'No hay un autómata definido.')
            return

        cadena = self._cadena_var.get()
        if not automaton.estado_inicial:
            messagebox.showwarning('Sin estado inicial',
                                   'Defina un estado inicial para el autómata.')
            return

        try:
            resultado = automaton.procesar_cadena(cadena)
        except Exception as e:
            messagebox.showerror('Error',
                                 f'Error al procesar la cadena:\n{str(e)}')
            return

        self._traza = resultado.get('traza', [])
        self._traza_aceptada = resultado.get('aceptada', False)
        self._modo_paso = True
        self._paso_actual = 0

        # Show step controls (after btn_frame so they appear in the right place)
        self._step_controls.pack(fill=tk.X, padx=12, pady=(0, 4),
                                 after=self._btn_frame)

        self._mostrar_paso_actual()
        self._update_step_buttons()

        self.app.add_log(t('log.step_started', w=cadena), 'info')

    def _paso_siguiente(self):
        if self._paso_actual < len(self._traza) - 1:
            self._paso_actual += 1
            self._mostrar_paso_actual()
            self._update_step_buttons()

    def _paso_anterior(self):
        if self._paso_actual > 0:
            self._paso_actual -= 1
            self._mostrar_paso_actual()
            self._update_step_buttons()

    def _update_step_buttons(self):
        if self._paso_actual <= 0:
            self._btn_prev.configure(state=tk.DISABLED)
        else:
            self._btn_prev.configure(state=tk.NORMAL)

        if self._paso_actual >= len(self._traza) - 1:
            self._btn_next.configure(state=tk.DISABLED)
            self._mostrar_resultado()
        else:
            self._btn_next.configure(state=tk.NORMAL)
            self._result_label.configure(text='')

        total = len(self._traza) - 1
        self._step_label.configure(text=t('proc.step_label', cur=self._paso_actual, tot=total))

    def _mostrar_paso_actual(self):
        if not self._traza or self._paso_actual < 0:
            return

        self._trace_text.configure(state=tk.NORMAL)
        self._trace_text.delete('1.0', tk.END)

        for i in range(self._paso_actual + 1):
            step = self._traza[i]
            is_current = (i == self._paso_actual)
            prefix = '▶ ' if is_current else '  '

            self._trace_text.insert(tk.END, f'{prefix}Paso {i}: ',
                                    'step_number' if is_current else '')

            if 'estado' in step:
                # AFD trace
                estado = step['estado']
                simbolo = step.get('simbolo_leido', '')
                cadena_restante = step.get('cadena_restante', '')

                self._trace_text.insert(tk.END, f'Estado=')
                self._trace_text.insert(tk.END, f'{estado}', 'estado')
                if simbolo:
                    self._trace_text.insert(tk.END, f'  Lee=')
                    self._trace_text.insert(tk.END, f"'{simbolo}'", 'simbolo')
                self._trace_text.insert(tk.END, f'  Restante=')
                self._trace_text.insert(tk.END, f'"{cadena_restante}"', 'cadena')

            elif 'estados_activos' in step:
                # AFN/AFN-λ trace
                estados_activos = step['estados_activos']
                simbolo = step.get('simbolo_leido', '')
                cadena_restante = step.get('cadena_restante', '')
                clausura = step.get('clausura_lambda', None)

                estados_str = ', '.join(sorted(estados_activos)) if estados_activos else '∅'
                self._trace_text.insert(tk.END, f'Estados=')
                self._trace_text.insert(tk.END, f'{{{estados_str}}}', 'estado')
                if simbolo:
                    self._trace_text.insert(tk.END, f'  Lee=')
                    self._trace_text.insert(tk.END, f"'{simbolo}'", 'simbolo')
                if clausura is not None:
                    clausura_str = ', '.join(sorted(clausura)) if clausura else '∅'
                    self._trace_text.insert(tk.END, f'  CL_ε=')
                    self._trace_text.insert(tk.END, f'{{{clausura_str}}}', 'estado')
                self._trace_text.insert(tk.END, f'  Restante=')
                self._trace_text.insert(tk.END, f'"{cadena_restante}"', 'cadena')

            self._trace_text.insert(tk.END, '\n')

        self._trace_text.configure(state=tk.DISABLED)
        self._highlight_current_state(step)

    def _mostrar_traza_completa(self):
        self._trace_text.configure(state=tk.NORMAL)
        self._trace_text.delete('1.0', tk.END)

        if not self._traza:
            self._trace_text.insert(tk.END, t('proc.no_trace'), 'cadena')
            self._trace_text.configure(state=tk.DISABLED)
            return

        for i, step in enumerate(self._traza):
            self._trace_text.insert(tk.END, f'  Paso {i}: ', 'step_number')

            if 'estado' in step:
                estado = step['estado']
                simbolo = step.get('simbolo_leido', '')
                cadena_restante = step.get('cadena_restante', '')
                self._trace_text.insert(tk.END, f'Estado=')
                self._trace_text.insert(tk.END, f'{estado}', 'estado')
                if simbolo:
                    self._trace_text.insert(tk.END, f'  Lee=')
                    self._trace_text.insert(tk.END, f"'{simbolo}'", 'simbolo')
                self._trace_text.insert(tk.END, f'  Restante=')
                self._trace_text.insert(tk.END, f'"{cadena_restante}"', 'cadena')

            elif 'estados_activos' in step:
                estados_activos = step['estados_activos']
                simbolo = step.get('simbolo_leido', '')
                cadena_restante = step.get('cadena_restante', '')
                clausura = step.get('clausura_lambda', None)
                estados_str = ', '.join(sorted(estados_activos)) if estados_activos else '∅'
                self._trace_text.insert(tk.END, f'Estados=')
                self._trace_text.insert(tk.END, f'{{{estados_str}}}', 'estado')
                if simbolo:
                    self._trace_text.insert(tk.END, f'  Lee=')
                    self._trace_text.insert(tk.END, f"'{simbolo}'", 'simbolo')
                if clausura is not None:
                    clausura_str = ', '.join(sorted(clausura)) if clausura else '∅'
                    self._trace_text.insert(tk.END, f'  CL_ε=')
                    self._trace_text.insert(tk.END, f'{{{clausura_str}}}', 'estado')
                self._trace_text.insert(tk.END, f'  Restante=')
                self._trace_text.insert(tk.END, f'"{cadena_restante}"', 'cadena')

            self._trace_text.insert(tk.END, '\n')

        self._trace_text.configure(state=tk.DISABLED)

    def _mostrar_resultado(self):
        c = theme.colors
        if self._traza_aceptada:
            self._result_label.configure(text=t('proc.accepted'), fg=c['green'])
        else:
            self._result_label.configure(text=t('proc.rejected'), fg=c['red'])

    def _highlight_current_state(self, step):
        if not hasattr(self.app, 'canvas_widget') or not self.app.canvas_widget:
            return

        states = set()
        if 'estado' in step:
            estado = step['estado']
            if estado:
                states.add(estado)
        elif 'estados_activos' in step:
            states = step['estados_activos']

        self.app.canvas_widget.set_highlighted_states(states)

    def _reset(self):
        self._cadena_var.set('')
        self._traza = []
        self._traza_aceptada = False
        self._modo_paso = False
        self._paso_actual = -1

        self._step_controls.pack_forget()
        self._result_label.configure(text='')

        self._trace_text.configure(state=tk.NORMAL)
        self._trace_text.delete('1.0', tk.END)
        self._trace_text.configure(state=tk.DISABLED)

        if hasattr(self.app, 'canvas_widget') and self.app.canvas_widget:
            self.app.canvas_widget.clear_highlights()

    # ── Tema ─────────────────────────────────────────────────────

    def _on_theme_change(self):
        c = theme.colors
        self.configure(bg=c['bg_panel'])
        self._input_frame.configure(bg=c['bg_panel'])
        self._btn_frame.configure(bg=c['bg_panel'])
        self._result_frame.configure(bg=c['bg_panel'])
        self._trace_frame.configure(bg=c['bg_panel'])

        self._trace_text.tag_configure('step_number', foreground=c['accent'],
                                       font=('Consolas', 10, 'bold'))
        self._trace_text.tag_configure('estado', foreground=c['yellow'],
                                       font=('Consolas', 10, 'bold'))
        self._trace_text.tag_configure('simbolo', foreground=c['green'],
                                       font=('Consolas', 10, 'bold'))
        self._trace_text.tag_configure('cadena', foreground=c['text_secondary'])
        self._trace_text.tag_configure('error', foreground=c['red'],
                                       font=('Consolas', 10, 'bold'))
        self._trace_text.tag_configure('highlight_step',
                                       background='#4A2A7A',
                                       font=('Consolas', 10, 'bold'))

        self._btn_verificar.configure(bg=c['green'])
        self._btn_paso.configure(bg=c['accent'], fg=c['text_on_accent'])
        self._btn_reset.configure(bg=c['bg_surface'], fg=c['text'])
        self._btn_prev.configure(bg=c['bg_surface'], fg=c['text'])
        self._btn_next.configure(bg=c['bg_surface'], fg=c['text'])
        self._step_label.configure(bg=c['bg_panel'], fg=c['text_secondary'])
        self._result_label.configure(bg=c['bg_panel'])
        self._trace_label_ref.configure(bg=c['bg_panel'], fg=c['text_secondary'])

        if self._traza_aceptada:
            self._result_label.configure(fg=c['green'])
        elif self._result_label.cget('text'):
            self._result_label.configure(fg=c['red'])

        if not self._cadena_var.get():
            self._hint_label.configure(bg=c['bg_panel'], fg=c['text_secondary'])
            self._hint_label.place(in_=self._entry, x=8, y=0,
                                   relheight=1.0, anchor='w')

    def refresh_lang(self):
        """Refresh all UI text after language change."""
        try:
            self._string_w_label.configure(text=t('proc.string_w'))
            self._hint_label.configure(text=t('proc.hint'))
            self._btn_verificar.configure(text=t('proc.verify'))
            self._btn_paso.configure(text=t('proc.step_mode'))
            self._btn_reset.configure(text=t('proc.reset'))
            self._btn_prev.configure(text=t('proc.prev'))
            self._btn_next.configure(text=t('proc.next'))
            self._trace_label_ref.configure(text=t('proc.trace'))
        except Exception:
            pass
