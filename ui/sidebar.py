"""
Sidebar — Panel lateral izquierdo para definir el autómata.

Contiene:
  - Tipo de Autómata (AFD / AFN / AFN-λ)
  - Estados: agregar / eliminar con badges
  - Alfabeto: agregar / eliminar con badges
  - Estado Inicial: combobox
  - Estados Finales: checkboxes
  - Acciones: Cargar Ejemplo, Importar JSON, Exportar JSON, Limpiar Todo
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from ui.theme import theme
from ui.i18n import lang, t
from core.afd import AFD
from core.afn import AFN
from core.afn_lambda import AFNLambda
from core.serializer import guardar_json, cargar_json
from core.examples import ALL_EXAMPLES


class Sidebar(tk.Frame):
    """Panel lateral izquierdo para definir el autómata."""

    def __init__(self, parent, app_ref, **kwargs):
        c = theme.colors
        super().__init__(parent, bg=c['bg_panel'], width=280, **kwargs)
        self.app = app_ref
        self.pack_propagate(False)
        self._tipo_var = tk.StringVar(value='AFD')
        self._estado_entry_var = tk.StringVar()
        self._simbolo_entry_var = tk.StringVar()
        self._estado_inicial_var = tk.StringVar()
        self._estados_finales_vars = {}  # estado -> BooleanVar
        self._section_labels = []       # kept for theme
        self._section_label_map = {}   # key -> widget, for lang refresh
        self._separators = []

        self._build_ui()
        theme.on_change(self._on_theme_change)

    # ── Construcción de la UI ────────────────────────────────────

    def _build_ui(self):
        c = theme.colors

        # Título
        self._title = tk.Label(self, text=t('sidebar.title'), bg=c['bg_panel'],
                               fg=c['accent'], font=('Segoe UI', 13, 'bold'))
        self._title.pack(anchor='w', padx=12, pady=(10, 2))

        # Scrollable content
        self._scroll_canvas = tk.Canvas(self, bg=c['bg_panel'], highlightthickness=0, bd=0)
        self._scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                         command=self._scroll_canvas.yview)
        self._scroll_inner = tk.Frame(self._scroll_canvas, bg=c['bg_panel'])

        self._scroll_inner.bind(
            '<Configure>',
            lambda e: self._scroll_canvas.configure(
                scrollregion=self._scroll_canvas.bbox('all'))
        )
        self._canvas_window = self._scroll_canvas.create_window(
            (0, 0), window=self._scroll_inner, anchor='nw')
        self._scroll_canvas.configure(yscrollcommand=self._scrollbar.set)

        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Resize inner width to match canvas
        self._scroll_canvas.bind('<Configure>', self._on_canvas_configure)

        # Bind mouse wheel
        self._scroll_canvas.bind('<Enter>', self._bind_mousewheel)
        self._scroll_canvas.bind('<Leave>', self._unbind_mousewheel)

        inner = self._scroll_inner

        # ── Tipo de Autómata ─────────────────────────────────────
        self._build_section_label(inner, t('sidebar.type'), key='sidebar.type')

        self._tipo_frame = tk.Frame(inner, bg=c['bg_panel'])
        self._tipo_frame.pack(fill=tk.X, padx=12, pady=(0, 4))

        for tipo, tipo_key in [('AFD','type.afd'),('AFN','type.afn'),('AFN-λ','type.afnl')]:
            rb = tk.Radiobutton(
                self._tipo_frame, text=t(tipo_key), variable=self._tipo_var, value=tipo,
                bg=c['bg_panel'], fg=c['text'], selectcolor=c['bg_input'],
                activebackground=c['bg_panel'], activeforeground=c['text'],
                font=('Segoe UI', 10), command=self._on_tipo_change,
                indicatoron=True
            )
            rb.pack(side=tk.LEFT, padx=(0, 10))
            if not hasattr(self, '_tipo_radiobuttons'):
                self._tipo_radiobuttons = []
            self._tipo_radiobuttons.append((rb, tipo_key))

        self._separator(inner)

        # ── Estados ──────────────────────────────────────────────
        self._build_section_label(inner, t('sidebar.states'), key='sidebar.states')

        self._est_entry_frame = tk.Frame(inner, bg=c['bg_panel'])
        self._est_entry_frame.pack(fill=tk.X, padx=12, pady=(0, 4))

        self._est_entry = tk.Entry(
            self._est_entry_frame, textvariable=self._estado_entry_var,
            bg=c['bg_input'], fg=c['text'], insertbackground=c['text'],
            font=('Consolas', 10), width=14, relief='flat',
            highlightthickness=1, highlightcolor=c['accent'],
            highlightbackground=c['border']
        )
        self._est_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self._est_entry.bind('<Return>', lambda e: self._agregar_estado())

        self._btn_agregar_estado = tk.Button(
            self._est_entry_frame, text=t('sidebar.add'), command=self._agregar_estado,
            bg=c['accent'], fg=c['text_on_accent'], font=('Segoe UI', 9),
            relief='flat', cursor='hand2', padx=8
        )
        self._btn_agregar_estado.pack(side=tk.LEFT)

        # Badges de estados
        self._estados_badges_frame = tk.Frame(inner, bg=c['bg_panel'])
        self._estados_badges_frame.pack(fill=tk.X, padx=12, pady=(0, 4))

        self._separator(inner)

        # ── Alfabeto ─────────────────────────────────────────────
        self._build_section_label(inner, t('sidebar.alphabet'), key='sidebar.alphabet')

        self._alf_entry_frame = tk.Frame(inner, bg=c['bg_panel'])
        self._alf_entry_frame.pack(fill=tk.X, padx=12, pady=(0, 4))

        self._alf_entry = tk.Entry(
            self._alf_entry_frame, textvariable=self._simbolo_entry_var,
            bg=c['bg_input'], fg=c['text'], insertbackground=c['text'],
            font=('Consolas', 10), width=14, relief='flat',
            highlightthickness=1, highlightcolor=c['accent'],
            highlightbackground=c['border']
        )
        self._alf_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self._alf_entry.bind('<Return>', lambda e: self._agregar_simbolo())

        self._btn_agregar_simbolo = tk.Button(
            self._alf_entry_frame, text=t('sidebar.add'), command=self._agregar_simbolo,
            bg=c['accent'], fg=c['text_on_accent'], font=('Segoe UI', 9),
            relief='flat', cursor='hand2', padx=8
        )
        self._btn_agregar_simbolo.pack(side=tk.LEFT)

        # Badges de símbolos
        self._alfabeto_badges_frame = tk.Frame(inner, bg=c['bg_panel'])
        self._alfabeto_badges_frame.pack(fill=tk.X, padx=12, pady=(0, 4))

        self._separator(inner)

        # ── Estado Inicial ───────────────────────────────────────
        self._build_section_label(inner, t('sidebar.initial'), key='sidebar.initial')

        self._init_frame = tk.Frame(inner, bg=c['bg_panel'])
        self._init_frame.pack(fill=tk.X, padx=12, pady=(0, 4))

        self._init_combo = ttk.Combobox(
            self._init_frame, textvariable=self._estado_inicial_var,
            state='readonly', width=20, font=('Consolas', 10)
        )
        self._init_combo.pack(fill=tk.X)
        self._init_combo.bind('<<ComboboxSelected>>', self._on_initial_change)

        self._separator(inner)

        # ── Estados Finales ──────────────────────────────────────
        self._build_section_label(inner, t('sidebar.finals'), key='sidebar.finals')

        self._finales_frame = tk.Frame(inner, bg=c['bg_panel'])
        self._finales_frame.pack(fill=tk.X, padx=12, pady=(0, 4))

        self._finales_placeholder = tk.Label(
            self._finales_frame, text=t('sidebar.no_states'),
            bg=c['bg_panel'], fg=c['text_secondary'],
            font=('Segoe UI', 9, 'italic')
        )
        self._finales_placeholder.pack(anchor='w')

        self._separator(inner)

        # ── Acciones ─────────────────────────────────────────────
        self._build_section_label(inner, t('sidebar.actions'), key='sidebar.actions')

        self._actions_frame = tk.Frame(inner, bg=c['bg_panel'])
        self._actions_frame.pack(fill=tk.X, padx=12, pady=(0, 10))

        btn_style = {
            'bg': c['bg_surface'], 'fg': c['text'],
            'activebackground': c['accent_hover'],
            'activeforeground': c['text_on_accent'],
            'font': ('Segoe UI', 9), 'relief': 'flat', 'cursor': 'hand2',
            'padx': 6, 'pady': 3, 'anchor': 'w'
        }

        self._btn_ejemplo = tk.Button(
            self._actions_frame, text=t('sidebar.load_example'),
            command=self._cargar_ejemplo, **btn_style
        )
        self._btn_ejemplo.pack(fill=tk.X, pady=1)

        self._btn_importar = tk.Button(
            self._actions_frame, text=t('sidebar.import_json'),
            command=self._importar_json, **btn_style
        )
        self._btn_importar.pack(fill=tk.X, pady=1)

        self._btn_exportar = tk.Button(
            self._actions_frame, text=t('sidebar.export_json'),
            command=self._exportar_json, **btn_style
        )
        self._btn_exportar.pack(fill=tk.X, pady=1)

        self._btn_limpiar = tk.Button(
            self._actions_frame, text=t('sidebar.clear_all'),
            command=self._limpiar_todo,
            bg=c['red'], fg='#FFFFFF', activebackground='#DC2626',
            activeforeground='#FFFFFF', font=('Segoe UI', 9),
            relief='flat', cursor='hand2', padx=6, pady=3, anchor='w'
        )
        self._btn_limpiar.pack(fill=tk.X, pady=(4, 0))

    def _build_section_label(self, parent, text, key=None):
        c = theme.colors
        lbl = tk.Label(parent, text=text, bg=c['bg_panel'],
                       fg=c['text_secondary'], font=('Segoe UI', 10, 'bold'))
        lbl.pack(anchor='w', padx=12, pady=(8, 2))
        self._section_labels.append(lbl)
        if key:
            self._section_label_map[key] = lbl

    def _separator(self, parent):
        c = theme.colors
        sep = tk.Frame(parent, bg=c['border'], height=1)
        sep.pack(fill=tk.X, padx=12, pady=6)
        self._separators.append(sep)

    # ── Scroll helpers ───────────────────────────────────────────

    def _on_canvas_configure(self, event):
        self._scroll_canvas.itemconfig(self._canvas_window, width=event.width)

    def _bind_mousewheel(self, event):
        self._scroll_canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        self._scroll_canvas.bind_all('<Button-4>', self._on_mousewheel_linux)
        self._scroll_canvas.bind_all('<Button-5>', self._on_mousewheel_linux)

    def _unbind_mousewheel(self, event):
        self._scroll_canvas.unbind_all('<MouseWheel>')
        self._scroll_canvas.unbind_all('<Button-4>')
        self._scroll_canvas.unbind_all('<Button-5>')

    def _on_mousewheel(self, event):
        self._scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def _on_mousewheel_linux(self, event):
        if event.num == 4:
            self._scroll_canvas.yview_scroll(-1, 'units')
        elif event.num == 5:
            self._scroll_canvas.yview_scroll(1, 'units')

    # ── Lógica de estados ────────────────────────────────────────

    def _agregar_estado(self):
        nombre = self._estado_entry_var.get().strip()
        if not nombre:
            return
        automaton = self.app.current_automaton
        if not automaton:
            return
        if nombre in automaton.estados:
            messagebox.showwarning(t('dlg.dup_state'), t('msg.dup_state', s=nombre))
            return
        automaton.agregar_estado(nombre)
        self._estado_entry_var.set('')
        self.app.add_log(t('log.state_added', s=nombre), 'info')
        self._refresh_ui()
        self.app.on_automaton_changed()

    def _eliminar_estado(self, nombre):
        automaton = self.app.current_automaton
        if not automaton:
            return
        automaton.eliminar_estado(nombre)
        self.app.add_log(t('log.state_removed', s=nombre), 'info')
        self._refresh_ui()
        self.app.on_automaton_changed()

    # ── Lógica de alfabeto ───────────────────────────────────────

    def _agregar_simbolo(self):
        simbolo = self._simbolo_entry_var.get().strip()
        if not simbolo:
            return
        if len(simbolo) > 1:
            messagebox.showwarning(t('dlg.invalid_sym'), t('msg.sym_too_long'))
            return
        automaton = self.app.current_automaton
        if not automaton:
            return
        if simbolo in automaton.alfabeto:
            messagebox.showwarning(t('dlg.dup_sym'), t('msg.dup_sym', s=simbolo))
            return
        automaton.agregar_simbolo(simbolo)
        self._simbolo_entry_var.set('')
        self.app.add_log(t('log.state_added', s=simbolo), 'info')
        self._refresh_ui()
        self.app.on_automaton_changed()

    def _eliminar_simbolo(self, simbolo):
        automaton = self.app.current_automaton
        if not automaton:
            return
        automaton.eliminar_simbolo(simbolo)
        self.app.add_log(f'Símbolo eliminado: {simbolo}', 'info')
        self._refresh_ui()
        self.app.on_automaton_changed()

    # ── Tipo de autómata ─────────────────────────────────────────

    def _on_tipo_change(self):
        tipo = self._tipo_var.get()
        self.app.set_tipo(tipo)  # set_tipo already calls on_automaton_changed()
        self.app.add_log(t('log.type_changed', t=tipo), 'info')

    # ── Estado inicial ───────────────────────────────────────────

    def _on_initial_change(self, event=None):
        estado = self._estado_inicial_var.get()
        automaton = self.app.current_automaton
        if automaton and estado:
            automaton.definir_estado_inicial(estado)
            self.app.add_log(t('log.initial_set', s=estado), 'info')
            self._refresh_ui()
            self.app.on_automaton_changed()

    # ── Estados finales ──────────────────────────────────────────

    def _on_final_toggle(self, estado, var):
        automaton = self.app.current_automaton
        if not automaton:
            return
        if var.get():
            automaton.agregar_estado_final(estado)
            self.app.add_log(t('log.final_added', s=estado), 'info')
        else:
            automaton.eliminar_estado_final(estado)
            self.app.add_log(t('log.final_removed', s=estado), 'info')
        self.app.on_automaton_changed()

    # ── Acciones ─────────────────────────────────────────────────

    def _cargar_ejemplo(self):
        """Muestra diálogo para seleccionar un ejemplo pre-cargado."""
        c = theme.colors

        dialog = tk.Toplevel(self)
        dialog.title('Cargar Ejemplo')
        dialog.geometry('420x400')
        dialog.configure(bg=c['bg_panel'])
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        tk.Label(dialog, text='Seleccione un ejemplo:', bg=c['bg_panel'],
                 fg=c['text'], font=('Segoe UI', 11, 'bold')).pack(padx=12, pady=(10, 6))

        listbox_frame = tk.Frame(dialog, bg=c['bg_panel'])
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 6))

        listbox = tk.Listbox(
            listbox_frame, bg=c['bg_input'], fg=c['text'],
            selectbackground=c['accent'], selectforeground=c['text_on_accent'],
            font=('Segoe UI', 10), relief='flat', bd=0,
            highlightthickness=1, highlightcolor=c['accent'],
            highlightbackground=c['border']
        )
        sb = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(fill=tk.BOTH, expand=True)

        descriptions = {}
        for i, ejemplo in enumerate(ALL_EXAMPLES):
            listbox.insert(tk.END, ejemplo['nombre'])
            descriptions[i] = ejemplo['descripcion']

        desc_label = tk.Label(dialog, text='', bg=c['bg_panel'],
                              fg=c['text_secondary'], font=('Segoe UI', 9),
                              wraplength=380, justify='left')
        desc_label.pack(padx=12, pady=(0, 6), anchor='w')

        def on_select(event=None):
            sel = listbox.curselection()
            if sel:
                desc_label.configure(text=descriptions.get(sel[0], ''))

        listbox.bind('<<ListboxSelect>>', on_select)

        def cargar():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning(t('dlg.no_selection'), t('msg.no_selection'), parent=dialog)
                return
            ejemplo = ALL_EXAMPLES[sel[0]]
            dialog.destroy()
            self._aplicar_ejemplo(ejemplo)

        btn_frame = tk.Frame(dialog, bg=c['bg_panel'])
        btn_frame.pack(fill=tk.X, padx=12, pady=(0, 10))

        tk.Button(btn_frame, text='Cancelar', command=dialog.destroy,
                  bg=c['bg_surface'], fg=c['text'], font=('Segoe UI', 9),
                  relief='flat', cursor='hand2', padx=12).pack(side=tk.RIGHT, padx=(4, 0))
        tk.Button(btn_frame, text='Cargar', command=cargar,
                  bg=c['accent'], fg=c['text_on_accent'], font=('Segoe UI', 9),
                  relief='flat', cursor='hand2', padx=12).pack(side=tk.RIGHT)

    def _aplicar_ejemplo(self, ejemplo):
        """Aplica un ejemplo seleccionado."""
        tipo = ejemplo['tipo']
        funcion = ejemplo['funcion']

        if tipo == 'AFD_par':
            afd1, _ = funcion()
            automaton = afd1
            nuevo_tipo = 'AFD'
        else:
            automaton = funcion()
            if tipo == 'AFD':
                nuevo_tipo = 'AFD'
            elif tipo == 'AFN':
                nuevo_tipo = 'AFN'
            elif tipo == 'AFNLambda':
                nuevo_tipo = 'AFN-λ'
            else:
                nuevo_tipo = 'AFD'

        # Set automaton directly (avoids creating a blank then overwriting)
        self.app.current_automaton = automaton
        self.app.current_tipo = nuevo_tipo
        self._tipo_var.set(nuevo_tipo)

        self.app.add_log(t('log.example_loaded', name=ejemplo['nombre']), 'success')
        self.app.on_automaton_changed()

    def _importar_json(self):
        filepath = filedialog.askopenfilename(
            title='Importar autómata',
            filetypes=[('JSON', '*.json'), ('Todos', '*.*')]
        )
        if not filepath:
            return

        try:
            automaton = cargar_json(filepath)
            if isinstance(automaton, AFNLambda):
                nuevo_tipo = 'AFN-λ'
            elif isinstance(automaton, AFN):
                nuevo_tipo = 'AFN'
            else:
                nuevo_tipo = 'AFD'

            # Set automaton directly to avoid type mismatch
            self.app.current_automaton = automaton
            self.app.current_tipo = nuevo_tipo
            self._tipo_var.set(nuevo_tipo)

            self.app.add_log(t('log.imported_from', f=filepath), 'success')
            self.app.on_automaton_changed()

        except Exception as e:
            messagebox.showerror(t('dlg.error'), f"{'No se pudo importar' if lang.current=='es' else 'Could not import'}:\n{str(e)}")
            self.app.add_log(t('log.import_error', e=str(e)), 'error')

    def _exportar_json(self):
        automaton = self.app.current_automaton
        if not automaton or not automaton.estados:
            messagebox.showwarning(t('dlg.no_export'), t('msg.no_export'))
            return

        filepath = filedialog.asksaveasfilename(
            title='Exportar autómata',
            defaultextension='.json',
            filetypes=[('JSON', '*.json'), ('Todos', '*.*')]
        )
        if not filepath:
            return

        try:
            guardar_json(automaton, filepath)
            self.app.add_log(f'Autómata exportado a: {filepath}', 'success')
            messagebox.showinfo('Exportado', f'Autómata exportado a:\n{filepath}')
        except Exception as e:
            messagebox.showerror('Error de exportación',
                                 f'No se pudo exportar:\n{str(e)}')
            self.app.add_log(f'Error exportando: {str(e)}', 'error')

    def _limpiar_todo(self):
        if not messagebox.askyesno('Confirmar', '¿Desea limpiar todo el autómata?'):
            return
        tipo = self._tipo_var.get()
        self.app.set_tipo(tipo)
        self.app.add_log('Autómata limpiado', 'info')
        self._refresh_ui()
        self.app.on_automaton_changed()

    # ── Refrescar UI ─────────────────────────────────────────────

    def refresh(self):
        """Actualiza la sidebar para reflejar el automata actual."""
        # Sync the tipo radio button with the app's current tipo
        if hasattr(self.app, 'current_tipo'):
            self._tipo_var.set(self.app.current_tipo)
        self._refresh_ui()

    def _refresh_ui(self):
        automaton = self.app.current_automaton
        if not automaton:
            return

        c = theme.colors

        # ── Badges de estados ────────────────────────────────────
        for w in self._estados_badges_frame.winfo_children():
            w.destroy()

        for estado in sorted(automaton.estados):
            badge = tk.Frame(self._estados_badges_frame, bg=c['bg_surface'], bd=0)
            badge.pack(side=tk.LEFT, padx=2, pady=2)

            lbl = tk.Label(badge, text=estado, bg=c['bg_surface'], fg=c['text'],
                           font=('Consolas', 9), padx=4, pady=1)
            lbl.pack(side=tk.LEFT)

            btn_del = tk.Label(badge, text='✕', bg=c['bg_surface'], fg=c['red'],
                               font=('Segoe UI', 8, 'bold'), cursor='hand2', padx=2)
            btn_del.pack(side=tk.LEFT)
            btn_del.bind('<Button-1>', lambda e, s=estado: self._eliminar_estado(s))

        # ── Badges de símbolos ───────────────────────────────────
        for w in self._alfabeto_badges_frame.winfo_children():
            w.destroy()

        for simbolo in sorted(automaton.alfabeto):
            badge = tk.Frame(self._alfabeto_badges_frame, bg=c['bg_surface'], bd=0)
            badge.pack(side=tk.LEFT, padx=2, pady=2)

            lbl = tk.Label(badge, text=simbolo, bg=c['bg_surface'], fg=c['accent'],
                           font=('Consolas', 10, 'bold'), padx=6, pady=1)
            lbl.pack(side=tk.LEFT)

            btn_del = tk.Label(badge, text='✕', bg=c['bg_surface'], fg=c['red'],
                               font=('Segoe UI', 8, 'bold'), cursor='hand2', padx=2)
            btn_del.pack(side=tk.LEFT)
            btn_del.bind('<Button-1>', lambda e, s=simbolo: self._eliminar_simbolo(s))

        # ── Combobox de estado inicial ───────────────────────────
        estados_list = sorted(automaton.estados)
        self._init_combo['values'] = estados_list
        if automaton.estado_inicial:
            self._estado_inicial_var.set(automaton.estado_inicial)
        else:
            self._estado_inicial_var.set('')

        # ── Checkboxes de estados finales ────────────────────────
        for w in self._finales_frame.winfo_children():
            w.destroy()

        if not estados_list:
            placeholder = tk.Label(
                self._finales_frame, text=t('sidebar.no_states_ph'),
                bg=c['bg_panel'], fg=c['text_secondary'],
                font=('Segoe UI', 9, 'italic')
            )
            placeholder.pack(anchor='w')
        else:
            self._estados_finales_vars = {}
            for estado in estados_list:
                var = tk.BooleanVar(value=(estado in automaton.estados_finales))
                self._estados_finales_vars[estado] = var
                cb = tk.Checkbutton(
                    self._finales_frame, text=estado, variable=var,
                    bg=c['bg_panel'], fg=c['text'],
                    activebackground=c['bg_panel'], activeforeground=c['text'],
                    selectcolor=c['bg_input'], font=('Consolas', 10),
                    command=lambda e=estado, v=var: self._on_final_toggle(e, v)
                )
                cb.pack(anchor='w')

    # ── Tema ─────────────────────────────────────────────────────


    def refresh_lang(self):
        """Refresh all UI text after language change."""
        self._title.configure(text=t('sidebar.title'))
        # Update section labels
        for key, lbl in self._section_label_map.items():
            try:
                lbl.configure(text=t(key))
            except Exception:
                pass
        # Refresh radio button labels
        for rb, key in getattr(self, '_tipo_radiobuttons', []):
            try: rb.configure(text=t(key))
            except Exception: pass
        self._btn_agregar_estado.configure(text=t('sidebar.add'))
        self._btn_agregar_simbolo.configure(text=t('sidebar.add'))
        self._btn_ejemplo.configure(text=t('sidebar.load_example'))
        self._btn_importar.configure(text=t('sidebar.import_json'))
        self._btn_exportar.configure(text=t('sidebar.export_json'))
        self._btn_limpiar.configure(text=t('sidebar.clear_all'))
        self._refresh_ui()

    def _on_theme_change(self):
        c = theme.colors
        self.configure(bg=c['bg_panel'])
        self._title.configure(bg=c['bg_panel'], fg=c['accent'])
        self._scroll_canvas.configure(bg=c['bg_panel'])
        self._scroll_inner.configure(bg=c['bg_panel'])

        for lbl in self._section_labels:
            lbl.configure(bg=c['bg_panel'], fg=c['text_secondary'])
        for sep in self._separators:
            sep.configure(bg=c['border'])

        self._refresh_ui()
