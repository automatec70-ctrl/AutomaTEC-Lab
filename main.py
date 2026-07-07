"""
AutomaTEC-Lab — Aplicación de Autómatas Finitos / Finite Automata Application
Entry point principal.
"""

import sys
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.theme import theme
from ui.i18n import lang, t, tipo_display
from ui.canvas_widget import AutomataCanvas
from ui.table_widget import TablaTransiciones
from ui.sidebar import Sidebar
from ui.string_processor import StringProcessor
from ui.minimization_panel import MinimizationPanel
from ui.equivalence_panel import EquivalencePanel
from ui.operations_panel import OperationsPanel
from ui.properties_panel import PropertiesPanel
from ui.afn_panels import (SubsetConstructionPanel, EpsilonEliminationPanel,
                            AFNOperationsPanel, ConversionChainPanel)
from ui.regex_panel import RegexPanel
from ui.log_panel import LogPanel
from ui.help_dialog import HelpDialog
from ui.examples_dialog import ExamplesDialog
from core.afd import AFD
from core.afn import AFN
from core.afn_lambda import AFNLambda
from core.serializer import *
from core.examples import ALL_EXAMPLES


class AutomaTECLab(tk.Tk):
    """Main window of AutomaTEC-Lab."""

    def __init__(self):
        super().__init__()

        self.title(t('app.title'))
        self.geometry("1280x800")
        self.minsize(1024, 768)

        self.current_tipo = 'AFD'
        self.current_automaton = AFD()

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        theme.apply_to_ttk_style(self.style)

        c = theme.colors
        self.configure(bg=c['bg_main'])

        self._build_menu()
        self._build_layout()
        self._build_status_bar()

        theme.on_change(self._on_theme_change)
        lang.on_change(self._on_lang_change)

        self.add_log(t('log.started'), 'info')

        self.bind('<Control-n>', lambda e: self._nuevo_automata())
        self.bind('<Control-o>', lambda e: self.import_json())
        self.bind('<Control-s>', lambda e: self.export_json())
        self.bind('<Control-t>', lambda e: self._toggle_theme())
        self.bind('<F1>', lambda e: self._show_help())
        self.bind('<Control-q>', lambda e: self.destroy())

    # ── Menu ──────────────────────────────────────────────────────

    def _make_menu(self, parent=None, **kwargs):
        c = theme.colors
        opts = dict(tearoff=0, bg=c['bg_surface'], fg=c['text'],
                    activebackground=c['accent_hover'],
                    activeforeground=c['text_on_accent'],
                    font=('Segoe UI', 9))
        opts.update(kwargs)
        return tk.Menu(parent, **opts) if parent else tk.Menu(self, **opts)

    def _build_menu(self):
        c = theme.colors
        self._menubar = self._make_menu()

        # ── File ──
        self._menu_file = self._make_menu(self._menubar)
        self._menu_new  = self._make_menu(self._menu_file)
        self._menu_new.add_command(label=t('menu.file.new_afd'),
                                   command=lambda: self.set_tipo('AFD'))
        self._menu_new.add_command(label=t('menu.file.new_afn'),
                                   command=lambda: self.set_tipo('AFN'))
        self._menu_new.add_command(label=t('menu.file.new_afnl'),
                                   command=lambda: self.set_tipo('AFN-λ'))
        self._menu_file.add_cascade(label=t('menu.file.new'), menu=self._menu_new)
        self._menu_file.add_separator()
        self._menu_file.add_command(label=t('menu.file.open'),   command=self.import_json)
        self._menu_file.add_command(label=t('menu.file.save'),   command=self.export_json)
        self._menu_file.add_command(label=t('menu.file.save_as'),command=self.export_json_as)
        self._menu_file.add_separator()
        self._menu_file.add_command(label=t('menu.file.examples'),command=self._show_examples)
        self._menu_file.add_separator()
        self._menu_file.add_command(label=t('menu.file.exit'),   command=self.destroy)
        self._menubar.add_cascade(label=t('menu.file'), menu=self._menu_file)

        # ── Edit ──
        self._menu_edit = self._make_menu(self._menubar)
        self._menu_edit.add_command(label=t('menu.edit.clear'),  command=self._limpiar_todo)
        self._menubar.add_cascade(label=t('menu.edit'), menu=self._menu_edit)

        # ── View ──
        self._menu_view = self._make_menu(self._menubar)
        self._menu_view.add_command(label=t('menu.view.theme'),  command=self._toggle_theme)

        # Language sub-menu
        self._menu_lang = self._make_menu(self._menu_view)
        self._lang_var = tk.StringVar(value=lang.current)
        self._menu_lang.add_radiobutton(
            label=t('menu.view.lang_es'), value='es',
            variable=self._lang_var, command=lambda: self._set_language('es'))
        self._menu_lang.add_radiobutton(
            label=t('menu.view.lang_en'), value='en',
            variable=self._lang_var, command=lambda: self._set_language('en'))
        self._menu_view.add_cascade(label=t('menu.view.language'), menu=self._menu_lang)
        self._menubar.add_cascade(label=t('menu.view'), menu=self._menu_view)

        # ── Tools ──
        self._menu_tools = self._make_menu(self._menubar)
        self._menu_tools.add_command(label=t('menu.tools.completeness'),
                                     command=self._verificar_completitud)
        self._menu_tools.add_command(label=t('menu.tools.remove_useless'),
                                     command=self._eliminar_inutiles)
        self._menubar.add_cascade(label=t('menu.tools'), menu=self._menu_tools)

        # ── Help ──
        self._menu_help = self._make_menu(self._menubar)
        self._menu_help.add_command(label=t('menu.help.tutorial'), command=self._show_help)
        self._menu_help.add_separator()
        self._menu_help.add_command(label=t('menu.help.about'),    command=self._show_about)
        self._menubar.add_cascade(label=t('menu.help'), menu=self._menu_help)

        self.config(menu=self._menubar)

    def _rebuild_menu(self):
        """Rebuild menu labels after language change."""
        c = theme.colors

        def relabel(menu, entries):
            """Update labels of existing menu entries by index."""
            for idx, key in entries:
                try:
                    menu.entryconfigure(idx, label=t(key))
                except Exception:
                    pass

        # File menu
        relabel(self._menu_file, [
            (0, 'menu.file.new'),
            (2, 'menu.file.open'),
            (3, 'menu.file.save'),
            (4, 'menu.file.save_as'),
            (6, 'menu.file.examples'),
            (8, 'menu.file.exit'),
        ])
        relabel(self._menu_new, [
            (0, 'menu.file.new_afd'),
            (1, 'menu.file.new_afn'),
            (2, 'menu.file.new_afnl'),
        ])
        # Edit
        relabel(self._menu_edit, [(0, 'menu.edit.clear')])
        # View
        relabel(self._menu_view, [
            (0, 'menu.view.theme'),
            (1, 'menu.view.language'),
        ])
        relabel(self._menu_lang, [
            (0, 'menu.view.lang_es'),
            (1, 'menu.view.lang_en'),
        ])
        # Tools
        relabel(self._menu_tools, [
            (0, 'menu.tools.completeness'),
            (1, 'menu.tools.remove_useless'),
        ])
        # Help
        relabel(self._menu_help, [
            (0, 'menu.help.tutorial'),
            (2, 'menu.help.about'),
        ])
        # Cascade labels
        relabel(self._menubar, [
            (0, 'menu.file'),
            (1, 'menu.edit'),
            (2, 'menu.view'),
            (3, 'menu.tools'),
            (4, 'menu.help'),
        ])

    # ── Layout ────────────────────────────────────────────────────

    def _build_layout(self):
        c = theme.colors

        self.hpaned = tk.PanedWindow(self, orient=tk.HORIZONTAL,
                                     bg=c['border'], sashwidth=4, sashrelief=tk.FLAT)
        self.hpaned.pack(fill=tk.BOTH, expand=True)

        self.sidebar = Sidebar(self.hpaned, app_ref=self)
        self.hpaned.add(self.sidebar, minsize=200, width=260)

        right_frame = tk.Frame(self.hpaned, bg=c['bg_main'])
        self.hpaned.add(right_frame, minsize=600)

        self.vpaned = tk.PanedWindow(right_frame, orient=tk.VERTICAL,
                                     bg=c['border'], sashwidth=4, sashrelief=tk.FLAT)
        self.vpaned.pack(fill=tk.BOTH, expand=True)

        self.canvas_widget = AutomataCanvas(self.vpaned, theme_ref=theme)
        self.vpaned.add(self.canvas_widget, minsize=200, height=350)

        notebook_frame = tk.Frame(self.vpaned, bg=c['bg_main'])
        self.vpaned.add(notebook_frame, minsize=200, height=250)

        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self._create_tabs()

        self.log_panel = LogPanel(self.vpaned, theme_ref=theme)
        self.vpaned.add(self.log_panel, minsize=80, height=130)

    def _create_tabs(self):
        """Create all notebook tabs and track them for language refresh."""
        self._tabs = []  # list of (frame, panel, tab_key)

        def add_tab(key, PanelClass, *args, **kwargs):
            frame = tk.Frame(self.notebook)
            self.notebook.add(frame, text=t(key))
            panel = PanelClass(frame, *args, **kwargs)
            panel.pack(fill=tk.BOTH, expand=True)
            self._tabs.append((frame, panel, key))
            return panel

        self.tabla_widget        = add_tab('tab.table',           TablaTransiciones,
                                           theme_ref=theme, app_ref=self)
        self.string_processor    = add_tab('tab.process',         StringProcessor,  app_ref=self)
        self.minimization_panel  = add_tab('tab.minimize',        MinimizationPanel,app_ref=self)
        self.equivalence_panel   = add_tab('tab.equivalence',     EquivalencePanel, app_ref=self)
        self.operations_panel    = add_tab('tab.operations',      OperationsPanel,  app_ref=self)
        self.properties_panel    = add_tab('tab.properties',      PropertiesPanel,  app_ref=self)
        self.subset_panel        = add_tab('tab.subsets',         SubsetConstructionPanel, app_ref=self)
        self.epsilon_panel       = add_tab('tab.eliminate_lambda',EpsilonEliminationPanel, app_ref=self)
        self.afn_ops_panel       = add_tab('tab.afn_operations',  AFNOperationsPanel, app_ref=self)
        self.conversion_panel    = add_tab('tab.conversion',      ConversionChainPanel, app_ref=self)
        self.regex_panel         = add_tab('tab.regex',           RegexPanel, app_ref=self)

        # Keep backward-compat names
        self.tab_tabla       = self._tabs[0][0]
        self.tab_procesar    = self._tabs[1][0]
        self.tab_minimizar   = self._tabs[2][0]
        self.tab_equivalencia= self._tabs[3][0]
        self.tab_operaciones = self._tabs[4][0]
        self.tab_propiedades = self._tabs[5][0]
        self.tab_subconjuntos= self._tabs[6][0]
        self.tab_epsilon     = self._tabs[7][0]
        self.tab_afn_ops     = self._tabs[8][0]
        self.tab_conversion  = self._tabs[9][0]
        self.tab_regex       = self._tabs[10][0]

    def _refresh_tab_labels(self):
        """Update tab labels after language change."""
        for idx, (frame, panel, key) in enumerate(self._tabs):
            try:
                self.notebook.tab(idx, text=t(key))
            except Exception:
                pass

    def _build_status_bar(self):
        c = theme.colors
        self.status_bar = tk.Frame(self, bg=c['bg_panel'], height=24)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        self.status_label = tk.Label(
            self.status_bar,
            text=t('status.default'),
            bg=c['bg_panel'], fg=c['text_secondary'],
            font=('Consolas', 9), anchor='w', padx=8)
        self.status_label.pack(fill=tk.X, side=tk.LEFT, expand=True)

    # ── Automaton change ──────────────────────────────────────────

    def set_tipo(self, tipo):
        if tipo == 'AFD':
            self.current_automaton = AFD()
        elif tipo == 'AFN':
            self.current_automaton = AFN()
        elif tipo == 'AFN-λ':
            self.current_automaton = AFNLambda()
        self.current_tipo = tipo
        self.on_automaton_changed()
        self.add_log(t('log.new_automaton', t=tipo), 'info')

    def on_automaton_changed(self):
        auto = self.current_automaton
        tipo = self.current_tipo
        self.canvas_widget.dibujar_automata(auto, tipo)
        self.tabla_widget.configurar(
            estados=auto.estados, alfabeto=auto.alfabeto,
            estado_inicial=auto.estado_inicial,
            estados_finales=auto.estados_finales,
            delta=auto.delta, tipo=tipo)
        self.sidebar.refresh()
        self._update_status_bar()

    def _update_status_bar(self):
        auto = self.current_automaton
        tipo = self.current_tipo
        self.status_label.configure(
            text=f"{tipo_display(tipo)}  |Q|={len(auto.estados)}  |Σ|={len(auto.alfabeto)}  "
                 f"q₀={auto.estado_inicial or '—'}  |F|={len(auto.estados_finales)}")

    # ── Log ───────────────────────────────────────────────────────

    def add_log(self, message, log_type='info'):
        if hasattr(self, 'log_panel'):
            self.log_panel.add_log(message, log_type)

    # ── Menu actions ──────────────────────────────────────────────

    def _nuevo_automata(self):
        self.set_tipo(self.current_tipo)

    def _limpiar_todo(self):
        self.set_tipo(self.current_tipo)
        self.add_log(t('log.cleared'), 'info')

    def _toggle_theme(self):
        theme.toggle()
        c = theme.colors
        self.configure(bg=c['bg_main'])
        theme.apply_to_ttk_style(self.style)
        self._update_status_bar()

    def _set_language(self, code: str):
        lang.set(code)
        self._lang_var.set(code)

    def _verificar_completitud(self):
        auto = self.current_automaton
        if not isinstance(auto, AFD):
            messagebox.showinfo(t('dlg.completeness'), "Solo aplica para AFDs." if lang.current == 'es' else "Only applies to DFAs.")
            return
        completo = auto.es_completo()
        if completo:
            messagebox.showinfo(t('dlg.completeness'), t('msg.completeness_yes'))
            self.add_log(t('log.complete_yes'), 'success')
        else:
            messagebox.showwarning(t('dlg.completeness'), t('msg.completeness_no'))
            self.add_log(t('log.complete_no'), 'warning')

    def _eliminar_inutiles(self):
        auto = self.current_automaton
        if not isinstance(auto, AFD):
            messagebox.showinfo(t('dlg.completeness'),
                                "Solo aplica para AFDs." if lang.current == 'es'
                                else "Only applies to DFAs.")
            return
        orig = len(auto.estados)
        afd_limpio = auto.limpiar()
        auto.estados = afd_limpio.estados
        auto.alfabeto = afd_limpio.alfabeto
        auto.delta = afd_limpio.delta
        auto.estado_inicial = afd_limpio.estado_inicial
        auto.estados_finales = afd_limpio.estados_finales
        new = len(auto.estados)
        self.on_automaton_changed()
        self.add_log(t('log.useless_removed', orig=orig, new=new), 'success')

    def _show_help(self):
        HelpDialog(self)

    def _show_examples(self):
        ExamplesDialog(self, self)

    def _show_about(self):
        messagebox.showinfo(t('menu.help.about').strip(), t('about.text'))

    # ── Import / Export ───────────────────────────────────────────

    def import_json(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("All", "*.*")],
            title="Import automaton" if lang.current == 'en' else "Importar autómata")
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                tipo = data.get('tipo', 'AFD')
                if tipo == 'AFD':
                    self.current_automaton = deserializar_afd(data)
                    self.current_tipo = 'AFD'
                elif tipo == 'AFN':
                    self.current_automaton = deserializar_afn(data)
                    self.current_tipo = 'AFN'
                elif tipo in ('AFNLambda', 'AFN-λ'):
                    self.current_automaton = deserializar_afn_lambda(data)
                    self.current_tipo = 'AFN-λ'
                else:
                    self.current_automaton = deserializar_generico(data)
                    if isinstance(self.current_automaton, AFD):
                        self.current_tipo = 'AFD'
                    elif isinstance(self.current_automaton, AFNLambda):
                        self.current_tipo = 'AFN-λ'
                    else:
                        self.current_tipo = 'AFN'
                self.on_automaton_changed()
                self.add_log(t('log.imported_from', f=os.path.basename(filepath)), 'success')
            except Exception as e:
                messagebox.showerror(t('dlg.error'),
                                     f"{'No se pudo importar' if lang.current=='es' else 'Could not import'}:\n{e}")
                self.add_log(t('log.import_error', e=str(e)), 'error')

    def export_json(self):
        if not self.current_automaton.estados:
            messagebox.showwarning(t('dlg.no_export'), t('msg.no_export'))
            return
        if not hasattr(self, '_last_save_path'):
            self._last_save_path = None
        if self._last_save_path is None:
            self.export_json_as()
            return
        try:
            data = serializar_generico(self.current_automaton)
            with open(self._last_save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.add_log(t('log.exported', f=os.path.basename(self._last_save_path)), 'success')
        except Exception as e:
            messagebox.showerror(t('dlg.error'), str(e))

    def export_json_as(self):
        if not self.current_automaton.estados:
            messagebox.showwarning(t('dlg.no_export'), t('msg.no_export'))
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="Export automaton" if lang.current == 'en' else "Exportar autómata")
        if filepath:
            try:
                data = serializar_generico(self.current_automaton)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self._last_save_path = filepath
                self.add_log(t('log.exported', f=os.path.basename(filepath)), 'success')
            except Exception as e:
                messagebox.showerror(t('dlg.error'), str(e))

    def load_example(self, example_func):
        try:
            resultado = example_func()
            if isinstance(resultado, tuple):
                automaton = resultado[0]
                self.add_log(t('log.example_pair'), 'info')
            else:
                automaton = resultado
            self.current_automaton = automaton
            if isinstance(automaton, AFNLambda):
                self.current_tipo = 'AFN-λ'
            elif isinstance(automaton, AFN):
                self.current_tipo = 'AFN'
            else:
                self.current_tipo = 'AFD'
            self.on_automaton_changed()
            self.add_log(t('log.example_loaded_type', t=self.current_tipo), 'success')
        except Exception as e:
            self.add_log(t('log.example_error', e=str(e)), 'error')

    # ── Theme & Language change ───────────────────────────────────

    def _on_theme_change(self):
        c = theme.colors
        self.configure(bg=c['bg_main'])
        theme.apply_to_ttk_style(self.style)
        self._update_status_bar()

    def _on_lang_change(self):
        """Called when the language changes — refresh all UI text."""
        self.title(t('app.title'))
        self._rebuild_menu()
        self._refresh_tab_labels()
        self._update_status_bar()
        self.add_log(t('log.started'), 'info')
        # Propagate to each panel that supports it
        for _, panel, _ in self._tabs:
            if hasattr(panel, 'refresh_lang'):
                panel.refresh_lang()
        if hasattr(self.sidebar, 'refresh_lang'):
            self.sidebar.refresh_lang()
        if hasattr(self.canvas_widget, 'refresh_lang'):
            self.canvas_widget.refresh_lang()
        if hasattr(self.log_panel, 'refresh_lang'):
            self.log_panel.refresh_lang()
        # Extra panels not in self._tabs
        for panel in [self.subset_panel, self.epsilon_panel,
                      self.afn_ops_panel, self.conversion_panel,
                      self.regex_panel]:
            if hasattr(panel, 'refresh_lang'):
                panel.refresh_lang()


if __name__ == '__main__':
    app = AutomaTECLab()
    app.mainloop()
