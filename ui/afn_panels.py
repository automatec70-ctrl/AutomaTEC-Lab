"""
Paneles AFN — Construcción de subconjuntos, eliminación de λ, operaciones AFN, cadena de conversión.

Contiene:
1. SubsetConstructionPanel — AFN/AFN-λ → AFD
2. EpsilonEliminationPanel — AFN-λ → AFN
3. AFNOperationsPanel — Operaciones que retornan AFN/AFN-λ
4. ConversionChainPanel — AFN-λ → AFN → AFD → AFD Mínimo
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from ui.i18n import lang, t
from core.afd import AFD
from core.afn import AFN
from core.afn_lambda import AFNLambda, LAMBDA
from ui.theme import theme


# ================================================================
# SubsetConstructionPanel — AFN/AFN-λ → AFD
# ================================================================

class SubsetConstructionPanel(tk.Frame):
    """Panel para la construcción de subconjuntos (AFN/AFN-λ → AFD)."""

    def __init__(self, parent, app_ref, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme
        self.app = app_ref  # referencia a AutomaTEC-Lab
        self._result_afd = None
        self._pasos = []
        self._step_index = 0
        self._setup_ui()
        self.theme.on_change(self._on_theme_change)

    def _setup_ui(self):
        c = self.theme.colors
        self.configure(bg=c['bg_panel'])

        # Botones
        btn_frame = tk.Frame(self, bg=c['bg_panel'])
        btn_frame.pack(fill=tk.X, padx=8, pady=6)

        self.btn_convertir = tk.Button(
            btn_frame, text=t('afn.subset.btn_convert'),
            command=self._convertir,
            bg=c['accent'], fg=c['text_on_accent'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            relief='flat', font=('Segoe UI', 9, 'bold'),
            padx=12, pady=4, cursor='hand2'
        )
        self.btn_convertir.pack(side=tk.LEFT, padx=4)

        self.btn_paso = tk.Button(
            btn_frame, text=t('afn.subset.btn_step'),
            command=self._paso_a_paso,
            bg=c['bg_surface'], fg=c['text'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            relief='flat', font=('Segoe UI', 9),
            padx=10, pady=4, cursor='hand2'
        )
        self.btn_paso.pack(side=tk.LEFT, padx=4)

        self.btn_next_step = tk.Button(
            btn_frame, text=t('afn.subset.btn_next'),
            command=self._next_step,
            bg=c['bg_surface'], fg=c['text'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            relief='flat', font=('Segoe UI', 9),
            padx=10, pady=4, cursor='hand2'
        )
        self.btn_next_step.pack(side=tk.LEFT, padx=4)
        self.btn_next_step.configure(state=tk.DISABLED)

        self.btn_usar = tk.Button(
            btn_frame, text=t('afn.subset.btn_use'),
            command=self._usar_resultado,
            bg=c['green'], fg='#FFFFFF',
            activebackground='#059669', activeforeground='#FFFFFF',
            relief='flat', font=('Segoe UI', 9),
            padx=10, pady=4, cursor='hand2'
        )
        self.btn_usar.pack(side=tk.RIGHT, padx=4)
        self.btn_usar.configure(state=tk.DISABLED)

        # Área de resultados
        result_frame = tk.Frame(self, bg=c['bg_panel'])
        result_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.result_text = tk.Text(
            result_frame, wrap=tk.WORD, state=tk.DISABLED,
            bg=c['bg_input'], fg=c['text'],
            font=('Consolas', 9), relief='flat',
            padx=8, pady=6, height=12
        )
        result_scroll = ttk.Scrollbar(
            result_frame, orient=tk.VERTICAL, command=self.result_text.yview
        )
        self.result_text.configure(yscrollcommand=result_scroll.set)
        result_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tags para colores
        self.result_text.tag_configure('header', foreground=c['accent'],
                                       font=('Consolas', 10, 'bold'))
        self.result_text.tag_configure('step', foreground=c['green'])
        self.result_text.tag_configure('mapping', foreground=c['yellow'])
        self.result_text.tag_configure('error', foreground=c['red'])

    def _convertir(self):
        """Ejecuta la construcción de subconjuntos completa."""
        automaton = self.app.current_automaton
        if not isinstance(automaton, (AFN, AFNLambda)):
            messagebox.showwarning(t('dlg.not_afn'), t('msg.not_afn'))
            return
        if not automaton.estados or not automaton.estado_inicial:
            messagebox.showwarning(t('dlg.no_automaton'), t('msg.no_automaton'))
            return

        try:
            resultado = automaton.construccion_subconjuntos()
            self._result_afd = resultado['afd']
            self._pasos = resultado['pasos']
            self._mapeo = resultado['mapeo']
            self._step_index = 0

            self._mostrar_resultado_completo()
            self.btn_usar.configure(state=tk.NORMAL)
            self.app.add_log(t('log.subset_done'), "success")
        except Exception as e:
            messagebox.showerror("Error", f"Error en construcción de subconjuntos:\n{str(e)}")
            self.app.add_log(f"Error en construcción de subconjuntos: {str(e)}", "error")

    def _paso_a_paso(self):
        """Inicia el modo paso a paso."""
        automaton = self.app.current_automaton
        if not isinstance(automaton, (AFN, AFNLambda)):
            messagebox.showwarning(t('dlg.not_afn'), t('msg.not_afn'))
            return
        if not automaton.estados or not automaton.estado_inicial:
            messagebox.showwarning(t('dlg.no_automaton'), t('msg.no_automaton'))
            return

        try:
            resultado = automaton.construccion_subconjuntos()
            self._result_afd = resultado['afd']
            self._pasos = resultado['pasos']
            self._mapeo = resultado['mapeo']
            self._step_index = 0

            self.btn_next_step.configure(state=tk.NORMAL)
            self._show_current_step()
            self.app.add_log(t('log.subset_started'), "info")
        except Exception as e:
            messagebox.showerror("Error", f"Error:\n{str(e)}")

    def _next_step(self):
        """Muestra el siguiente paso."""
        if self._step_index < len(self._pasos):
            self._show_current_step()
            self._step_index += 1
        else:
            self.btn_next_step.configure(state=tk.DISABLED)
            self.btn_usar.configure(state=tk.NORMAL)
            self._append_text(t('afn.subset.completed'), 'header')
            self.app.add_log(t('log.subset_step_done'), "success")

    def _show_current_step(self):
        """Muestra el paso actual."""
        if self._step_index >= len(self._pasos):
            return

        paso = self._pasos[self._step_index]
        self.result_text.configure(state=tk.NORMAL)

        if self._step_index == 0:
            self.result_text.delete('1.0', tk.END)

        self.result_text.insert(tk.END, f"\n{'═' * 50}\n", 'header')
        self.result_text.insert(tk.END, f"{paso['descripcion']}\n\n", 'step')

        if 'conjunto' in paso:
            conjunto_str = '{' + ', '.join(paso['conjunto']) + '}'
            self.result_text.insert(tk.END, f"  Conjunto: {conjunto_str}\n", 'mapping')

        if 'transiciones_generadas' in paso:
            for t in paso['transiciones_generadas']:
                self.result_text.insert(
                    tk.END,
                    f"  δ({paso['estado_actual']}, {t['simbolo']}) → {t.get('nombre_destino', '')}\n",
                    'mapping'
                )
                if 'conjunto_destino' in t:
                    dest_str = '{' + ', '.join(t['conjunto_destino']) + '}'
                    self.result_text.insert(tk.END, f"    = {dest_str}\n", 'step')

        if 'clausura_lambda' in paso and paso['clausura_lambda']:
            cl_str = '{' + ', '.join(paso['clausura_lambda']) + '}'
            self.result_text.insert(tk.END, f"  CL_ε: {cl_str}\n", 'step')

        self.result_text.configure(state=tk.DISABLED)
        self.result_text.see(tk.END)

    def _mostrar_resultado_completo(self):
        """Muestra el resultado completo de la conversión."""
        self.result_text.configure(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)

        afd = self._result_afd

        self.result_text.insert(tk.END, "═ Construcción de Subconjuntos ═\n\n", 'header')

        # Pasos
        for i, paso in enumerate(self._pasos):
            self.result_text.insert(tk.END, f"Paso {i}: ", 'step')
            self.result_text.insert(tk.END, f"{paso['descripcion']}\n")
            for t in paso.get('transiciones_generadas', []):
                self.result_text.insert(
                    tk.END,
                    f"  δ({paso['estado_actual']}, {t['simbolo']}) → {t.get('nombre_destino', '?')}\n"
                )

        # Mapeo
        self.result_text.insert(tk.END, "\n═ Mapeo de estados ═\n", 'header')
        for nombre, conjunto in sorted(self._mapeo.items()):
            conj_str = '{' + ', '.join(conjunto) + '}'
            self.result_text.insert(tk.END, f"  {nombre} = {conj_str}\n", 'mapping')

        # AFD resultante
        self.result_text.insert(tk.END, f"\n═ AFD Resultante ═\n", 'header')
        self.result_text.insert(tk.END, f"  Estados: {sorted(afd.estados)}\n")
        self.result_text.insert(tk.END, f"  Alfabeto: {sorted(afd.alfabeto)}\n")
        self.result_text.insert(tk.END, f"  Inicial: {afd.estado_inicial}\n")
        self.result_text.insert(tk.END, f"  Finales: {sorted(afd.estados_finales)}\n")
        self.result_text.insert(tk.END, f"  |Q| = {len(afd.estados)}\n")

        # Tabla de transiciones
        self.result_text.insert(tk.END, "\n  Tabla δ:\n", 'step')
        for estado in sorted(afd.estados):
            for simbolo in sorted(afd.alfabeto):
                dest = afd.delta.get(estado, {}).get(simbolo, '—')
                self.result_text.insert(tk.END, f"    δ({estado}, {simbolo}) = {dest}\n")

        self.result_text.configure(state=tk.DISABLED)

    def _usar_resultado(self):
        """Reemplaza el autómata actual con el AFD resultante."""
        if self._result_afd is None:
            return
        self.app.current_automaton = self._result_afd
        self.app.current_tipo = 'AFD'
        self.app.on_automaton_changed()
        self.app.add_log(t('log.afd_result_set'), "success")

    def _append_text(self, text, tag=None):
        """Agrega texto al área de resultados."""
        self.result_text.configure(state=tk.NORMAL)
        if tag:
            self.result_text.insert(tk.END, text, tag)
        else:
            self.result_text.insert(tk.END, text)
        self.result_text.configure(state=tk.DISABLED)
        self.result_text.see(tk.END)

    def refresh_lang(self):
        try:
            self.btn_convertir.configure(text=t('afn.subset.btn_convert'))
            self.btn_paso.configure(text=t('afn.subset.btn_step'))
            self.btn_next_step.configure(text=t('afn.subset.btn_next'))
            self.btn_usar.configure(text=t('afn.subset.btn_use'))
        except Exception:
            pass

    def _on_theme_change(self):
        c = self.theme.colors
        self.configure(bg=c['bg_panel'])
        self.result_text.configure(bg=c['bg_input'], fg=c['text'])
        self.result_text.tag_configure('header', foreground=c['accent'],
                                       font=('Consolas', 10, 'bold'))
        self.result_text.tag_configure('step', foreground=c['green'])
        self.result_text.tag_configure('mapping', foreground=c['yellow'])
        self.result_text.tag_configure('error', foreground=c['red'])
        self.btn_convertir.configure(bg=c['accent'], fg=c['text_on_accent'])
        self.btn_paso.configure(bg=c['bg_surface'], fg=c['text'])
        self.btn_next_step.configure(bg=c['bg_surface'], fg=c['text'])
        self.btn_usar.configure(bg=c['green'])


# ================================================================
# EpsilonEliminationPanel — AFN-λ → AFN
# ================================================================

class EpsilonEliminationPanel(tk.Frame):
    """Panel para eliminar transiciones lambda (AFN-λ → AFN)."""

    def __init__(self, parent, app_ref, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme
        self.app = app_ref
        self._result_afn = None
        self._setup_ui()
        self.theme.on_change(self._on_theme_change)

    def _setup_ui(self):
        c = self.theme.colors
        self.configure(bg=c['bg_panel'])

        # Botones
        btn_frame = tk.Frame(self, bg=c['bg_panel'])
        btn_frame.pack(fill=tk.X, padx=8, pady=6)

        self.btn_eliminar = tk.Button(
            btn_frame, text=t('afn.epsilon.btn_eliminate'),
            command=self._eliminar_lambda,
            bg=c['accent'], fg=c['text_on_accent'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            relief='flat', font=('Segoe UI', 9, 'bold'),
            padx=12, pady=4, cursor='hand2'
        )
        self.btn_eliminar.pack(side=tk.LEFT, padx=4)

        self.btn_usar = tk.Button(
            btn_frame, text=t('afn.subset.btn_use'),
            command=self._usar_resultado,
            bg=c['green'], fg='#FFFFFF',
            relief='flat', font=('Segoe UI', 9),
            padx=10, pady=4, cursor='hand2'
        )
        self.btn_usar.pack(side=tk.RIGHT, padx=4)
        self.btn_usar.configure(state=tk.DISABLED)

        # Resultado
        result_frame = tk.Frame(self, bg=c['bg_panel'])
        result_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.result_text = tk.Text(
            result_frame, wrap=tk.WORD, state=tk.DISABLED,
            bg=c['bg_input'], fg=c['text'],
            font=('Consolas', 9), relief='flat',
            padx=8, pady=6, height=12
        )
        scroll = ttk.Scrollbar(result_frame, orient=tk.VERTICAL,
                               command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.result_text.tag_configure('header', foreground=c['accent'],
                                       font=('Consolas', 10, 'bold'))
        self.result_text.tag_configure('closure', foreground=c['green'])
        self.result_text.tag_configure('new_trans', foreground=c['yellow'])

    def _eliminar_lambda(self):
        """Elimina las transiciones lambda."""
        automaton = self.app.current_automaton
        if not isinstance(automaton, AFNLambda):
            messagebox.showwarning("Tipo incorrecto",
                                   "Se requiere un AFN-λ para eliminar λ-transiciones.")
            return
        if not automaton.tiene_transiciones_lambda():
            messagebox.showinfo("Sin λ-transiciones",
                                "El AFN-λ actual no tiene transiciones λ.")
            return

        try:
            # Tabla de clausuras
            tabla_clausuras = automaton.tabla_clausuras_lambda()

            # Eliminar lambda
            afn_result = automaton.eliminar_lambda_transiciones()
            self._result_afn = afn_result

            # Mostrar resultado
            self.result_text.configure(state=tk.NORMAL)
            self.result_text.delete('1.0', tk.END)

            # Clausuras
            self.result_text.insert(tk.END, "═ Tabla de ε-Clausuras ═\n\n", 'header')
            for estado, clausura in sorted(tabla_clausuras.items()):
                cl_str = '{' + ', '.join(clausura) + '}'
                self.result_text.insert(tk.END, f"  CL_ε({estado}) = {cl_str}\n", 'closure')

            # AFN resultante
            self.result_text.insert(tk.END, "\n═ AFN sin λ-transiciones ═\n", 'header')
            self.result_text.insert(tk.END, f"  Estados: {sorted(afn_result.estados)}\n")
            self.result_text.insert(tk.END, f"  Alfabeto: {sorted(afn_result.alfabeto)}\n")
            self.result_text.insert(tk.END, f"  Inicial: {afn_result.estado_inicial}\n")
            self.result_text.insert(tk.END, f"  Finales: {sorted(afn_result.estados_finales)}\n")

            # Transiciones
            self.result_text.insert(tk.END, "\n  Transiciones:\n", 'new_trans')
            for estado in sorted(afn_result.delta):
                for simbolo in sorted(afn_result.delta[estado]):
                    destinos = afn_result.delta[estado][simbolo]
                    dest_str = '{' + ', '.join(sorted(destinos)) + '}'
                    self.result_text.insert(
                        tk.END, f"    δ({estado}, {simbolo}) = {dest_str}\n"
                    )

            self.result_text.configure(state=tk.DISABLED)
            self.btn_usar.configure(state=tk.NORMAL)
            self.app.add_log(t('log.epsilon_done'), "success")

        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar λ-transiciones:\n{str(e)}")
            self.app.add_log(f"Error: {str(e)}", "error")

    def _usar_resultado(self):
        if self._result_afn is None:
            return
        self.app.current_automaton = self._result_afn
        self.app.current_tipo = 'AFN'
        self.app.on_automaton_changed()
        self.app.add_log(t('log.afn_set'), "success")

    def refresh_lang(self):
        try:
            self.btn_eliminar.configure(text=t('afn.epsilon.btn_eliminate'))
            self.btn_usar.configure(text=t('afn.epsilon.btn_use'))
        except Exception:
            pass

    def _on_theme_change(self):
        c = self.theme.colors
        self.configure(bg=c['bg_panel'])
        self.result_text.configure(bg=c['bg_input'], fg=c['text'])
        self.result_text.tag_configure('header', foreground=c['accent'],
                                       font=('Consolas', 10, 'bold'))
        self.result_text.tag_configure('closure', foreground=c['green'])
        self.result_text.tag_configure('new_trans', foreground=c['yellow'])
        self.btn_eliminar.configure(bg=c['accent'], fg=c['text_on_accent'])
        self.btn_usar.configure(bg=c['green'])


# ================================================================
# AFNOperationsPanel — Operaciones que retornan AFN/AFN-λ
# ================================================================

class AFNOperationsPanel(tk.Frame):
    """Panel para operaciones sobre AFN/AFN-λ que retornan AFN/AFN-λ."""

    def __init__(self, parent, app_ref, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme
        self.app = app_ref
        self._result = None
        self._result_tipo = None
        self._setup_ui()
        self.theme.on_change(self._on_theme_change)

    def _setup_ui(self):
        c = self.theme.colors
        self.configure(bg=c['bg_panel'])

        # Etiqueta
        self.lbl_ops_title = tk.Label(
            self, text=t('afn.ops.title'),
            bg=c['bg_panel'], fg=c['text'],
            font=('Segoe UI', 10, 'bold')
        )
        self.lbl_ops_title.pack(anchor='w', padx=8, pady=(6, 2))

        # Botones de operaciones
        btn_frame = tk.Frame(self, bg=c['bg_panel'])
        btn_frame.pack(fill=tk.X, padx=8, pady=4)

        btn_style = dict(
            bg=c['bg_surface'], fg=c['text'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            relief='flat', font=('Segoe UI', 9),
            padx=10, pady=4, cursor='hand2'
        )

        self.btn_kleene = tk.Button(
            btn_frame, text=t('afn.ops.btn_kleene'),
            command=lambda: self._aplicar_operacion('kleene'),
            **btn_style
        )
        self.btn_kleene.pack(side=tk.LEFT, padx=3)

        self.btn_positive = tk.Button(
            btn_frame, text=t('afn.ops.btn_positive'),
            command=lambda: self._aplicar_operacion('positive'),
            **btn_style
        )
        self.btn_positive.pack(side=tk.LEFT, padx=3)

        self.btn_reverse = tk.Button(
            btn_frame, text=t('afn.ops.btn_reverse'),
            command=lambda: self._aplicar_operacion('reverse'),
            **btn_style
        )
        self.btn_reverse.pack(side=tk.LEFT, padx=3)

        self.btn_usar = tk.Button(
            btn_frame, text=t('afn.ops.btn_usar'),
            command=self._usar_resultado,
            bg=c['green'], fg='#FFFFFF',
            relief='flat', font=('Segoe UI', 9),
            padx=10, pady=4, cursor='hand2'
        )
        self.btn_usar.pack(side=tk.RIGHT, padx=3)
        self.btn_usar.configure(state=tk.DISABLED)

        # Resultado
        result_frame = tk.Frame(self, bg=c['bg_panel'])
        result_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.result_text = tk.Text(
            result_frame, wrap=tk.WORD, state=tk.DISABLED,
            bg=c['bg_input'], fg=c['text'],
            font=('Consolas', 9), relief='flat',
            padx=8, pady=6, height=12
        )
        scroll = ttk.Scrollbar(result_frame, orient=tk.VERTICAL,
                               command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.result_text.tag_configure('header', foreground=c['accent'],
                                       font=('Consolas', 10, 'bold'))
        self.result_text.tag_configure('info', foreground=c['green'])

    def _aplicar_operacion(self, operacion):
        """Aplica la operación seleccionada."""
        automaton = self.app.current_automaton
        if not isinstance(automaton, (AFN, AFNLambda)):
            messagebox.showwarning("Tipo incorrecto",
                                   "Se requiere un AFN o AFN-λ.")
            return
        if not automaton.estados or not automaton.estado_inicial:
            messagebox.showwarning("Sin autómata",
                                   "El autómata no está definido.")
            return

        try:
            nombre_op = ''
            if operacion == 'kleene':
                result = automaton.clausura_kleene()
                nombre_op = 'Clausura de Kleene (A*)'
            elif operacion == 'positive':
                result = automaton.clausura_positiva()
                nombre_op = 'Clausura Positiva (A+)'
            elif operacion == 'reverse':
                result = automaton.reverso()
                nombre_op = 'Reverso (Aᴿ)'
            else:
                return

            self._result = result
            self._result_tipo = 'AFN-λ' if isinstance(result, AFNLambda) else 'AFN'

            # Mostrar resultado
            self.result_text.configure(state=tk.NORMAL)
            self.result_text.delete('1.0', tk.END)

            self.result_text.insert(tk.END, f"═ {nombre_op} ═\n\n", 'header')
            self.result_text.insert(tk.END, f"  Tipo: {self._result_tipo}\n", 'info')
            self.result_text.insert(tk.END, f"  Estados: {sorted(result.estados)}\n")
            self.result_text.insert(tk.END, f"  Alfabeto: {sorted(result.alfabeto)}\n")
            self.result_text.insert(tk.END, f"  Inicial: {result.estado_inicial}\n")
            self.result_text.insert(tk.END, f"  Finales: {sorted(result.estados_finales)}\n")

            # Transiciones
            self.result_text.insert(tk.END, "\n  Transiciones:\n")
            for estado in sorted(result.delta):
                for simbolo in sorted(result.delta[estado]):
                    destinos = result.delta[estado][simbolo]
                    if isinstance(destinos, set):
                        dest_str = '{' + ', '.join(sorted(destinos)) + '}'
                    else:
                        dest_str = str(destinos)
                    self.result_text.insert(
                        tk.END, f"    δ({estado}, {simbolo}) = {dest_str}\n"
                    )

            self.result_text.insert(tk.END, f"\n  |Q| = {len(result.estados)}\n", 'info')
            self.result_text.configure(state=tk.DISABLED)

            self.btn_usar.configure(state=tk.NORMAL)
            self.app.add_log(t('log.afn_op_done', op=nombre_op), "success")

        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar operación:\n{str(e)}")
            self.app.add_log(f"Error: {str(e)}", "error")

    def _usar_resultado(self):
        if self._result is None:
            return
        self.app.current_automaton = self._result
        self.app.current_tipo = self._result_tipo
        self.app.on_automaton_changed()
        self.app.add_log(t('log.result_set', t=self._result_tipo), "success")

    def refresh_lang(self):
        try:
            self.lbl_ops_title.configure(text=t('afn.ops.title'))
            self.btn_kleene.configure(text=t('afn.ops.btn_kleene'))
            self.btn_positive.configure(text=t('afn.ops.btn_positive'))
            self.btn_reverse.configure(text=t('afn.ops.btn_reverse'))
            self.btn_usar.configure(text=t('afn.ops.btn_usar'))
        except Exception:
            pass

    def _on_theme_change(self):
        c = self.theme.colors
        self.configure(bg=c['bg_panel'])
        self.result_text.configure(bg=c['bg_input'], fg=c['text'])
        self.result_text.tag_configure('header', foreground=c['accent'],
                                       font=('Consolas', 10, 'bold'))
        self.result_text.tag_configure('info', foreground=c['green'])
        for btn in (self.btn_kleene, self.btn_positive, self.btn_reverse):
            btn.configure(bg=c['bg_surface'], fg=c['text'])
        self.btn_usar.configure(bg=c['green'])


# ================================================================
# ConversionChainPanel — AFN-λ → AFN → AFD → AFD Mínimo
# ================================================================

class ConversionChainPanel(tk.Frame):
    """Panel para la cadena de conversión completa: AFN-λ → AFN → AFD → AFD Mínimo."""

    def __init__(self, parent, app_ref, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme
        self.app = app_ref
        self._chain_steps = []
        self._current_step = 0
        self._final_afd_min = None
        self._setup_ui()
        self.theme.on_change(self._on_theme_change)

    def _setup_ui(self):
        c = self.theme.colors
        self.configure(bg=c['bg_panel'])

        # Botones
        btn_frame = tk.Frame(self, bg=c['bg_panel'])
        btn_frame.pack(fill=tk.X, padx=8, pady=6)

        self.btn_ejecutar = tk.Button(
            btn_frame, text=t('afn.chain.btn_run'),
            command=self._ejecutar_cadena,
            bg=c['accent'], fg=c['text_on_accent'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            relief='flat', font=('Segoe UI', 9, 'bold'),
            padx=12, pady=4, cursor='hand2'
        )
        self.btn_ejecutar.pack(side=tk.LEFT, padx=4)

        # Navegación de pasos
        nav_frame = tk.Frame(self, bg=c['bg_panel'])
        nav_frame.pack(fill=tk.X, padx=8, pady=2)

        self.btn_prev = tk.Button(
            nav_frame, text=t('afn.chain.btn_prev'), command=self._prev_step,
            bg=c['bg_surface'], fg=c['text'],
            relief='flat', font=('Segoe UI', 9),
            padx=8, pady=2, cursor='hand2'
        )
        self.btn_prev.pack(side=tk.LEFT, padx=2)
        self.btn_prev.configure(state=tk.DISABLED)

        self.step_label = tk.Label(
            nav_frame, text=t('afn.chain.step_label'),
            bg=c['bg_panel'], fg=c['text_secondary'],
            font=('Consolas', 9)
        )
        self.step_label.pack(side=tk.LEFT, padx=8)

        self.btn_next = tk.Button(
            nav_frame, text=t('afn.chain.btn_next'), command=self._next_step,
            bg=c['bg_surface'], fg=c['text'],
            relief='flat', font=('Segoe UI', 9),
            padx=8, pady=2, cursor='hand2'
        )
        self.btn_next.pack(side=tk.LEFT, padx=2)
        self.btn_next.configure(state=tk.DISABLED)

        self.btn_usar = tk.Button(
            nav_frame, text=t('afn.chain.btn_use'),
            command=self._usar_resultado,
            bg=c['green'], fg='#FFFFFF',
            relief='flat', font=('Segoe UI', 9),
            padx=8, pady=2, cursor='hand2'
        )
        self.btn_usar.pack(side=tk.RIGHT, padx=4)
        self.btn_usar.configure(state=tk.DISABLED)

        # Resultado
        result_frame = tk.Frame(self, bg=c['bg_panel'])
        result_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.result_text = tk.Text(
            result_frame, wrap=tk.WORD, state=tk.DISABLED,
            bg=c['bg_input'], fg=c['text'],
            font=('Consolas', 9), relief='flat',
            padx=8, pady=6, height=12
        )
        scroll = ttk.Scrollbar(result_frame, orient=tk.VERTICAL,
                               command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.result_text.tag_configure('header', foreground=c['accent'],
                                       font=('Consolas', 10, 'bold'))
        self.result_text.tag_configure('step_title', foreground=c['yellow'],
                                        font=('Consolas', 10, 'bold'))
        self.result_text.tag_configure('info', foreground=c['green'])

    def _ejecutar_cadena(self):
        """Ejecuta la cadena completa de conversión."""
        automaton = self.app.current_automaton
        if not isinstance(automaton, (AFN, AFNLambda)):
            messagebox.showwarning("Tipo incorrecto",
                                   "Se requiere un AFN o AFN-λ para la cadena de conversión.")
            return
        if not automaton.estados or not automaton.estado_inicial:
            messagebox.showwarning("Sin autómata",
                                   "El autómata no está definido.")
            return

        try:
            self._chain_steps = []

            # Paso 0: Original
            tipo_orig = 'AFN-λ' if isinstance(automaton, AFNLambda) else 'AFN'
            self._chain_steps.append({
                'titulo': f'Original ({tipo_orig})',
                'automaton': automaton,
                'tipo': tipo_orig
            })

            current = automaton

            # Paso 1: Eliminar λ si es AFN-λ
            if isinstance(current, AFNLambda) and current.tiene_transiciones_lambda():
                afn = current.eliminar_lambda_transiciones()
                self._chain_steps.append({
                    'titulo': 'Paso 1: AFN-λ → AFN (eliminar λ)',
                    'automaton': afn,
                    'tipo': 'AFN'
                })
                current = afn

            # Paso 2: Construcción de subconjuntos → AFD
            resultado_sub = current.construccion_subconjuntos()
            afd = resultado_sub['afd']
            self._chain_steps.append({
                'titulo': 'Paso 2: AFN → AFD (subconjuntos)',
                'automaton': afd,
                'tipo': 'AFD'
            })

            # Paso 3: Minimización
            resultado_min = afd.minimizar()
            afd_min = resultado_min['afd_minimo']
            self._chain_steps.append({
                'titulo': 'Paso 3: AFD → AFD Mínimo',
                'automaton': afd_min,
                'tipo': 'AFD'
            })

            self._final_afd_min = afd_min
            self._current_step = 0

            # Habilitar navegación
            self.btn_prev.configure(state=tk.DISABLED)
            self.btn_next.configure(state=tk.NORMAL)
            self.btn_usar.configure(state=tk.NORMAL)

            self._show_step(0)
            self.app.add_log("Cadena de conversión completada.", "success")

        except Exception as e:
            messagebox.showerror("Error", f"Error en cadena de conversión:\n{str(e)}")
            self.app.add_log(f"Error: {str(e)}", "error")

    def _show_step(self, index):
        """Muestra un paso de la cadena."""
        if index < 0 or index >= len(self._chain_steps):
            return

        self._current_step = index
        paso = self._chain_steps[index]
        auto = paso['automaton']

        self.step_label.configure(text=f"Paso {index + 1}/{len(self._chain_steps)}")

        self.result_text.configure(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)

        self.result_text.insert(tk.END, f"═ {paso['titulo']} ═\n\n", 'step_title')
        self.result_text.insert(tk.END, f"  Tipo: {paso['tipo']}\n", 'info')
        self.result_text.insert(tk.END, f"  |Q| = {len(auto.estados)}\n", 'info')
        self.result_text.insert(tk.END, f"  |Σ| = {len(auto.alfabeto)}\n")
        self.result_text.insert(tk.END, f"  Estados: {sorted(auto.estados)}\n")
        self.result_text.insert(tk.END, f"  Alfabeto: {sorted(auto.alfabeto)}\n")
        self.result_text.insert(tk.END, f"  Inicial: {auto.estado_inicial}\n")
        self.result_text.insert(tk.END, f"  Finales: {sorted(auto.estados_finales)}\n")

        # Transiciones
        self.result_text.insert(tk.END, "\n  Transiciones:\n")
        if paso['tipo'] == 'AFD':
            for estado in sorted(auto.estados):
                for simbolo in sorted(auto.alfabeto):
                    dest = auto.delta.get(estado, {}).get(simbolo, '—')
                    self.result_text.insert(tk.END, f"    δ({estado}, {simbolo}) = {dest}\n")
        else:
            for estado in sorted(auto.delta):
                for simbolo in sorted(auto.delta[estado]):
                    destinos = auto.delta[estado][simbolo]
                    if isinstance(destinos, set):
                        dest_str = '{' + ', '.join(sorted(destinos)) + '}'
                    else:
                        dest_str = str(destinos)
                    self.result_text.insert(tk.END, f"    δ({estado}, {simbolo}) = {dest_str}\n")

        self.result_text.configure(state=tk.DISABLED)

        # Navegación
        self.btn_prev.configure(state=tk.NORMAL if index > 0 else tk.DISABLED)
        self.btn_next.configure(
            state=tk.NORMAL if index < len(self._chain_steps) - 1 else tk.DISABLED
        )

    def _prev_step(self):
        if self._current_step > 0:
            self._show_step(self._current_step - 1)

    def _next_step(self):
        if self._current_step < len(self._chain_steps) - 1:
            self._show_step(self._current_step + 1)

    def _usar_resultado(self):
        if self._final_afd_min is None:
            return
        self.app.current_automaton = self._final_afd_min
        self.app.current_tipo = 'AFD'
        self.app.on_automaton_changed()
        self.app.add_log(t('log.min_afd_set'), "success")

    def refresh_lang(self):
        try:
            self.btn_ejecutar.configure(text=t('afn.chain.btn_run'))
            self.btn_prev.configure(text=t('afn.chain.btn_prev'))
            self.btn_next.configure(text=t('afn.chain.btn_next'))
            self.btn_usar.configure(text=t('afn.chain.btn_use'))
            # Only reset step label if not actively showing a step
            if self.step_label.cget('text') in ('Paso: —', 'Step: —'):
                self.step_label.configure(text=t('afn.chain.step_label'))
        except Exception:
            pass

    def _on_theme_change(self):
        c = self.theme.colors
        self.configure(bg=c['bg_panel'])
        self.result_text.configure(bg=c['bg_input'], fg=c['text'])
        self.result_text.tag_configure('header', foreground=c['accent'],
                                       font=('Consolas', 10, 'bold'))
        self.result_text.tag_configure('step_title', foreground=c['yellow'],
                                        font=('Consolas', 10, 'bold'))
        self.result_text.tag_configure('info', foreground=c['green'])
        self.btn_ejecutar.configure(bg=c['accent'], fg=c['text_on_accent'])
        for btn in (self.btn_prev, self.btn_next):
            btn.configure(bg=c['bg_surface'], fg=c['text'])
        self.btn_usar.configure(bg=c['green'])
        self.step_label.configure(bg=c['bg_panel'], fg=c['text_secondary'])

# ── Language refresh helpers (added by i18n patch) ───────────────

def _afn_panel_refresh_lang(panel):
    """Generic refresh for AFN sub-panels that have simple button labels."""
    pass  # Buttons are rebuilt on next panel open; static UI is minimal
