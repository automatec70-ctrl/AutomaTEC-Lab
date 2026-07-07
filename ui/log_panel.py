"""
LogPanel — Panel de registro de acciones.
Muestra mensajes con marca de tiempo, coloreados por tipo.
"""

from ui.i18n import lang, t
import tkinter as tk
from tkinter import ttk
from datetime import datetime


class LogPanel(tk.Frame):
    """Panel de log con mensajes coloreados por tipo."""

    def __init__(self, parent, theme_ref, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme_ref
        self._setup_ui()
        self.theme.on_change(self._on_theme_change)

    def _setup_ui(self):
        """Construye la interfaz del panel de log."""
        c = self.theme.colors

        self.configure(bg=c['bg_panel'])

        # Barra superior con título y botón limpiar
        header = tk.Frame(self, bg=c['bg_panel'])
        header.pack(fill=tk.X, padx=4, pady=(4, 0))

        self._title_label = tk.Label(
            header, text=t('log.title'), bg=c['bg_panel'],
            fg=c['text'], font=('Segoe UI', 10, 'bold'))
        self._title_label.pack(side=tk.LEFT, padx=4)

        self.btn_limpiar = tk.Button(
            header, text=t('log.clear'), command=self.limpiar,
            bg=c['bg_surface'], fg=c['text'],
            activebackground=c['accent_hover'],
            activeforeground=c['text_on_accent'],
            relief='flat', font=('Segoe UI', 8), padx=8, cursor='hand2'
        )
        self.btn_limpiar.pack(side=tk.RIGHT, padx=4)

        # Text widget con scrollbar
        text_frame = tk.Frame(self, bg=c['bg_panel'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.text = tk.Text(
            text_frame, wrap=tk.WORD, state=tk.DISABLED,
            bg=c['bg_input'], fg=c['text'],
            font=('Consolas', 9), relief='flat',
            insertbackground=c['text'],
            selectbackground=c['accent'],
            selectforeground=c['text_on_accent'],
            padx=6, pady=4, height=6
        )

        scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.text.yview
        )
        self.text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configurar tags de colores
        self.text.tag_configure('info', foreground=c['log_info'])
        self.text.tag_configure('success', foreground=c['log_success'])
        self.text.tag_configure('error', foreground=c['log_error'])
        self.text.tag_configure('warning', foreground=c['log_warning'])
        self.text.tag_configure('timestamp', foreground=c['text_secondary'])

    def add_log(self, message, log_type='info'):
        """
        Agrega una entrada al log.
        
        Args:
            message: Texto del mensaje
            log_type: 'info', 'success', 'error', 'warning'
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        tag = log_type if log_type in ('info', 'success', 'error', 'warning') else 'info'

        self.text.configure(state=tk.NORMAL)
        self.text.insert(tk.END, f'[{timestamp}] ', 'timestamp')
        self.text.insert(tk.END, f'{message}\n', tag)
        self.text.configure(state=tk.DISABLED)

        # Auto-scroll al final
        self.text.see(tk.END)

    def limpiar(self):
        """Limpia todo el log."""
        self.text.configure(state=tk.NORMAL)
        self.text.delete('1.0', tk.END)
        self.text.configure(state=tk.DISABLED)

    def _on_theme_change(self):
        """Actualiza colores cuando cambia el tema."""
        c = self.theme.colors
        self.configure(bg=c['bg_panel'])
        self.text.configure(
            bg=c['bg_input'], fg=c['text'],
            insertbackground=c['text'],
            selectbackground=c['accent'],
            selectforeground=c['text_on_accent']
        )

        # Actualizar tags
        self.text.tag_configure('info', foreground=c['log_info'])
        self.text.tag_configure('success', foreground=c['log_success'])
        self.text.tag_configure('error', foreground=c['log_error'])
        self.text.tag_configure('warning', foreground=c['log_warning'])
        self.text.tag_configure('timestamp', foreground=c['text_secondary'])

        # Título y botón
        self._title_label.configure(bg=c['bg_panel'], fg=c['text'])
        self.btn_limpiar.configure(bg=c['bg_surface'], fg=c['text'])

    def refresh_lang(self):
        try:
            self._title_label.configure(text=t('log.title'))
            self.btn_limpiar.configure(text=t('log.clear'))
        except Exception:
            pass
