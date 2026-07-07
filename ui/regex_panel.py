"""
RegexPanel — Panel de Expresiones Regulares ↔ Autómatas.

Contiene:
- Conversión ER → AFN-λ (Construcción de Thompson)
- Conversión AFD → ER (Lema de Arden)
- Detección de errores de sintaxis
- Visualización de pasos
"""

import tkinter as tk
from tkinter import ttk, messagebox

from ui.i18n import lang, t
from core.afd import AFD
from core.afn import AFN
from core.afn_lambda import AFNLambda
from core.regex import RegexParser, ThompsonConstruction, ArdenConversion
from core.regex import regex_to_afn_lambda, afd_to_regex, infer_alphabet
from ui.theme import theme


class RegexPanel(tk.Frame):
    """Panel para conversiones entre Expresiones Regulares y Autómatas."""

    def __init__(self, parent, app_ref, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme
        self.app = app_ref
        self._result_afn_lambda = None
        self._result_regex = None
        self._setup_ui()
        self.theme.on_change(self._on_theme_change)

    def _setup_ui(self):
        c = self.theme.colors
        self.configure(bg=c['bg_panel'])

        # ═══ Sección: ER → AFN-λ ═══
        self.er_frame = tk.LabelFrame(
            self, text=t('regex.er_title'),
            bg=c['bg_panel'], fg=c['accent'],
            font=('Segoe UI', 10, 'bold'),
            bd=1, relief='groove',
            highlightbackground=c['border']
        )
        self.er_frame.pack(fill=tk.X, padx=8, pady=(6, 3))

        # Entry para expresión regular
        entry_frame = tk.Frame(self.er_frame, bg=c['bg_panel'])
        entry_frame.pack(fill=tk.X, padx=8, pady=4)

        tk.Label(
            entry_frame, text=t('regex.er_label'), bg=c['bg_panel'], fg=c['text'],
            font=('Consolas', 10, 'bold')
        ).pack(side=tk.LEFT, padx=(0, 4))

        self.regex_entry = tk.Entry(
            entry_frame, font=('Consolas', 11),
            bg=c['bg_input'], fg=c['text'],
            insertbackground=c['text'],
            selectbackground=c['accent'],
            selectforeground=c['text_on_accent'],
            relief='flat', bd=0,
            highlightthickness=1,
            highlightcolor=c['accent'],
            highlightbackground=c['border']
        )
        self.regex_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, ipady=3)

        self.btn_thompson = tk.Button(
            entry_frame, text=t('regex.btn_thompson'),
            command=self._er_to_afn_lambda,
            bg=c['accent'], fg=c['text_on_accent'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            relief='flat', font=('Segoe UI', 9, 'bold'),
            padx=10, pady=3, cursor='hand2'
        )
        self.btn_thompson.pack(side=tk.LEFT, padx=4)

        # Operadores soportados
        ops_frame = tk.Frame(self.er_frame, bg=c['bg_panel'])
        ops_frame.pack(fill=tk.X, padx=8, pady=(0, 4))

        tk.Label(
            ops_frame, text=t('regex.operators'),
            bg=c['bg_panel'], fg=c['text_secondary'],
            font=('Segoe UI', 8)
        ).pack(anchor='w')

        # Syntax error label
        self.error_label = tk.Label(
            self.er_frame, text="", bg=c['bg_panel'], fg=c['red'],
            font=('Segoe UI', 9)
        )
        self.error_label.pack(anchor='w', padx=8, pady=(0, 2))

        # Botón usar resultado ER→AFN-λ
        self.btn_usar_afn_lambda = tk.Button(
            self.er_frame, text=t('regex.btn_use_afnl'),
            command=self._usar_afn_lambda,
            bg=c['green'], fg='#FFFFFF',
            relief='flat', font=('Segoe UI', 9),
            padx=8, pady=2, cursor='hand2'
        )
        self.btn_usar_afn_lambda.pack(anchor='e', padx=8, pady=(0, 4))
        self.btn_usar_afn_lambda.configure(state=tk.DISABLED)

        # ═══ Sección: AFD → ER ═══
        self.afd_er_frame = tk.LabelFrame(
            self, text=t('regex.afd_title'),
            bg=c['bg_panel'], fg=c['accent'],
            font=('Segoe UI', 10, 'bold'),
            bd=1, relief='groove',
            highlightbackground=c['border']
        )
        self.afd_er_frame.pack(fill=tk.X, padx=8, pady=(3, 3))

        afd_btn_frame = tk.Frame(self.afd_er_frame, bg=c['bg_panel'])
        afd_btn_frame.pack(fill=tk.X, padx=8, pady=4)

        self.btn_arden = tk.Button(
            afd_btn_frame, text=t('regex.btn_arden'),
            command=self._afd_to_er,
            bg=c['accent'], fg=c['text_on_accent'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            relief='flat', font=('Segoe UI', 9, 'bold'),
            padx=10, pady=3, cursor='hand2'
        )
        self.btn_arden.pack(side=tk.LEFT, padx=4)

        self.regex_result_label = tk.Label(
            afd_btn_frame, text="", bg=c['bg_panel'], fg=c['green'],
            font=('Consolas', 11, 'bold')
        )
        self.regex_result_label.pack(side=tk.LEFT, padx=8, fill=tk.X, expand=True)

        # ═══ Resultado / Pasos ═══
        result_frame = tk.Frame(self, bg=c['bg_panel'])
        result_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.result_text = tk.Text(
            result_frame, wrap=tk.WORD, state=tk.DISABLED,
            bg=c['bg_input'], fg=c['text'],
            font=('Consolas', 9), relief='flat',
            padx=8, pady=6, height=8
        )
        scroll = ttk.Scrollbar(result_frame, orient=tk.VERTICAL,
                               command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tags
        self.result_text.tag_configure('header', foreground=c['accent'],
                                       font=('Consolas', 10, 'bold'))
        self.result_text.tag_configure('step', foreground=c['green'])
        self.result_text.tag_configure('regex', foreground=c['yellow'],
                                       font=('Consolas', 10, 'bold'))
        self.result_text.tag_configure('error', foreground=c['red'])

        # Bind de validación en tiempo real
        self.regex_entry.bind('<KeyRelease>', self._on_regex_change)

    def _on_regex_change(self, event=None):
        """Valida la expresión regular mientras se escribe."""
        regex_str = self.regex_entry.get().strip()
        if not regex_str:
            self.error_label.configure(text="")
            return

        try:
            parser = RegexParser()
            parser.parse(regex_str)
            self.error_label.configure(text=t('regex.valid'), fg=self.theme.colors['green'])
        except ValueError as e:
            self.error_label.configure(text=f"✗ {str(e)}", fg=self.theme.colors['red'])

    def _er_to_afn_lambda(self):
        """Convierte la expresión regular a AFN-λ usando Thompson."""
        regex_str = self.regex_entry.get().strip()
        if not regex_str:
            messagebox.showwarning(t('dlg.no_regex'), t('msg.no_regex'))
            return

        try:
            # Parsear y verificar
            parser = RegexParser()
            ast = parser.parse(regex_str)
            self.error_label.configure(text="✓ Expresión válida", fg=self.theme.colors['green'])

            # Construir AFN-λ
            alphabet = infer_alphabet(regex_str)
            constructor = ThompsonConstruction()
            afn_lambda = constructor.thompson(ast, alphabet)

            self._result_afn_lambda = afn_lambda

            # Mostrar resultado
            self.result_text.configure(state=tk.NORMAL)
            self.result_text.delete('1.0', tk.END)

            self.result_text.insert(tk.END, "═ Construcción de Thompson ═\n\n", 'header')
            self.result_text.insert(tk.END, f"  Expresión: ", 'header')
            self.result_text.insert(tk.END, f"{regex_str}\n\n", 'regex')

            self.result_text.insert(tk.END, f"  AFN-λ resultante:\n", 'step')
            self.result_text.insert(tk.END, f"    Estados: {sorted(afn_lambda.estados)}\n")
            self.result_text.insert(tk.END, f"    |Q| = {len(afn_lambda.estados)}\n")
            self.result_text.insert(tk.END, f"    Alfabeto: {sorted(afn_lambda.alfabeto)}\n")
            self.result_text.insert(tk.END, f"    Inicial: {afn_lambda.estado_inicial}\n")
            self.result_text.insert(tk.END, f"    Finales: {sorted(afn_lambda.estados_finales)}\n")

            tiene_lambda = afn_lambda.tiene_transiciones_lambda()
            self.result_text.insert(
                tk.END, f"    Tiene λ-transiciones: {'Sí' if tiene_lambda else 'No'}\n", 'step'
            )

            # Transiciones
            self.result_text.insert(tk.END, "\n  Transiciones:\n")
            for estado in sorted(afn_lambda.delta):
                for simbolo in sorted(afn_lambda.delta[estado]):
                    destinos = afn_lambda.delta[estado][simbolo]
                    if isinstance(destinos, set):
                        dest_str = '{' + ', '.join(sorted(destinos)) + '}'
                    else:
                        dest_str = str(destinos)
                    self.result_text.insert(
                        tk.END, f"    δ({estado}, {simbolo}) = {dest_str}\n"
                    )

            self.result_text.configure(state=tk.DISABLED)
            self.btn_usar_afn_lambda.configure(state=tk.NORMAL)
            self.app.add_log(t('log.thompson_done', r=regex_str, n=len(afn_lambda.estados)), "success")

        except ValueError as e:
            self.error_label.configure(text=f"✗ Error: {str(e)}", fg=self.theme.colors['red'])
            self.app.add_log(f"Error de parsing: {str(e)}", "error")
        except Exception as e:
            messagebox.showerror("Error", f"Error en construcción de Thompson:\n{str(e)}")
            self.app.add_log(f"Error: {str(e)}", "error")

    def _afd_to_er(self):
        """Convierte el AFD actual a expresión regular usando Arden."""
        automaton = self.app.current_automaton
        if not isinstance(automaton, AFD):
            messagebox.showwarning(t('dlg.not_afd'), t('msg.not_afd'))
            return
        if not automaton.estados or not automaton.estado_inicial:
            messagebox.showwarning(t('dlg.no_automaton'), t('msg.no_automaton'))
            return

        try:
            resultado = afd_to_regex(automaton)
            regex_str = resultado['regex']
            pasos = resultado['pasos']

            self._result_regex = regex_str

            # Mostrar resultado
            self.regex_result_label.configure(text=f"ER = {regex_str}")

            self.result_text.configure(state=tk.NORMAL)
            self.result_text.delete('1.0', tk.END)

            self.result_text.insert(tk.END, "═ AFD → ER (Lema de Arden) ═\n\n", 'header')
            self.result_text.insert(tk.END, f"  Expresión regular: ", 'header')
            self.result_text.insert(tk.END, f"{regex_str}\n\n", 'regex')

            # Pasos
            self.result_text.insert(tk.END, "═ Pasos ═\n\n", 'header')
            for i, paso in enumerate(pasos):
                self.result_text.insert(tk.END, f"Paso {i + 1}: ", 'step')
                self.result_text.insert(tk.END, f"{paso['descripcion']}\n")

                if 'ecuaciones' in paso and paso['ecuaciones']:
                    for var, expr in paso['ecuaciones'].items():
                        self.result_text.insert(tk.END, f"    {var} = {expr}\n")
                    self.result_text.insert(tk.END, "\n")

            self.result_text.configure(state=tk.DISABLED)
            self.app.add_log(t('log.arden_done', r=regex_str), "success")

        except Exception as e:
            messagebox.showerror("Error", f"Error en conversión AFD → ER:\n{str(e)}")
            self.app.add_log(f"Error: {str(e)}", "error")

    def _usar_afn_lambda(self):
        """Reemplaza el autómata actual con el AFN-λ resultante."""
        if self._result_afn_lambda is None:
            return
        self.app.current_automaton = self._result_afn_lambda
        self.app.current_tipo = 'AFN-λ'
        self.app.on_automaton_changed()
        self.app.add_log(t('log.afnl_set'), "success")

    def _on_theme_change(self):
        c = self.theme.colors
        self.configure(bg=c['bg_panel'])
        self.regex_entry.configure(
            bg=c['bg_input'], fg=c['text'],
            insertbackground=c['text'],
            highlightcolor=c['accent'],
            highlightbackground=c['border']
        )
        self.result_text.configure(bg=c['bg_input'], fg=c['text'])
        self.result_text.tag_configure('header', foreground=c['accent'],
                                       font=('Consolas', 10, 'bold'))
        self.result_text.tag_configure('step', foreground=c['green'])
        self.result_text.tag_configure('regex', foreground=c['yellow'],
                                       font=('Consolas', 10, 'bold'))
        self.result_text.tag_configure('error', foreground=c['red'])
        self.btn_thompson.configure(bg=c['accent'], fg=c['text_on_accent'])
        self.btn_arden.configure(bg=c['accent'], fg=c['text_on_accent'])
        self.btn_usar_afn_lambda.configure(bg=c['green'])

    def refresh_lang(self):
        try:
            self.er_frame.configure(text=t('regex.er_title'))
            self.afd_er_frame.configure(text=t('regex.afd_title'))
            self.btn_thompson.configure(text=t('regex.btn_thompson'))
            self.btn_arden.configure(text=t('regex.btn_arden'))
            self.btn_usar_afn_lambda.configure(text=t('regex.btn_use_afnl'))
            # Update er label and operators hint
            for w in self.er_frame.winfo_children():
                try:
                    for child in w.winfo_children():
                        txt = child.cget('text')
                        if t('regex.er_label') in txt or 'ER:' in txt or 'RE:' in txt:
                            child.configure(text=t('regex.er_label'))
                        elif 'union' in txt.lower() or 'unión' in txt.lower():
                            child.configure(text=t('regex.operators'))
                except Exception:
                    pass
        except Exception:
            pass
