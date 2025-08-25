# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
import shutil
from PIL import Image, ImageTk
import webbrowser
import tkinter.font as tkFont
import urllib.parse
import re
import time
import subprocess
import sys
import platform

def resource_path(relative_path):
    """Obtener la ruta correcta para recursos, funciona tanto en .py como en .exe"""
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
import threading
import winreg

class SplashScreen:
    def __init__(self):
        self.splash = tk.Tk()
        self.splash.title("Avilon")
        
        # Ocultar inmediatamente la ventana para evitar el parpadeo
        self.splash.withdraw()
        
        # Configurar icono
        try:
            icon_path = resource_path("logo.ico")
            if os.path.exists(icon_path):
                self.splash.iconbitmap(icon_path)
        except Exception as e:
            print(f"No se pudo cargar el icono del splash: {e}")
        
        # Configurar ventana sin bordes y centrada
        self.splash.overrideredirect(True)
        self.splash.configure(bg='#0a0a0a')
        
        # Dimensiones del splash (más grande para más profesional)
        splash_width = 500
        splash_height = 350
        
        # Centrar la ventana
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        x = (screen_width - splash_width) // 2
        y = (screen_height - splash_height) // 2
        
        self.splash.geometry(f"{splash_width}x{splash_height}+{x}+{y}")
        
        # Crear canvas para efectos de fondo
        self.canvas = tk.Canvas(
            self.splash, 
            width=splash_width, 
            height=splash_height,
            highlightthickness=0,
            bg='#0a0a0a'
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
        
        # Contenedor principal
        self.setup_main_content()
        
        # Configurar estilo de la barra de progreso
        self.setup_progress_style()
        
        # Iniciar animaciones de entrada
        self.start_entrance_animation()
        
    def create_gradient_background(self):
        """Crear fondo con gradiente profesional minimalista"""
        # Colores del gradiente elegante (de arriba a abajo)
        colors = [
            '#0a0a0a',  # Negro profundo
            '#151515',  # Negro suave
            '#1a1a1a',  # Gris muy oscuro
            '#202020',  # Gris oscuro
            '#1a1a1a',  # Gris muy oscuro
            '#151515',  # Negro suave
            '#0a0a0a'   # Negro profundo
        ]
        
        height_per_section = 350 // len(colors)
        
        for i, color in enumerate(colors):
            y1 = i * height_per_section
            y2 = (i + 1) * height_per_section
            self.canvas.create_rectangle(
                0, y1, 500, y2,
                fill=color, outline=color
            )
    
    def create_border_glow(self):
        """Crear borde con efecto glow minimalista"""
        # Borde exterior con gradiente elegante y sutil
        border_colors = ['#c9b037', '#d4d4d4', '#e8e8e8', '#f5f5f5']
        
        for i, color in enumerate(border_colors):
            thickness = len(border_colors) - i
            self.canvas.create_rectangle(
                i, i, 500-i, 350-i,
                outline=color, width=thickness, fill=''
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
            logo_path = resource_path("logo.ico")
            
            if os.path.exists(logo_path):
                # Cargar y redimensionar el logo
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((80, 80), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                
                # Posición inicial del logo (será animada)
                self.logo_id = self.canvas.create_image(
                    250, 70, image=self.logo_photo, anchor='center'
                )
            else:
                # Logo placeholder más profesional
                self.logo_id = self.canvas.create_text(
                    250, 70, text="🚀", font=('Segoe UI Emoji', 60),
                    fill='#c9b037', anchor='center'
                )
        except Exception:
            # Fallback logo
            self.logo_id = self.canvas.create_text(
                250, 70, text="🚀", font=('Segoe UI Emoji', 60),
                fill='#c9b037', anchor='center'
            )
    
    def create_title(self):
        """Crear título con efecto glow"""
        # Sombra del título (sutil)
        self.canvas.create_text(
            251, 131, text="AVILON", 
            font=('Segoe UI', 32, 'bold'),
            fill='#404040', anchor='center'
        )
        
        # Título principal
        self.title_id = self.canvas.create_text(
            250, 130, text="AVILON", 
            font=('Segoe UI', 32, 'bold'),
            fill='#ffffff', anchor='center'
        )
    
    def create_subtitle(self):
        """Crear subtítulo elegante"""
        self.subtitle_id = self.canvas.create_text(
            250, 160, text="Game Library Manager", 
            font=('Segoe UI', 12),
            fill='#a0a0a0', anchor='center'
        )
    
    def create_modern_progress_bar(self):
        """Crear barra de progreso moderna"""
        # Fondo de la barra
        self.progress_bg = self.canvas.create_rectangle(
            100, 220, 400, 235,
            fill='#2a2a2a', outline='#404040', width=1
        )
        
        # Barra de progreso activa (inicialmente invisible)
        self.progress_fill = self.canvas.create_rectangle(
            100, 220, 100, 235,
            fill='', outline=''
        )
        
        # Variables para progreso
        self.progress_value = 0
    
    def create_status_area(self):
        """Crear área de estado y versión"""
        # Estado de carga
        self.status_id = self.canvas.create_text(
            250, 255, text="Iniciando...", 
            font=('Segoe UI', 10),
            fill='#b0b0b0', anchor='center'
        )
        
        # Versión
        self.version_id = self.canvas.create_text(
            250, 320, text="v1.5.2", 
            font=('Segoe UI', 9),
            fill='#808080', anchor='center'
        )
    
    def create_decorative_particles(self):
        """Crear partículas decorativas"""
        self.particles = []
        import random
        
        for _ in range(20):
            x = random.randint(50, 450)
            y = random.randint(50, 300)
            size = random.randint(1, 3)
            
            particle = self.canvas.create_oval(
                x, y, x+size, y+size,
                fill='#c9b037', outline='', stipple='gray25'
            )
            self.particles.append(particle)
    
    def start_entrance_animation(self):
        """Iniciar animaciones de entrada"""
        self.animate_logo_entrance()
        self.animate_title_fade_in()
        self.animate_particles()
    
    def animate_logo_entrance(self):
        """Animar entrada del logo"""
        if self.logo_animation_step < 20:
            # Efecto de "bounce in"
            scale = 0.5 + (self.logo_animation_step / 20) * 0.5
            if self.logo_animation_step > 15:
                scale += 0.1 * (20 - self.logo_animation_step) / 5
            
            self.logo_animation_step += 1
            self.splash.after(50, self.animate_logo_entrance)
    
    def animate_title_fade_in(self):
        """Animar fade in del título"""
        if self.title_alpha < 255:
            self.title_alpha += 15
            # Aplicar efecto de fade (simulado con colores)
            self.splash.after(100, self.animate_title_fade_in)
    
    def animate_particles(self):
        """Animar partículas flotantes"""
        import random
        
        for particle in self.particles:
            coords = self.canvas.coords(particle)
            if len(coords) >= 4:
                # Movimiento aleatorio sutil
                dx = random.uniform(-0.5, 0.5)
                dy = random.uniform(-0.5, 0.5)
                self.canvas.move(particle, dx, dy)
                
                # Cambiar opacidad aleatoriamente
                if random.random() < 0.1:
                    colors = ['#c9b037', '#d4d4d4', '#a0a0a0', '#e8e8e8']
                    new_color = random.choice(colors)
                    self.canvas.itemconfig(particle, fill=new_color)
        
        self.splash.after(100, self.animate_particles)
    
    def setup_progress_style(self):
        """Configurar el estilo de la barra de progreso"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores modernos para la barra
        style.configure(
            "Modern.TProgressbar",
            background='linear-gradient(90deg, #404040, #c9b037)',
            troughcolor='#2a2a2a',
            borderwidth=0,
            lightcolor='#c9b037',
            darkcolor='#404040',
            relief='flat'
        )
    
    def update_progress(self, value, status_text):
        """Actualizar la barra de progreso y el texto de estado con animación"""
        # Actualizar barra de progreso
        self.progress_value = value
        progress_width = int((value / 100) * 300)  # 300 es el ancho total de la barra
        
        # Crear gradiente para la barra de progreso
        self.canvas.delete(self.progress_fill)
        if value > 0:
            # Crear barra con gradiente elegante
            colors = ['#404040', '#707070', '#c9b037']
            segment_width = progress_width // len(colors) if progress_width > 0 else 0
            
            x_start = 100
            for i, color in enumerate(colors):
                x_end = min(x_start + segment_width, 100 + progress_width)
                if x_end > x_start:
                    self.canvas.create_rectangle(
                        x_start, 220, x_end, 235,
                        fill=color, outline=''
                    )
                x_start = x_end
                if x_start >= 100 + progress_width:
                    break
            
            # Efecto de brillo en la barra
            if value > 5:
                shine_x = 100 + progress_width - 20
                self.canvas.create_rectangle(
                    shine_x, 220, shine_x + 10, 235,
                    fill='#ffffff', outline='', stipple='gray25'
                )
        
        # Actualizar texto de estado con animación
        self.canvas.itemconfig(self.status_id, text=status_text)
        
        # Efecto de pulsación para el estado
        self.animate_status_pulse()
        
        self.splash.update()
    
    def animate_status_pulse(self):
        """Animar pulsación del texto de estado"""
        colors = ['#b0b0b0', '#ffffff', '#b0b0b0']
        for i, color in enumerate(colors):
            self.splash.after(i * 100, lambda c=color: self.canvas.itemconfig(self.status_id, fill=c))
    
    def simulate_loading(self):
        """Simular proceso de carga con efectos visuales mejorados"""
        self.loading_steps = [
            (5, "🔧 Inicializando componentes..."),
            (15, "⚙️ Cargando configuración..."),
            (30, "📁 Verificando archivos..."),
            (45, "🎨 Configurando interfaz..."),
            (60, "🎮 Preparando biblioteca de juegos..."),
            (75, "🔍 Indexando contenido..."),
            (90, "✨ Aplicando últimos toques..."),
            (100, "🚀 ¡Listo para despegar!")
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
            self.splash.after(delay, self.update_loading_step)
        else:
            # Completar la carga con animación de salida
            self.splash.after(800, self.start_exit_animation)
    
    def create_loading_effect(self):
        """Crear efecto visual durante la carga"""
        # Crear ondas de energía desde el logo
        for i in range(3):
            self.splash.after(i * 100, self.create_energy_wave)
    
    def create_energy_wave(self):
        """Crear onda de energía"""
        import random
        
        # Crear círculo expandiéndose desde el logo
        wave = self.canvas.create_oval(
            245, 65, 255, 75,
            outline='#c9b037', width=2, fill=''
        )
        
        def expand_wave(size=0):
            if size < 50:
                new_size = size + 5
                self.canvas.coords(wave, 
                                 250 - new_size, 70 - new_size,
                                 250 + new_size, 70 + new_size)
                
                # Desvanecer el color
                alpha = max(0, 255 - size * 5)
                self.splash.after(50, lambda: expand_wave(new_size))
            else:
                self.canvas.delete(wave)
        
        expand_wave()
    
    def start_exit_animation(self):
        """Iniciar animación de salida"""
        self.exit_alpha = 255
        self.fade_out()
    
    def fade_out(self):
        """Animación de fade out"""
        if self.exit_alpha > 0:
            self.exit_alpha -= 15
            
            # Simular fade out moviendo elementos
            for particle in self.particles:
                self.canvas.move(particle, 0, 2)
            
            self.splash.after(50, self.fade_out)
        else:
            self.close_splash()
    
    def close_splash(self):
        """Cerrar el splash screen con callback"""
        try:
            self.splash.destroy()
        except:
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
                self.splash.after(30, lambda: fade_in(alpha))
            else:
                # Iniciar simulación de carga después del fade in
                self.splash.after(500, self.simulate_loading)
        
        fade_in()
        self.splash.mainloop()

class AvalonGameManager:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1200x800")
        self.root.configure(bg="#2f3136")
        
        # Obtener directorio base del programa (funciona tanto en .py como en .exe)
        if getattr(sys, 'frozen', False):
            # Si está ejecutándose como ejecutable, usar AppData para datos del usuario
            self.base_dir = os.path.join(os.environ['APPDATA'], 'Avilon')
            # Crear el directorio si no existe
            os.makedirs(self.base_dir, exist_ok=True)
        else:
            # Si está ejecutándose como script (desarrollo)
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Configurar icono de la ventana principal
        try:
            self.icon_path = resource_path("logo.ico")
            if os.path.exists(self.icon_path):
                self.root.iconbitmap(self.icon_path)
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")
            self.icon_path = None
        
        # Archivo para almacenar los juegos
        self.games_file = os.path.join(self.base_dir, "avilon_games.json")
        self.games = self.load_games()
        
        # Crear directorio de imágenes si no existe
        self.images_dir = os.path.join(self.base_dir, "game_images")
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Variable para la búsqueda
        self.search_var = None
        
        # Sistema de favoritos
        self.favorites_filter = "all"  # "all" o "favorites"
        
        # Sistema de idiomas y configuración
        self.config_file = os.path.join(self.base_dir, "avilon_config.json")
        self.config = self.load_config()
        self.current_language = self.config.get('language', 'es')
        self.current_theme = self.config.get('theme', 'slate')
        self.startup_enabled = self.config.get('startup', False)
        self.translations = self.load_translations()
        self.themes = self.load_themes()
        
        # Establecer título con traducciones
        self.root.title(self.get_text('window_title'))
        
        # Configurar estilo Discord-like
        self.setup_styles()
        
        # Crear barra de menú
        self.create_menu_bar()
        
        # Crear la interfaz
        self.create_main_interface()
        
        # Cargar juegos existentes
        self.refresh_games_display()
        
        # Migrar juegos existentes al directorio local (solo la primera vez)
        self.migrate_existing_games()
        
        # Binding para redimensionamiento responsive
        self.root.bind('<Configure>', self.on_window_resize)
        
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
    
    def apply_window_icon(self, window):
        """Aplicar el icono a cualquier ventana"""
        try:
            if hasattr(self, 'icon_path') and self.icon_path and os.path.exists(self.icon_path):
                window.iconbitmap(self.icon_path)
        except Exception as e:
            print(f"No se pudo aplicar el icono a la ventana: {e}")
    
    def setup_keyboard_shortcuts(self):
        """Configurar atajos de teclado para mayor comodidad"""
        # Atajo para añadir juego (Ctrl+N)
        self.root.bind('<Control-n>', lambda e: self.show_add_game_dialog())
        self.root.bind('<Control-N>', lambda e: self.show_add_game_dialog())
        
        # Atajo para configuración (Ctrl+Shift+P)
        self.root.bind('<Control-Shift-P>', lambda e: self.show_config_dialog())
        self.root.bind('<Control-Shift-p>', lambda e: self.show_config_dialog())
        
        # Atajo para guía de usuario (F1)
        self.root.bind('<F1>', lambda e: self.show_user_guide_dialog())
        
        # Atajo para buscar (Ctrl+F)
        self.root.bind('<Control-f>', lambda e: self.focus_search_bar())
        self.root.bind('<Control-F>', lambda e: self.focus_search_bar())
        
        # Atajo para limpiar búsqueda (Escape)
        self.root.bind('<Escape>', lambda e: self.clear_search_and_focus())
        
        # Atajo para actualizar lista (F5)
        self.root.bind('<F5>', lambda e: self.refresh_games_display())
        
        # Atajo para mostrar solo favoritos (Ctrl+Shift+F)
        self.root.bind('<Control-Shift-F>', lambda e: self.toggle_favorites_filter())
        self.root.bind('<Control-Shift-f>', lambda e: self.toggle_favorites_filter())
        
        # Atajo para salir de la aplicación (Ctrl+Q)
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<Control-Q>', lambda e: self.on_closing())
    
    def focus_search_bar(self):
        """Enfocar la barra de búsqueda"""
        if hasattr(self, 'search_entry') and self.search_entry:
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
        
        # Actualizar el fondo de la ventana principal
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Configurar ttk styles
        style.theme_use('clam')
        style.configure('Dark.TFrame', background=self.colors['bg_dark'])
        style.configure('Sidebar.TFrame', background=self.colors['sidebar'])
        
        # Estilo mejorado para tarjetas de juegos con gradiente sutil
        style.configure('Game.TFrame', 
                       background=self.colors['bg_light'],
                       relief='flat',
                       borderwidth=1)
        
        # Color más claro para hover (dinámico según el tema) con efecto gradiente
        if self.current_theme == 'light':
            hover_color = '#f0f0f0'
            self.card_shadow_color = '#e0e0e0'
        else:
            hover_color = '#4a5058'
            self.card_shadow_color = '#25282c'
            
        style.configure('GameHover.TFrame', 
                       background=self.colors['bg_light'],
                       relief='solid',
                       borderwidth=1)
        
        style.configure('Dark.TLabel', 
                       background=self.colors['bg_dark'], 
                       foreground=self.colors['text'])
        
        # Configurar estilos específicos para diferentes elementos según el tema
        if self.current_theme == 'light':
            button_text_color = '#ffffff'  # Texto blanco para botones en tema claro
        else:
            button_text_color = self.colors['text']
        
        style.configure('Accent.TButton',
                       background=self.colors['accent'],
                       foreground=button_text_color,
                       borderwidth=0,
                       focuscolor='none')
        
        # Color activo dinámico para botones
        if self.current_theme == 'light':
            active_color = '#004499'
        elif self.current_theme == 'slate':
            active_color = '#677bc4'
        else:
            active_color = self.colors['accent']
            
        style.map('Accent.TButton',
                 background=[('active', active_color)])
        
        # Estilos adicionales para elementos profesionales
        style.configure('GameTitle.TLabel',
                       background=self.colors['bg_light'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 11, 'bold'))
        
        style.configure('GameSubtitle.TLabel',
                       background=self.colors['bg_light'],
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 9))
    
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
                'add_game_button': '+ Añadir Juego',
                'library': 'BIBLIOTECA',
                'games_count': 'juegos',
                'game_singular': 'juego',
                'no_games': 'No hay juegos en tu biblioteca.\nVe a "Archivo" → "Añadir Juego" para comenzar.',
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
                'config_subtitle': 'Personaliza tu experiencia de juego',
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
                'add_to_favorites': 'Añadir a favoritos',
                'remove_from_favorites': 'Quitar de favoritos',
                
                # Inicio automático
                'startup_label': 'Iniciar con Windows:',
                'startup_enabled': 'Programa configurado para iniciar con Windows',
                'startup_disabled': 'Programa removido del inicio automático',
                'startup_error': 'Error al configurar el inicio automático',
                
                # Guía de uso
                'how_to_use_menu': 'Cómo se usa',
                'user_guide_title': 'Guía de Usuario - Cómo usar Avilon',
                'guide_tab_games': 'Juegos',
                'guide_tab_maps': 'Mapas', 
                'guide_tab_features': 'Características',
                'guide_tab_tips': 'Consejos',
                
                # Pestaña Juegos
                'guide_games_title': '🎮 Gestión de Juegos',
                'guide_games_add_title': '📝 Cómo agregar un juego:',
                'guide_games_add_content': '''1. Ve al menú "Archivo" → "Añadir Juego"
2. Completa el nombre del juego
3. Selecciona una imagen (opcional):
   • Formatos soportados: PNG, JPG, JPEG, BMP, GIF
   • Recomendado: 250x280 píxeles
4. Configura el mapa (ver pestaña "Mapas")
5. Haz clic en "Guardar"''',
                'guide_games_manage_title': '⚙️ Gestionar juegos existentes:',
                'guide_games_manage_content': '''• Hacer clic en ⭐ para marcar/desmarcar como favorito
• Usar "Ver mapa" para abrir el mapa del juego
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
• Inicia con Windows si está habilitado
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
                'guide_shortcuts_workflow_content': '''1. Ctrl + N para añadir juegos rápidamente
2. Ctrl + F para buscar sin usar el ratón
3. Escape para limpiar y empezar de nuevo
4. Ctrl + Shift + F para ver solo tus favoritos
5. F5 para refrescar cuando agregues archivos manualmente''',
                
                # Subtítulo de la guía
                'guide_subtitle': 'Todo lo que necesitas saber para usar Avilon'
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
                'add_game_button': '+ Add Game',
                'library': 'LIBRARY',
                'games_count': 'games',
                'game_singular': 'game',
                'no_games': 'No games in your library.\nGo to "File" → "Add Game" to get started.',
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
                'config_subtitle': 'Customize your gaming experience',
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
                
                # Game buttons
                'view_map': 'View map',
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
                'add_to_favorites': 'Add to favorites',
                'remove_from_favorites': 'Remove from favorites',
                
                # Startup
                'startup_label': 'Start with Windows:',
                'startup_enabled': 'Program configured to start with Windows',
                'startup_disabled': 'Program removed from automatic startup',
                'startup_error': 'Error configuring automatic startup',
                
                # User Guide
                'how_to_use_menu': 'How to Use',
                'user_guide_title': 'User Guide - How to use Avilon',
                'guide_tab_games': 'Games',
                'guide_tab_maps': 'Maps', 
                'guide_tab_features': 'Features',
                'guide_tab_tips': 'Tips',
                
                # Games tab
                'guide_games_title': '🎮 Game Management',
                'guide_games_add_title': '📝 How to add a game:',
                'guide_games_add_content': '''1. Go to "File" → "Add Game" menu
2. Fill in the game name
3. Select an image (optional):
   • Supported formats: PNG, JPG, JPEG, BMP, GIF
   • Recommended: 250x280 pixels
4. Configure the map (see "Maps" tab)
5. Click "Save"''',
                'guide_games_manage_title': '⚙️ Managing existing games:',
                'guide_games_manage_content': '''• Click on ⭐ to mark/unmark as favorite
• Use "View map" to open the game map
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
• Starts with Windows if enabled
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
                'guide_shortcuts_workflow_content': '''1. Ctrl + N to add games quickly
2. Ctrl + F to search without using mouse
3. Escape to clear and start over
4. Ctrl + Shift + F to see only favorites
5. F5 to refresh when adding files manually''',
                
                # Guide subtitle
                'guide_subtitle': 'Everything you need to know about using Avilon'
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
                'add_game_button': '+ Ajouter un jeu',
                'library': 'BIBLIOTHÈQUE',
                'games_count': 'jeux',
                'game_singular': 'jeu',
                'no_games': 'Aucun jeu dans votre bibliothèque.\nAllez dans "Fichier" → "Ajouter un jeu" pour commencer.',
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
                'config_subtitle': 'Personnalisez votre expérience de jeu',
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
                'add_to_favorites': 'Ajouter aux favoris',
                'remove_from_favorites': 'Retirer des favoris',
                
                # Startup
                'startup_label': 'Démarrer avec Windows:',
                'startup_enabled': 'Programme configuré pour démarrer avec Windows',
                'startup_disabled': 'Programme retiré du démarrage automatique',
                'startup_error': 'Erreur lors de la configuration du démarrage automatique',
                
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
                'guide_shortcuts_workflow_content': '''1. Ctrl + N pour ajouter des jeux rapidement
2. Ctrl + F pour rechercher sans utiliser la souris
3. Échap pour effacer et recommencer
4. Ctrl + Shift + F pour voir seulement les favoris
5. F5 pour actualiser lors d'ajouts manuels de fichiers'''
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
                'add_game_button': '+ Spiel hinzufügen',
                'library': 'BIBLIOTHEK',
                'games_count': 'Spiele',
                'game_singular': 'Spiel',
                'no_games': 'Keine Spiele in Ihrer Bibliothek.\nGehen Sie zu "Datei" → "Spiel hinzufügen", um zu beginnen.',
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
                'config_subtitle': 'Passen Sie Ihr Spielerlebnis an',
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
                'add_to_favorites': 'Zu Favoriten hinzufügen',
                'remove_from_favorites': 'Aus Favoriten entfernen',
                
                # Startup
                'startup_label': 'Mit Windows starten:',
                'startup_enabled': 'Programm zum Start mit Windows konfiguriert',
                'startup_disabled': 'Programm aus automatischem Start entfernt',
                'startup_error': 'Fehler beim Konfigurieren des automatischen Starts',
                
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
                'guide_shortcuts_workflow_content': '''1. Strg + N zum schnellen Hinzufügen von Spielen
2. Strg + F zum Suchen ohne Maus
3. Escape zum Löschen und Neubeginn
4. Strg + Shift + F um nur Favoriten zu sehen
5. F5 zum Aktualisieren bei manuellen Dateiänderungen'''
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
                'add_game_button': '+ Aggiungi gioco',
                'library': 'LIBRERIA',
                'games_count': 'giochi',
                'game_singular': 'gioco',
                'no_games': 'Nessun gioco nella tua libreria.\nVai su "File" → "Aggiungi gioco" per iniziare.',
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
                'config_subtitle': 'Personalizza la tua esperienza di gioco',
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
                'add_to_favorites': 'Aggiungi ai preferiti',
                'remove_from_favorites': 'Rimuovi dai preferiti',
                
                # Startup
                'startup_label': 'Avvia con Windows:',
                'startup_enabled': 'Programma configurato per avviarsi con Windows',
                'startup_disabled': 'Programma rimosso dall\'avvio automatico',
                'startup_error': 'Errore durante la configurazione dell\'avvio automatico'
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
                'add_game_button': '+ Adicionar jogo',
                'library': 'BIBLIOTECA',
                'games_count': 'jogos',
                'game_singular': 'jogo',
                'no_games': 'Nenhum jogo na sua biblioteca.\nVá para "Arquivo" → "Adicionar jogo" para começar.',
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
                'config_subtitle': 'Personalize sua experiência de jogo',
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
                'add_to_favorites': 'Adicionar aos favoritos',
                'remove_from_favorites': 'Remover dos favoritos',
                
                # Startup
                'startup_label': 'Iniciar com Windows:',
                'startup_enabled': 'Programa configurado para iniciar com Windows',
                'startup_disabled': 'Programa removido do início automático',
                'startup_error': 'Erro ao configurar o início automático'
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
                'add_game_button': '+ Spel toevoegen',
                'library': 'BIBLIOTHEEK',
                'games_count': 'spellen',
                'game_singular': 'spel',
                'no_games': 'Geen spellen in je bibliotheek.\nGa naar "Bestand" → "Spel toevoegen" om te beginnen.',
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
                'config_subtitle': 'Pas je spelervaring aan',
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
                'add_to_favorites': 'Toevoegen aan favorieten',
                'remove_from_favorites': 'Verwijderen uit favorieten',
                
                # Startup
                'startup_label': 'Starten met Windows:',
                'startup_enabled': 'Programma ingesteld om te starten met Windows',
                'startup_disabled': 'Programma verwijderd van automatisch opstarten',
                'startup_error': 'Fout bij het instellen van automatisch opstarten'
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
                'add_game_button': '+ Добавить игру',
                'library': 'БИБЛИОТЕКА',
                'games_count': 'игр',
                'game_singular': 'игра',
                'no_games': 'Нет игр в вашей библиотеке.\nПерейдите в "Файл" → "Добавить игру", чтобы начать.',
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
                'config_subtitle': 'Настройте свой игровой опыт',
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
                'add_to_favorites': 'Добавить в избранное',
                'remove_from_favorites': 'Удалить из избранного',
                
                # Startup
                'startup_label': 'Запуск с Windows:',
                'startup_enabled': 'Программа настроена для запуска с Windows',
                'startup_disabled': 'Программа удалена из автозапуска',
                'startup_error': 'Ошибка настройки автозапуска'
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
                'add_game_button': '+ ゲームを追加',
                'library': 'ライブラリ',
                'games_count': 'ゲーム',
                'game_singular': 'ゲーム',
                'no_games': 'ライブラリにゲームがありません。\n「ファイル」→「ゲームを追加」から始めてください。',
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
                'config_subtitle': 'ゲーム体験をカスタマイズ',
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
                'add_to_favorites': 'お気に入りに追加',
                'remove_from_favorites': 'お気に入りから削除',
                
                # Startup
                'startup_label': 'Windowsと一緒に起動:',
                'startup_enabled': 'プログラムがWindowsと一緒に起動するよう設定されました',
                'startup_disabled': 'プログラムが自動起動から削除されました',
                'startup_error': '自動起動の設定でエラーが発生しました'
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
                'add_game_button': '+ 添加游戏',
                'library': '游戏库',
                'games_count': '游戏',
                'game_singular': '游戏',
                'no_games': '您的游戏库中没有游戏。\n请前往"文件"→"添加游戏"开始。',
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
                'config_subtitle': '自定义您的游戏体验',
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
                'add_to_favorites': '添加到收藏夹',
                'remove_from_favorites': '从收藏夹中删除',
                
                # Startup
                'startup_label': '随Windows启动:',
                'startup_enabled': '程序已配置为随Windows启动',
                'startup_disabled': '程序已从自动启动中删除',
                'startup_error': '配置自动启动时出错'
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
                'startup': getattr(self, 'startup_enabled', False)
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
    
    def set_startup_registry(self, enable):
        """Configurar inicio automático en el registro de Windows"""
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "Avilon"
        
        try:
            # Obtener la ruta del ejecutable actual
            if getattr(sys, 'frozen', False):
                # Si es un .exe compilado, usar ruta absoluta y comillas por seguridad
                app_path = f'"{os.path.abspath(sys.executable)}"'
            else:
                # Si es un script de Python
                app_path = f'python "{os.path.abspath(__file__)}"'
            
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
        """Verificar si el programa está configurado para iniciar con Windows"""
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "Avilon"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            try:
                value, _ = winreg.QueryValueEx(key, app_name)
                print(f"Entrada encontrada en registro: {value}")
                # Verificar que la entrada del registro apunte a un archivo que existe
                # Remover comillas si las hay para verificar la existencia del archivo
                exe_path = value.strip('"')
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
                'bg_dark': '#2f3136',
                'bg_light': '#36393f',
                'bg_medium': '#40444b',
                'sidebar': '#2f3136',
                'accent': '#7289da',
                'accent_hover': '#677bc4',
                'text': '#ffffff',
                'text_primary': '#ffffff',
                'text_secondary': '#99aab5',
                'text_muted': '#99aab5',
                'success': '#43b581',
                'danger': '#f04747',
                'warning': '#ff9500'
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
                'text': '#ffffff',
                'text_primary': '#ffffff',
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
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.get_text('file_menu'), menu=file_menu)
        file_menu.add_command(label=self.get_text('add_game'), command=self.show_add_game_dialog, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label=self.get_text('config_menu'), command=self.show_config_dialog, accelerator="Ctrl+Shift+P")
        file_menu.add_separator()
        file_menu.add_command(label=self.get_text('exit_menu'), command=self.on_closing, accelerator="Ctrl+Q")
        
        # Menú Ver
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.get_text('view_menu'), menu=view_menu)
        view_menu.add_command(label=self.get_text('search_menu'), command=self.focus_search_bar, accelerator="Ctrl+F")
        view_menu.add_command(label=self.get_text('toggle_favorites_menu'), command=self.toggle_favorites_filter, accelerator="Ctrl+Shift+F")
        view_menu.add_separator()
        view_menu.add_command(label=self.get_text('refresh_list_menu'), command=self.refresh_games_display, accelerator="F5")
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.get_text('help_menu'), menu=help_menu)
        help_menu.add_command(label=self.get_text('how_to_use_menu'), command=self.show_user_guide_dialog, accelerator="F1")
        help_menu.add_command(label=self.get_text('about_menu'), command=self.show_about_dialog)
    
    def show_about_dialog(self):
        """Mostrar ventana Acerca de"""
        about_window = tk.Toplevel(self.root)
        about_window.withdraw()  # Ocultar la ventana inicialmente
        about_window.title(self.get_text('about_title'))
        about_window.geometry("400x350")
        about_window.configure(bg=self.colors['bg_dark'])
        about_window.resizable(False, False)
        self.apply_window_icon(about_window)
        
        # Centrar la ventana
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Configurar icono
        try:
            about_window.iconbitmap("logo.ico")
        except:
            pass
        
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
                                 text="Versión 1.5.2",
                                 style='Dark.TLabel',
                                 font=('Arial', 9, 'italic'))
        version_label.pack(pady=(0, 15))
        
        # Logo
        try:
            # Cargar y mostrar el logo
            from PIL import Image, ImageTk
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
        
        # Centrar la ventana en la pantalla
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() - about_window.winfo_width()) // 2
        y = (about_window.winfo_screenheight() - about_window.winfo_height()) // 2
        about_window.geometry(f"+{x}+{y}")
        
        # Mostrar la ventana una vez que está completamente configurada
        about_window.deiconify()
    
    def show_user_guide_dialog(self):
        """Mostrar ventana de Guía de Usuario con diseño ultra moderno"""
        guide_window = tk.Toplevel(self.root)
        guide_window.withdraw()  # Ocultar la ventana inicialmente
        guide_window.title(self.get_text('user_guide_title'))
        guide_window.geometry("1100x800")
        guide_window.configure(bg=self.colors['bg_dark'])
        guide_window.resizable(False, False)  # Ventana no redimensionable
        self.apply_window_icon(guide_window)
        
        # Centrar la ventana
        guide_window.transient(self.root)
        guide_window.grab_set()
        
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
        x = (guide_window.winfo_screenwidth() - guide_window.winfo_width()) // 2
        y = (guide_window.winfo_screenheight() - guide_window.winfo_height()) // 2
        guide_window.geometry(f"+{x}+{y}")
        
        # Mostrar la ventana con efecto fade-in
        guide_window.deiconify()
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
    
    def create_modern_card(self, parent, icon, title, content, icon_bg=None, action_button=None):
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
        icon_canvas.create_text(30, 30, text=icon, fill='white', font=('Segoe UI Emoji', 20, 'bold'))
        
        # Área de texto
        text_frame = tk.Frame(header_frame, bg=self.colors['bg_medium'])
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Título principal
        title_label = tk.Label(text_frame, text=title,
                              bg=self.colors['bg_medium'],
                              fg=self.colors['text'],
                              font=('Segoe UI', 16, 'bold'),
                              anchor='w', justify='left')
        title_label.pack(fill=tk.X, pady=(5, 0))
        
        # Contenido principal con texto ajustable
        content_frame = tk.Frame(inner_frame, bg=self.colors['bg_medium'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Usar Text widget en lugar de Label para mejor control del contenido
        content_text = tk.Text(content_frame,
                              wrap=tk.WORD,
                              bg=self.colors['bg_light'],
                              fg=self.colors['text_secondary'],
                              font=('Segoe UI', 11),
                              relief='flat',
                              padx=15,
                              pady=12,
                              height=4,  # Altura en líneas
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
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header de introducción moderno
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=(30, 40), padx=30)
        
        intro_title = tk.Label(intro_frame,
                              text="🎮 " + self.get_text('guide_games_title'),
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
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratón - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
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
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header de introducción
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=(30, 40), padx=30)
        
        intro_title = tk.Label(intro_frame,
                              text="🗺️ " + self.get_text('guide_maps_title'),
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
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratón - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
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
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header de introducción
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=(30, 40), padx=30)
        
        intro_title = tk.Label(intro_frame,
                              text="✨ " + self.get_text('guide_features_title'),
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
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratón - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
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
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header de introducción
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=(30, 40), padx=30)
        
        intro_title = tk.Label(intro_frame,
                              text="💡 " + self.get_text('guide_tips_title'),
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
        )
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratón - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
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
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
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
        )
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratón
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Sistema de scroll mejorado
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el árbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # También bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)

    def show_config_dialog(self):
        """Mostrar ventana de configuración con diseño profesional"""
        config_window = tk.Toplevel(self.root)
        config_window.withdraw()  # Ocultar la ventana inicialmente
        config_window.title(self.get_text('config_title'))
        config_window.geometry("550x800")
        config_window.configure(bg=self.colors['bg_dark'])
        config_window.resizable(True, True)  # Permitir redimensionar para mayor flexibilidad
        self.apply_window_icon(config_window)
        
        # Centrar la ventana
        config_window.transient(self.root)
        config_window.grab_set()
        
        # Configurar icono
        try:
            config_window.iconbitmap("logo.ico")
        except:
            pass
        
        # Frame principal con mejor padding
        main_frame = tk.Frame(config_window, bg=self.colors['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Header con título y subtítulo
        header_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Título principal
        title_label = tk.Label(header_frame, 
                              text=self.get_text('config_title'), 
                              bg=self.colors['bg_dark'],
                              fg=self.colors['text_primary'],
                              font=('Segoe UI', 18, 'bold'))
        title_label.pack(anchor='center')
        
        # Subtítulo
        subtitle_label = tk.Label(header_frame, 
                                 text=self.get_text('config_subtitle'), 
                                 bg=self.colors['bg_dark'],
                                 fg=self.colors['text_secondary'],
                                 font=('Segoe UI', 10))
        subtitle_label.pack(anchor='center', pady=(5, 0))
        
        # Separador
        separator1 = tk.Frame(main_frame, bg=self.colors['accent'], height=2)
        separator1.pack(fill=tk.X, pady=(0, 25))
        
        # === SECCIÓN DE IDIOMA ===
        self.create_config_section(main_frame, "🌐", self.get_text('language_label'), 
                                  "Selecciona el idioma de la interfaz")
        
        language_card = self.create_config_card(main_frame)
        
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
                                     font=('Segoe UI', 10))
        
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
        language_combo.pack(pady=10)
        
        # === SECCIÓN DE TEMA ===
        self.create_config_section(main_frame, "🎨", self.get_text('theme_label'), 
                                  "Elige el tema visual de la aplicación")
        
        theme_card = self.create_config_card(main_frame)
        
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
                                  font=('Segoe UI', 10))
        
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
        theme_combo.pack(pady=10)
        
        # === SECCIÓN DE INICIO AUTOMÁTICO ===
        self.create_config_section(main_frame, "🚀", self.get_text('startup_label'), 
                                  "Inicia Avilon automáticamente con Windows")
        
        startup_card = self.create_config_card(main_frame)
        
        # Variable para el checkbox del inicio automático
        actual_startup_status = self.check_startup_status()
        self.temp_startup = tk.BooleanVar(value=actual_startup_status)
        
        # CHECKBOX con diseño integrado
        startup_checkbox = tk.Checkbutton(startup_card,
                                         text=" ✓ Iniciar automáticamente con Windows",
                                         variable=self.temp_startup,
                                         bg=self.colors['bg_medium'],
                                         fg=self.colors['text_primary'],
                                         selectcolor=self.colors['accent'],
                                         activebackground=self.colors['bg_medium'],
                                         activeforeground=self.colors['text_primary'],
                                         font=('Segoe UI', 11, 'bold'),
                                         relief='flat',
                                         borderwidth=0,
                                         padx=15,
                                         pady=10,
                                         cursor='hand2',
                                         anchor='w')
        startup_checkbox.pack(fill=tk.X, pady=(10, 15))
        
        # === ÁREA DE BOTONES REDISEÑADA ===
        
        # Frame principal para botones con el mismo fondo que la ventana
        button_area = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        button_area.pack(fill=tk.X, pady=(25, 30))
        
        # Frame interno para botones
        button_container = tk.Frame(button_area, bg=self.colors['bg_dark'])
        button_container.pack(pady=15, padx=20)
        
        # BOTÓN CANCELAR - más pequeño
        cancel_btn = tk.Button(button_container,
                              text=self.get_text('cancel'),
                              bg='#dc3545',
                              fg='white',
                              font=('Segoe UI', 11, 'bold'),
                              relief='flat',
                              borderwidth=0,
                              padx=20,
                              pady=8,
                              cursor='hand2',
                              command=config_window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # BOTÓN GUARDAR CAMBIOS - más pequeño
        save_btn = tk.Button(button_container,
                            text=self.get_text('save_changes'),
                            bg=self.colors['accent'],
                            fg='white',
                            font=('Segoe UI', 11, 'bold'),
                            relief='flat',
                            borderwidth=0,
                            padx=25,
                            pady=8,
                            cursor='hand2',
                            command=lambda: self.apply_config_changes(config_window, language_combo, theme_combo, 
                                                                   lang_display_values, theme_display_values,
                                                                   title_label, subtitle_label, 
                                                            save_btn, cancel_btn))
        save_btn.pack(side=tk.RIGHT)
               
        # Efectos hover para los botones rediseñados
        def on_save_enter(event):
            save_btn.configure(bg=self.colors['accent_hover'] if 'accent_hover' in self.colors else '#0056b3')
        
        def on_save_leave(event):
            save_btn.configure(bg=self.colors['accent'])
        
        def on_cancel_enter(event):
            cancel_btn.configure(bg='#c82333')
        
        def on_cancel_leave(event):
            cancel_btn.configure(bg='#dc3545')
        
        # Efectos de click
        def on_save_click(event):
            save_btn.configure(relief='sunken')
            save_btn.after(100, lambda: save_btn.configure(relief='flat'))
        
        def on_cancel_click(event):
            cancel_btn.configure(relief='sunken')
            cancel_btn.after(100, lambda: cancel_btn.configure(relief='flat'))
        
        # Binding de eventos
        save_btn.bind('<Enter>', on_save_enter)
        save_btn.bind('<Leave>', on_save_leave)
        save_btn.bind('<Button-1>', on_save_click)
        
        cancel_btn.bind('<Enter>', on_cancel_enter)
        cancel_btn.bind('<Leave>', on_cancel_leave)
        cancel_btn.bind('<Button-1>', on_cancel_click)
        
        # Centrar la ventana en la pantalla
        config_window.update_idletasks()
        x = (config_window.winfo_screenwidth() - config_window.winfo_width()) // 2
        y = (config_window.winfo_screenheight() - config_window.winfo_height()) // 2
        config_window.geometry(f"+{x}+{y}")
        
        # Mostrar la ventana una vez que está completamente configurada
        config_window.deiconify()
    
    def create_config_section(self, parent, icon, title, description):
        """Crear una sección de configuración con título e icono"""
        section_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Frame para el título con icono
        title_frame = tk.Frame(section_frame, bg=self.colors['bg_dark'])
        title_frame.pack(fill=tk.X)
        
        # Icono
        icon_label = tk.Label(title_frame,
                             text=icon,
                             bg=self.colors['bg_dark'],
                             fg=self.colors['accent'],
                             font=('Segoe UI', 16))
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Contenedor para título y descripción
        text_frame = tk.Frame(title_frame, bg=self.colors['bg_dark'])
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Título
        title_label = tk.Label(text_frame,
                              text=title,
                              bg=self.colors['bg_dark'],
                              fg=self.colors['text_primary'],
                              font=('Segoe UI', 12, 'bold'))
        title_label.pack(anchor='w')
        
        # Descripción
        desc_label = tk.Label(text_frame,
                             text=description,
                             bg=self.colors['bg_dark'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 9))
        desc_label.pack(anchor='w')
        
        return section_frame
    
    def create_config_card(self, parent):
        """Crear una tarjeta de configuración estilizada"""
        card_frame = tk.Frame(parent, 
                             bg=self.colors['bg_medium'], 
                             relief='flat',
                             borderwidth=1)
        card_frame.pack(fill=tk.X, pady=(0, 20), ipady=8, ipadx=12)
        
        # Efecto de hover sutil para la card
        def on_card_enter(event):
            card_frame.configure(bg=self.colors['bg_light'])
        
        def on_card_leave(event):
            card_frame.configure(bg=self.colors['bg_medium'])
        
        card_frame.bind('<Enter>', on_card_enter)
        card_frame.bind('<Leave>', on_card_leave)
        
        # Hacer que todos los widgets hijos respondan al hover
        def bind_hover_to_children(widget):
            for child in widget.winfo_children():
                child.bind('<Enter>', on_card_enter)
                child.bind('<Leave>', on_card_leave)
                bind_hover_to_children(child)
        
        # Programar el binding después de que se agreguen los widgets hijos
        card_frame.after(1, lambda: bind_hover_to_children(card_frame))
        
        return card_frame
    
    def apply_config_changes(self, config_window, language_combo=None, theme_combo=None, 
                           lang_display_values=None, theme_display_values=None,
                           title_label=None, subtitle_label=None, save_btn=None, cancel_btn=None):
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
        
        if changes_made:
            self.save_config()
            
            # Si cambió el idioma, actualizar la ventana de configuración primero
            if language_changed and title_label and subtitle_label and save_btn and cancel_btn:
                # Actualizar título de la ventana
                config_window.title(self.get_text('config_title'))
                
                # Actualizar etiquetas principales
                title_label.configure(text=self.get_text('config_title'))
                subtitle_label.configure(text=self.get_text('config_subtitle'))
                
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
        self.root.title(self.get_text('window_title'))
        
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
        # Frame principal
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Área de contenido principal (sin sidebar)
        self.create_content_area(main_frame)
    

    
    def create_content_area(self, parent):
        """Crear área de contenido principal"""
        content_frame = ttk.Frame(parent, style='Dark.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(content_frame, style='Dark.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Crear frame superior para organizar elementos horizontalmente
        top_frame = ttk.Frame(header_frame, style='Dark.TFrame')
        top_frame.pack(fill=tk.X)
        
        # Botones de filtro en la esquina superior izquierda
        self.create_filter_buttons(top_frame)
        
        # Barra de búsqueda en la esquina superior derecha
        self.create_search_bar(top_frame)
        
        # Título AVILON centrado en su propia línea
        title_frame = ttk.Frame(header_frame, style='Dark.TFrame')
        title_frame.pack(fill=tk.X, pady=(5, 0))
        
        title_label = ttk.Label(title_frame, text="AVILON",
                               style='Dark.TLabel',
                               font=('Segoe UI', 24, 'bold'))
        title_label.pack(anchor=tk.CENTER, pady=(0, 5))
        
        # Frame scrollable para juegos
        self.create_scrollable_games_area(content_frame)
    
    def create_filter_buttons(self, parent):
        """Crear botones de filtro en la esquina superior izquierda"""
        # Frame para los botones de filtro
        filter_frame = ttk.Frame(parent, style='Dark.TFrame')
        filter_frame.pack(side=tk.LEFT, anchor=tk.NW, padx=(10, 0), pady=(5, 0))
        
        # Contar juegos para los contadores
        total_count = len(self.games)
        favorites_count = len([game for game in self.games if game.get('favorite', False)])
        
        # Botón "Todos" con contador
        all_text = f"{self.get_text('all_games')} ({total_count})"
        self.all_button = tk.Button(filter_frame,
                                   text=all_text,
                                   font=('Segoe UI', 10),
                                   bg=self.colors['accent'] if self.favorites_filter == "all" else self.colors['bg_light'],
                                   fg='white' if self.favorites_filter == "all" else self.colors['text'],
                                   activebackground=self.colors['accent'],
                                   activeforeground='white',
                                   relief='flat',
                                   bd=0,
                                   padx=15,
                                   pady=8,
                                   cursor='hand2',
                                   command=lambda: self.set_favorites_filter("all"))
        self.all_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón "Favoritos" con contador  
        favorites_text = f"{self.get_text('favorites')} ({favorites_count})"
        self.favorites_button = tk.Button(filter_frame,
                                         text=favorites_text,
                                         font=('Segoe UI', 10),
                                         bg=self.colors['accent'] if self.favorites_filter == "favorites" else self.colors['bg_light'],
                                         fg='white' if self.favorites_filter == "favorites" else self.colors['text'],
                                         activebackground=self.colors['accent'],
                                         activeforeground='white',
                                         relief='flat',
                                         bd=0,
                                         padx=15,
                                         pady=8,
                                         cursor='hand2',
                                         command=lambda: self.set_favorites_filter("favorites"))
        self.favorites_button.pack(side=tk.LEFT)
    
    def create_search_bar(self, parent):
        """Crear barra de búsqueda mejorada con efectos y transiciones"""
        # Variable para el texto de búsqueda
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        # Container principal alineado a la derecha en el top_frame
        container = ttk.Frame(parent, style='Dark.TFrame')
        container.pack(side=tk.RIGHT, padx=(0, 10), pady=(5, 0))  # Alineado a la derecha del top_frame
        
        # Frame de la barra de búsqueda con efectos visuales usando colores del tema
        self.search_bar_frame = tk.Frame(container, 
                                        bg=self.colors['bg_light'],
                                        relief='flat',
                                        bd=1,
                                        highlightthickness=1,
                                        highlightcolor=self.colors['accent'],
                                        highlightbackground=self.colors['bg_dark'])
        self.search_bar_frame.pack(pady=2)
        
        # Frame interno para los elementos
        inner_frame = tk.Frame(self.search_bar_frame, bg=self.colors['bg_light'])
        inner_frame.pack(padx=8, pady=5)
        
        # Ícono de búsqueda animado
        self.search_icon = tk.Label(inner_frame, 
                                   text="🔍",
                                   bg=self.colors['bg_light'],
                                   fg=self.colors['text_muted'],
                                   font=('Segoe UI', 11))
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
            entry_bg = '#484c52'  # Fondo más claro que el tema para mejor contraste
            entry_fg = '#ffffff'  # Texto blanco
            insert_color = '#ffffff'  # Cursor blanco
            select_bg = '#7289da'
            select_fg = '#ffffff'
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
        else:
            # Fallback para cualquier tema nuevo
            entry_bg = '#ffffff'
            entry_fg = '#333333'
            insert_color = '#333333'
            select_bg = '#0078d4'
            select_fg = '#ffffff'
        
        self.search_entry = tk.Entry(inner_frame,
                                    textvariable=self.search_var,
                                    font=('Segoe UI', 10),
                                    width=25,
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
                                     font=('Segoe UI', 10, 'bold'),
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
    
    def set_favorites_filter(self, filter_type):
        """Establecer filtro de favoritos y actualizar interfaz"""
        self.favorites_filter = filter_type
        
        # Actualizar colores de botones
        if hasattr(self, 'all_button') and self.all_button.winfo_exists():
            if filter_type == "all":
                self.all_button.config(bg=self.colors['accent'], fg='white')
                self.favorites_button.config(bg=self.colors['bg_light'], fg=self.colors['text'])
            else:
                self.all_button.config(bg=self.colors['bg_light'], fg=self.colors['text'])
                self.favorites_button.config(bg=self.colors['accent'], fg='white')
        
        # Actualizar contadores
        self.update_filter_button_counters()
        
        # Actualizar visualización de juegos
        self.refresh_games_display()
    
    def update_search_bar_colors(self):
        """Actualizar colores de la barra de búsqueda según el tema actual"""
        if hasattr(self, 'search_entry') and self.search_entry.winfo_exists():
            # Configurar colores específicos para cada tema con mejor contraste
            if self.current_theme == 'light':
                entry_bg = '#ffffff'
                entry_fg = '#333333'
                insert_color = '#333333'
                select_bg = '#0078d4'
                select_fg = '#ffffff'
            elif self.current_theme == 'slate':
                entry_bg = '#484c52'  # Fondo más claro que el tema para mejor contraste
                entry_fg = '#ffffff'  # Texto blanco
                insert_color = '#ffffff'  # Cursor blanco
                select_bg = '#7289da'
                select_fg = '#ffffff'
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
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind mousewheel para scroll sin barra visible
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
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
    
    def setup_hover_effects_enhanced(self, card_frame, name_label, header_frame, buttons_frame):
        """Configurar efectos hover sutiles y profesionales para las tarjetas"""
        # Colores hover más sutiles y elegantes
        if self.current_theme == 'light':
            hover_border_color = '#e3e6ea'
            name_hover_color = self.colors['accent']
        else:
            hover_border_color = '#4a5058'
            name_hover_color = '#7dd3fc'  # Azul claro sutil
        
        # Estado original
        original_bg = self.colors['bg_light']
        original_name_color = self.colors['text_primary']
        
        def on_enter(event):
            """Efecto hover sutil y profesional"""
            # Solo cambiar el borde de la tarjeta y el color del nombre
            card_frame.configure(style='GameHover.TFrame')
            
            # Cambiar color del nombre del juego para indicar que es clickeable
            name_label.configure(fg=name_hover_color)
            
            # Efecto sutil en la sombra (más discreto)
            try:
                parent = card_frame.master
                if hasattr(parent, 'master'):
                    shadow_frame = None
                    for child in parent.winfo_children():
                        if isinstance(child, tk.Frame) and child != card_frame:
                            shadow_frame = child
                            break
                    if shadow_frame:
                        # Solo cambiar el color, mantener altura
                        shadow_frame.configure(bg=hover_border_color)
            except:
                pass
            
        def on_leave(event):
            """Restaurar estado original"""
            # Restaurar borde original
            card_frame.configure(style='Game.TFrame')
            
            # Restaurar color original del nombre
            name_label.configure(fg=original_name_color)
            
            # Restaurar sombra original
            try:
                parent = card_frame.master
                if hasattr(parent, 'master'):
                    shadow_frame = None
                    for child in parent.winfo_children():
                        if isinstance(child, tk.Frame) and child != card_frame:
                            shadow_frame = child
                            break
                    if shadow_frame:
                        shadow_frame.configure(bg=self.card_shadow_color)
            except:
                pass
        
        # Aplicar eventos hover solo a elementos clickeables
        name_label.bind('<Enter>', on_enter)
        name_label.bind('<Leave>', on_leave)
        
        # También aplicar a la imagen si existe
        def bind_to_image_only(widget):
            """Aplicar efectos hover solo a la imagen del juego"""
            try:
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label) and hasattr(child, 'image'):
                        child.bind('<Enter>', on_enter)
                        child.bind('<Leave>', on_leave)
                    elif hasattr(child, 'winfo_children'):
                        bind_to_image_only(child)
            except:
                pass
                
        bind_to_image_only(card_frame)
    
    def show_add_game_dialog(self):
        """Mostrar diálogo para añadir juego"""
        dialog = tk.Toplevel(self.root)
        dialog.title(self.get_text('add_game_title'))
        dialog.geometry("600x550")  # Más grande para mejor visualización
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)  # Evitar redimensionado
        self.apply_window_icon(dialog)
        
        # Centrar diálogo
        dialog.geometry("+{}+{}".format(
            self.root.winfo_rootx() + 300,
            self.root.winfo_rooty() + 125
        ))
        
        # Variables
        self.game_name_var = tk.StringVar()
        self.game_image_path = tk.StringVar()
        self.map_type_var = tk.StringVar(value="image")
        self.map_content_var = tk.StringVar()
        
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
        
        # Imagen del juego
        image_label = ttk.Label(form_frame, text=self.get_text('game_image'),
                               style='Dark.TLabel')
        image_label.pack(anchor=tk.W, pady=(0, 5))
        
        image_frame = ttk.Frame(form_frame, style='Dark.TFrame')
        image_frame.pack(fill=tk.X, pady=(0, 15))
        
        image_entry = tk.Entry(image_frame, textvariable=self.game_image_path,
                              bg=self.colors['bg_light'], fg=self.colors['text'],
                              font=('Segoe UI', 10), relief='flat',
                              insertbackground=self.colors['text'])
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
        
        image_radio = tk.Radiobutton(map_type_frame, text=self.get_text('map_type_image'),
                                    variable=self.map_type_var, value="image",
                                    bg=self.colors['bg_dark'], fg=self.colors['text'],
                                    selectcolor=self.colors['bg_light'],
                                    activebackground=self.colors['bg_dark'])
        image_radio.pack(side=tk.LEFT)
        
        iframe_radio = tk.Radiobutton(map_type_frame, text=self.get_text('map_type_web'),
                                     variable=self.map_type_var, value="iframe",
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
                                    insertbackground=self.colors['text'])
        map_content_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        browse_map_button = ttk.Button(map_content_frame, text=self.get_text('browse_map'),
                                      command=self.browse_map_content)
        browse_map_button.pack(side=tk.RIGHT, padx=(10, 0))
        
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
            import time
            timestamp = str(int(time.time()))
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
            return source_path  # Retornar ruta original si falla la copia
    
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
                if image_path and image_path.startswith(self.images_dir):
                    used_images.add(os.path.basename(image_path))
                
                # Agregar imagen del mapa si es de tipo imagen y está en el directorio local
                if (game.get('map_type') == 'image' and map_content and 
                    map_content.startswith(self.images_dir)):
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
            self.save_games()
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
            'favorite': False  # Los juegos nuevos no son favoritos por defecto
        }
        
        # Añadir a la lista
        self.games.append(game)
        
        # Guardar en archivo
        self.save_games()
        
        # Actualizar interfaz
        self.refresh_games_display()
        
        # Cerrar diálogo
        dialog.destroy()
        
        messagebox.showinfo(self.get_text('success'), self.get_text('game_saved'))
    
    def refresh_games_display(self):
        """Actualizar la visualización de juegos"""
        # Actualizar contadores en botones de filtro
        self.update_filter_button_counters()
        # Limpiar frame scrollable
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Obtener juegos filtrados
        filtered_games = self.get_filtered_games()
        
        if not filtered_games:
            # Mostrar mensaje si no hay juegos (ya sea porque no hay juegos o por el filtro)
            if not self.games:
                message = self.get_text('no_games') if hasattr(self, 'get_text') else "No hay juegos agregados"
            else:
                message = "No se encontraron juegos que coincidan con la búsqueda"
            
            no_games_label = ttk.Label(self.scrollable_frame,
                                      text=message,
                                      style='Dark.TLabel',
                                      font=('Segoe UI', 14),
                                      justify='center')
            no_games_label.pack(pady=50, expand=True, anchor='center')
            return
        
        # Mostrar juegos en grid (estilo Steam) - RESPONSIVE
        row = 0
        col = 0
        
        # Calcular columnas dinámicamente basado en el ancho de la ventana
        window_width = self.root.winfo_width()
        sidebar_width = 200
        available_width = window_width - sidebar_width - 50  # Resta sidebar y padding
        card_width = 250 + 20  # Ancho de tarjeta + padding
        max_cols = max(1, available_width // card_width)  # Al menos 1 columna
        
        # Configurar todas las columnas para que sean responsivas
        for c in range(max_cols):
            self.scrollable_frame.grid_columnconfigure(c, weight=1)
        
        for i, game in enumerate(filtered_games):
            self.create_game_card(self.scrollable_frame, game, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Configurar filas para que se expandan correctamente
        for r in range(row + 1):
            self.scrollable_frame.grid_rowconfigure(r, weight=1)
    
    def get_filtered_games(self):
        """Obtener juegos filtrados con prioridad para favoritos"""
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
    
    def create_game_card(self, parent, game, row, col):
        """Crear tarjeta de juego con diseño profesional y moderno"""
        # Frame principal con efecto de elevación
        main_container = tk.Frame(parent, bg=self.colors['bg_dark'])
        main_container.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
        # Frame de sombra para efecto de profundidad
        shadow_frame = tk.Frame(main_container, 
                               bg=self.card_shadow_color,
                               height=2)
        shadow_frame.pack(side='bottom', fill='x')
        
        # Frame principal de la tarjeta con mejor diseño
        card_frame = ttk.Frame(main_container, style='Game.TFrame')
        card_frame.pack(fill='both', expand=True)
        
        # Header de la tarjeta con título y favorito
        header_frame = tk.Frame(card_frame, bg=self.colors['bg_light'], height=45)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Nombre del juego con mejor tipografía
        name_label = tk.Label(header_frame, 
                             text=game['name'][:25] + "..." if len(game['name']) > 25 else game['name'],
                             bg=self.colors['bg_light'],
                             fg=self.colors['text_primary'],
                             font=('Segoe UI', 11, 'bold'),
                             cursor='hand2',
                             anchor='w')
        name_label.pack(side='left', fill='both', expand=True, padx=(15, 5), pady=10)
        name_label.bind("<Button-1>", lambda e, g=game: self.open_game_map(g))
        
        # Estrella de favoritos modernizada
        is_favorite = game.get('favorite', False)
        star_color = '#FFD700' if is_favorite else '#B0B0B0'
        star_text = '⭐' if is_favorite else '☆'
        
        favorite_star = tk.Label(header_frame,
                               text=star_text,
                               font=('Segoe UI', 16, 'bold'),
                               fg=star_color,
                               bg=self.colors['bg_light'],
                               cursor='hand2',
                               width=3)
        favorite_star.pack(side='right', padx=(5, 15), pady=10)
        
        # Efectos hover mejorados para la estrella
        def on_star_enter(event):
            if game.get('favorite', False):
                favorite_star.config(fg='#FF6B35', text='⭐')  # Naranja para quitar
            else:
                favorite_star.config(fg='#FFD700', text='⭐')  # Dorado para agregar
        
        def on_star_leave(event):
            current_favorite = game.get('favorite', False)
            star_color = '#FFD700' if current_favorite else '#B0B0B0'
            star_text = '⭐' if current_favorite else '☆'
            favorite_star.config(fg=star_color, text=star_text)
        
        favorite_star.bind("<Enter>", on_star_enter)
        favorite_star.bind("<Leave>", on_star_leave)
        favorite_star.bind("<Button-1>", lambda e, g=game: self.toggle_favorite(g))
        
        # Contenedor de imagen con mejor diseño
        image_container = tk.Frame(card_frame, bg=self.colors['bg_light'])
        image_container.pack(pady=(0, 15), padx=15)
        
        try:
            # Cargar y redimensionar imagen con bordes redondeados simulados
            image = Image.open(game['image_path'])
            image = image.resize((240, 270), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Label de imagen con mejor presentación
            image_label = tk.Label(image_container, 
                                  image=photo, 
                                  bg=self.colors['bg_light'],
                                  cursor='hand2',
                                  relief='solid',
                                  bd=1)
            image_label.image = photo
            image_label.pack()
            image_label.bind("<Button-1>", lambda e, g=game: self.open_game_map(g))
            
        except Exception as e:
            # Imagen por defecto con mejor diseño
            default_photo = self.create_default_image(240, 270, 
                                                    game['name'][:15] + "..." if len(game['name']) > 15 else game['name'])
            
            if default_photo:
                placeholder_label = tk.Label(image_container, 
                                            image=default_photo,
                                            bg=self.colors['bg_light'],
                                            cursor='hand2',
                                            relief='solid',
                                            bd=1)
                placeholder_label.image = default_photo
            else:
                placeholder_label = tk.Label(image_container, 
                                            text="🎮\n" + self.get_text('no_image'),
                                            bg=self.colors['bg_light'],
                                            fg=self.colors['text_muted'],
                                            font=('Segoe UI', 20),
                                            width=30, height=17,
                                            relief='solid',
                                            bd=1)
            
            placeholder_label.pack()
            placeholder_label.bind("<Button-1>", lambda e, g=game: self.open_game_map(g))
        
        # Frame para botones con mejor diseño
        buttons_frame = tk.Frame(card_frame, bg=self.colors['bg_light'])
        buttons_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Botón de editar mejorado con ícono
        edit_button = tk.Button(buttons_frame, 
                               text="✏️ " + self.get_text('edit_game'), 
                               bg=self.colors['warning'], 
                               fg='white',
                               font=('Segoe UI', 9, 'bold'),
                               relief='flat',
                               cursor='hand2',
                               pady=8,
                               command=lambda g=game: self.edit_game(g))
        edit_button.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Botón de eliminar mejorado con ícono
        delete_button = tk.Button(buttons_frame, 
                                 text="🗑️ " + self.get_text('delete_game'), 
                                 bg=self.colors['danger'], 
                                 fg='white',
                                 font=('Segoe UI', 9, 'bold'),
                                 relief='flat',
                                 cursor='hand2',
                                 pady=8,
                                 command=lambda g=game: self.delete_game(g))
        delete_button.pack(side='right', fill='x', expand=True, padx=(5, 0))
        
        # Efectos hover para botones
        def on_edit_enter(event):
            edit_button.config(bg=self.colors['accent_hover'] if hasattr(self.colors, 'accent_hover') else self.colors['accent'])
        
        def on_edit_leave(event):
            edit_button.config(bg=self.colors['warning'])
            
        def on_delete_enter(event):
            delete_button.config(bg='#ff6666')
        
        def on_delete_leave(event):
            delete_button.config(bg=self.colors['danger'])
        
        edit_button.bind("<Enter>", on_edit_enter)
        edit_button.bind("<Leave>", on_edit_leave)
        delete_button.bind("<Enter>", on_delete_enter)
        delete_button.bind("<Leave>", on_delete_leave)
        
        # Agregar efectos hover mejorados para toda la tarjeta
        self.setup_hover_effects_enhanced(card_frame, name_label, header_frame, buttons_frame)
    
    def toggle_favorite(self, game):
        """Alternar estado de favorito de un juego con efectos visuales"""
        # Cambiar estado de favorito
        current_favorite = game.get('favorite', False)
        game['favorite'] = not current_favorite
        
        # Guardar cambios
        self.save_games()
        
        # Mostrar mensaje de feedback temporal
        action = self.get_text('add_to_favorites') if game['favorite'] else self.get_text('remove_from_favorites')
        self.show_temporary_message(f"{action}: {game['name']}", game['favorite'])
        
        # Actualizar visualización con animación sutil
        self.refresh_games_display()
        
        # Actualizar contadores en botones de filtro si existen
        self.update_filter_button_counters()
    
    def show_temporary_message(self, message, is_favorite):
        """Mostrar mensaje temporal de feedback al usuario"""
        # Crear ventana temporal
        temp_window = tk.Toplevel(self.root)
        temp_window.title("")
        temp_window.geometry("300x80")
        temp_window.resizable(False, False)
        temp_window.transient(self.root)
        
        # Configurar colores según si es favorito o no
        bg_color = '#4CAF50' if is_favorite else '#FF9800'  # Verde para agregar, naranja para quitar
        
        temp_window.configure(bg=bg_color)
        
        # Centrar la ventana
        temp_window.update_idletasks()
        x = (temp_window.winfo_screenwidth() // 2) - (300 // 2)
        y = (temp_window.winfo_screenheight() // 2) - (80 // 2)
        temp_window.geometry(f"300x80+{x}+{y}")
        
        # Quitar decoraciones de ventana
        temp_window.overrideredirect(True)
        
        # Mensaje
        label = tk.Label(temp_window, 
                        text=message,
                        bg=bg_color,
                        fg='white',
                        font=('Segoe UI', 10, 'bold'),
                        wraplength=280)
        label.pack(expand=True)
        
        # Auto-cerrar después de 2 segundos
        temp_window.after(2000, temp_window.destroy)
    
    def update_filter_button_counters(self):
        """Actualizar contadores en los botones de filtro"""
        if not hasattr(self, 'all_button') or not self.all_button.winfo_exists():
            return
            
        # Contar favoritos
        favorites_count = len([game for game in self.games if game.get('favorite', False)])
        total_count = len(self.games)
        
        # Actualizar texto de botones con contadores
        all_text = f"{self.get_text('all_games')} ({total_count})"
        favorites_text = f"{self.get_text('favorites')} ({favorites_count})"
        
        # Actualizar botones si existen
        try:
            self.all_button.config(text=all_text)
            self.favorites_button.config(text=favorites_text)
        except tk.TclError:
            # Los botones fueron destruidos, no hacer nada
            pass
    
    def open_game_map(self, game):
        """Abrir ventana con el mapa del juego"""
        print(f"Abriendo mapa para {game['name']} - Tipo: {game['map_type']}")  # Debug
        
        if game['map_type'] == 'image':
            # Para imágenes, crear ventana tkinter normal
            map_window = tk.Toplevel(self.root)
            map_window.title(f"{self.get_text('map_window_title')} - {game['name']}")
            map_window.geometry("1000x700")
            map_window.configure(bg=self.colors['bg_dark'])
            
            # Configurar icono de la ventana del mapa
            self.apply_window_icon(map_window)
            
            self.show_image_map(map_window, game)
        else:
            # Para mapas web, ir directamente a webview sin crear ventana tkinter
            self.show_iframe_map_direct(game)
    
    def show_iframe_map_direct(self, game):
        """Abrir mapa web directamente sin crear ventana tkinter primero"""
        print(f"Abriendo mapa web directamente: {game['map_content']}")  # Debug
        
        # Método directo usando webview - sin ventana tkinter intermedia
        try:
            import webview
            
            # Crear ventana webview directamente
            webview.create_window(
                title=f"Mapa - {game['name']}",
                url=game['map_content'],
                width=1000,
                height=700,
                resizable=True,
                minimized=False,
                on_top=False,
                shadow=True,
                text_select=True
            )
            
            # Iniciar webview - esto bloquea hasta que se cierre la ventana
            webview.start(debug=False)
            
        except ImportError:
            print("webview no disponible, creando ventana tkinter como fallback...")
            # Si webview no está disponible, crear ventana tkinter como fallback
            self.create_tkinter_map_window(game)
        except Exception as e:
            print(f"Error con webview directo: {e}")
            # Si hay error, crear ventana tkinter como fallback
            self.create_tkinter_map_window(game)
    
    def create_tkinter_map_window(self, game):
        """Crear ventana tkinter para mapa web como fallback"""
        # Crear ventana tkinter solo cuando sea necesario
        map_window = tk.Toplevel(self.root)
        map_window.title(f"{self.get_text('map_window_title')} - {game['name']}")
        map_window.geometry("1000x700")
        map_window.configure(bg=self.colors['bg_dark'])
        
        # Configurar icono de la ventana del mapa
        self.apply_window_icon(map_window)
        
        # Usar el método de fallback HTML
        self.show_html_browser(map_window, game)
    
    def show_image_map(self, window, game):
        """Mostrar mapa como imagen"""
        try:
            # Cargar imagen
            image = Image.open(game['map_content'])
            
            # Crear frame principal que ocupe toda la ventana
            main_frame = tk.Frame(window, bg=self.colors['bg_dark'])
            main_frame.pack(fill="both", expand=True, padx=0, pady=0)
            
            # Crear canvas scrollable para imagen grande
            canvas = tk.Canvas(main_frame, bg=self.colors['bg_dark'], highlightthickness=0)
            
            # Crear scrollbars
            scrollbar_v = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollbar_h = ttk.Scrollbar(main_frame, orient="horizontal", command=canvas.xview)
            
            canvas.configure(yscrollcommand=scrollbar_v.set, 
                           xscrollcommand=scrollbar_h.set)
            
            # Obtener dimensiones reales de la ventana
            window.update_idletasks()  # Asegurar que la ventana esté actualizada
            window_width = window.winfo_width() - 20  # Dejar margen pequeño
            window_height = window.winfo_height() - 20
            
            # Si las dimensiones no están disponibles, usar valores por defecto
            if window_width <= 20:
                window_width = 980
            if window_height <= 20:
                window_height = 680
                
            img_width, img_height = image.size
            
            # Calcular tamaño de visualización manteniendo ratio
            ratio = min(window_width/img_width, window_height/img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            # Si la imagen es más pequeña que la ventana, mostrarla a tamaño original
            if new_width >= img_width and new_height >= img_height:
                new_width = img_width
                new_height = img_height
            else:
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            
            # Centrar la imagen en el canvas
            canvas_width = max(new_width, window_width)
            canvas_height = max(new_height, window_height)
            
            x_center = canvas_width // 2
            y_center = canvas_height // 2
            
            canvas.create_image(x_center, y_center, anchor="center", image=photo)
            canvas.image = photo  # Mantener referencia
            
            # Configurar región de scroll
            canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))
            
            # Layout optimizado para eliminar espacios
            # Scrollbar horizontal abajo
            scrollbar_h.pack(side="bottom", fill="x")
            # Scrollbar vertical a la derecha
            scrollbar_v.pack(side="right", fill="y")
            # Canvas ocupa el resto del espacio
            canvas.pack(side="left", fill="both", expand=True)
            
            # Variables para manejar redimensionamiento
            canvas.original_image = Image.open(game['map_content'])  # Imagen original
            canvas.current_scale = 1.0
            canvas.is_manual_zoom = False  # Para saber si el usuario hizo zoom manual
            
            # Función para redimensionar imagen cuando cambie el tamaño de ventana
            def resize_image_to_window():
                try:
                    # Obtener nuevas dimensiones de la ventana
                    window.update_idletasks()
                    new_window_width = window.winfo_width() - 20
                    new_window_height = window.winfo_height() - 20
                    
                    # Verificar que las dimensiones sean válidas
                    if new_window_width <= 20 or new_window_height <= 20:
                        return
                    
                    # Si no hay zoom manual, ajustar automáticamente
                    if not canvas.is_manual_zoom:
                        # Calcular nuevo ratio para ajustar a la ventana
                        ratio = min(new_window_width/img_width, new_window_height/img_height)
                        new_width = int(img_width * ratio)
                        new_height = int(img_height * ratio)
                        
                        # Si la imagen es más pequeña que la ventana, mostrarla a tamaño original
                        if new_width >= img_width and new_height >= img_height:
                            new_width = img_width
                            new_height = img_height
                            canvas.current_scale = 1.0
                        else:
                            canvas.current_scale = ratio
                        
                        # Redimensionar imagen
                        resized_image = canvas.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(resized_image)
                        
                        # Actualizar canvas
                        canvas.delete("all")
                        canvas_width = max(new_width, new_window_width)
                        canvas_height = max(new_height, new_window_height)
                        
                        x_center = canvas_width // 2
                        y_center = canvas_height // 2
                        
                        canvas.create_image(x_center, y_center, anchor="center", image=photo)
                        canvas.image = photo
                        canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))
                        
                except Exception as e:
                    print(f"Error al redimensionar imagen: {e}")
            
            # Función para manejar el evento de redimensionamiento de ventana
            def on_window_resize(event):
                # Solo responder al evento de la ventana principal, no del canvas
                if event.widget == window:
                    # Usar after para evitar múltiples llamadas rápidas
                    if hasattr(canvas, 'resize_job'):
                        window.after_cancel(canvas.resize_job)
                    canvas.resize_job = window.after(100, resize_image_to_window)
            
            # Vincular evento de redimensionamiento
            window.bind("<Configure>", on_window_resize)
            
            # Configurar zoom con scroll del mouse
            def on_mousewheel(event):
                if event.state & 0x4:  # Ctrl presionado
                    # Zoom con Ctrl + scroll
                    canvas.is_manual_zoom = True  # Marcar que hay zoom manual
                    current_scale = canvas.current_scale
                    if event.delta > 0:
                        new_scale = current_scale * 1.1
                    else:
                        new_scale = current_scale * 0.9
                    
                    # Limitar zoom
                    new_scale = max(0.1, min(5.0, new_scale))
                    canvas.current_scale = new_scale
                    
                    # Redimensionar imagen
                    scaled_width = int(img_width * new_scale)
                    scaled_height = int(img_height * new_scale)
                    scaled_image = canvas.original_image.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
                    scaled_photo = ImageTk.PhotoImage(scaled_image)
                    
                    canvas.delete("all")
                    canvas.create_image(scaled_width//2, scaled_height//2, anchor="center", image=scaled_photo)
                    canvas.image = scaled_photo
                    canvas.configure(scrollregion=(0, 0, scaled_width, scaled_height))
                else:
                    # Scroll normal
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            canvas.bind("<MouseWheel>", on_mousewheel)
            
            # Permitir arrastrar la imagen
            def start_move(event):
                canvas.scan_mark(event.x, event.y)
                
            def move_image(event):
                canvas.scan_dragto(event.x, event.y, gain=1)
                
            canvas.bind("<Button-1>", start_move)
            canvas.bind("<B1-Motion>", move_image)
            
            # Función para resetear zoom (doble click)
            def reset_zoom(event):
                canvas.is_manual_zoom = False
                resize_image_to_window()
            
            canvas.bind("<Double-Button-1>", reset_zoom)
            
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
        """Mostrar mapa web en ventana integrada del programa"""
        print(f"Abriendo mapa web: {game['map_content']}")  # Debug
        
        # Método directo usando webview en la misma ventana
        try:
            import webview
            
            # Cerrar la ventana de tkinter y crear una nueva ventana de webview
            window.destroy()
            
            # Crear ventana webview que reemplace completamente la ventana de tkinter
            webview.create_window(
                title=f"Mapa - {game['name']}",
                url=game['map_content'],
                width=1000,
                height=700,
                resizable=True,
                minimized=False,
                on_top=False,
                shadow=True,
                text_select=True
            )
            
            # Iniciar webview - esto bloquea hasta que se cierre la ventana
            webview.start(debug=False)
            
        except ImportError:
            print("webview no disponible, intentando método HTML directo...")
            self.show_html_browser(window, game)
        except Exception as e:
            print(f"Error con webview: {e}")
            self.show_html_browser(window, game)
    
    def show_html_browser(self, window, game):
        """Método de fallback usando tkinterweb con HTML optimizado"""
        try:
            from tkinterweb import HtmlFrame
            
            # Crear frame HTML que ocupe toda la ventana
            html_frame = HtmlFrame(window, 
                                 horizontal_scrollbar="auto",
                                 vertical_scrollbar="auto")
            html_frame.pack(fill=tk.BOTH, expand=True)
            
            # HTML completamente optimizado para iframe
            html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa - {game['name']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        html, body {{
            height: 100%;
            width: 100%;
            overflow: hidden;
            background: {self.colors['bg_dark']};
        }}
        #mapIframe {{
            width: 100vw;
            height: 100vh;
            border: none;
            display: block;
        }}
        .loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: {self.colors['text']};
            font-family: Arial, sans-serif;
            text-align: center;
            z-index: 1000;
        }}
    </style>
</head>
<body>
    <div class="loading" id="loading">
        <h3>Cargando mapa...</h3>
        <p>Por favor espera</p>
    </div>
    
    <iframe id="mapIframe" 
            src="{game['map_content']}" 
            frameborder="0"
            scrolling="auto"
            allowfullscreen="true"
            allow="geolocation; microphone; camera; midi; encrypted-media; fullscreen; payment; autoplay"
            sandbox="allow-scripts allow-same-origin allow-popups allow-forms allow-downloads allow-top-navigation allow-modals"
            onload="hideLoading()"
            onerror="showError()">
    </iframe>
    
    <script>
        function hideLoading() {{
            document.getElementById('loading').style.display = 'none';
            console.log('Iframe cargado correctamente');
        }}
        
        function showError() {{
            document.getElementById('loading').innerHTML = 
                '<h3>⚠️ Error de carga</h3><p>El sitio puede tener restricciones</p>' +
                '<p><a href="{game['map_content']}" target="_blank" style="color: {self.colors['accent']};">Abrir en navegador</a></p>';
        }}
        
        // Ocultar loading después de 5 segundos como máximo
        setTimeout(function() {{
            document.getElementById('loading').style.display = 'none';
        }}, 5000);
        
        // Verificar si el iframe está cargando
        window.addEventListener('load', function() {{
            setTimeout(hideLoading, 1000);
        }});
    </script>
</body>
</html>
            '''
            
            # Cargar el HTML
            html_frame.load_html(html_content)
            print(f"HTML browser cargado para: {game['map_content']}")
            
        except ImportError:
            print("tkinterweb no disponible, usando fallback final...")
            self.show_simple_redirect(window, game)
        except Exception as e:
            print(f"Error con HTML browser: {e}")
            self.show_simple_redirect(window, game)
    
    def show_simple_redirect(self, window, game):
        """Método más simple - crear archivo HTML temporal y abrirlo"""
        try:
            import tempfile
            import os
            
            # Crear archivo HTML temporal
            html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa - {game['name']}</title>
    <style>
        * {{ margin: 0; padding: 0; }}
        html, body {{ height: 100%; overflow: hidden; }}
        iframe {{ width: 100vw; height: 100vh; border: none; }}
    </style>
</head>
<body>
    <iframe src="{game['map_content']}" 
            frameborder="0" 
            allowfullscreen 
            allow="geolocation; camera; microphone; encrypted-media">
    </iframe>
</body>
</html>
            '''
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file = f.name
            
            # Abrir archivo en navegador por defecto
            import webbrowser
            webbrowser.open(f'file://{temp_file}')
            
            # Cerrar ventana de tkinter
            window.destroy()
            
            # Programar eliminación del archivo temporal
            def cleanup():
                try:
                    os.unlink(temp_file)
                except:
                    pass
            
            # Eliminar archivo después de 30 segundos
            import threading
            timer = threading.Timer(30.0, cleanup)
            timer.start()
            
            print(f"Archivo temporal creado y abierto: {temp_file}")
            
        except Exception as e:
            print(f"Error con redirect simple: {e}")
            # Fallback final - el método original
            self.show_webview_fallback_in_frame(window, game)
    
    def show_alternative_browser(self, window, game):
        """Método alternativo usando pywebview embebido correctamente"""
        try:
            import webview
            
            # Crear frame contenedor
            container = tk.Frame(window, bg=self.colors['bg_dark'])
            container.pack(fill=tk.BOTH, expand=True)
            
            # Intentar crear webview embebido en el contenedor
            def create_webview():
                try:
                    # Ocultar la ventana de tkinter temporalmente
                    window.withdraw()
                    
                    # Crear ventana de webview que reemplace la de tkinter
                    webview.create_window(
                        title=f"🗺️ Mapa - {game['name']}",
                        url=game['map_content'],
                        width=1000,
                        height=700,
                        resizable=True,
                        minimized=False,
                        on_top=False,
                        shadow=True
                    )
                    
                    # Iniciar webview
                    webview.start(debug=False)
                    
                    # Cuando webview se cierre, cerrar también la ventana de tkinter
                    window.destroy()
                    
                except Exception as e:
                    print(f"Error con webview: {e}")
                    # Restaurar ventana y mostrar fallback
                    try:
                        window.deiconify()
                        self.show_webview_fallback_in_frame(container, game)
                    except:
                        pass
            
            # Ejecutar en hilo separado
            import threading
            webview_thread = threading.Thread(target=create_webview, daemon=True)
            webview_thread.start()
            
        except ImportError:
            print("webview no disponible, usando fallback final...")
            self.show_webview_fallback_in_frame(window, game)
        except Exception as e:
            print(f"Error con alternative browser: {e}")
            self.show_webview_fallback_in_frame(window, game)
    
    def show_webview_embedded(self, container, game):
        """Método alternativo para embeber contenido web usando HTML/iframe básico"""
        try:
            from tkinterweb import HtmlFrame
            
            # Crear frame HTML que ocupe toda la ventana
            html_frame = HtmlFrame(container, 
                                 horizontal_scrollbar="auto",
                                 vertical_scrollbar="auto",
                                 background=self.colors['bg_dark'])
            html_frame.pack(fill=tk.BOTH, expand=True)
            
            # HTML optimizado con iframe embebido
            iframe_html = f'''
            <!DOCTYPE html>
            <html style="margin:0; padding:0; height:100%; width:100%;">
            <head>
                <meta charset="UTF-8">
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    html, body {{ height: 100%; width: 100%; overflow: hidden; }}
                    iframe {{ 
                        width: 100%; 
                        height: 100vh; 
                        border: none; 
                        display: block; 
                    }}
                </style>
            </head>
            <body>
                <iframe src="{game['map_content']}" 
                        frameborder="0" 
                        allowfullscreen
                        allow="geolocation; microphone; camera; encrypted-media; fullscreen"
                        sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-top-navigation">
                </iframe>
            </body>
            </html>
            '''
            
            html_frame.load_html(iframe_html)
            
        except ImportError:
            print("tkinterweb no disponible, usando fallback básico")
            self.show_webview_fallback_in_frame(container, game)
        except Exception as e:
            print(f"Error con embedded webview: {e}")
            self.show_webview_fallback_in_frame(container, game)
    
    def show_webview_fallback_in_frame(self, container, game):
        """Mostrar fallback cuando webview no funciona"""
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
        
        # Mensaje secundario
        reason_label = tk.Label(container,
                               text="El sitio web puede tener restricciones para mostrarse en frames integrados",
                               bg=self.colors['bg_dark'],
                               fg=self.colors['text_muted'],
                               font=('Arial', 10))
        reason_label.pack(pady=(0, 20))
        
        # Descripción
        desc_label = tk.Label(container,
                             text="Haz clic en el botón de abajo para abrir el mapa en tu navegador:",
                             bg=self.colors['bg_dark'],
                             fg=self.colors['text_muted'],
                             font=('Arial', 10))
        desc_label.pack(pady=(0, 30))
        
        # Botón para abrir en navegador
        def open_in_browser():
            try:
                import webbrowser
                webbrowser.open(game['map_content'])
                import tkinter.messagebox as messagebox
                messagebox.showinfo(
                    self.get_text('success'),
                    f"Mapa de {game['name']} abierto en navegador"
                )
            except Exception as e:
                import tkinter.messagebox as messagebox
                messagebox.showerror(
                    self.get_text('error'),
                    f"Error al abrir navegador: {e}"
                )
        
        browser_button = tk.Button(container,
                                 text="🌐 Abrir en navegador",
                                 bg=self.colors['accent'],
                                 fg=self.colors['text'],
                                 font=('Arial', 12, 'bold'),
                                 relief='flat',
                                 cursor='hand2',
                                 command=open_in_browser,
                                 padx=30,
                                 pady=15)
        browser_button.pack()
    
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
                              insertbackground=self.colors['text'])
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
        
        image_radio = tk.Radiobutton(map_type_frame, text=self.get_text('map_type_image'),
                                    variable=self.edit_map_type_var, value="image",
                                    bg=self.colors['bg_dark'], fg=self.colors['text'],
                                    selectcolor=self.colors['bg_light'],
                                    activebackground=self.colors['bg_dark'])
        image_radio.pack(side=tk.LEFT)
        
        iframe_radio = tk.Radiobutton(map_type_frame, text=self.get_text('map_type_web'),
                                     variable=self.edit_map_type_var, value="iframe",
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
                                    bg=self.colors['bg_light'], fg=self.colors['text'],
                                    font=('Segoe UI', 10), relief='flat',
                                    insertbackground=self.colors['text'])
        map_content_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        browse_map_button = ttk.Button(map_content_frame, text=self.get_text('browse_map'),
                                      command=self.browse_edit_map_content)
        browse_map_button.pack(side=tk.RIGHT, padx=(10, 0))
        
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
        
        # Actualizar el juego en la lista
        game_index = self.games.index(self.edit_original_game)
        self.games[game_index] = {
            'name': name,
            'image_path': local_image_path,
            'map_type': map_type,
            'map_content': local_map_content,
            'favorite': self.edit_original_game.get('favorite', False)  # Preservar estado de favorito
        }
        
        # Guardar y actualizar la interfaz
        self.save_games()
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
            self.games.remove(game)
            self.save_games()
            self.refresh_games_display()
            
            # Limpiar imágenes no utilizadas después de eliminar
            self.cleanup_unused_images()
    
    def load_games(self):
        """Cargar juegos desde archivo JSON"""
        if os.path.exists(self.games_file):
            try:
                with open(self.games_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error cargando juegos: {e}")
                return []
        return []
    
    def save_games(self):
        """Guardar juegos en archivo JSON"""
        try:
            with open(self.games_file, 'w', encoding='utf-8') as f:
                json.dump(self.games, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando juegos: {e}")
    
    def on_window_resize(self, event):
        """Manejar redimensionamiento de ventana para layout responsive"""
        # Solo procesar eventos del widget root, no de widgets hijos
        if event.widget == self.root:
            # Usar after para evitar múltiples llamadas rápidas durante el redimensionamiento
            if hasattr(self, '_resize_job'):
                self.root.after_cancel(self._resize_job)
            self._resize_job = self.root.after(300, self.refresh_games_display)
    
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
        
        # Configurar icono del diálogo de edición
        try:
            dialog.iconbitmap("logo.ico")
        except:
            pass
        
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
    def start_main_app():
        """Iniciar la aplicación principal después del splash"""
        root = tk.Tk()
        app = AvalonGameManager(root)
        root.mainloop()
    
    # Mostrar splash screen con callback
    splash = SplashScreen()
    splash.show(on_complete=start_main_app)

if __name__ == "__main__":
    main()
