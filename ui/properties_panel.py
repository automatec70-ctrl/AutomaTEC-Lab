"""
PropertiesPanel — Panel para propiedades del lenguaje de un AFD.

Contiene:
  - Grilla de botones de verificación de propiedades:
    - ¿Lenguaje vacío?
    - ¿Lenguaje infinito?
    - ¿Lenguaje finito?
    - Cadena más corta aceptada
    - Estados accesibles
    - Estados productivos
    - Estados útiles
    - [Limpiar AFD] (eliminar estados no útiles)
  - Cada propiedad muestra resultado en label con código de color
  - Estados accesibles/productivos/útiles mostrados como lista separada por comas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Set

from ui.i18n import lang, t
from ui.theme import theme
from core.afd import AFD


class PropertiesPanel(tk.Frame):
    """Panel para propiedades del lenguaje de un AFD."""

    def __init__(self, parent, app_ref, **kwargs):
        c = theme.colors
        super().__init__(parent, bg=c['bg_panel'], **kwargs)
        self.app = app_ref

        self._result_labels = {}

        self._build_ui()
        theme.on_change(self._on_theme_change)

    # ── Construcción de la UI ────────────────────────────────────

    def _build_ui(self):
        c = theme.colors

        # Título
        self._title = tk.Label(self, text=t('prop.title'),
                               bg=c['bg_panel'], fg=c['accent'],
                               font=('Segoe UI', 12, 'bold'))
        self._title.pack(anchor='w', padx=12, pady=(10, 4))

        # Info del AFD
        self._afd_info = tk.Label(
            self, text='', bg=c['bg_panel'], fg=c['text_secondary'],
            font=('Consolas', 9), wraplength=500, justify='left')
        self._afd_info.pack(anchor='w', padx=12, pady=(0, 4))

        # Scrollable content
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

        # Propiedades
        properties = [
            ('vacio',       'prop.btn.empty',      self._check_vacio),
            ('infinito',    'prop.btn.infinite',   self._check_infinito),
            ('finito',      'prop.btn.finite',     self._check_finito),
            ('cadena_corta','prop.btn.shortest',   self._check_cadena_corta),
            ('accesibles',  'prop.btn.accessible', self._check_accesibles),
            ('productivos', 'prop.btn.productive', self._check_productivos),
            ('utiles',      'prop.btn.useful',     self._check_utiles),
        ]

        self._prop_buttons = {}   # key -> button widget
        for key, i18n_key, command in properties:
            self._build_property_row(inner, key, i18n_key, command)

        # Separador
        self._separator = tk.Frame(inner, bg=c['border'], height=1)
        self._separator.pack(fill=tk.X, padx=12, pady=8)

        # Botón Limpiar AFD
        self._btn_limpiar = tk.Button(
            inner, text=t('prop.clean'),
            command=self._limpiar_afd,
            bg=c['red'], fg='#FFFFFF', activebackground='#DC2626',
            activeforeground='#FFFFFF', font=('Segoe UI', 9, 'bold'),
            relief='flat', cursor='hand2', padx=10, pady=4)
        self._btn_limpiar.pack(fill=tk.X, padx=12, pady=(0, 4))

        # Botón Verificar Todo
        self._btn_all = tk.Button(
            inner, text=t('prop.verify_all'),
            command=self._verificar_todas,
            bg=c['accent'], fg=c['text_on_accent'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            font=('Segoe UI', 9, 'bold'), relief='flat', cursor='hand2',
            padx=10, pady=4)
        self._btn_all.pack(fill=tk.X, padx=12, pady=(0, 10))

    def _build_property_row(self, parent, key: str, i18n_key: str,
                            command):
        c = theme.colors

        row = tk.Frame(parent, bg=c['bg_panel'])
        row.pack(fill=tk.X, padx=12, pady=2)

        btn = tk.Button(
            row, text=t(i18n_key), command=command,
            bg=c['bg_surface'], fg=c['text'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            font=('Segoe UI', 9), relief='flat', cursor='hand2',
            padx=8, pady=2, anchor='w')
        btn.pack(side=tk.LEFT, fill=tk.X, expand=False)
        self._prop_buttons[key] = (btn, i18n_key)

        result = tk.Label(
            row, text='', bg=c['bg_panel'], fg=c['text'],
            font=('Consolas', 9), anchor='w', wraplength=350,
            justify='left')
        result.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

        self._result_labels[key] = result

    # ── Obtener AFD ──────────────────────────────────────────────

    def _get_afd(self) -> Optional[AFD]:
        automaton = self.app.current_automaton
        if not automaton:
            messagebox.showwarning(t('dlg.no_automaton'), t('msg.no_automaton'))
            return None
        if not isinstance(automaton, AFD):
            messagebox.showwarning(t('dlg.not_afd'), t('msg.prop_not_afd'))
            return None
        if not automaton.estado_inicial:
            messagebox.showwarning(t('dlg.no_initial'), t('msg.no_initial'))
            return None
        if not automaton.estados:
            messagebox.showwarning(t('dlg.no_states'), t('msg.no_states'))
            return None
        return automaton

    # ── Verificar propiedades ────────────────────────────────────

    def _check_vacio(self):
        afd = self._get_afd()
        if afd is None:
            return
        c = theme.colors
        try:
            es_vacio = afd.es_lenguaje_vacio()
            if es_vacio:
                self._result_labels['vacio'].configure(
                    text=t('prop.empty_yes'), fg=c['green'])
                self.app.add_log(t('log.prop_empty_yes'), 'info')
            else:
                self._result_labels['vacio'].configure(
                    text=t('prop.empty_no'), fg=c['red'])
                self.app.add_log(t('log.prop_empty_no'), 'info')
        except Exception as e:
            self._result_labels['vacio'].configure(
                text=f'Error: {str(e)}', fg=c['red'])

    def _check_infinito(self):
        afd = self._get_afd()
        if afd is None:
            return
        c = theme.colors
        try:
            es_infinito = afd.es_lenguaje_infinito()
            if es_infinito:
                self._result_labels['infinito'].configure(
                    text=t('prop.infinite_yes'), fg=c['green'])
                self.app.add_log(t('log.prop_infinite_yes'), 'info')
            else:
                self._result_labels['infinito'].configure(
                    text=t('prop.infinite_no'), fg=c['red'])
                self.app.add_log(t('log.prop_infinite_no'), 'info')
        except Exception as e:
            self._result_labels['infinito'].configure(
                text=f'Error: {str(e)}', fg=c['red'])

    def _check_finito(self):
        afd = self._get_afd()
        if afd is None:
            return
        c = theme.colors
        try:
            es_finito = afd.es_lenguaje_finito()
            if es_finito:
                self._result_labels['finito'].configure(
                    text=t('prop.finite_yes'), fg=c['green'])
                self.app.add_log(t('log.prop_finite_yes'), 'info')
            else:
                self._result_labels['finito'].configure(
                    text=t('prop.finite_no'), fg=c['red'])
                self.app.add_log(t('log.prop_finite_no'), 'info')
        except Exception as e:
            self._result_labels['finito'].configure(
                text=f'Error: {str(e)}', fg=c['red'])

    def _check_cadena_corta(self):
        afd = self._get_afd()
        if afd is None:
            return
        c = theme.colors
        try:
            cadena = afd.cadena_mas_corta()
            if cadena is None:
                self._result_labels['cadena_corta'].configure(
                    text=t('prop.shortest_none'), fg=c['text_secondary'])
                self.app.add_log(t('log.prop_shortest_none'), 'info')
            elif cadena == '':
                self._result_labels['cadena_corta'].configure(
                    text=t('prop.shortest_lambda'), fg=c['green'])
                self.app.add_log(t('log.prop_shortest_empty'), 'info')
            else:
                self._result_labels['cadena_corta'].configure(
                    text=t('prop.shortest_val', w=cadena, n=len(cadena)), fg=c['green'])
                self.app.add_log(t('log.prop_shortest', w=cadena), 'info')
        except Exception as e:
            self._result_labels['cadena_corta'].configure(
                text=f'Error: {str(e)}', fg=c['red'])

    def _check_accesibles(self):
        afd = self._get_afd()
        if afd is None:
            return
        c = theme.colors
        try:
            accesibles = afd.estados_accesibles()
            no_accesibles = afd.estados - accesibles

            if accesibles:
                lista = ', '.join(sorted(accesibles))
                self._result_labels['accesibles'].configure(
                    text=f'{lista} ({len(accesibles)}/{len(afd.estados)})',
                    fg=c['green'])
            else:
                self._result_labels['accesibles'].configure(
                    text=t('prop.no_accessible'),
                    fg=c['text_secondary'])

            if no_accesibles:
                self.app.add_log(
                    t('log.prop_not_accessible', states=', '.join(sorted(no_accesibles))), 'warning')
            self.app.add_log(
                t('log.prop_accessible', n=len(accesibles), total=len(afd.estados)),
                'info')
        except Exception as e:
            self._result_labels['accesibles'].configure(
                text=f'Error: {str(e)}', fg=c['red'])

    def _check_productivos(self):
        afd = self._get_afd()
        if afd is None:
            return
        c = theme.colors
        try:
            productivos = afd.estados_productivos()
            no_productivos = afd.estados - productivos

            if productivos:
                lista = ', '.join(sorted(productivos))
                self._result_labels['productivos'].configure(
                    text=f'{lista} ({len(productivos)}/{len(afd.estados)})',
                    fg=c['green'])
            else:
                self._result_labels['productivos'].configure(
                    text=t('prop.no_productive'),
                    fg=c['text_secondary'])

            if no_productivos:
                self.app.add_log(
                    t('log.prop_not_productive', states=', '.join(sorted(no_productivos))), 'warning')
            self.app.add_log(
                t('log.prop_productive', n=len(productivos), total=len(afd.estados)), 'info')
        except Exception as e:
            self._result_labels['productivos'].configure(
                text=f'Error: {str(e)}', fg=c['red'])

    def _check_utiles(self):
        afd = self._get_afd()
        if afd is None:
            return
        c = theme.colors
        try:
            utiles = afd.estados_utiles()
            no_utiles = afd.estados - utiles

            if utiles:
                lista = ', '.join(sorted(utiles))
                self._result_labels['utiles'].configure(
                    text=f'{lista} ({len(utiles)}/{len(afd.estados)})',
                    fg=c['green'])
            else:
                self._result_labels['utiles'].configure(
                    text=t('prop.no_useful'),
                    fg=c['text_secondary'])

            if no_utiles:
                self.app.add_log(
                    f'Estados NO útiles: '
                    f'{", ".join(sorted(no_utiles))}', 'warning')
            self.app.add_log(
                t('log.prop_useful', n=len(utiles), total=len(afd.estados)), 'info')
        except Exception as e:
            self._result_labels['utiles'].configure(
                text=f'Error: {str(e)}', fg=c['red'])

    def _verificar_todas(self):
        afd = self._get_afd()
        if afd is None:
            return
        c = theme.colors

        self.update_afd_info()

        try:
            # Lenguaje vacío
            es_vacio = afd.es_lenguaje_vacio()
            if es_vacio:
                self._result_labels['vacio'].configure(
                    text='✓ SÍ — L(M) = ∅', fg=c['green'])
            else:
                self._result_labels['vacio'].configure(
                    text='✗ NO — L(M) ≠ ∅', fg=c['red'])

            # Lenguaje infinito
            es_infinito = afd.es_lenguaje_infinito()
            if es_infinito:
                self._result_labels['infinito'].configure(
                    text='✓ SÍ — |L(M)| = ∞', fg=c['green'])
            else:
                self._result_labels['infinito'].configure(
                    text='✗ NO — |L(M)| < ∞', fg=c['red'])

            # Lenguaje finito
            es_finito = afd.es_lenguaje_finito()
            if es_finito:
                self._result_labels['finito'].configure(
                    text='✓ SÍ — |L(M)| < ∞', fg=c['green'])
            else:
                self._result_labels['finito'].configure(
                    text='✗ NO — |L(M)| = ∞', fg=c['red'])

            # Cadena más corta
            cadena = afd.cadena_mas_corta()
            if cadena is None:
                self._result_labels['cadena_corta'].configure(
                    text='No existe (L = ∅)', fg=c['text_secondary'])
            elif cadena == '':
                self._result_labels['cadena_corta'].configure(
                    text='λ (cadena vacía)', fg=c['green'])
            else:
                self._result_labels['cadena_corta'].configure(
                    text=f'"{cadena}" (|w|={len(cadena)})', fg=c['green'])

            # Estados accesibles
            accesibles = afd.estados_accesibles()
            if accesibles:
                lista = ', '.join(sorted(accesibles))
                self._result_labels['accesibles'].configure(
                    text=f'{lista} ({len(accesibles)}/{len(afd.estados)})',
                    fg=c['green'])
            else:
                self._result_labels['accesibles'].configure(
                    text='∅ (ningún estado accesible)',
                    fg=c['text_secondary'])

            # Estados productivos
            productivos = afd.estados_productivos()
            if productivos:
                lista = ', '.join(sorted(productivos))
                self._result_labels['productivos'].configure(
                    text=f'{lista} ({len(productivos)}/{len(afd.estados)})',
                    fg=c['green'])
            else:
                self._result_labels['productivos'].configure(
                    text='∅ (ningún estado productivo)',
                    fg=c['text_secondary'])

            # Estados útiles
            utiles = afd.estados_utiles()
            no_utiles = afd.estados - utiles
            if utiles:
                lista = ', '.join(sorted(utiles))
                self._result_labels['utiles'].configure(
                    text=f'{lista} ({len(utiles)}/{len(afd.estados)})',
                    fg=c['green'])
            else:
                self._result_labels['utiles'].configure(
                    text='∅ (ningún estado útil)',
                    fg=c['text_secondary'])

            self.app.add_log(t('log.prop_all'), 'success')

            if no_utiles:
                self.app.add_log(
                    t('log.prop_not_useful', states=', '.join(sorted(no_utiles))),
                    'warning')

        except Exception as e:
            messagebox.showerror('Error',
                                 f'Error al verificar propiedades:\n{str(e)}')
            self.app.add_log(f'Error en propiedades: {str(e)}', 'error')

    # ── Limpiar AFD ──────────────────────────────────────────────

    def _limpiar_afd(self):
        afd = self._get_afd()
        if afd is None:
            return

        utiles = afd.estados_utiles()
        no_utiles = afd.estados - utiles

        if not no_utiles:
            messagebox.showinfo(t('dlg.clean_title'), t('msg.clean_already'))
            return

        if not messagebox.askyesno(
            'Confirmar limpieza',
            t('msg.clean_confirm', n=len(no_utiles), states=', '.join(sorted(no_utiles)))
        ):
            return

        try:
            afd_limpio = afd.limpiar()

            afd.estados = afd_limpio.estados
            afd.alfabeto = afd_limpio.alfabeto
            afd.delta = afd_limpio.delta
            afd.estado_inicial = afd_limpio.estado_inicial
            afd.estados_finales = afd_limpio.estados_finales

            self.app.add_log(
                t('log.clean_done', n=len(no_utiles), r=len(afd.estados)), 'success')

            self.update_afd_info()
            self.app.on_automaton_changed()
            self._verificar_todas()

        except Exception as e:
            messagebox.showerror('Error',
                                 f'Error al limpiar AFD:\n{str(e)}')
            self.app.add_log(f'Error limpiando AFD: {str(e)}', 'error')

    # ── Actualizar info ──────────────────────────────────────────

    def update_afd_info(self):
        automaton = self.app.current_automaton
        if automaton and isinstance(automaton, AFD):
            info = (f'AFD: Q={sorted(automaton.estados)}, '
                    f'Σ={sorted(automaton.alfabeto)}, '
                    f'q0={automaton.estado_inicial}, '
                    f'F={sorted(automaton.estados_finales)}, '
                    f'|Q|={len(automaton.estados)}')
            self._afd_info.configure(text=info)
        else:
            self._afd_info.configure(text='(no hay AFD definido)')

    # ── Tema ─────────────────────────────────────────────────────

    def _on_theme_change(self):
        c = theme.colors
        self.configure(bg=c['bg_panel'])
        self._title.configure(bg=c['bg_panel'], fg=c['accent'])
        self._afd_info.configure(bg=c['bg_panel'], fg=c['text_secondary'])
        self._scroll_canvas.configure(bg=c['bg_panel'])
        self._scroll_inner.configure(bg=c['bg_panel'])
        self._separator.configure(bg=c['border'])

        for key, label in self._result_labels.items():
            label.configure(bg=c['bg_panel'])

    def refresh_lang(self):
        try:
            self._title.configure(text=t('prop.title'))
            self._btn_limpiar.configure(text=t('prop.clean'))
            self._btn_all.configure(text=t('prop.verify_all'))
            for key, (btn, i18n_key) in getattr(self, '_prop_buttons', {}).items():
                try: btn.configure(text=t(i18n_key))
                except Exception: pass
        except Exception:
            pass
