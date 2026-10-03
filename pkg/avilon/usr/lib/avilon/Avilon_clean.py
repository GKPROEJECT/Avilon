# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
import shutil
from PIL import Image, ImageTk, ImageDraw
import webbrowser
import tkinter.font as tkFont
import urllib.parse
import re
import time
import subprocess
import sys
import platform
import shlex
from datetime import datetime, timedelta

def resource_path(relative_path):
    """Obtener la ruta correcta para recursos, funciona tanto en .py como en .exe"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def get_app_data_dir():
    """Obtener el directorio de datos apropiado para el sistema operativo."""
    if sys.platform.startswith('linux'):
        data_home = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
        return os.path.join(data_home, 'Avilon')
    if sys.platform == 'win32' and getattr(sys, 'frozen', False):
        return os.path.join(os.environ.get('APPDATA', os.path.expanduser('~/AppData/Roaming')), 'Avilon')
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.expanduser('~'), '.avilon')
    return os.path.dirname(os.path.abspath(__file__))


def prepare_app_data_dir():
    """Crear datos del usuario y conservar datos de una instalación Linux anterior."""
    data_dir = get_app_data_dir()
    os.makedirs(data_dir, exist_ok=True)
    if sys.platform.startswith('linux'):
        legacy_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.abspath(legacy_dir) != os.path.abspath(data_dir):
            for filename in ('avilon_games.json', 'avilon_config.json'):
                legacy_file = os.path.join(legacy_dir, filename)
                current_file = os.path.join(data_dir, filename)
                if os.path.isfile(legacy_file) and not os.path.exists(current_file):
                    shutil.copy2(legacy_file, current_file)
    return data_dir


def set_window_icon(window):
    """Apply platform-appropriate, high-resolution Avilon window icons."""
    try:
        if sys.platform == 'win32':
            icon_path = resource_path('logo.ico')
            if os.path.isfile(icon_path):
                window.iconbitmap(icon_path)
                return

        icon_path = resource_path('logo.png')
        if os.path.isfile(icon_path):
            with Image.open(icon_path) as source:
                master_icon = source.convert('RGBA')
            icon_sizes = (16, 24, 32, 48, 64, 128, 256)
            icons = tuple(
                ImageTk.PhotoImage(
                    fit_icon_to_square(master_icon, size),
                    master=window,
                )
                for size in icon_sizes
            )
            window.iconphoto(True, *icons)
            window._avilon_icons = icons
            return

        logo_path = resource_path('logo.png')
        if os.path.isfile(logo_path):
            with Image.open(logo_path) as logo:
                icon = ImageTk.PhotoImage(fit_icon_to_square(logo), master=window)
            window.iconphoto(True, icon)
            window._avilon_icons = (icon,)
    except Exception as e:
        print(f"No se pudo aplicar el icono de Avilon: {e}")


def fit_icon_to_square(image, size=128):
    image = image.convert('RGBA')
    image.thumbnail((size, size), Image.Resampling.LANCZOS)
    square = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    square.alpha_composite(image, ((size - image.width) // 2, (size - image.height) // 2))
    return square


def desktop_entry_quote(value):
    """Escapar argumentos para la sintaxis Exec de archivos .desktop."""
    escaped = (value.replace('\\', '\\\\').replace('"', '\\"')
               .replace('$', '\\$').replace('`', '\\`').replace('%', '%%'))
    return f'"{escaped}"'


def get_primary_monitor_bounds(window):
    """Return the primary monitor bounds, with a Tk screen-size fallback."""
    if sys.platform.startswith('linux'):
        try:
            import gi
            gi.require_version('Gdk', '3.0')
            from gi.repository import Gdk

            display = Gdk.Display.get_default()
            if display is not None:
                monitor = display.get_primary_monitor()
                if monitor is None and display.get_n_monitors() > 0:
                    monitors = [
                        display.get_monitor(index)
                        for index in range(display.get_n_monitors())
                    ]
                    monitor = next(
                        (
                            candidate for candidate in monitors
                            if candidate is not None
                            and candidate.get_geometry().x <= 0
                            < candidate.get_geometry().x + candidate.get_geometry().width
                            and candidate.get_geometry().y <= 0
                            < candidate.get_geometry().y + candidate.get_geometry().height
                        ),
                        monitors[0]
                    )
                if monitor is not None:
                    geometry = monitor.get_geometry()
                    if geometry.width > 0 and geometry.height > 0:
                        return geometry.x, geometry.y, geometry.width, geometry.height
        except (ImportError, ValueError, AttributeError, RuntimeError):
            pass

    return 0, 0, window.winfo_screenwidth(), window.winfo_screenheight()


def center_window_on_primary_monitor(window, width, height):
    """Center a Tk window on the primary display (placement may be WM-managed on Wayland)."""
    monitor_x, monitor_y, monitor_width, monitor_height = get_primary_monitor_bounds(window)
    width = min(width, monitor_width)
    height = min(height, monitor_height)
    x = monitor_x + (monitor_width - width) // 2
    y = monitor_y + (monitor_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")
    return x, y, width, height


def is_path_within(path, directory):
    try:
        return os.path.commonpath((os.path.abspath(path), os.path.abspath(directory))) == os.path.abspath(directory)
    except (OSError, ValueError):
        return False


def mousewheel_units(event):
    if getattr(event, 'num', None) == 4:
        return -3
    if getattr(event, 'num', None) == 5:
        return 3
    delta = getattr(event, 'delta', 0)
    if abs(delta) >= 120:
        return -int(delta / 120)
    return -1 if delta > 0 else 1 if delta < 0 else 0


import threading
if sys.platform == 'win32':
    import winreg
else:
    winreg = None
try:
    import pygetwindow as gw
except ImportError:
    gw = None

class SplashScreen:
    def __init__(self, language='es', translations=None):
        self.language = language
        self.translations = translations if translations else {}
        
        self.splash = tk.Tk()
        self.splash.title("AVILON")
        
        # Ocultar inmediatamente la ventana para evitar el parpadeo
        self.splash.withdraw()
        
        set_window_icon(self.splash)
        
        # Configurar ventana sin bordes y centrada
        self.splash.overrideredirect(True)
        self.splash.configure(bg='#080d18')
        self.splash_width = 640
        self.splash_height = 440
        self.splash_geometry = center_window_on_primary_monitor(
            self.splash, self.splash_width, self.splash_height
        )
        
        # Crear canvas para efectos de fondo
        self.canvas = tk.Canvas(
            self.splash, 
            width=self.splash_width,
            height=self.splash_height,
            highlightthickness=0,
            bg='#080d18'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Crear fondo con gradiente
        self.create_gradient_background()
        
        # Crear borde con efecto glow
        self.create_border_glow()
        
        # Variables para animaciones
        self.logo_animation_step = 0
        self.title_alpha = 0
        self.glow_intensity = 0
        self.animation_active = True
        self.after_ids = set()
        
        # Contenedor principal
        self.setup_main_content()
        
        # Configurar estilo de la barra de progreso
        self.setup_progress_style()
        
        # Iniciar animaciones de entrada
        self.start_entrance_animation()
        
    def create_gradient_background(self):
        """Draw a restrained gaming backdrop with a framed content panel."""
        colors = [
            '#080d18',
            '#0b1220',
            '#101a2a',
            '#121d30',
            '#101a2a',
            '#0b1220',
            '#080d18'
        ]
        
        height_per_section = self.splash_height // len(colors)
        
        for i, color in enumerate(colors):
            y1 = i * height_per_section
            y2 = (self.splash_height if i == len(colors) - 1
                  else (i + 1) * height_per_section)
            self.canvas.create_rectangle(
                0, y1, self.splash_width, y2,
                fill=color, outline=color
            )
    
    def create_border_glow(self):
        """Add restrained esports-style framing and accent lines."""
        self.canvas.create_rectangle(
            1, 1, self.splash_width - 1, self.splash_height - 1,
            outline='#26364e', width=1, fill=''
        )
        self.canvas.create_rectangle(
            1, 1, self.splash_width - 1, 4,
            fill='#4f8cff', outline=''
        )
        self.canvas.create_rectangle(
            24, 24, self.splash_width - 24, self.splash_height - 24,
            outline='#1d2b40', width=1, fill=''
        )
        self.canvas.create_line(24, 24, 72, 24, fill='#55d6ff', width=2)
        self.canvas.create_line(24, 24, 24, 72, fill='#55d6ff', width=2)
        self.canvas.create_line(
            self.splash_width - 24, self.splash_height - 24,
            self.splash_width - 72, self.splash_height - 24,
            fill='#7568ff', width=2
        )
    
    def setup_main_content(self):
        """Configurar el contenido principal del splash"""
        # Logo animado
        self.setup_animated_logo()
        
        # Título con efecto
        self.create_title()
        
        # Subtítulo
        self.create_subtitle()
        
        # Barra de progreso moderna
        self.create_modern_progress_bar()
        
        # Estado y versión
        self.create_status_area()
        
        # Partículas decorativas
        self.create_decorative_particles()
    
    def setup_animated_logo(self):
        """Configurar logo con animación"""
        try:
            logo_path = resource_path("logo.png")
            
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path).convert('RGBA')
                logo_image.thumbnail((76, 76), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                
                self.logo_id = self.canvas.create_image(
                    self.splash_width // 2, 82, image=self.logo_photo, anchor='center'
                )
            else:
                self.logo_id = self.canvas.create_text(
                    self.splash_width // 2, 82, text="◆", font=('Segoe UI', 56, 'bold'),
                    fill='#55d6ff', anchor='center'
                )
        except Exception:
            self.logo_id = self.canvas.create_text(
                self.splash_width // 2, 82, text="◆", font=('Segoe UI', 56, 'bold'),
                fill='#55d6ff', anchor='center'
            )
    
    def create_title(self):
        """Crear título con diseño moderno"""
        self.title_id = self.canvas.create_text(
            self.splash_width // 2, 169, text="AVILON",
            font=('Segoe UI', 34, 'bold'),
            fill='#4b607a', anchor='center'
        )
        self.canvas.create_text(
            self.splash_width // 2, 211,
            text=self.get_splash_text('splash_tagline'),
            font=('Segoe UI', 8, 'bold'),
            fill='#7790ad', anchor='center'
        )
    
    def create_subtitle(self):
        """Crear subtítulo elegante"""
        subtitle_text = self.get_splash_text('splash_subtitle')
        self.subtitle_id = self.canvas.create_text(
            self.splash_width // 2, 242, text=subtitle_text,
            font=('Segoe UI', 12),
            fill='#b7c5d8', anchor='center'
        )
    
    def create_modern_progress_bar(self):
        """Crear barra de progreso moderna"""
        progress_y = 300
        progress_x1 = 88
        progress_x2 = self.splash_width - 88
        progress_h = 7
        
        self.progress_bg = self.canvas.create_rectangle(
            progress_x1, progress_y, progress_x2, progress_y + progress_h,
            fill='#172337', outline='#2c405d', width=1
        )
        
        self.progress_value = 0
        self.progress_items = []
        self.progress_x1 = progress_x1
        self.progress_x2 = progress_x2
        self.progress_y = progress_y
        self.progress_h = progress_h
    
    def create_status_area(self):
        """Crear área de estado y versión"""
        status_text = self.get_splash_text('splash_initializing')
        self.status_id = self.canvas.create_text(
            self.splash_width // 2, 329, text=status_text,
            font=('Segoe UI', 10),
            fill='#c5d3e5', anchor='center'
        )
        self.progress_percent_id = self.canvas.create_text(
            self.splash_width // 2, 360, text='0%',
            font=('Segoe UI', 10, 'bold'),
            fill='#55d6ff', anchor='center'
        )
        
        version_text = self.get_splash_text('splash_version')
        self.version_id = self.canvas.create_text(
            self.splash_width // 2, 397, text=version_text,
            font=('Segoe UI', 8),
            fill='#71839d', anchor='center'
        )
    
    def create_decorative_particles(self):
        """Crear partículas decorativas sutiles"""
        self.particles = []
        import random
        
        for _ in range(12):
            x = random.randint(40, self.splash_width - 40)
            y = random.randint(40, self.splash_height - 40)
            size = random.randint(1, 2)
            
            particle = self.canvas.create_oval(
                x, y, x+size, y+size,
                fill='#55d6ff', outline=''
            )
            self.particles.append(particle)
    
    def start_entrance_animation(self):
        """Iniciar animaciones de entrada"""
        self.animate_logo_entrance()
        self.animate_title_fade_in()
        self.animate_particles()

    def schedule_after(self, delay, callback):
        """Programar una tarea del splash que se pueda cancelar antes de destruirlo."""
        after_id = None

        def run_callback():
            self.after_ids.discard(after_id)
            if self.animation_active:
                callback()

        after_id = self.splash.after(delay, run_callback)
        self.after_ids.add(after_id)
        return after_id
    
    def animate_logo_entrance(self):
        """Animar entrada del logo elegante"""
        if self.animation_active and self.logo_animation_step < 25:
            progress = self.logo_animation_step / 25
            logo_y = 82 + int(20 * progress)
            self.canvas.coords(self.logo_id, self.splash_width // 2, logo_y)
            self.logo_animation_step += 1
            self.schedule_after(40, self.animate_logo_entrance)
    
    def animate_title_fade_in(self):
        """Animar fade in del título elegante"""
        if self.animation_active and self.title_alpha < 255:
            self.title_alpha = min(255, self.title_alpha + 18)
            red = 75 + int((245 - 75) * self.title_alpha / 255)
            green = 96 + int((248 - 96) * self.title_alpha / 255)
            blue = 122 + int((255 - 122) * self.title_alpha / 255)
            self.canvas.itemconfig(
                self.title_id, fill=f'#{red:02x}{green:02x}{blue:02x}'
            )
            self.schedule_after(80, self.animate_title_fade_in)
    
    def animate_particles(self):
        """Animar partículas flotantes sutiles"""
        if not self.animation_active:
            return
            
        import random
        
        for particle in self.particles:
            coords = self.canvas.coords(particle)
            if len(coords) >= 4:
                dx = random.uniform(-0.3, 0.3)
                dy = random.uniform(-0.3, 0.3)
                self.canvas.move(particle, dx, dy)
                
                if random.random() < 0.08:
                    colors = ['#55d6ff', '#4f8cff', '#7568ff']
                    new_color = random.choice(colors)
                    self.canvas.itemconfig(particle, fill=new_color)
        
        self.schedule_after(120, self.animate_particles)
    
    def setup_progress_style(self):
        """Configurar el estilo de la barra de progreso"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores modernos para la barra
        style.configure(
            "Modern.TProgressbar",
            background='#55d6ff',
            troughcolor='#172337',
            borderwidth=0,
            lightcolor='#55d6ff',
            darkcolor='#7568ff',
            relief='flat'
        )
    
    def update_progress(self, value, status_text):
        """Actualizar la barra de progreso y el texto de estado"""
        self.progress_value = value
        progress_width = int((value / 100) * (self.progress_x2 - self.progress_x1))
        
        for item in self.progress_items:
            self.canvas.delete(item)
        self.progress_items.clear()
        if value > 0:
            fill = self.canvas.create_rectangle(
                self.progress_x1, self.progress_y,
                self.progress_x1 + progress_width, self.progress_y + self.progress_h,
                fill='#55d6ff', outline=''
            )
            self.progress_items.append(fill)
        
        self.canvas.itemconfig(self.status_id, text=status_text)
        self.canvas.itemconfig(self.progress_percent_id, text=f'{value}%')
        self.animate_status_pulse()
        self.splash.update_idletasks()
    
    def animate_status_pulse(self):
        """Animar pulsación sutil del texto de estado"""
        colors = ['#c5d3e5', '#ffffff', '#c5d3e5']
        for i, color in enumerate(colors):
            self.schedule_after(i * 80, lambda c=color: self.canvas.itemconfig(self.status_id, fill=c))
    
    def simulate_loading(self):
        """Simular proceso de carga con efectos visuales mejorados"""
        self.loading_steps = [
            (5, self.get_splash_text('splash_init_components')),
            (15, self.get_splash_text('splash_loading_config')),
            (30, self.get_splash_text('splash_verifying_files')),
            (45, self.get_splash_text('splash_setting_interface')),
            (60, self.get_splash_text('splash_preparing_library')),
            (75, self.get_splash_text('splash_indexing_content')),
            (90, self.get_splash_text('splash_final_touches')),
            (100, self.get_splash_text('splash_ready'))
        ]
        
        self.current_step = 0
        self.update_loading_step()
    
    def update_loading_step(self):
        """Actualizar un paso de carga con efectos"""
        if self.current_step < len(self.loading_steps):
            progress, status = self.loading_steps[self.current_step]
            self.update_progress(progress, status)
            self.current_step += 1
            
            # Efecto visual especial en ciertos pasos
            if progress in [30, 60, 90]:
                self.create_loading_effect()
            
            # Tiempo variable según el paso (más realista)
            delay = 400 if progress < 50 else 600 if progress < 90 else 300
            self.schedule_after(delay, self.update_loading_step)
        else:
            # Completar la carga con animación de salida
            self.schedule_after(800, self.start_exit_animation)
    
    def create_loading_effect(self):
        """Crear efecto visual durante la carga"""
        # Crear ondas de energía desde el logo
        for i in range(3):
            self.schedule_after(i * 100, self.create_energy_wave)
    
    def create_energy_wave(self):
        """Crear onda de energía elegante"""
        center_x = self.splash_width // 2
        center_y = 102
        wave = self.canvas.create_oval(
            center_x - 5, center_y - 5, center_x + 5, center_y + 5,
            outline='#55d6ff', width=2, fill=''
        )
        
        def expand_wave(size=0):
            if size < 60:
                new_size = size + 4
                self.canvas.coords(wave, 
                                 self.splash_width // 2 - new_size, 102 - new_size,
                                 self.splash_width // 2 + new_size, 102 + new_size)
                
                self.schedule_after(40, lambda: expand_wave(new_size))
            else:
                self.canvas.delete(wave)
        
        expand_wave()
    
    def start_exit_animation(self):
        """Iniciar animación de salida"""
        self.exit_alpha = 255
        self.fade_out()
    
    def fade_out(self):
        """Animación de fade out elegante"""
        if self.exit_alpha > 0:
            self.exit_alpha -= 12
            
            for particle in self.particles:
                self.canvas.move(particle, 0, 1)
            
            self.schedule_after(40, self.fade_out)
        else:
            self.close_splash()
    
    def get_splash_text(self, key):
        """Obtener texto traducido para el splash screen"""
        if not self.translations:
            return key
        
        lang_dict = self.translations.get(self.language, {})
        return lang_dict.get(key, self.translations.get('es', {}).get(key, key))
    
    def close_splash(self):
        """Cerrar el splash screen con callback"""
        self.animation_active = False
        for after_id in self.after_ids:
            try:
                self.splash.after_cancel(after_id)
            except tk.TclError:
                pass
        self.after_ids.clear()
        try:
            self.splash.destroy()
        except tk.TclError:
            pass
            
        if hasattr(self, 'on_complete_callback') and self.on_complete_callback:
            self.on_complete_callback()
    
    def show(self, on_complete=None):
        """Mostrar el splash screen y iniciar la simulación de carga"""
        self.on_complete_callback = on_complete
        
        # Hacer visible la ventana (fue ocultada en __init__)
        self.splash.deiconify()
        
        # Efecto de fade in inicial
        self.splash.attributes('-alpha', 0.0)
        self.splash.update()
        
        def fade_in(alpha=0.0):
            if alpha < 1.0:
                alpha = min(1.0, alpha + 0.1)
                self.splash.attributes('-alpha', alpha)
                self.schedule_after(30, lambda: fade_in(alpha))
            else:
                # Iniciar simulación de carga después del fade in
                self.schedule_after(500, self.simulate_loading)
        
        fade_in()
        self.splash.mainloop()

class AvalonGameManager:
    def __init__(self, root):
        self.root = root
        center_window_on_primary_monitor(self.root, 1200, 800)
        self.root.configure(bg="#2f3136")
        
        # Obtener directorio base del programa (funciona tanto en .py como en .exe)
        self.base_dir = prepare_app_data_dir()
        
        # Configurar icono de la ventana principal
        try:
            self.icon_path = resource_path("logo.ico")
            set_window_icon(self.root)
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")
            self.icon_path = None
        
        # Archivo para almacenar los juegos
        self.games_file = os.path.join(self.base_dir, "avilon_games.json")
        
        # Crear directorio de imágenes si no existe
        self.images_dir = os.path.join(self.base_dir, "game_images")
        os.makedirs(self.images_dir, exist_ok=True)
        self.games = self.load_games()
        
        # Variable para la búsqueda
        self.search_var = None
        
        # Sistema de favoritos
        self.favorites_filter = "all"
        self.game_card_widgets = {}  # Almacenar referencias a widgets de tarjetas por nombre de juego
        
        # Sistema de idiomas y configuración
        self.config_file = os.path.join(self.base_dir, "avilon_config.json")
        self.config_existed_before_start = os.path.isfile(self.config_file)
        
        self.default_keybinds = {
            'add_game': '<Control-n>',
            'config': '<Control-Shift-P>',
            'help': '<F1>',
            'search': '<Control-f>',
            'clear_search': '<Escape>',
            'refresh': '<F5>',
            'favorites': '<Control-Shift-F>',
            'exit': '<Control-q>'
        }
        
        self.config = self.load_config()
        self.tutorial_completed = self.config.get(
            'tutorial_completed',
            self.config_existed_before_start,
        )
        self.current_language = self.config.get('language', 'es')
        self.current_theme = self.config.get('theme', 'slate')
        self.startup_enabled = self.config.get('startup', False)
        self.keybinds = self.config.get('keybinds', self.default_keybinds.copy())
        self.translations = self.load_translations()
        self.themes = self.load_themes()
        
        self.root.title('AVILON')
        
        # Configurar estilo Discord-like
        self.setup_styles()
        
        # Crear barra de menú
        self.create_menu_bar()
        
        # Crear la interfaz
        self.create_main_interface()
        
        # Migrar juegos existentes al directorio local (solo la primera vez)
        self.migrate_existing_games()

        # Cargar juegos después de migrar rutas de imágenes existentes
        self.refresh_games_display()
        
        # Configurar atajos de teclado
        self.setup_keyboard_shortcuts()
        
        # Variables para animaciones gaming
        self.animation_running = False
        self.animation_after_id = None
        self.rgb_index = 0
        self.pulse_alpha = 0
        self.glow_intensity = 0
        
        # Configurar cierre de aplicación para limpiar CEF
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Iniciar animaciones si el tema lo requiere
        self.start_theme_animations()
        if not self.tutorial_completed:
            self.root.after(350, self.show_first_run_tutorial)
    
    def apply_window_icon(self, window):
        """Aplicar el icono a cualquier ventana"""
        set_window_icon(window)
    
    def setup_keyboard_shortcuts(self):
        """Configurar atajos de teclado para mayor comodidad"""
        keybinds = self.keybinds
        
        try:
            add_game_key = keybinds.get('add_game', '<Control-n>')
            if add_game_key:
                self.root.bind(add_game_key, lambda e: self.show_add_game_dialog())
            
            config_key = keybinds.get('config', '<Control-Shift-P>')
            if config_key:
                self.root.bind(config_key, lambda e: self.show_config_dialog())
            
            help_key = keybinds.get('help', '<F1>')
            if help_key:
                self.root.bind(help_key, lambda e: self.show_user_guide_dialog())
            
            search_key = keybinds.get('search', '<Control-f>')
            if search_key:
                self.root.bind(search_key, lambda e: self.focus_search_bar())
            
            clear_search_key = keybinds.get('clear_search', '<Escape>')
            if clear_search_key:
                self.root.bind(clear_search_key, lambda e: self.clear_search_and_focus())
            
            refresh_key = keybinds.get('refresh', '<F5>')
            if refresh_key:
                self.root.bind(refresh_key, lambda e: self.refresh_games_display())
            
            favorites_key = keybinds.get('favorites', '<Control-Shift-F>')
            if favorites_key:
                self.root.bind(favorites_key, lambda e: self.toggle_favorites_filter())
            
            exit_key = keybinds.get('exit', '<Control-q>')
            if exit_key:
                self.root.bind(exit_key, lambda e: self.on_closing())
        except Exception as e:
            print(f"Error setting up keyboard shortcuts: {e}")
    
    
    def focus_search_bar(self):
        """Enfocar la barra de búsqueda"""
        if hasattr(self, 'search_entry') and self.search_entry:
            self.open_search_bar()
            self.search_entry.focus_set()
            # Si hay placeholder, eliminarlo
            if hasattr(self, 'placeholder_active') and self.placeholder_active:
                self.remove_placeholder()
    
    def clear_search_and_focus(self):
        """Limpiar búsqueda y quitar foco"""
        if hasattr(self, 'search_var') and self.search_var:
            self.search_var.set("")
            self.on_search_change()
        if hasattr(self, 'search_entry') and self.search_entry:
            self.search_entry.master.focus()  # Quitar foco de la barra de búsqueda
    
    def toggle_favorites_filter(self):
        """Alternar entre mostrar todos los juegos y solo favoritos"""
        if hasattr(self, 'favorites_filter'):
            if self.favorites_filter == "all":
                self.set_favorites_filter("favorites")
            else:
                self.set_favorites_filter("all")
    
    def setup_styles(self):
        """Configurar estilos según el tema seleccionado"""
        style = ttk.Style()
        
        # Obtener colores del tema actual
        self.colors = self.themes.get(self.current_theme, self.themes['slate'])
        self.ui_font_family = tkFont.nametofont('TkDefaultFont').actual('family')
        
        # Actualizar el fondo de la ventana principal
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Configurar ttk styles
        style.theme_use('clam')
        style.configure('Dark.TFrame', background=self.colors['bg_dark'])
        style.configure('Sidebar.TFrame', background=self.colors['sidebar'])
        style.configure(
            'Dark.TLabel',
            background=self.colors['bg_dark'],
            foreground=self.colors['text'],
            font=(self.ui_font_family, 10),
        )
        style.configure(
            'Section.TLabel',
            background=self.colors['bg_dark'],
            foreground=self.colors['text_muted'],
            font=(self.ui_font_family, 9),
        )
        
        self.card_shadow_color = self.colors['bg_dark']
        style.configure(
            'Game.TFrame',
            background=self.colors['bg_light'],
            relief='flat',
            borderwidth=1,
        )
        style.configure(
            'GameHover.TFrame',
            background=self.colors['bg_light'],
            relief='solid',
            borderwidth=1,
        )
        
        button_text_color = '#ffffff' if self.current_theme == 'light' else self.colors['text']
        style.configure(
            'Accent.TButton',
            background=self.colors['accent'],
            foreground=button_text_color,
            borderwidth=0,
            focuscolor='none',
            padding=(14, 9),
            font=(self.ui_font_family, 10, 'bold'),
        )
        style.map(
            'Accent.TButton',
            background=[
                ('pressed', self.colors.get('accent_hover', self.colors['accent'])),
                ('active', self.colors.get('accent_hover', self.colors['accent'])),
            ],
        )
        style.configure(
            'GameTitle.TLabel',
            background=self.colors['bg_light'],
            foreground=self.colors['text_primary'],
            font=(self.ui_font_family, 11, 'bold'),
        )
        style.configure(
            'GameSubtitle.TLabel',
            background=self.colors['bg_light'],
            foreground=self.colors['text_secondary'],
            font=(self.ui_font_family, 9),
        )
        if hasattr(self, 'menubar'):
            self._apply_menu_colors()
    
    def load_translations(self):
        """Cargar todas las traducciones"""
        return {
            'es': {
                # Menús
                'file_menu': 'Archivo',
                'view_menu': 'Ver',
                'help_menu': 'Ayuda',
                'config_menu': 'Configuración',
                'about_menu': 'Acerca de',
                'exit_menu': 'Salir',
                'search_menu': 'Buscar',
                'toggle_favorites_menu': 'Alternar Favoritos',
                'refresh_list_menu': 'Actualizar Lista',
                
                # Ventana principal
                'window_title': 'Avilon',
                'add_game': 'Añadir Juego',
                'export_games': 'Exportar Juegos',
                'import_games': 'Importar Juegos',
                'export_game_dialog_title': 'Seleccionar Juegos para Exportar',
                'import_game_dialog_title': 'Importar Juegos',

                'export_button': 'Exportar Seleccionados',
                'import_button': 'Importar Juegos',
                'exported_successfully': 'Juegos exportados correctamente',
                'imported_successfully': 'Juegos importados correctamente',
                'export_failed': 'Error al exportar juegos',
                'import_failed': 'Error al importar juegos',
                'add_game_button': '+ Añadir Juego',
                'library': 'BIBLIOTECA',
                'games_count': 'juegos',
                'game_singular': 'juego',
                'no_games': 'No hay juegos en tu biblioteca.\nVe a "Archivo" → "Añadir Juego" para comenzar.',
                'no_favorites': 'No tienes ningún juego favorito.',
                'no_games_search': 'No se encontraron juegos que coincidan con la búsqueda',
                'no_recent_games': 'Los juegos que abras aparecerán aquí.',
                'search_placeholder': 'Buscar juegos... (favoritos siempre visibles)',
                
                # Formulario añadir juego
                'add_game_title': 'Añadir Nuevo Juego',
                'game_name': 'Nombre del juego:',
                'game_image': 'Imagen del juego:',
                'browse_image': 'Examinar imagen',
                'map_content': 'Ruta/URL del mapa:',
                'map_type_label': 'Tipo de mapa:',
                'map_type_image': 'Imagen',
                'map_type_web': 'Página web',
                'browse_map': 'Examinar',
                'save': 'Guardar',
                'cancel': 'Cancelar',
                'save_changes': 'Guardar cambios',
                
                # Mensajes
                'error': 'Error',
                'success': 'Éxito',
                'game_saved': 'Juego guardado correctamente',
                'fill_required_fields': 'Por favor, completa todos los campos requeridos',
                'invalid_image': 'Formato de imagen no válido',
                'invalid_url': 'URL no válida',
                'select_image': 'Seleccionar imagen',
                'select_map': 'Seleccionar mapa',
                'image_files': 'Archivos de imagen',
                'all_files': 'Todos los archivos',
                
                # Ventana acerca de
                'about_title': 'Acerca de Avilon',
                'about_description': 'Avilon es un programa diseñado y programado por una única persona, donde podrás gestionar los mapas de tus juegos favoritos',
                'close': 'Cerrar',
                
                # Configuración
                'config_title': 'Configuración',
                'language_label': 'Idioma:',
                'theme_label': 'Tema:',
                'spanish': 'Español',
                'english': 'English',
                'french': 'Français',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'Português',
                'dutch': 'Nederlands',
                'russian': 'Русский',
                'japanese': '日本語',
                'chinese': '中文',
                'theme_slate': 'Pizarra',
                'theme_dark': 'Oscuro',
                'theme_light': 'Claro',
                'theme_blue': 'Azul',
                'theme_green': 'Verde',
                'theme_cyberpunk': 'Cyberpunk',
                'theme_gaming_rgb': 'Gaming RGB',
                'theme_retro_arcade': 'Retro Arcade',
                'theme_midnight_gaming': 'Gaming Nocturno',
                'theme_esports': 'Esports',
                'apply': 'Aplicar',
                'config_saved': 'Configuración guardada correctamente',
                'config_section_language_desc': 'Selecciona el idioma de la interfaz',
                'config_section_theme_desc': 'Elige el tema visual de la aplicación',
                'config_section_startup_desc': 'Inicia Avilon automáticamente con el sistema',
                'startup_auto_start_label': 'Iniciar automáticamente con el sistema',
                
                # Botones de juego
                'view_map': 'Ver mapa',
                'edit': 'Editar',
                'delete': 'Eliminar',
                'delete_game': 'Borrar juego',
                'edit_game': 'Editar juego',
                'no_image': 'Sin imagen',
                'confirm_delete': '¿Estás seguro de que quieres eliminar este juego?',
                'confirm_title': 'Confirmar',
                'yes': 'Sí',
                'no': 'No',
                
                # Editar juego
                'edit_game_title': 'Editar Juego',
                
                # Títulos de ventana
                'map_window_title': 'Mapa',
                
                # Sistema de favoritos
                'all_games': 'Todos',
                'favorites': 'Favoritos',
                'recent': 'Recientes',
                'add_to_favorites': 'Añadir a favoritos',
                'remove_from_favorites': 'Quitar de favoritos',
                
                # Inicio automático
                'startup_label': 'Iniciar con el sistema:',
                'startup_enabled': 'Programa configurado para iniciar con el sistema',
                'startup_disabled': 'Programa removido del inicio automático',
                'startup_error': 'Error al configurar el inicio automático',
                
                # Guía de uso
                'how_to_use_menu': 'Cómo se usa',
                'tutorial_menu': 'Ver tutorial',
                'report_bug_menu': 'Reportar un error',
                'user_guide_title': 'Guía de Usuario - Cómo usar Avilon',
                'guide_tab_games': 'Juegos',
                'guide_tab_maps': 'Mapas', 
                'guide_tab_features': 'Características',
                'guide_tab_tips': 'Consejos',
                
                # Pestaña Juegos
                'guide_games_title': '🎮 Gestión de Juegos',
                'guide_games_add_title': '📝 Cómo agregar un juego:',
                'guide_games_add_content': '''1. Ve al menú "Archivo" → "Añadir Juego"
2. Escribe el nombre del juego
3. Escribe una descripción del juego (opcional)
4. Selecciona una imagen (obligatoria):
   • Formatos soportados: PNG, JPG, JPEG, BMP, GIF
   • Recomendado: 250x280 píxeles
5. Configura el mapa (ver pestaña "Mapas")
6. Haz clic en "Guardar"''',
                'guide_games_manage_title': '⚙️ Gestionar juegos existentes:',
                'guide_games_manage_content': '''• Hacer clic en ⭐ para marcar/desmarcar como favorito
• "Editar" para modificar los datos del juego
• "Eliminar" para borrar el juego de la biblioteca''',
                
                # Pestaña Mapas
                'guide_maps_title': '🗺️ Configuración de Mapas',
                'guide_maps_types_title': '📋 Tipos de mapas soportados:',
                'guide_maps_image_title': '🖼️ Mapas de Imagen:',
                'guide_maps_image_content': '''• Formatos: PNG, JPG, JPEG, BMP, GIF
• Funciones: Zoom, desplazamiento, pantalla completa
• Ideal para mapas estáticos del juego''',
                'guide_maps_web_title': '🌐 Mapas Web (iframe):',
                'guide_maps_web_content': '''• Cualquier URL válida (http:// o https://)
• Mapas interactivos online
• Wikis de juegos, guías web, etc.
• Se abre en ventana integrada''',
                
                # Pestaña Características
                'guide_features_title': '✨ Características Principales',
                'guide_features_search_title': '🔍 Sistema de Búsqueda:',
                'guide_features_search_content': '''• Buscar por nombre de juego
• Los favoritos siempre permanecen visibles
• Filtros: "Todos" y "Favoritos"''',
                'guide_features_themes_title': '🎨 Temas y Personalización:',
                'guide_features_themes_content': '''• 5 temas disponibles: Pizarra, Oscuro, Claro, Azul, Verde
• Idiomas múltiples soportados
• Configuración guardada automáticamente''',
                'guide_features_startup_title': '🚀 Inicio Automático:',
                'guide_features_startup_content': '''• Configurable desde Configuración
• Inicia con el sistema si está habilitado
• Fácil activación/desactivación''',
                
                # Pestaña Consejos
                'guide_tips_title': '💡 Consejos y Trucos',
                'guide_tips_organization_title': '📚 Organización:',
                'guide_tips_organization_content': '''• Usa nombres descriptivos para tus juegos
• Marca como favoritos los juegos que más uses
• Organiza las imágenes por categorías''',
                'guide_tips_images_title': '🖼️ Mejores Prácticas para Imágenes:',
                'guide_tips_images_content': '''• Usa imágenes con buena resolución
• Tamaño recomendado: 250x280 píxeles
• Evita imágenes muy pesadas (>5MB)''',
                'guide_tips_maps_title': '🗺️ Consejos para Mapas:',
                'guide_tips_maps_content': '''• Para mapas web, verifica que la URL sea accesible
• Los mapas de imagen grandes se pueden hacer zoom
• Usa mapas interactivos cuando sea posible''',
                
                # Pestaña Atajos de Teclado
                'guide_tab_shortcuts': 'Atajos de Teclado',
                'guide_shortcuts_title': '⌨️ Atajos de Teclado',
                'guide_shortcuts_subtitle': 'Acelera tu trabajo con estos atajos de teclado útiles',
                'guide_shortcuts_games_title': '🎮 Gestión de Juegos',
                'guide_shortcuts_games_content': '''• Ctrl + N - Añadir nuevo juego
• Ctrl + F - Buscar juegos
• Escape - Limpiar búsqueda
• F5 - Actualizar lista de juegos
• Ctrl + Shift + F - Alternar vista de favoritos''',
                'guide_shortcuts_navigation_title': '🧭 Navegación y Configuración',
                'guide_shortcuts_navigation_content': '''• F1 - Abrir guía de usuario
• Ctrl + Shift + P - Abrir configuración
• Ctrl + Q - Salir de la aplicación''',
                'guide_shortcuts_tips_title': '💡 Consejos para Atajos',
                'guide_shortcuts_tips_content': '''• Los atajos funcionan en cualquier parte de la aplicación
• Puedes usar tanto mayúsculas como minúsculas
• La tecla Escape siempre limpia la búsqueda actual
• F1 es tu tecla de ayuda rápida''',
                'guide_shortcuts_workflow_title': '⚡ Flujo de Trabajo Rápido',
                'guide_shortcuts_workflow_content': 'Los atajos de teclado pueden personalizarse en la ventana de Configuración. Abre la ventana de Configuración desde el menú o presiona Ctrl + Shift + P para cambiar los atajos según tus preferencias.',
                'guide_shortcuts_open_settings': 'Abrir Configuración',
                
                # Subtítulo de la guía
                'guide_subtitle': 'Todo lo que necesitas saber para usar Avilon',
                
                # Objetivos en la presentación del juego
                'objectives': 'Objetivos',
                'no_objectives': 'Sin objetivos',
                'new_objective': 'Nuevo objetivo',
                'write_objective': 'Escribe el objetivo:',
                'add_objective': 'Añadir objetivo',
                
                # Descripción y metadata del juego
                'game_description': 'Descripción (opcional):',
                'description': 'Descripción',
                'added_date': 'Fecha de adición',
                'play_time': 'Tiempo jugado',
                'days': 'días',
                'day': 'día',
                'hours': 'horas',
                'hour': 'hora',
                'minutes': 'minutos',
                'minute': 'minuto',
                'never_opened': 'Aún no abierto',
                
                # Splash Screen
                'splash_tagline': 'BIBLIOTECA DE JUEGOS  •  MAPAS  •  GUÍAS',
                'splash_subtitle': 'Gestor de Biblioteca de Mapas',
                'splash_version': 'versión 3.0',
                'splash_initializing': 'Iniciando...',
                'splash_init_components': '🔧 Inicializando componentes...',
                'splash_loading_config': '⚙️ Cargando configuración...',
                'splash_verifying_files': '📁 Verificando archivos...',
                'splash_setting_interface': '🎨 Configurando interfaz...',
                'splash_preparing_library': '🎮 Preparando biblioteca de juegos...',
                'splash_indexing_content': '🔍 Indexando contenido...',
                'splash_final_touches': '✨ Aplicando últimos toques...',
                'splash_ready': '🚀 ¡Listo para despegar!',
                
                # Atajos de teclado
                'keybinds_label': 'Atajos de teclado',
                'keybinds_desc': 'Personaliza los atajos de teclado',
                'command': 'Comando',
                'add_game_label': 'Añadir juego',
                'search_label': 'Buscar',
                'clear_search_label': 'Limpiar búsqueda',
                'refresh_label': 'Actualizar',
                'favorites_label': 'Favoritos',
                'reset': 'Restablecer predeterminados',
                'capture_keybind': 'Presiona la combinación de teclas...',
                'capture_cancel': '(Presiona ESC para cancelar)',
                'capture_button': '🎹 Capturar'
            },
            
            'en': {
                # Menus
                'file_menu': 'File',
                'view_menu': 'View',
                'help_menu': 'Help',
                'config_menu': 'Settings',
                'about_menu': 'About',
                'exit_menu': 'Exit',
                'search_menu': 'Search',
                'toggle_favorites_menu': 'Toggle Favorites',
                'refresh_list_menu': 'Refresh List',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': 'Add Game',
                'export_games': 'Export Games',
                'import_games': 'Import Games',
                'export_game_dialog_title': 'Select Games to Export',
                'import_game_dialog_title': 'Import Games',

                'export_button': 'Export Selected',
                'import_button': 'Import Games',
                'exported_successfully': 'Games exported successfully',
                'imported_successfully': 'Games imported successfully',
                'export_failed': 'Error exporting games',
                'import_failed': 'Error importing games',
                'add_game_button': '+ Add Game',
                'library': 'LIBRARY',
                'games_count': 'games',
                'game_singular': 'game',
                'no_games': 'No games in your library.\nGo to "File" → "Add Game" to get started.',
                'no_favorites': 'You don’t have any favorite games.',
                'no_games_search': 'No games found matching your search',
                'no_recent_games': 'Games you open will appear here.',
                'search_placeholder': 'Search games... (favorites always visible)',
                
                # Add game form
                'add_game_title': 'Add New Game',
                'game_name': 'Game name:',
                'game_image': 'Game image:',
                'browse_image': 'Browse image',
                'map_content': 'Map path/URL:',
                'map_type_label': 'Map type:',
                'map_type_image': 'Image',
                'map_type_web': 'Website',
                'browse_map': 'Browse',
                'save': 'Save',
                'cancel': 'Cancel',
                'save_changes': 'Save changes',
                
                # Messages
                'error': 'Error',
                'success': 'Success',
                'game_saved': 'Game saved successfully',
                'fill_required_fields': 'Please fill in all required fields',
                'invalid_image': 'Invalid image format',
                'invalid_url': 'Invalid URL',
                'select_image': 'Select image',
                'select_map': 'Select map',
                'image_files': 'Image files',
                'all_files': 'All files',
                
                # About window
                'about_title': 'About Avilon',
                'about_description': 'Avilon is a program designed and programmed by a single person, where you can manage maps for your favorite games',
                'close': 'Close',
                
                # Configuration
                'config_title': 'Settings',
                'language_label': 'Language:',
                'theme_label': 'Theme:',
                'spanish': 'Español',
                'english': 'English',
                'french': 'Français',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'Português',
                'dutch': 'Nederlands',
                'russian': 'Русский',
                'japanese': '日本語',
                'chinese': '中文',
                'theme_slate': 'Slate',
                'theme_dark': 'Dark',
                'theme_light': 'Light',
                'theme_blue': 'Blue',
                'theme_green': 'Green',
                'theme_cyberpunk': 'Cyberpunk',
                'theme_gaming_rgb': 'Gaming RGB',
                'theme_retro_arcade': 'Retro Arcade',
                'theme_midnight_gaming': 'Midnight Gaming',
                'theme_esports': 'Esports',
                'apply': 'Apply',
                'config_saved': 'Settings saved successfully',
                'config_section_language_desc': 'Select the interface language',
                'config_section_theme_desc': 'Choose the visual theme of the application',
                'config_section_startup_desc': 'Start Avilon automatically with the system',
                'startup_auto_start_label': 'Start automatically with the system',
                
                # Game buttons
                'view_map': 'View map',
                'view_guide': 'View guide',
                'edit': 'Edit',
                'delete': 'Delete',
                'delete_game': 'Delete game',
                'edit_game': 'Edit game',
                'no_image': 'No image',
                'confirm_delete': 'Are you sure you want to delete this game?',
                'confirm_title': 'Confirm',
                'yes': 'Yes',
                'no': 'No',
                
                # Edit game
                'edit_game_title': 'Edit Game',
                
                # Window titles
                'map_window_title': 'Map',
                
                # Favorites system
                'all_games': 'All',
                'favorites': 'Favorites',
                'recent': 'Recent',
                'add_to_favorites': 'Add to favorites',
                'remove_from_favorites': 'Remove from favorites',
                
                # Startup
                'startup_label': 'Start with system:',
                'startup_enabled': 'Program configured to start with the system',
                'startup_disabled': 'Program removed from automatic startup',
                'startup_error': 'Error configuring automatic startup',
                
                # User Guide
                'how_to_use_menu': 'How to Use',
                'tutorial_menu': 'View Tutorial',
                'report_bug_menu': 'Report an error',
                'user_guide_title': 'User Guide - How to use Avilon',
                'guide_tab_games': 'Games',
                'guide_tab_maps': 'Maps', 
                'guide_tab_features': 'Features',
                'guide_tab_tips': 'Tips',
                
                # Games tab
                'guide_games_title': '🎮 Game Management',
                'guide_games_add_title': '📝 How to add a game:',
                'guide_games_add_content': '''1. Go to "File" → "Add Game" menu
2. Enter the game name
3. Enter a game description (optional)
4. Select an image (required):
   • Supported formats: PNG, JPG, JPEG, BMP, GIF
   • Recommended: 250x280 pixels
5. Configure the map (see "Maps" tab)
6. Click "Save"''',
                'guide_games_manage_title': '⚙️ Managing existing games:',
                'guide_games_manage_content': '''• Click on ⭐ to mark/unmark as favorite
• "Edit" to modify game data
• "Delete" to remove the game from library''',
                
                # Maps tab
                'guide_maps_title': '🗺️ Map Configuration',
                'guide_maps_types_title': '📋 Supported map types:',
                'guide_maps_image_title': '🖼️ Image Maps:',
                'guide_maps_image_content': '''• Formats: PNG, JPG, JPEG, BMP, GIF
• Features: Zoom, pan, fullscreen
• Ideal for static game maps''',
                'guide_maps_web_title': '🌐 Web Maps (iframe):',
                'guide_maps_web_content': '''• Any valid URL (http:// or https://)
• Interactive online maps
• Game wikis, web guides, etc.
• Opens in integrated window''',
                
                # Features tab
                'guide_features_title': '✨ Main Features',
                'guide_features_search_title': '🔍 Search System:',
                'guide_features_search_content': '''• Search by game name
• Favorites always remain visible
• Filters: "All" and "Favorites"''',
                'guide_features_themes_title': '🎨 Themes and Customization:',
                'guide_features_themes_content': '''• 5 available themes: Slate, Dark, Light, Blue, Green
• Multiple language support
• Settings saved automatically''',
                'guide_features_startup_title': '🚀 Auto Start:',
                'guide_features_startup_content': '''• Configurable from Settings
• Starts with the system if enabled
• Easy activation/deactivation''',
                
                # Tips tab
                'guide_tips_title': '💡 Tips and Tricks',
                'guide_tips_organization_title': '📚 Organization:',
                'guide_tips_organization_content': '''• Use descriptive names for your games
• Mark frequently used games as favorites
• Organize images by categories''',
                'guide_tips_images_title': '🖼️ Best Practices for Images:',
                'guide_tips_images_content': '''• Use good resolution images
• Recommended size: 250x280 pixels
• Avoid very heavy images (>5MB)''',
                'guide_tips_maps_title': '🗺️ Map Tips:',
                'guide_tips_maps_content': '''• For web maps, verify the URL is accessible
• Large image maps can be zoomed
• Use interactive maps when possible''',
                
                # Keyboard Shortcuts tab
                'guide_tab_shortcuts': 'Keyboard Shortcuts',
                'guide_shortcuts_title': '⌨️ Keyboard Shortcuts',
                'guide_shortcuts_subtitle': 'Speed up your work with these useful keyboard shortcuts',
                'guide_shortcuts_games_title': '🎮 Game Management',
                'guide_shortcuts_games_content': '''• Ctrl + N - Add new game
• Ctrl + F - Search games
• Escape - Clear search
• F5 - Refresh game list
• Ctrl + Shift + F - Toggle favorites view''',
                'guide_shortcuts_navigation_title': '🧭 Navigation and Settings',
                'guide_shortcuts_navigation_content': '''• F1 - Open user guide
• Ctrl + Shift + P - Open settings
• Ctrl + Q - Exit application''',
                'guide_shortcuts_tips_title': '💡 Shortcut Tips',
                'guide_shortcuts_tips_content': '''• Shortcuts work anywhere in the application
• You can use both uppercase and lowercase
• Escape key always clears current search
• F1 is your quick help key''',
                'guide_shortcuts_workflow_title': '⚡ Quick Workflow',
                'guide_shortcuts_workflow_content': 'Keyboard shortcuts can be customized in the Settings window. Open the Settings window from the menu or press Ctrl + Shift + P to modify shortcuts according to your preferences.',
                'guide_shortcuts_open_settings': 'Open Settings',
                
                # Guide subtitle
                'guide_subtitle': 'Everything you need to know about using Avilon',
                
                # Objectives in game presentation
                'objectives': 'Objectives',
                'no_objectives': 'No objectives',
                'new_objective': 'New objective',
                'write_objective': 'Write the objective:',
                'add_objective': 'Add objective',
                
                # Game description and metadata
                'game_description': 'Description (optional):',
                'description': 'Description',
                'added_date': 'Added date',
                'play_time': 'Play time',
                'days': 'days',
                'day': 'day',
                'hours': 'hours',
                'hour': 'hour',
                'minutes': 'minutes',
                'minute': 'minute',
                'never_opened': 'Never opened',
                
                # Splash Screen
                'splash_tagline': 'GAME LIBRARY  •  MAPS  •  GUIDES',
                'splash_subtitle': 'Map Library Manager',
                'splash_version': 'version 3.0',
                'splash_initializing': 'Starting up...',
                'splash_init_components': '🔧 Initializing components...',
                'splash_loading_config': '⚙️ Loading configuration...',
                'splash_verifying_files': '📁 Verifying files...',
                'splash_setting_interface': '🎨 Setting up interface...',
                'splash_preparing_library': '🎮 Preparing game library...',
                'splash_indexing_content': '🔍 Indexing content...',
                'splash_final_touches': '✨ Applying final touches...',
                'splash_ready': '🚀 Ready to launch!',
                
                # Keyboard shortcuts
                'keybinds_label': 'Keyboard Shortcuts',
                'keybinds_desc': 'Customize your keyboard shortcuts',
                'command': 'Command',
                'add_game_label': 'Add game',
                'search_label': 'Search',
                'clear_search_label': 'Clear search',
                'refresh_label': 'Refresh',
                'favorites_label': 'Favorites',
                'reset': 'Reset to defaults',
                'capture_keybind': 'Press the key combination...',
                'capture_cancel': '(Press ESC to cancel)',
                'capture_button': '🎹 Capture'
            },
            
            'fr': {
                # Menus
                'file_menu': 'Fichier',
                'view_menu': 'Affichage',
                'help_menu': 'Aide',
                'config_menu': 'Paramètres',
                'about_menu': 'À propos',
                'exit_menu': 'Quitter',
                'search_menu': 'Rechercher',
                'toggle_favorites_menu': 'Basculer Favoris',
                'refresh_list_menu': 'Actualiser la Liste',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': 'Ajouter un jeu',
                'export_games': 'Exporter des jeux',
                'import_games': 'Importer des jeux',
                'export_game_dialog_title': 'Sélectionner les jeux à exporter',
                'import_game_dialog_title': 'Importer des jeux',

                'export_button': 'Exporter la sélection',
                'import_button': 'Importer des jeux',
                'exported_successfully': 'Jeux exportés avec succès',
                'imported_successfully': 'Jeux importés avec succès',
                'export_failed': 'Erreur lors de l\'export des jeux',
                'import_failed': 'Erreur lors de l\'import des jeux',
                'add_game_button': '+ Ajouter un jeu',
                'library': 'BIBLIOTHÈQUE',
                'games_count': 'jeux',
                'game_singular': 'jeu',
                'no_games': 'Aucun jeu dans votre bibliothèque.\nAllez dans "Fichier" → "Ajouter un jeu" pour commencer.',
                'no_favorites': 'Vous n’avez aucun jeu favori.',
                'no_games_search': 'Aucun jeu trouvé correspondant à votre recherche',
                'no_recent_games': 'Les jeux ouverts apparaîtront ici.',
                'search_placeholder': 'Rechercher des jeux... (favoris toujours visibles)',
                
                # Add game form
                'add_game_title': 'Ajouter un nouveau jeu',
                'game_name': 'Nom du jeu:',
                'game_image': 'Image du jeu:',
                'browse_image': 'Parcourir l\'image',
                'map_content': 'Chemin/URL de la carte:',
                'map_type_label': 'Type de carte:',
                'map_type_image': 'Image',
                'map_type_web': 'Site web',
                'browse_map': 'Parcourir',
                'save': 'Sauvegarder',
                'cancel': 'Annuler',
                'save_changes': 'Sauvegarder les modifications',
                
                # Messages
                'error': 'Erreur',
                'success': 'Succès',
                'game_saved': 'Jeu sauvegardé avec succès',
                'fill_required_fields': 'Veuillez remplir tous les champs requis',
                'invalid_image': 'Format d\'image invalide',
                'invalid_url': 'URL invalide',
                'select_image': 'Sélectionner une image',
                'select_map': 'Sélectionner une carte',
                'image_files': 'Fichiers image',
                'all_files': 'Tous les fichiers',
                
                # About window
                'about_title': 'À propos d\'Avilon',
                'about_description': 'Avilon est un programme conçu et programmé par une seule personne, où vous pouvez gérer les cartes de vos jeux préférés',
                'close': 'Fermer',
                
                # Configuration
                'config_title': 'Paramètres',
                'language_label': 'Langue:',
                'theme_label': 'Thème:',
                'spanish': 'Español',
                'english': 'English',
                'french': 'Français',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'Português',
                'dutch': 'Nederlands',
                'russian': 'Русский',
                'japanese': '日本語',
                'chinese': '中文',
                'theme_slate': 'Ardoise',
                'theme_dark': 'Sombre',
                'theme_light': 'Clair',
                'theme_blue': 'Bleu',
                'theme_green': 'Vert',
                'theme_cyberpunk': 'Cyberpunk',
                'theme_gaming_rgb': 'Gaming RGB',
                'theme_retro_arcade': 'Rétro Arcade',
                'theme_midnight_gaming': 'Gaming de Minuit',
                'theme_esports': 'Esports',
                'apply': 'Appliquer',
                'config_saved': 'Paramètres sauvegardés avec succès',
                
                # Game buttons
                'view_map': 'Voir la carte',
                'edit': 'Modifier',
                'delete': 'Supprimer',
                'delete_game': 'Supprimer le jeu',
                'edit_game': 'Modifier le jeu',
                'no_image': 'Aucune image',
                'confirm_delete': 'Êtes-vous sûr de vouloir supprimer ce jeu?',
                'confirm_title': 'Confirmer',
                'yes': 'Oui',
                'no': 'Non',
                
                # Edit game
                'edit_game_title': 'Modifier le jeu',
                
                # Window titles
                'map_window_title': 'Carte',
                
                # Favorites system
                'all_games': 'Tous',
                'favorites': 'Favoris',
                'recent': 'Récents',
                'add_to_favorites': 'Ajouter aux favoris',
                'remove_from_favorites': 'Retirer des favoris',
                
                # Startup
                'startup_label': 'Démarrer avec le système:',
                'startup_enabled': 'Programme configuré pour démarrer avec le système',
                'startup_disabled': 'Programme retiré du démarrage automatique',
                'startup_error': 'Erreur lors de la configuration du démarrage automatique',
                
                # Configuration sections
                'config_section_language_desc': 'Sélectionnez la langue de l\'interface',
                'config_section_theme_desc': 'Choisissez le thème visuel de l\'application',
                'config_section_startup_desc': 'Démarrez Avilon automatiquement avec le système',
                'startup_auto_start_label': 'Démarrer automatiquement avec le système',
                
                # User Guide
                'how_to_use_menu': 'Comment utiliser',
                'tutorial_menu': 'Voir le tutoriel',
                'report_bug_menu': 'Signaler une erreur',
                'user_guide_title': 'Guide Utilisateur - Comment utiliser Avilon',
                'guide_tab_games': 'Jeux',
                'guide_tab_maps': 'Cartes',
                'guide_tab_features': 'Fonctionnalités',
                'guide_tab_tips': 'Conseils',
                
                # Games tab
                'guide_games_title': '🎮 Gestion des Jeux',
                'guide_games_add_title': '📝 Comment ajouter un jeu:',
                'guide_games_add_content': '''1. Allez au menu "Fichier" → "Ajouter un jeu"
2. Écrivez le nom du jeu
3. Écrivez une description du jeu (facultatif)
4. Sélectionnez une image (obligatoire):
   • Formats supportés: PNG, JPG, JPEG, BMP, GIF
   • Recommandé: 250x280 pixels
5. Configurez la carte (voir onglet "Cartes")
6. Cliquez sur "Enregistrer"''',
                'guide_games_manage_title': '⚙️ Gérer les jeux existants:',
                'guide_games_manage_content': '''• Cliquez sur ⭐ pour marquer/démarquer comme favori
• "Modifier" pour modifier les données du jeu
• "Supprimer" pour supprimer le jeu de la bibliothèque''',
                
                # Maps tab
                'guide_maps_title': '🗺️ Configuration des Cartes',
                'guide_maps_types_title': '📋 Types de cartes supportés:',
                'guide_maps_image_title': '🖼️ Cartes Image:',
                'guide_maps_image_content': '''• Formats: PNG, JPG, JPEG, BMP, GIF
• Fonctionnalités: Zoom, panoramique, plein écran
• Idéal pour les cartes de jeu statiques''',
                'guide_maps_web_title': '🌐 Cartes Web (iframe):',
                'guide_maps_web_content': '''• N\'importe quelle URL valide (http:// ou https://)
• Cartes interactives en ligne
• Wikis de jeu, guides web, etc.
• S\'ouvre dans une fenêtre intégrée''',
                
                # Features tab
                'guide_features_title': '✨ Fonctionnalités Principales',
                'guide_features_search_title': '🔍 Système de Recherche:',
                'guide_features_search_content': '''• Rechercher par nom de jeu
• Les favoris restent toujours visibles
• Filtres: "Tous" et "Favoris"''',
                'guide_features_themes_title': '🎨 Thèmes et Personnalisation:',
                'guide_features_themes_content': '''• 5 thèmes disponibles: Ardoise, Sombre, Clair, Bleu, Vert
• Support de plusieurs langues
• Paramètres enregistrés automatiquement''',
                'guide_features_startup_title': '🚀 Démarrage Automatique:',
                'guide_features_startup_content': '''• Configurable depuis les Paramètres
• Démarre avec le système si activé
• Activation/désactivation facile''',
                
                # Tips tab
                'guide_tips_title': '💡 Conseils et Astuces',
                'guide_tips_organization_title': '📚 Organisation:',
                'guide_tips_organization_content': '''• Utilisez des noms descriptifs pour vos jeux
• Marquez comme favoris les jeux que vous utilisez souvent
• Organisez les images par catégories''',
                'guide_tips_images_title': '🖼️ Meilleures Pratiques pour les Images:',
                'guide_tips_images_content': '''• Utilisez des images de bonne qualité
• Taille recommandée: 250x280 pixels
• Évitez les images très lourdes (>5MB)''',
                'guide_tips_maps_title': '🗺️ Conseils pour les Cartes:',
                'guide_tips_maps_content': '''• Pour les cartes web, vérifiez que l\'URL est accessible
• Les grandes cartes images peuvent être zoomées
• Utilisez des cartes interactives si possible''',
                
                # Keyboard Shortcuts tab - Already exists below
                # Pestaña Atajos de Teclado
                'guide_tab_shortcuts': 'Raccourcis Clavier',
                'guide_shortcuts_title': '⌨️ Raccourcis Clavier',
                'guide_shortcuts_subtitle': 'Accélérez votre travail avec ces raccourcis clavier utiles',
                'guide_shortcuts_games_title': '🎮 Gestion des Jeux',
                'guide_shortcuts_games_content': '''• Ctrl + N - Ajouter un nouveau jeu
• Ctrl + F - Rechercher des jeux
• Échap - Effacer la recherche
• F5 - Actualiser la liste des jeux
• Ctrl + Shift + F - Basculer l'affichage des favoris''',
                'guide_shortcuts_navigation_title': '🧭 Navigation et Paramètres',
                'guide_shortcuts_navigation_content': '''• F1 - Ouvrir le guide utilisateur
• Ctrl + Shift + P - Ouvrir les paramètres
• Ctrl + Q - Quitter l'application''',
                'guide_shortcuts_tips_title': '💡 Conseils pour les Raccourcis',
                'guide_shortcuts_tips_content': '''• Les raccourcis fonctionnent partout dans l'application
• Vous pouvez utiliser majuscules et minuscules
• La touche Échap efface toujours la recherche actuelle
• F1 est votre touche d'aide rapide''',
                'guide_shortcuts_workflow_title': '⚡ Flux de Travail Rapide',
                'guide_shortcuts_workflow_content': 'Les raccourcis clavier peuvent être personnalisés dans la fenêtre Paramètres. Ouvrez la fenêtre Paramètres depuis le menu ou appuyez sur Ctrl + Shift + P pour modifier les raccourcis selon vos préférences.',
                'guide_shortcuts_open_settings': 'Ouvrir Paramètres',
                
                # Guide subtitle
                'guide_subtitle': 'Tout ce que vous devez savoir pour utiliser Avilon',
                
                # Objectifs dans la présentation du jeu
                'objectives': 'Objectifs',
                'no_objectives': 'Aucun objectif',
                'new_objective': 'Nouvel objectif',
                'write_objective': 'Écrivez l\'objectif:',
                'add_objective': 'Ajouter un objectif',
                
                # Description et métadonnées du jeu
                'game_description': 'Description (optionnel):',
                'description': 'Description',
                'added_date': 'Date d\'ajout',
                'play_time': 'Temps de jeu',
                'days': 'jours',
                'day': 'jour',
                'hours': 'heures',
                'hour': 'heure',
                'minutes': 'minutes',
                'minute': 'minute',
                'never_opened': 'Jamais ouvert',
                
                # Splash Screen
                'splash_tagline': 'BIBLIOTHÈQUE DE JEUX  •  CARTES  •  GUIDES',
                'splash_subtitle': 'Gestionnaire de Bibliothèque de Cartes',
                'splash_version': 'version 3.0',
                'splash_initializing': 'Démarrage...',
                'splash_init_components': '🔧 Initialisation des composants...',
                'splash_loading_config': '⚙️ Chargement de la configuration...',
                'splash_verifying_files': '📁 Vérification des fichiers...',
                'splash_setting_interface': '🎨 Configuration de l\'interface...',
                'splash_preparing_library': '🎮 Préparation de la bibliothèque de jeux...',
                'splash_indexing_content': '🔍 Indexation du contenu...',
                'splash_final_touches': '✨ Application des dernières touches...',
                'splash_ready': '🚀 Prêt à lancer!',
                
                # Raccourcis clavier
                'keybinds_label': 'Raccourcis clavier',
                'keybinds_desc': 'Personnalisez vos raccourcis clavier',
                'command': 'Commande',
                'add_game_label': 'Ajouter un jeu',
                'search_label': 'Rechercher',
                'clear_search_label': 'Effacer la recherche',
                'refresh_label': 'Actualiser',
                'favorites_label': 'Favoris',
                'reset': 'Réinitialiser par défaut',
                'capture_keybind': 'Appuyez sur la combinaison de touches...',
                'capture_cancel': '(Appuyez sur ESC pour annuler)',
                'capture_button': '🎹 Capturer'
            },
            
            'de': {
                # Menus
                'file_menu': 'Datei',
                'view_menu': 'Ansicht',
                'help_menu': 'Hilfe',
                'config_menu': 'Einstellungen',
                'about_menu': 'Über',
                'exit_menu': 'Beenden',
                'search_menu': 'Suchen',
                'toggle_favorites_menu': 'Favoriten umschalten',
                'refresh_list_menu': 'Liste aktualisieren',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': 'Spiel hinzufügen',
                'export_games': 'Spiele exportieren',
                'import_games': 'Spiele importieren',
                'export_game_dialog_title': 'Spiele zum Exportieren auswählen',
                'import_game_dialog_title': 'Spiele importieren',

                'export_button': 'Auswahl exportieren',
                'import_button': 'Spiele importieren',
                'exported_successfully': 'Spiele erfolgreich exportiert',
                'imported_successfully': 'Spiele erfolgreich importiert',
                'export_failed': 'Fehler beim Exportieren von Spielen',
                'import_failed': 'Fehler beim Importieren von Spielen',
                'add_game_button': '+ Spiel hinzufügen',
                'library': 'BIBLIOTHEK',
                'games_count': 'Spiele',
                'game_singular': 'Spiel',
                'no_games': 'Keine Spiele in Ihrer Bibliothek.\nGehen Sie zu "Datei" → "Spiel hinzufügen", um zu beginnen.',
                'no_favorites': 'Du hast keine Lieblingsspiele.',
                'no_games_search': 'Keine Spiele gefunden, die Ihrer Suche entsprechen',
                'no_recent_games': 'Geöffnete Spiele erscheinen hier.',
                'search_placeholder': 'Spiele suchen... (Favoriten immer sichtbar)',
                
                # Add game form
                'add_game_title': 'Neues Spiel hinzufügen',
                'game_name': 'Spielname:',
                'game_image': 'Spielbild:',
                'browse_image': 'Bild durchsuchen',
                'map_content': 'Karten-Pfad/URL:',
                'map_type_label': 'Kartentyp:',
                'map_type_image': 'Bild',
                'map_type_web': 'Webseite',
                'browse_map': 'Durchsuchen',
                'save': 'Speichern',
                'cancel': 'Abbrechen',
                'save_changes': 'Änderungen speichern',
                
                # Messages
                'error': 'Fehler',
                'success': 'Erfolg',
                'game_saved': 'Spiel erfolgreich gespeichert',
                'fill_required_fields': 'Bitte füllen Sie alle erforderlichen Felder aus',
                'invalid_image': 'Ungültiges Bildformat',
                'invalid_url': 'Ungültige URL',
                'select_image': 'Bild auswählen',
                'select_map': 'Karte auswählen',
                'image_files': 'Bilddateien',
                'all_files': 'Alle Dateien',
                
                # About window
                'about_title': 'Über Avilon',
                'about_description': 'Avilon ist ein Programm, das von einer einzigen Person entworfen und programmiert wurde, mit dem Sie Karten für Ihre Lieblingsspiele verwalten können',
                'close': 'Schließen',
                
                # Configuration
                'config_title': 'Einstellungen',
                'language_label': 'Sprache:',
                'theme_label': 'Design:',
                'spanish': 'Español',
                'english': 'English',
                'french': 'Français',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'Português',
                'dutch': 'Nederlands',
                'russian': 'Русский',
                'japanese': '日本語',
                'chinese': '中文',
                'theme_slate': 'Schiefer',
                'theme_dark': 'Dunkel',
                'theme_light': 'Hell',
                'theme_blue': 'Blau',
                'theme_green': 'Grün',
                'theme_cyberpunk': 'Cyberpunk',
                'theme_gaming_rgb': 'Gaming RGB',
                'theme_retro_arcade': 'Retro Arcade',
                'theme_midnight_gaming': 'Mitternacht Gaming',
                'theme_esports': 'Esports',
                'apply': 'Anwenden',
                'config_saved': 'Einstellungen erfolgreich gespeichert',
                
                # Game buttons
                'view_map': 'Karte anzeigen',
                'edit': 'Bearbeiten',
                'delete': 'Löschen',
                'delete_game': 'Spiel löschen',
                'edit_game': 'Spiel bearbeiten',
                'no_image': 'Kein Bild',
                'confirm_delete': 'Sind Sie sicher, dass Sie dieses Spiel löschen möchten?',
                'confirm_title': 'Bestätigen',
                'yes': 'Ja',
                'no': 'Nein',
                
                # Edit game
                'edit_game_title': 'Spiel bearbeiten',
                
                # Window titles
                'map_window_title': 'Karte',
                
                # Favorites system
                'all_games': 'Alle',
                'favorites': 'Favoriten',
                'recent': 'Zuletzt',
                'add_to_favorites': 'Zu Favoriten hinzufügen',
                'remove_from_favorites': 'Aus Favoriten entfernen',
                
                # Startup
                'startup_label': 'Mit dem System starten:',
                'startup_enabled': 'Programm für den Systemstart konfiguriert',
                'startup_disabled': 'Programm aus automatischem Start entfernt',
                'startup_error': 'Fehler beim Konfigurieren des automatischen Starts',
                
                # Configuration sections
                'config_section_language_desc': 'Wählen Sie die Schnittstelle Sprache',
                'config_section_theme_desc': 'Wählen Sie das visuelle Design der Anwendung',
                'config_section_startup_desc': 'Starten Sie Avilon automatisch mit dem System',
                'startup_auto_start_label': 'Automatisch mit dem System starten',
                
                # User Guide
                'how_to_use_menu': 'Gebrauchsanleitung',
                'tutorial_menu': 'Tutorial anzeigen',
                'report_bug_menu': 'Fehler melden',
                'user_guide_title': 'Benutzerhandbuch - Wie man Avilon verwendet',
                'guide_tab_games': 'Spiele',
                'guide_tab_maps': 'Karten',
                'guide_tab_features': 'Funktionen',
                'guide_tab_tips': 'Tipps',
                
                # Games tab
                'guide_games_title': '🎮 Spielverwaltung',
                'guide_games_add_title': '📝 Wie man ein Spiel hinzufügt:',
                'guide_games_add_content': '''1. Gehen Sie zum Menü "Datei" → "Spiel hinzufügen"
2. Geben Sie den Spielnamen ein
3. Geben Sie eine Spielbeschreibung ein (optional)
4. Wählen Sie ein Bild (erforderlich):
   • Unterstützte Formate: PNG, JPG, JPEG, BMP, GIF
   • Empfohlen: 250x280 Pixel
5. Konfigurieren Sie die Karte (siehe Reiter "Karten")
6. Klicken Sie auf "Speichern"''',
                'guide_games_manage_title': '⚙️ Vorhandene Spiele verwalten:',
                'guide_games_manage_content': '''• Klicken Sie auf ⭐, um als Favorit zu markieren/aufzuheben
• "Bearbeiten", um Spieldaten zu ändern
• "Löschen", um das Spiel aus der Bibliothek zu entfernen''',
                
                # Maps tab
                'guide_maps_title': '🗺️ Kartenkonfiguration',
                'guide_maps_types_title': '📋 Unterstützte Kartentypen:',
                'guide_maps_image_title': '🖼️ Bildkarten:',
                'guide_maps_image_content': '''• Formate: PNG, JPG, JPEG, BMP, GIF
• Funktionen: Zoom, Schwenken, Vollbildmodus
• Ideal für statische Spielkarten''',
                'guide_maps_web_title': '🌐 Webbkarten (iframe):',
                'guide_maps_web_content': '''• Jede gültige URL (http:// oder https://)
• Interaktive Online-Karten
• Spiel-Wikis, Web-Handbücher, etc.
• Öffnet sich in integriertem Fenster''',
                
                # Features tab
                'guide_features_title': '✨ Hauptfunktionen',
                'guide_features_search_title': '🔍 Suchsystem:',
                'guide_features_search_content': '''• Nach Spielname suchen
• Favoriten bleiben immer sichtbar
• Filter: "Alle" und "Favoriten"''',
                'guide_features_themes_title': '🎨 Themen und Anpassung:',
                'guide_features_themes_content': '''• 5 verfügbare Themen: Schiefer, Dunkel, Hell, Blau, Grün
• Unterstützung mehrerer Sprachen
• Einstellungen werden automatisch gespeichert''',
                'guide_features_startup_title': '🚀 Automatischer Start:',
                'guide_features_startup_content': '''• Konfigurierbar aus den Einstellungen
• Startet mit dem System, wenn aktiviert
• Einfache Aktivierung/Deaktivierung''',
                
                # Tips tab
                'guide_tips_title': '💡 Tipps und Tricks',
                'guide_tips_organization_title': '📚 Organisation:',
                'guide_tips_organization_content': '''• Verwenden Sie beschreibende Namen für Ihre Spiele
• Markieren Sie häufig verwendete Spiele als Favoriten
• Organisieren Sie Bilder nach Kategorien''',
                'guide_tips_images_title': '🖼️ Best Practices für Bilder:',
                'guide_tips_images_content': '''• Verwenden Sie Bilder in guter Qualität
• Empfohlene Größe: 250x280 Pixel
• Vermeiden Sie sehr große Bilder (>5MB)''',
                'guide_tips_maps_title': '🗺️ Kartentipps:',
                'guide_tips_maps_content': '''• Überprüfen Sie bei Webkarten, ob die URL erreichbar ist
• Große Bildkarten können vergrößert werden
• Verwenden Sie interaktive Karten wenn möglich''',
                
                # Keyboard Shortcuts tab - Already exists below
                # Pestaña Atajos de Teclado
                'guide_tab_shortcuts': 'Tastenkürzel',
                'guide_shortcuts_title': '⌨️ Tastenkürzel',
                'guide_shortcuts_subtitle': 'Beschleunigen Sie Ihre Arbeit mit diesen nützlichen Tastenkürzeln',
                'guide_shortcuts_games_title': '🎮 Spielverwaltung',
                'guide_shortcuts_games_content': '''• Strg + N - Neues Spiel hinzufügen
• Strg + F - Spiele suchen
• Escape - Suche löschen
• F5 - Spielliste aktualisieren
• Strg + Shift + F - Favoritenansicht umschalten''',
                'guide_shortcuts_navigation_title': '🧭 Navigation und Einstellungen',
                'guide_shortcuts_navigation_content': '''• F1 - Benutzerhandbuch öffnen
• Strg + Shift + P - Einstellungen öffnen
• Strg + Q - Anwendung beenden''',
                'guide_shortcuts_tips_title': '💡 Tipps für Tastenkürzel',
                'guide_shortcuts_tips_content': '''• Tastenkürzel funktionieren überall in der Anwendung
• Sie können Groß- und Kleinbuchstaben verwenden
• Die Escape-Taste löscht immer die aktuelle Suche
• F1 ist Ihre schnelle Hilfe-Taste''',
                'guide_shortcuts_workflow_title': '⚡ Schneller Arbeitsablauf',
                'guide_shortcuts_workflow_content': 'Tastenkombinationen können im Einstellungsfenster angepasst werden. Öffnen Sie das Einstellungsfenster über das Menü oder drücken Sie Strg + Umschalt + P, um die Tastenkombinationen nach Ihren Vorlieben zu ändern.',
                'guide_shortcuts_open_settings': 'Einstellungen öffnen',
                
                # Guide subtitle
                'guide_subtitle': 'Alles, was Sie über die Verwendung von Avilon wissen müssen',
                
                # Ziele in der Spielpräsentation
                'objectives': 'Ziele',
                'no_objectives': 'Keine Ziele',
                'new_objective': 'Neues Ziel',
                'write_objective': 'Schreiben Sie das Ziel:',
                'add_objective': 'Ziel hinzufügen',
                
                # Spielbeschreibung und Metadaten
                'game_description': 'Beschreibung (optional):',
                'description': 'Beschreibung',
                'added_date': 'Hinzugefügt am',
                'play_time': 'Spielzeit',
                'days': 'Tage',
                'day': 'Tag',
                'hours': 'Stunden',
                'hour': 'Stunde',
                'minutes': 'Minuten',
                'minute': 'Minute',
                'never_opened': 'Noch nie geöffnet',
                
                # Splash Screen
                'splash_tagline': 'SPIELEBIBLIOTHEK  •  KARTEN  •  GUIDES',
                'splash_subtitle': 'Kartenbibliotheks-Manager',
                'splash_version': 'Version 3.0',
                'splash_initializing': 'Starten...',
                'splash_init_components': '🔧 Komponenten werden initialisiert...',
                'splash_loading_config': '⚙️ Konfiguration wird geladen...',
                'splash_verifying_files': '📁 Dateien werden überprüft...',
                'splash_setting_interface': '🎨 Schnittstelle wird konfiguriert...',
                'splash_preparing_library': '🎮 Spielbibliothek wird vorbereitet...',
                'splash_indexing_content': '🔍 Inhalte werden indiziert...',
                'splash_final_touches': '✨ Letzte Anpassungen werden vorgenommen...',
                'splash_ready': '🚀 Bereit zum Starten!',
                
                # Tastenkombinationen
                'keybinds_label': 'Tastenkombinationen',
                'keybinds_desc': 'Passen Sie Ihre Tastenkombinationen an',
                'command': 'Befehl',
                'add_game_label': 'Spiel hinzufügen',
                'search_label': 'Suchen',
                'clear_search_label': 'Suche löschen',
                'refresh_label': 'Aktualisieren',
                'favorites_label': 'Favoriten',
                'reset': 'Auf Standard zurücksetzen',
                'capture_keybind': 'Drücken Sie die Tastenkombination...',
                'capture_cancel': '(Drücken Sie ESC zum Abbrechen)',
                'capture_button': '🎹 Erfassen'
            },
            
            'it': {
                # Menus
                'file_menu': 'File',
                'view_menu': 'Visualizza',
                'help_menu': 'Aiuto',
                'config_menu': 'Impostazioni',
                'about_menu': 'Informazioni',
                'exit_menu': 'Esci',
                'search_menu': 'Cerca',
                'toggle_favorites_menu': 'Alterna Preferiti',
                'refresh_list_menu': 'Aggiorna Elenco',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': 'Aggiungi gioco',
                'export_games': 'Esporta giochi',
                'import_games': 'Importa giochi',
                'export_game_dialog_title': 'Seleziona giochi da esportare',
                'import_game_dialog_title': 'Importa giochi',

                'export_button': 'Esporta selezionati',
                'import_button': 'Importa giochi',
                'exported_successfully': 'Giochi esportati con successo',
                'imported_successfully': 'Giochi importati con successo',
                'export_failed': 'Errore durante l\'esportazione dei giochi',
                'import_failed': 'Errore durante l\'importazione dei giochi',
                'add_game_button': '+ Aggiungi gioco',
                'library': 'LIBRERIA',
                'games_count': 'giochi',
                'game_singular': 'gioco',
                'no_games': 'Nessun gioco nella tua libreria.\nVai su "File" → "Aggiungi gioco" per iniziare.',
                'no_favorites': 'Non hai giochi preferiti.',
                'no_games_search': 'Nessun gioco trovato corrispondente alla tua ricerca',
                'no_recent_games': 'I giochi aperti appariranno qui.',
                'search_placeholder': 'Cerca giochi... (preferiti sempre visibili)',
                
                # Add game form
                'add_game_title': 'Aggiungi nuovo gioco',
                'game_name': 'Nome del gioco:',
                'game_image': 'Immagine del gioco:',
                'browse_image': 'Sfoglia immagine',
                'map_content': 'Percorso/URL della mappa:',
                'map_type_label': 'Tipo di mappa:',
                'map_type_image': 'Immagine',
                'map_type_web': 'Sito web',
                'browse_map': 'Sfoglia',
                'save': 'Salva',
                'cancel': 'Annulla',
                'save_changes': 'Salva modifiche',
                
                # Messages
                'error': 'Errore',
                'success': 'Successo',
                'game_saved': 'Gioco salvato con successo',
                'fill_required_fields': 'Si prega di compilare tutti i campi obbligatori',
                'invalid_image': 'Formato immagine non valido',
                'invalid_url': 'URL non valido',
                'select_image': 'Seleziona immagine',
                'select_map': 'Seleziona mappa',
                'image_files': 'File immagine',
                'all_files': 'Tutti i file',
                
                # About window
                'about_title': 'Informazioni su Avilon',
                'about_description': 'Avilon è un programma progettato e programmato da una singola persona, dove puoi gestire le mappe dei tuoi giochi preferiti',
                'close': 'Chiudi',
                
                # Configuration
                'config_title': 'Impostazioni',
                'language_label': 'Lingua:',
                'theme_label': 'Tema:',
                'spanish': 'Español',
                'english': 'English',
                'french': 'Français',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'Português',
                'dutch': 'Nederlands',
                'russian': 'Русский',
                'japanese': '日本語',
                'chinese': '中文',
                'theme_slate': 'Lavagna',
                'theme_dark': 'Scuro',
                'theme_light': 'Chiaro',
                'theme_blue': 'Blu',
                'theme_green': 'Verde',
                'theme_cyberpunk': 'Cyberpunk',
                'theme_gaming_rgb': 'Gaming RGB',
                'theme_retro_arcade': 'Retro Arcade',
                'theme_midnight_gaming': 'Gaming Notturno',
                'theme_esports': 'Esports',
                'apply': 'Applica',
                'config_saved': 'Impostazioni salvate con successo',
                
                # Game buttons
                'view_map': 'Visualizza mappa',
                'edit': 'Modifica',
                'delete': 'Elimina',
                'delete_game': 'Elimina gioco',
                'edit_game': 'Modifica gioco',
                'no_image': 'Nessuna immagine',
                'confirm_delete': 'Sei sicuro di voler eliminare questo gioco?',
                'confirm_title': 'Conferma',
                'yes': 'Sì',
                'no': 'No',
                
                # Edit game
                'edit_game_title': 'Modifica gioco',
                
                # Window titles
                'map_window_title': 'Mappa',
                
                # Favorites system
                'all_games': 'Tutti',
                'favorites': 'Preferiti',
                'recent': 'Recenti',
                'add_to_favorites': 'Aggiungi ai preferiti',
                'remove_from_favorites': 'Rimuovi dai preferiti',
                
                # Startup
                'startup_label': 'Avvia con il sistema:',
                'startup_enabled': 'Programma configurato per l’avvio con il sistema',
                'startup_disabled': 'Programma rimosso dall\'avvio automatico',
                'startup_error': 'Errore durante la configurazione dell\'avvio automatico',
                
                # Configuration sections
                'config_section_language_desc': 'Seleziona la lingua dell\'interfaccia',
                'config_section_theme_desc': 'Scegli il tema visivo dell\'applicazione',
                'config_section_startup_desc': 'Avvia Avilon automaticamente con il sistema',
                'startup_auto_start_label': 'Avvia automaticamente con il sistema',
                
                # User Guide
                'how_to_use_menu': 'Come usare',
                'tutorial_menu': 'Mostra tutorial',
                'report_bug_menu': 'Segnala un errore',
                'user_guide_title': 'Guida Utente - Come usare Avilon',
                'guide_tab_games': 'Giochi',
                'guide_tab_maps': 'Mappe',
                'guide_tab_features': 'Caratteristiche',
                'guide_tab_tips': 'Suggerimenti',
                
                # Games tab
                'guide_games_title': '🎮 Gestione Giochi',
                'guide_games_add_title': '📝 Come aggiungere un gioco:',
                'guide_games_add_content': '''1. Vai al menu "File" → "Aggiungi gioco"
2. Scrivi il nome del gioco
3. Scrivi una descrizione del gioco (facoltativo)
4. Seleziona un\'immagine (obbligatoria):
   • Formati supportati: PNG, JPG, JPEG, BMP, GIF
   • Consigliato: 250x280 pixel
5. Configura la mappa (vedi tab "Mappe")
6. Fai clic su "Salva"''',
                'guide_games_manage_title': '⚙️ Gestisci giochi esistenti:',
                'guide_games_manage_content': '''• Fai clic su ⭐ per contrassegnare/deselezionare come preferito
• "Modifica" per modificare i dati del gioco
• "Elimina" per rimuovere il gioco dalla libreria''',
                
                # Maps tab
                'guide_maps_title': '🗺️ Configurazione Mappe',
                'guide_maps_types_title': '📋 Tipi di mappe supportate:',
                'guide_maps_image_title': '🖼️ Mappe Immagine:',
                'guide_maps_image_content': '''• Formati: PNG, JPG, JPEG, BMP, GIF
• Funzioni: Zoom, panoramica, schermo intero
• Ideale per mappe statiche del gioco''',
                'guide_maps_web_title': '🌐 Mappe Web (iframe):',
                'guide_maps_web_content': '''• Qualsiasi URL valido (http:// o https://)
• Mappe interattive online
• Wiki di giochi, guide web, ecc.
• Si apre in finestra integrata''',
                
                # Features tab
                'guide_features_title': '✨ Caratteristiche Principali',
                'guide_features_search_title': '🔍 Sistema di Ricerca:',
                'guide_features_search_content': '''• Cerca per nome del gioco
• I preferiti rimangono sempre visibili
• Filtri: "Tutti" e "Preferiti"''',
                'guide_features_themes_title': '🎨 Temi e Personalizzazione:',
                'guide_features_themes_content': '''• 5 temi disponibili: Lavagna, Scuro, Chiaro, Blu, Verde
• Supporto per più lingue
• Impostazioni salvate automaticamente''',
                'guide_features_startup_title': '🚀 Avvio Automatico:',
                'guide_features_startup_content': '''• Configurabile dalle Impostazioni
• Si avvia con il sistema se abilitato
• Facile attivazione/disattivazione''',
                
                # Tips tab
                'guide_tips_title': '💡 Suggerimenti e Trucchi',
                'guide_tips_organization_title': '📚 Organizzazione:',
                'guide_tips_organization_content': '''• Usa nomi descrittivi per i tuoi giochi
• Contrassegna come preferiti i giochi più usati
• Organizza le immagini per categorie''',
                'guide_tips_images_title': '🖼️ Best Practice per Immagini:',
                'guide_tips_images_content': '''• Usa immagini ad alta risoluzione
• Dimensione consigliata: 250x280 pixel
• Evita immagini molto pesanti (>5MB)''',
                'guide_tips_maps_title': '🗺️ Suggerimenti per Mappe:',
                'guide_tips_maps_content': '''• Per mappe web, verifica che l\'URL sia accessibile
• Le mappe immagine grandi possono essere ingrandite
• Usa mappe interattive quando possibile''',
                
                # Keyboard Shortcuts tab
                'guide_tab_shortcuts': 'Scorciatoie da Tastiera',
                'guide_shortcuts_title': '⌨️ Scorciatoie da Tastiera',
                'guide_shortcuts_subtitle': 'Accelera il tuo lavoro con questi utili scorciatoi da tastiera',
                'guide_shortcuts_games_title': '🎮 Gestione Giochi',
                'guide_shortcuts_games_content': '''• Ctrl + N - Aggiungi nuovo gioco
• Ctrl + F - Cerca giochi
• Escape - Cancella ricerca
• F5 - Aggiorna lista dei giochi
• Ctrl + Shift + F - Attiva/disattiva visualizzazione preferiti''',
                'guide_shortcuts_navigation_title': '🧭 Navigazione e Impostazioni',
                'guide_shortcuts_navigation_content': '''• F1 - Apri guida utente
• Ctrl + Shift + P - Apri impostazioni
• Ctrl + Q - Esci dall\'applicazione''',
                'guide_shortcuts_tips_title': '💡 Suggerimenti per Scorciatoi',
                'guide_shortcuts_tips_content': '''• Gli scorciatoi funzionano ovunque nell\'applicazione
• Puoi usare maiuscole e minuscole
• Il tasto Escape cancella sempre la ricerca corrente
• F1 è il tuo tasto di aiuto rapido''',
                'guide_shortcuts_workflow_title': '⚡ Flusso di Lavoro Veloce',
                'guide_shortcuts_workflow_content': 'I tasti di scelta rapida possono essere personalizzati nella finestra Impostazioni. Apri la finestra Impostazioni dal menu o premi Ctrl + Maiusc + P per modificare i tasti di scelta rapida secondo le tue preferenze.',
                'guide_shortcuts_open_settings': 'Apri Impostazioni',
                
                # Guide subtitle
                'guide_subtitle': 'Tutto quello che devi sapere per usare Avilon',
                
                # Obiettivi nella presentazione del gioco
                'objectives': 'Obiettivi',
                'no_objectives': 'Nessun obiettivo',
                'new_objective': 'Nuovo obiettivo',
                'write_objective': 'Scrivi l\'obiettivo:',
                'add_objective': 'Aggiungi obiettivo',
                
                # Descrizione del gioco e metadati
                'game_description': 'Descrizione (opzionale):',
                'description': 'Descrizione',
                'added_date': 'Data di aggiunta',
                'play_time': 'Tempo di gioco',
                'days': 'giorni',
                'day': 'giorno',
                'hours': 'ore',
                'hour': 'ora',
                'minutes': 'minuti',
                'minute': 'minuto',
                'never_opened': 'Mai aperto',
                
                # Splash Screen
                'splash_tagline': 'LIBRERIA GIOCHI  •  MAPPE  •  GUIDE',
                'splash_subtitle': 'Gestione Biblioteca Mappe',
                'splash_version': 'versione 3.0',
                'splash_initializing': 'Avvio...',
                'splash_init_components': '🔧 Inizializzazione componenti...',
                'splash_loading_config': '⚙️ Caricamento configurazione...',
                'splash_verifying_files': '📁 Verifica dei file...',
                'splash_setting_interface': '🎨 Configurazione interfaccia...',
                'splash_preparing_library': '🎮 Preparazione libreria giochi...',
                'splash_indexing_content': '🔍 Indicizzazione contenuti...',
                'splash_final_touches': '✨ Applicazione ultimi ritocchi...',
                'splash_ready': '🚀 Pronto per il lancio!',
                
                # Scorciatoie da tastiera
                'keybinds_label': 'Scorciatoie da tastiera',
                'keybinds_desc': 'Personalizza le tue scorciatoie da tastiera',
                'command': 'Comando',
                'add_game_label': 'Aggiungi gioco',
                'search_label': 'Ricerca',
                'clear_search_label': 'Cancella ricerca',
                'refresh_label': 'Aggiorna',
                'favorites_label': 'Preferiti',
                'reset': 'Ripristina impostazioni predefinite',
                'capture_keybind': 'Premi la combinazione di tasti...',
                'capture_cancel': '(Premi ESC per annullare)',
                'capture_button': '🎹 Cattura'
            },
            
            'pt': {
                # Menus
                'file_menu': 'Arquivo',
                'view_menu': 'Visualizar',
                'help_menu': 'Ajuda',
                'config_menu': 'Configurações',
                'about_menu': 'Sobre',
                'exit_menu': 'Sair',
                'search_menu': 'Buscar',
                'toggle_favorites_menu': 'Alternar Favoritos',
                'refresh_list_menu': 'Atualizar Lista',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': 'Adicionar jogo',
                'export_games': 'Exportar jogos',
                'import_games': 'Importar jogos',
                'export_game_dialog_title': 'Selecione jogos para exportar',
                'import_game_dialog_title': 'Importar jogos',

                'export_button': 'Exportar selecionados',
                'import_button': 'Importar jogos',
                'exported_successfully': 'Jogos exportados com sucesso',
                'imported_successfully': 'Jogos importados com sucesso',
                'export_failed': 'Erro ao exportar jogos',
                'import_failed': 'Erro ao importar jogos',
                'add_game_button': '+ Adicionar jogo',
                'library': 'BIBLIOTECA',
                'games_count': 'jogos',
                'game_singular': 'jogo',
                'no_games': 'Nenhum jogo na sua biblioteca.\nVá para "Arquivo" → "Adicionar jogo" para começar.',
                'no_favorites': 'Você não tem jogos favoritos.',
                'no_games_search': 'Nenhum jogo encontrado correspondente à sua pesquisa',
                'no_recent_games': 'Os jogos abertos aparecerão aqui.',
                'search_placeholder': 'Buscar jogos... (favoritos sempre visíveis)',
                
                # Add game form
                'add_game_title': 'Adicionar novo jogo',
                'game_name': 'Nome do jogo:',
                'game_image': 'Imagem do jogo:',
                'browse_image': 'Procurar imagem',
                'map_content': 'Caminho/URL do mapa:',
                'map_type_label': 'Tipo de mapa:',
                'map_type_image': 'Imagem',
                'map_type_web': 'Site web',
                'browse_map': 'Procurar',
                'save': 'Salvar',
                'cancel': 'Cancelar',
                'save_changes': 'Salvar alterações',
                
                # Messages
                'error': 'Erro',
                'success': 'Sucesso',
                'game_saved': 'Jogo salvo com sucesso',
                'fill_required_fields': 'Por favor, preencha todos os campos obrigatórios',
                'invalid_image': 'Formato de imagem inválido',
                'invalid_url': 'URL inválida',
                'select_image': 'Selecionar imagem',
                'select_map': 'Selecionar mapa',
                'image_files': 'Arquivos de imagem',
                'all_files': 'Todos os arquivos',
                
                # About window
                'about_title': 'Sobre Avilon',
                'about_description': 'Avilon é um programa projetado e programado por uma única pessoa, onde você pode gerenciar mapas dos seus jogos favoritos',
                'close': 'Fechar',
                
                # Configuration
                'config_title': 'Configurações',
                'language_label': 'Idioma:',
                'theme_label': 'Tema:',
                'spanish': 'Español',
                'english': 'English',
                'french': 'Français',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'Português',
                'dutch': 'Nederlands',
                'russian': 'Русский',
                'japanese': '日本語',
                'chinese': '中文',
                'theme_slate': 'Ardósia',
                'theme_dark': 'Escuro',
                'theme_light': 'Claro',
                'theme_blue': 'Azul',
                'theme_green': 'Verde',
                'theme_cyberpunk': 'Cyberpunk',
                'theme_gaming_rgb': 'Gaming RGB',
                'theme_retro_arcade': 'Retro Arcade',
                'theme_midnight_gaming': 'Gaming Noturno',
                'theme_esports': 'Esports',
                'apply': 'Aplicar',
                'config_saved': 'Configurações salvas com sucesso',
                
                # Game buttons
                'view_map': 'Ver mapa',
                'edit': 'Editar',
                'delete': 'Excluir',
                'delete_game': 'Excluir jogo',
                'edit_game': 'Editar jogo',
                'no_image': 'Sem imagem',
                'confirm_delete': 'Tem certeza de que deseja excluir este jogo?',
                'confirm_title': 'Confirmar',
                'yes': 'Sim',
                'no': 'Não',
                
                # Edit game
                'edit_game_title': 'Editar jogo',
                
                # Window titles
                'map_window_title': 'Mapa',
                
                # Favorites system
                'all_games': 'Todos',
                'favorites': 'Favoritos',
                'recent': 'Recentes',
                'add_to_favorites': 'Adicionar aos favoritos',
                'remove_from_favorites': 'Remover dos favoritos',
                
                # Startup
                'startup_label': 'Iniciar com o sistema:',
                'startup_enabled': 'Programa configurado para iniciar com o sistema',
                'startup_disabled': 'Programa removido do início automático',
                'startup_error': 'Erro ao configurar o início automático',
                
                # Configuration sections
                'config_section_language_desc': 'Selecione o idioma da interface',
                'config_section_theme_desc': 'Escolha o tema visual da aplicação',
                'config_section_startup_desc': 'Inicie Avilon automaticamente com o sistema',
                'startup_auto_start_label': 'Iniciar automaticamente com o sistema',
                
                # User Guide
                'how_to_use_menu': 'Como usar',
                'tutorial_menu': 'Ver tutorial',
                'report_bug_menu': 'Reportar um erro',
                'user_guide_title': 'Guia do Usuário - Como usar Avilon',
                'guide_tab_games': 'Jogos',
                'guide_tab_maps': 'Mapas',
                'guide_tab_features': 'Recursos',
                'guide_tab_tips': 'Dicas',
                
                # Games tab
                'guide_games_title': '🎮 Gerenciamento de Jogos',
                'guide_games_add_title': '📝 Como adicionar um jogo:',
                'guide_games_add_content': '''1. Vá para o menu "Arquivo" → "Adicionar Jogo"
2. Escreva o nome do jogo
3. Escreva uma descrição do jogo (opcional)
4. Selecione uma imagem (obrigatória):
   • Formatos suportados: PNG, JPG, JPEG, BMP, GIF
   • Recomendado: 250x280 pixels
5. Configure o mapa (veja aba "Mapas")
6. Clique em "Salvar"''',
                'guide_games_manage_title': '⚙️ Gerenciar jogos existentes:',
                'guide_games_manage_content': '''• Clique em ⭐ para marcar/desmarcar como favorito
• "Editar" para modificar dados do jogo
• "Excluir" para remover o jogo da biblioteca''',
                
                # Maps tab
                'guide_maps_title': '🗺️ Configuração de Mapas',
                'guide_maps_types_title': '📋 Tipos de mapas suportados:',
                'guide_maps_image_title': '🖼️ Mapas de Imagem:',
                'guide_maps_image_content': '''• Formatos: PNG, JPG, JPEG, BMP, GIF
• Recursos: Zoom, panorâmica, tela inteira
• Ideal para mapas estáticos do jogo''',
                'guide_maps_web_title': '🌐 Mapas Web (iframe):',
                'guide_maps_web_content': '''• Qualquer URL válida (http:// ou https://)
• Mapas interativos online
• Wikis de jogos, guias web, etc.
• Abre em janela integrada''',
                
                # Features tab
                'guide_features_title': '✨ Recursos Principais',
                'guide_features_search_title': '🔍 Sistema de Pesquisa:',
                'guide_features_search_content': '''• Pesquisar por nome do jogo
• Favoritos sempre permanecem visíveis
• Filtros: "Todos" e "Favoritos"''',
                'guide_features_themes_title': '🎨 Temas e Personalização:',
                'guide_features_themes_content': '''• 5 temas disponíveis: Lousa, Escuro, Claro, Azul, Verde
• Suporte para múltiplos idiomas
• Configurações salvas automaticamente''',
                'guide_features_startup_title': '🚀 Inicialização Automática:',
                'guide_features_startup_content': '''• Configurável nas Configurações
• Inicia com o sistema se habilitado
• Fácil ativação/desativação''',
                
                # Tips tab
                'guide_tips_title': '💡 Dicas e Truques',
                'guide_tips_organization_title': '📚 Organização:',
                'guide_tips_organization_content': '''• Use nomes descritivos para seus jogos
• Marque como favoritos os jogos mais usados
• Organize as imagens por categorias''',
                'guide_tips_images_title': '🖼️ Melhores Práticas para Imagens:',
                'guide_tips_images_content': '''• Use imagens com boa resolução
• Tamanho recomendado: 250x280 pixels
• Evite imagens muito pesadas (>5MB)''',
                'guide_tips_maps_title': '🗺️ Dicas para Mapas:',
                'guide_tips_maps_content': '''• Para mapas web, verifique se a URL está acessível
• Mapas de imagem grandes podem ser ampliados
• Use mapas interativos quando possível''',
                
                # Keyboard Shortcuts tab
                'guide_tab_shortcuts': 'Atalhos de Teclado',
                'guide_shortcuts_title': '⌨️ Atalhos de Teclado',
                'guide_shortcuts_subtitle': 'Acelere seu trabalho com estes atalhos de teclado úteis',
                'guide_shortcuts_games_title': '🎮 Gerenciamento de Jogos',
                'guide_shortcuts_games_content': '''• Ctrl + N - Adicionar novo jogo
• Ctrl + F - Pesquisar jogos
• Escape - Limpar pesquisa
• F5 - Atualizar lista de jogos
• Ctrl + Shift + F - Alternar visualização de favoritos''',
                'guide_shortcuts_navigation_title': '🧭 Navegação e Configurações',
                'guide_shortcuts_navigation_content': '''• F1 - Abrir guia do usuário
• Ctrl + Shift + P - Abrir configurações
• Ctrl + Q - Sair da aplicação''',
                'guide_shortcuts_tips_title': '💡 Dicas para Atalhos',
                'guide_shortcuts_tips_content': '''• Os atalhos funcionam em qualquer lugar da aplicação
• Você pode usar maiúsculas e minúsculas
• A tecla Escape sempre limpa a pesquisa atual
• F1 é sua tecla de ajuda rápida''',
                'guide_shortcuts_workflow_title': '⚡ Fluxo de Trabalho Rápido',
                'guide_shortcuts_workflow_content': 'Os atalhos de teclado podem ser personalizados na janela Configurações. Abra a janela Configurações no menu ou pressione Ctrl + Shift + P para modificar os atalhos de acordo com suas preferências.',
                'guide_shortcuts_open_settings': 'Abrir Configurações',
                
                # Guide subtitle
                'guide_subtitle': 'Tudo que você precisa saber para usar Avilon',
                
                # Objetivos na apresentação do jogo
                'objectives': 'Objetivos',
                'no_objectives': 'Nenhum objetivo',
                'new_objective': 'Novo objetivo',
                'write_objective': 'Escreva o objetivo:',
                'add_objective': 'Adicionar objetivo',
                
                # Descrição do jogo e metadados
                'game_description': 'Descrição (opcional):',
                'description': 'Descrição',
                'added_date': 'Data de adição',
                'play_time': 'Tempo de jogo',
                'days': 'dias',
                'day': 'dia',
                'hours': 'horas',
                'hour': 'hora',
                'minutes': 'minutos',
                'minute': 'minuto',
                'never_opened': 'Nunca aberto',
                
                # Splash Screen
                'splash_tagline': 'BIBLIOTECA DE JOGOS  •  MAPAS  •  GUIAS',
                'splash_subtitle': 'Gerenciador de Biblioteca de Mapas',
                'splash_version': 'versão 3.0',
                'splash_initializing': 'Iniciando...',
                'splash_init_components': '🔧 Inicializando componentes...',
                'splash_loading_config': '⚙️ Carregando configuração...',
                'splash_verifying_files': '📁 Verificando arquivos...',
                'splash_setting_interface': '🎨 Configurando interface...',
                'splash_preparing_library': '🎮 Preparando biblioteca de jogos...',
                'splash_indexing_content': '🔍 Indexando conteúdo...',
                'splash_final_touches': '✨ Aplicando toques finais...',
                'splash_ready': '🚀 Pronto para lançar!',
                
                # Atalhos de teclado
                'keybinds_label': 'Atalhos de teclado',
                'keybinds_desc': 'Personalize seus atalhos de teclado',
                'command': 'Comando',
                'add_game_label': 'Adicionar jogo',
                'search_label': 'Pesquisar',
                'clear_search_label': 'Limpar pesquisa',
                'refresh_label': 'Atualizar',
                'favorites_label': 'Favoritos',
                'reset': 'Redefinir padrões',
                'capture_keybind': 'Pressione a combinação de teclas...',
                'capture_cancel': '(Pressione ESC para cancelar)',
                'capture_button': '🎹 Capturar'
            },
            
            'nl': {
                # Menus
                'file_menu': 'Bestand',
                'view_menu': 'Weergave',
                'help_menu': 'Help',
                'config_menu': 'Instellingen',
                'about_menu': 'Over',
                'exit_menu': 'Afsluiten',
                'search_menu': 'Zoeken',
                'toggle_favorites_menu': 'Favorieten Wisselen',
                'refresh_list_menu': 'Lijst Vernieuwen',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': 'Spel toevoegen',
                'export_games': 'Spellen exporteren',
                'import_games': 'Spellen importeren',
                'export_game_dialog_title': 'Selecteer spellen om te exporteren',
                'import_game_dialog_title': 'Spellen importeren',

                'export_button': 'Selectie exporteren',
                'import_button': 'Spellen importeren',
                'exported_successfully': 'Spellen succesvol geëxporteerd',
                'imported_successfully': 'Spellen succesvol geïmporteerd',
                'export_failed': 'Fout bij het exporteren van spellen',
                'import_failed': 'Fout bij het importeren van spellen',
                'add_game_button': '+ Spel toevoegen',
                'library': 'BIBLIOTHEEK',
                'games_count': 'spellen',
                'game_singular': 'spel',
                'no_games': 'Geen spellen in je bibliotheek.\nGa naar "Bestand" → "Spel toevoegen" om te beginnen.',
                'no_favorites': 'Je hebt geen favoriete spellen.',
                'no_games_search': 'Geen spellen gevonden die overeenkomen met je zoekopdracht',
                'no_recent_games': 'Geopende spellen verschijnen hier.',
                'search_placeholder': 'Zoek spellen... (favorieten altijd zichtbaar)',
                
                # Add game form
                'add_game_title': 'Nieuw spel toevoegen',
                'game_name': 'Spelnaam:',
                'game_image': 'Spelafbeelding:',
                'browse_image': 'Afbeelding bladeren',
                'map_content': 'Kaart pad/URL:',
                'map_type_label': 'Kaart type:',
                'map_type_image': 'Afbeelding',
                'map_type_web': 'Website',
                'browse_map': 'Bladeren',
                'save': 'Opslaan',
                'cancel': 'Annuleren',
                'save_changes': 'Wijzigingen opslaan',
                
                # Messages
                'error': 'Fout',
                'success': 'Succes',
                'game_saved': 'Spel succesvol opgeslagen',
                'fill_required_fields': 'Vul alle verplichte velden in',
                'invalid_image': 'Ongeldige afbeeldingsformaat',
                'invalid_url': 'Ongeldige URL',
                'select_image': 'Selecteer afbeelding',
                'select_map': 'Selecteer kaart',
                'image_files': 'Afbeeldingsbestanden',
                'all_files': 'Alle bestanden',
                
                # About window
                'about_title': 'Over Avilon',
                'about_description': 'Avilon is een programma ontworpen en geprogrammeerd door één persoon, waar je kaarten voor je favoriete spellen kunt beheren',
                'close': 'Sluiten',
                
                # Configuration
                'config_title': 'Instellingen',
                'language_label': 'Taal:',
                'theme_label': 'Thema:',
                'spanish': 'Español',
                'english': 'English',
                'french': 'Français',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'Português',
                'dutch': 'Nederlands',
                'russian': 'Русский',
                'japanese': '日本語',
                'chinese': '中文',
                'theme_slate': 'Lei',
                'theme_dark': 'Donker',
                'theme_light': 'Licht',
                'theme_blue': 'Blauw',
                'theme_green': 'Groen',
                'theme_cyberpunk': 'Cyberpunk',
                'theme_gaming_rgb': 'Gaming RGB',
                'theme_retro_arcade': 'Retro Arcade',
                'theme_midnight_gaming': 'Middernacht Gaming',
                'theme_esports': 'Esports',
                'apply': 'Toepassen',
                'config_saved': 'Instellingen succesvol opgeslagen',
                
                # Game buttons
                'view_map': 'Kaart bekijken',
                'edit': 'Bewerken',
                'delete': 'Verwijderen',
                'delete_game': 'Spel verwijderen',
                'edit_game': 'Spel bewerken',
                'no_image': 'Geen afbeelding',
                'confirm_delete': 'Weet je zeker dat je dit spel wilt verwijderen?',
                'confirm_title': 'Bevestigen',
                'yes': 'Ja',
                'no': 'Nee',
                
                # Edit game
                'edit_game_title': 'Spel bewerken',
                
                # Window titles
                'map_window_title': 'Kaart',
                
                # Favorites system
                'all_games': 'Alle',
                'favorites': 'Favorieten',
                'recent': 'Recent',
                'add_to_favorites': 'Toevoegen aan favorieten',
                'remove_from_favorites': 'Verwijderen uit favorieten',
                
                # Startup
                'startup_label': 'Starten met het systeem:',
                'startup_enabled': 'Programma ingesteld om met het systeem te starten',
                'startup_disabled': 'Programma verwijderd van automatisch opstarten',
                'startup_error': 'Fout bij het instellen van automatisch opstarten',
                
                # Configuration sections
                'config_section_language_desc': 'Selecteer de taal van de interface',
                'config_section_theme_desc': 'Kies het visuele thema van de applicatie',
                'config_section_startup_desc': 'Start Avilon automatisch met het systeem',
                'startup_auto_start_label': 'Automatisch starten met het systeem',
                
                # User Guide
                'how_to_use_menu': 'Hoe te gebruiken',
                'tutorial_menu': 'Tutorial bekijken',
                'report_bug_menu': 'Een fout melden',
                'user_guide_title': 'Gebruikershandleiding - Hoe Avilon te gebruiken',
                'guide_tab_games': 'Spellen',
                'guide_tab_maps': 'Kaarten',
                'guide_tab_features': 'Kenmerken',
                'guide_tab_tips': 'Tips',
                
                # Games tab
                'guide_games_title': '🎮 Spelbeheer',
                'guide_games_add_title': '📝 Een spel toevoegen:',
                'guide_games_add_content': '''1. Ga naar menu "Bestand" → "Spel toevoegen"
2. Typ de spelnaam in
3. Typ een spelomschrijving in (optioneel)
4. Selecteer een afbeelding (vereist):
   • Ondersteunde formaten: PNG, JPG, JPEG, BMP, GIF
   • Aanbevolen: 250x280 pixels
5. Configureer de kaart (zie tab "Kaarten")
6. Klik op "Opslaan"''',
                'guide_games_manage_title': '⚙️ Bestaande spellen beheren:',
                'guide_games_manage_content': '''• Klik op ⭐ om als favoriet in/uit te schakelen
• "Bewerken" om spelgegevens aan te passen
• "Verwijderen" om het spel uit je bibliotheek te verwijderen''',
                
                # Maps tab
                'guide_maps_title': '🗺️ Kaartconfiguratie',
                'guide_maps_types_title': '📋 Ondersteunde kaarttypen:',
                'guide_maps_image_title': '🖼️ Afbeeldingskaarten:',
                'guide_maps_image_content': '''• Formaten: PNG, JPG, JPEG, BMP, GIF
• Functies: Zoomen, pannen, volledig scherm
• Ideaal voor statische spelkaarten''',
                'guide_maps_web_title': '🌐 Webkaarten (iframe):',
                'guide_maps_web_content': '''• Elke geldige URL (http:// of https://)
• Interactieve online kaarten
• Spelwiki\'s, webgidsen, enz.
• Opent in geïntegreerd venster''',
                
                # Features tab
                'guide_features_title': '✨ Hoofdfuncties',
                'guide_features_search_title': '🔍 Zoeksysteem:',
                'guide_features_search_content': '''• Zoeken op spelnaam
• Favorieten blijven altijd zichtbaar
• Filters: "Alle" en "Favorieten"''',
                'guide_features_themes_title': '🎨 Thema\'s en Aanpassing:',
                'guide_features_themes_content': '''• 5 beschikbare thema\'s: Lei, Donker, Licht, Blauw, Groen
• Ondersteuning voor meerdere talen
• Instellingen automatisch opgeslagen''',
                'guide_features_startup_title': '🚀 Automatisch Starten:',
                'guide_features_startup_content': '''• Configureerbaar vanuit Instellingen
• Start met het systeem als ingeschakeld
• Gemakkelijke in/uitschakeling''',
                
                # Tips tab
                'guide_tips_title': '💡 Tips en Trucs',
                'guide_tips_organization_title': '📚 Organisatie:',
                'guide_tips_organization_content': '''• Gebruik beschrijvende namen voor je spellen
• Markeer veel gebruikte spellen als favoriet
• Organiseer afbeeldingen naar categorie\'ën''',
                'guide_tips_images_title': '🖼️ Beste Praktijken voor Afbeeldingen:',
                'guide_tips_images_content': '''• Gebruik afbeeldingen met goede resolutie
• Aanbevolen grootte: 250x280 pixels
• Vermijd zeer zware afbeeldingen (>5MB)''',
                'guide_tips_maps_title': '🗺️ Kaart Tips:',
                'guide_tips_maps_content': '''• Voor webkaarten, controleer of de URL toegankelijk is
• Grote afbeeldingskaarten kunnen worden ingezoomd
• Gebruik interactieve kaarten waar mogelijk''',
                
                # Keyboard Shortcuts tab
                'guide_tab_shortcuts': 'Toetsenbord Snelkoppelingen',
                'guide_shortcuts_title': '⌨️ Toetsenbord Snelkoppelingen',
                'guide_shortcuts_subtitle': 'Versnel je werk met deze nuttige toetsenbordssnelkoppelingen',
                'guide_shortcuts_games_title': '🎮 Spelbeheer',
                'guide_shortcuts_games_content': '''• Ctrl + N - Nieuw spel toevoegen
• Ctrl + F - Spellen zoeken
• Escape - Zoekopdracht wissen
• F5 - Spellenlijst vernieuwen
• Ctrl + Shift + F - Favorieten weergave omschakelen''',
                'guide_shortcuts_navigation_title': '🧭 Navigatie en Instellingen',
                'guide_shortcuts_navigation_content': '''• F1 - Gebruikershandleiding openen
• Ctrl + Shift + P - Instellingen openen
• Ctrl + Q - Toepassing afsluiten''',
                'guide_shortcuts_tips_title': '💡 Snelkoppeling Tips',
                'guide_shortcuts_tips_content': '''• Snelkoppelingen werken overal in de toepassing
• Je kunt zowel hoofd- als kleine letters gebruiken
• Escape wist altijd de huidige zoekopdracht
• F1 is je snelle hulptoets''',
                'guide_shortcuts_workflow_title': '⚡ Snelle Workflow',
                'guide_shortcuts_workflow_content': 'Toetsenbordsnelkoppelingen kunnen worden aangepast in het instellingenvenster. Open het instellingenvenster via het menu of druk op Ctrl + Shift + P om snelkoppelingen naar uw voorkeur aan te passen.',
                'guide_shortcuts_open_settings': 'Instellingen openen',
                
                # Guide subtitle
                'guide_subtitle': 'Alles wat je moet weten om Avilon te gebruiken',
                
                # Doelstellingen in gamepresentatie
                'objectives': 'Doelstellingen',
                'no_objectives': 'Geen doelstellingen',
                'new_objective': 'Nieuwe doelstelling',
                'write_objective': 'Schrijf de doelstelling:',
                'add_objective': 'Doelstelling toevoegen',
                
                # Spelomschrijving en metagegevens
                'game_description': 'Beschrijving (optioneel):',
                'description': 'Beschrijving',
                'added_date': 'Toegevoegde datum',
                'play_time': 'Speeltijd',
                'days': 'dagen',
                'day': 'dag',
                'hours': 'uren',
                'hour': 'uur',
                'minutes': 'minuten',
                'minute': 'minuut',
                'never_opened': 'Nog nooit geopend',
                
                # Splash Screen
                'splash_tagline': 'GAMEBIBLIOTHEEK  •  KAARTEN  •  GIDSEN',
                'splash_subtitle': 'Kaartbibliotheker',
                'splash_version': 'versie 3.0',
                'splash_initializing': 'Starten...',
                'splash_init_components': '🔧 Componenten initialiseren...',
                'splash_loading_config': '⚙️ Configuratie laden...',
                'splash_verifying_files': '📁 Bestanden verifiëren...',
                'splash_setting_interface': '🎨 Interface configureren...',
                'splash_preparing_library': '🎮 Spelbibliotheken voorbereiden...',
                'splash_indexing_content': '🔍 Inhoud indexeren...',
                'splash_final_touches': '✨ Laatste aanpassingen toepassen...',
                'splash_ready': '🚀 Klaar om te starten!',
                
                # Sneltoetsen
                'keybinds_label': 'Sneltoetsen',
                'keybinds_desc': 'Pas uw sneltoetsen aan',
                'command': 'Opdracht',
                'add_game_label': 'Spel toevoegen',
                'search_label': 'Zoeken',
                'clear_search_label': 'Zoekterm wissen',
                'refresh_label': 'Vernieuwen',
                'favorites_label': 'Favorieten',
                'reset': 'Standaardinstellingen herstellen',
                'capture_keybind': 'Druk op de toetscombinatie...',
                'capture_cancel': '(Druk op ESC om te annuleren)',
                'capture_button': '🎹 Vastleggen'
            },
            
            'ru': {
                # Menus
                'file_menu': 'Файл',
                'view_menu': 'Вид',
                'help_menu': 'Справка',
                'config_menu': 'Настройки',
                'about_menu': 'О программе',
                'exit_menu': 'Выход',
                'search_menu': 'Поиск',
                'toggle_favorites_menu': 'Переключить Избранное',
                'refresh_list_menu': 'Обновить Список',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': 'Добавить игру',
                'export_games': 'Экспортировать игры',
                'import_games': 'Импортировать игры',
                'export_game_dialog_title': 'Выберите игры для экспорта',
                'import_game_dialog_title': 'Импортировать игры',

                'export_button': 'Экспортировать выбранное',
                'import_button': 'Импортировать игры',
                'exported_successfully': 'Игры успешно экспортированы',
                'imported_successfully': 'Игры успешно импортированы',
                'export_failed': 'Ошибка при экспорте игр',
                'import_failed': 'Ошибка при импорте игр',
                'add_game_button': '+ Добавить игру',
                'library': 'БИБЛИОТЕКА',
                'games_count': 'игр',
                'game_singular': 'игра',
                'no_games': 'Нет игр в вашей библиотеке.\nПерейдите в "Файл" → "Добавить игру", чтобы начать.',
                'no_favorites': 'У вас нет любимых игр.',
                'no_games_search': 'Не найдено игр, соответствующих вашему поиску',
                'no_recent_games': 'Открытые игры появятся здесь.',
                'search_placeholder': 'Поиск игр... (избранные всегда видимы)',
                
                # Add game form
                'add_game_title': 'Добавить новую игру',
                'game_name': 'Название игры:',
                'game_image': 'Изображение игры:',
                'browse_image': 'Выбрать изображение',
                'map_content': 'Путь/URL карты:',
                'map_type_label': 'Тип карты:',
                'map_type_image': 'Изображение',
                'map_type_web': 'Веб-сайт',
                'browse_map': 'Обзор',
                'save': 'Сохранить',
                'cancel': 'Отмена',
                'save_changes': 'Сохранить изменения',
                
                # Messages
                'error': 'Ошибка',
                'success': 'Успех',
                'game_saved': 'Игра успешно сохранена',
                'fill_required_fields': 'Пожалуйста, заполните все обязательные поля',
                'invalid_image': 'Неверный формат изображения',
                'invalid_url': 'Неверный URL',
                'select_image': 'Выбрать изображение',
                'select_map': 'Выбрать карту',
                'image_files': 'Файлы изображений',
                'all_files': 'Все файлы',
                
                # About window
                'about_title': 'О Avilon',
                'about_description': 'Avilon - это программа, разработанная и запрограммированная одним человеком, где вы можете управлять картами ваших любимых игр',
                'close': 'Закрыть',
                
                # Configuration
                'config_title': 'Настройки',
                'language_label': 'Язык:',
                'theme_label': 'Тема:',
                'spanish': 'Español',
                'english': 'English',
                'french': 'Français',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'Português',
                'dutch': 'Nederlands',
                'russian': 'Русский',
                'japanese': '日本語',
                'chinese': '中文',
                'theme_slate': 'Сланец',
                'theme_dark': 'Тёмная',
                'theme_light': 'Светлая',
                'theme_blue': 'Синяя',
                'theme_green': 'Зелёная',
                'theme_cyberpunk': 'Киберпанк',
                'theme_gaming_rgb': 'Gaming RGB',
                'theme_retro_arcade': 'Ретро Аркада',
                'theme_midnight_gaming': 'Полуночный Гейминг',
                'theme_esports': 'Киберспорт',
                'apply': 'Применить',
                'config_saved': 'Настройки успешно сохранены',
                
                # Game buttons
                'view_map': 'Посмотреть карту',
                'edit': 'Редактировать',
                'delete': 'Удалить',
                'delete_game': 'Удалить игру',
                'edit_game': 'Редактировать игру',
                'no_image': 'Нет изображения',
                'confirm_delete': 'Вы уверены, что хотите удалить эту игру?',
                'confirm_title': 'Подтвердить',
                'yes': 'Да',
                'no': 'Нет',
                
                # Edit game
                'edit_game_title': 'Редактировать игру',
                
                # Window titles
                'map_window_title': 'Карта',
                
                # Favorites system
                'all_games': 'Все',
                'favorites': 'Избранные',
                'recent': 'Недавние',
                'add_to_favorites': 'Добавить в избранное',
                'remove_from_favorites': 'Удалить из избранного',
                
                # Startup
                'startup_label': 'Запуск вместе с системой:',
                'startup_enabled': 'Программа настроена для запуска вместе с системой',
                'startup_disabled': 'Программа удалена из автозапуска',
                'startup_error': 'Ошибка настройки автозапуска',
                
                # Configuration sections
                'config_section_language_desc': 'Выберите язык интерфейса',
                'config_section_theme_desc': 'Выберите визуальную тему приложения',
                'config_section_startup_desc': 'Запускайте Avilon автоматически при запуске системы',
                'startup_auto_start_label': 'Запускать автоматически при запуске системы',
                
                # User Guide
                'how_to_use_menu': 'Как использовать',
                'tutorial_menu': 'Показать обучение',
                'report_bug_menu': 'Сообщить об ошибке',
                'user_guide_title': 'Руководство пользователя - Как использовать Avilon',
                'guide_tab_games': 'Игры',
                'guide_tab_maps': 'Карты',
                'guide_tab_features': 'Возможности',
                'guide_tab_tips': 'Советы',
                
                # Games tab
                'guide_games_title': '🎮 Управление Играми',
                'guide_games_add_title': '📝 Как добавить игру:',
                'guide_games_add_content': '''1. Перейдите в меню "Файл" → "Добавить игру"
2. Введите название игры
3. Введите описание игры (опционально)
4. Выберите изображение (обязательно):
   • Поддерживаемые форматы: PNG, JPG, JPEG, BMP, GIF
   • Рекомендуется: 250x280 пиксели
5. Настройте карту (см. вкладку "Карты")
6. Нажмите "Сохранить"''',
                'guide_games_manage_title': '⚙️ Управление существующими играми:',
                'guide_games_manage_content': '''• Нажмите на ⭐ для отмечения/отмены отметки избранного
• "Редактировать" для изменения данных игры
• "Удалить" для удаления игры из библиотеки''',
                
                # Maps tab
                'guide_maps_title': '🗺️ Настройка Карт',
                'guide_maps_types_title': '📋 Поддерживаемые типы карт:',
                'guide_maps_image_title': '🖼️ Карты-Изображения:',
                'guide_maps_image_content': '''• Форматы: PNG, JPG, JPEG, BMP, GIF
• Функции: Масштабирование, панорамирование, полноэкранный режим
• Идеально для статических карт игры''',
                'guide_maps_web_title': '🌐 Веб-Карты (iframe):',
                'guide_maps_web_content': '''• Любой действительный URL (http:// или https://)
• Интерактивные онлайн-карты
• Wiki игр, веб-гайды и т. д.
• Открывается в встроенном окне''',
                
                # Features tab
                'guide_features_title': '✨ Основные Возможности',
                'guide_features_search_title': '🔍 Система Поиска:',
                'guide_features_search_content': '''• Поиск по названию игры
• Избранные всегда остаются видимыми
• Фильтры: "Все" и "Избранные"''',
                'guide_features_themes_title': '🎨 Темы и Настройка:',
                'guide_features_themes_content': '''• 5 доступных тем: Сланец, Темная, Светлая, Синяя, Зеленая
• Поддержка нескольких языков
• Параметры сохраняются автоматически''',
                'guide_features_startup_title': '🚀 Автоматический Запуск:',
                'guide_features_startup_content': '''• Настраивается из Параметров
• Запускается вместе с системой, если включено
• Легкое включение/отключение''',
                
                # Tips tab
                'guide_tips_title': '💡 Советы и Трюки',
                'guide_tips_organization_title': '📚 Организация:',
                'guide_tips_organization_content': '''• Используйте описательные названия для ваших игр
• Отметьте часто используемые игры как избранные
• Организуйте изображения по категориям''',
                'guide_tips_images_title': '🖼️ Лучшие Практики для Изображений:',
                'guide_tips_images_content': '''• Используйте изображения хорошего качества
• Рекомендуемый размер: 250x280 пиксели
• Избегайте очень больших изображений (>5MB)''',
                'guide_tips_maps_title': '🗺️ Советы по Картам:',
                'guide_tips_maps_content': '''• Для веб-карт проверьте доступность URL
• Большие карты-изображения можно масштабировать
• По возможности используйте интерактивные карты''',
                
                # Keyboard Shortcuts tab
                'guide_tab_shortcuts': 'Горячие Клавиши',
                'guide_shortcuts_title': '⌨️ Горячие Клавиши',
                'guide_shortcuts_subtitle': 'Ускорьте свою работу с помощью этих полезных сочетаний клавиш',
                'guide_shortcuts_games_title': '🎮 Управление Играми',
                'guide_shortcuts_games_content': '''• Ctrl + N - Добавить новую игру
• Ctrl + F - Поиск игр
• Escape - Очистить поиск
• F5 - Обновить список игр
• Ctrl + Shift + F - Переключить представление избранного''',
                'guide_shortcuts_navigation_title': '🧭 Навигация и Параметры',
                'guide_shortcuts_navigation_content': '''• F1 - Открыть руководство пользователя
• Ctrl + Shift + P - Открыть параметры
• Ctrl + Q - Выход из приложения''',
                'guide_shortcuts_tips_title': '💡 Советы по Горячим Клавишам',
                'guide_shortcuts_tips_content': '''• Горячие клавиши работают везде в приложении
• Вы можете использовать прописные и строчные буквы
• Escape всегда очищает текущий поиск
• F1 - ваша клавиша быстрой помощи''',
                'guide_shortcuts_workflow_title': '⚡ Быстрый Рабочий Процесс',
                'guide_shortcuts_workflow_content': 'Горячие клавиши можно настроить в окне Параметры. Откройте окно Параметры из меню или нажмите Ctrl + Shift + P, чтобы изменить горячие клавиши в соответствии с вашими предпочтениями.',
                'guide_shortcuts_open_settings': 'Открыть параметры',
                
                # Guide subtitle
                'guide_subtitle': 'Все, что вам нужно знать для использования Avilon',
                
                # Цели в представлении игры
                'objectives': 'Цели',
                'no_objectives': 'Нет целей',
                'new_objective': 'Новая цель',
                'write_objective': 'Напишите цель:',
                'add_objective': 'Добавить цель',
                
                # Описание игры и метаданные
                'game_description': 'Описание (опционально):',
                'description': 'Описание',
                'added_date': 'Дата добавления',
                'play_time': 'Время игры',
                'days': 'дней',
                'day': 'день',
                'hours': 'часов',
                'hour': 'час',
                'minutes': 'минут',
                'minute': 'минута',
                'never_opened': 'Никогда не открыто',
                
                # Splash Screen
                'splash_tagline': 'БИБЛИОТЕКА ИГР  •  КАРТЫ  •  РУКОВОДСТВА',
                'splash_subtitle': 'Менеджер библиотеки карт',
                'splash_version': 'версия 3.0',
                'splash_initializing': 'Запуск...',
                'splash_init_components': '🔧 Инициализация компонентов...',
                'splash_loading_config': '⚙️ Загрузка конфигурации...',
                'splash_verifying_files': '📁 Проверка файлов...',
                'splash_setting_interface': '🎨 Настройка интерфейса...',
                'splash_preparing_library': '🎮 Подготовка библиотеки игр...',
                'splash_indexing_content': '🔍 Индексирование содержимого...',
                'splash_final_touches': '✨ Применение финальных штрихов...',
                'splash_ready': '🚀 Готово к запуску!',
                
                # Горячие клавиши
                'keybinds_label': 'Горячие клавиши',
                'keybinds_desc': 'Настройте свои горячие клавиши',
                'command': 'Команда',
                'add_game_label': 'Добавить игру',
                'search_label': 'Поиск',
                'clear_search_label': 'Очистить поиск',
                'refresh_label': 'Обновить',
                'favorites_label': 'Избранное',
                'reset': 'Восстановить по умолчанию',
                'capture_keybind': 'Нажмите комбинацию клавиш...',
                'capture_cancel': '(Нажмите ESC для отмены)',
                'capture_button': '🎹 Захватить'
            },
            
            'ja': {
                # Menus
                'file_menu': 'ファイル',
                'view_menu': '表示',
                'help_menu': 'ヘルプ',
                'config_menu': '設定',
                'about_menu': 'について',
                'exit_menu': '終了',
                'search_menu': '検索',
                'toggle_favorites_menu': 'お気に入り切替',
                'refresh_list_menu': 'リスト更新',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': 'ゲームを追加',
                'export_games': 'ゲームをエクスポート',
                'import_games': 'ゲームをインポート',
                'export_game_dialog_title': 'エクスポートするゲームを選択',
                'import_game_dialog_title': 'ゲームをインポート',

                'export_button': '選択したゲームをエクスポート',
                'import_button': 'ゲームをインポート',
                'exported_successfully': 'ゲームのエクスポートに成功しました',
                'imported_successfully': 'ゲームのインポートに成功しました',
                'export_failed': 'ゲームのエクスポートに失敗しました',
                'import_failed': 'ゲームのインポートに失敗しました',
                'add_game_button': '+ ゲームを追加',
                'library': 'ライブラリ',
                'games_count': 'ゲーム',
                'game_singular': 'ゲーム',
                'no_games': 'ライブラリにゲームがありません。\n「ファイル」→「ゲームを追加」から始めてください。',
                'no_favorites': 'お気に入りのゲームはありません。',
                'no_games_search': '検索に一致するゲームが見つかりません',
                'no_recent_games': '開いたゲームがここに表示されます。',
                'search_placeholder': 'ゲームを検索... (お気に入りは常に表示)',
                
                # Add game form
                'add_game_title': '新しいゲームを追加',
                'game_name': 'ゲーム名:',
                'game_image': 'ゲーム画像:',
                'browse_image': '画像を参照',
                'map_content': 'マップパス/URL:',
                'map_type_label': 'マップタイプ:',
                'map_type_image': '画像',
                'map_type_web': 'ウェブサイト',
                'browse_map': '参照',
                'save': '保存',
                'cancel': 'キャンセル',
                'save_changes': '変更を保存',
                
                # Messages
                'error': 'エラー',
                'success': '成功',
                'game_saved': 'ゲームが正常に保存されました',
                'fill_required_fields': '必須項目をすべて入力してください',
                'invalid_image': '無効な画像形式',
                'invalid_url': '無効なURL',
                'select_image': '画像を選択',
                'select_map': 'マップを選択',
                'image_files': '画像ファイル',
                'all_files': 'すべてのファイル',
                
                # About window
                'about_title': 'Avilonについて',
                'about_description': 'Avilonは一人で設計・プログラムされたプログラムで、お気に入りのゲームのマップを管理できます',
                'close': '閉じる',
                
                # Configuration
                'config_title': '設定',
                'language_label': '言語:',
                'theme_label': 'テーマ:',
                'spanish': 'Español',
                'english': 'English',
                'french': 'Français',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'Português',
                'dutch': 'Nederlands',
                'russian': 'Русский',
                'japanese': '日本語',
                'chinese': '中文',
                'theme_slate': 'スレート',
                'theme_dark': 'ダーク',
                'theme_light': 'ライト',
                'theme_blue': 'ブルー',
                'theme_green': 'グリーン',
                'theme_cyberpunk': 'サイバーパンク',
                'theme_gaming_rgb': 'ゲーミングRGB',
                'theme_retro_arcade': 'レトロアーケード',
                'theme_midnight_gaming': 'ミッドナイトゲーミング',
                'theme_esports': 'eスポーツ',
                'apply': '適用',
                'config_saved': '設定が正常に保存されました',
                
                # Game buttons
                'view_map': 'マップを表示',
                'edit': '編集',
                'delete': '削除',
                'delete_game': 'ゲームを削除',
                'edit_game': 'ゲームを編集',
                'no_image': '画像なし',
                'confirm_delete': 'このゲームを削除してもよろしいですか？',
                'confirm_title': '確認',
                'yes': 'はい',
                'no': 'いいえ',
                
                # Edit game
                'edit_game_title': 'ゲームを編集',
                
                # Window titles
                'map_window_title': 'マップ',
                
                # Favorites system
                'all_games': 'すべて',
                'favorites': 'お気に入り',
                'recent': '最近',
                'add_to_favorites': 'お気に入りに追加',
                'remove_from_favorites': 'お気に入りから削除',
                
                # Startup
                'startup_label': 'システム起動時に起動:',
                'startup_enabled': 'システム起動時にプログラムを起動するよう設定しました',
                'startup_disabled': 'プログラムが自動起動から削除されました',
                'startup_error': '自動起動の設定でエラーが発生しました',
                
                # Configuration sections
                'config_section_language_desc': 'インターフェース言語を選択',
                'config_section_theme_desc': 'アプリケーションのビジュアルテーマを選択',
                'config_section_startup_desc': 'システム起動時にAvilonを自動起動',
                'startup_auto_start_label': 'システム起動時に自動起動',
                
                # User Guide
                'how_to_use_menu': '使い方',
                'tutorial_menu': 'チュートリアルを見る',
                'report_bug_menu': 'エラーを報告',
                'user_guide_title': 'ユーザーガイド - Avilon の使い方',
                'guide_tab_games': 'ゲーム',
                'guide_tab_maps': 'マップ',
                'guide_tab_features': '機能',
                'guide_tab_tips': 'ヒント',
                
                # Games tab
                'guide_games_title': '🎮 ゲーム管理',
                'guide_games_add_title': '📝 ゲームを追加する方法:',
                'guide_games_add_content': '''1. メニューの「ファイル」→「ゲームを追加」に進みます
2. ゲーム名を入力します
3. ゲーム説明を入力します(オプション)
4. 画像を選択します(必須):
   • サポートされている形式: PNG、JPG、JPEG、BMP、GIF
   • 推奨: 250x280ピクセル
5. マップを設定します(「マップ」タブを参照)
6. 「保存」をクリックします''',
                'guide_games_manage_title': '⚙️ 既存ゲームを管理する:',
                'guide_games_manage_content': '''• ⭐ をクリックしてお気に入りのマークを付ける/削除する
• 「編集」してゲームデータを変更する
• 「削除」してゲームをライブラリから削除する''',
                
                # Maps tab
                'guide_maps_title': '🗺️ マップ設定',
                'guide_maps_types_title': '📋 サポートされているマップタイプ:',
                'guide_maps_image_title': '🖼️ 画像マップ:',
                'guide_maps_image_content': '''• 形式: PNG、JPG、JPEG、BMP、GIF
• 機能: ズーム、パン、全画面表示
• 静的なゲームマップに最適''',
                'guide_maps_web_title': '🌐 ウェブマップ(iframe):',
                'guide_maps_web_content': '''• 有効なURL (http://またはhttps://)
• インタラクティブなオンラインマップ
• ゲームウィキ、ウェブガイドなど
• 統合ウィンドウで開きます''',
                
                # Features tab
                'guide_features_title': '✨ 主な機能',
                'guide_features_search_title': '🔍 検索システム:',
                'guide_features_search_content': '''• ゲーム名で検索
• お気に入りは常に表示されたままです
• フィルタ: 「すべて」と「お気に入り」''',
                'guide_features_themes_title': '🎨 テーマとカスタマイズ:',
                'guide_features_themes_content': '''• 5つの利用可能なテーマ: スレート、ダーク、ライト、ブルー、グリーン
• 複数言語サポート
• 設定は自動的に保存されます''',
                'guide_features_startup_title': '🚀 自動起動:',
                'guide_features_startup_content': '''• 設定から設定可能
• 有効な場合、システム起動時に開始します
• 簡単な有効/無効切り替え''',
                
                # Tips tab
                'guide_tips_title': '💡 ヒントとコツ',
                'guide_tips_organization_title': '📚 組織:',
                'guide_tips_organization_content': '''• ゲームに説明的な名前を使用する
• よく使うゲームをお気に入りにマークする
• 画像をカテゴリ別に整理する''',
                'guide_tips_images_title': '🖼️ 画像のベストプラクティス:',
                'guide_tips_images_content': '''• 高解像度の画像を使用する
• 推奨サイズ: 250x280ピクセル
• 非常に大きな画像を避ける(>5MB)''',
                'guide_tips_maps_title': '🗺️ マップのヒント:',
                'guide_tips_maps_content': '''• ウェブマップの場合、URLがアクセス可能であることを確認
• 大きな画像マップはズームできます
• 可能な限りインタラクティブなマップを使用する''',
                
                # Keyboard Shortcuts tab
                'guide_tab_shortcuts': 'キーボードショートカット',
                'guide_shortcuts_title': '⌨️ キーボードショートカット',
                'guide_shortcuts_subtitle': 'これらの便利なキーボードショートカットで作業を高速化してください',
                'guide_shortcuts_games_title': '🎮 ゲーム管理',
                'guide_shortcuts_games_content': '''• Ctrl + N - 新しいゲームを追加
• Ctrl + F - ゲームを検索
• Escape - 検索をクリア
• F5 - ゲームリストを更新
• Ctrl + Shift + F - お気に入り表示を切り替える''',
                'guide_shortcuts_navigation_title': '🧭 ナビゲーションと設定',
                'guide_shortcuts_navigation_content': '''• F1 - ユーザーガイドを開く
• Ctrl + Shift + P - 設定を開く
• Ctrl + Q - アプリケーションを終了する''',
                'guide_shortcuts_tips_title': '💡 ショートカットのヒント',
                'guide_shortcuts_tips_content': '''• ショートカットはアプリケーション全体で動作します
• 大文字と小文字の両方を使用できます
• Escapeキーは常に現在の検索をクリアします
• F1は素早いヘルプキーです''',
                'guide_shortcuts_workflow_title': '⚡ クイックワークフロー',
                'guide_shortcuts_workflow_content': 'キーボードショートカットは設定ウィンドウでカスタマイズできます。メニューから設定ウィンドウを開くか、Ctrl + Shift + P を押して、ショートカットを設定に合わせて変更してください。',
                'guide_shortcuts_open_settings': '設定を開く',
                
                # Guide subtitle
                'guide_subtitle': 'Avilon を使用するために知っておくべきすべてのこと',
                
                # ゲームプレゼンテーションの目的
                'objectives': '目的',
                'no_objectives': '目的なし',
                'new_objective': '新しい目的',
                'write_objective': '目的を記述してください:',
                'add_objective': '目的を追加',
                
                # ゲームの説明とメタデータ
                'game_description': '説明（オプション）:',
                'description': '説明',
                'added_date': '追加日',
                'play_time': 'プレイ時間',
                'days': '日',
                'day': '日',
                'hours': '時間',
                'hour': '時間',
                'minutes': '分',
                'minute': '分',
                'never_opened': 'まだ開かれていません',
                
                # Splash Screen
                'splash_tagline': 'ゲームライブラリ  •  マップ  •  ガイド',
                'splash_subtitle': 'マップライブラリマネージャー',
                'splash_version': 'バージョン 3.0',
                'splash_initializing': '起動中...',
                'splash_init_components': '🔧 コンポーネントの初期化...',
                'splash_loading_config': '⚙️ 設定の読み込み...',
                'splash_verifying_files': '📁 ファイルの確認...',
                'splash_setting_interface': '🎨 インターフェースの設定...',
                'splash_preparing_library': '🎮 ゲームライブラリの準備...',
                'splash_indexing_content': '🔍 コンテンツのインデックス作成...',
                'splash_final_touches': '✨ 最後の仕上げを適用...',
                'splash_ready': '🚀 起動準備完了!',
                
                # キーボードショートカット
                'keybinds_label': 'キーボードショートカット',
                'keybinds_desc': 'キーボードショートカットをカスタマイズする',
                'command': 'コマンド',
                'add_game_label': 'ゲーム追加',
                'search_label': '検索',
                'clear_search_label': '検索をクリア',
                'refresh_label': '更新',
                'favorites_label': 'お気に入り',
                'reset': 'デフォルトにリセット',
                'capture_keybind': 'キーの組み合わせを押してください...',
                'capture_cancel': '(キャンセルするにはESCを押してください)',
                'capture_button': '🎹 キャプチャ'
            },
            
            'zh': {
                # Menus
                'file_menu': '文件',
                'view_menu': '查看',
                'help_menu': '帮助',
                'config_menu': '设置',
                'about_menu': '关于',
                'exit_menu': '退出',
                'search_menu': '搜索',
                'toggle_favorites_menu': '切换收藏夹',
                'refresh_list_menu': '刷新列表',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': '添加游戏',
                'export_games': '导出游戏',
                'import_games': '导入游戏',
                'export_game_dialog_title': '选择要导出的游戏',
                'import_game_dialog_title': '导入游戏',

                'export_button': '导出所选',
                'import_button': '导入游戏',
                'exported_successfully': '游戏导出成功',
                'imported_successfully': '游戏导入成功',
                'export_failed': '导出游戏失败',
                'import_failed': '导入游戏失败',
                'add_game_button': '+ 添加游戏',
                'library': '游戏库',
                'games_count': '游戏',
                'game_singular': '游戏',
                'no_games': '您的游戏库中没有游戏。\n请前往"文件"→"添加游戏"开始。',
                'no_favorites': '你还没有收藏的游戏。',
                'no_games_search': '未找到与您的搜索相符的游戏',
                'no_recent_games': '打开过的游戏会显示在这里。',
                'search_placeholder': '搜索游戏... (收藏夹始终可见)',
                
                # Add game form
                'add_game_title': '添加新游戏',
                'game_name': '游戏名称:',
                'game_image': '游戏图像:',
                'browse_image': '浏览图像',
                'map_content': '地图路径/URL:',
                'map_type_label': '地图类型:',
                'map_type_image': '图像',
                'map_type_web': '网站',
                'browse_map': '浏览',
                'save': '保存',
                'cancel': '取消',
                'save_changes': '保存更改',
                
                # Messages
                'error': '错误',
                'success': '成功',
                'game_saved': '游戏保存成功',
                'fill_required_fields': '请填写所有必填字段',
                'invalid_image': '无效的图像格式',
                'invalid_url': '无效的URL',
                'select_image': '选择图像',
                'select_map': '选择地图',
                'image_files': '图像文件',
                'all_files': '所有文件',
                
                # About window
                'about_title': '关于Avilon',
                'about_description': 'Avilon是一个由单人设计和编程的程序，您可以在其中管理您最喜欢的游戏地图',
                'close': '关闭',
                
                # Configuration
                'config_title': '设置',
                'language_label': '语言:',
                'theme_label': '主题:',
                'spanish': 'Español',
                'english': 'English',
                'french': 'Français',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'Português',
                'dutch': 'Nederlands',
                'russian': 'Русский',
                'japanese': '日本語',
                'chinese': '中文',
                'theme_slate': '板岩',
                'theme_dark': '深色',
                'theme_light': '浅色',
                'theme_blue': '蓝色',
                'theme_green': '绿色',
                'theme_cyberpunk': '赛博朋克',
                'theme_gaming_rgb': '游戏RGB',
                'theme_retro_arcade': '复古街机',
                'theme_midnight_gaming': '午夜游戏',
                'theme_esports': '电子竞技',
                'apply': '应用',
                'config_saved': '设置保存成功',
                
                # Game buttons
                'view_map': '查看地图',
                'edit': '编辑',
                'delete': '删除',
                'delete_game': '删除游戏',
                'edit_game': '编辑游戏',
                'no_image': '无图像',
                'confirm_delete': '您确定要删除这个游戏吗？',
                'confirm_title': '确认',
                'yes': '是',
                'no': '否',
                
                # Edit game
                'edit_game_title': '编辑游戏',
                
                # Window titles
                'map_window_title': '地图',
                
                # Favorites system
                'all_games': '全部',
                'favorites': '收藏夹',
                'recent': '最近',
                'add_to_favorites': '添加到收藏夹',
                'remove_from_favorites': '从收藏夹中删除',
                
                # Startup
                'startup_label': '随系统启动:',
                'startup_enabled': '程序已配置为随系统启动',
                'startup_disabled': '程序已从自动启动中删除',
                'startup_error': '配置自动启动时出错',
                
                # Configuration sections
                'config_section_language_desc': '选择界面语言',
                'config_section_theme_desc': '选择应用的视觉主题',
                'config_section_startup_desc': '随系统自动启动Avilon',
                'startup_auto_start_label': '随系统自动启动',
                
                # User Guide
                'how_to_use_menu': '如何使用',
                'tutorial_menu': '查看教程',
                'report_bug_menu': '报告错误',
                'user_guide_title': '用户指南 - 如何使用 Avilon',
                'guide_tab_games': '游戏',
                'guide_tab_maps': '地图',
                'guide_tab_features': '功能',
                'guide_tab_tips': '提示',
                
                # Games tab
                'guide_games_title': '🎮 游戏管理',
                'guide_games_add_title': '📝 如何添加游戏:',
                'guide_games_add_content': '''1. 转到菜单"文件"→"添加游戏"
2. 输入游戏名称
3. 输入游戏描述(可选)
4. 选择一张图像(必需):
   • 支持的格式: PNG、JPG、JPEG、BMP、GIF
   • 建议: 250x280 像素
5. 配置地图(请参见"地图"标签页)
6. 单击"保存"''',
                'guide_games_manage_title': '⚙️ 管理现有游戏:',
                'guide_games_manage_content': '''• 单击 ⭐ 标记/取消标记为收藏
• "编辑"来修改游戏数据
• "删除"从库中移除游戏''',
                
                # Maps tab
                'guide_maps_title': '🗺️ 地图配置',
                'guide_maps_types_title': '📋 支持的地图类型:',
                'guide_maps_image_title': '🖼️ 图像地图:',
                'guide_maps_image_content': '''• 格式: PNG、JPG、JPEG、BMP、GIF
• 功能: 缩放、平移、全屏显示
• 理想用于静态游戏地图''',
                'guide_maps_web_title': '🌐 网络地图(iframe):',
                'guide_maps_web_content': '''• 任何有效的 URL(http:// 或 https://)
• 交互式在线地图
• 游戏 Wiki、网络指南等
• 在集成窗口中打开''',
                
                # Features tab
                'guide_features_title': '✨ 主要功能',
                'guide_features_search_title': '🔍 搜索系统:',
                'guide_features_search_content': '''• 按游戏名称搜索
• 收藏夹始终保持可见
• 筛选: "全部"和"收藏夹"''',
                'guide_features_themes_title': '🎨 主题和自定义:',
                'guide_features_themes_content': '''• 5 个可用主题: 板岩、深色、浅色、蓝色、绿色
• 支持多种语言
• 设置自动保存''',
                'guide_features_startup_title': '🚀 自动启动:',
                'guide_features_startup_content': '''• 可从设置配置
• 如果启用，将随系统启动
• 轻松启用/禁用''',
                
                # Tips tab
                'guide_tips_title': '💡 提示和技巧',
                'guide_tips_organization_title': '📚 组织:',
                'guide_tips_organization_content': '''• 为游戏使用描述性名称
• 将常用游戏标记为收藏
• 按类别组织图像''',
                'guide_tips_images_title': '🖼️ 图像最佳实践:',
                'guide_tips_images_content': '''• 使用高分辨率图像
• 推荐尺寸: 250x280 像素
• 避免非常大的图像 (>5MB)''',
                'guide_tips_maps_title': '🗺️ 地图提示:',
                'guide_tips_maps_content': '''• 对于网络地图,请验证 URL 是否可访问
• 大型图像地图可以缩放
• 尽可能使用交互式地图''',
                
                # Keyboard Shortcuts tab
                'guide_tab_shortcuts': '键盘快捷键',
                'guide_shortcuts_title': '⌨️ 键盘快捷键',
                'guide_shortcuts_subtitle': '使用这些有用的键盘快捷键加快您的工作速度',
                'guide_shortcuts_games_title': '🎮 游戏管理',
                'guide_shortcuts_games_content': '''• Ctrl + N - 添加新游戏
• Ctrl + F - 搜索游戏
• Escape - 清除搜索
• F5 - 刷新游戏列表
• Ctrl + Shift + F - 切换收藏夹视图''',
                'guide_shortcuts_navigation_title': '🧭 导航和设置',
                'guide_shortcuts_navigation_content': '''• F1 - 打开用户指南
• Ctrl + Shift + P - 打开设置
• Ctrl + Q - 退出应用程序''',
                'guide_shortcuts_tips_title': '💡 快捷键提示',
                'guide_shortcuts_tips_content': '''• 快捷键在应用程序的任何地方都可以使用
• 您可以使用大写和小写
• Escape 键始终清除当前搜索
• F1 是您的快速帮助键''',
                'guide_shortcuts_workflow_title': '⚡ 快速工作流程',
                'guide_shortcuts_workflow_content': '可以在设置窗口中自定义键盘快捷键。从菜单打开设置窗口或按 Ctrl + Shift + P 根据您的偏好修改快捷键。',
                'guide_shortcuts_open_settings': '打开设置',
                
                # Guide subtitle
                'guide_subtitle': '您需要了解的有关使用 Avilon 的所有信息',
                
                # 游戏呈现中的目标
                'objectives': '目标',
                'no_objectives': '没有目标',
                'new_objective': '新目标',
                'write_objective': '写下目标:',
                'add_objective': '添加目标',
                
                # 游戏描述和元数据
                'game_description': '描述（可选）:',
                'description': '描述',
                'added_date': '添加日期',
                'play_time': '游戏时间',
                'days': '天',
                'day': '天',
                'hours': '小时',
                'hour': '小时',
                'minutes': '分钟',
                'minute': '分钟',
                'never_opened': '从未打开',
                
                # Splash Screen
                'splash_tagline': '游戏库  •  地图  •  指南',
                'splash_subtitle': '地图库管理器',
                'splash_version': '版本 3.0',
                'splash_initializing': '正在启动...',
                'splash_init_components': '🔧 初始化组件...',
                'splash_loading_config': '⚙️ 加载配置...',
                'splash_verifying_files': '📁 验证文件...',
                'splash_setting_interface': '🎨 设置界面...',
                'splash_preparing_library': '🎮 准备游戏库...',
                'splash_indexing_content': '🔍 索引内容...',
                'splash_final_touches': '✨ 应用最后的调整...',
                'splash_ready': '🚀 准备启动！',
                
                # 键盘快捷键
                'keybinds_label': '键盘快捷键',
                'keybinds_desc': '自定义您的键盘快捷键',
                'command': '命令',
                'add_game_label': '添加游戏',
                'search_label': '搜索',
                'clear_search_label': '清除搜索',
                'refresh_label': '刷新',
                'favorites_label': '收藏夹',
                'reset': '恢复默认值',
                'capture_keybind': '按下键盘组合...',
                'capture_cancel': '(按ESC取消)',
                'capture_button': '🎹 捕获'
            }
        }
    
    def load_config(self):
        """Cargar configuración desde archivo"""
        try:
            import json
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config
        except:
            return {'language': 'es', 'theme': 'slate', 'startup': False}  # Configuración por defecto
    
    def save_config(self):
        """Guardar configuración a archivo"""
        try:
            import json
            config = {
                'language': self.current_language,
                'theme': self.current_theme,
                'startup': getattr(self, 'startup_enabled', False),
                'keybinds': getattr(self, 'keybinds', self.default_keybinds.copy()),
                'tutorial_completed': getattr(self, 'tutorial_completed', True)
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_text(self, key):
        """Obtener texto traducido"""
        # Asegurar que las traducciones estén cargadas
        if not hasattr(self, 'translations') or not self.translations:
            self.translations = self.load_translations()
        
        translation = self.translations.get(self.current_language, {}).get(key, None)
        
        # Si no se encuentra la traducción, intentar con el idioma por defecto
        if translation is None:
            translation = self.translations.get('es', {}).get(key, key)
        
        return translation

    def get_tutorial_copy(self):
        """Return first-run onboarding text in the selected UI language."""
        copy = {
            'es': {
                'title': 'Te damos la bienvenida a Avilon',
                'back': 'Atrás', 'next': 'Continuar', 'skip': 'Omitir',
                'finish': 'Empezar a usar Avilon', 'guide': 'Abrir la guía',
                'steps': [
                    ('Tu biblioteca de juegos',
                     'Avilon reúne en un solo lugar los juegos y los recursos que consultas mientras juegas. Añade tus títulos para empezar a organizar tu biblioteca.'),
                    ('Añade tus juegos',
                     'Abre Archivo → Añadir juego. Ponle un nombre, añade una imagen y, si quieres, una descripción. Puedes editar o eliminar cada juego cuando quieras.'),
                    ('Guarda mapas y guías',
                     'Añade un mapa como imagen o como página web. Abre un juego para ver sus recursos y consultar su mapa o guía.'),
                    ('Encuentra lo que buscas',
                     'Usa Todos para ver tu biblioteca, Favoritos para tus juegos destacados y Recientes para volver rápidamente a los juegos que has abierto. También puedes buscar por nombre.'),
                    ('¿Necesitas ayuda?',
                     'Si tienes cualquier duda sobre Avilon, abre la Guía de usuario desde el menú Ayuda. Allí encontrarás instrucciones y consejos para cada función.'),
                ],
            },
            'en': {
                'title': 'Welcome to Avilon',
                'back': 'Back', 'next': 'Continue', 'skip': 'Skip',
                'finish': 'Start using Avilon', 'guide': 'Open the user guide',
                'steps': [
                    ('Your game library',
                     'Avilon brings together the games and resources you use while playing. Add your titles to start organizing your library.'),
                    ('Add your games',
                     'Choose File → Add Game. Enter a name, add an image, and optionally write a description. You can edit or remove a game at any time.'),
                    ('Keep maps and guides close',
                     'Add a map as an image or a web page. Open a game to view its resources and access its map or guide.'),
                    ('Find what you need',
                     'Use All for your library, Favorites for highlighted games, and Recent to return to games you have opened. You can also search by name.'),
                    ('Need a hand?',
                     'If you have any questions about Avilon, open the User Guide from the Help menu. It has instructions and tips for the app.'),
                ],
            },
            'fr': {
                'title': 'Bienvenue dans Avilon',
                'back': 'Retour', 'next': 'Continuer', 'skip': 'Passer',
                'finish': 'Commencer avec Avilon', 'guide': 'Ouvrir le guide',
                'steps': [
                    ('Votre bibliothèque de jeux', 'Avilon rassemble les jeux et ressources que vous utilisez. Ajoutez vos jeux pour organiser votre bibliothèque.'),
                    ('Ajoutez vos jeux', 'Choisissez Fichier → Ajouter un jeu. Saisissez un nom, ajoutez une image et, si vous le souhaitez, une description.'),
                    ('Gardez cartes et guides à portée de main', 'Ajoutez une carte sous forme d’image ou de page web. Ouvrez un jeu pour accéder à sa carte ou à son guide.'),
                    ('Trouvez rapidement vos jeux', 'Utilisez Tous, Favoris et Récents pour parcourir votre bibliothèque. Vous pouvez aussi rechercher un jeu par son nom.'),
                    ('Besoin d’aide ?', 'Pour toute question, ouvrez le Guide utilisateur depuis le menu Aide. Vous y trouverez des explications et des conseils.'),
                ],
            },
            'de': {
                'title': 'Willkommen bei Avilon',
                'back': 'Zurück', 'next': 'Weiter', 'skip': 'Überspringen',
                'finish': 'Avilon starten', 'guide': 'Benutzerhandbuch öffnen',
                'steps': [
                    ('Deine Spielebibliothek', 'Avilon bündelt deine Spiele und hilfreichen Ressourcen. Füge Spiele hinzu, um deine Bibliothek zu organisieren.'),
                    ('Spiele hinzufügen', 'Wähle Datei → Spiel hinzufügen. Vergib einen Namen, füge ein Bild und optional eine Beschreibung hinzu.'),
                    ('Karten und Anleitungen speichern', 'Füge Karten als Bild oder Webseite hinzu. Öffne ein Spiel, um auf seine Karte oder Anleitung zuzugreifen.'),
                    ('Finde deine Spiele schnell', 'Nutze Alle, Favoriten und Zuletzt, um deine Bibliothek zu filtern. Du kannst auch nach Namen suchen.'),
                    ('Brauchst du Hilfe?', 'Bei Fragen öffne das Benutzerhandbuch über das Menü Hilfe. Dort findest du Anleitungen und Tipps.'),
                ],
            },
            'it': {
                'title': 'Benvenuto in Avilon',
                'back': 'Indietro', 'next': 'Continua', 'skip': 'Salta',
                'finish': 'Inizia a usare Avilon', 'guide': 'Apri la guida',
                'steps': [
                    ('La tua raccolta di giochi', 'Avilon riunisce giochi e risorse utili. Aggiungi i tuoi titoli per organizzare la raccolta.'),
                    ('Aggiungi i tuoi giochi', 'Scegli File → Aggiungi gioco. Inserisci un nome, un’immagine e, se vuoi, una descrizione.'),
                    ('Tieni mappe e guide a portata di mano', 'Aggiungi una mappa come immagine o pagina web. Apri un gioco per consultare la mappa o la guida.'),
                    ('Trova subito i tuoi giochi', 'Usa Tutti, Preferiti e Recenti per filtrare la raccolta. Puoi anche cercare per nome.'),
                    ('Ti serve aiuto?', 'Per qualsiasi dubbio, apri la Guida utente dal menu Aiuto. Troverai istruzioni e suggerimenti.'),
                ],
            },
            'pt': {
                'title': 'Boas-vindas ao Avilon',
                'back': 'Voltar', 'next': 'Continuar', 'skip': 'Ignorar',
                'finish': 'Começar a usar o Avilon', 'guide': 'Abrir o guia',
                'steps': [
                    ('A sua biblioteca de jogos', 'O Avilon reúne os jogos e recursos que usa enquanto joga. Adicione títulos para organizar a biblioteca.'),
                    ('Adicione os seus jogos', 'Escolha Arquivo → Adicionar jogo. Insira um nome, uma imagem e, se quiser, uma descrição.'),
                    ('Guarde mapas e guias', 'Adicione um mapa como imagem ou página web. Abra um jogo para consultar o mapa ou guia.'),
                    ('Encontre os seus jogos', 'Use Todos, Favoritos e Recentes para filtrar a biblioteca. Também pode pesquisar pelo nome.'),
                    ('Precisa de ajuda?', 'Se tiver dúvidas, abra o Guia do utilizador no menu Ajuda. Encontrará instruções e sugestões.'),
                ],
            },
            'nl': {
                'title': 'Welkom bij Avilon',
                'back': 'Terug', 'next': 'Verder', 'skip': 'Overslaan',
                'finish': 'Avilon gebruiken', 'guide': 'Gebruikersgids openen',
                'steps': [
                    ('Je gamebibliotheek', 'Avilon verzamelt je games en handige bronnen. Voeg games toe om je bibliotheek te organiseren.'),
                    ('Voeg je games toe', 'Kies Bestand → Game toevoegen. Vul een naam in, voeg een afbeelding toe en eventueel een beschrijving.'),
                    ('Bewaar kaarten en gidsen', 'Voeg een kaart toe als afbeelding of webpagina. Open een game om de kaart of gids te bekijken.'),
                    ('Vind je games snel terug', 'Gebruik Alle, Favorieten en Recent om je bibliotheek te filteren. Zoeken op naam kan ook.'),
                    ('Hulp nodig?', 'Open bij vragen de Gebruikersgids via het menu Help. Daar vind je uitleg en tips.'),
                ],
            },
            'ru': {
                'title': 'Добро пожаловать в Avilon',
                'back': 'Назад', 'next': 'Далее', 'skip': 'Пропустить',
                'finish': 'Начать работу', 'guide': 'Открыть руководство',
                'steps': [
                    ('Ваша игровая библиотека', 'Avilon объединяет игры и полезные материалы. Добавьте игры, чтобы упорядочить библиотеку.'),
                    ('Добавьте игры', 'Выберите Файл → Добавить игру. Укажите название, изображение и при желании описание.'),
                    ('Сохраняйте карты и руководства', 'Добавьте карту как изображение или веб-страницу. Откройте игру, чтобы посмотреть её материалы.'),
                    ('Быстро находите игры', 'Используйте Все, Избранное и Недавние для фильтрации библиотеки. Также доступен поиск по названию.'),
                    ('Нужна помощь?', 'Откройте Руководство пользователя в меню Справка. Там есть инструкции и советы.'),
                ],
            },
            'ja': {
                'title': 'Avilon へようこそ',
                'back': '戻る', 'next': '次へ', 'skip': 'スキップ',
                'finish': 'Avilon を使い始める', 'guide': 'ユーザーガイドを開く',
                'steps': [
                    ('ゲームライブラリ', 'Avilon ではゲームと便利な情報をまとめて管理できます。まずゲームを追加しましょう。'),
                    ('ゲームを追加', '「ファイル」→「ゲームを追加」を選び、名前と画像を設定します。説明は任意です。'),
                    ('マップやガイドを保存', '画像またはウェブページとしてマップを追加できます。ゲームを開くと関連情報を確認できます。'),
                    ('ゲームをすばやく検索', '「すべて」「お気に入り」「最近」を使って表示を切り替えたり、名前で検索したりできます。'),
                    ('困ったときは', '使い方で迷ったら「ヘルプ」メニューのユーザーガイドをご覧ください。各機能の説明があります。'),
                ],
            },
            'zh': {
                'title': '欢迎使用 Avilon',
                'back': '上一步', 'next': '继续', 'skip': '跳过',
                'finish': '开始使用 Avilon', 'guide': '打开用户指南',
                'steps': [
                    ('你的游戏库', 'Avilon 将游戏和常用资源集中管理。添加游戏即可开始整理你的游戏库。'),
                    ('添加游戏', '选择“文件”→“添加游戏”，填写名称并添加图片；描述为可选项。'),
                    ('保存地图和指南', '地图可以图片或网页形式添加。打开游戏即可查看相关地图和指南。'),
                    ('快速找到游戏', '使用“全部”“收藏”和“最近”筛选游戏，也可以按名称搜索。'),
                    ('需要帮助？', '如有疑问，请从“帮助”菜单打开用户指南，查看功能说明和使用技巧。'),
                ],
            },
        }
        return copy.get(self.current_language, copy['en'])

    def show_first_run_tutorial(self, force=False):
        """Present the onboarding wizard on first launch or when requested."""
        if (self.tutorial_completed and not force) or not self.root.winfo_exists():
            return

        copy = self.get_tutorial_copy()
        pages = copy['steps']
        current_step = [0]
        dialog = tk.Toplevel(self.root)
        dialog.title(copy['title'])
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.resizable(True, True)
        dialog.transient(self.root)
        self.apply_window_icon(dialog)
        _, _, dialog_width, dialog_height = center_window_on_primary_monitor(dialog, 760, 640)
        dialog.minsize(min(640, dialog_width), min(540, dialog_height))

        shell = tk.Frame(dialog, bg=self.colors['bg_dark'])
        shell.pack(fill=tk.BOTH, expand=True, padx=34, pady=24)

        brand = tk.Label(
            shell, text='AVILON', bg=self.colors['bg_dark'],
            fg=self.colors['accent'], font=(self.ui_font_family, 11, 'bold'),
        )
        brand.pack(anchor=tk.W)
        title = tk.Label(
            shell, text=copy['title'], bg=self.colors['bg_dark'],
            fg=self.colors['text_primary'], font=(self.ui_font_family, 22, 'bold'),
            anchor=tk.W, justify=tk.LEFT,
        )
        title.pack(anchor=tk.W, pady=(7, 4))
        step_label = tk.Label(
            shell, bg=self.colors['bg_dark'], fg=self.colors['text_muted'],
            font=(self.ui_font_family, 9),
        )
        step_label.pack(anchor=tk.W, pady=(0, 20))

        card = tk.Frame(shell, bg=self.colors['bg_light'], padx=26, pady=24)
        card.pack(fill=tk.BOTH, expand=True)
        icon = tk.Label(
            card, bg=self.colors['bg_light'], fg=self.colors['accent'],
            font=(self.ui_font_family, 28, 'bold'),
        )
        icon.pack(anchor=tk.W)
        page_title = tk.Label(
            card, bg=self.colors['bg_light'], fg=self.colors['text_primary'],
            font=(self.ui_font_family, 16, 'bold'), anchor=tk.W, justify=tk.LEFT,
        )
        page_title.pack(anchor=tk.W, pady=(12, 8))
        page_body = tk.Label(
            card, bg=self.colors['bg_light'], fg=self.colors['text_secondary'],
            font=(self.ui_font_family, 11), anchor=tk.W, justify=tk.LEFT,
            wraplength=max(360, dialog_width - 150),
        )
        page_body.pack(anchor=tk.W, fill=tk.X)

        footer = tk.Frame(shell, bg=self.colors['bg_dark'])
        footer.pack(fill=tk.X, pady=(18, 0))
        back_button = tk.Button(
            footer, text=copy['back'], command=lambda: change_step(-1),
            bg=self.colors['bg_light'], fg=self.colors['text_primary'],
            activebackground=self.colors['bg_medium'], activeforeground=self.colors['text_primary'],
            relief='flat', bd=0, highlightthickness=0, padx=16, pady=9,
            font=(self.ui_font_family, 10, 'bold'), cursor='hand2',
        )
        back_button.pack(side=tk.LEFT)
        skip_button = tk.Button(
            footer, text=copy['skip'], command=lambda: finish_tutorial(),
            bg=self.colors['bg_dark'], fg=self.colors['text_muted'],
            activebackground=self.colors['bg_dark'], activeforeground=self.colors['text_primary'],
            relief='flat', bd=0, highlightthickness=0, padx=16, pady=9,
            font=(self.ui_font_family, 10), cursor='hand2',
        )
        skip_button.pack(side=tk.RIGHT, padx=(8, 0))
        next_button = tk.Button(
            footer, command=lambda: change_step(1),
            bg=self.colors['accent'], fg=self.colors['bg_dark'],
            activebackground=self.colors['accent_hover'], activeforeground=self.colors['bg_dark'],
            relief='flat', bd=0, highlightthickness=0, padx=18, pady=9,
            font=(self.ui_font_family, 10, 'bold'), cursor='hand2',
        )
        next_button.pack(side=tk.RIGHT)

        def finish_tutorial(open_guide=False):
            self.tutorial_completed = True
            self.save_config()
            try:
                if dialog.grab_current() == dialog:
                    dialog.grab_release()
                dialog.destroy()
            except tk.TclError:
                pass
            if open_guide and self.root.winfo_exists():
                self.root.after_idle(self.show_user_guide_dialog)

        def change_step(delta):
            new_step = current_step[0] + delta
            if new_step < 0:
                return
            if new_step >= len(pages):
                finish_tutorial()
                return
            current_step[0] = new_step
            render_step()

        def render_step():
            index = current_step[0]
            page_title.configure(text=pages[index][0])
            page_body.configure(text=pages[index][1])
            icon.configure(text=f'{index + 1:02d}')
            step_label.configure(
                text=f"{index + 1} / {len(pages)}"
            )
            back_button.configure(state=tk.NORMAL if index else tk.DISABLED)
            skip_button.pack_forget()
            next_button.pack_forget()
            if index == len(pages) - 1:
                next_button.configure(
                    text=copy['guide'],
                    command=lambda: finish_tutorial(open_guide=True),
                )
                next_button.pack(side=tk.RIGHT)
            else:
                skip_button.pack(side=tk.RIGHT, padx=(8, 0))
                next_button.configure(text=copy['next'], command=lambda: change_step(1))
                next_button.pack(side=tk.RIGHT)

        dialog.protocol('WM_DELETE_WINDOW', finish_tutorial)
        dialog.bind('<Escape>', lambda event: finish_tutorial())
        dialog.bind('<Left>', lambda event: change_step(-1))
        dialog.bind('<Right>', lambda event: change_step(1))
        dialog.bind(
            '<Configure>',
            lambda event: page_body.configure(
                wraplength=max(360, event.width - 150)
            ) if event.widget is dialog else None,
            add='+',
        )
        render_step()
        dialog.wait_visibility()
        dialog.grab_set()
        dialog.focus_force()
    
    def _get_linux_autostart_file(self):
        config_home = os.environ.get('XDG_CONFIG_HOME', '')
        if not config_home or not os.path.isabs(config_home):
            config_home = os.path.expanduser('~/.config')
        return os.path.join(config_home, 'autostart', 'avilon.desktop')

    def set_startup_registry(self, enable):
        """Configurar el inicio automático en Windows o en el autostart XDG."""
        if sys.platform.startswith('linux'):
            desktop_file = self._get_linux_autostart_file()
            autostart_dir = os.path.dirname(desktop_file)
            try:
                if enable:
                    os.makedirs(autostart_dir, exist_ok=True)
                    if getattr(sys, 'frozen', False):
                        command_parts = [os.path.abspath(sys.executable)]
                    else:
                        launcher = shutil.which('avilon')
                        if launcher:
                            command_parts = [os.path.abspath(launcher)]
                        else:
                            command_parts = [
                                os.path.abspath(sys.executable),
                                os.path.abspath(__file__),
                            ]
                    command = ' '.join(desktop_entry_quote(part) for part in command_parts)
                    desktop_file_contents = (
                            '[Desktop Entry]\n'
                            'Type=Application\n'
                            'Name=AVILON\n'
                            'Comment=Game library, maps, and guides\n'
                            f'Exec={command}\n'
                            f'TryExec={desktop_entry_quote(command_parts[0])}\n'
                            'Terminal=false\n'
                            'StartupNotify=false\n'
                            'Hidden=false\n'
                            'X-GNOME-Autostart-enabled=true\n'
                        )
                    temporary_file = desktop_file + '.tmp'
                    try:
                        with open(temporary_file, 'w', encoding='utf-8') as desktop:
                            desktop.write(desktop_file_contents)
                        os.replace(temporary_file, desktop_file)
                    finally:
                        if os.path.exists(temporary_file):
                            os.remove(temporary_file)
                else:
                    try:
                        os.remove(desktop_file)
                    except FileNotFoundError:
                        pass
                self.startup_enabled = enable
                return True
            except OSError as e:
                print(f"Error al configurar el inicio automático de Linux: {e}")
                return False

        if winreg is None:
            print("El inicio automático no está disponible en este sistema.")
            return False

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "Avilon"
        key = None
        
        try:
            # Obtener la ruta del ejecutable actual
            if getattr(sys, 'frozen', False):
                app_path = subprocess.list2cmdline([os.path.abspath(sys.executable)])
            else:
                app_path = subprocess.list2cmdline([
                    os.path.abspath(sys.executable), os.path.abspath(__file__)
                ])
            
            print(f"Configurando inicio automático: {enable}")
            print(f"Ruta del ejecutable: {app_path}")
            
            # Abrir la clave del registro
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            
            if enable:
                # Agregar entrada al registro
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
                self.startup_enabled = True
                return True
            else:
                try:
                    # Eliminar entrada del registro
                    winreg.DeleteValue(key, app_name)
                    self.startup_enabled = False
                    return True
                except FileNotFoundError:
                    # La entrada no existe, no es un error
                    self.startup_enabled = False
                    return True
                    
        except Exception as e:
            print(f"Error al configurar inicio automático: {e}")
            return False
        finally:
            try:
                winreg.CloseKey(key)
            except:
                pass
    
    def check_startup_status(self):
        """Verificar el inicio automático en Windows o en el autostart XDG."""
        if sys.platform.startswith('linux'):
            desktop_file = self._get_linux_autostart_file()
            self.startup_enabled = False
            try:
                with open(desktop_file, 'r', encoding='utf-8') as desktop:
                    entry = {}
                    for line in desktop:
                        key, separator, value = line.rstrip('\n').partition('=')
                        if separator:
                            entry[key] = value

                command = shlex.split(entry.get('Exec', ''))
                try_exec = shlex.split(entry.get('TryExec', ''))
                if (
                    entry.get('Type') == 'Application'
                    and entry.get('Hidden', 'false').lower() != 'true'
                    and entry.get('X-GNOME-Autostart-enabled', 'true').lower() != 'false'
                    and command
                ):
                    executable = command[0].replace('%%', '%')
                    startup_target = command[1].replace('%%', '%') if len(command) > 1 else None
                    self.startup_enabled = (
                        os.path.isfile(executable) and os.access(executable, os.X_OK)
                        and (
                            not try_exec
                            or (
                                os.path.isfile(try_exec[0].replace('%%', '%'))
                                and os.access(try_exec[0].replace('%%', '%'), os.X_OK)
                            )
                        )
                        and (startup_target is None or os.path.isfile(startup_target))
                    )
            except FileNotFoundError:
                pass
            except (OSError, ValueError) as e:
                print(f"Error al verificar el inicio automático de Linux: {e}")
            return self.startup_enabled

        if winreg is None:
            return False
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "Avilon"
        key = None
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            try:
                value, _ = winreg.QueryValueEx(key, app_name)
                print(f"Entrada encontrada en registro: {value}")
                # The Run value may contain both a quoted executable and script path.
                if value.startswith('"'):
                    closing_quote = value.find('"', 1)
                    exe_path = value[1:closing_quote] if closing_quote > 1 else value
                else:
                    exe_path = value.split(maxsplit=1)[0]
                if os.path.exists(exe_path):
                    print(f"Ejecutable confirmado en: {exe_path}")
                    return True
                else:
                    print(f"ADVERTENCIA: Ejecutable no encontrado en: {exe_path}")
                    # Limpiar entrada inválida del registro
                    try:
                        winreg.DeleteValue(key, app_name)
                        print("Entrada inválida eliminada del registro")
                    except:
                        pass
                    return False
            except FileNotFoundError:
                print("No hay entrada en el registro para inicio automático")
                return False
        except Exception as e:
            print(f"Error al verificar estado de inicio automático: {e}")
            return False
        finally:
            try:
                winreg.CloseKey(key)
            except:
                pass
    
    def load_themes(self):
        """Cargar todos los temas disponibles"""
        return {
            'slate': {
                'name': 'Slate',
                'bg_dark': '#0b1020',
                'bg_light': '#151d2e',
                'bg_medium': '#202b40',
                'sidebar': '#0f1728',
                'accent': '#59d8e8',
                'accent_hover': '#3fc2d4',
                'text': '#edf3fc',
                'text_primary': '#f4f7fc',
                'text_secondary': '#c3cede',
                'text_muted': '#91a1b7',
                'success': '#42d6a4',
                'danger': '#f06b78',
                'warning': '#f1a85b'
            },
            'dark': {
                'name': 'Dark',
                'bg_dark': '#1a1a1a',
                'bg_light': '#2a2a2a',
                'bg_medium': '#3a3a3a',
                'sidebar': '#1a1a1a',
                'accent': '#4a9eff',
                'accent_hover': '#3a8eef',
                'text': '#ffffff',
                'text_primary': '#ffffff',
                'text_secondary': '#cccccc',
                'text_muted': '#cccccc',
                'success': '#00aa00',
                'danger': '#ff4444',
                'warning': '#ffaa00'
            },
            'light': {
                'name': 'Light',
                'bg_dark': '#f5f5f5',
                'bg_light': '#ffffff',
                'bg_medium': '#e5e5e5',
                'sidebar': '#e8e8e8',
                'accent': '#0066cc',
                'accent_hover': '#0055bb',
                'text': '#333333',
                'text_primary': '#333333',
                'text_secondary': '#666666',
                'text_muted': '#666666',
                'success': '#008800',
                'danger': '#cc0000',
                'warning': '#cc8800'
            },
            'blue': {
                'name': 'Blue',
                'bg_dark': '#1e3a8a',
                'bg_light': '#3b82f6',
                'bg_medium': '#2563eb',
                'sidebar': '#1e3a8a',
                'accent': '#60a5fa',
                'accent_hover': '#4f95f9',
                'text': '#ffffff',
                'text_primary': '#ffffff',
                'text_secondary': '#bfdbfe',
                'text_muted': '#bfdbfe',
                'success': '#10b981',
                'danger': '#ef4444',
                'warning': '#f59e0b'
            },
            'green': {
                'name': 'Green',
                'bg_dark': '#064e3b',
                'bg_light': '#059669',
                'bg_medium': '#047857',
                'sidebar': '#064e3b',
                'accent': '#34d399',
                'accent_hover': '#22c785',
                'text': '#ffffff',
                'text_primary': '#ffffff',
                'text_secondary': '#a7f3d0',
                'text_muted': '#a7f3d0',
                'success': '#10b981',
                'danger': '#ef4444',
                'warning': '#f59e0b'
            },
            'cyberpunk': {
                'name': 'Cyberpunk',
                'bg_dark': '#0a0a0f',
                'bg_light': '#1a1a2e',
                'bg_medium': '#16213e',
                'sidebar': '#0f0f1a',
                'accent': '#ff00ff',
                'accent_hover': '#e600e6',
                'text': "#FFFFFF",
                'text_primary': "#FFFFFF",
                'text_secondary': '#cccccc',
                'text_muted': '#aaaaaa',
                'success': '#00ff88',
                'danger': '#ff4466',
                'warning': '#ffdd00',
                'animated': True,
                'pulse_color': '#ff00ff',
                'glow_effect': True
            },
            'gaming_rgb': {
                'name': 'Gaming RGB',
                'bg_dark': '#0d1117',
                'bg_light': '#21262d',
                'bg_medium': '#30363d',
                'sidebar': '#0d1117',
                'accent': '#ff6b35',
                'accent_hover': '#f92672',
                'text': '#ffffff',
                'text_primary': '#ffffff',
                'text_secondary': '#cccccc',
                'text_muted': '#999999',
                'success': '#50fa7b',
                'danger': '#ff5555',
                'warning': '#ffb86c',
                'animated': True,
                'rainbow_cycle': True,
                'rgb_colors': ['#ff0000', '#ff8800', '#ffff00', '#00ff00', '#0088ff', '#0000ff', '#8800ff']
            },
            'retro_arcade': {
                'name': 'Retro Arcade',
                'bg_dark': '#1a0033',
                'bg_light': '#330066',
                'bg_medium': '#4d0099',
                'sidebar': '#1a0033',
                'accent': '#ffff00',
                'accent_hover': '#e6e600',
                'text': '#ffffff',
                'text_primary': '#ffffff',
                'text_secondary': '#dddddd',
                'text_muted': '#bbbbbb',
                'success': '#00ff44',
                'danger': '#ff4444',
                'warning': '#ffaa00',
                'animated': True,
                'neon_glow': True,
                'arcade_colors': ['#ffff00', '#ff9900', '#ff0088']
            },
            'midnight_gaming': {
                'name': 'Midnight Gaming',
                'bg_dark': '#000000',
                'bg_light': '#1c1c1c',
                'bg_medium': '#2d2d2d',
                'sidebar': '#0a0a0a',
                'accent': '#00d4ff',
                'accent_hover': '#00bfef',
                'text': '#ffffff',
                'text_primary': '#ffffff',
                'text_secondary': '#cccccc',
                'text_muted': '#999999',
                'success': '#00cc66',
                'danger': '#ff4466',
                'warning': '#ffaa00',
                'animated': True,
                'starfield_effect': True,
                'midnight_colors': ['#00d4ff', '#0088ff', '#004499']
            },
            'esports': {
                'name': 'Esports',
                'bg_dark': '#0f1419',
                'bg_light': '#1e2328',
                'bg_medium': '#282c34',
                'sidebar': '#0f1419',
                'accent': '#c9aa71',
                'accent_hover': '#b8965a',
                'text': '#ffffff',
                'text_primary': '#ffffff',
                'text_secondary': '#cccccc',
                'text_muted': '#999999',
                'success': '#0ec879',
                'danger': '#e74c3c',
                'warning': '#f39c12',
                'animated': True,
                'competitive_glow': True,
                'esports_colors': ['#c9aa71', '#d4af37', '#ffd700']
            }
        }
    
    def start_theme_animations(self):
        """Iniciar animaciones específicas del tema"""
        if self.colors.get('animated', False):
            self.animation_running = True
            if self.colors.get('rainbow_cycle', False):
                self.animate_rgb_cycle()
            elif self.colors.get('pulse_color', False):
                self.animate_pulse_effect()
            elif self.colors.get('neon_glow', False):
                self.animate_neon_glow()
            elif self.colors.get('starfield_effect', False):
                self.animate_starfield()
            elif self.colors.get('competitive_glow', False):
                self.animate_competitive_glow()
    
    def stop_theme_animations(self):
        """Detener todas las animaciones del tema"""
        self.animation_running = False
        if self.animation_after_id:
            self.root.after_cancel(self.animation_after_id)
            self.animation_after_id = None
    
    def animate_rgb_cycle(self):
        """Animación RGB cíclica para Gaming RGB"""
        if not self.animation_running:
            return
            
        rgb_colors = self.colors.get('rgb_colors', ['#ff0000', '#00ff00', '#0000ff'])
        current_color = rgb_colors[self.rgb_index % len(rgb_colors)]
        
        # Aplicar color actual a elementos específicos
        try:
            # Actualizar color de acento dinámicamente
            if hasattr(self, 'search_bar_frame'):
                self.search_bar_frame.config(highlightcolor=current_color)
            
            # Actualizar botones de filtro si existen
            if hasattr(self, 'filter_all_button'):
                self.filter_all_button.config(fg=current_color)
            if hasattr(self, 'filter_favorites_button'):
                self.filter_favorites_button.config(fg=current_color)
                
        except:
            pass
        
        self.rgb_index += 1
        self.animation_after_id = self.root.after(500, self.animate_rgb_cycle)
    
    def animate_pulse_effect(self):
        """Efecto de pulso para Cyberpunk"""
        if not self.animation_running:
            return
            
        import math
        self.pulse_alpha = (math.sin(self.pulse_alpha + 0.2) + 1) / 2
        pulse_color = self.colors.get('pulse_color', '#ff00ff')
        
        # Aplicar efecto de pulso
        try:
            if hasattr(self, 'title_label'):
                alpha = int(self.pulse_alpha * 255)
                # Crear efecto de resplandor variando la intensidad
                glow_color = f"#{hex(min(255, int(self.pulse_alpha * 255)))[2:].zfill(2)}00{hex(min(255, int(self.pulse_alpha * 255)))[2:].zfill(2)}"
                
        except:
            pass
        
        self.animation_after_id = self.root.after(100, self.animate_pulse_effect)
    
    def animate_neon_glow(self):
        """Efecto neón para Retro Arcade"""
        if not self.animation_running:
            return
            
        import math
        self.glow_intensity = (math.sin(self.glow_intensity + 0.3) + 1) / 2
        arcade_colors = self.colors.get('arcade_colors', ['#ffff00', '#ff9900', '#ff0088'])
        current_color = arcade_colors[int(self.glow_intensity * len(arcade_colors)) % len(arcade_colors)]
        
        # Aplicar efecto neón
        try:
            if hasattr(self, 'library_label'):
                self.library_label.config(fg=current_color)
        except:
            pass
        
        self.animation_after_id = self.root.after(200, self.animate_neon_glow)
    
    def animate_starfield(self):
        """Efecto de campo de estrellas para Midnight Gaming"""
        if not self.animation_running:
            return
            
        midnight_colors = self.colors.get('midnight_colors', ['#00d4ff', '#0088ff', '#004499'])
        import random
        current_color = random.choice(midnight_colors)
        
        # Crear efecto sutil de parpadeo
        try:
            if hasattr(self, 'games_count_label'):
                if random.random() > 0.7:  # 30% chance de cambio
                    self.games_count_label.config(fg=current_color)
        except:
            pass
        
        self.animation_after_id = self.root.after(1000, self.animate_starfield)
    
    def animate_competitive_glow(self):
        """Efecto de resplandor competitivo para Esports"""
        if not self.animation_running:
            return
            
        import math
        glow_cycle = (math.sin(self.glow_intensity + 0.15) + 1) / 2
        esports_colors = self.colors.get('esports_colors', ['#c9aa71', '#d4af37', '#ffd700'])
        color_index = int(glow_cycle * len(esports_colors)) % len(esports_colors)
        current_color = esports_colors[color_index]
        
        # Aplicar resplandor dorado sutil
        try:
            if hasattr(self, 'search_entry'):
                if glow_cycle > 0.5:
                    self.search_entry.config(insertbackground=current_color)
        except:
            pass
        
        self.glow_intensity += 0.1
        self.animation_after_id = self.root.after(300, self.animate_competitive_glow)
    
    def create_menu_bar(self):
        """Crear barra de menú"""
        self.menubar = tk.Menu(self.root, tearoff=0)
        self.root.config(menu=self.menubar)
        self._apply_menu_colors()
        
        # Menú Archivo
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=self.get_text('file_menu'), menu=file_menu)
        file_menu.add_command(label=self.get_text('add_game'), command=self.show_add_game_dialog, accelerator="Ctrl+N")
        file_menu.add_command(label=self.get_text('export_games'), command=self.show_export_games_dialog)
        file_menu.add_command(label=self.get_text('import_games'), command=self.show_import_games_dialog)
        file_menu.add_command(label=self.get_text('config_menu'), command=self.show_config_dialog, accelerator="Ctrl+Shift+P")
        file_menu.add_command(label=self.get_text('exit_menu'), command=self.on_closing, accelerator="Ctrl+Q")
        
        # Menú Ver
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=self.get_text('view_menu'), menu=view_menu)
        view_menu.add_command(label=self.get_text('search_menu'), command=self.focus_search_bar, accelerator="Ctrl+F")
        view_menu.add_command(label=self.get_text('toggle_favorites_menu'), command=self.toggle_favorites_filter, accelerator="Ctrl+Shift+F")
        view_menu.add_command(label=self.get_text('refresh_list_menu'), command=self.refresh_games_display, accelerator="F5")
        
        # Menú Ayuda
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=self.get_text('help_menu'), menu=help_menu)
        help_menu.add_command(
            label=self.get_text('tutorial_menu'),
            command=lambda: self.show_first_run_tutorial(force=True),
        )
        help_menu.add_command(label=self.get_text('how_to_use_menu'), command=self.show_user_guide_dialog, accelerator="F1")
        help_menu.add_command(label=self.get_text('report_bug_menu'), command=self.open_contact_page)
        help_menu.add_command(label=self.get_text('about_menu'), command=self.show_about_dialog)

        self.app_menus = (self.menubar, file_menu, view_menu, help_menu)
        self._apply_menu_colors()
        if not getattr(self, '_menu_move_binding_set', False):
            self.root.bind('<Configure>', self._close_menus_on_window_move, add='+')
            self._menu_move_binding_set = True

    def _close_menus_on_window_move(self, event):
        if event.widget is not self.root:
            return
        for menu in getattr(self, 'app_menus', ())[1:]:
            try:
                menu.unpost()
            except tk.TclError:
                pass
        try:
            self.menubar.activate(-1)
        except tk.TclError:
            pass

    def _apply_menu_colors(self):
        menu_options = {
            'background': self.colors['bg_light'],
            'foreground': self.colors['text_primary'],
            'activebackground': self.colors['bg_medium'],
            'activeforeground': self.colors['accent'],
            'disabledforeground': self.colors['text_muted'],
            'borderwidth': 0,
            'activeborderwidth': 0,
            'relief': 'flat',
            'font': (self.ui_font_family, 10),
        }
        for menu in getattr(self, 'app_menus', (self.menubar,)):
            try:
                menu.configure(**menu_options)
            except tk.TclError:
                continue
    
    def show_about_dialog(self):
        """Mostrar ventana Acerca de"""
        about_window = tk.Toplevel(self.root)
        about_window.withdraw()  # Ocultar la ventana inicialmente
        about_window.title(self.get_text('about_title'))
        about_window.geometry("520x360")
        about_window.configure(bg=self.colors['bg_dark'])
        about_window.resizable(False, False)
        self.apply_window_icon(about_window)
        
        # Centrar la ventana
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(about_window, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(main_frame, 
                               text="Avilon", 
                               style='Dark.TLabel',
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Descripción
        description_label = ttk.Label(main_frame,
                                     text=self.get_text('about_description'),
                                     style='Dark.TLabel',
                                     font=('Arial', 10),
                                     wraplength=350,
                                     justify='center')
        description_label.pack(pady=(0, 10))
        
        # Versión
        version_label = ttk.Label(main_frame,
                                 text="Versión 3.0",
                                 style='Dark.TLabel',
                                 font=('Arial', 9, 'italic'))
        version_label.pack(pady=(0, 15))
        
        # Logo
        try:
            # Cargar y mostrar el logo
            from PIL import Image, ImageTk, ImageDraw
            if self.icon_path and os.path.exists(self.icon_path):
                logo_image = Image.open(self.icon_path)
                # Redimensionar el logo si es necesario (mantener proporciones)
                logo_image = logo_image.resize((64, 64), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_image)
                
                logo_label = tk.Label(main_frame,
                                     image=logo_photo,
                                     bg=self.colors['bg_dark'])
                logo_label.image = logo_photo  # Mantener referencia
                logo_label.pack(pady=(5, 15))
            
        except ImportError:
            # Si PIL no está disponible, intentar con el método nativo de Tkinter
            try:
                # Tkinter no soporta .ico directamente, pero podemos intentarlo
                logo_photo = tk.PhotoImage(file="logo.ico")
                logo_label = tk.Label(main_frame,
                                     image=logo_photo,
                                     bg=self.colors['bg_dark'])
                logo_label.image = logo_photo
                logo_label.pack(pady=(5, 15))
            except:
                # Si no se puede cargar el logo, mostrar texto alternativo
                logo_text = tk.Label(main_frame,
                                    text="🎮",
                                    bg=self.colors['bg_dark'],
                                    fg=self.colors['text'],
                                    font=('Arial', 24))
                logo_text.pack(pady=(5, 15))
        except:
            # Si hay cualquier otro error al cargar el logo
            logo_text = tk.Label(main_frame,
                                text="🎮",
                                bg=self.colors['bg_dark'],
                                fg=self.colors['text'],
                                font=('Arial', 24))
            logo_text.pack(pady=(5, 15))
        
        # Centrar la ventana en el monitor principal
        about_window.update_idletasks()
        center_window_on_primary_monitor(
            about_window,
            520,
            360,
        )
        
        # Mostrar la ventana una vez que está completamente configurada
        about_window.deiconify()
    
    def open_contact_page(self):
        """Abrir la página de contacto en el navegador predeterminado"""
        try:
            webbrowser.open('https://avilon.es/contacto')
        except Exception as e:
            messagebox.showerror(self.get_text('error'), f"No se pudo abrir la página: {e}")
    
    def show_export_games_dialog(self):
        """Mostrar diálogo para seleccionar juegos a exportar con vista de grid"""
        if not self.games:
            messagebox.showinfo(self.get_text('info'), self.get_text('no_games'))
            return
        
        export_window = tk.Toplevel(self.root)
        export_window.withdraw()
        export_window.title(self.get_text('export_game_dialog_title'))
        export_window.geometry("1500x850")
        export_window.configure(bg=self.colors['bg_dark'])
        export_window.resizable(True, True)
        export_window.minsize(1000, 600)
        self.apply_window_icon(export_window)
        
        export_window.transient(self.root)
        export_window.grab_set()
        
        main_frame = tk.Frame(export_window, bg=self.colors['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        header_frame.pack(fill='x', padx=0, pady=0)
        
        header_bg = tk.Frame(header_frame, bg=self.colors['bg_medium'], height=70)
        header_bg.pack(fill='x')
        header_bg.pack_propagate(False)
        
        title_label = tk.Label(header_bg, 
                              text=self.get_text('export_game_dialog_title'),
                              bg=self.colors['bg_medium'],
                              fg=self.colors['accent'],
                              font=('Segoe UI', 16, 'bold'))
        title_label.pack(anchor='center', pady=15)
        
        games_container = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        games_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(games_container, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox('all'))
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:
                canvas.itemconfig(canvas_window, width=canvas_width)
        
        def on_canvas_configure(e):
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:
                canvas.itemconfig(canvas_window, width=canvas_width)
        
        scrollable_frame.bind('<Configure>', on_frame_configure)
        canvas.bind('<Configure>', on_canvas_configure)
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        
        scroll_active = [True]
        
        def on_canvas_enter(event):
            scroll_active[0] = True
            canvas.focus_set()
        
        def on_canvas_leave(event):
            scroll_active[0] = False
        
        def on_mousewheel(event):
            if scroll_active[0]:
                scrollregion = canvas.cget('scrollregion')
                if scrollregion:
                    try:
                        _, _, _, content_height = map(float, scrollregion.split())
                        canvas_height = canvas.winfo_height()
                        
                        # Solo permitir scroll si el contenido es más alto que el canvas
                        if content_height > canvas_height:
                            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                    except (ValueError, AttributeError):
                        pass
                return "break"
        
        canvas.bind("<Enter>", on_canvas_enter)
        canvas.bind("<Leave>", on_canvas_leave)
        canvas.bind("<MouseWheel>", on_mousewheel)
        
        game_vars = {}
        
        games_grid_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        games_grid_frame.pack(fill='x', padx=10, pady=10)
        
        scrollable_frame.bind("<Enter>", on_canvas_enter)
        scrollable_frame.bind("<Leave>", on_canvas_leave)
        scrollable_frame.bind("<MouseWheel>", on_mousewheel)
        games_grid_frame.bind("<Enter>", on_canvas_enter)
        games_grid_frame.bind("<Leave>", on_canvas_leave)
        games_grid_frame.bind("<MouseWheel>", on_mousewheel)
        
        cols = 8
        for col in range(cols):
            games_grid_frame.grid_columnconfigure(col, weight=1)
        
        for idx, game in enumerate(self.games):
            game_vars[game['name']] = tk.BooleanVar(value=False)
            row = idx // cols
            col = idx % cols
            self.create_export_game_card(games_grid_frame, game, game_vars[game['name']], row, col, scroll_active, canvas, on_mousewheel, on_canvas_enter, on_canvas_leave)
        
        # Configurar las filas del grid
        num_rows = (len(self.games) + cols - 1) // cols if self.games else 0
        for row in range(num_rows):
            games_grid_frame.grid_rowconfigure(row, weight=0)
        
        canvas.pack(side='left', fill='both', expand=True)
        
        buttons_frame = tk.Frame(main_frame, bg=self.colors['bg_medium'])
        buttons_frame.pack(fill='x', padx=0, pady=0, side='bottom')
        
        buttons_container = tk.Frame(buttons_frame, bg=self.colors['bg_medium'])
        buttons_container.pack(fill='x', padx=20, pady=15)
        
        def export_selected():
            selected_games = [g for g in self.games if game_vars[g['name']].get()]
            if not selected_games:
                messagebox.showwarning(self.get_text('warning'), self.get_text('no_games'))
                return
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".zip",
                filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
                initialfile="exported_games.zip"
            )
            
            if file_path:
                try:
                    self.export_games_to_file(selected_games, file_path)
                    messagebox.showinfo(self.get_text('success'), self.get_text('exported_successfully'))
                    export_window.destroy()
                except Exception as e:
                    messagebox.showerror(self.get_text('error'), f"{self.get_text('export_failed')}: {str(e)}")
        
        cancel_btn = tk.Button(buttons_container,
                              text=self.get_text('cancel'),
                              bg=self.colors['bg_medium'],
                              fg=self.colors['text'],
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat',
                              cursor='hand2',
                              padx=35,
                              pady=8,
                              command=export_window.destroy)
        cancel_btn.pack(side='right', padx=(10, 0))
        
        self._add_hover_effect(cancel_btn, self.colors['bg_light'], '#505060')
        
        export_btn = tk.Button(buttons_container,
                              text=self.get_text('export_button'),
                              bg=self.colors['accent'],
                              fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat',
                              cursor='hand2',
                              padx=35,
                              pady=10,
                              command=export_selected)
        export_btn.pack(side='right', padx=5)
        
        self._add_hover_effect(export_btn, self.colors['accent'], self.colors.get('accent_hover', '#5b7fde'))
        
        export_window.update_idletasks()
        x = (export_window.winfo_screenwidth() - 1500) // 2
        y = (export_window.winfo_screenheight() - 850) // 2
        export_window.geometry(f"1500x850+{x}+{y}")
        export_window.deiconify()
    
    def create_export_game_card(self, parent, game, game_var, row, col, scroll_active=None, canvas=None, on_mousewheel=None, on_canvas_enter=None, on_canvas_leave=None):
        """Crear tarjeta de juego para diálogo de exportación con layout grid"""
        card_container = tk.Frame(parent, bg=self.colors['bg_dark'])
        card_container.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        if on_canvas_enter and on_canvas_leave:
            card_container.bind("<Enter>", on_canvas_enter)
            card_container.bind("<Leave>", on_canvas_leave)
        
        if on_mousewheel:
            card_container.bind("<MouseWheel>", on_mousewheel)
        
        card_frame = tk.Frame(card_container, bg=self.colors['bg_light'], highlightthickness=2, relief='flat', bd=0, highlightbackground='#404050')
        card_frame.pack(fill='both', expand=True)
        
        top_frame = tk.Frame(card_frame, bg=self.colors['bg_light'], height=180)
        top_frame.pack(fill='x', padx=0, pady=0)
        top_frame.pack_propagate(False)
        
        try:
            image = Image.open(game['image_path'])
            thumbnail = image.copy()
            thumbnail.thumbnail((170, 170), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(thumbnail)
            
            image_label = tk.Label(top_frame, 
                                  image=photo,
                                  bg=self.colors['bg_dark'],
                                  bd=0,
                                  highlightthickness=0,
                                  cursor='hand2')
            image_label.image = photo
            image_label.pack(fill='both', expand=True, padx=8, pady=8)
        except Exception as e:
            placeholder = tk.Label(top_frame,
                                  text="🎮",
                                  bg=self.colors['bg_light'],
                                  fg=self.colors['text_muted'],
                                  font=('Segoe UI', 60),
                                  cursor='hand2')
            placeholder.pack(fill='both', expand=True, padx=8, pady=8)
            image_label = placeholder
        
        content_frame = tk.Frame(card_frame, bg=self.colors['bg_light'])
        content_frame.pack(fill='both', expand=True, padx=12, pady=10)
        
        checkbox = tk.Checkbutton(content_frame,
                                 variable=game_var,
                                 bg=self.colors['bg_light'],
                                 fg=self.colors['text'],
                                 activebackground=self.colors['bg_light'],
                                 activeforeground=self.colors['text'],
                                 cursor='hand2',
                                 selectcolor=self.colors['accent'])
        checkbox.pack(side='left', padx=(0, 8), pady=0)
        
        text_frame = tk.Frame(content_frame, bg=self.colors['bg_light'], cursor='hand2')
        text_frame.pack(side='left', fill='both', expand=True)
        
        name_label = tk.Label(text_frame,
                             text=game['name'][:22] + "..." if len(game['name']) > 22 else game['name'],
                             bg=self.colors['bg_light'],
                             fg=self.colors['text_primary'],
                             font=('Segoe UI', 10, 'bold'),
                             anchor='w',
                             justify='left',
                             cursor='hand2',
                             wraplength=150)
        name_label.pack(fill='x', anchor='w', pady=(0, 3))
        
        description = game.get('description', '')
        desc_preview = description[:45] + "..." if len(description) > 45 else description
        desc_label = tk.Label(text_frame,
                             text=desc_preview if desc_preview else "—",
                             bg=self.colors['bg_light'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 8),
                             anchor='w',
                             justify='left',
                             cursor='hand2',
                             wraplength=150)
        desc_label.pack(fill='x', anchor='w', pady=(0, 0))
        
        def toggle_checkbox(event=None):
            game_var.set(not game_var.get())
        
        def on_card_enter(event):
            card_frame.config(bg='#2a2f38', highlightbackground=self.colors['accent'])
            top_frame.config(bg='#2a2f38')
            content_frame.config(bg='#2a2f38')
            name_label.config(bg='#2a2f38', fg='#ffffff')
            desc_label.config(bg='#2a2f38', fg='#c0c0c8')
            text_frame.config(bg='#2a2f38')
            if image_label:
                image_label.config(bg='#2a2f38')
            checkbox.config(bg='#2a2f38', activebackground='#2a2f38')
        
        def on_card_leave(event):
            card_frame.config(bg=self.colors['bg_light'], highlightbackground='#404050')
            top_frame.config(bg=self.colors['bg_light'])
            content_frame.config(bg=self.colors['bg_light'])
            name_label.config(bg=self.colors['bg_light'], fg=self.colors['text_primary'])
            desc_label.config(bg=self.colors['bg_light'], fg=self.colors['text_secondary'])
            text_frame.config(bg=self.colors['bg_light'])
            if image_label:
                image_label.config(bg=self.colors['bg_light'])
            checkbox.config(bg=self.colors['bg_light'], activebackground=self.colors['bg_light'])
        
        def on_card_hover_enter(event):
            on_card_enter(event)
        
        def on_card_hover_leave(event):
            on_card_leave(event)
        
        card_frame.bind("<Enter>", on_card_hover_enter)
        card_frame.bind("<Leave>", on_card_hover_leave)
        top_frame.bind("<Enter>", on_card_hover_enter)
        top_frame.bind("<Leave>", on_card_hover_leave)
        image_label.bind("<Enter>", on_card_hover_enter)
        image_label.bind("<Leave>", on_card_hover_leave)
        name_label.bind("<Enter>", on_card_hover_enter)
        name_label.bind("<Leave>", on_card_hover_leave)
        content_frame.bind("<Enter>", on_card_hover_enter)
        content_frame.bind("<Leave>", on_card_hover_leave)
        text_frame.bind("<Enter>", on_card_hover_enter)
        text_frame.bind("<Leave>", on_card_hover_leave)
        checkbox.bind("<Enter>", on_card_hover_enter)
        checkbox.bind("<Leave>", on_card_hover_leave)
        desc_label.bind("<Enter>", on_card_hover_enter)
        desc_label.bind("<Leave>", on_card_hover_leave)
        
        if on_mousewheel:
            card_frame.bind("<MouseWheel>", on_mousewheel)
            top_frame.bind("<MouseWheel>", on_mousewheel)
            image_label.bind("<MouseWheel>", on_mousewheel)
            name_label.bind("<MouseWheel>", on_mousewheel)
            content_frame.bind("<MouseWheel>", on_mousewheel)
            text_frame.bind("<MouseWheel>", on_mousewheel)
            checkbox.bind("<MouseWheel>", on_mousewheel)
            desc_label.bind("<MouseWheel>", on_mousewheel)
        
        def on_text_click(event):
            toggle_checkbox()
        
        image_label.bind("<Button-1>", on_text_click)
        name_label.bind("<Button-1>", on_text_click)
        desc_label.bind("<Button-1>", on_text_click)
    
    def export_games_to_file(self, games, file_path):
        """Exportar juegos a archivo ZIP"""
        import zipfile
        import json
        import os
        
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for game in games:
                map_content = game.get('map_content', '')
                map_type = game.get('map_type', 'image')
                
                game_data = {
                    'name': game['name'],
                    'description': game.get('description', ''),
                    'map_type': map_type,
                    'map_content': map_content,
                    'favorite': game.get('favorite', False),
                    'last_opened_at': game.get('last_opened_at')
                }
                
                zipf.writestr(f"{game['name']}/game_data.json", json.dumps(game_data, ensure_ascii=False, indent=2))
                
                if os.path.exists(game['image_path']):
                    zipf.write(game['image_path'], arcname=f"{game['name']}/image{os.path.splitext(game['image_path'])[1]}")
                
                if map_type == 'image' and map_content and os.path.exists(map_content):
                    zipf.write(map_content, arcname=f"{game['name']}/map{os.path.splitext(map_content)[1]}")
    
    def show_import_games_dialog(self):
        """Mostrar diálogo para importar juegos"""
        file_path = filedialog.askopenfilename(
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
            title=self.get_text('import_game_dialog_title')
        )
        
        if file_path:
            try:
                if not self.import_games_from_file(file_path):
                    return
                messagebox.showinfo(self.get_text('success'), self.get_text('imported_successfully'))
                self.refresh_games_display()
            except Exception as e:
                messagebox.showerror(self.get_text('error'), f"{self.get_text('import_failed')}: {str(e)}")
    
    def import_games_from_file(self, file_path):
        """Importar juegos desde archivo ZIP"""
        import zipfile
        import json
        import os
        from PIL import Image
        original_games = self.games.copy()
        
        with zipfile.ZipFile(file_path, 'r') as zipf:
            for folder in set([name.split('/')[0] for name in zipf.namelist()]):
                if folder:
                    try:
                        game_data_str = zipf.read(f"{folder}/game_data.json").decode('utf-8')
                        game_data = json.loads(game_data_str)
                        
                        games_dir = os.path.join(os.path.dirname(self.config_file), 'games_images')
                        os.makedirs(games_dir, exist_ok=True)
                        
                        image_files = [f for f in zipf.namelist() if f.startswith(f"{folder}/image")]
                        
                        if image_files:
                            image_file = image_files[0]
                            image_data = zipf.read(image_file)
                            image_path = os.path.join(games_dir, f"{game_data['name']}{os.path.splitext(image_file)[1]}")
                            with open(image_path, 'wb') as img_file:
                                img_file.write(image_data)
                        else:
                            image_path = ""
                        
                        map_content = game_data.get('map_content', '')
                        map_type = game_data.get('map_type', 'image')
                        
                        if map_type == 'image':
                            map_files = [f for f in zipf.namelist() if f.startswith(f"{folder}/map")]
                            if map_files:
                                map_file = map_files[0]
                                map_data = zipf.read(map_file)
                                map_path = os.path.join(games_dir, f"{game_data['name']}_map{os.path.splitext(map_file)[1]}")
                                with open(map_path, 'wb') as map_img_file:
                                    map_img_file.write(map_data)
                                map_content = map_path
                        
                        new_game = {
                            'name': game_data['name'],
                            'description': game_data.get('description', ''),
                            'image_path': image_path,
                            'map_type': map_type,
                            'map_content': map_content,
                            'favorite': game_data.get('favorite', False),
                            'last_opened_at': game_data.get('last_opened_at'),
                            'tasks': [],
                            'date_added': datetime.now().isoformat()
                        }
                        
                        if new_game['name'] not in [g['name'] for g in self.games]:
                            self.games.append(new_game)
                    except Exception as e:
                        print(f"Error importing game from {folder}: {e}")
        
        if not self.save_games():
            self.games = original_games
            return False
        return True
    
    def show_user_guide_dialog(self):
        """Mostrar ventana de Guía de Usuario con diseño ultra moderno"""
        guide_window = tk.Toplevel(self.root)
        guide_window.withdraw()  # Ocultar la ventana inicialmente
        guide_window.title(self.get_text('user_guide_title'))
        guide_width = max(640, min(1100, guide_window.winfo_screenwidth() - 80))
        guide_height = max(520, min(800, guide_window.winfo_screenheight() - 100))
        guide_window.geometry(f"{guide_width}x{guide_height}")
        guide_window.configure(bg=self.colors['bg_dark'])
        guide_window.resizable(True, True)
        self.apply_window_icon(guide_window)
        guide_window.minsize(min(800, guide_width), min(600, guide_height))
        
        # Centrar la ventana
        guide_window.transient(self.root)
        
        # Importar el módulo ttk para las pestañas
        from tkinter import ttk
        
        # Header moderno con gradiente mejorado
        header_frame = tk.Frame(guide_window, bg=self.colors['bg_dark'], height=120)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Canvas principal del header
        header_canvas = tk.Canvas(header_frame, bg=self.colors['accent'], highlightthickness=0, height=120)
        header_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Gradiente diagonal mejorado
        for i in range(120):
            # Crear un gradiente más sofisticado
            progress = i / 120.0
            alpha1 = 1.0 - progress * 0.4
            alpha2 = 0.8 - progress * 0.6
            
            # Color principal
            color1 = self.blend_colors(self.colors['accent'], self.colors['bg_dark'], alpha1)
            # Color secundario para profundidad
            if i < 60:
                color2 = self.blend_colors('#6366f1', color1, 0.3)
            else:
                color2 = color1
            
            header_canvas.create_line(0, i, 1000, i, fill=color2, width=1)
        
        # Elementos decorativos en el header
        # Círculos decorativos con transparencia
        for x, y, size, alpha in [(150, 30, 40, 0.1), (850, 40, 60, 0.08), (750, 80, 30, 0.12)]:
            color = self.blend_colors('#ffffff', self.colors['accent'], alpha)
            header_canvas.create_oval(x, y, x+size, y+size, fill=color, outline='')
        
        # Icono principal del header
        header_canvas.create_text(80, 60, text="📚", font=('Segoe UI Emoji', 32), fill='white')
        
        # Título principal del header con sombra
        # Sombra del texto
        header_canvas.create_text(502, 47, text=self.get_text('user_guide_title'),
                                 fill='#000000', font=('Segoe UI', 24, 'bold'), anchor='center')
        # Texto principal
        header_canvas.create_text(500, 45, text=self.get_text('user_guide_title'),
                                 fill='white', font=('Segoe UI', 24, 'bold'), anchor='center')
        
        # Subtítulo estilizado
        header_canvas.create_text(500, 75, text=self.get_text('guide_subtitle'),
                                 fill='#e5e7eb', font=('Segoe UI', 12), anchor='center')
        
        # Línea decorativa
        header_canvas.create_line(350, 95, 650, 95, fill='#ffffff', width=2)
        
        # Frame contenedor principal con padding mejorado
        main_container = tk.Frame(guide_window, bg=self.colors['bg_dark'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(15, 20))
        
        # Crear el Notebook con estilo personalizado sin afectar el tema global
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Guardar el tema actual para restaurarlo después
        style = ttk.Style()
        original_theme = style.theme_use()
        
        # Configurar estilos únicos solo para esta ventana
        try:
            # Crear estilos únicos que no interfieran con los existentes
            style.configure('GuideWindow.TNotebook', 
                           background=self.colors['bg_dark'], 
                           borderwidth=0,
                           tabmargins=[0, 0, 0, 0])
            
            # Estilo único para las pestañas de la guía
            style.configure('GuideWindow.TNotebook.Tab',
                           padding=[30, 15],
                           font=('Segoe UI', 11, 'bold'),
                           focuscolor='none',
                           background=self.colors['bg_medium'],
                           foreground=self.colors['text_secondary'],
                           borderwidth=0,
                           relief='flat')
            
            # Mapeo de estados para pestañas de la guía
            style.map('GuideWindow.TNotebook.Tab',
                     background=[('selected', self.colors['accent']),
                               ('active', self.colors['bg_light'])],
                     foreground=[('selected', 'white'),
                               ('active', self.colors['text'])])
            
            notebook.configure(style='GuideWindow.TNotebook')
            
        except Exception as e:
            # Si hay error con los estilos, usar el notebook básico
            print(f"Warning: Could not apply custom styles: {e}")
        
        # Función para restaurar tema cuando se cierre la ventana
        def on_guide_window_close():
            try:
                # Restaurar el tema original
                style.theme_use(original_theme)
            except:
                pass
            guide_window.destroy()
        
        guide_window.protocol("WM_DELETE_WINDOW", on_guide_window_close)
        
        # Crear las pestañas con iconos mejorados
        games_frame = tk.Frame(notebook, bg=self.colors['bg_dark'])
        notebook.add(games_frame, text="🎮  " + self.get_text('guide_tab_games').upper())
        
        maps_frame = tk.Frame(notebook, bg=self.colors['bg_dark'])
        notebook.add(maps_frame, text="🗺️  " + self.get_text('guide_tab_maps').upper())
        
        features_frame = tk.Frame(notebook, bg=self.colors['bg_dark'])
        notebook.add(features_frame, text="✨  " + self.get_text('guide_tab_features').upper())
        
        tips_frame = tk.Frame(notebook, bg=self.colors['bg_dark'])
        notebook.add(tips_frame, text="💡  " + self.get_text('guide_tab_tips').upper())
        
        # Nueva pestaña de atajos de teclado
        shortcuts_frame = tk.Frame(notebook, bg=self.colors['bg_dark'])
        notebook.add(shortcuts_frame, text="⌨️  " + self.get_text('guide_tab_shortcuts').upper())
        
        # Crear contenido moderno para cada pestaña
        self.create_modern_guide_games_tab(games_frame)
        self.create_modern_guide_maps_tab(maps_frame)
        self.create_modern_guide_features_tab(features_frame)
        self.create_modern_guide_tips_tab(tips_frame)
        self.create_modern_guide_shortcuts_tab(shortcuts_frame)
        
        # Agregar animación de entrada
        self.animate_guide_window_entrance(guide_window)
        
        # Centrar la ventana en la pantalla
        guide_window.update_idletasks()
        center_window_on_primary_monitor(
            guide_window, guide_window.winfo_width(), guide_window.winfo_height()
        )
        
        # Mostrar la ventana con efecto fade-in
        guide_window.deiconify()
        guide_window.wait_visibility()
        guide_window.grab_set()
        guide_window.attributes('-alpha', 0.0)
        self.fade_in_window(guide_window)
    
    def animate_guide_window_entrance(self, window):
        """Animación de entrada suave para la ventana de guía"""
        def animate_scale(scale=0.95):
            if scale <= 1.0:
                # No hay una forma directa de escalar en tkinter, así que usamos el efecto de transparencia
                window.after(20, lambda: animate_scale(scale + 0.01))
        
        animate_scale()
    
    def fade_in_window(self, window, alpha=0.0):
        """Efecto fade-in para ventanas"""
        if alpha < 1.0:
            window.attributes('-alpha', alpha)
            window.after(30, lambda: self.fade_in_window(window, alpha + 0.05))
        else:
            window.attributes('-alpha', 1.0)

    def configure_guide_scrolling(self, parent, canvas, scrollbar, scrollable_frame):
        """Configurar scroll para rueda de Linux/Wayland, X11 y eventos MouseWheel."""
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        window_item = canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

        def update_scroll_region(_event=None):
            canvas.configure(scrollregion=canvas.bbox('all'))

        def resize_content(event):
            canvas.itemconfigure(window_item, width=event.width)
            update_scroll_region()

        def scroll(event):
            units = mousewheel_units(event)
            if units:
                canvas.yview_scroll(units, 'units')
            return 'break'

        scrollable_frame.bind('<Configure>', update_scroll_region, add='+')
        canvas.bind('<Configure>', resize_content, add='+')

        widgets = [canvas]
        while widgets:
            widget = widgets.pop()
            for sequence in ('<MouseWheel>', '<Button-4>', '<Button-5>'):
                widget.bind(sequence, scroll, add='+')
            widgets.extend(widget.winfo_children())

    def blend_colors(self, color1, color2, alpha):
        """Mezclar dos colores para crear gradiente"""
        # Convertir colores hex a RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        # Mezclar colores
        mixed_rgb = (
            rgb1[0] * alpha + rgb2[0] * (1 - alpha),
            rgb1[1] * alpha + rgb2[1] * (1 - alpha),
            rgb1[2] * alpha + rgb2[2] * (1 - alpha)
        )
        
        return rgb_to_hex(mixed_rgb)
    
    def create_modern_card(self, parent, icon, title, content, icon_bg=None, action_button=None, icon_font_size=20):
        """Crear una tarjeta moderna e interactiva para la guía"""
        if icon_bg is None:
            icon_bg = self.colors['accent']
        
        # Frame contenedor principal con margen
        container_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        container_frame.pack(fill=tk.X, padx=25, pady=15)
        
        # Frame principal de la tarjeta sin canvas - más simple y funcional
        card_frame = tk.Frame(container_frame, bg=self.colors['bg_medium'], relief='solid', bd=1)
        card_frame.pack(fill=tk.X, pady=5)
        
        # Configurar borde sutil
        border_color = self.blend_colors(self.colors['accent'], self.colors['bg_medium'], 0.3)
        card_frame.configure(highlightbackground=border_color, highlightthickness=1, bd=0)
        
        # Padding interno
        inner_frame = tk.Frame(card_frame, bg=self.colors['bg_medium'])
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Header con icono y título
        header_frame = tk.Frame(inner_frame, bg=self.colors['bg_medium'])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Icono con efecto visual
        icon_frame = tk.Frame(header_frame, bg=self.colors['bg_medium'])
        icon_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        # Canvas solo para el icono (más pequeño y controlado)
        icon_canvas = tk.Canvas(icon_frame, width=60, height=60, bg=self.colors['bg_medium'], 
                               highlightthickness=0, bd=0)
        icon_canvas.pack()
        
        # Efecto glow para el icono
        glow_color = self.blend_colors(icon_bg, self.colors['bg_medium'], 0.3)
        icon_canvas.create_oval(5, 5, 55, 55, fill=glow_color, outline='', width=0)
        icon_canvas.create_oval(8, 8, 52, 52, fill=icon_bg, outline='', width=0)
        icon_canvas.create_text(30, 30, text=icon, fill='white', font=('Segoe UI Emoji', icon_font_size, 'bold'))
        
        # Área de texto
        text_frame = tk.Frame(header_frame, bg=self.colors['bg_medium'])
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Título principal
        title_label = tk.Label(text_frame, text=title,
                              bg=self.colors['bg_medium'],
                              fg=self.colors['text'],
                              font=('Segoe UI', 16, 'bold'),
                              anchor='w', justify='left')
        title_words = title.split(maxsplit=1)
        if len(title_words) == 2 and not any(char.isalnum() for char in title_words[0]):
            title_label.configure(text=title_words[1])
        title_label.pack(fill=tk.X, pady=(5, 0))
        
        # Contenido principal con texto ajustable
        content_frame = tk.Frame(inner_frame, bg=self.colors['bg_medium'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Usar Text widget en lugar de Label para mejor control del contenido
        content_lines = content.splitlines() or ['']
        estimated_wrapped_lines = sum(
            max(1, (len(line) + 59) // 60) for line in content_lines
        )
        content_text = tk.Text(content_frame,
                              wrap=tk.WORD,
                              bg=self.colors['bg_light'],
                              fg=self.colors['text_secondary'],
                              font=('Segoe UI', 11),
                              relief='flat',
                              padx=15,
                              pady=12,
                              height=max(4, estimated_wrapped_lines),
                              cursor='arrow',
                              selectbackground=self.colors['accent'],
                              selectforeground='white')
        content_text.pack(fill=tk.BOTH, expand=True)
        content_text.insert('1.0', content)
        content_text.config(state='disabled')  # Solo lectura
        
        # Botón de acción opcional
        if action_button:
            button_frame = tk.Frame(inner_frame, bg=self.colors['bg_medium'])
            button_frame.pack(fill=tk.X, pady=(15, 0))
            
            action_btn = tk.Button(button_frame, 
                                  text=action_button['text'],
                                  bg=self.colors['accent'],
                                  fg='white',
                                  font=('Segoe UI', 10, 'bold'),
                                  relief='flat',
                                  padx=20, pady=10,
                                  cursor='hand2',
                                  command=action_button.get('command', lambda: None))
            action_btn.pack(side=tk.LEFT)
            
            # Efectos hover para el botón
            def on_button_enter(e):
                action_btn.configure(bg=self.blend_colors(self.colors['accent'], '#ffffff', 0.9))
            
            def on_button_leave(e):
                action_btn.configure(bg=self.colors['accent'])
            
            action_btn.bind('<Enter>', on_button_enter)
            action_btn.bind('<Leave>', on_button_leave)
        
        # Efectos hover para toda la tarjeta - simplificados
        def on_card_enter(event):
            new_bg = self.blend_colors(self.colors['bg_medium'], '#ffffff', 0.97)
            card_frame.configure(bg=new_bg)
            inner_frame.configure(bg=new_bg)
            header_frame.configure(bg=new_bg)
            icon_frame.configure(bg=new_bg)
            text_frame.configure(bg=new_bg)
            content_frame.configure(bg=new_bg)
            title_label.configure(bg=new_bg)
            icon_canvas.configure(bg=new_bg)
            
            # Cambiar color del borde
            hover_border = self.blend_colors(self.colors['accent'], new_bg, 0.6)
            card_frame.configure(highlightbackground=hover_border)
            
        def on_card_leave(event):
            card_frame.configure(bg=self.colors['bg_medium'])
            inner_frame.configure(bg=self.colors['bg_medium'])
            header_frame.configure(bg=self.colors['bg_medium'])
            icon_frame.configure(bg=self.colors['bg_medium'])
            text_frame.configure(bg=self.colors['bg_medium'])
            content_frame.configure(bg=self.colors['bg_medium'])
            title_label.configure(bg=self.colors['bg_medium'])
            icon_canvas.configure(bg=self.colors['bg_medium'])
            
            # Restaurar color del borde
            border_color = self.blend_colors(self.colors['accent'], self.colors['bg_medium'], 0.3)
            card_frame.configure(highlightbackground=border_color)
        
        # Función recursiva para aplicar hover a todos los widgets hijos
        def bind_hover_events(widget):
            widget.bind('<Enter>', on_card_enter)
            widget.bind('<Leave>', on_card_leave)
            for child in widget.winfo_children():
                if child != content_text:  # No aplicar a content_text para evitar interferir con la selección
                    bind_hover_events(child)
        
        bind_hover_events(card_frame)
        
        return card_frame
    
    def create_professional_card(self, parent, icon, title, content, icon_bg=None):
        """Crear una tarjeta profesional para la guía"""
        if icon_bg is None:
            icon_bg = self.colors['accent']
            
        # Frame principal de la tarjeta
        card_frame = tk.Frame(parent, bg=self.colors['bg_medium'], relief='flat', bd=0)
        card_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Crear efecto de sombra/elevación
        shadow_frame = tk.Frame(parent, bg='#1a1a1a', height=2)
        shadow_frame.pack(fill=tk.X, padx=22, pady=(0, 2))
        
        # Frame interno con padding
        inner_frame = tk.Frame(card_frame, bg=self.colors['bg_medium'])
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header de la tarjeta con icono
        header_frame = tk.Frame(inner_frame, bg=self.colors['bg_medium'])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Icono circular
        icon_canvas = tk.Canvas(header_frame, width=50, height=50, bg=self.colors['bg_medium'], highlightthickness=0)
        icon_canvas.pack(side=tk.LEFT, padx=(0, 15))
        
        # Dibujar círculo de fondo para el icono
        icon_canvas.create_oval(5, 5, 45, 45, fill=icon_bg, outline='', width=0)
        icon_canvas.create_text(25, 25, text=icon, fill='white', font=('Segoe UI', 18, 'bold'))
        
        # Título de la tarjeta
        title_label = tk.Label(header_frame, text=title,
                              bg=self.colors['bg_medium'],
                              fg=self.colors['text'],
                              font=('Segoe UI', 14, 'bold'))
        title_label.pack(side=tk.LEFT, anchor='w')
        
        # Contenido de la tarjeta
        content_frame = tk.Frame(inner_frame, bg=self.colors['bg_medium'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        content_text = tk.Text(content_frame,
                              wrap=tk.WORD,
                              bg=self.colors['bg_light'],
                              fg=self.colors['text'],
                              font=('Segoe UI', 10),
                              relief='flat',
                              padx=20,
                              pady=15,
                              height=6,
                              cursor='arrow')
        content_text.pack(fill=tk.BOTH, expand=True)
        content_text.insert('1.0', content)
        content_text.config(state='disabled')
        
        return card_frame
    
    def create_guide_games_tab_professional(self, parent):
        """Crear el contenido profesional de la pestaña Juegos"""
        # Frame principal con scroll
        canvas = tk.Canvas(parent, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Título con descripción
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=20, padx=30)
        
        intro_text = tk.Label(intro_frame,
                             text="Aprende a gestionar tu biblioteca de juegos de forma eficiente",
                             bg=self.colors['bg_dark'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 12),
                             wraplength=800)
        intro_text.pack()
        
        # Tarjeta: Agregar juegos
        self.create_professional_card(
            scrollable_frame,
            "📝",
            self.get_text('guide_games_add_title'),
            self.get_text('guide_games_add_content'),
            '#4f46e5'  # Color azul
        )
        
        # Tarjeta: Gestionar juegos
        self.create_professional_card(
            scrollable_frame,
            "⚙️",
            self.get_text('guide_games_manage_title'),
            self.get_text('guide_games_manage_content'),
            '#059669'  # Color verde
        )
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratón - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el árbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # También bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_guide_maps_tab_professional(self, parent):
        """Crear el contenido profesional de la pestaña Mapas"""
        # Frame principal con scroll
        canvas = tk.Canvas(parent, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Título con descripción
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=20, padx=30)
        
        intro_text = tk.Label(intro_frame,
                             text="Configura mapas de imagen y web para tener acceso rápido a la información de tus juegos",
                             bg=self.colors['bg_dark'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 12),
                             wraplength=800)
        intro_text.pack()
        
        # Tarjeta: Mapas de imagen
        self.create_professional_card(
            scrollable_frame,
            "🖼️",
            self.get_text('guide_maps_image_title'),
            self.get_text('guide_maps_image_content'),
            '#dc2626'  # Color rojo
        )
        
        # Tarjeta: Mapas web
        self.create_professional_card(
            scrollable_frame,
            "🌐",
            self.get_text('guide_maps_web_title'),
            self.get_text('guide_maps_web_content'),
            '#2563eb'  # Color azul fuerte
        )
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratón - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el árbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # También bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_guide_features_tab_professional(self, parent):
        """Crear el contenido profesional de la pestaña Características"""
        # Frame principal con scroll
        canvas = tk.Canvas(parent, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Título con descripción
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=20, padx=30)
        
        intro_text = tk.Label(intro_frame,
                             text="Descubre todas las características que hacen de Avilon una herramienta potente y personalizable",
                             bg=self.colors['bg_dark'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 12),
                             wraplength=800)
        intro_text.pack()
        
        # Tarjeta: Sistema de búsqueda
        self.create_professional_card(
            scrollable_frame,
            "🔍",
            self.get_text('guide_features_search_title'),
            self.get_text('guide_features_search_content'),
            '#7c3aed'  # Color púrpura
        )
        
        # Tarjeta: Temas y personalización
        self.create_professional_card(
            scrollable_frame,
            "🎨",
            self.get_text('guide_features_themes_title'),
            self.get_text('guide_features_themes_content'),
            '#ea580c'  # Color naranja
        )
        
        # Tarjeta: Inicio automático
        self.create_professional_card(
            scrollable_frame,
            "🚀",
            self.get_text('guide_features_startup_title'),
            self.get_text('guide_features_startup_content'),
            '#0891b2'  # Color cyan
        )
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratón - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el árbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # También bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_guide_tips_tab_professional(self, parent):
        """Crear el contenido profesional de la pestaña Consejos"""
        # Frame principal con scroll
        canvas = tk.Canvas(parent, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Título con descripción
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=20, padx=30)
        
        intro_text = tk.Label(intro_frame,
                             text="Consejos prácticos para aprovechar al máximo Avilon y optimizar tu experiencia",
                             bg=self.colors['bg_dark'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 12),
                             wraplength=800)
        intro_text.pack()
        
        # Tarjeta: Organización
        self.create_professional_card(
            scrollable_frame,
            "📚",
            self.get_text('guide_tips_organization_title'),
            self.get_text('guide_tips_organization_content'),
            '#16a34a'  # Color verde claro
        )
        
        # Tarjeta: Mejores prácticas para imágenes
        self.create_professional_card(
            scrollable_frame,
            "🖼️",
            self.get_text('guide_tips_images_title'),
            self.get_text('guide_tips_images_content'),
            '#c026d3'  # Color magenta
        )
        
        # Tarjeta: Consejos para mapas
        self.create_professional_card(
            scrollable_frame,
            "🗺️",
            self.get_text('guide_tips_maps_title'),
            self.get_text('guide_tips_maps_content'),
            '#0369a1'  # Color azul oscuro
        )
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratón - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el árbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # También bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_guide_games_tab(self, parent):
        """Crear el contenido de la pestaña Juegos"""
        # Frame principal con scroll
        canvas = tk.Canvas(parent, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Dark.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Título principal
        title_label = ttk.Label(scrollable_frame, 
                               text=self.get_text('guide_games_title'),
                               style='Dark.TLabel',
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(10, 20), padx=20, anchor='w')
        
        # Sección: Agregar juegos
        add_title = ttk.Label(scrollable_frame,
                             text=self.get_text('guide_games_add_title'),
                             style='Dark.TLabel',
                             font=('Segoe UI', 12, 'bold'))
        add_title.pack(pady=(0, 10), padx=20, anchor='w')
        
        add_content = tk.Text(scrollable_frame,
                             height=7,
                             wrap=tk.WORD,
                             bg=self.colors['bg_light'],
                             fg=self.colors['text'],
                             font=('Segoe UI', 10),
                             relief='flat',
                             padx=15,
                             pady=10)
        add_content.pack(fill=tk.X, padx=20, pady=(0, 20))
        add_content.insert('1.0', self.get_text('guide_games_add_content'))
        add_content.config(state='disabled')
        
        # Sección: Gestionar juegos
        manage_title = ttk.Label(scrollable_frame,
                                text=self.get_text('guide_games_manage_title'),
                                style='Dark.TLabel',
                                font=('Segoe UI', 12, 'bold'))
        manage_title.pack(pady=(0, 10), padx=20, anchor='w')
        
        manage_content = tk.Text(scrollable_frame,
                                height=5,
                                wrap=tk.WORD,
                                bg=self.colors['bg_light'],
                                fg=self.colors['text'],
                                font=('Segoe UI', 10),
                                relief='flat',
                                padx=15,
                                pady=10)
        manage_content.pack(fill=tk.X, padx=20, pady=(0, 20))
        manage_content.insert('1.0', self.get_text('guide_games_manage_content'))
        manage_content.config(state='disabled')
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratón - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el árbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # También bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_guide_maps_tab(self, parent):
        """Crear el contenido de la pestaña Mapas"""
        # Frame principal con scroll
        canvas = tk.Canvas(parent, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Dark.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Título principal
        title_label = ttk.Label(scrollable_frame, 
                               text=self.get_text('guide_maps_title'),
                               style='Dark.TLabel',
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(10, 20), padx=20, anchor='w')
        
        # Tipos de mapas
        types_title = ttk.Label(scrollable_frame,
                               text=self.get_text('guide_maps_types_title'),
                               style='Dark.TLabel',
                               font=('Segoe UI', 12, 'bold'))
        types_title.pack(pady=(0, 15), padx=20, anchor='w')
        
        # Mapas de imagen
        image_title = ttk.Label(scrollable_frame,
                               text=self.get_text('guide_maps_image_title'),
                               style='Dark.TLabel',
                               font=('Segoe UI', 11, 'bold'))
        image_title.pack(pady=(0, 5), padx=20, anchor='w')
        
        image_content = tk.Text(scrollable_frame,
                               height=4,
                               wrap=tk.WORD,
                               bg=self.colors['bg_light'],
                               fg=self.colors['text'],
                               font=('Segoe UI', 10),
                               relief='flat',
                               padx=15,
                               pady=10)
        image_content.pack(fill=tk.X, padx=20, pady=(0, 15))
        image_content.insert('1.0', self.get_text('guide_maps_image_content'))
        image_content.config(state='disabled')
        
        # Mapas web
        web_title = ttk.Label(scrollable_frame,
                             text=self.get_text('guide_maps_web_title'),
                             style='Dark.TLabel',
                             font=('Segoe UI', 11, 'bold'))
        web_title.pack(pady=(0, 5), padx=20, anchor='w')
        
        web_content = tk.Text(scrollable_frame,
                             height=5,
                             wrap=tk.WORD,
                             bg=self.colors['bg_light'],
                             fg=self.colors['text'],
                             font=('Segoe UI', 10),
                             relief='flat',
                             padx=15,
                             pady=10)
        web_content.pack(fill=tk.X, padx=20, pady=(0, 20))
        web_content.insert('1.0', self.get_text('guide_maps_web_content'))
        web_content.config(state='disabled')
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratón - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el árbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # También bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_guide_features_tab(self, parent):
        """Crear el contenido de la pestaña Características"""
        # Frame principal con scroll
        canvas = tk.Canvas(parent, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Dark.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Título principal
        title_label = ttk.Label(scrollable_frame, 
                               text=self.get_text('guide_features_title'),
                               style='Dark.TLabel',
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(10, 20), padx=20, anchor='w')
        
        # Sistema de búsqueda
        search_title = ttk.Label(scrollable_frame,
                                text=self.get_text('guide_features_search_title'),
                                style='Dark.TLabel',
                                font=('Segoe UI', 11, 'bold'))
        search_title.pack(pady=(0, 5), padx=20, anchor='w')
        
        search_content = tk.Text(scrollable_frame,
                                height=4,
                                wrap=tk.WORD,
                                bg=self.colors['bg_light'],
                                fg=self.colors['text'],
                                font=('Segoe UI', 10),
                                relief='flat',
                                padx=15,
                                pady=10)
        search_content.pack(fill=tk.X, padx=20, pady=(0, 15))
        search_content.insert('1.0', self.get_text('guide_features_search_content'))
        search_content.config(state='disabled')
        
        # Temas
        themes_title = ttk.Label(scrollable_frame,
                                text=self.get_text('guide_features_themes_title'),
                                style='Dark.TLabel',
                                font=('Segoe UI', 11, 'bold'))
        themes_title.pack(pady=(0, 5), padx=20, anchor='w')
        
        themes_content = tk.Text(scrollable_frame,
                                height=4,
                                wrap=tk.WORD,
                                bg=self.colors['bg_light'],
                                fg=self.colors['text'],
                                font=('Segoe UI', 10),
                                relief='flat',
                                padx=15,
                                pady=10)
        themes_content.pack(fill=tk.X, padx=20, pady=(0, 15))
        themes_content.insert('1.0', self.get_text('guide_features_themes_content'))
        themes_content.config(state='disabled')
        
        # Inicio automático
        startup_title = ttk.Label(scrollable_frame,
                                 text=self.get_text('guide_features_startup_title'),
                                 style='Dark.TLabel',
                                 font=('Segoe UI', 11, 'bold'))
        startup_title.pack(pady=(0, 5), padx=20, anchor='w')
        
        startup_content = tk.Text(scrollable_frame,
                                 height=4,
                                 wrap=tk.WORD,
                                 bg=self.colors['bg_light'],
                                 fg=self.colors['text'],
                                 font=('Segoe UI', 10),
                                 relief='flat',
                                 padx=15,
                                 pady=10)
        startup_content.pack(fill=tk.X, padx=20, pady=(0, 20))
        startup_content.insert('1.0', self.get_text('guide_features_startup_content'))
        startup_content.config(state='disabled')
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratón - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el árbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # También bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_guide_tips_tab(self, parent):
        """Crear el contenido de la pestaña Consejos"""
        # Frame principal con scroll
        canvas = tk.Canvas(parent, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Dark.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Título principal
        title_label = ttk.Label(scrollable_frame, 
                               text=self.get_text('guide_tips_title'),
                               style='Dark.TLabel',
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(10, 20), padx=20, anchor='w')
        
        # Organización
        org_title = ttk.Label(scrollable_frame,
                             text=self.get_text('guide_tips_organization_title'),
                             style='Dark.TLabel',
                             font=('Segoe UI', 11, 'bold'))
        org_title.pack(pady=(0, 5), padx=20, anchor='w')
        
        org_content = tk.Text(scrollable_frame,
                             height=4,
                             wrap=tk.WORD,
                             bg=self.colors['bg_light'],
                             fg=self.colors['text'],
                             font=('Segoe UI', 10),
                             relief='flat',
                             padx=15,
                             pady=10)
        org_content.pack(fill=tk.X, padx=20, pady=(0, 15))
        org_content.insert('1.0', self.get_text('guide_tips_organization_content'))
        org_content.config(state='disabled')
        
        # Imágenes
        images_title = ttk.Label(scrollable_frame,
                                text=self.get_text('guide_tips_images_title'),
                                style='Dark.TLabel',
                                font=('Segoe UI', 11, 'bold'))
        images_title.pack(pady=(0, 5), padx=20, anchor='w')
        
        images_content = tk.Text(scrollable_frame,
                                height=4,
                                wrap=tk.WORD,
                                bg=self.colors['bg_light'],
                                fg=self.colors['text'],
                                font=('Segoe UI', 10),
                                relief='flat',
                                padx=15,
                                pady=10)
        images_content.pack(fill=tk.X, padx=20, pady=(0, 15))
        images_content.insert('1.0', self.get_text('guide_tips_images_content'))
        images_content.config(state='disabled')
        
        # Mapas
        maps_title = ttk.Label(scrollable_frame,
                              text=self.get_text('guide_tips_maps_title'),
                              style='Dark.TLabel',
                              font=('Segoe UI', 11, 'bold'))
        maps_title.pack(pady=(0, 5), padx=20, anchor='w')
        
        maps_content = tk.Text(scrollable_frame,
                              height=4,
                              wrap=tk.WORD,
                              bg=self.colors['bg_light'],
                              fg=self.colors['text'],
                              font=('Segoe UI', 10),
                              relief='flat',
                              padx=15,
                              pady=10)
        maps_content.pack(fill=tk.X, padx=20, pady=(0, 20))
        maps_content.insert('1.0', self.get_text('guide_tips_maps_content'))
        maps_content.config(state='disabled')
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratón - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el árbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # También bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_modern_guide_games_tab(self, parent):
        """Crear el contenido moderno de la pestaña Juegos"""
        # Frame principal con scroll suave
        canvas = tk.Canvas(parent, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header de introducción moderno
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=(30, 40), padx=30)
        
        intro_title = tk.Label(intro_frame,
                              text=self.get_text('guide_games_title'),
                              bg=self.colors['bg_dark'],
                              fg=self.colors['text'],
                              font=('Segoe UI', 20, 'bold'))
        intro_title.pack(anchor='w')
        
        intro_subtitle = tk.Label(intro_frame,
                                 text=self.get_text('guide_subtitle'),
                                 bg=self.colors['bg_dark'],
                                 fg=self.colors['text_secondary'],
                                 font=('Segoe UI', 13))
        intro_subtitle.pack(anchor='w', pady=(5, 0))
        
        # Tarjeta: Agregar juegos nuevos
        self.create_modern_card(
            scrollable_frame,
            "➕",
            self.get_text('guide_games_add_title'),
            self.get_text('guide_games_add_content'),
            '#10b981',  # Verde moderno
            {
                'text': self.get_text('add_game_button'),
                'command': self.show_add_game_dialog
            }
        )
        
        # Tarjeta: Organizar biblioteca
        self.create_modern_card(
            scrollable_frame,
            "📚",
            self.get_text('guide_games_manage_title'),
            self.get_text('guide_games_manage_content'),
            '#3b82f6',  # Azul moderno
        )
        
        # Tarjeta: Gestión avanzada - usando contenido existente
        self.create_modern_card(
            scrollable_frame,
            "⚙️",
            self.get_text('guide_features_title'),
            self.get_text('guide_features_search_content'),
            '#8b5cf6',  # Púrpura moderno
        )
        
        self.configure_guide_scrolling(parent, canvas, scrollbar, scrollable_frame)
    
    def create_modern_guide_maps_tab(self, parent):
        """Crear el contenido moderno de la pestaña Mapas"""
        # Frame principal con scroll
        canvas = tk.Canvas(parent, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header de introducción
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=(30, 40), padx=30)
        
        intro_title = tk.Label(intro_frame,
                              text=self.get_text('guide_maps_title'),
                              bg=self.colors['bg_dark'],
                              fg=self.colors['text'],
                              font=('Segoe UI', 20, 'bold'))
        intro_title.pack(anchor='w')
        
        intro_subtitle = tk.Label(intro_frame,
                                 text=self.get_text('guide_subtitle'),
                                 bg=self.colors['bg_dark'],
                                 fg=self.colors['text_secondary'],
                                 font=('Segoe UI', 13))
        intro_subtitle.pack(anchor='w', pady=(5, 0))
        
        # Tarjeta: Mapas de imagen
        self.create_modern_card(
            scrollable_frame,
            "🖼️",
            self.get_text('guide_maps_image_title'),
            self.get_text('guide_maps_image_content'),
            '#f59e0b',  # Ámbar
        )
        
        # Tarjeta: Mapas web
        self.create_modern_card(
            scrollable_frame,
            "🌐",
            self.get_text('guide_maps_web_title'),
            self.get_text('guide_maps_web_content'),
            '#ef4444',  # Rojo moderno
        )
        
        # Tarjeta: Consejos para mapas
        self.create_modern_card(
            scrollable_frame,
            "🔍",
            self.get_text('guide_tips_maps_title'),
            self.get_text('guide_tips_maps_content'),
            '#06b6d4',  # Cian
        )
        
        self.configure_guide_scrolling(parent, canvas, scrollbar, scrollable_frame)
    
    def create_modern_guide_features_tab(self, parent):
        """Crear el contenido moderno de la pestaña Características"""
        # Frame principal con scroll
        canvas = tk.Canvas(parent, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header de introducción
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=(30, 40), padx=30)
        
        intro_title = tk.Label(intro_frame,
                              text=self.get_text('guide_features_title'),
                              bg=self.colors['bg_dark'],
                              fg=self.colors['text'],
                              font=('Segoe UI', 20, 'bold'))
        intro_title.pack(anchor='w')
        
        intro_subtitle = tk.Label(intro_frame,
                                 text=self.get_text('guide_subtitle'),
                                 bg=self.colors['bg_dark'],
                                 fg=self.colors['text_secondary'],
                                 font=('Segoe UI', 13))
        intro_subtitle.pack(anchor='w', pady=(5, 0))
        
        # Tarjeta: Sistema de búsqueda
        self.create_modern_card(
            scrollable_frame,
            "🔍",
            self.get_text('guide_features_search_title'),
            self.get_text('guide_features_search_content'),
            '#8b5cf6',  # Púrpura
        )
        
        # Tarjeta: Temas personalizables
        self.create_modern_card(
            scrollable_frame,
            "🎨",
            self.get_text('guide_features_themes_title'),
            self.get_text('guide_features_themes_content'),
            '#10b981',  # Verde
            {
                'text': self.get_text('config_button'),
                'command': self.show_config_dialog
            }
        )
        
        # Tarjeta: Consejos para imágenes
        self.create_modern_card(
            scrollable_frame,
            "🖼️",
            self.get_text('guide_tips_images_title'),
            self.get_text('guide_tips_images_content'),
            '#f59e0b',  # Ámbar
        )
        
        self.configure_guide_scrolling(parent, canvas, scrollbar, scrollable_frame)
    
    def create_modern_guide_tips_tab(self, parent):
        """Crear el contenido moderno de la pestaña Consejos"""
        # Frame principal con scroll
        canvas = tk.Canvas(parent, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header de introducción
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=(30, 40), padx=30)
        
        intro_title = tk.Label(intro_frame,
                              text=self.get_text('guide_tips_title'),
                              bg=self.colors['bg_dark'],
                              fg=self.colors['text'],
                              font=('Segoe UI', 20, 'bold'))
        intro_title.pack(anchor='w')
        
        intro_subtitle = tk.Label(intro_frame,
                                 text=self.get_text('guide_subtitle'),
                                 bg=self.colors['bg_dark'],
                                 fg=self.colors['text_secondary'],
                                 font=('Segoe UI', 13))
        intro_subtitle.pack(anchor='w', pady=(5, 0))
        
        # Tarjeta: Organización eficiente
        self.create_modern_card(
            scrollable_frame,
            "📋",
            self.get_text('guide_tips_organization_title'),
            self.get_text('guide_tips_organization_content'),
            '#3b82f6',  # Azul
        )
        
        # Tarjeta: Mejores prácticas para imágenes
        self.create_modern_card(
            scrollable_frame,
            "🖼️",
            self.get_text('guide_tips_images_title'),
            self.get_text('guide_tips_images_content'),
            '#ef4444',  # Rojo
        )
        
        # Tarjeta: Consejos para mapas
        self.create_modern_card(
            scrollable_frame,
            "🗺️",
            self.get_text('guide_tips_maps_title'),
            self.get_text('guide_tips_maps_content'),
            '#10b981',  # Verde
            icon_font_size=16
        )
        
        self.configure_guide_scrolling(parent, canvas, scrollbar, scrollable_frame)

    def create_modern_guide_shortcuts_tab(self, parent):
        """Crear el contenido moderno de la pestaña Atajos de Teclado"""
        # Frame principal con scroll
        canvas = tk.Canvas(parent, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header de introducción
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=(30, 40), padx=30)
        
        intro_title = tk.Label(intro_frame,
                              text=self.get_text('guide_shortcuts_title'),
                              bg=self.colors['bg_dark'],
                              fg=self.colors['text'],
                              font=('Segoe UI', 20, 'bold'))
        intro_title.pack(anchor='w')
        
        intro_subtitle = tk.Label(intro_frame,
                                 text=self.get_text('guide_shortcuts_subtitle'),
                                 bg=self.colors['bg_dark'],
                                 fg=self.colors['text_secondary'],
                                 font=('Segoe UI', 13))
        intro_subtitle.pack(anchor='w', pady=(5, 0))
        
        # Tarjeta: Atajos principales
        self.create_modern_card(
            scrollable_frame,
            "🎮",
            self.get_text('guide_shortcuts_games_title'),
            self.get_text('guide_shortcuts_games_content'),
            '#3b82f6',  # Azul
        )
        
        # Tarjeta: Atajos de navegación
        self.create_modern_card(
            scrollable_frame,
            "🧭",
            self.get_text('guide_shortcuts_navigation_title'),
            self.get_text('guide_shortcuts_navigation_content'),
            '#8b5cf6',  # Púrpura
        )
        
        # Tarjeta: Consejos de uso
        self.create_modern_card(
            scrollable_frame,
            "💡",
            self.get_text('guide_shortcuts_tips_title'),
            self.get_text('guide_shortcuts_tips_content'),
            '#10b981',  # Verde
        )
        
        # Tarjeta: Productividad
        self.create_modern_card(
            scrollable_frame,
            "⚡",
            self.get_text('guide_shortcuts_workflow_title'),
            self.get_text('guide_shortcuts_workflow_content'),
            '#f59e0b',  # Amarillo/Naranja
            action_button={
                'text': self.get_text('guide_shortcuts_open_settings'),
                'command': self.show_config_dialog
            }
        )
        
        self.configure_guide_scrolling(parent, canvas, scrollbar, scrollable_frame)

    def show_config_dialog(self):
        """Mostrar ventana de configuración con diseño profesional"""
        config_window = tk.Toplevel(self.root)
        config_window.withdraw()  # Ocultar la ventana inicialmente
        config_window.title(self.get_text('config_title'))
        center_window_on_primary_monitor(config_window, 780, 820)
        config_window.configure(bg=self.colors['bg_dark'])
        config_window.resizable(True, True)  # Permitir redimensionar para mayor flexibilidad
        self.apply_window_icon(config_window)
        
        # Centrar la ventana
        config_window.transient(self.root)
        
        main_frame = tk.Frame(config_window, bg=self.colors['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=22)
        
        header_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        header_frame.pack(fill=tk.X, pady=(0, 14))

        title_label = tk.Label(header_frame,
                              text=self.get_text('config_title'), 
                              bg=self.colors['bg_dark'],
                              fg=self.colors['text_primary'],
                              font=('Segoe UI', 23, 'bold'))
        title_label.pack(anchor='center', pady=(4, 0))
        
        separator1 = tk.Frame(main_frame, bg=self.colors['bg_light'], height=1)
        separator1.pack(fill=tk.X, pady=(0, 14))

        settings_style = ttk.Style(config_window)
        settings_style.configure(
            'Settings.TCombobox',
            fieldbackground=self.colors['bg_dark'],
            background=self.colors['bg_medium'],
            foreground=self.colors['text_primary'],
            arrowcolor=self.colors['accent'],
            bordercolor=self.colors['bg_light'],
            lightcolor=self.colors['bg_light'],
            darkcolor=self.colors['bg_dark'],
            padding=(10, 8),
            font=('Segoe UI', 10),
        )
        settings_style.map(
            'Settings.TCombobox',
            fieldbackground=[('readonly', self.colors['bg_dark'])],
            foreground=[('readonly', self.colors['text_primary'])],
            selectbackground=[('readonly', self.colors['bg_dark'])],
            selectforeground=[('readonly', self.colors['text_primary'])],
        )

        settings_area = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        settings_area.pack(fill=tk.BOTH, expand=True)
        settings_canvas = tk.Canvas(
            settings_area,
            bg=self.colors['bg_dark'],
            highlightthickness=0,
            bd=0,
        )
        settings_scrollbar = ttk.Scrollbar(
            settings_area, orient=tk.VERTICAL, command=settings_canvas.yview
        )
        settings_content = tk.Frame(settings_canvas, bg=self.colors['bg_dark'])
        settings_content.bind(
            '<Configure>',
            lambda _event: settings_canvas.configure(
                scrollregion=settings_canvas.bbox('all')
            ),
        )
        settings_canvas_window = settings_canvas.create_window(
            (0, 0), window=settings_content, anchor='nw'
        )
        settings_canvas.configure(yscrollcommand=settings_scrollbar.set)
        settings_canvas.bind(
            '<Configure>',
            lambda event: settings_canvas.itemconfigure(
                settings_canvas_window, width=event.width
            ),
        )
        settings_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        settings_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === SECCIÓN DE IDIOMA ===
        language_card = self.create_config_card(settings_content)
        
        # Combobox para seleccionar idioma
        languages = [
            ('es', self.get_text('spanish')),
            ('en', self.get_text('english')),
            ('fr', self.get_text('french')),
            ('de', self.get_text('german')),
            ('it', self.get_text('italian')),
            ('pt', self.get_text('portuguese')),
            ('nl', self.get_text('dutch')),
            ('ru', self.get_text('russian')),
            ('ja', self.get_text('japanese')),
            ('zh', self.get_text('chinese'))
        ]
        
        # Variable para almacenar solo el código del idioma
        self.temp_language = tk.StringVar(value=self.current_language)
        
        language_combo = ttk.Combobox(language_card,
                                     state='readonly',
                                     width=25,
                                     style='Settings.TCombobox')
        
        # Configurar valores y selección actual
        lang_display_values = {lang[0]: lang[1] for lang in languages}
        language_combo['values'] = list(lang_display_values.values())
        language_combo.set(lang_display_values.get(self.current_language, self.get_text('spanish')))
        
        # Manejar cambio de selección de idioma
        def on_language_change(event):
            selected_display = language_combo.get()
            for code, display in lang_display_values.items():
                if display == selected_display:
                    self.temp_language.set(code)
                    break
        
        language_combo.bind('<<ComboboxSelected>>', on_language_change)
        language_icon = tk.Label(
            language_card,
            text='🌐',
            bg=self.colors['accent'],
            fg='white',
            font=('Segoe UI', 16, 'bold'),
            width=3,
            height=1,
        )
        language_icon.pack(side=tk.LEFT, padx=(14, 0), pady=12, ipady=5)
        language_info = tk.Frame(language_card, bg=self.colors['bg_light'])
        language_info.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(12, 12), pady=12)
        tk.Label(
            language_info,
            text=self.get_text('language_label'),
            bg=self.colors['bg_light'],
            fg=self.colors['text_primary'],
            font=('Segoe UI', 11, 'bold'),
        ).pack(anchor='w')
        tk.Label(
            language_info,
            text=self.get_text('config_section_language_desc'),
            bg=self.colors['bg_light'],
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 9),
        ).pack(anchor='w', pady=(3, 0))
        language_combo.pack(side=tk.RIGHT, padx=14, pady=12)

        # === SECCIÓN DE TEMA ===
        theme_card = self.create_config_card(settings_content)

        # Combobox para seleccionar tema
        themes = [
            ('slate', self.get_text('theme_slate')),
            ('dark', self.get_text('theme_dark')),
            ('light', self.get_text('theme_light')),
            ('blue', self.get_text('theme_blue')),
            ('green', self.get_text('theme_green')),
            ('cyberpunk', self.get_text('theme_cyberpunk')),
            ('gaming_rgb', self.get_text('theme_gaming_rgb')),
            ('retro_arcade', self.get_text('theme_retro_arcade')),
            ('midnight_gaming', self.get_text('theme_midnight_gaming')),
            ('esports', self.get_text('theme_esports'))
        ]
        
        # Variable para almacenar solo el código del tema
        self.temp_theme = tk.StringVar(value=self.current_theme)
        
        theme_combo = ttk.Combobox(theme_card,
                                  state='readonly',
                                  width=25,
                                  style='Settings.TCombobox')
        
        # Configurar valores y selección actual
        theme_display_values = {theme[0]: theme[1] for theme in themes}
        theme_combo['values'] = list(theme_display_values.values())
        theme_combo.set(theme_display_values.get(self.current_theme, self.get_text('theme_slate')))
        
        # Manejar cambio de selección de tema
        def on_theme_change(event):
            selected_display = theme_combo.get()
            for code, display in theme_display_values.items():
                if display == selected_display:
                    self.temp_theme.set(code)
                    break
        
        theme_combo.bind('<<ComboboxSelected>>', on_theme_change)
        theme_icon = tk.Label(
            theme_card,
            text='🎨',
            bg=self.colors['accent'],
            fg='white',
            font=('Segoe UI', 15, 'bold'),
            width=3,
            height=1,
        )
        theme_icon.pack(side=tk.LEFT, padx=(14, 0), pady=12, ipady=5)
        theme_info = tk.Frame(theme_card, bg=self.colors['bg_light'])
        theme_info.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(12, 12), pady=12)
        tk.Label(
            theme_info,
            text=self.get_text('theme_label'),
            bg=self.colors['bg_light'],
            fg=self.colors['text_primary'],
            font=('Segoe UI', 11, 'bold'),
        ).pack(anchor='w')
        tk.Label(
            theme_info,
            text=self.get_text('config_section_theme_desc'),
            bg=self.colors['bg_light'],
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 9),
        ).pack(anchor='w', pady=(3, 0))
        theme_combo.pack(side=tk.RIGHT, padx=14, pady=12)
        
        # === SECCIÓN DE INICIO AUTOMÁTICO ===
        self.create_config_section(settings_content, "🚀", self.get_text('startup_label'),
                                  self.get_text('config_section_startup_desc'))
        
        startup_card = self.create_config_card(settings_content)
        
        # Variable para el checkbox del inicio automático
        actual_startup_status = self.check_startup_status()
        self.temp_startup = tk.BooleanVar(value=actual_startup_status)
        
        # Frame contenedor para el checkbox con hover mejorado
        startup_option_frame = tk.Frame(startup_card, bg=self.colors['bg_light'])
        startup_option_frame.pack(fill=tk.X, padx=12, pady=10)
        
        # CHECKBOX con diseño integrado
        startup_checkbox = tk.Checkbutton(startup_option_frame,
                                         text=self.get_text('startup_auto_start_label'),
                                         variable=self.temp_startup,
                                         bg=self.colors['bg_light'],
                                         fg=self.colors['text_primary'],
                                         selectcolor=self.colors['accent'],
                                         activebackground=self.colors['bg_light'],
                                         activeforeground=self.colors['text_primary'],
                                         font=('Segoe UI', 11, 'bold'),
                                         relief='flat',
                                         borderwidth=0,
                                         highlightthickness=0,
                                         highlightbackground=self.colors['bg_light'],
                                         highlightcolor=self.colors['bg_light'],
                                         padx=8,
                                         pady=8,
                                         cursor='hand2',
                                         anchor='w')
        startup_checkbox.pack(fill=tk.X)
        
        # === SECCIÓN DE ATAJOS DE TECLADO ===
        self.create_config_section(settings_content, "⌨️", self.get_text('keybinds_label') if 'keybinds_label' in self.translations.get(self.current_language, {}) else 'Atajos de teclado',
                                  self.get_text('keybinds_desc') if 'keybinds_desc' in self.translations.get(self.current_language, {}) else 'Personaliza los atajos de teclado')
        
        keybinds_card = self.create_config_card(settings_content)
        
        keybinds_descriptions = {
            'add_game': self.get_text('add_game_label'),
            'config': self.get_text('config_menu'),
            'help': self.get_text('help_label'),
            'search': self.get_text('search_label'),
            'clear_search': self.get_text('clear_search_label'),
            'refresh': self.get_text('refresh_label'),
            'favorites': self.get_text('favorites_label'),
            'exit': self.get_text('exit_menu')
        }
        
        self.temp_keybinds = {}
        
        keybind_widgets = tk.Frame(keybinds_card, bg=self.colors['bg_light'])
        keybind_widgets.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        header_frame = tk.Frame(keybind_widgets, bg=self.colors['bg_light'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)
        
        header_label = tk.Label(header_frame, text=self.get_text('keybinds_label'), bg=self.colors['bg_light'], fg=self.colors['text_secondary'], font=('Segoe UI', 9, 'bold'))
        header_label.grid(row=0, column=0, sticky='w', padx=5)
        
        header_command = tk.Label(header_frame, text=self.get_text('command'), bg=self.colors['bg_light'], fg=self.colors['text_secondary'], font=('Segoe UI', 9, 'bold'))
        header_command.grid(row=0, column=1, sticky='e', padx=8)
        
        reset_keybinds_btn = tk.Button(header_frame, 
                                      text='↻',
                                      bg=self.colors['bg_medium'],
                                      fg='white',
                                      font=('Segoe UI', 11, 'bold'),
                                      relief='flat',
                                      borderwidth=0,
                                      padx=12,
                                      pady=5,
                                      cursor='hand2',
                                      command=lambda: self.reset_keybinds_to_default(self.temp_keybinds),
                                      activebackground=self.colors.get('accent_hover', self.colors['accent']),
                                      activeforeground='white')
        reset_keybinds_btn.grid(row=0, column=2, padx=5)
        
        for key_id, desc in keybinds_descriptions.items():
            keybind_row = tk.Frame(
                keybind_widgets,
                bg=self.colors['bg_medium'],
                highlightthickness=1,
                highlightbackground=self.colors['bg_light'],
            )
            keybind_row.pack(fill=tk.X, pady=4)
            keybind_row.grid_columnconfigure(0, weight=1)
            
            label = tk.Label(keybind_row, text=desc, bg=self.colors['bg_medium'], fg=self.colors['text_primary'], font=('Segoe UI', 10), anchor='w')
            label.grid(row=0, column=0, sticky='ew', padx=10, pady=8)
            
            self.temp_keybinds[key_id] = tk.StringVar(value=self.keybinds.get(key_id, self.default_keybinds.get(key_id, '')))
            
            entry = tk.Entry(keybind_row, textvariable=self.temp_keybinds[key_id], bg=self.colors['bg_dark'], fg=self.colors['accent'], font=('Segoe UI', 10, 'bold'), state='readonly', relief='flat', borderwidth=0, width=18, justify='center', readonlybackground=self.colors['bg_dark'])
            entry.grid(row=0, column=1, padx=5, pady=8)
            
            capture_btn = tk.Button(keybind_row, 
                                   text=self.get_text('capture_button'),
                                   bg=self.colors['accent'],
                                   fg='white',
                                   font=('Segoe UI', 9, 'bold'),
                                   relief='flat',
                                   borderwidth=0,
                                   padx=14,
                                   pady=6,
                                   cursor='hand2',
                                   command=lambda k=key_id: self.capture_keybind_dialog(k, config_window),
                                   activebackground=self.colors.get('accent_hover', self.colors['accent']),
                                   activeforeground='white')
            capture_btn.grid(row=0, column=2, padx=5, pady=8)
        
        button_container = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        button_container.pack(side=tk.BOTTOM, fill=tk.X, pady=(14, 0))
        tk.Frame(button_container, bg=self.colors['bg_light'], height=1).pack(
            side=tk.TOP, fill=tk.X, pady=(0, 12)
        )
        
        # BOTÓN CANCELAR - más pequeño
        cancel_btn = tk.Button(button_container,
                              text=self.get_text('cancel'),
                              bg=self.colors['bg_medium'],
                              fg=self.colors['text_primary'],
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat',
                              borderwidth=0,
                              padx=18,
                              pady=9,
                              cursor='hand2',
                              command=config_window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # BOTÓN GUARDAR CAMBIOS - más pequeño
        save_btn = tk.Button(button_container,
                            text=self.get_text('save_changes'),
                            bg=self.colors['accent'],
                            fg='white',
                            font=('Segoe UI', 10, 'bold'),
                            relief='flat',
                            borderwidth=0,
                            padx=22,
                            pady=9,
                            cursor='hand2',
                            command=lambda: self.apply_config_changes(config_window, language_combo, theme_combo, 
                                                                   lang_display_values, theme_display_values,
                                                                   title_label,
                                                            save_btn, cancel_btn))
        save_btn.pack(side=tk.RIGHT)
               
        # Efectos hover para los botones rediseñados
        def on_save_enter(event):
            save_btn.configure(bg=self.colors['accent_hover'] if 'accent_hover' in self.colors else '#0056b3')
        
        def on_save_leave(event):
            save_btn.configure(bg=self.colors['accent'])
        
        def on_cancel_enter(event):
            cancel_btn.configure(bg=self.colors['bg_light'])
        
        def on_cancel_leave(event):
            cancel_btn.configure(bg=self.colors['bg_medium'])
        
        # Binding de eventos
        save_btn.bind('<Enter>', on_save_enter)
        save_btn.bind('<Leave>', on_save_leave)
        
        cancel_btn.bind('<Enter>', on_cancel_enter)
        cancel_btn.bind('<Leave>', on_cancel_leave)

        def scroll_settings(event):
            units = mousewheel_units(event)
            if units:
                settings_canvas.yview_scroll(units, 'units')
            return 'break'

        def bind_settings_scroll(widget):
            widget.bind('<MouseWheel>', scroll_settings, add='+')
            widget.bind('<Button-4>', scroll_settings, add='+')
            widget.bind('<Button-5>', scroll_settings, add='+')
            for child in widget.winfo_children():
                bind_settings_scroll(child)

        bind_settings_scroll(settings_content)
        settings_canvas.bind('<MouseWheel>', scroll_settings, add='+')
        settings_canvas.bind('<Button-4>', scroll_settings, add='+')
        settings_canvas.bind('<Button-5>', scroll_settings, add='+')
        
        # Bind para Enter - hacer click en guardar
        def on_enter_press(event):
            self.apply_config_changes(config_window, language_combo, theme_combo, 
                                    lang_display_values, theme_display_values,
                                    title_label,
                                    save_btn, cancel_btn)
        
        config_window.bind('<Return>', on_enter_press)
        
        # Mostrar la ventana una vez que está completamente configurada
        config_window.deiconify()
        config_window.after_idle(config_window.grab_set)
    
    def capture_keybind_dialog(self, key_id, parent_window):
        """Abrir diálogo para capturar combinación de teclas"""
        capture_window = tk.Toplevel(parent_window)
        capture_window.withdraw()
        capture_window.title(self.get_text('config_title'))
        capture_window.geometry("400x150")
        capture_window.configure(bg=self.colors['bg_dark'])
        capture_window.resizable(False, False)
        self.apply_window_icon(capture_window)
        
        capture_window.transient(parent_window)
        capture_window.grab_set()
        
        capture_text = self.get_text('capture_keybind') if 'capture_keybind' in self.translations.get(self.current_language, {}) else 'Presiona la combinación de teclas...'
        cancel_text = self.get_text('capture_cancel') if 'capture_cancel' in self.translations.get(self.current_language, {}) else '(Presiona ESC para cancelar)'
        
        label = tk.Label(capture_window, 
                        text=capture_text,
                        bg=self.colors['bg_dark'],
                        fg=self.colors['text_primary'],
                        font=('Segoe UI', 14, 'bold'),
                        pady=20)
        label.pack()
        
        info_label = tk.Label(capture_window,
                             text=cancel_text,
                             bg=self.colors['bg_dark'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 10))
        info_label.pack()
        
        captured_keys = {'control': False, 'shift': False, 'alt': False, 'keys': []}
        
        def on_key_press(event):
            captured_keys['keys'] = []
            
            if event.state & 0x0004:
                captured_keys['control'] = True
            if event.state & 0x0001:
                captured_keys['shift'] = True
            if event.state & 0x0008:
                captured_keys['alt'] = True
            
            keysym = event.keysym.lower()
            
            if keysym == 'escape':
                capture_window.destroy()
                return
            
            if keysym not in ['control_l', 'control_r', 'shift_l', 'shift_r', 'alt_l', 'alt_r']:
                captured_keys['keys'].append(event.keysym)
            
            if keysym not in ['control_l', 'control_r', 'shift_l', 'shift_r', 'alt_l', 'alt_r']:
                keybind_str = self._format_keybind(captured_keys)
                self.temp_keybinds[key_id].set(keybind_str)
                capture_window.destroy()
        
        capture_window.bind('<KeyPress>', on_key_press)
        
        x = (capture_window.winfo_screenwidth() - capture_window.winfo_width()) // 2
        y = (capture_window.winfo_screenheight() - capture_window.winfo_height()) // 2
        capture_window.geometry(f"+{x}+{y}")
        
        capture_window.update_idletasks()
        capture_window.deiconify()
        capture_window.focus_set()
    
    def _format_keybind(self, captured_keys):
        """Formatear la combinación de teclas en formato Tkinter"""
        parts = []
        
        if captured_keys['control']:
            parts.append('Control')
        if captured_keys['shift']:
            parts.append('Shift')
        if captured_keys['alt']:
            parts.append('Alt')
        
        if captured_keys['keys']:
            key = captured_keys['keys'][0]
            if key.startswith('F') and len(key) > 1 and key[1:].isdigit():
                parts.append(key)
            elif key in ['space', 'Tab', 'Return', 'Escape']:
                parts.append(key)
            else:
                parts.append(key.lower() if len(key) == 1 else key)
        
        if parts:
            return '<' + '-'.join(parts) + '>'
        return ''
    
    def create_config_section(self, parent, icon, title, description):
        """Crear una sección de configuración con título e icono"""
        section_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        section_frame.pack(fill=tk.X, pady=(8, 8))
        
        # Frame para el título con icono
        title_frame = tk.Frame(section_frame, bg=self.colors['bg_dark'])
        title_frame.pack(fill=tk.X)
        
        # Icono
        icon_label = tk.Label(title_frame,
                             text=icon,
                             bg=self.colors['accent'],
                             fg='white',
                             font=('Segoe UI', 14, 'bold'),
                             width=3,
                             height=1)
        icon_label.pack(side=tk.LEFT, padx=(0, 12), ipady=3)
        
        # Contenedor para título y descripción
        text_frame = tk.Frame(title_frame, bg=self.colors['bg_dark'])
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Título
        title_label = tk.Label(text_frame,
                              text=title,
                              bg=self.colors['bg_dark'],
                              fg=self.colors['text_primary'],
                              font=('Segoe UI', 11, 'bold'))
        title_label.pack(anchor='w')
        
        # Descripción
        desc_label = tk.Label(text_frame,
                             text=description,
                             bg=self.colors['bg_dark'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 9))
        desc_label.pack(anchor='w')

        tk.Frame(section_frame, bg=self.colors['bg_light'], height=1).pack(
            fill=tk.X, pady=(10, 0)
        )
        
        return section_frame
    
    def create_config_card(self, parent):
        """Crear una tarjeta de configuración estilizada"""
        card_frame = tk.Frame(
            parent,
            bg=self.colors['bg_light'],
            relief='flat',
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.colors['bg_medium'],
            highlightcolor=self.colors['bg_medium'],
        )
        card_frame.pack(fill=tk.X, pady=(0, 12), ipady=8)
        
        return card_frame
    
    def reset_keybinds_to_default(self, temp_keybinds):
        """Restablecer atajos de teclado a los valores predeterminados"""
        for key_id, default_key in self.default_keybinds.items():
            if key_id in temp_keybinds:
                temp_keybinds[key_id].set(default_key)
    
    def apply_config_changes(self, config_window, language_combo=None, theme_combo=None, 
                           lang_display_values=None, theme_display_values=None,
                           title_label=None, save_btn=None, cancel_btn=None):
        """Aplicar cambios de configuración"""
        # Obtener los valores usando las variables temporales
        new_language = self.temp_language.get()
        new_theme = self.temp_theme.get()
        new_startup = self.temp_startup.get()
        
        changes_made = False
        startup_message = ""
        language_changed = False
        
        if new_language != self.current_language:
            self.current_language = new_language
            changes_made = True
            language_changed = True
            
        if new_theme != self.current_theme:
            # Detener animaciones del tema anterior
            self.stop_theme_animations()
            self.current_theme = new_theme
            changes_made = True
            # Actualizar colores y reiniciar animaciones
            self.colors = self.themes[self.current_theme]
            self.start_theme_animations()
        
        # Manejar cambios en el inicio automático
        current_startup_status = self.check_startup_status()
        if new_startup != current_startup_status:
            if self.set_startup_registry(new_startup):
                changes_made = True
                if new_startup:
                    startup_message = self.get_text('startup_enabled')
                else:
                    startup_message = self.get_text('startup_disabled')
            else:
                startup_message = self.get_text('startup_error')
        
        # Manejar cambios en atajos de teclado
        if hasattr(self, 'temp_keybinds'):
            try:
                for key_id, var in self.temp_keybinds.items():
                    new_keybind = var.get().strip()
                    current_keybind = self.keybinds.get(key_id, '')
                    if new_keybind and new_keybind != current_keybind:
                        self.keybinds[key_id] = new_keybind
                        changes_made = True
                
                if changes_made:
                    self.setup_keyboard_shortcuts()
            except Exception as e:
                print(f"Error updating keybinds: {e}")
        
        if changes_made:
            self.save_config()
            
            # Si cambió el idioma, actualizar la ventana de configuración primero
            if language_changed and title_label and save_btn and cancel_btn:
                # Actualizar título de la ventana
                config_window.title(self.get_text('config_title'))
                
                # Actualizar etiquetas principales
                title_label.configure(text=self.get_text('config_title'))
                
                # Actualizar botones
                save_btn.configure(text=self.get_text('save_changes'))
                cancel_btn.configure(text=self.get_text('cancel'))
                
                # Actualizar comboboxes si están disponibles
                if language_combo and lang_display_values:
                    # Actualizar valores del combo de idiomas
                    languages = [
                        ('es', self.get_text('spanish')),
                        ('en', self.get_text('english')),
                        ('fr', self.get_text('french')),
                        ('de', self.get_text('german')),
                        ('it', self.get_text('italian')),
                        ('pt', self.get_text('portuguese')),
                        ('nl', self.get_text('dutch')),
                        ('ru', self.get_text('russian')),
                        ('ja', self.get_text('japanese')),
                        ('zh', self.get_text('chinese'))
                    ]
                    updated_lang_values = {lang[0]: lang[1] for lang in languages}
                    language_combo['values'] = list(updated_lang_values.values())
                    language_combo.set(updated_lang_values.get(self.current_language, self.get_text('spanish')))
                
                if theme_combo and theme_display_values:
                    # Actualizar valores del combo de temas
                    themes = [
                        ('slate', self.get_text('theme_slate')),
                        ('dark', self.get_text('theme_dark')),
                        ('light', self.get_text('theme_light')),
                        ('blue', self.get_text('theme_blue')),
                        ('green', self.get_text('theme_green'))
                    ]
                    updated_theme_values = {theme[0]: theme[1] for theme in themes}
                    theme_combo['values'] = list(updated_theme_values.values())
                    theme_combo.set(updated_theme_values.get(self.current_theme, self.get_text('theme_slate')))
                
                # Actualizar toda la interfaz principal
                self.refresh_interface()
            
            # Preparar mensaje de confirmación
            config_message = self.get_text('config_saved')
            if startup_message:
                config_message += f"\n{startup_message}"
            
            # Mostrar mensaje de confirmación
            import tkinter.messagebox as messagebox
            messagebox.showinfo(self.get_text('success'), config_message)
            
            # Cerrar ventana de configuración solo después de actualizar todo
            config_window.destroy()
            
            # Si no hubo cambio de idioma, actualizar la interfaz
            if not language_changed:
                self.refresh_interface()
        else:
            # Si solo se cambió el inicio automático sin otros cambios
            if startup_message:
                import tkinter.messagebox as messagebox
                messagebox.showinfo(self.get_text('success'), startup_message)
            config_window.destroy()
    
    def refresh_interface(self):
        """Actualizar toda la interfaz con el nuevo idioma y tema"""
        # Recargar traducciones por si cambió el idioma
        self.translations = self.load_translations()
        
        # Reconfigurar estilos con el nuevo tema
        self.setup_styles()
        
        # Actualizar color de fondo de la ventana principal
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Actualizar título de la ventana con el nuevo idioma
        self.root.title('AVILON')
        
        # Limpiar la barra de menú actual
        self.root.config(menu="")
        
        # Recrear la barra de menú con las nuevas traducciones
        self.create_menu_bar()
        
        # Actualizar la interfaz principal
        # Destruir y recrear los elementos principales
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.destroy()
        
        # Recrear la interfaz
        self.create_main_interface()
        self.refresh_games_display()
        
        # Actualizar colores de la barra de búsqueda después de recrear la interfaz
        self.root.after(100, self.update_search_bar_colors)
    
    def create_main_interface(self):
        """Crear la interfaz principal"""
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=28, pady=(22, 18))
        self.create_content_area(main_frame)
    
    def create_content_area(self, parent):
        """Crear área de contenido principal"""
        content_frame = ttk.Frame(parent, style='Dark.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(content_frame, style='Dark.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 18))

        brand_frame = ttk.Frame(header_frame, style='Dark.TFrame')
        brand_frame.pack(fill=tk.X, pady=(0, 8))
        brand_frame.configure(height=36)
        brand_frame.pack_propagate(False)
        self.create_search_bar(brand_frame)

        toolbar = ttk.Frame(header_frame, style='Dark.TFrame')
        toolbar.pack(fill=tk.X)
        self.create_filter_buttons(toolbar)

        self.create_scrollable_games_area(content_frame)
    
    def create_filter_buttons(self, parent):
        """Crear filtros compactos alineados a la derecha de la biblioteca."""
        total_count = len(self.games)
        favorites_count = len([game for game in self.games if game.get('favorite', False)])
        recent_count = sum(1 for game in self.games if game.get('last_opened_at'))
        self.filter_frame = tk.Frame(
            parent,
            bg=self.colors['bg_dark'],
            padx=0,
            pady=0,
        )
        self.filter_frame.pack(side=tk.RIGHT, anchor=tk.E)

        self.all_button = tk.Button(
            self.filter_frame,
            text=f"{self.get_text('all_games')}   {total_count}",
            font=(self.ui_font_family, 10, 'bold'),
            relief='flat',
            bd=0,
            highlightthickness=0,
            padx=16,
            pady=8,
            cursor='hand2',
            command=lambda: self.set_favorites_filter('all'),
        )
        self.all_button.pack(side=tk.LEFT)

        self.favorites_button = tk.Button(
            self.filter_frame,
            text=f"{self.get_text('favorites')}   {favorites_count}",
            font=(self.ui_font_family, 10, 'bold'),
            relief='flat',
            bd=0,
            highlightthickness=0,
            padx=16,
            pady=8,
            cursor='hand2',
            command=lambda: self.set_favorites_filter('favorites'),
        )
        self.favorites_button.pack(side=tk.LEFT)

        self.recent_button = tk.Button(
            self.filter_frame,
            text=f"{self.get_text('recent')}   {recent_count}",
            font=(self.ui_font_family, 10, 'bold'),
            relief='flat',
            bd=0,
            highlightthickness=0,
            padx=16,
            pady=8,
            cursor='hand2',
            command=lambda: self.set_favorites_filter('recent'),
        )
        self.recent_button.pack(side=tk.LEFT)

        for button in (self.all_button, self.favorites_button, self.recent_button):
            button.bind(
                '<Enter>',
                lambda event, item=button: self._set_filter_button_hover(item, True),
            )
            button.bind(
                '<Leave>',
                lambda event, item=button: self._set_filter_button_hover(item, False),
            )
        self._refresh_filter_button_styles()

    def _set_filter_button_hover(self, button, hovered):
        selected_button = {
            'all': self.all_button,
            'favorites': self.favorites_button,
            'recent': self.recent_button,
        }.get(self.favorites_filter, self.all_button)
        if button is selected_button:
            background = self.colors['accent_hover'] if hovered else self.colors['accent']
            foreground = self.colors['bg_dark']
        else:
            background = self.colors['bg_medium'] if hovered else self.colors['bg_light']
            foreground = self.colors['text_secondary']
        button.configure(bg=background, fg=foreground, activebackground=background,
                         activeforeground=foreground)

    def _refresh_filter_button_styles(self):
        if not all(
            hasattr(self, name) and getattr(self, name).winfo_exists()
            for name in ('all_button', 'favorites_button', 'recent_button')
        ):
            return
        self._set_filter_button_hover(self.all_button, False)
        self._set_filter_button_hover(self.favorites_button, False)
        self._set_filter_button_hover(self.recent_button, False)
    
    def create_search_bar(self, parent):
        """Crear barra de búsqueda mejorada con efectos y transiciones"""
        # Variable para el texto de búsqueda
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.on_search_change)
        
        container = ttk.Frame(parent, style='Dark.TFrame')
        container.pack(side=tk.RIGHT)

        self.search_toggle_button = tk.Canvas(
            container,
            width=36,
            height=36,
            bg=self.colors['bg_dark'],
            highlightthickness=0,
            bd=0,
            cursor='hand2',
        )
        self._draw_search_toggle_icon(self.colors['text_primary'])
        self.search_toggle_button.bind('<Button-1>', lambda event: self.toggle_search_bar())
        self.search_toggle_button.bind(
            '<Enter>',
            lambda event: self._draw_search_toggle_icon(self.colors['accent']),
        )
        self.search_toggle_button.bind(
            '<Leave>',
            lambda event: self._draw_search_toggle_icon(self.colors['text_primary']),
        )
        self.search_toggle_button.pack(side=tk.RIGHT, anchor=tk.N, pady=(0, 8))
        
        self.search_bar_frame = tk.Frame(container, 
                                        bg=self.colors['bg_light'],
                                        relief='flat',
                                        bd=0,
                                        highlightthickness=1,
                                        highlightcolor=self.colors['accent'],
                                        highlightbackground=self.colors['bg_medium'])
        self.search_bar_visible = False
        
        inner_frame = tk.Frame(self.search_bar_frame, bg=self.colors['bg_light'])
        inner_frame.pack(padx=12, pady=8)
        
        # Ícono de búsqueda animado
        self.search_icon = tk.Label(inner_frame, 
                                   text="🔍",
                                   bg=self.colors['bg_light'],
                                   fg=self.colors['text_muted'],
                                   font=(self.ui_font_family, 11))
        self.search_icon.pack(side=tk.LEFT, padx=(0, 6))
        
        # Campo de entrada con estilo mejorado usando colores del tema
        # Configurar colores específicos para cada tema con mejor contraste
        if self.current_theme == 'light':
            entry_bg = '#ffffff'
            entry_fg = '#333333'
            insert_color = '#333333'
            select_bg = '#0078d4'
            select_fg = '#ffffff'
        elif self.current_theme == 'slate':
            entry_bg = self.colors['bg_light']
            entry_fg = self.colors['text_primary']
            insert_color = self.colors['accent']
            select_bg = self.colors['accent']
            select_fg = '#0b1020'
        elif self.current_theme == 'dark':
            entry_bg = '#505050'  # Fondo más claro que el tema para mejor contraste
            entry_fg = '#ffffff'  # Texto blanco
            insert_color = '#ffffff'  # Cursor blanco
            select_bg = '#4a9eff'
            select_fg = '#ffffff'
        elif self.current_theme == 'blue':
            entry_bg = '#4f7bc7'  # Fondo más claro que el tema
            entry_fg = '#ffffff'
            insert_color = '#ffffff'
            select_bg = '#60a5fa'
            select_fg = '#ffffff'
        elif self.current_theme == 'green':
            entry_bg = '#0d8f6b'  # Fondo más claro que el tema
            entry_fg = '#ffffff'
            insert_color = '#ffffff'
            select_bg = '#34d399'
            select_fg = '#ffffff'
        elif self.current_theme == 'cyberpunk':
            entry_bg = '#000000'  # Fondo negro para cyberpunk
            entry_fg = '#ffffff'  # Texto blanco
            insert_color = '#ff00ff'  # Cursor magenta para el tema cyberpunk
            select_bg = '#ff00ff'
            select_fg = '#000000'
        elif self.current_theme == 'gaming_rgb':
            entry_bg = '#0d1117'  # Fondo muy oscuro para gaming rgb
            entry_fg = '#ffffff'  # Texto blanco
            insert_color = '#ff6b35'  # Cursor naranja acorde al tema
            select_bg = '#ff6b35'
            select_fg = '#ffffff'
        elif self.current_theme == 'retro_arcade':
            entry_bg = '#1a0033'  # Fondo muy oscuro para retro arcade
            entry_fg = '#ffffff'  # Texto blanco
            insert_color = '#ffff00'  # Cursor amarillo acorde al tema
            select_bg = '#ffff00'
            select_fg = '#1a0033'
        elif self.current_theme == 'midnight_gaming':
            entry_bg = '#000000'  # Fondo negro para midnight gaming
            entry_fg = '#ffffff'  # Texto blanco
            insert_color = '#00d4ff'  # Cursor cyan acorde al tema
            select_bg = '#00d4ff'
            select_fg = '#000000'
        elif self.current_theme == 'esports':
            entry_bg = '#0f1419'  # Fondo muy oscuro para esports
            entry_fg = '#ffffff'
            insert_color = '#c9aa71'  # Cursor dorado acorde al tema
            select_bg = '#c9aa71'
            select_fg = '#0f1419'
        else:
            # Fallback para cualquier tema nuevo
            entry_bg = '#ffffff'
            entry_fg = '#333333'
            insert_color = '#333333'
            select_bg = '#0078d4'
            select_fg = '#ffffff'
        
        self.search_entry = tk.Entry(inner_frame,
                                    textvariable=self.search_var,
                                    font=(self.ui_font_family, 10),
                                    width=28,
                                    bg=entry_bg,
                                    fg=entry_fg,
                                    insertbackground=insert_color,
                                    selectbackground=select_bg,
                                    selectforeground=select_fg,
                                    relief='flat',
                                    bd=0,
                                    highlightthickness=0)
        self.search_entry.pack(side=tk.LEFT, padx=3)
        
        # Botón limpiar con efectos hover usando colores del tema
        self.clear_button = tk.Button(inner_frame,
                                     text="✗",
                                     font=(self.ui_font_family, 10, 'bold'),
                                     bg=self.colors['bg_light'],
                                     fg=self.colors['text_muted'],
                                     activebackground='#ff4444',
                                     activeforeground='white',
                                     relief='flat',
                                     bd=0,
                                     width=2,
                                     cursor='hand2',
                                     command=self.clear_search)
        self.clear_button.pack(side=tk.LEFT, padx=(6, 0))
        
        # Configurar placeholder y efectos
        self.setup_search_effects()
        self.setup_search_placeholder()
        if not getattr(self, '_search_click_binding_set', False):
            self.root.bind_all('<Button-1>', self._on_global_search_click, add='+')
            self._search_click_binding_set = True

    def toggle_search_bar(self):
        if self.search_bar_visible:
            self.close_search_bar()
        else:
            self.open_search_bar()

    def _draw_search_toggle_icon(self, color):
        if not hasattr(self, 'search_toggle_button') or not self.search_toggle_button.winfo_exists():
            return
        self.search_toggle_button.delete('all')
        self.search_toggle_button.create_oval(
            8, 7, 21, 20,
            outline=color,
            width=2,
        )
        self.search_toggle_button.create_line(
            19, 18, 27, 26,
            fill=color,
            width=2,
            capstyle=tk.ROUND,
        )

    def open_search_bar(self):
        if not self.search_bar_visible and self.search_bar_frame.winfo_exists():
            self.search_bar_frame.pack(side=tk.RIGHT, padx=(0, 8))
            self.search_bar_visible = True
        self.search_entry.focus_set()

    def close_search_bar(self):
        if self.search_bar_visible and self.search_bar_frame.winfo_exists():
            self.search_bar_frame.pack_forget()
            self.search_bar_visible = False

    def _on_global_search_click(self, event):
        if not getattr(self, 'search_bar_visible', False):
            return

        widget = event.widget
        while widget is not None:
            if widget is self.search_bar_frame or widget is self.search_toggle_button:
                return
            widget = getattr(widget, 'master', None)

        self.root.after_idle(self.close_search_bar)
    
    def set_favorites_filter(self, filter_type):
        """Establecer el filtro de biblioteca activo."""
        self.favorites_filter = filter_type
        
        # Actualizar colores de botones
        if hasattr(self, 'all_button') and self.all_button.winfo_exists():
            self._refresh_filter_button_styles()
        
        # Actualizar contadores
        self.update_filter_button_counters()
        
        # Actualizar visualización de juegos
        self.refresh_games_display()
    
    def update_search_bar_colors(self):
        """Actualizar colores de la barra de búsqueda según el tema actual"""
        if hasattr(self, 'search_toggle_button') and self.search_toggle_button.winfo_exists():
            self.search_toggle_button.configure(bg=self.colors['bg_dark'])
            self._draw_search_toggle_icon(self.colors['text_primary'])

        if hasattr(self, 'search_entry') and self.search_entry.winfo_exists():
            # Configurar colores específicos para cada tema con mejor contraste
            if self.current_theme == 'light':
                entry_bg = '#ffffff'
                entry_fg = '#333333'
                insert_color = '#333333'
                select_bg = '#0078d4'
                select_fg = '#ffffff'
            elif self.current_theme == 'slate':
                entry_bg = self.colors['bg_light']
                entry_fg = self.colors['text_primary']
                insert_color = self.colors['accent']
                select_bg = self.colors['accent']
                select_fg = '#0b1020'
            elif self.current_theme == 'dark':
                entry_bg = '#505050'  # Fondo más claro que el tema para mejor contraste
                entry_fg = '#ffffff'  # Texto blanco
                insert_color = '#ffffff'  # Cursor blanco
                select_bg = '#4a9eff'
                select_fg = '#ffffff'
            elif self.current_theme == 'blue':
                entry_bg = '#4f7bc7'  # Fondo más claro que el tema
                entry_fg = '#ffffff'
                insert_color = '#ffffff'
                select_bg = '#60a5fa'
                select_fg = '#ffffff'
            elif self.current_theme == 'green':
                entry_bg = '#0d8f6b'  # Fondo más claro que el tema
                entry_fg = '#ffffff'
                insert_color = '#ffffff'
                select_bg = '#34d399'
                select_fg = '#ffffff'
            elif self.current_theme == 'cyberpunk':
                entry_bg = '#000000'
                entry_fg = '#ffffff'
                insert_color = '#ff00ff'
                select_bg = '#ff00ff'
                select_fg = '#000000'
            elif self.current_theme == 'gaming_rgb':
                entry_bg = '#0d1117'
                entry_fg = '#ffffff'
                insert_color = '#ff6b35'
                select_bg = '#ff6b35'
                select_fg = '#ffffff'
            elif self.current_theme == 'retro_arcade':
                entry_bg = '#1a0033'
                entry_fg = '#ffffff'
                insert_color = '#ffff00'
                select_bg = '#ffff00'
                select_fg = '#1a0033'
            elif self.current_theme == 'midnight_gaming':
                entry_bg = '#000000'
                entry_fg = '#ffffff'
                insert_color = '#00d4ff'
                select_bg = '#00d4ff'
                select_fg = '#000000'
            elif self.current_theme == 'esports':
                entry_bg = '#0f1419'
                entry_fg = '#ffffff'
                insert_color = '#c9aa71'
                select_bg = '#c9aa71'
                select_fg = '#0f1419'
            else:
                # Fallback para cualquier tema nuevo
                entry_bg = '#ffffff'
                entry_fg = '#333333'
                insert_color = '#333333'
                select_bg = '#0078d4'
                select_fg = '#ffffff'
            
            # Aplicar los colores al campo de entrada
            self.search_entry.configure(
                bg=entry_bg,
                fg=entry_fg,
                insertbackground=insert_color,
                selectbackground=select_bg,
                selectforeground=select_fg
            )
            
            # Actualizar también los colores del frame de la barra de búsqueda
            if hasattr(self, 'search_bar_frame') and self.search_bar_frame.winfo_exists():
                self.search_bar_frame.configure(
                    bg=self.colors['bg_light'],
                    highlightcolor=self.colors['accent'],
                    highlightbackground=self.colors['bg_dark']
                )
            
            # Actualizar ícono de búsqueda
            if hasattr(self, 'search_icon') and self.search_icon.winfo_exists():
                self.search_icon.configure(
                    bg=self.colors['bg_light'],
                    fg=self.colors['text_muted']
                )
            
            # Actualizar botón de limpiar
            if hasattr(self, 'clear_button') and self.clear_button.winfo_exists():
                self.clear_button.configure(
                    bg=self.colors['bg_light'],
                    fg=self.colors['text_muted']
                )
    
    def setup_search_effects(self):
        """Configurar efectos visuales para la barra de búsqueda"""
        # Efectos de hover para el frame de búsqueda
        def on_search_hover_enter(event):
            self.search_bar_frame.config(highlightcolor=self.colors['accent'], highlightbackground=self.colors['accent'])
            self.animate_search_icon('🔍', self.colors['accent'])
            
        def on_search_hover_leave(event):
            if self.search_entry != self.root.focus_get():
                self.search_bar_frame.config(highlightcolor=self.colors['bg_dark'], highlightbackground=self.colors['bg_dark'])
                self.animate_search_icon('🔍', self.colors['text_muted'])
        
        # Efectos de focus
        def on_search_focus_enter(event):
            self.search_bar_frame.config(highlightcolor=self.colors['accent'], highlightbackground=self.colors['accent'])
            self.animate_search_icon('🔍', self.colors['accent'])
            self.on_search_focus_in(event)
            
        def on_search_focus_leave(event):
            self.search_bar_frame.config(highlightcolor=self.colors['bg_dark'], highlightbackground=self.colors['bg_dark'])
            self.animate_search_icon('🔍', self.colors['text_muted'])
            self.on_search_focus_out(event)
        
        # Efectos para el botón limpiar
        def on_clear_hover_enter(event):
            self.clear_button.config(bg='#ff6666', fg='white')
            
        def on_clear_hover_leave(event):
            self.clear_button.config(bg=self.colors['bg_light'], fg=self.colors['text_muted'])
            
        def on_clear_click(event):
            self.clear_button.config(bg='#ff4444')
            self.root.after(100, lambda: self.clear_button.config(bg='#ff6666'))
        
        # Manejar escritura directa (sin necesidad de hacer click primero)
        def on_key_press(event):
            # Si hay placeholder activo y el usuario empieza a escribir
            if self.is_placeholder_active and event.char.isprintable():
                self.remove_placeholder()
                # No bloquear el evento, permitir que el carácter se escriba
                return None
            elif event.keysym == 'BackSpace' and not self.is_placeholder_active:
                # Si se borra todo el contenido, podríamos restaurar placeholder después
                self.root.after(1, self.check_empty_field)
                
        def on_key_release(event):
            # Verificar si el campo está vacío después de una pulsación de tecla
            if not self.is_placeholder_active:
                self.root.after(1, self.check_empty_field)
        
        # Bind eventos
        self.search_bar_frame.bind('<Enter>', on_search_hover_enter)
        self.search_bar_frame.bind('<Leave>', on_search_hover_leave)
        self.search_entry.bind('<FocusIn>', on_search_focus_enter)
        self.search_entry.bind('<FocusOut>', on_search_focus_leave)
        self.search_entry.bind('<KeyPress>', on_key_press)
        self.search_entry.bind('<KeyRelease>', on_key_release)
        self.clear_button.bind('<Enter>', on_clear_hover_enter)
        self.clear_button.bind('<Leave>', on_clear_hover_leave)
        self.clear_button.bind('<Button-1>', on_clear_click)
        
        # Efecto de pulsación suave en Enter
        def on_enter_key(event):
            self.animate_search_pulse()
            
        self.search_entry.bind('<Return>', on_enter_key)
    
    def setup_search_placeholder(self):
        """Configurar el sistema de placeholder mejorado"""
        self.placeholder_text = self.get_text('search_placeholder') if hasattr(self, 'get_text') else "Buscar juegos..."
        self.is_placeholder_active = True
        
        # Configurar placeholder inicial
        self.search_entry.insert(0, self.placeholder_text)
        self.search_entry.config(fg=self.colors['text_muted'])
        
        # Variable para rastrear el estado del placeholder
        self.search_focused = False
    
    def remove_placeholder(self):
        """Eliminar el placeholder cuando el usuario empiece a escribir"""
        if self.is_placeholder_active:
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=self.colors['text'])
            self.is_placeholder_active = False
    
    def restore_placeholder(self):
        """Restaurar el placeholder cuando el campo esté vacío"""
        if not self.is_placeholder_active and not self.search_entry.get().strip():
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, self.placeholder_text)
            self.search_entry.config(fg=self.colors['text_muted'])
            self.is_placeholder_active = True
    
    def check_empty_field(self):
        """Verificar si el campo está vacío y restaurar placeholder si es necesario"""
        if not self.is_placeholder_active and not self.search_entry.get().strip():
            # Solo restaurar placeholder si el campo no tiene foco
            if self.search_entry != self.root.focus_get():
                self.restore_placeholder()
    
    def animate_search_icon(self, icon, color):
        """Animar el ícono de búsqueda con transición de color"""
        try:
            self.search_icon.config(fg=color)
            # Efecto de pulsación sutil
            original_font = self.search_icon.cget('font')
            if isinstance(original_font, str):
                font_family, font_size = original_font.split()[0], int(original_font.split()[1])
            else:
                font_family, font_size = original_font[0], original_font[1]
            
            self.search_icon.config(font=(font_family, font_size + 1))
            self.root.after(150, lambda: self.search_icon.config(font=(font_family, font_size)))
        except:
            pass
    
    def animate_search_pulse(self):
        """Crear efecto de pulsación en la barra de búsqueda"""
        original_bg = self.search_bar_frame.cget('highlightbackground')
        
        # Secuencia de colores para el efecto de pulsación usando el color de acento del tema
        accent_color = self.colors['accent']
        colors = [accent_color, accent_color, accent_color, original_bg, original_bg]
        
        def pulse_step(step=0):
            if step < len(colors):
                self.search_bar_frame.config(highlightcolor=colors[step], highlightbackground=colors[step])
                self.root.after(50, lambda: pulse_step(step + 1))
        
        pulse_step()
    
    def on_search_focus_in(self, event):
        """Manejar cuando el campo de búsqueda recibe el foco con efectos"""
        self.search_focused = True
    # Solo eliminar placeholder si está activo, pero no automáticamente
        # Esperar a que el usuario empiece a escribir
        
            
    def on_search_focus_out(self, event):
        """Manejar cuando el campo de búsqueda pierde el foco con efectos"""
        self.search_focused = False
        
        # Restaurar placeholder si el campo está vacío
        if not self.is_placeholder_active and not self.search_entry.get().strip():
            # Animación de aparición del placeholder
            self.animate_placeholder_fade_in()
            self.restore_placeholder()
    
    def clear_search(self):
        """Limpiar la búsqueda con efectos de animación"""
        # Efecto de pulsación en el botón
        self.animate_clear_button_press()
        
        # Limpiar el contenido
        self.search_var.set('')
        self.search_entry.delete(0, tk.END)
        
        # Restaurar placeholder con animación
        self.animate_placeholder_fade_in()
        self.restore_placeholder()
        
        # Actualizar la vista de juegos para mostrar todos
        self.refresh_games_display()
        
        # Focus en el campo con efecto
        self.search_entry.focus()
        self.animate_search_pulse()
    
    def animate_placeholder_fade_out(self):
        """Animar desaparición del placeholder"""
        colors = ['#666666', '#555555', '#444444', '#333333', '#222222']
        
        def fade_step(step=0):
            if step < len(colors) and hasattr(self, 'search_entry'):
                try:
                    self.search_entry.config(fg=colors[step])
                    self.root.after(30, lambda: fade_step(step + 1))
                except:
                    pass
        
        fade_step()
    
    def animate_placeholder_fade_in(self):
        """Animar aparición del placeholder"""
        colors = ['#222222', '#333333', '#444444', '#555555', '#666666']
        
        def fade_step(step=0):
            if step < len(colors) and hasattr(self, 'search_entry'):
                try:
                    self.search_entry.config(fg=colors[step])
                    self.root.after(30, lambda: fade_step(step + 1))
                except:
                    pass
        
        fade_step()
    
    def animate_clear_button_press(self):
        """Animar pulsación del botón limpiar"""
        original_bg = self.clear_button.cget('bg')
        
        # Secuencia de colores para simular pulsación
        self.clear_button.config(bg='#ff4444', fg='white')
        self.root.after(100, lambda: self.clear_button.config(bg='#ff6666'))
        self.root.after(200, lambda: self.clear_button.config(bg=original_bg, fg='#888888'))
    
    def on_search_change(self, *args):
        """Manejar cambios en el texto de búsqueda con efectos mejorados"""
        search_text = self.search_var.get()
        
        # Si hay placeholder activo, ignorar cambios hasta que se escriba algo real
        if self.is_placeholder_active:
            return
            
        # Solo procesar búsquedas reales
        if search_text.strip():
            # Efecto sutil de typing
            self.animate_typing_effect()
            self.refresh_games_display()
        else:
            # Si se borra todo el texto, mostrar todos los juegos
            self.refresh_games_display()
    
    def animate_typing_effect(self):
        """Efecto sutil mientras se escribe"""
        try:
            # Brillo sutil en el ícono mientras se escribe
            self.search_icon.config(fg='#00ccff')
            self.root.after(300, lambda: self.search_icon.config(fg='#00aaff' if self.search_focused else '#888888'))
        except:
            pass
    
    def create_scrollable_games_area(self, parent):
        """Crear área scrollable para los juegos"""
        # Canvas sin scrollbar visible pero con funcionalidad de scroll
        self.canvas = tk.Canvas(parent, bg=self.colors['bg_dark'], 
                               highlightthickness=0)
        self.scrollable_frame = ttk.Frame(self.canvas, style='Dark.TFrame')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.games_canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        self.canvas.bind('<Configure>', self._resize_games_canvas_content)
        self.canvas.bind('<Configure>', self._on_games_canvas_resize, add='+')
        
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind mousewheel para scroll sin barra visible
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel, add='+')
        self.canvas.bind_all("<Button-4>", self._on_mousewheel, add='+')
        self.canvas.bind_all("<Button-5>", self._on_mousewheel, add='+')

    def _resize_games_canvas_content(self, event):
        self.canvas.itemconfigure(self.games_canvas_window, width=event.width)

    def _on_games_canvas_resize(self, event):
        required_columns = max(1, event.width // 294)
        if required_columns == getattr(self, '_game_grid_columns', 0):
            return

        if getattr(self, '_game_grid_refresh_pending', False):
            return
        self._game_grid_refresh_pending = True
        self.root.after_idle(self._reflow_game_cards)

    def _reflow_game_cards(self):
        self._game_grid_refresh_pending = False
        viewport_width = self.canvas.winfo_width()
        if viewport_width <= 1:
            return

        columns = max(1, viewport_width // 294)
        previous_columns = getattr(self, '_game_grid_columns', 0)
        if columns == previous_columns:
            return

        for column in range(previous_columns):
            self.scrollable_frame.grid_columnconfigure(column, weight=0, uniform='')
        for column in range(columns):
            self.scrollable_frame.grid_columnconfigure(
                column, weight=1, uniform='game-cards'
            )

        cards = [
            widget for widget in self.scrollable_frame.winfo_children()
            if widget.winfo_manager() == 'grid'
        ]
        for index, card in enumerate(cards):
            card.grid_configure(row=index // columns, column=index % columns)

        for row in range((len(cards) + columns - 1) // columns):
            self.scrollable_frame.grid_rowconfigure(row, weight=0)

        self._game_grid_columns = columns

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        # Solo permitir scroll si el contenido es más grande que el canvas
        scrollregion = self.canvas.cget('scrollregion')
        if scrollregion:
            try:
                _, _, _, content_height = map(float, scrollregion.split())
                canvas_height = self.canvas.winfo_height()
                
                # Solo permitir scroll si el contenido es más alto que el canvas
                if content_height > canvas_height:
                    self.canvas.yview_scroll(mousewheel_units(event), "units")
            except (ValueError, AttributeError):
                pass
    
    def setup_hover_effects(self, card_frame, name_label):
        """Configurar efectos hover para las cartas de juego"""
        # Obtener color hover dinámico
        if self.current_theme == 'light':
            hover_color = '#e8e8e8'
        else:
            hover_color = '#4f545c'
            
        # Configurar eventos hover para el frame y todos sus hijos
        def on_enter(event):
            # Cambiar color de fondo del frame al hacer hover
            card_frame.configure(style='GameHover.TFrame')
            # Cambiar también el fondo del nombre para que coincida
            name_label.configure(bg=hover_color)
            
        def on_leave(event):
            # Restaurar color original
            card_frame.configure(style='Game.TFrame')
            # Restaurar fondo original del nombre
            name_label.configure(bg=self.colors['bg_light'])
            
        # Bind eventos al frame principal
        card_frame.bind('<Enter>', on_enter)
        card_frame.bind('<Leave>', on_leave)
        
        # Bind eventos a todos los widgets hijos para mantener el efecto
        def bind_to_children(widget):
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            for child in widget.winfo_children():
                bind_to_children(child)
        
        bind_to_children(card_frame)
    
    def setup_hover_effects_enhanced(
        self, card_frame, name_label, image_container=None, accent_bar=None
    ):
        """Aplicar a toda la tarjeta un hover uniforme con transición suave."""
        surface_color = self.colors['bg_light']
        accent_color = self.colors['accent']
        name_hover_color = accent_color if self.current_theme == 'light' else '#7dd3fc'

        def blend_color(start, end, amount):
            start_rgb = tuple(int(start[index:index + 2], 16) for index in (1, 3, 5))
            end_rgb = tuple(int(end[index:index + 2], 16) for index in (1, 3, 5))
            channels = tuple(
                round(first + (last - first) * amount)
                for first, last in zip(start_rgb, end_rgb)
            )
            return '#{:02x}{:02x}{:02x}'.format(*channels)

        hover_surface = blend_color(surface_color, accent_color, 0.08)
        resting_border = blend_color(self.colors['bg_dark'], surface_color, 0.55)
        surface_widgets = []

        def collect_surface_widgets(widget):
            if isinstance(widget, (tk.Frame, tk.Label)):
                surface_widgets.append(widget)
            for child in widget.winfo_children():
                collect_surface_widgets(child)

        collect_surface_widgets(card_frame)
        current = {
            'surface': surface_color,
            'border': resting_border,
            'title': self.colors['text_primary'],
            'hovered': False,
            'after_id': None,
            'generation': 0,
            'destroyed': False,
        }

        def apply_colors(surface, border, title):
            for widget in surface_widgets:
                try:
                    widget.configure(bg=surface)
                except tk.TclError:
                    continue
            try:
                card_frame.configure(
                    highlightbackground=border,
                    highlightcolor=border
                )
                if accent_bar:
                    accent_bar.configure(bg=border)
                name_label.configure(fg=title)
            except tk.TclError:
                return
            current.update(surface=surface, border=border, title=title)

        def animate_hover(is_hovered):
            if current['destroyed']:
                return
            current['hovered'] = is_hovered
            current['generation'] += 1
            generation = current['generation']
            if current['after_id'] is not None:
                try:
                    card_frame.after_cancel(current['after_id'])
                except tk.TclError:
                    pass
                current['after_id'] = None

            start = (current['surface'], current['border'], current['title'])
            end = (
                hover_surface if is_hovered else surface_color,
                accent_color if is_hovered else resting_border,
                name_hover_color if is_hovered else self.colors['text_primary'],
            )
            steps = 7

            def animate_step(step):
                if current['destroyed'] or generation != current['generation']:
                    return
                amount = step / steps
                colors = tuple(
                    blend_color(first, last, amount)
                    for first, last in zip(start, end)
                )
                apply_colors(*colors)
                if step < steps:
                    try:
                        current['after_id'] = card_frame.after(
                            18, lambda: animate_step(step + 1)
                        )
                    except tk.TclError:
                        current['after_id'] = None
                else:
                    current['after_id'] = None

            animate_step(1)

        def is_pointer_over_card():
            try:
                pointer_x, pointer_y = card_frame.winfo_pointerxy()
                widget = card_frame.winfo_containing(pointer_x, pointer_y)
                while widget is not None:
                    if widget == card_frame:
                        return True
                    widget = widget.master
            except tk.TclError:
                return False
            return False

        def on_enter(_event):
            if not current['hovered']:
                animate_hover(True)

        def on_leave(_event):
            try:
                card_frame.after_idle(
                    lambda: animate_hover(False)
                    if (
                        current['hovered']
                        and not current['destroyed']
                        and not is_pointer_over_card()
                    )
                    else None
                )
            except tk.TclError:
                pass

        def on_destroy(event):
            if event.widget != card_frame:
                return
            current['destroyed'] = True
            if current['after_id'] is not None:
                try:
                    card_frame.after_cancel(current['after_id'])
                except tk.TclError:
                    pass

        card_frame.configure(
            highlightthickness=1,
            highlightbackground=resting_border,
            highlightcolor=resting_border,
        )

        def bind_hover_to_tree(widget):
            widget.bind('<Enter>', on_enter, add='+')
            widget.bind('<Leave>', on_leave, add='+')
            for child in widget.winfo_children():
                bind_hover_to_tree(child)

        bind_hover_to_tree(card_frame)
        if image_container:
            bind_hover_to_tree(image_container)
        card_frame.bind('<Destroy>', on_destroy, add='+')
    
    def show_add_game_dialog(self):
        """Mostrar diálogo para añadir juego"""
        dialog = tk.Toplevel(self.root)
        dialog.title(self.get_text('add_game_title'))
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(True, True)
        self.apply_window_icon(dialog)
        center_window_on_primary_monitor(dialog, 720, 760)
        
        # Variables
        self.game_name_var = tk.StringVar()
        self.game_image_path = tk.StringVar()
        self.map_type_var = tk.StringVar(value="image")
        self.map_content_var = tk.StringVar()
        self.game_description_var = tk.StringVar()
        
        # Crear formulario
        self.create_add_game_form(dialog)
    
    def create_add_game_form(self, parent):
        """Crear formulario para añadir juego"""
        # Frame principal del formulario
        form_frame = ttk.Frame(parent, style='Dark.TFrame')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(form_frame, text=self.get_text('add_game_title'),
                               style='Dark.TLabel',
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Nombre del juego
        name_label = ttk.Label(form_frame, text=self.get_text('game_name'),
                              style='Dark.TLabel')
        name_label.pack(anchor=tk.W, pady=(0, 5))
        
        name_entry = tk.Entry(form_frame, textvariable=self.game_name_var,
                             bg=self.colors['bg_light'], fg=self.colors['text'],
                             font=('Segoe UI', 10), relief='flat',
                             insertbackground=self.colors['text'])
        name_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
        
        # Descripción del juego
        description_label = ttk.Label(form_frame, text=self.get_text('game_description'),
                                     style='Dark.TLabel')
        description_label.pack(anchor=tk.W, pady=(0, 5))
        
        description_entry = tk.Entry(form_frame, textvariable=self.game_description_var,
                                    bg=self.colors['bg_light'], fg=self.colors['text'],
                                    font=('Segoe UI', 10), relief='flat',
                                    insertbackground=self.colors['text'])
        description_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
        
        # Imagen del juego
        image_label = ttk.Label(form_frame, text=self.get_text('game_image'),
                               style='Dark.TLabel')
        image_label.pack(anchor=tk.W, pady=(0, 5))
        
        image_frame = ttk.Frame(form_frame, style='Dark.TFrame')
        image_frame.pack(fill=tk.X, pady=(0, 15))
        
        image_entry = tk.Entry(image_frame, textvariable=self.game_image_path,
                              bg=self.colors['bg_light'], fg=self.colors['text'],
                              font=('Segoe UI', 10), relief='flat',
                              insertbackground=self.colors['text'],
                              state='readonly',
                              readonlybackground=self.colors['bg_light'])
        image_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        browse_button = ttk.Button(image_frame, text=self.get_text('browse_map'),
                                  command=self.browse_image)
        browse_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Tipo de mapa
        map_type_label = ttk.Label(form_frame, text=self.get_text('map_type_label'),
                                  style='Dark.TLabel')
        map_type_label.pack(anchor=tk.W, pady=(0, 5))
        
        map_type_frame = ttk.Frame(form_frame, style='Dark.TFrame')
        map_type_frame.pack(fill=tk.X, pady=(0, 15))
        
        def toggle_browse_button():
            """Mostrar/ocultar botón examinar y controlar estado de entrada según tipo de mapa"""
            if self.map_type_var.get() == "image":
                self.add_game_browse_button.pack(side=tk.RIGHT, padx=(10, 0))
                map_content_entry.config(
                    state='readonly',
                    readonlybackground=self.colors['bg_light'],
                )
            else:
                self.add_game_browse_button.pack_forget()
                map_content_entry.config(state='normal', bg=self.colors['bg_light'], fg=self.colors['text'])
        
        image_radio = tk.Radiobutton(map_type_frame, text=self.get_text('map_type_image'),
                                    variable=self.map_type_var, value="image",
                                    command=toggle_browse_button,
                                    bg=self.colors['bg_dark'], fg=self.colors['text'],
                                    selectcolor=self.colors['bg_light'],
                                    activebackground=self.colors['bg_dark'])
        image_radio.pack(side=tk.LEFT)
        
        iframe_radio = tk.Radiobutton(map_type_frame, text=self.get_text('map_type_web'),
                                     variable=self.map_type_var, value="iframe",
                                     command=toggle_browse_button,
                                     bg=self.colors['bg_dark'], fg=self.colors['text'],
                                     selectcolor=self.colors['bg_light'],
                                     activebackground=self.colors['bg_dark'])
        iframe_radio.pack(side=tk.LEFT, padx=(20, 0))
        
        # Contenido del mapa
        map_content_label = ttk.Label(form_frame, text=self.get_text('map_content'),
                                     style='Dark.TLabel')
        map_content_label.pack(anchor=tk.W, pady=(0, 5))
        
        map_content_frame = ttk.Frame(form_frame, style='Dark.TFrame')
        map_content_frame.pack(fill=tk.X, pady=(0, 20))
        
        map_content_entry = tk.Entry(map_content_frame, textvariable=self.map_content_var,
                                    bg=self.colors['bg_light'], fg=self.colors['text'],
                                    font=('Segoe UI', 10), relief='flat',
                                    insertbackground=self.colors['text'],
                                    readonlybackground=self.colors['bg_light'])
        map_content_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        self.add_game_browse_button = ttk.Button(map_content_frame, text=self.get_text('browse_map'),
                                      command=self.browse_map_content)
        self.add_game_browse_button.pack(side=tk.RIGHT, padx=(10, 0))
        toggle_browse_button()
        
        # Botones
        button_frame = ttk.Frame(form_frame, style='Dark.TFrame')
        button_frame.pack(fill=tk.X)
        
        cancel_button = ttk.Button(button_frame, text=self.get_text('cancel'),
                                  command=parent.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        save_button = ttk.Button(button_frame, text=self.get_text('save'),
                                style='Accent.TButton',
                                command=lambda: self.save_game(parent))
        save_button.pack(side=tk.RIGHT)
        
        # Bind Enter para guardar
        parent.bind('<Return>', lambda event: self.save_game(parent))
        
        # Enfocar automáticamente el campo de nombre al abrir
        name_entry.after(100, name_entry.focus_set)
    
    def browse_image(self):
        """Explorar imagen para el juego"""
        filename = filedialog.askopenfilename(
            title="Seleccionar imagen del juego",
            filetypes=[("Archivos de imagen", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if filename:
            self.game_image_path.set(filename)
    
    def browse_map_content(self):
        """Explorar contenido del mapa"""
        if self.map_type_var.get() == "image":
            filename = filedialog.askopenfilename(
                title="Seleccionar imagen del mapa",
                filetypes=[("Archivos de imagen", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if filename:
                self.map_content_var.set(filename)
        else:
            # Para iframe, permitir entrada manual de URL
            url = simpledialog.askstring("URL del mapa", "Introduce la URL (debe comenzar con http:// o https://):")
            if url:
                self.map_content_var.set(url)
    
    def validate_image_file(self, file_path):
        """Validar que el archivo sea una imagen válida"""
        if not file_path:
            return False, "No se ha seleccionado ningún archivo"
        
        if not os.path.exists(file_path):
            return False, "El archivo no existe"
        
        # Verificar extensión
        valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in valid_extensions:
            return False, f"Formato de imagen no válido. Use: {', '.join(valid_extensions)}"
        
        # Intentar abrir la imagen para verificar que es válida
        try:
            with Image.open(file_path) as img:
                img.verify()  # Verificar que la imagen no esté corrupta
            return True, "Imagen válida"
        except Exception as e:
            return False, f"La imagen está corrupta o no es válida: {str(e)}"
    
    def copy_image_to_local(self, source_path, game_name, image_type="game"):
        """Copiar imagen al directorio local del programa"""
        if not source_path or not os.path.exists(source_path):
            return None
        
        try:
            # Obtener extensión original
            file_ext = os.path.splitext(source_path)[1].lower()
            
            # Crear nombre único para evitar conflictos
            timestamp = str(time.time_ns())
            safe_game_name = "".join(c for c in game_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_game_name = safe_game_name.replace(' ', '_')[:30]  # Limitar longitud
            
            new_filename = f"{safe_game_name}_{image_type}_{timestamp}{file_ext}"
            destination_path = os.path.join(self.images_dir, new_filename)
            
            # Copiar archivo
            import shutil
            shutil.copy2(source_path, destination_path)
            
            return destination_path
        except Exception as e:
            print(f"Error copiando imagen: {str(e)}")
            return None
    
    def create_default_image(self, width=250, height=280, text="Sin imagen"):
        """Crear imagen por defecto profesional con gradientes y diseño moderno"""
        try:
            # Crear imagen con gradiente elegante según el tema
            img = Image.new('RGB', (width, height), color='#2f3136')
            try:
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(img)
                
                # Crear gradiente vertical sutil
                if self.current_theme == 'light':
                    top_color = (240, 240, 245)
                    bottom_color = (220, 220, 230)
                    icon_color = (100, 100, 120)
                    text_color = (80, 80, 100)
                else:
                    top_color = (55, 60, 70)
                    bottom_color = (35, 40, 50)
                    icon_color = (150, 150, 170)
                    text_color = (200, 200, 220)
                
                # Dibujar gradiente
                for y in range(height):
                    blend_factor = y / height
                    r = int(top_color[0] * (1 - blend_factor) + bottom_color[0] * blend_factor)
                    g = int(top_color[1] * (1 - blend_factor) + bottom_color[1] * blend_factor)
                    b = int(top_color[2] * (1 - blend_factor) + bottom_color[2] * blend_factor)
                    draw.line([(0, y), (width, y)], fill=(r, g, b))
                
                # Dibujar ícono de juego grande centrado
                icon_size = min(width, height) // 4
                icon_x = width // 2
                icon_y = height // 2 - 20
                
                # Dibujar controlador de juego estilizado
                controller_width = icon_size
                controller_height = icon_size // 2
                controller_x = icon_x - controller_width // 2
                controller_y = icon_y - controller_height // 2
                
                # Cuerpo del controlador
                draw.rounded_rectangle(
                    [controller_x, controller_y, 
                     controller_x + controller_width, controller_y + controller_height],
                    radius=controller_height // 4,
                    fill=icon_color,
                    outline=(icon_color[0] + 30, icon_color[1] + 30, icon_color[2] + 30),
                    width=2
                )
                
                # Botones del controlador
                button_size = controller_height // 6
                for i in range(4):
                    btn_x = controller_x + controller_width // 3 + (i % 2) * button_size * 2
                    btn_y = controller_y + controller_height // 4 + (i // 2) * button_size * 2
                    draw.ellipse([btn_x, btn_y, btn_x + button_size, btn_y + button_size], 
                               fill=(icon_color[0] + 40, icon_color[1] + 40, icon_color[2] + 40))
                
                # D-pad
                dpad_size = controller_height // 5
                dpad_x = controller_x + controller_width // 6
                dpad_y = controller_y + controller_height // 3
                
                # Cruz del D-pad
                draw.rectangle([dpad_x + dpad_size//3, dpad_y, 
                              dpad_x + 2*dpad_size//3, dpad_y + dpad_size], 
                             fill=(icon_color[0] + 40, icon_color[1] + 40, icon_color[2] + 40))
                draw.rectangle([dpad_x, dpad_y + dpad_size//3, 
                              dpad_x + dpad_size, dpad_y + 2*dpad_size//3], 
                             fill=(icon_color[0] + 40, icon_color[1] + 40, icon_color[2] + 40))
                
                # Texto del nombre del juego
                try:
                    # Intentar fuentes más modernas
                    font_title = ImageFont.truetype("segoeui.ttf", 14)
                    font_subtitle = ImageFont.truetype("segoeui.ttf", 10)
                except:
                    try:
                        font_title = ImageFont.truetype("arial.ttf", 14)
                        font_subtitle = ImageFont.truetype("arial.ttf", 10)
                    except:
                        font_title = ImageFont.load_default()
                        font_subtitle = ImageFont.load_default()
                
                # Título principal
                title_bbox = draw.textbbox((0, 0), text, font=font_title)
                title_width = title_bbox[2] - title_bbox[0]
                title_x = (width - title_width) // 2
                title_y = icon_y + icon_size + 20
                
                draw.text((title_x, title_y), text, fill=text_color, font=font_title)
                
                # Subtítulo
                subtitle = "🎮 Imagen no disponible"
                subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
                subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
                subtitle_x = (width - subtitle_width) // 2
                subtitle_y = title_y + 25
                
                draw.text((subtitle_x, subtitle_y), subtitle, 
                         fill=(text_color[0] - 40, text_color[1] - 40, text_color[2] - 40), 
                         font=font_subtitle)
                
                # Marco decorativo sutil
                border_color = (icon_color[0] + 20, icon_color[1] + 20, icon_color[2] + 20)
                draw.rectangle([2, 2, width-3, height-3], outline=border_color, width=1)
                
            except ImportError:
                # Fallback si PIL no está completo
            
                pass
            
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error creando imagen por defecto: {str(e)}")
            return None
    
    def cleanup_unused_images(self):
        """Limpiar imágenes no utilizadas del directorio local"""
        if not os.path.exists(self.images_dir):
            return
        
        try:
            # Obtener todas las rutas de imágenes utilizadas actualmente
            used_images = set()
            for game in self.games:
                image_path = game.get('image_path', '')
                map_content = game.get('map_content', '')
                
                # Agregar imagen del juego si está en el directorio local
                if image_path and is_path_within(image_path, self.images_dir):
                    used_images.add(os.path.basename(image_path))
                
                # Agregar imagen del mapa si es de tipo imagen y está en el directorio local
                if (game.get('map_type') == 'image' and map_content and
                    is_path_within(map_content, self.images_dir)):
                    used_images.add(os.path.basename(map_content))
            
            # Obtener todas las imágenes en el directorio local
            local_images = set()
            for filename in os.listdir(self.images_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    local_images.add(filename)
            
            # Eliminar imágenes no utilizadas
            unused_images = local_images - used_images
            for unused_image in unused_images:
                unused_path = os.path.join(self.images_dir, unused_image)
                try:
                    os.remove(unused_path)
                    print(f"Imagen no utilizada eliminada: {unused_image}")
                except Exception as e:
                    print(f"Error eliminando imagen {unused_image}: {str(e)}")
                    
        except Exception as e:
            print(f"Error durante la limpieza de imágenes: {str(e)}")
    
    def migrate_existing_games(self):
        """Migrar juegos existentes para usar el directorio local de imágenes"""
        changes_made = False
        
        for i, game in enumerate(self.games):
            try:
                # Migrar imagen del juego si no está en el directorio local
                image_path = game.get('image_path', '')
                if image_path and not image_path.startswith(self.images_dir) and os.path.exists(image_path):
                    new_image_path = self.copy_image_to_local(image_path, game['name'], "game")
                    if new_image_path and new_image_path != image_path:
                        self.games[i]['image_path'] = new_image_path
                        changes_made = True
                        print(f"Migrada imagen del juego '{game['name']}'")
                
                # Migrar imagen del mapa si es de tipo imagen y no está en el directorio local
                map_content = game.get('map_content', '')
                if (game.get('map_type') == 'image' and map_content and 
                    not map_content.startswith(self.images_dir) and os.path.exists(map_content)):
                    new_map_path = self.copy_image_to_local(map_content, game['name'], "map")
                    if new_map_path and new_map_path != map_content:
                        self.games[i]['map_content'] = new_map_path
                        changes_made = True
                        print(f"Migrada imagen del mapa del juego '{game['name']}'")
                
                # Añadir campo favorite si no existe
                if 'favorite' not in game:
                    self.games[i]['favorite'] = False
                    changes_made = True
                        
            except Exception as e:
                print(f"Error migrando juego '{game.get('name', 'Sin nombre')}': {str(e)}")
        
        # Guardar cambios si se hicieron migraciones
        if changes_made:
            if self.save_games():
                print("Migración completada")
    
    def validate_url(self, url):
        """Validar que la URL sea válida"""
        if not url:
            return False, "No se ha introducido ninguna URL"
        
        # Verificar que empiece con http:// o https://
        if not url.startswith(('http://', 'https://')):
            return False, "La URL debe comenzar con http:// o https://"
        
        # Validar formato básico de URL
        try:
            result = urllib.parse.urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False, "Formato de URL no válido"
            return True, "URL válida"
        except Exception as e:
            return False, f"URL no válida: {str(e)}"
    
    def save_game(self, dialog):
        """Guardar juego nuevo con validaciones mejoradas"""
        name = self.game_name_var.get().strip()
        image_path = self.game_image_path.get().strip()
        map_type = self.map_type_var.get()
        map_content = self.map_content_var.get().strip()
        
        # Validación del nombre
        if not name:
            messagebox.showerror("Campo obligatorio", "El nombre del juego es obligatorio")
            return
        
        if len(name) < 2:
            messagebox.showerror("Nombre inválido", "El nombre del juego debe tener al menos 2 caracteres")
            return
        
        # Validación de la imagen del juego
        if not image_path:
            messagebox.showerror("Campo obligatorio", "Debe seleccionar una imagen para el juego")
            return
        
        is_valid_image, image_message = self.validate_image_file(image_path)
        if not is_valid_image:
            messagebox.showerror("Imagen inválida", f"Error en la imagen del juego:\n{image_message}")
            return
        
        # Validación del contenido del mapa
        if not map_content:
            messagebox.showerror("Campo obligatorio", "Debe especificar el contenido del mapa")
            return
        
        if map_type == "image":
            # Validar imagen del mapa
            is_valid_map_image, map_image_message = self.validate_image_file(map_content)
            if not is_valid_map_image:
                messagebox.showerror("Imagen del mapa inválida", f"Error en la imagen del mapa:\n{map_image_message}")
                return
        else:
            # Validar URL del iframe
            is_valid_url, url_message = self.validate_url(map_content)
            if not is_valid_url:
                messagebox.showerror("URL inválida", f"Error en la URL del mapa:\n{url_message}")
                return
        
        # Verificar que no existe ya un juego con el mismo nombre
        for existing_game in self.games:
            if existing_game['name'].lower() == name.lower():
                messagebox.showerror("Juego duplicado", f"Ya existe un juego llamado '{name}'")
                return
        
        # Copiar imagen del juego al directorio local
        local_image_path = self.copy_image_to_local(image_path, name, "game")
        if not local_image_path:
            messagebox.showerror("Error", "No se pudo copiar la imagen del juego")
            return
        
        # Copiar imagen del mapa si es de tipo imagen
        local_map_content = map_content
        if map_type == "image":
            local_map_content = self.copy_image_to_local(map_content, name, "map")
            if not local_map_content:
                messagebox.showerror("Error", "No se pudo copiar la imagen del mapa")
                return
        
        # Crear objeto juego
        game = {
            'name': name,
            'image_path': local_image_path,
            'map_type': map_type,
            'map_content': local_map_content,
            'favorite': False,
            'tasks': [],
            'description': self.game_description_var.get().strip() if hasattr(self, 'game_description_var') else '',
            'date_added': datetime.now().isoformat(),
            'total_play_time': 0
        }
        
        # Añadir a la lista
        self.games.append(game)
        
        # Guardar en archivo
        if not self.save_games():
            self.games.remove(game)
            return
        
        # Actualizar interfaz
        self.refresh_games_display()
        
        # Cerrar diálogo
        dialog.destroy()
        
        messagebox.showinfo(self.get_text('success'), self.get_text('game_saved'))
    
    def refresh_games_display(self):
        """Actualizar la visualización de juegos"""
        # Limpiar referencias a widgets destruidos
        self.game_card_widgets = {}
        
        # Actualizar contadores en botones de filtro
        self.update_filter_button_counters()
        # Limpiar frame scrollable
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Obtener juegos filtrados
        filtered_games = self.get_filtered_games()
        
        if not filtered_games:
            # Mostrar mensaje si no hay juegos (ya sea porque no hay juegos o por el filtro)
            if (
                self.favorites_filter == 'favorites'
                and not any(game.get('favorite', False) for game in self.games)
            ):
                message = self.get_text('no_favorites')
            elif not self.games:
                message = self.get_text('no_games') if hasattr(self, 'get_text') else "No hay juegos agregados"
            elif (
                self.favorites_filter == 'recent'
                and not any(game.get('last_opened_at') for game in self.games)
            ):
                message = self.get_text('no_recent_games')
            else:
                message = self.get_text('no_games_search')
            
            no_games_label = ttk.Label(self.scrollable_frame,
                                      text=message,
                                      style='Dark.TLabel',
                                      foreground=self.colors['text_secondary'],
                                      font=(self.ui_font_family, 13),
                                      justify='center')
            no_games_label.pack(pady=72, expand=True, anchor='center')
            return
        
        # Choose a column count from the actual game viewport, not the window width.
        row = 0
        col = 0

        viewport_width = self.canvas.winfo_width()
        if viewport_width <= 1:
            viewport_width = 294
        max_cols = max(1, viewport_width // 294)
        self.game_card_image_width = 238
        self.game_card_image_height = 268

        for c in range(getattr(self, '_game_grid_columns', 0)):
            self.scrollable_frame.grid_columnconfigure(c, weight=0, uniform='')
        for c in range(max_cols):
            self.scrollable_frame.grid_columnconfigure(c, weight=1, uniform='game-cards')
        self._game_grid_columns = max_cols
        
        for i, game in enumerate(filtered_games):
            self.create_game_card(self.scrollable_frame, game, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Keep card rows at their natural height; the outer canvas handles vertical scrolling.
        for r in range(row + 1):
            self.scrollable_frame.grid_rowconfigure(r, weight=0)
    
    def get_filtered_games(self):
        """Obtener juegos filtrados con prioridad para favoritos"""
        if self.favorites_filter == 'recent':
            recent_games = [
                game for game in self.games
                if game.get('last_opened_at')
            ]

            def last_opened_timestamp(game):
                try:
                    return datetime.fromisoformat(game['last_opened_at']).timestamp()
                except (TypeError, ValueError, OSError, OverflowError):
                    return 0

            recent_games.sort(key=last_opened_timestamp, reverse=True)
            if (
                hasattr(self, 'search_var')
                and self.search_var
                and not getattr(self, 'is_placeholder_active', True)
            ):
                search_text = self.search_var.get().strip().casefold()
                if search_text:
                    recent_games = [
                        game for game in recent_games
                        if search_text in game.get('name', '').casefold()
                    ]
            return recent_games

        # Si estamos en modo "solo favoritos", mostrar solo esos
        if hasattr(self, 'favorites_filter') and self.favorites_filter == "favorites":
            filtered_games = [game for game in self.games if game.get('favorite', False)]
            
            # Aplicar búsqueda dentro de favoritos si hay texto
            if (hasattr(self, 'search_var') and self.search_var and 
                hasattr(self, 'is_placeholder_active') and not self.is_placeholder_active):
                
                search_text = self.search_var.get().strip().lower()
                if search_text:
                    filtered_games = [game for game in filtered_games 
                                    if search_text in game.get('name', '').lower()]
            
            return filtered_games
        
        # Modo "todos" con prioridad para favoritos
        all_games = self.games.copy()
        
        # Separar favoritos y no favoritos
        favorites = [game for game in all_games if game.get('favorite', False)]
        non_favorites = [game for game in all_games if not game.get('favorite', False)]
        
        # Si hay búsqueda activa
        if (hasattr(self, 'search_var') and self.search_var and 
            hasattr(self, 'is_placeholder_active') and not self.is_placeholder_active):
            
            search_text = self.search_var.get().strip().lower()
            if search_text:
                # Separar favoritos que coinciden y que no coinciden
                matching_favorites = [game for game in favorites 
                                    if search_text in game.get('name', '').lower()]
                non_matching_favorites = [game for game in favorites 
                                        if search_text not in game.get('name', '').lower()]
                
                # Solo no-favoritos que coinciden
                matching_non_favorites = [game for game in non_favorites 
                                        if search_text in game.get('name', '').lower()]
                
                # Orden: Favoritos que coinciden → Favoritos que no coinciden → No-favoritos que coinciden
                return matching_favorites + non_matching_favorites + matching_non_favorites
        
        # Sin búsqueda: Favoritos primero, luego el resto
        return favorites + non_favorites
    
    def create_rounded_image(self, image, size, radius=15):
        """Crear imagen con bordes redondeados"""
        image = image.resize(size, Image.Resampling.LANCZOS)
        
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), size], radius=radius, fill=255)
        
        image.putalpha(mask)
        return image

    def create_game_card(self, parent, game, row, col):
        """Crear tarjeta de juego con diseño profesional y moderno"""
        main_container = tk.Frame(parent, bg=self.colors['bg_dark'])
        main_container.grid(row=row, column=col, padx=12, pady=12)

        card_frame = tk.Frame(
            main_container,
            bg=self.colors['bg_light'],
            highlightthickness=1,
            highlightbackground=self.colors['bg_medium'],
            highlightcolor=self.colors['accent'],
        )
        card_frame.pack(fill='both', expand=True)
        
        header_frame = tk.Frame(card_frame, bg=self.colors['bg_light'], height=56)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)

        accent_bar = tk.Frame(header_frame, bg=self.colors['accent'], height=3)
        accent_bar.place(x=0, y=0, relwidth=1, height=3)
        
        name_label = tk.Label(header_frame, 
                             text=game['name'],
                             bg=self.colors['bg_light'],
                             fg=self.colors['text_primary'],
                             font=(self.ui_font_family, 11, 'bold'),
                             cursor='hand2',
                             anchor='center',
                             justify='center',
                             wraplength=max(120, getattr(self, 'game_card_image_width', 238) - 90))
        name_label.place(relx=0.5, rely=0.5, anchor='center', relwidth=1, relheight=1)
        name_label.bind("<Button-1>", lambda e, g=game: self.show_game_presentation(g))
        
        is_favorite = game.get('favorite', False)
        star_color = '#FFD700' if is_favorite else '#A0A0A0'
        star_text = '★' if is_favorite else '☆'
        
        favorite_star = tk.Label(header_frame,
                               text=star_text,
                               font=(self.ui_font_family, 16, 'bold'),
                               fg=star_color,
                               bg=self.colors['bg_light'],
                               cursor='hand2',
                               width=3)
        favorite_star.place(relx=1, rely=0.5, anchor='e', x=-8)
        
        if game['name'] not in self.game_card_widgets:
            self.game_card_widgets[game['name']] = {}
        self.game_card_widgets[game['name']]['favorite_star'] = favorite_star
        
        def on_star_enter(event):
            if game.get('favorite', False):
                favorite_star.config(fg='#FF8C00')
            else:
                favorite_star.config(fg='#FFD700')
        
        def on_star_leave(event):
            current_favorite = game.get('favorite', False)
            star_color = '#FFD700' if current_favorite else '#A0A0A0'
            favorite_star.config(fg=star_color)
        
        favorite_star.bind("<Enter>", on_star_enter)
        favorite_star.bind("<Leave>", on_star_leave)
        favorite_star.bind("<Button-1>", lambda e, g=game, star=favorite_star: self.toggle_favorite(g, star))
        
        image_container = tk.Frame(card_frame, bg=self.colors['bg_light'])
        image_container.pack(pady=(8, 2), padx=12)
        
        try:
            image = Image.open(game['image_path'])
            image_width = getattr(self, 'game_card_image_width', 238)
            image_height = getattr(self, 'game_card_image_height', 268)
            rounded_image = self.create_rounded_image(
                image, (image_width, image_height), radius=12
            )
            photo = ImageTk.PhotoImage(rounded_image)
            
            image_label = tk.Label(image_container, 
                                  image=photo, 
                                  bg=self.colors['bg_light'],
                                  cursor='hand2',
                                  bd=0,
                                  highlightthickness=0)
            image_label.image = photo
            image_label.pack(padx=1, pady=1)
            image_label.bind("<Button-1>", lambda e, g=game: self.show_game_presentation(g))
            
        except Exception as e:
            default_photo = self.create_default_image(238, 268, 
                                                    game['name'][:15] + "..." if len(game['name']) > 15 else game['name'])
            
            if default_photo:
                placeholder_label = tk.Label(image_container, 
                                            image=default_photo,
                                            bg=self.colors['bg_light'],
                                            cursor='hand2',
                                            bd=0,
                                            highlightthickness=0)
                placeholder_label.image = default_photo
            else:
                placeholder_label = tk.Label(image_container, 
                                            text="🎮\n" + self.get_text('no_image'),
                                            bg=self.colors['bg_medium'],
                                            fg=self.colors['text_muted'],
                                            font=(self.ui_font_family, 18),
                                            width=max(16, image_width // 8),
                                            height=max(10, image_height // 16),
                                            bd=0,
                                            highlightthickness=0)
            
            placeholder_label.pack(padx=1, pady=1)
            placeholder_label.bind("<Button-1>", lambda e, g=game: self.show_game_presentation(g))
        
        buttons_frame = tk.Frame(card_frame, bg=self.colors['bg_light'])
        buttons_frame.pack(fill='x', padx=12, pady=(8, 12))
        
        edit_button = tk.Button(buttons_frame, 
                               text=self.get_text('edit_game'),
                               bg=self.colors['bg_medium'],
                               fg=self.colors['text_primary'],
                               font=(self.ui_font_family, 9, 'bold'),
                               relief='flat',
                               bd=0,
                               borderwidth=0,
                               highlightthickness=0,
                               overrelief='flat',
                               cursor='hand2',
                               pady=10,
                               activebackground=self.colors['accent'],
                               activeforeground='#0b1020',
                               command=lambda g=game: self.edit_game(g))
        edit_button.pack(side='left', fill='x', expand=True, padx=(0, 6))
        
        delete_button = tk.Button(buttons_frame, 
                                 text=self.get_text('delete_game'),
                                 bg=self.colors['bg_medium'],
                                 fg=self.colors['text_primary'],
                                 font=(self.ui_font_family, 9, 'bold'),
                                 relief='flat',
                                 bd=0,
                                 borderwidth=0,
                                 highlightthickness=0,
                                 overrelief='flat',
                                 cursor='hand2',
                                 pady=10,
                                 activebackground=self.colors['danger'],
                                 activeforeground='white',
                                 command=lambda g=game: self.delete_game(g))
        delete_button.pack(side='right', fill='x', expand=True, padx=(6, 0))
        
        def on_edit_enter(event):
            edit_button.config(bg=self.colors['accent'], fg='#0b1020')
        
        def on_edit_leave(event):
            edit_button.config(bg=self.colors['bg_medium'], fg=self.colors['text_primary'])
            
        def on_delete_enter(event):
            delete_button.config(bg=self.colors['danger'])
        
        def on_delete_leave(event):
            delete_button.config(bg=self.colors['bg_medium'])
        
        edit_button.bind("<Enter>", on_edit_enter)
        edit_button.bind("<Leave>", on_edit_leave)
        delete_button.bind("<Enter>", on_delete_enter)
        delete_button.bind("<Leave>", on_delete_leave)
        
        self.setup_hover_effects_enhanced(
            card_frame,
            name_label,
            image_container,
            accent_bar,
        )
    
    def toggle_favorite(self, game, favorite_star=None):
        """Alternar estado de favorito de un juego con efectos visuales"""
        # Cambiar estado de favorito
        current_favorite = game.get('favorite', False)
        game['favorite'] = not current_favorite
        
        # Guardar cambios
        if not self.save_games():
            game['favorite'] = current_favorite
            return
        
        # Actualizar la estrella visualmente
        star_color = '#FFD700' if game['favorite'] else '#A0A0A0'
        star_text = '★' if game['favorite'] else '☆'
        
        # Actualizar el widget que se pasó (puede ser de tarjeta o presentación)
        stars_to_animate = []
        if favorite_star:
            favorite_star.config(fg=star_color, text=star_text)
            stars_to_animate.append(favorite_star)
        
        # Sincronizar con la tarjeta del juego si existe en el diccionario
        if game['name'] in self.game_card_widgets:
            card_star = self.game_card_widgets[game['name']].get('favorite_star')
            if card_star:
                card_star.config(fg=star_color, text=star_text)
                if card_star not in stars_to_animate:
                    stars_to_animate.append(card_star)

        for star in stars_to_animate:
            self.animate_favorite_star(star, game['favorite'], star_color)
        
        # Actualizar visualización solo si estamos filtrando por favoritos
        # De lo contrario, el juego seguirá visible en la lista
        if hasattr(self, 'favorites_filter') and self.favorites_filter == "favorites":
            self.refresh_games_display()
        
        # Actualizar contadores en botones de filtro si existen
        self.update_filter_button_counters()

    def animate_favorite_star(self, favorite_star, is_favorite, final_color):
        """Give the favorite toggle a brief pulse without changing its final size."""
        try:
            original_font = favorite_star.cget('font')
            font = tkFont.Font(root=self.root, font=original_font)
            font_info = font.actual()
            family = font_info['family']
            base_size = abs(int(font_info['size']))
            weight = font_info['weight']
        except tk.TclError:
            return

        pulse_color = '#FFD700' if is_favorite else '#FF8C00'
        frames = (
            (base_size + 5, pulse_color),
            (base_size + 2, pulse_color),
            (base_size, final_color),
        )

        def show_frame(index):
            if not favorite_star.winfo_exists():
                return
            if index == len(frames):
                favorite_star.config(font=original_font, fg=final_color)
                return

            size, color = frames[index]
            favorite_star.config(
                font=(family, size, weight),
                fg=color,
            )
            self.root.after(70, lambda: show_frame(index + 1))

        show_frame(0)
    
    def show_temporary_message(self, message, is_favorite):
        """Mostrar mensaje temporal de feedback al usuario"""
        # Crear ventana temporal (invisible inicialmente)
        temp_window = tk.Toplevel(self.root)
        temp_window.withdraw()
        temp_window.title("")
        temp_window.geometry("300x80")
        temp_window.resizable(False, False)
        temp_window.transient(self.root)
        
        # Configurar colores según si es favorito o no
        bg_color = '#4CAF50' if is_favorite else '#FF9800'  # Verde para agregar, naranja para quitar
        
        temp_window.configure(bg=bg_color)
        
        # Mensaje
        label = tk.Label(temp_window, 
                        text=message,
                        bg=bg_color,
                        fg='white',
                        font=('Segoe UI', 10, 'bold'),
                        wraplength=280)
        label.pack(expand=True)
        
        # Quitar decoraciones de ventana
        temp_window.overrideredirect(True)
        
        # Centrar la ventana
        temp_window.update_idletasks()
        x = (temp_window.winfo_screenwidth() // 2) - (300 // 2)
        y = (temp_window.winfo_screenheight() // 2) - (80 // 2)
        temp_window.geometry(f"300x80+{x}+{y}")
        
        # Mostrar la ventana después de estar lista
        temp_window.deiconify()
        
        # Auto-cerrar después de 2 segundos
        temp_window.after(2000, temp_window.destroy)
    
    def update_filter_button_counters(self):
        """Actualizar contadores en los botones de filtro"""
        if not hasattr(self, 'all_button') or not self.all_button.winfo_exists():
            return
            
        # Contar favoritos
        favorites_count = len([game for game in self.games if game.get('favorite', False)])
        total_count = len(self.games)
        recent_count = sum(1 for game in self.games if game.get('last_opened_at'))
        
        # Actualizar texto de botones con contadores
        all_text = f"{self.get_text('all_games')}   {total_count}"
        favorites_text = f"{self.get_text('favorites')}   {favorites_count}"
        recent_text = f"{self.get_text('recent')}   {recent_count}"
        
        # Actualizar botones si existen
        try:
            self.all_button.config(text=all_text)
            self.favorites_button.config(text=favorites_text)
            self.recent_button.config(text=recent_text)
            self._refresh_filter_button_styles()
        except tk.TclError:
            # Los botones fueron destruidos, no hacer nada
            pass

    def record_game_opened(self, game):
        """Persist the timestamp used to order recently opened games."""
        previous_last_opened = game.get('last_opened_at')
        game['last_opened_at'] = datetime.now().astimezone().isoformat(timespec='seconds')
        if not self.save_games():
            if previous_last_opened is None:
                game.pop('last_opened_at', None)
            else:
                game['last_opened_at'] = previous_last_opened
            return False
        self.update_filter_button_counters()
        if self.favorites_filter == 'recent':
            self.refresh_games_display()
        return True
    
    def show_game_presentation(self, game):
        """Mostrar ventana de presentación del juego con opciones de abrir mapa o guía"""
        self.record_game_opened(game)

        presentation_window = tk.Toplevel(self.root)
        presentation_window.withdraw()
        presentation_window.transient(self.root)
        presentation_window.title(game['name'])
        presentation_window.resizable(True, True)
        
        self.apply_window_icon(presentation_window)
        presentation_window.configure(bg=self.colors['bg_dark'])
        
        style = ttk.Style()
        style.configure(
            "Presentation.Horizontal.TProgressbar",
            background=self.colors['accent'],
            troughcolor=self.colors['bg_dark'],
            borderwidth=0,
            lightcolor=self.colors['accent'],
            darkcolor=self.colors['accent'],
            relief='flat'
        )
        
        _, _, monitor_width, monitor_height = get_primary_monitor_bounds(presentation_window)
        requested_width = min(1150, max(800, monitor_width - 80))
        requested_height = min(750, max(600, monitor_height - 100))
        _, _, window_width, window_height = center_window_on_primary_monitor(
            presentation_window, requested_width, requested_height
        )
        presentation_window.minsize(min(900, window_width), min(620, window_height))
        
        main_frame = tk.Frame(presentation_window, bg=self.colors['bg_dark'])
        main_frame.pack(fill='both', expand=True, padx=28, pady=24)
        
        content_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        content_frame.pack(fill='both', expand=True, pady=(0, 18))
        
        left_panel = tk.Frame(
            content_frame,
            bg=self.colors['bg_dark'],
            padx=10,
            pady=8,
        )
        left_panel.pack(side='left', fill='y', expand=False, padx=(0, 20))
        
        image_label = None
        last_height = [0]
        
        def update_image_size(event=None):
            """Actualizar tamaño de imagen según el tamaño de la ventana"""
            if image_label is None or not hasattr(image_label, 'winfo_exists') or not image_label.winfo_exists():
                return
            
            window_height = presentation_window.winfo_height()
            if window_height < 100:
                return
            
            if abs(window_height - last_height[0]) < 30:
                return
            
            last_height[0] = window_height
            max_img_height = int((window_height - 120) * 0.9)
            aspect_ratio = 220 / 290
            img_height = min(290, max(150, max_img_height))
            img_width = int(img_height * aspect_ratio)
            
            try:
                original_image = Image.open(game['image_path'])
                resized_image = original_image.resize((img_width, img_height), Image.Resampling.LANCZOS)
                new_photo = ImageTk.PhotoImage(resized_image)
                image_label.config(image=new_photo)
                image_label.image = new_photo
            except Exception:
                pass
        
        try:
            def create_rounded_image_with_border(image_path, width, height, border_size=3, corner_radius=15):
                """Crear imagen con esquinas redondeadas y marco"""
                image = Image.open(image_path)
                image = image.resize((width, height), Image.Resampling.LANCZOS)
                
                border_color = self.colors.get('accent', '#4a7fd7')
                border_rgb = tuple(int(border_color[i:i+2], 16) for i in (1, 3, 5))
                
                bordered_img = Image.new('RGB', 
                    (width + border_size * 2, height + border_size * 2), 
                    border_rgb)
                bordered_img.paste(image, (border_size, border_size))
                
                mask = Image.new('L', bordered_img.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle(
                    [(0, 0), bordered_img.size],
                    radius=corner_radius,
                    fill=255
                )
                
                rounded_img = Image.new('RGBA', bordered_img.size)
                rounded_img.paste(bordered_img, (0, 0))
                rounded_img.putalpha(mask)
                
                return rounded_img
            
            rounded_image = create_rounded_image_with_border(
                game['image_path'], 220, 290, border_size=0, corner_radius=15
            )
            photo = ImageTk.PhotoImage(rounded_image)
            
            image_frame = tk.Frame(
                left_panel,
                bg=self.colors['accent'],
                padx=2,
                pady=2,
            )
            image_frame.pack(pady=(0, 16))
            
            image_label = tk.Label(
                image_frame,
                image=photo,
                bg=self.colors['accent'],
                highlightthickness=0,
                highlightcolor=self.colors['accent'],
                highlightbackground=self.colors['bg_medium']
            )
            image_label.image = photo
            image_label.pack()
            
            if game.get('description', '').strip():
                description_label = tk.Label(
                    left_panel,
                    text=game.get('description', ''),
                    font=('Segoe UI', 10),
                    fg=self.colors['text_muted'],
                    bg=self.colors['bg_dark'],
                    wraplength=220,
                    justify='left'
                )
                description_label.pack(fill='x', pady=(0, 4))
            
            presentation_window.bind('<Configure>', update_image_size)
            
        except Exception as e:
            placeholder_label = tk.Label(
                left_panel,
                text="🎮",
                font=('Segoe UI', 60),
                bg=self.colors['bg_light'],
                fg=self.colors['text_muted']
            )
            placeholder_label.pack(pady=(0, 20), expand=True)
        
        right_panel = tk.Frame(
            content_frame,
            bg=self.colors['bg_dark'],
            padx=12,
            pady=12,
        )
        right_panel.pack(side='left', fill='both', expand=True)
        
        title_frame = tk.Frame(right_panel, bg=self.colors['bg_dark'])
        title_frame.pack(fill='x', pady=(0, 12))

        game_title_frame = tk.Frame(title_frame, bg=self.colors['bg_dark'])
        game_title_frame.pack(fill='x')

        title_group = tk.Frame(game_title_frame, bg=self.colors['bg_dark'])
        title_group.pack(anchor='center')
        
        title_label = tk.Label(
            title_group,
            text=game['name'],
            font=('Segoe UI', 30, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark'],
            wraplength=max(400, window_width - 500),
            justify='center',
            anchor='center',
        )
        title_label.pack(side='left')
        
        is_favorite = game.get('favorite', False)
        star_color = '#FFD700' if is_favorite else '#B0B0B0'
        star_text = '★' if is_favorite else '☆'
        
        favorite_star = tk.Label(
            title_group,
            text=star_text,
            font=('Segoe UI', 21, 'bold'),
            fg=star_color,
            bg=self.colors['bg_dark'],
            cursor='hand2',
        )
        favorite_star.pack(side='left', padx=(8, 0))
        
        def on_star_enter(event):
            if game.get('favorite', False):
                favorite_star.config(fg='#FF6B35', text='★')
            else:
                favorite_star.config(fg='#FFD700', text='★')
        
        def on_star_leave(event):
            current_favorite = game.get('favorite', False)
            star_color = '#FFD700' if current_favorite else '#B0B0B0'
            star_text = '★' if current_favorite else '☆'
            favorite_star.config(fg=star_color, text=star_text)
        
        favorite_star.bind("<Enter>", on_star_enter)
        favorite_star.bind("<Leave>", on_star_leave)
        favorite_star.bind("<Button-1>", lambda e, g=game, star=favorite_star: self.toggle_favorite(g, star))
        
        if 'date_added' in game:
            try:
                date_obj = datetime.fromisoformat(game['date_added'])
                formatted_date = date_obj.strftime('%d/%m/%Y')
                date_label = tk.Label(
                    right_panel,
                    text=f"{self.get_text('added_date')}: {formatted_date}",
                    font=('Segoe UI', 10),
                    fg=self.colors['text_muted'],
                    bg=self.colors['bg_dark']
                )
                date_label.pack(anchor='center', pady=(0, 18))
            except Exception:
                pass
        
        def add_task():
            add_task_window = tk.Toplevel(presentation_window)
            add_task_window.title(self.get_text('new_objective'))
            add_task_window.configure(bg=self.colors['bg_dark'])
            add_task_window.resizable(False, False)
            add_task_window.transient(presentation_window)
            
            self.apply_window_icon(add_task_window)
            
            _, _, dialog_width, dialog_height = center_window_on_primary_monitor(
                add_task_window, 480, 230
            )
            add_task_window.minsize(dialog_width, dialog_height)
            
            content_frame_task = tk.Frame(add_task_window, bg=self.colors['bg_dark'])
            content_frame_task.pack(fill='both', expand=True, padx=26, pady=24)
            
            label = tk.Label(
                content_frame_task,
                text=self.get_text('write_objective'),
                font=('Segoe UI', 10),
                fg=self.colors['text_primary'],
                bg=self.colors['bg_dark']
            )
            label.pack(anchor='w', pady=(0, 10))
            
            entry = tk.Entry(
                content_frame_task,
                font=('Segoe UI', 10),
                bg=self.colors['bg_medium'],
                fg=self.colors['text_primary'],
                insertbackground=self.colors['accent'],
                relief='flat',
                bd=1
            )
            entry.pack(fill='x', pady=(0, 8), ipady=5)
            entry.focus()
            
            buttons_frame_task = tk.Frame(content_frame_task, bg=self.colors['bg_dark'])
            buttons_frame_task.pack(fill='x', pady=(12, 0))
            
            def save_task():
                task_text = entry.get().strip()
                if task_text:
                    if 'tasks' not in game:
                        game['tasks'] = []
                    game['tasks'].append({'text': task_text, 'done': False})
                    if not self.save_games():
                        game['tasks'].pop()
                        return
                    refresh_tasks_display()
                    add_task_window.destroy()
            
            def on_cancel():
                add_task_window.destroy()
            
            save_btn = tk.Button(
                buttons_frame_task,
                text=self.get_text('save'),
                font=('Segoe UI', 10, 'bold'),
                fg='white',
                bg=self.colors['accent'],
                relief='flat',
                cursor='hand2',
                bd=0,
                borderwidth=0,
                highlightthickness=0,
                overrelief='flat',
                command=save_task
            )
            save_btn.pack(side='right', padx=(8, 0), ipadx=10, ipady=5)
            
            cancel_btn = tk.Button(
                buttons_frame_task,
                text=self.get_text('cancel'),
                font=('Segoe UI', 10, 'bold'),
                fg=self.colors['text_primary'],
                bg=self.colors['bg_medium'],
                relief='flat',
                cursor='hand2',
                bd=0,
                borderwidth=0,
                highlightthickness=0,
                overrelief='flat',
                command=on_cancel
            )
            cancel_btn.pack(side='right', padx=5, ipadx=10, ipady=5)
            
            self._add_hover_effect(save_btn, self.colors['accent'], 
                                 self.colors.get('accent_hover', '#5b7fde'))
            self._add_hover_effect(cancel_btn, self.colors['bg_medium'], 
                                 self.colors.get('bg_light', '#505050'))
            
            entry.bind('<Return>', lambda e: save_task())
            add_task_window.bind('<Escape>', lambda e: on_cancel())
            add_task_window.grab_set()
            entry.focus_set()
        
        tasks_header_frame = tk.Frame(right_panel, bg=self.colors['bg_dark'])
        tasks_header_frame.pack(fill='x', pady=(8, 12))
        
        tasks_label = tk.Label(
            tasks_header_frame,
            text=self.get_text('objectives').upper(),
            font=('Segoe UI', 15, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark'],
            anchor='center',
        )
        tasks_label.place(relx=0.5, rely=0.5, anchor='center')
        
        add_task_button = tk.Button(
            tasks_header_frame,
            text="+",
            font=('Segoe UI', 10, 'bold'),
            fg=(
                self.colors['text_primary']
                if self.current_theme == 'light'
                else self.colors['bg_dark']
            ),
            bg=self.colors['accent'],
            relief='flat',
            cursor='hand2',
            bd=0,
            borderwidth=0,
            highlightthickness=0,
            overrelief='flat',
            activebackground=self.colors['accent_hover'],
            activeforeground=(
                self.colors['text_primary']
                if self.current_theme == 'light'
                else self.colors['bg_dark']
            ),
            padx=8,
            pady=2,
            command=add_task
        )
        add_task_button.pack(side='right', padx=(12, 0))
        
        self._add_hover_effect(add_task_button, self.colors['accent'], 
                             self.colors.get('accent_hover', '#5b7fde'))
        
        progress_frame = tk.Frame(right_panel, bg=self.colors['bg_dark'])
        progress_frame.pack(fill='x', pady=(0, 16))
        
        progress_bar = tk.Canvas(
            progress_frame,
            height=7,
            bg=self.colors['bg_dark'],
            highlightthickness=0,
        )
        progress_bar.pack(fill='x', padx=0)
        progress_track = progress_bar.create_rectangle(
            0, 0, 1, 7,
            fill=self.colors['bg_dark'],
            outline='',
        )
        progress_value = progress_bar.create_rectangle(
            0, 0, 0, 7,
            fill=self.colors['accent'],
            outline='',
        )

        def render_progress(value):
            width = max(1, progress_bar.winfo_width())
            progress_bar.coords(progress_track, 0, 0, width, 7)
            progress_bar.coords(progress_value, 0, 0, width * value / 100, 7)

        progress_bar.bind(
            '<Configure>',
            lambda event: render_progress(
                int(progress_bar.coords(progress_value)[2] / max(1, event.width) * 100)
                if progress_bar.coords(progress_value) else 0
            ),
        )
        
        progress_label = tk.Label(
            progress_frame,
            text="0/0 (0%)",
            font=('Segoe UI', 9),
            fg=self.colors['text_muted'],
            bg=self.colors['bg_dark']
        )
        progress_label.pack(anchor='e', padx=2, pady=(2, 0))
        
        tasks_frame = tk.Frame(right_panel, bg=self.colors['bg_dark'])
        tasks_frame.pack(fill='both', expand=True, padx=0, pady=(0, 4))
        
        canvas = tk.Canvas(tasks_frame, bg=self.colors['bg_dark'], highlightthickness=0, cursor='arrow')
        scrollbar = ttk.Scrollbar(tasks_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox('all'))
            update_scrollbar_visibility()
        
        def on_canvas_configure(e):
            canvas.itemconfig(canvas_window, width=e.width)
            update_scrollbar_visibility()
        
        def update_scrollbar_visibility():
            scrollbar.pack_forget()
        
        scrollable_frame.bind('<Configure>', on_frame_configure)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.bind('<Configure>', on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_mousewheel(event):
            try:
                if canvas.bbox('all') is None:
                    return "break"
                
                canvas_height = canvas.winfo_height()
                scroll_region_height = canvas.bbox('all')[3] - canvas.bbox('all')[1]
                
                if scroll_region_height > canvas_height:
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                
                return "break"
            except:
                return "break"
        
        def _bind_mousewheel_recursive(widget):
            widget.bind('<MouseWheel>', _on_mousewheel)
            for child in widget.winfo_children():
                _bind_mousewheel_recursive(child)
        
        canvas.bind('<MouseWheel>', _on_mousewheel)
        scrollable_frame.bind('<MouseWheel>', _on_mousewheel)
        
        canvas.pack(side='left', fill='both', expand=True)
        
        task_checkboxes = {}
        
        def update_progress_and_checkboxes():
            total_tasks = len(game.get('tasks', []))
            completed_tasks = sum(1 for task in game.get('tasks', []) if task.get('done', False))
            progress_percentage = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
            render_progress(progress_percentage)
            progress_label.config(text=f"{completed_tasks}/{total_tasks} ({progress_percentage}%)")
            
            for idx, task in enumerate(game.get('tasks', [])):
                if idx in task_checkboxes:
                    indicator, checkbox = task_checkboxes[idx]
                    is_done = task.get('done', False)
                    indicator.delete('all')
                    indicator.create_oval(
                        2, 2, 19, 19,
                        outline=self.colors['accent'] if is_done else self.colors['text_muted'],
                        width=2,
                        fill=self.colors['accent'] if is_done else self.colors['bg_dark'],
                    )
                    if is_done:
                        indicator.create_line(6, 10, 9, 13, fill=self.colors['bg_dark'], width=2)
                        indicator.create_line(9, 13, 15, 7, fill=self.colors['bg_dark'], width=2)
                        checkbox.config(fg=self.colors['text_muted'], font=('Segoe UI', 10, 'overstrike'))
                    else:
                        checkbox.config(fg=self.colors['text_primary'], font=('Segoe UI', 10))
        
        def refresh_tasks_display():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            task_checkboxes.clear()
            
            if not game.get('tasks', []):
                no_tasks_label = tk.Label(
                    scrollable_frame,
                    text=self.get_text('no_objectives'),
                    font=('Segoe UI', 11),
                    fg=self.colors['text_muted'],
                    bg=self.colors['bg_dark'],
                    pady=24,
                )
                no_tasks_label.pack(fill='x', padx=12, pady=20)
            else:
                for idx, task in enumerate(game.get('tasks', [])):
                    task_item_frame = tk.Frame(
                        scrollable_frame,
                        bg=self.colors['bg_light'],
                        highlightthickness=1,
                        highlightbackground=self.colors['bg_medium'],
                    )
                    task_item_frame.pack(fill='x', expand=True, padx=8, pady=4)

                    left_container = tk.Frame(task_item_frame, bg=self.colors['bg_light'])
                    left_container.pack(side='left', fill='both', expand=True, padx=12, pady=11)

                    indicator = tk.Canvas(
                        left_container,
                        width=21,
                        height=21,
                        bg=self.colors['bg_light'],
                        highlightthickness=0,
                        cursor='hand2',
                    )
                    indicator.pack(side='left', padx=(0, 12))

                    checkbox = tk.Label(
                        left_container,
                        text=task.get('text', ''),
                        font=('Segoe UI', 10),
                        fg=self.colors['text_muted'] if task.get('done') else self.colors['text_primary'],
                        bg=self.colors['bg_light'],
                        anchor='w',
                        justify='left',
                        wraplength=520,
                        cursor='hand2',
                    )
                    checkbox.pack(side='left', fill='x', expand=True)

                    def toggle_task(task_idx=idx):
                        previous_value = game['tasks'][task_idx].get('done', False)
                        game['tasks'][task_idx]['done'] = not previous_value
                        if not self.save_games():
                            game['tasks'][task_idx]['done'] = previous_value
                            return
                        update_progress_and_checkboxes()

                    indicator.bind('<Button-1>', lambda event, action=toggle_task: action())
                    checkbox.bind('<Button-1>', lambda event, action=toggle_task: action())

                    task_checkboxes[idx] = (indicator, checkbox)
                    
                    right_container = tk.Frame(task_item_frame, bg=self.colors['bg_light'])
                    right_container.pack(side='right', padx=5, pady=5)
                    
                    delete_btn = tk.Button(
                        right_container,
                        text="✕",
                        font=('Segoe UI', 10, 'bold'),
                        bg=self.colors['bg_light'],
                        fg=self.colors['danger'],
                        relief='flat',
                        bd=0,
                        borderwidth=0,
                        highlightthickness=0,
                        overrelief='flat',
                        activebackground=self.colors['bg_light'],
                        activeforeground=self.colors['danger'],
                        cursor='hand2',
                        padx=4,
                        pady=0,
                        command=lambda t_idx=idx: delete_task(t_idx)
                    )
                    delete_btn.pack()

                    def set_task_hover(event, row=task_item_frame, hovered=True):
                        row.configure(
                            highlightbackground=(
                                self.colors['accent'] if hovered else self.colors['bg_medium']
                            )
                        )

                    for item in (
                        task_item_frame,
                        left_container,
                        indicator,
                        checkbox,
                        right_container,
                        delete_btn,
                    ):
                        item.bind('<Enter>', set_task_hover)
                        item.bind(
                            '<Leave>',
                            lambda event, row=task_item_frame: row.configure(
                                highlightbackground=self.colors['bg_medium']
                            ),
                        )

                    delete_btn.bind(
                        '<Enter>',
                        lambda event, button=delete_btn: button.configure(
                            bg=self.colors['bg_light'],
                            fg=self.blend_colors(
                                self.colors['danger'], '#ffffff', 0.75
                            ),
                        ),
                        add='+',
                    )
                    delete_btn.bind(
                        '<Leave>',
                        lambda event, button=delete_btn: button.configure(
                            bg=self.colors['bg_light'],
                            fg=self.colors['danger'],
                        ),
                        add='+',
                    )

                update_progress_and_checkboxes()
            
            total_tasks = len(game.get('tasks', []))
            completed_tasks = sum(1 for task in game.get('tasks', []) if task.get('done', False))
            progress_percentage = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
            
            render_progress(progress_percentage)
            progress_label.config(text=f"{completed_tasks}/{total_tasks} ({progress_percentage}%)")
            
            _bind_mousewheel_recursive(scrollable_frame)
        
        def delete_task(task_idx):
            if 'tasks' in game and task_idx < len(game['tasks']):
                removed_task = game['tasks'].pop(task_idx)
                if not self.save_games():
                    game['tasks'].insert(task_idx, removed_task)
                    return
                refresh_tasks_display()
        
        refresh_tasks_display()
        
        buttons_frame = tk.Frame(
            main_frame,
            bg=self.colors['bg_dark'],
        )
        buttons_frame.pack(fill='x', side='bottom', pady=(8, 0))
        
        center_buttons = tk.Frame(buttons_frame, bg=self.colors['bg_dark'])
        center_buttons.pack(side='right')
        
        button_style = {
            'font': ('Segoe UI', 11, 'bold'),
            'fg': (
                self.colors['text_primary']
                if self.current_theme == 'light'
                else self.colors['bg_dark']
            ),
            'relief': 'flat',
            'cursor': 'hand2',
            'pady': 11,
            'padx': 22,
            'bd': 0,
            'borderwidth': 0,
            'highlightthickness': 0,
            'overrelief': 'flat',
        }
        
        open_map_button = tk.Button(
            center_buttons,
            text=self.get_text('view_map'),
            bg=self.colors['accent'],
            **button_style,
            command=lambda: self.on_presentation_map_click(presentation_window, game)
        )
        open_map_button.pack(side='left', padx=(0, 15))
        
        close_button = tk.Button(
            center_buttons,
            text=self.get_text('close'),
            bg=self.colors['bg_medium'],
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text_primary'],
            relief='flat',
            cursor='hand2',
            pady=11,
            padx=22,
            bd=0,
            borderwidth=0,
            highlightthickness=0,
            overrelief='flat',
            command=presentation_window.destroy
        )
        close_button.pack(side='left')
        
        self._add_hover_effect(open_map_button, self.colors['accent'], 
                             self.colors.get('accent_hover', '#5b7fde'))
        self._add_hover_effect(
            close_button,
            self.colors['bg_medium'],
            self.colors['bg_dark'],
        )
        
        def on_presentation_mousewheel(event):
            try:
                widget_at_cursor = presentation_window.winfo_containing(event.x_root, event.y_root)
                if widget_at_cursor is not None:
                    for w in [canvas, scrollable_frame] + list(scrollable_frame.winfo_children()):
                        if w == widget_at_cursor or w.winfo_containing(event.x_root, event.y_root) == w:
                            return "break"
                return "break"
            except:
                pass
        
        presentation_window.bind('<MouseWheel>', on_presentation_mousewheel)
        
        presentation_window.deiconify()
        presentation_window.wait_visibility()
        presentation_window.grab_set()
    
    def get_map_type_label(self, map_type):
        """Obtener etiqueta legible para el tipo de mapa"""
        map_types = {
            'local': self.get_text('map_type_local') if hasattr(self, 'get_text') else 'Mapa Local',
            'web': self.get_text('map_type_web') if hasattr(self, 'get_text') else 'Guía Web',
            'image': self.get_text('map_type_image') if hasattr(self, 'get_text') else 'Mapa de Imagen'
        }
        return map_types.get(map_type, 'Tipo Desconocido')
    
    def _add_hover_effect(self, button, normal_color, hover_color):
        """Agregar efecto hover a un botón"""
        def on_enter(event):
            button.config(bg=hover_color)
        def on_leave(event):
            button.config(bg=normal_color)
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def on_presentation_map_click(self, presentation_window, game):
        """Manejar clic en botón de abrir mapa desde presentación"""
        self._close_presentation_and_open_map(presentation_window, game)
    
    def on_presentation_guide_click(self, presentation_window, game):
        """Manejar clic en botón de abrir guía desde presentación"""
        self._close_presentation_and_open_map(presentation_window, game)

    def _close_presentation_and_open_map(self, presentation_window, game):
        """Liberar la captura modal antes de cambiar de Tk a la ventana GTK."""
        try:
            if presentation_window.grab_current() == presentation_window:
                presentation_window.grab_release()
        except tk.TclError:
            pass

        presentation_window.destroy()
        self.root.after_idle(lambda: self.open_game_map(game))

    def open_game_map(self, game):
        """Abrir ventana con el mapa del juego"""
        print(f"Abriendo mapa para {game['name']} - Tipo: {game['map_type']}")  # Debug
        
        if game['map_type'] == 'image':
            # Para imágenes, crear ventana tkinter normal
            map_window = tk.Toplevel(self.root)
            map_window.transient(self.root)
            map_window.title(f"{self.get_text('map_window_title')} - {game['name']}")
            center_window_on_primary_monitor(map_window, 1000, 700)
            map_window.configure(bg=self.colors['bg_dark'])
            
            # Configurar icono de la ventana del mapa
            self.apply_window_icon(map_window)
            
            self.show_image_map(map_window, game)
        else:
            # Para mapas web, ir directamente a webview sin crear ventana tkinter
            self.show_iframe_map_direct(game)
    
    def show_iframe_map_direct(self, game):
        """Abrir el mapa con el motor WebKitGTK nativo, no con el navegador externo."""
        try:
            import webview

            monitor_x, monitor_y, monitor_width, monitor_height = get_primary_monitor_bounds(self.root)
            window_width = min(1000, monitor_width)
            window_height = min(700, monitor_height)
            window_x = monitor_x + (monitor_width - window_width) // 2
            window_y = monitor_y + (monitor_height - window_height) // 2
            web_window = webview.create_window(
                title=f"{self.get_text('map_window_title')} - {game['name']}",
                url=game['map_content'],
                width=window_width,
                height=window_height,
                x=window_x,
                y=window_y,
                resizable=True,
                minimized=False,
                on_top=False,
                shadow=True,
                text_select=True,
                focus=True
            )

            if sys.platform.startswith('linux'):
                from gi.repository import GLib

                def focus_webview():
                    native_window = web_window.native
                    if native_window is None:
                        return False

                    icon_path = resource_path('logo.png')
                    if os.path.isfile(icon_path):
                        native_window.set_icon_from_file(icon_path)
                    native_window.present()
                    scrolled_window = native_window.get_child()
                    web_widget = scrolled_window.get_child() if scrolled_window else None
                    if web_widget is not None:
                        web_widget.grab_focus()
                    return False

                web_window.events.shown += lambda: GLib.idle_add(focus_webview)
                webview.start(debug=False, gui='gtk')
            else:
                webview.start(debug=False)
        except Exception as e:
            print(f"Error iniciando el visor web nativo: {e}")
            if sys.platform.startswith('linux'):
                details = (
                    "No se pudo iniciar el visor WebKitGTK.\n\n"
                    "En CachyOS/Arch instala los paquetes del sistema "
                    "'webkit2gtk-4.1' y 'python-gobject', y las dependencias Python "
                    "de requirements.txt.\n\n"
                    f"Detalle: {e}"
                )
            else:
                details = f"No se pudo iniciar el visor web integrado.\n\nDetalle: {e}"
            messagebox.showerror(self.get_text('error'), details, parent=self.root)

    def create_tkinter_map_window(self, game):
        """Informar de que no hay motor web integrado disponible."""
        map_window = tk.Toplevel(self.root)
        map_window.transient(self.root)
        map_window.title(f"{self.get_text('map_window_title')} - {game['name']}")
        center_window_on_primary_monitor(map_window, 1000, 700)
        map_window.configure(bg=self.colors['bg_dark'])
        self.apply_window_icon(map_window)
        self.show_webview_fallback_in_frame(map_window, game)
    
    def show_image_map(self, window, game):
        """Mostrar mapa o guía de imagen con controles de zoom y desplazamiento."""
        try:
            with Image.open(game['map_content']) as source:
                canvas = tk.Canvas(
                    window,
                    bg=self.colors['bg_dark'],
                    highlightthickness=0,
                    bd=0,
                )
                toolbar = tk.Frame(window, bg=self.colors['bg_dark'])
                toolbar.pack(side=tk.TOP, fill=tk.X, padx=18, pady=(12, 6))

                controls = tk.Frame(toolbar, bg=self.colors['bg_dark'])
                controls.pack(side=tk.RIGHT)
                canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

                original_image = source.convert('RGBA')
                original_width, original_height = original_image.size
                canvas.original_image = original_image
                canvas.current_scale = 1.0
                canvas.is_manual_zoom = False

                zoom_label = tk.Label(
                    controls,
                    text='100%',
                    bg=self.colors['bg_dark'],
                    fg=self.colors['text_secondary'],
                    font=(self.ui_font_family, 9),
                    width=6,
                )
                zoom_label.pack(side=tk.LEFT, padx=(4, 8))

                def render_image(scale, anchor=None):
                    scale = max(0.1, min(5.0, scale))
                    old_width = max(1, round(original_width * canvas.current_scale))
                    old_height = max(1, round(original_height * canvas.current_scale))
                    if anchor is None:
                        anchor_x = canvas.winfo_width() / 2
                        anchor_y = canvas.winfo_height() / 2
                    else:
                        anchor_x, anchor_y = anchor
                    image_x = canvas.canvasx(anchor_x) / old_width
                    image_y = canvas.canvasy(anchor_y) / old_height

                    scaled_width = max(1, round(original_width * scale))
                    scaled_height = max(1, round(original_height * scale))
                    resized = original_image.resize(
                        (scaled_width, scaled_height),
                        Image.Resampling.LANCZOS,
                    )
                    photo = ImageTk.PhotoImage(resized, master=canvas)
                    canvas.delete('map-image')
                    canvas.create_image(
                        0,
                        0,
                        anchor=tk.NW,
                        image=photo,
                        tags='map-image',
                    )
                    canvas.image = photo
                    canvas.current_scale = scale
                    canvas.configure(
                        scrollregion=(0, 0, scaled_width, scaled_height),
                    )
                    zoom_label.configure(text=f'{round(scale * 100)}%')
                    canvas.update_idletasks()
                    if scaled_width > 0:
                        canvas.xview_moveto(
                            max(0, min(1, (image_x * scaled_width - anchor_x) / scaled_width))
                        )
                    if scaled_height > 0:
                        canvas.yview_moveto(
                            max(0, min(1, (image_y * scaled_height - anchor_y) / scaled_height))
                        )

                def zoom_by(factor, event=None):
                    anchor = (event.x, event.y) if event is not None else None
                    canvas.is_manual_zoom = True
                    render_image(canvas.current_scale * factor, anchor)

                def fit_image():
                    width = max(1, canvas.winfo_width())
                    height = max(1, canvas.winfo_height())
                    scale = min(width / original_width, height / original_height, 1.0)
                    canvas.is_manual_zoom = False
                    render_image(scale)

                def make_zoom_button(text, command, accent=False):
                    button = tk.Button(
                        controls,
                        text=text,
                        command=command,
                        bg=self.colors['accent'] if accent else self.colors['bg_light'],
                        fg=self.colors['bg_dark'] if accent else self.colors['text_primary'],
                        activebackground=self.colors['accent_hover'],
                        activeforeground=self.colors['bg_dark'],
                        relief='flat',
                        bd=0,
                        highlightthickness=0,
                        font=(self.ui_font_family, 9, 'bold'),
                        padx=12,
                        pady=6,
                        cursor='hand2',
                    )
                    button.pack(side=tk.LEFT, padx=(6, 0))
                    return button

                make_zoom_button('−', lambda: zoom_by(1 / 1.2))
                make_zoom_button('+', lambda: zoom_by(1.2))
                fit_labels = {
                    'es': 'Ajustar',
                    'en': 'Fit',
                    'fr': 'Ajuster',
                    'de': 'Einpassen',
                    'it': 'Adatta',
                    'pt': 'Ajustar',
                    'nl': 'Passend',
                    'ru': 'По размеру',
                    'ja': 'フィット',
                    'zh': '适合',
                }
                make_zoom_button(
                    fit_labels.get(self.current_language, 'Fit'),
                    fit_image,
                    accent=True,
                )

                def resize_to_fit(event):
                    if event.widget is canvas and not canvas.is_manual_zoom:
                        fit_image()

                def on_mousewheel(event):
                    if event.state & 0x4:
                        if getattr(event, 'num', None) == 4:
                            direction = 1
                        elif getattr(event, 'num', None) == 5:
                            direction = -1
                        else:
                            direction = 1 if event.delta > 0 else -1
                        zoom_by(1.2 if direction > 0 else 1 / 1.2, event)
                        return 'break'

                    if getattr(event, 'num', None) == 4:
                        canvas.yview_scroll(-3, 'units')
                    elif getattr(event, 'num', None) == 5:
                        canvas.yview_scroll(3, 'units')
                    else:
                        units = -int(event.delta / 120) if abs(event.delta) >= 120 else (-1 if event.delta > 0 else 1)
                        canvas.yview_scroll(units, 'units')
                    return 'break'

                def start_pan(event):
                    canvas.scan_mark(event.x, event.y)

                def pan_image(event):
                    canvas.scan_dragto(event.x, event.y, gain=1)

                canvas.bind('<Configure>', resize_to_fit, add='+')
                canvas.bind('<MouseWheel>', on_mousewheel)
                canvas.bind('<Button-4>', on_mousewheel)
                canvas.bind('<Button-5>', on_mousewheel)
                canvas.bind('<Button-1>', start_pan)
                canvas.bind('<B1-Motion>', pan_image)
                canvas.bind('<Double-Button-1>', lambda event: fit_image())
                window.bind('<Control-plus>', lambda event: (zoom_by(1.2), 'break')[1])
                window.bind('<Control-equal>', lambda event: (zoom_by(1.2), 'break')[1])
                window.bind('<Control-minus>', lambda event: (zoom_by(1 / 1.2), 'break')[1])

                window.after_idle(fit_image)

        except Exception as e:
            # Si no se puede cargar la imagen del mapa, mostrar imagen por defecto
            default_photo = self.create_default_image(800, 600, f"Error: No se pudo cargar\nel mapa de {game['name']}")
            
            if default_photo:
                # Crear canvas para mostrar la imagen por defecto
                canvas = tk.Canvas(window, bg=self.colors['bg_dark'], highlightthickness=0)
                canvas.create_image(400, 300, image=default_photo)
                canvas.image = default_photo  # Mantener referencia
                canvas.pack(fill="both", expand=True)
            else:
                # Fallback a texto si no se puede crear la imagen por defecto
                error_label = ttk.Label(window, 
                                       text=f"Error al cargar imagen del mapa:\n{str(e)}\n\nVerifica que el archivo de imagen existe y es válido.",
                                       style='Dark.TLabel',
                                       justify='center')
                error_label.pack(expand=True)
    
    def show_iframe_map(self, window, game):
        """Mostrar el mapa con el motor web nativo de Avilon."""
        window.destroy()
        self.show_iframe_map_direct(game)
    
    def show_html_browser(self, window, game):
        """No usar motores HTML incompletos como sustituto de WebKit."""
        self.show_webview_fallback_in_frame(window, game)
    
    def show_simple_redirect(self, window, game):
        """No delegar mapas a un navegador externo ni mostrar iframes incompletos."""
        self.show_webview_fallback_in_frame(window, game)
    
    def show_webview_fallback_in_frame(self, container, game):
        """Mostrar el error del motor web sin abrir páginas en otro navegador."""
        # Limpiar contenedor
        for widget in container.winfo_children():
            widget.destroy()
        
        # Mensaje informativo
        info_label = tk.Label(container,
                             text="⚠️ Error al cargar el mapa web",
                             bg=self.colors['bg_dark'],
                             fg=self.colors['text'],
                             font=('Arial', 14, 'bold'))
        info_label.pack(pady=(50, 10))
        
        message = (
            "WebKitGTK no está instalado o no se pudo iniciar."
            if sys.platform.startswith('linux')
            else "El visor web integrado no está disponible."
        )
        reason_label = tk.Label(
            container,
            text=f"{message}\n\nInstala o repara el motor web integrado y vuelve a intentarlo.",
            bg=self.colors['bg_dark'],
            fg=self.colors['text_muted'],
            font=('Arial', 10),
            justify='center'
        )
        reason_label.pack(pady=(0, 20))
    
    def edit_game(self, game):
        """Mostrar diálogo para editar juego"""
        dialog = tk.Toplevel(self.root)
        dialog.title(self.get_text('edit_game_title'))
        dialog.geometry("600x550")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Configurar icono del diálogo de edición
        self.apply_window_icon(dialog)
        
        # Centrar diálogo
        dialog.geometry("+{}+{}".format(
            self.root.winfo_rootx() + 300,
            self.root.winfo_rooty() + 125
        ))
        
        # Variables con valores actuales del juego
        self.edit_game_name_var = tk.StringVar(value=game['name'])
        self.edit_game_image_path = tk.StringVar(value=game['image_path'])
        self.edit_map_type_var = tk.StringVar(value=game['map_type'])
        self.edit_map_content_var = tk.StringVar(value=game['map_content'])
        self.edit_game_description_var = tk.StringVar(value=game.get('description', ''))
        self.edit_original_game = game
        
        # Configurar icono del diálogo de edición (segunda función)
        self.apply_window_icon(dialog)
        
        # Crear formulario de edición
        self.create_edit_game_form(dialog)
    
    def create_edit_game_form(self, parent):
        """Crear formulario para editar juego"""
        # Frame principal del formulario
        form_frame = ttk.Frame(parent, style='Dark.TFrame')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(form_frame, text=self.get_text('edit_game_title'),
                               style='Dark.TLabel',
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Nombre del juego
        name_label = ttk.Label(form_frame, text=self.get_text('game_name'),
                              style='Dark.TLabel')
        name_label.pack(anchor=tk.W, pady=(0, 5))
        
        name_entry = tk.Entry(form_frame, textvariable=self.edit_game_name_var,
                             bg=self.colors['bg_light'], fg=self.colors['text'],
                             font=('Segoe UI', 10), relief='flat',
                             insertbackground=self.colors['text'])
        name_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
        
        # Imagen del juego
        image_label = ttk.Label(form_frame, text=self.get_text('game_image'),
                               style='Dark.TLabel')
        image_label.pack(anchor=tk.W, pady=(0, 5))
        
        image_frame = ttk.Frame(form_frame, style='Dark.TFrame')
        image_frame.pack(fill=tk.X, pady=(0, 15))
        
        image_entry = tk.Entry(image_frame, textvariable=self.edit_game_image_path,
                              bg=self.colors['bg_light'], fg=self.colors['text'],
                              font=('Segoe UI', 10), relief='flat',
                              insertbackground=self.colors['text'],
                              state='readonly',
                              readonlybackground=self.colors['bg_light'])
        image_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        browse_button = ttk.Button(image_frame, text=self.get_text('browse_map'),
                                  command=self.browse_edit_image)
        browse_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Tipo de mapa
        map_type_label = ttk.Label(form_frame, text=self.get_text('map_type_label'),
                                  style='Dark.TLabel')
        map_type_label.pack(anchor=tk.W, pady=(0, 5))
        
        map_type_frame = ttk.Frame(form_frame, style='Dark.TFrame')
        map_type_frame.pack(fill=tk.X, pady=(0, 15))
        
        def toggle_edit_browse_button():
            """Mostrar/ocultar botón examinar y controlar estado de entrada según tipo de mapa"""
            if self.edit_map_type_var.get() == "image":
                self.edit_game_browse_button.pack(side=tk.RIGHT, padx=(10, 0))
                map_content_entry.config(
                    state='readonly',
                    readonlybackground=self.colors['bg_light'],
                )
            else:
                self.edit_game_browse_button.pack_forget()
                map_content_entry.config(state='normal', bg=self.colors['bg_light'], fg=self.colors['text'])
        
        image_radio = tk.Radiobutton(map_type_frame, text=self.get_text('map_type_image'),
                                    variable=self.edit_map_type_var, value="image",
                                    command=toggle_edit_browse_button,
                                    bg=self.colors['bg_dark'], fg=self.colors['text'],
                                    selectcolor=self.colors['bg_light'],
                                    activebackground=self.colors['bg_dark'])
        image_radio.pack(side=tk.LEFT)
        
        iframe_radio = tk.Radiobutton(map_type_frame, text=self.get_text('map_type_web'),
                                     variable=self.edit_map_type_var, value="iframe",
                                     command=toggle_edit_browse_button,
                                     bg=self.colors['bg_dark'], fg=self.colors['text'],
                                     selectcolor=self.colors['bg_light'],
                                     activebackground=self.colors['bg_dark'])
        iframe_radio.pack(side=tk.LEFT, padx=(20, 0))
        
        # Contenido del mapa
        map_content_label = ttk.Label(form_frame, text=self.get_text('map_content'),
                                     style='Dark.TLabel')
        map_content_label.pack(anchor=tk.W, pady=(0, 5))
        
        map_content_frame = ttk.Frame(form_frame, style='Dark.TFrame')
        map_content_frame.pack(fill=tk.X, pady=(0, 20))
        
        map_content_entry = tk.Entry(map_content_frame, textvariable=self.edit_map_content_var,
                                    bg=self.colors['bg_dark'], fg=self.colors['text'],
                                    font=('Segoe UI', 10), relief='flat',
                                    insertbackground=self.colors['text'],
                                    readonlybackground=self.colors['bg_light'])
        map_content_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        self.edit_game_browse_button = ttk.Button(map_content_frame, text=self.get_text('browse_map'),
                                      command=self.browse_edit_map_content)
        self.edit_game_browse_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Establecer estado inicial del botón basado en el tipo de mapa actual
        toggle_edit_browse_button()
        
        # Botones
        button_frame = ttk.Frame(form_frame, style='Dark.TFrame')
        button_frame.pack(fill=tk.X)
        
        cancel_button = ttk.Button(button_frame, text=self.get_text('cancel'),
                                  command=parent.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        save_button = ttk.Button(button_frame, text=self.get_text('save_changes'),
                                style='Accent.TButton',
                                command=lambda: self.save_edited_game(parent))
        save_button.pack(side=tk.RIGHT)
        
        # Bind Enter para guardar
        parent.bind('<Return>', lambda event: self.save_edited_game(parent))
    
    def browse_edit_image(self):
        """Explorar imagen para el juego (modo edición)"""
        filename = filedialog.askopenfilename(
            title="Seleccionar imagen del juego",
            filetypes=[("Archivos de imagen", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if filename:
            self.edit_game_image_path.set(filename)
    
    def browse_edit_map_content(self):
        """Explorar contenido del mapa (modo edición)"""
        if self.edit_map_type_var.get() == "image":
            filename = filedialog.askopenfilename(
                title="Seleccionar imagen del mapa",
                filetypes=[("Archivos de imagen", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if filename:
                self.edit_map_content_var.set(filename)
        else:
            # Para iframe, permitir entrada manual de URL
            url = simpledialog.askstring("URL del mapa", "Introduce la URL (debe comenzar con http:// o https://):")
            if url:
                self.edit_map_content_var.set(url)
    
    def save_edited_game(self, dialog):
        """Guardar cambios del juego editado"""
        # Validar campos
        name = self.edit_game_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "El nombre del juego no puede estar vacío")
            return
        
        image_path = self.edit_game_image_path.get().strip()
        map_content = self.edit_map_content_var.get().strip()
        map_type = self.edit_map_type_var.get()
        
        # Validar imagen si se cambió
        if image_path and image_path != self.edit_original_game['image_path']:
            is_valid, error_msg = self.validate_image_file(image_path)
            if not is_valid:
                messagebox.showerror("Error de imagen", error_msg)
                return
        
        # Validar contenido del mapa
        if not map_content:
            messagebox.showerror("Error", "Debe especificar el contenido del mapa")
            return
        
        if map_type == "image":
            is_valid, error_msg = self.validate_image_file(map_content)
            if not is_valid:
                messagebox.showerror("Error de mapa", error_msg)
                return
        elif map_type == "iframe":
            if not (map_content.startswith("http://") or map_content.startswith("https://")):
                messagebox.showerror("Error", "La URL debe comenzar con http:// o https://")
                return
        
        # Copiar imagen del juego si cambió
        local_image_path = image_path
        if image_path and image_path != self.edit_original_game['image_path']:
            local_image_path = self.copy_image_to_local(image_path, name, "game")
            if not local_image_path:
                messagebox.showerror("Error", "No se pudo copiar la nueva imagen del juego")
                return
        elif not image_path:
            # Si no se especificó imagen, mantener la original
            local_image_path = self.edit_original_game['image_path']
        
        # Copiar imagen del mapa si cambió y es de tipo imagen
        local_map_content = map_content
        if map_type == "image" and map_content != self.edit_original_game.get('map_content', ''):
            local_map_content = self.copy_image_to_local(map_content, name, "map")
            if not local_map_content:
                messagebox.showerror("Error", "No se pudo copiar la nueva imagen del mapa")
                return
        
        # Actualizar el juego en la lista preservando campos existentes
        game_index = self.games.index(self.edit_original_game)
        previous_game = self.games[game_index]
        self.games[game_index] = {
            'name': name,
            'image_path': local_image_path,
            'map_type': map_type,
            'map_content': local_map_content,
            'favorite': self.edit_original_game.get('favorite', False),
            'tasks': self.edit_original_game.get('tasks', []),
            'description': self.edit_original_game.get('description', ''),
            'date_added': self.edit_original_game.get('date_added', datetime.now().isoformat()),
            'total_play_time': self.edit_original_game.get('total_play_time', 0),
            'last_opened_at': self.edit_original_game.get('last_opened_at')
        }
        
        # Guardar y actualizar la interfaz
        if not self.save_games():
            self.games[game_index] = previous_game
            return
        self.refresh_games_display()
        
        # Limpiar imágenes no utilizadas
        self.cleanup_unused_images()
        
        messagebox.showinfo("Éxito", f"Juego '{name}' actualizado correctamente")
        dialog.destroy()
    
    def delete_game(self, game):
        """Eliminar juego"""
        confirm_title = self.get_text('confirm_title')
        confirm_message = self.get_text('confirm_delete').replace('este juego', f"'{game['name']}'").replace('this game', f"'{game['name']}'")
        
        if messagebox.askyesno(confirm_title, confirm_message):
            game_index = self.games.index(game)
            self.games.remove(game)
            if not self.save_games():
                self.games.insert(game_index, game)
                return
            self.refresh_games_display()
            
            # Limpiar imágenes no utilizadas después de eliminar
            self.cleanup_unused_images()
    
    def load_games(self):
        """Cargar juegos desde archivo JSON"""
        if os.path.exists(self.games_file):
            try:
                with open(self.games_file, 'r', encoding='utf-8') as f:
                    games = json.load(f)
                    for game in games:
                        if 'tasks' not in game:
                            game['tasks'] = []
                        if 'description' not in game:
                            game['description'] = ''
                        if 'date_added' not in game:
                            game['date_added'] = datetime.now().isoformat()
                        if 'total_play_time' not in game:
                            game['total_play_time'] = 0
                        game.setdefault('last_opened_at', None)
                    return games
            except Exception as e:
                print(f"Error cargando juegos: {e}")
                return []
        return []
    
    def save_games(self):
        """Guardar juegos en el archivo local de la biblioteca."""
        temporary_file = f"{self.games_file}.tmp"
        try:
            with open(temporary_file, 'w', encoding='utf-8') as output:
                json.dump(self.games, output, indent=2, ensure_ascii=False)
            os.replace(temporary_file, self.games_file)
            return True
        except OSError as error:
            try:
                os.remove(temporary_file)
            except FileNotFoundError:
                pass
            print(f"Error guardando juegos: {error}")
            messagebox.showerror(
                self.get_text('error'),
                f"No se pudo guardar la biblioteca local.\n\n{error}",
                parent=self.root
            )
            return False
    
    def on_closing(self):
        """Método llamado al cerrar la aplicación para limpiar recursos"""
        try:
            # Limpiar CEF si está inicializado
            try:
                from cefpython3 import cefpython as cef
                if cef.GetAppSetting("initialized"):
                    cef.Shutdown()
            except ImportError:
                pass
            except Exception as e:
                print(f"Error cerrando CEF: {e}")
        except Exception as e:
            print(f"Error en cleanup: {e}")
        finally:
            # Cerrar la aplicación
            self.root.quit()
            self.root.destroy()

    def edit_game(self, game):
        """Mostrar di�logo para editar juego"""
        dialog = tk.Toplevel(self.root)
        dialog.title(self.get_text('edit_game_title'))
        dialog.geometry("600x550")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        self.apply_window_icon(dialog)
        
        # Centrar di�logo
        dialog.geometry("+{}+{}".format(
            self.root.winfo_rootx() + 300,
            self.root.winfo_rooty() + 125
        ))
        
        # Variables con valores actuales del juego
        self.edit_game_name_var = tk.StringVar(value=game['name'])
        self.edit_game_image_path = tk.StringVar(value=game['image_path'])
        self.edit_map_type_var = tk.StringVar(value=game['map_type'])
        self.edit_map_content_var = tk.StringVar(value=game['map_content'])
        self.edit_original_game = game
        
        # Crear formulario de edici�n
        self.create_edit_game_form(dialog)

def main():
    def load_config_for_splash():
        """Cargar configuración antes del splash screen"""
        try:
            base_dir = prepare_app_data_dir()
            
            config_file = os.path.join(base_dir, "avilon_config.json")
            config = {'language': 'es', 'theme': 'slate', 'startup': False}
            
            if os.path.exists(config_file):
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    config.update(loaded_config)
            
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return {'language': 'es', 'theme': 'slate', 'startup': False}
    
    def start_main_app():
        """Iniciar la biblioteca local después del splash."""
        root = tk.Tk()
        AvalonGameManager(root)
        root.mainloop()
    
    config = load_config_for_splash()
    language = config.get('language', 'es')
    
    translations_temp = {}
    try:
        temp_app = AvalonGameManager.__new__(AvalonGameManager)
        translations_temp = temp_app.load_translations()
    except:
        pass
    
    splash = SplashScreen(language=language, translations=translations_temp)
    splash.show(on_complete=start_main_app)

if __name__ == "__main__":
    main()
