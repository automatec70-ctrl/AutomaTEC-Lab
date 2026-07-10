"""
Sistema de temas para AutomaTEC-Lab.
Soporta tema oscuro (por defecto) y tema claro.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict


class Theme:
    """Gestor de temas con soporte para modo oscuro y claro."""

    # Dark theme colors (default)
    DARK = {
        'bg_main': '#1E1E2E',
        'bg_panel': '#2A2A3E',
        'bg_surface': '#353550',
        'bg_input': '#353550',
        'bg_canvas': '#0F0F1A',
        'accent': '#7C3AED',
        'accent_hover': '#9F67FF',
        'green': '#10B981',
        'red': '#EF4444',
        'yellow': '#F59E0B',
        'text': '#E2E8F0',
        'text_secondary': '#94A3B8',
        'text_on_accent': '#FFFFFF',
        'border': '#3A3A52',
        'grid_line': '#2A2A3E',
        'state_fill': '#2A2A3E',
        'state_border': '#7C3AED',
        'final_accent': '#10B981',
        'transition_arrow': '#7C3AED',
        'highlight': '#A78BFA',
        'select_bg': '#7C3AED',
        'select_fg': '#FFFFFF',
        'tab_active_bg': '#7C3AED',
        'tab_active_fg': '#FFFFFF',
        'tab_inactive_bg': '#1E1E2E',
        'tab_inactive_fg': '#94A3B8',
        'scrollbar_bg': '#3A3A52',
        'scrollbar_trough': '#1E1E2E',
        'log_info': '#E2E8F0',
        'log_success': '#10B981',
        'log_error': '#EF4444',
        'log_warning': '#F59E0B',
    }

    # Light theme colors
    LIGHT = {
        'bg_main': '#F8FAFC',
        'bg_panel': '#FFFFFF',
        'bg_surface': '#F1F5F9',
        'bg_input': '#FFFFFF',
        'bg_canvas': '#F8FAFC',
        'accent': '#7C3AED',
        'accent_hover': '#6D28D9',
        'green': '#059669',
        'red': '#DC2626',
        'yellow': '#D97706',
        'text': '#1E293B',
        'text_secondary': '#64748B',
        'text_on_accent': '#FFFFFF',
        'border': '#E2E8F0',
        'grid_line': '#E2E8F0',
        'state_fill': '#FFFFFF',
        'state_border': '#7C3AED',
        'final_accent': '#059669',
        'transition_arrow': '#7C3AED',
        'highlight': '#A78BFA',
        'select_bg': '#7C3AED',
        'select_fg': '#FFFFFF',
        'tab_active_bg': '#7C3AED',
        'tab_active_fg': '#FFFFFF',
        'tab_inactive_bg': '#F1F5F9',
        'tab_inactive_fg': '#64748B',
        'scrollbar_bg': '#CBD5E1',
        'scrollbar_trough': '#F1F5F9',
        'log_info': '#1E293B',
        'log_success': '#059669',
        'log_error': '#DC2626',
        'log_warning': '#D97706',
    }

    # Aliases for backward compatibility with table_widget and other widgets
    # that use the old ThemedStyle color key names
    _ALIASES = {
        'fg_text': 'text',
        'fg_muted': 'text_secondary',
        'fg_button': 'text_on_accent',
        'bg_button': 'accent',
        'bg_button_hover': 'accent_hover',
        'bg_button_active': 'accent_hover',
        'accent_violet': 'accent',
        'accent_green': 'green',
        'accent_red': 'red',
        'accent_yellow': 'yellow',
        'table_header_bg': 'bg_surface',
        'table_header_fg': 'text',
        'table_cell_bg': 'bg_panel',
        'table_cell_fg': 'text',
        'log_bg': 'bg_main',
    }

    def __init__(self):
        self._is_dark = True
        self._colors = dict(self.DARK)
        self._callbacks = []

    @property
    def is_dark(self) -> bool:
        return self._is_dark

    @property
    def colors(self) -> Dict[str, str]:
        """Return colors dict with aliases resolved for backward compatibility."""
        result = dict(self._colors)
        # Add aliased keys so old code using fg_text, accent_violet, etc. still works
        for alias, canonical in self._ALIASES.items():
            if canonical in result:
                result[alias] = result[canonical]
        return result

    def toggle(self) -> None:
        """Alterna entre tema oscuro y claro."""
        self._is_dark = not self._is_dark
        self._colors = dict(self.DARK if self._is_dark else self.LIGHT)
        for cb in self._callbacks:
            cb()

    def on_change(self, callback) -> None:
        """Registra callback para cuando cambia el tema."""
        self._callbacks.append(callback)

    def apply_to_ttk_style(self, style: ttk.Style) -> None:
        """Aplica los colores actuales al estilo ttk."""
        c = self._colors

        # Use 'clam' theme as base for better customization support
        style.theme_use('clam')

        # Configure all ttk widgets with current theme colors
        style.configure('TFrame', background=c['bg_main'])
        style.configure('Panel.TFrame', background=c['bg_panel'])
        style.configure('Surface.TFrame', background=c['bg_surface'])

        style.configure('TLabel', background=c['bg_main'], foreground=c['text'],
                        font=('Segoe UI', 10))
        style.configure('Panel.TLabel', background=c['bg_panel'], foreground=c['text'],
                        font=('Segoe UI', 10))
        style.configure('Title.TLabel', background=c['bg_panel'], foreground=c['accent'],
                        font=('Segoe UI', 11, 'bold'))
        style.configure('Subtitle.TLabel', background=c['bg_panel'],
                        foreground=c['text_secondary'], font=('Segoe UI', 9))
        style.configure('Header.TLabel', background=c['bg_panel'], foreground=c['text'],
                        font=('Segoe UI', 12, 'bold'))
        style.configure('Muted.TLabel', background=c['bg_main'],
                        foreground=c['text_secondary'], font=('Segoe UI', 9))
        style.configure('Status.TLabel', background=c['bg_panel'],
                        foreground=c['text_secondary'], font=('Segoe UI', 9))

        style.configure('TButton', background=c['accent'], foreground=c['text_on_accent'],
                        font=('Segoe UI', 9), borderwidth=0, focuscolor='none')
        style.map('TButton', background=[('active', c['accent_hover'])])

        style.configure('Secondary.TButton', background=c['bg_surface'],
                        foreground=c['text'], font=('Segoe UI', 9))
        style.map('Secondary.TButton', background=[('active', c['border'])])

        style.configure('Accent.TButton', background=c['accent'],
                        foreground=c['text_on_accent'], font=('Segoe UI', 9, 'bold'),
                        borderwidth=0, focuscolor='none')
        style.map('Accent.TButton', background=[('active', c['accent_hover'])])

        style.configure('Danger.TButton', background=c['red'], foreground='#FFFFFF',
                        borderwidth=0, focuscolor='none')
        style.map('Danger.TButton', background=[('active', '#DC2626')])

        style.configure('Success.TButton', background=c['green'], foreground='#FFFFFF',
                        borderwidth=0, focuscolor='none')
        style.map('Success.TButton', background=[('active', '#059669')])

        style.configure('TEntry', fieldbackground=c['bg_input'], foreground=c['text'],
                        insertcolor=c['text'], bordercolor=c['border'],
                        focuscolor=c['accent'])

        style.configure('TCombobox', fieldbackground=c['bg_input'], foreground=c['text'],
                        bordercolor=c['border'], selectbackground=c['accent'],
                        selectforeground=c['text_on_accent'],
                        arrowcolor=c['text'])
        # The 'readonly' state overrides fieldbackground/foreground on many platforms,
        # so we must explicitly set them via map() for all states.
        style.map('TCombobox',
                  fieldbackground=[
                      ('readonly', c['bg_input']),
                      ('disabled', c['bg_surface']),
                      ('active',   c['bg_input']),
                      ('!disabled', c['bg_input']),
                  ],
                  foreground=[
                      ('readonly', c['text']),
                      ('disabled', c['text_secondary']),
                      ('active',   c['text']),
                      ('!disabled', c['text']),
                  ],
                  selectbackground=[
                      ('readonly', c['accent']),
                      ('!disabled', c['accent']),
                  ],
                  selectforeground=[
                      ('readonly', c['text_on_accent']),
                      ('!disabled', c['text_on_accent']),
                  ],
                  bordercolor=[
                      ('focus', c['accent']),
                      ('!disabled', c['border']),
                  ])

        style.configure('TCheckbutton', background=c['bg_panel'], foreground=c['text'],
                        font=('Segoe UI', 9))
        style.map('TCheckbutton', background=[('active', c['bg_panel'])])

        style.configure('TRadiobutton', background=c['bg_panel'], foreground=c['text'],
                        font=('Segoe UI', 9))
        style.map('TRadiobutton', background=[('active', c['bg_panel'])])

        style.configure('TNotebook', background=c['bg_main'], borderwidth=0)
        style.configure('TNotebook.Tab', background=c['tab_inactive_bg'],
                        foreground=c['tab_inactive_fg'], padding=[12, 4],
                        font=('Segoe UI', 9))
        style.map('TNotebook.Tab',
                  background=[('selected', c['tab_active_bg'])],
                  foreground=[('selected', c['tab_active_fg'])])

        style.configure('Horizontal.TSeparator', background=c['border'])
        style.configure('TSeparator', background=c['border'])

        style.configure('TScrollbar', background=c['scrollbar_bg'],
                        troughcolor=c['scrollbar_trough'], borderwidth=0, arrowsize=14)
        style.map('TScrollbar', background=[('active', c['accent'])])

        # Fix Combobox dropdown (popdown) listbox colors.
        # These are Tk option database settings — the only reliable way to style
        # the internal listbox that appears when the combobox is opened.
        try:
            style.master.option_add('*TCombobox*Listbox.background', c['bg_input'])
            style.master.option_add('*TCombobox*Listbox.foreground', c['text'])
            style.master.option_add('*TCombobox*Listbox.selectBackground', c['accent'])
            style.master.option_add('*TCombobox*Listbox.selectForeground', c['text_on_accent'])
            style.master.option_add('*TCombobox*Listbox.font', 'Consolas 10')
        except Exception:
            pass

        style.configure('Horizontal.TScrollbar', background=c['scrollbar_bg'],
                        troughcolor=c['scrollbar_trough'], borderwidth=0, arrowsize=14)

        style.configure('Treeview', background=c['bg_panel'], foreground=c['text'],
                        fieldbackground=c['bg_panel'], borderwidth=0,
                        font=('Segoe UI', 9))
        style.configure('Treeview.Heading', background=c['bg_surface'],
                        foreground=c['text'], font=('Segoe UI', 9, 'bold'))
        style.map('Treeview',
                  background=[('selected', c['select_bg'])],
                  foreground=[('selected', c['select_fg'])])

        style.configure('TLabelframe', background=c['bg_panel'], foreground=c['text'],
                        bordercolor=c['border'])
        style.configure('TLabelframe.Label', background=c['bg_panel'],
                        foreground=c['accent'], font=('Segoe UI', 10, 'bold'))

        style.configure('TScale', background=c['bg_panel'], troughcolor=c['bg_input'])

        style.configure('TPanedwindow', background=c['border'])

    def apply_to_widget(self, widget):
        """Aplica colores del tema a un widget tk específico."""
        c = self._colors

        if isinstance(widget, tk.Frame):
            widget.configure(bg=c['bg_panel'])
        elif isinstance(widget, tk.Label):
            widget.configure(bg=c['bg_panel'], fg=c['text'])
        elif isinstance(widget, tk.Button):
            widget.configure(bg=c['bg_surface'], fg=c['text'],
                             activebackground=c['accent_hover'],
                             activeforeground=c['text_on_accent'],
                             highlightbackground=c['border'])
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=c['bg_input'], fg=c['text'],
                             insertbackground=c['text'],
                             highlightbackground=c['border'],
                             highlightcolor=c['accent'])
        elif isinstance(widget, tk.Text):
            widget.configure(bg=c['bg_input'], fg=c['text'],
                             insertbackground=c['text'],
                             selectbackground=c['accent'],
                             selectforeground=c['text_on_accent'])
        elif isinstance(widget, tk.Canvas):
            widget.configure(bg=c['bg_canvas'],
                             highlightbackground=c['border'])
        elif isinstance(widget, tk.Checkbutton):
            widget.configure(bg=c['bg_panel'], fg=c['text'],
                             activebackground=c['bg_panel'],
                             activeforeground=c['text'],
                             selectcolor=c['bg_input'])
        elif isinstance(widget, tk.Radiobutton):
            widget.configure(bg=c['bg_panel'], fg=c['text'],
                             activebackground=c['bg_panel'],
                             activeforeground=c['text'],
                             selectcolor=c['bg_input'])
        elif isinstance(widget, tk.Listbox):
            widget.configure(bg=c['bg_input'], fg=c['text'],
                             selectbackground=c['accent'],
                             selectforeground=c['text_on_accent'])
        elif isinstance(widget, tk.Scrollbar):
            widget.configure(bg=c['scrollbar_bg'],
                             troughcolor=c['scrollbar_trough'],
                             activebackground=c['accent'])
        elif isinstance(widget, tk.Menubutton):
            widget.configure(bg=c['bg_surface'], fg=c['text'],
                             activebackground=c['accent_hover'],
                             activeforeground=c['text_on_accent'])

    def apply_to_all(self, widget=None):
        """Aplica tema recursivamente a todos los widgets."""
        if widget is None:
            return
        try:
            self.apply_to_widget(widget)
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self.apply_to_all(child)

    def get_color(self, name: str) -> str:
        """Obtiene un color del tema actual por nombre (soporta aliases)."""
        # Check canonical names first
        if name in self._colors:
            return self._colors[name]
        # Check aliases
        if name in self._ALIASES:
            canonical = self._ALIASES[name]
            return self._colors.get(canonical, '#000000')
        return '#000000'


# Global theme instance
theme = Theme()
