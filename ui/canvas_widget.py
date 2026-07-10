"""
Widget de visualizacion de automatas usando Graphviz.
Genera diagramas profesionalmente y los muestra en un Canvas de Tkinter.
Permite guardar la imagen en disco como PNG, SVG, PDF o EPS.
"""

from ui.i18n import lang, t, tipo_display
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import graphviz
import os
import sys
import subprocess
import tempfile
import shutil
from PIL import Image, ImageTk


def _ensure_graphviz_path():
    """
    Agrega el directorio de Graphviz al PATH de Windows si no esta.
    Retorna True si Graphviz esta disponible, False si no.
    """
    # Verificar si ya funciona
    try:
        subprocess.run(['dot', '-V'], capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass

    # Buscar en rutas comunes de Windows
    if sys.platform == 'win32':
        common_dirs = [
            r'C:\Program Files\Graphviz\bin',
            r'C:\Program Files (x86)\Graphviz\bin',
        ]
        # Agregar rutas desde variables de entorno
        pf = os.environ.get('ProgramFiles', '')
        pfx86 = os.environ.get('ProgramFiles(x86)', '')
        if pf:
            common_dirs.append(os.path.join(pf, 'Graphviz', 'bin'))
        if pfx86:
            common_dirs.append(os.path.join(pfx86, 'Graphviz', 'bin'))
        # Chocolatey
        common_dirs.append(r'C:\ProgramData\chocolatey\bin')
        # WinGet
        localappdata = os.environ.get('LOCALAPPDATA', '')
        if localappdata:
            common_dirs.append(os.path.join(localappdata, 'Microsoft', 'WinGet', 'Links'))

        for d in common_dirs:
            dot_exe = os.path.join(d, 'dot.exe')
            if os.path.isdir(d) and os.path.isfile(dot_exe):
                os.environ['PATH'] = d + os.pathsep + os.environ.get('PATH', '')
                return True

    return False


# Intentar configurar Graphviz al importar el modulo
_graphviz_available = _ensure_graphviz_path()


class AutomataCanvas(tk.Frame):
    """
    Widget que dibuja automatas usando Graphviz.
    Soporta: estados, transiciones, estados iniciales/finales, self-loops.
    Permite: zoom, guardar imagen en disco, resaltar estados.
    """

    def __init__(self, parent, theme_ref, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme_ref
        self.current_image = None
        self.current_photo = None
        self.zoom_level = 1.0
        self.highlighted_states = set()
        self.highlighted_transitions = []

        # State for the automaton being displayed
        self._estados = set()
        self._alfabeto = set()
        self._delta = {}
        self._estado_inicial = ''
        self._estados_finales = set()
        self._tipo = 'AFD'

        self._setup_ui()
        self.theme.on_change(self._on_theme_change)

    def _setup_ui(self):
        """Configura la interfaz del canvas."""
        c = self.theme.colors

        # Toolbar
        toolbar = tk.Frame(self, bg=c['bg_panel'], height=36)
        toolbar.pack(fill=tk.X, padx=0, pady=0)
        toolbar.pack_propagate(False)

        # Zoom controls
        self.btn_zoom_in = tk.Button(
            toolbar, text=t('canvas.zoom_in'), command=self.zoom_in,
            bg=c['bg_surface'], fg=c['text'],
            activebackground=c['accent_hover'], activeforeground=c['text_on_accent'],
            relief='flat', font=('Segoe UI', 9), padx=6, cursor='hand2'
        )
        self.btn_zoom_in.pack(side=tk.LEFT, padx=2, pady=3)

        self.btn_zoom_out = tk.Button(
            toolbar, text=t('canvas.zoom_out'), command=self.zoom_out,
            bg=c['bg_surface'], fg=c['text'],
            activebackground=c['accent_hover'], activeforeground=c['text_on_accent'],
            relief='flat', font=('Segoe UI', 9), padx=6, cursor='hand2'
        )
        self.btn_zoom_out.pack(side=tk.LEFT, padx=2, pady=3)

        self.btn_ajustar = tk.Button(
            toolbar, text=t('canvas.fit'), command=self._ajustar,
            bg=c['bg_surface'], fg=c['text'],
            activebackground=c['accent_hover'], activeforeground=c['text_on_accent'],
            relief='flat', font=('Segoe UI', 9), padx=6, cursor='hand2'
        )
        self.btn_ajustar.pack(side=tk.LEFT, padx=2, pady=3)

        self.zoom_label = tk.Label(
            toolbar, text="100%", bg=c['bg_panel'], fg=c['text_secondary'],
            font=('Consolas', 9)
        )
        self.zoom_label.pack(side=tk.LEFT, padx=6)

        # Separator
        tk.Frame(toolbar, bg=c['border'], width=1).pack(
            side=tk.LEFT, fill=tk.Y, padx=4, pady=4
        )

        # Save button
        self.btn_save = tk.Button(
            toolbar, text=t('canvas.save_image'), command=self.save_image,
            bg=c['green'], fg='#FFFFFF',
            activebackground='#059669', activeforeground='#FFFFFF',
            relief='flat', font=('Segoe UI', 9), padx=8, cursor='hand2'
        )
        self.btn_save.pack(side=tk.LEFT, padx=2, pady=3)

        # Type badge
        self.tipo_label = tk.Label(
            toolbar, text="AFD", bg=c['accent'], fg='#FFFFFF',
            font=('Consolas', 9, 'bold'), padx=6
        )
        self.tipo_label.pack(side=tk.RIGHT, padx=6, pady=3)

        # Canvas area with scrollbars
        canvas_frame = tk.Frame(self, bg=c['bg_canvas'])
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_frame, bg=c['bg_canvas'], highlightthickness=0, cursor='crosshair'
        )
        self.h_scroll = ttk.Scrollbar(
            canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview
        )
        self.v_scroll = ttk.Scrollbar(
            canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview
        )

        self.canvas.configure(
            xscrollcommand=self.h_scroll.set,
            yscrollcommand=self.v_scroll.set
        )

        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind mouse wheel for zoom
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind('<Button-4>', lambda e: self.zoom_in())
        self.canvas.bind('<Button-5>', lambda e: self.zoom_out())

    def _on_mousewheel(self, event):
        """Handle mouse wheel for zoom."""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def set_automaton(self, estados, alfabeto, delta, estado_inicial,
                      estados_finales, tipo='AFD'):
        """Establece el automata a visualizar y redibuja."""
        self._estados = estados if isinstance(estados, set) else set(estados)
        self._alfabeto = alfabeto if isinstance(alfabeto, set) else set(alfabeto)
        self._delta = delta
        self._estado_inicial = estado_inicial
        self._estados_finales = (
            estados_finales if isinstance(estados_finales, set)
            else set(estados_finales)
        )
        self._tipo = tipo
        self.tipo_label.configure(text=tipo_display(tipo))
        self.redraw()

    def set_highlighted_states(self, states):
        """Resalta los estados dados en el diagrama."""
        self.highlighted_states = set(states) if states else set()
        self.redraw()

    def set_highlighted_transitions(self, transitions):
        """Resalta las transiciones dadas."""
        self.highlighted_transitions = transitions or []
        self.redraw()

    def clear_highlights(self):
        """Limpia todos los resaltados."""
        self.highlighted_states = set()
        self.highlighted_transitions = []
        self.redraw()

    def _build_graphviz(self) -> graphviz.Digraph:
        """Construye el objeto graphviz.Digraph para el automata actual."""
        c = self.theme.colors

        dot = graphviz.Digraph(format='png')
        dot.attr(
            rankdir='LR', bgcolor=c['bg_canvas'], dpi='96',
            fontname='Consolas', pad='0.5', nodesep='0.6', ranksep='0.8'
        )

        # Graph title (hidden)
        dot.attr(label='', labelloc='t', fontsize='0')

        # Node defaults
        node_fill = c['state_fill']
        node_border = c['state_border']
        text_color = c['text']
        final_color = c['final_accent']
        highlight_color = c['highlight']

        dot.attr(
            'node', shape='circle', style='filled', fillcolor=node_fill,
            color=node_border, fontcolor=text_color, fontname='Consolas',
            fontsize='12', width='0.7', height='0.7', penwidth='2'
        )

        dot.attr(
            'edge', color=c['transition_arrow'], fontcolor=text_color,
            fontname='Consolas', fontsize='11', arrowsize='0.8', penwidth='1.5'
        )

        # Invisible starting node for initial arrow
        if self._estado_inicial:
            dot.node('__start__', label='', shape='none', width='0', height='0')
            dot.edge('__start__', self._estado_inicial)

        # Draw states
        for estado in sorted(self._estados):
            is_final = estado in self._estados_finales
            is_highlighted = estado in self.highlighted_states

            attrs = {}
            if is_final:
                attrs['shape'] = 'doublecircle'
                attrs['color'] = final_color
                attrs['penwidth'] = '2.5'
            if is_highlighted:
                attrs['color'] = highlight_color
                attrs['penwidth'] = '3'
                attrs['style'] = 'filled,bold'
                attrs['fillcolor'] = '#5A3AAA'

            dot.node(estado, **attrs)

        # Group transitions: (from, to) -> list of symbols
        transition_groups = {}

        if self._tipo == 'AFD':
            for desde in self._delta:
                for simbolo, hacia in self._delta[desde].items():
                    if simbolo in ('\u03bb', '\u03b5', 'lambda', 'epsilon'):
                        simbolo = '\u03bb'
                    if hacia and hacia in self._estados:
                        key = (desde, hacia)
                        if key not in transition_groups:
                            transition_groups[key] = []
                        transition_groups[key].append(simbolo)
        else:
            # AFN or AFN-lambda
            for desde in self._delta:
                for simbolo, hacia_set in self._delta[desde].items():
                    if simbolo in ('\u03bb', '\u03b5', 'lambda', 'epsilon'):
                        simbolo = '\u03bb'
                    targets = (
                        hacia_set
                        if isinstance(hacia_set, (set, list, frozenset, tuple))
                        else [hacia_set] if hacia_set else []
                    )
                    for hacia in targets:
                        if hacia and hacia in self._estados:
                            key = (desde, hacia)
                            if key not in transition_groups:
                                transition_groups[key] = []
                            if simbolo not in transition_groups[key]:
                                transition_groups[key].append(simbolo)

        # Draw transitions
        for (desde, hacia), simbolos in transition_groups.items():
            label = ', '.join(sorted(simbolos))
            attrs = {}

            # Check if highlighted
            for ht in self.highlighted_transitions:
                if ht.get('from') == desde and ht.get('to') == hacia:
                    attrs['color'] = highlight_color
                    attrs['penwidth'] = '2.5'
                    break

            if desde == hacia:
                # Self-loop
                attrs['label'] = label
                attrs['labeldistance'] = '2.5'
                attrs['labelangle'] = '-20'
                dot.edge(desde, hacia, **attrs)
            else:
                attrs['label'] = label
                dot.edge(desde, hacia, **attrs)

        return dot

    def redraw(self):
        """Redibuja el automata en el canvas."""
        if not self._estados:
            self.canvas.delete('all')
            c = self.theme.colors
            self.canvas.create_text(
                self.canvas.winfo_width() // 2 or 300,
                self.canvas.winfo_height() // 2 or 200,
                text=t('canvas.no_automaton'),
                fill=c['text_secondary'], font=('Segoe UI', 12)
            )
            return

        # Intentar encontrar Graphviz si no se encontro antes
        global _graphviz_available
        if not _graphviz_available:
            _graphviz_available = _ensure_graphviz_path()

        if not _graphviz_available:
            self.canvas.delete('all')
            c = self.theme.colors
            self.canvas.create_text(
                200, 100,
                text="Graphviz (dot) no encontrado.\n\n"
                     "Instala Graphviz desde:\n"
                     "https://graphviz.org/download/\n\n"
                     "Luego reinicia la aplicacion.",
                fill=c['red'], font=('Consolas', 10)
            )
            return

        try:
            dot = self._build_graphviz()

            # Render to PNG
            with tempfile.TemporaryDirectory() as tmpdir:
                filepath = dot.render(
                    filename='automata', directory=tmpdir, cleanup=True
                )

                # Load and display image
                img = Image.open(filepath)

                # Apply zoom
                w, h = img.size
                new_w = int(w * self.zoom_level)
                new_h = int(h * self.zoom_level)
                if new_w > 0 and new_h > 0:
                    img = img.resize((new_w, new_h), Image.LANCZOS)

                self.current_image = img
                self.current_photo = ImageTk.PhotoImage(img)

                self.canvas.delete('all')
                self.canvas.create_image(
                    0, 0, anchor=tk.NW, image=self.current_photo
                )
                self.canvas.configure(scrollregion=(0, 0, new_w, new_h))

        except Exception as e:
            self.canvas.delete('all')
            c = self.theme.colors
            error_msg = str(e)
            if 'dot' in error_msg.lower() or 'graphviz' in error_msg.lower():
                help_msg = (
                    "Graphviz no encontrado en el PATH.\n\n"
                    "Instala Graphviz desde:\n"
                    "https://graphviz.org/download/\n\n"
                    "En Windows, descarga el .msi,\n"
                    "instala y REINICIA la aplicacion.\n\n"
                    "Si ya lo instalaste, agrega\n"
                    "C:\\Program Files\\Graphviz\\bin\n"
                    "al PATH del sistema."
                )
            else:
                help_msg = f"Error al generar diagrama:\n{error_msg}"
            self.canvas.create_text(
                200, 150,
                text=help_msg,
                fill=c['red'], font=('Consolas', 10)
            )

    def zoom_in(self):
        """Incrementa el nivel de zoom."""
        self.zoom_level = min(5.0, self.zoom_level * 1.2)
        self.zoom_label.configure(text=f"{int(self.zoom_level * 100)}%")
        self._display_image()

    def zoom_out(self):
        """Decrementa el nivel de zoom."""
        self.zoom_level = max(0.1, self.zoom_level / 1.2)
        self.zoom_label.configure(text=f"{int(self.zoom_level * 100)}%")
        self._display_image()

    def _ajustar(self):
        """Ajusta la imagen al tamano del canvas."""
        if self.current_image is None:
            return
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w < 10 or canvas_h < 10:
            return
        zoom_w = canvas_w / self.current_image.width
        zoom_h = canvas_h / self.current_image.height
        self.zoom_level = min(zoom_w, zoom_h) * 0.95
        self.zoom_label.configure(text=f"{int(self.zoom_level * 100)}%")
        self._display_image()

    def _display_image(self):
        """Muestra la imagen en el canvas con el zoom actual."""
        if self.current_image is None:
            return

        w = int(self.current_image.width * self.zoom_level)
        h = int(self.current_image.height * self.zoom_level)

        if w < 1 or h < 1:
            return

        try:
            resized = self.current_image.resize((w, h), Image.LANCZOS)
            self.current_photo = ImageTk.PhotoImage(resized)

            self.canvas.delete('all')
            self.canvas.configure(scrollregion=(0, 0, w, h))
            self.canvas.create_image(
                0, 0, anchor='nw', image=self.current_photo, tags='automata'
            )
        except Exception:
            pass

    def save_image(self):
        """Guarda la imagen del automata en disco.
        Soporta PNG (300 DPI), SVG, PDF y EPS.
        """
        if not self._estados:
            messagebox.showwarning(
                "Sin automata", "No hay un automata para guardar."
            )
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG (300 DPI)", "*.png"),
                ("SVG (Vectorial)", "*.svg"),
                ("PDF", "*.pdf"),
                ("EPS (PostScript)", "*.eps"),
                ("Todos los archivos", "*.*")
            ],
            title="Guardar diagrama del automata"
        )

        if not filepath:
            return

        try:
            dot = self._build_graphviz()
            ext = os.path.splitext(filepath)[1][1:].lower()

            if ext == 'png':
                dot.attr(dpi='300')
                with tempfile.TemporaryDirectory() as tmpdir:
                    rendered = dot.render(
                        filename='automata', directory=tmpdir,
                        format='png', cleanup=True
                    )
                    shutil.copy2(rendered, filepath)
            else:
                with tempfile.TemporaryDirectory() as tmpdir:
                    rendered = dot.render(
                        filename='automata', directory=tmpdir,
                        format=ext, cleanup=True
                    )
                    shutil.copy2(rendered, filepath)

            messagebox.showinfo(
                "Imagen guardada", f"Diagrama guardado en:\n{filepath}"
            )
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo guardar la imagen:\n{str(e)}"
            )

    def _on_theme_change(self):
        """Reaplica colores cuando cambia el tema."""
        c = self.theme.colors
        self.configure(bg=c['bg_main'])
        self.btn_zoom_in.configure(bg=c['bg_surface'], fg=c['text'])
        self.btn_zoom_out.configure(bg=c['bg_surface'], fg=c['text'])
        self.btn_ajustar.configure(bg=c['bg_surface'], fg=c['text'])
        self.zoom_label.configure(bg=c['bg_panel'], fg=c['text_secondary'])
        self.btn_save.configure(bg=c['green'])
        self.tipo_label.configure(bg=c['accent'])
        self.canvas.configure(bg=c['bg_canvas'])
        self.redraw()

    # Backward-compatible aliases
    def dibujar_automata(self, automata, tipo='AFD'):
        """Alias: dibuja un objeto automata del core."""
        if automata is None:
            self._estados = set()
            self._alfabeto = set()
            self._delta = {}
            self._estado_inicial = ''
            self._estados_finales = set()
            self._tipo = tipo
            self.tipo_label.configure(text=tipo_display(tipo))
            self.redraw()
            return

        estados = getattr(automata, 'estados', set())
        alfabeto = getattr(automata, 'alfabeto', set())
        estado_inicial = getattr(automata, 'estado_inicial', '')
        estados_finales = getattr(automata, 'estados_finales', set())
        delta = getattr(automata, 'delta', {})

        self.set_automaton(
            estados, alfabeto, delta, estado_inicial,
            estados_finales, tipo
        )

    def refresh_theme(self):
        """Alias: actualiza colores del tema y redibuja."""
        self._on_theme_change()

    def guardar_imagen(self, ruta=None):
        """Alias: guarda la imagen del automata."""
        if ruta is not None:
            if not self._estados:
                return
            try:
                dot = self._build_graphviz()
                ext = os.path.splitext(ruta)[1][1:].lower()
                if ext == 'png':
                    dot.attr(dpi='300')
                with tempfile.TemporaryDirectory() as tmpdir:
                    rendered = dot.render(
                        filename='automata', directory=tmpdir,
                        format=ext if ext != 'png' else 'png',
                        cleanup=True
                    )
                    shutil.copy2(rendered, ruta)
            except Exception as e:
                messagebox.showerror(
                    "Error", f"No se pudo guardar:\n{str(e)}"
                )
        else:
            self.save_image()

    def refresh_lang(self):
        try:
            self.btn_zoom_in.configure(text=t('canvas.zoom_in'))
            self.btn_zoom_out.configure(text=t('canvas.zoom_out'))
            self.btn_ajustar.configure(text=t('canvas.fit'))
            self.btn_save.configure(text=t('canvas.save_image'))
            # Re-translate the automaton type badge
            self.tipo_label.configure(text=tipo_display(self._tipo))
        except Exception:
            pass
