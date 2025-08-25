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
        
        # Dimensiones del splash (mÃ¡s grande para mÃ¡s profesional)
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
        
        # TÃ­tulo con efecto
        self.create_title()
        
        # SubtÃ­tulo
        self.create_subtitle()
        
        # Barra de progreso moderna
        self.create_modern_progress_bar()
        
        # Estado y versiÃ³n
        self.create_status_area()
        
        # PartÃ­culas decorativas
        self.create_decorative_particles()
    
    def setup_animated_logo(self):
        """Configurar logo con animaciÃ³n"""
        try:
            logo_path = resource_path("logo.ico")
            
            if os.path.exists(logo_path):
                # Cargar y redimensionar el logo
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((80, 80), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                
                # PosiciÃ³n inicial del logo (serÃ¡ animada)
                self.logo_id = self.canvas.create_image(
                    250, 70, image=self.logo_photo, anchor='center'
                )
            else:
                # Logo placeholder mÃ¡s profesional
                self.logo_id = self.canvas.create_text(
                    250, 70, text="ðŸš€", font=('Segoe UI Emoji', 60),
                    fill='#c9b037', anchor='center'
                )
        except Exception:
            # Fallback logo
            self.logo_id = self.canvas.create_text(
                250, 70, text="ðŸš€", font=('Segoe UI Emoji', 60),
                fill='#c9b037', anchor='center'
            )
    
    def create_title(self):
        """Crear tÃ­tulo con efecto glow"""
        # Sombra del tÃ­tulo (sutil)
        self.canvas.create_text(
            251, 131, text="AVILON", 
            font=('Segoe UI', 32, 'bold'),
            fill='#404040', anchor='center'
        )
        
        # TÃ­tulo principal
        self.title_id = self.canvas.create_text(
            250, 130, text="AVILON", 
            font=('Segoe UI', 32, 'bold'),
            fill='#ffffff', anchor='center'
        )
    
    def create_subtitle(self):
        """Crear subtÃ­tulo elegante"""
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
        """Crear Ã¡rea de estado y versiÃ³n"""
        # Estado de carga
        self.status_id = self.canvas.create_text(
            250, 255, text="Iniciando...", 
            font=('Segoe UI', 10),
            fill='#b0b0b0', anchor='center'
        )
        
        # VersiÃ³n
        self.version_id = self.canvas.create_text(
            250, 320, text="v1.5.0", 
            font=('Segoe UI', 9),
            fill='#808080', anchor='center'
        )
    
    def create_decorative_particles(self):
        """Crear partÃ­culas decorativas"""
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
        """Animar fade in del tÃ­tulo"""
        if self.title_alpha < 255:
            self.title_alpha += 15
            # Aplicar efecto de fade (simulado con colores)
            self.splash.after(100, self.animate_title_fade_in)
    
    def animate_particles(self):
        """Animar partÃ­culas flotantes"""
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
        """Actualizar la barra de progreso y el texto de estado con animaciÃ³n"""
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
        
        # Actualizar texto de estado con animaciÃ³n
        self.canvas.itemconfig(self.status_id, text=status_text)
        
        # Efecto de pulsaciÃ³n para el estado
        self.animate_status_pulse()
        
        self.splash.update()
    
    def animate_status_pulse(self):
        """Animar pulsaciÃ³n del texto de estado"""
        colors = ['#b0b0b0', '#ffffff', '#b0b0b0']
        for i, color in enumerate(colors):
            self.splash.after(i * 100, lambda c=color: self.canvas.itemconfig(self.status_id, fill=c))
    
    def simulate_loading(self):
        """Simular proceso de carga con efectos visuales mejorados"""
        self.loading_steps = [
            (5, "ðŸ”§ Inicializando componentes..."),
            (15, "âš™ï¸ Cargando configuraciÃ³n..."),
            (30, "ðŸ“ Verificando archivos..."),
            (45, "ðŸŽ¨ Configurando interfaz..."),
            (60, "ðŸŽ® Preparando biblioteca de juegos..."),
            (75, "ðŸ” Indexando contenido..."),
            (90, "âœ¨ Aplicando Ãºltimos toques..."),
            (100, "ðŸš€ Â¡Listo para despegar!")
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
            
            # Tiempo variable segÃºn el paso (mÃ¡s realista)
            delay = 400 if progress < 50 else 600 if progress < 90 else 300
            self.splash.after(delay, self.update_loading_step)
        else:
            # Completar la carga con animaciÃ³n de salida
            self.splash.after(800, self.start_exit_animation)
    
    def create_loading_effect(self):
        """Crear efecto visual durante la carga"""
        # Crear ondas de energÃ­a desde el logo
        for i in range(3):
            self.splash.after(i * 100, self.create_energy_wave)
    
    def create_energy_wave(self):
        """Crear onda de energÃ­a"""
        import random
        
        # Crear cÃ­rculo expandiÃ©ndose desde el logo
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
        """Iniciar animaciÃ³n de salida"""
        self.exit_alpha = 255
        self.fade_out()
    
    def fade_out(self):
        """AnimaciÃ³n de fade out"""
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
        """Mostrar el splash screen y iniciar la simulaciÃ³n de carga"""
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
                # Iniciar simulaciÃ³n de carga despuÃ©s del fade in
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
            # Si estÃ¡ ejecutÃ¡ndose como ejecutable
            self.base_dir = os.path.dirname(sys.executable)
        else:
            # Si estÃ¡ ejecutÃ¡ndose como script
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
        
        # Crear directorio de imÃ¡genes si no existe
        self.images_dir = os.path.join(self.base_dir, "game_images")
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Variable para la bÃºsqueda
        self.search_var = None
        
        # Sistema de favoritos
        self.favorites_filter = "all"  # "all" o "favorites"
        
        # Sistema de idiomas y configuraciÃ³n
        self.config_file = os.path.join(self.base_dir, "avilon_config.json")
        self.config = self.load_config()
        self.current_language = self.config.get('language', 'es')
        self.current_theme = self.config.get('theme', 'slate')
        self.startup_enabled = self.config.get('startup', False)
        self.translations = self.load_translations()
        self.themes = self.load_themes()
        
        # Establecer tÃ­tulo con traducciones
        self.root.title(self.get_text('window_title'))
        
        # Configurar estilo Discord-like
        self.setup_styles()
        
        # Crear barra de menÃº
        self.create_menu_bar()
        
        # Crear la interfaz
        self.create_main_interface()
        
        # Cargar juegos existentes
        self.refresh_games_display()
        
        # Migrar juegos existentes al directorio local (solo la primera vez)
        self.migrate_existing_games()
        
        # Binding para redimensionamiento responsive
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Configurar cierre de aplicaciÃ³n para limpiar CEF
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def apply_window_icon(self, window):
        """Aplicar el icono a cualquier ventana"""
        try:
            if hasattr(self, 'icon_path') and self.icon_path and os.path.exists(self.icon_path):
                window.iconbitmap(self.icon_path)
        except Exception as e:
            print(f"No se pudo aplicar el icono a la ventana: {e}")
    
    def setup_styles(self):
        """Configurar estilos segÃºn el tema seleccionado"""
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
        
        # Color mÃ¡s claro para hover (dinÃ¡mico segÃºn el tema) con efecto gradiente
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
        
        # Configurar estilos especÃ­ficos para diferentes elementos segÃºn el tema
        if self.current_theme == 'light':
            button_text_color = '#ffffff'  # Texto blanco para botones en tema claro
        else:
            button_text_color = self.colors['text']
        
        style.configure('Accent.TButton',
                       background=self.colors['accent'],
                       foreground=button_text_color,
                       borderwidth=0,
                       focuscolor='none')
        
        # Color activo dinÃ¡mico para botones
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
                # MenÃºs
                'file_menu': 'Archivo',
                'help_menu': 'Ayuda',
                'config_menu': 'ConfiguraciÃ³n',
                'about_menu': 'Acerca de',
                
                # Ventana principal
                'window_title': 'Avilon',
                'add_game': 'AÃ±adir Juego',
                'add_game_button': '+ AÃ±adir Juego',
                'library': 'BIBLIOTECA',
                'games_count': 'juegos',
                'game_singular': 'juego',
                'no_games': 'No hay juegos en tu biblioteca.\nVe a "Archivo" â†’ "AÃ±adir Juego" para comenzar.',
                'search_placeholder': 'Buscar juegos... (favoritos siempre visibles)',
                
                # Formulario aÃ±adir juego
                'add_game_title': 'AÃ±adir Nuevo Juego',
                'game_name': 'Nombre del juego:',
                'game_image': 'Imagen del juego:',
                'browse_image': 'Examinar imagen',
                'map_content': 'Ruta/URL del mapa:',
                'map_type_label': 'Tipo de mapa:',
                'map_type_image': 'Imagen',
                'map_type_web': 'PÃ¡gina web (iframe)',
                'browse_map': 'Examinar',
                'save': 'Guardar',
                'cancel': 'Cancelar',
                'save_changes': 'Guardar cambios',
                
                # Mensajes
                'error': 'Error',
                'success': 'Ã‰xito',
                'game_saved': 'Juego guardado correctamente',
                'fill_required_fields': 'Por favor, completa todos los campos requeridos',
                'invalid_image': 'Formato de imagen no vÃ¡lido',
                'invalid_url': 'URL no vÃ¡lida',
                'select_image': 'Seleccionar imagen',
                'select_map': 'Seleccionar mapa',
                'image_files': 'Archivos de imagen',
                'all_files': 'Todos los archivos',
                
                # Ventana acerca de
                'about_title': 'Acerca de Avilon',
                'about_description': 'Avilon es un programa diseÃ±ado y programado por una Ãºnica persona, donde podrÃ¡s gestionar los mapas de tus juegos favoritos',
                'close': 'Cerrar',
                
                # ConfiguraciÃ³n
                'config_title': 'ConfiguraciÃ³n',
                'config_subtitle': 'Personaliza tu experiencia de juego',
                'language_label': 'Idioma:',
                'theme_label': 'Tema:',
                'spanish': 'EspaÃ±ol',
                'english': 'English',
                'french': 'FranÃ§ais',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'PortuguÃªs',
                'dutch': 'Nederlands',
                'russian': 'Ð ÑƒÑÑÐºÐ¸Ð¹',
                'japanese': 'æ—¥æœ¬èªž',
                'chinese': 'ä¸­æ–‡',
                'theme_slate': 'Pizarra',
                'theme_dark': 'Oscuro',
                'theme_light': 'Claro',
                'theme_blue': 'Azul',
                'theme_green': 'Verde',
                'apply': 'Aplicar',
                'config_saved': 'ConfiguraciÃ³n guardada correctamente',
                
                # Botones de juego
                'view_map': 'Ver mapa',
                'edit': 'Editar',
                'delete': 'Eliminar',
                'delete_game': 'Borrar juego',
                'edit_game': 'Editar juego',
                'no_image': 'Sin imagen',
                'confirm_delete': 'Â¿EstÃ¡s seguro de que quieres eliminar este juego?',
                'confirm_title': 'Confirmar',
                'yes': 'SÃ­',
                'no': 'No',
                
                # Editar juego
                'edit_game_title': 'Editar Juego',
                
                # TÃ­tulos de ventana
                'map_window_title': 'Mapa',
                
                # Sistema de favoritos
                'all_games': 'Todos',
                'favorites': 'Favoritos',
                'add_to_favorites': 'AÃ±adir a favoritos',
                'remove_from_favorites': 'Quitar de favoritos',
                
                # Inicio automÃ¡tico
                'startup_label': 'Iniciar con Windows:',
                'startup_enabled': 'Programa configurado para iniciar con Windows',
                'startup_disabled': 'Programa removido del inicio automÃ¡tico',
                'startup_error': 'Error al configurar el inicio automÃ¡tico',
                
                # GuÃ­a de uso
                'how_to_use_menu': 'CÃ³mo se usa',
                'user_guide_title': 'GuÃ­a de Usuario - CÃ³mo usar Avilon',
                'guide_tab_games': 'Juegos',
                'guide_tab_maps': 'Mapas', 
                'guide_tab_features': 'CaracterÃ­sticas',
                'guide_tab_tips': 'Consejos',
                
                # PestaÃ±a Juegos
                'guide_games_title': 'ðŸŽ® GestiÃ³n de Juegos',
                'guide_games_add_title': 'ðŸ“ CÃ³mo agregar un juego:',
                'guide_games_add_content': '''1. Ve al menÃº "Archivo" â†’ "AÃ±adir Juego"
2. Completa el nombre del juego
3. Selecciona una imagen (opcional):
   â€¢ Formatos soportados: PNG, JPG, JPEG, BMP, GIF
   â€¢ Recomendado: 250x280 pÃ­xeles
4. Configura el mapa (ver pestaÃ±a "Mapas")
5. Haz clic en "Guardar"''',
                'guide_games_manage_title': 'âš™ï¸ Gestionar juegos existentes:',
                'guide_games_manage_content': '''â€¢ Hacer clic en â­ para marcar/desmarcar como favorito
â€¢ Usar "Ver mapa" para abrir el mapa del juego
â€¢ "Editar" para modificar los datos del juego
â€¢ "Eliminar" para borrar el juego de la biblioteca''',
                
                # PestaÃ±a Mapas
                'guide_maps_title': 'ðŸ—ºï¸ ConfiguraciÃ³n de Mapas',
                'guide_maps_types_title': 'ðŸ“‹ Tipos de mapas soportados:',
                'guide_maps_image_title': 'ðŸ–¼ï¸ Mapas de Imagen:',
                'guide_maps_image_content': '''â€¢ Formatos: PNG, JPG, JPEG, BMP, GIF
â€¢ Funciones: Zoom, desplazamiento, pantalla completa
â€¢ Ideal para mapas estÃ¡ticos del juego''',
                'guide_maps_web_title': 'ðŸŒ Mapas Web (iframe):',
                'guide_maps_web_content': '''â€¢ Cualquier URL vÃ¡lida (http:// o https://)
â€¢ Mapas interactivos online
â€¢ Wikis de juegos, guÃ­as web, etc.
â€¢ Se abre en ventana integrada''',
                
                # PestaÃ±a CaracterÃ­sticas
                'guide_features_title': 'âœ¨ CaracterÃ­sticas Principales',
                'guide_features_search_title': 'ðŸ” Sistema de BÃºsqueda:',
                'guide_features_search_content': '''â€¢ Buscar por nombre de juego
â€¢ Los favoritos siempre permanecen visibles
â€¢ Filtros: "Todos" y "Favoritos"''',
                'guide_features_themes_title': 'ðŸŽ¨ Temas y PersonalizaciÃ³n:',
                'guide_features_themes_content': '''â€¢ 5 temas disponibles: Pizarra, Oscuro, Claro, Azul, Verde
â€¢ Idiomas mÃºltiples soportados
â€¢ ConfiguraciÃ³n guardada automÃ¡ticamente''',
                'guide_features_startup_title': 'ðŸš€ Inicio AutomÃ¡tico:',
                'guide_features_startup_content': '''â€¢ Configurable desde ConfiguraciÃ³n
â€¢ Inicia con Windows si estÃ¡ habilitado
â€¢ FÃ¡cil activaciÃ³n/desactivaciÃ³n''',
                
                # PestaÃ±a Consejos
                'guide_tips_title': 'ðŸ’¡ Consejos y Trucos',
                'guide_tips_organization_title': 'ðŸ“š OrganizaciÃ³n:',
                'guide_tips_organization_content': '''â€¢ Usa nombres descriptivos para tus juegos
â€¢ Marca como favoritos los juegos que mÃ¡s uses
â€¢ Organiza las imÃ¡genes por categorÃ­as''',
                'guide_tips_images_title': 'ðŸ–¼ï¸ Mejores PrÃ¡cticas para ImÃ¡genes:',
                'guide_tips_images_content': '''â€¢ Usa imÃ¡genes con buena resoluciÃ³n
â€¢ TamaÃ±o recomendado: 250x280 pÃ­xeles
â€¢ Evita imÃ¡genes muy pesadas (>5MB)''',
                'guide_tips_maps_title': 'ðŸ—ºï¸ Consejos para Mapas:',
                'guide_tips_maps_content': '''â€¢ Para mapas web, verifica que la URL sea accesible
â€¢ Los mapas de imagen grandes se pueden hacer zoom
â€¢ Usa mapas interactivos cuando sea posible''',
                
                # SubtÃ­tulo de la guÃ­a
                'guide_subtitle': 'Todo lo que necesitas saber para usar Avilon'
            },
            
            'en': {
                # Menus
                'file_menu': 'File',
                'help_menu': 'Help',
                'config_menu': 'Settings',
                'about_menu': 'About',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': 'Add Game',
                'add_game_button': '+ Add Game',
                'library': 'LIBRARY',
                'games_count': 'games',
                'game_singular': 'game',
                'no_games': 'No games in your library.\nGo to "File" â†’ "Add Game" to get started.',
                'search_placeholder': 'Search games... (favorites always visible)',
                
                # Add game form
                'add_game_title': 'Add New Game',
                'game_name': 'Game name:',
                'game_image': 'Game image:',
                'browse_image': 'Browse image',
                'map_content': 'Map path/URL:',
                'map_type_label': 'Map type:',
                'map_type_image': 'Image',
                'map_type_web': 'Website (iframe)',
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
                'spanish': 'EspaÃ±ol',
                'english': 'English',
                'french': 'FranÃ§ais',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'PortuguÃªs',
                'dutch': 'Nederlands',
                'russian': 'Ð ÑƒÑÑÐºÐ¸Ð¹',
                'japanese': 'æ—¥æœ¬èªž',
                'chinese': 'ä¸­æ–‡',
                'theme_slate': 'Slate',
                'theme_dark': 'Dark',
                'theme_light': 'Light',
                'theme_blue': 'Blue',
                'theme_green': 'Green',
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
                'guide_games_title': 'ðŸŽ® Game Management',
                'guide_games_add_title': 'ðŸ“ How to add a game:',
                'guide_games_add_content': '''1. Go to "File" â†’ "Add Game" menu
2. Fill in the game name
3. Select an image (optional):
   â€¢ Supported formats: PNG, JPG, JPEG, BMP, GIF
   â€¢ Recommended: 250x280 pixels
4. Configure the map (see "Maps" tab)
5. Click "Save"''',
                'guide_games_manage_title': 'âš™ï¸ Managing existing games:',
                'guide_games_manage_content': '''â€¢ Click on â­ to mark/unmark as favorite
â€¢ Use "View map" to open the game map
â€¢ "Edit" to modify game data
â€¢ "Delete" to remove the game from library''',
                
                # Maps tab
                'guide_maps_title': 'ðŸ—ºï¸ Map Configuration',
                'guide_maps_types_title': 'ðŸ“‹ Supported map types:',
                'guide_maps_image_title': 'ðŸ–¼ï¸ Image Maps:',
                'guide_maps_image_content': '''â€¢ Formats: PNG, JPG, JPEG, BMP, GIF
â€¢ Features: Zoom, pan, fullscreen
â€¢ Ideal for static game maps''',
                'guide_maps_web_title': 'ðŸŒ Web Maps (iframe):',
                'guide_maps_web_content': '''â€¢ Any valid URL (http:// or https://)
â€¢ Interactive online maps
â€¢ Game wikis, web guides, etc.
â€¢ Opens in integrated window''',
                
                # Features tab
                'guide_features_title': 'âœ¨ Main Features',
                'guide_features_search_title': 'ðŸ” Search System:',
                'guide_features_search_content': '''â€¢ Search by game name
â€¢ Favorites always remain visible
â€¢ Filters: "All" and "Favorites"''',
                'guide_features_themes_title': 'ðŸŽ¨ Themes and Customization:',
                'guide_features_themes_content': '''â€¢ 5 available themes: Slate, Dark, Light, Blue, Green
â€¢ Multiple language support
â€¢ Settings saved automatically''',
                'guide_features_startup_title': 'ðŸš€ Auto Start:',
                'guide_features_startup_content': '''â€¢ Configurable from Settings
â€¢ Starts with Windows if enabled
â€¢ Easy activation/deactivation''',
                
                # Tips tab
                'guide_tips_title': 'ðŸ’¡ Tips and Tricks',
                'guide_tips_organization_title': 'ðŸ“š Organization:',
                'guide_tips_organization_content': '''â€¢ Use descriptive names for your games
â€¢ Mark frequently used games as favorites
â€¢ Organize images by categories''',
                'guide_tips_images_title': 'ðŸ–¼ï¸ Best Practices for Images:',
                'guide_tips_images_content': '''â€¢ Use good resolution images
â€¢ Recommended size: 250x280 pixels
â€¢ Avoid very heavy images (>5MB)''',
                'guide_tips_maps_title': 'ðŸ—ºï¸ Map Tips:',
                'guide_tips_maps_content': '''â€¢ For web maps, verify the URL is accessible
â€¢ Large image maps can be zoomed
â€¢ Use interactive maps when possible''',
                
                # Guide subtitle
                'guide_subtitle': 'Everything you need to know about using Avilon'
            },
            
            'fr': {
                # Menus
                'file_menu': 'Fichier',
                'help_menu': 'Aide',
                'config_menu': 'ParamÃ¨tres',
                'about_menu': 'Ã€ propos',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': 'Ajouter un jeu',
                'add_game_button': '+ Ajouter un jeu',
                'library': 'BIBLIOTHÃˆQUE',
                'games_count': 'jeux',
                'game_singular': 'jeu',
                'no_games': 'Aucun jeu dans votre bibliothÃ¨que.\nAllez dans "Fichier" â†’ "Ajouter un jeu" pour commencer.',
                'search_placeholder': 'Rechercher des jeux... (favoris toujours visibles)',
                
                # Add game form
                'add_game_title': 'Ajouter un nouveau jeu',
                'game_name': 'Nom du jeu:',
                'game_image': 'Image du jeu:',
                'browse_image': 'Parcourir l\'image',
                'map_content': 'Chemin/URL de la carte:',
                'map_type_label': 'Type de carte:',
                'map_type_image': 'Image',
                'map_type_web': 'Site web (iframe)',
                'browse_map': 'Parcourir',
                'save': 'Sauvegarder',
                'cancel': 'Annuler',
                'save_changes': 'Sauvegarder les modifications',
                
                # Messages
                'error': 'Erreur',
                'success': 'SuccÃ¨s',
                'game_saved': 'Jeu sauvegardÃ© avec succÃ¨s',
                'fill_required_fields': 'Veuillez remplir tous les champs requis',
                'invalid_image': 'Format d\'image invalide',
                'invalid_url': 'URL invalide',
                'select_image': 'SÃ©lectionner une image',
                'select_map': 'SÃ©lectionner une carte',
                'image_files': 'Fichiers image',
                'all_files': 'Tous les fichiers',
                
                # About window
                'about_title': 'Ã€ propos d\'Avilon',
                'about_description': 'Avilon est un programme conÃ§u et programmÃ© par une seule personne, oÃ¹ vous pouvez gÃ©rer les cartes de vos jeux prÃ©fÃ©rÃ©s',
                'close': 'Fermer',
                
                # Configuration
                'config_title': 'ParamÃ¨tres',
                'config_subtitle': 'Personnalisez votre expÃ©rience de jeu',
                'language_label': 'Langue:',
                'theme_label': 'ThÃ¨me:',
                'spanish': 'EspaÃ±ol',
                'english': 'English',
                'french': 'FranÃ§ais',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'PortuguÃªs',
                'dutch': 'Nederlands',
                'russian': 'Ð ÑƒÑÑÐºÐ¸Ð¹',
                'japanese': 'æ—¥æœ¬èªž',
                'chinese': 'ä¸­æ–‡',
                'theme_slate': 'Ardoise',
                'theme_dark': 'Sombre',
                'theme_light': 'Clair',
                'theme_blue': 'Bleu',
                'theme_green': 'Vert',
                'apply': 'Appliquer',
                'config_saved': 'ParamÃ¨tres sauvegardÃ©s avec succÃ¨s',
                
                # Game buttons
                'view_map': 'Voir la carte',
                'edit': 'Modifier',
                'delete': 'Supprimer',
                'delete_game': 'Supprimer le jeu',
                'edit_game': 'Modifier le jeu',
                'no_image': 'Aucune image',
                'confirm_delete': 'ÃŠtes-vous sÃ»r de vouloir supprimer ce jeu?',
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
                'startup_label': 'DÃ©marrer avec Windows:',
                'startup_enabled': 'Programme configurÃ© pour dÃ©marrer avec Windows',
                'startup_disabled': 'Programme retirÃ© du dÃ©marrage automatique',
                'startup_error': 'Erreur lors de la configuration du dÃ©marrage automatique'
            },
            
            'de': {
                # Menus
                'file_menu': 'Datei',
                'help_menu': 'Hilfe',
                'config_menu': 'Einstellungen',
                'about_menu': 'Ãœber',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': 'Spiel hinzufÃ¼gen',
                'add_game_button': '+ Spiel hinzufÃ¼gen',
                'library': 'BIBLIOTHEK',
                'games_count': 'Spiele',
                'game_singular': 'Spiel',
                'no_games': 'Keine Spiele in Ihrer Bibliothek.\nGehen Sie zu "Datei" â†’ "Spiel hinzufÃ¼gen", um zu beginnen.',
                'search_placeholder': 'Spiele suchen... (Favoriten immer sichtbar)',
                
                # Add game form
                'add_game_title': 'Neues Spiel hinzufÃ¼gen',
                'game_name': 'Spielname:',
                'game_image': 'Spielbild:',
                'browse_image': 'Bild durchsuchen',
                'map_content': 'Karten-Pfad/URL:',
                'map_type_label': 'Kartentyp:',
                'map_type_image': 'Bild',
                'map_type_web': 'Webseite (iframe)',
                'browse_map': 'Durchsuchen',
                'save': 'Speichern',
                'cancel': 'Abbrechen',
                'save_changes': 'Ã„nderungen speichern',
                
                # Messages
                'error': 'Fehler',
                'success': 'Erfolg',
                'game_saved': 'Spiel erfolgreich gespeichert',
                'fill_required_fields': 'Bitte fÃ¼llen Sie alle erforderlichen Felder aus',
                'invalid_image': 'UngÃ¼ltiges Bildformat',
                'invalid_url': 'UngÃ¼ltige URL',
                'select_image': 'Bild auswÃ¤hlen',
                'select_map': 'Karte auswÃ¤hlen',
                'image_files': 'Bilddateien',
                'all_files': 'Alle Dateien',
                
                # About window
                'about_title': 'Ãœber Avilon',
                'about_description': 'Avilon ist ein Programm, das von einer einzigen Person entworfen und programmiert wurde, mit dem Sie Karten fÃ¼r Ihre Lieblingsspiele verwalten kÃ¶nnen',
                'close': 'SchlieÃŸen',
                
                # Configuration
                'config_title': 'Einstellungen',
                'config_subtitle': 'Passen Sie Ihr Spielerlebnis an',
                'language_label': 'Sprache:',
                'theme_label': 'Design:',
                'spanish': 'EspaÃ±ol',
                'english': 'English',
                'french': 'FranÃ§ais',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'PortuguÃªs',
                'dutch': 'Nederlands',
                'russian': 'Ð ÑƒÑÑÐºÐ¸Ð¹',
                'japanese': 'æ—¥æœ¬èªž',
                'chinese': 'ä¸­æ–‡',
                'theme_slate': 'Schiefer',
                'theme_dark': 'Dunkel',
                'theme_light': 'Hell',
                'theme_blue': 'Blau',
                'theme_green': 'GrÃ¼n',
                'apply': 'Anwenden',
                'config_saved': 'Einstellungen erfolgreich gespeichert',
                
                # Game buttons
                'view_map': 'Karte anzeigen',
                'edit': 'Bearbeiten',
                'delete': 'LÃ¶schen',
                'delete_game': 'Spiel lÃ¶schen',
                'edit_game': 'Spiel bearbeiten',
                'no_image': 'Kein Bild',
                'confirm_delete': 'Sind Sie sicher, dass Sie dieses Spiel lÃ¶schen mÃ¶chten?',
                'confirm_title': 'BestÃ¤tigen',
                'yes': 'Ja',
                'no': 'Nein',
                
                # Edit game
                'edit_game_title': 'Spiel bearbeiten',
                
                # Window titles
                'map_window_title': 'Karte',
                
                # Favorites system
                'all_games': 'Alle',
                'favorites': 'Favoriten',
                'add_to_favorites': 'Zu Favoriten hinzufÃ¼gen',
                'remove_from_favorites': 'Aus Favoriten entfernen',
                
                # Startup
                'startup_label': 'Mit Windows starten:',
                'startup_enabled': 'Programm zum Start mit Windows konfiguriert',
                'startup_disabled': 'Programm aus automatischem Start entfernt',
                'startup_error': 'Fehler beim Konfigurieren des automatischen Starts'
            },
            
            'it': {
                # Menus
                'file_menu': 'File',
                'help_menu': 'Aiuto',
                'config_menu': 'Impostazioni',
                'about_menu': 'Informazioni',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': 'Aggiungi gioco',
                'add_game_button': '+ Aggiungi gioco',
                'library': 'LIBRERIA',
                'games_count': 'giochi',
                'game_singular': 'gioco',
                'no_games': 'Nessun gioco nella tua libreria.\nVai su "File" â†’ "Aggiungi gioco" per iniziare.',
                'search_placeholder': 'Cerca giochi... (preferiti sempre visibili)',
                
                # Add game form
                'add_game_title': 'Aggiungi nuovo gioco',
                'game_name': 'Nome del gioco:',
                'game_image': 'Immagine del gioco:',
                'browse_image': 'Sfoglia immagine',
                'map_content': 'Percorso/URL della mappa:',
                'map_type_label': 'Tipo di mappa:',
                'map_type_image': 'Immagine',
                'map_type_web': 'Sito web (iframe)',
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
                'about_description': 'Avilon Ã¨ un programma progettato e programmato da una singola persona, dove puoi gestire le mappe dei tuoi giochi preferiti',
                'close': 'Chiudi',
                
                # Configuration
                'config_title': 'Impostazioni',
                'config_subtitle': 'Personalizza la tua esperienza di gioco',
                'language_label': 'Lingua:',
                'theme_label': 'Tema:',
                'spanish': 'EspaÃ±ol',
                'english': 'English',
                'french': 'FranÃ§ais',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'PortuguÃªs',
                'dutch': 'Nederlands',
                'russian': 'Ð ÑƒÑÑÐºÐ¸Ð¹',
                'japanese': 'æ—¥æœ¬èªž',
                'chinese': 'ä¸­æ–‡',
                'theme_slate': 'Lavagna',
                'theme_dark': 'Scuro',
                'theme_light': 'Chiaro',
                'theme_blue': 'Blu',
                'theme_green': 'Verde',
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
                'yes': 'SÃ¬',
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
                'help_menu': 'Ajuda',
                'config_menu': 'ConfiguraÃ§Ãµes',
                'about_menu': 'Sobre',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': 'Adicionar jogo',
                'add_game_button': '+ Adicionar jogo',
                'library': 'BIBLIOTECA',
                'games_count': 'jogos',
                'game_singular': 'jogo',
                'no_games': 'Nenhum jogo na sua biblioteca.\nVÃ¡ para "Arquivo" â†’ "Adicionar jogo" para comeÃ§ar.',
                'search_placeholder': 'Buscar jogos... (favoritos sempre visÃ­veis)',
                
                # Add game form
                'add_game_title': 'Adicionar novo jogo',
                'game_name': 'Nome do jogo:',
                'game_image': 'Imagem do jogo:',
                'browse_image': 'Procurar imagem',
                'map_content': 'Caminho/URL do mapa:',
                'map_type_label': 'Tipo de mapa:',
                'map_type_image': 'Imagem',
                'map_type_web': 'Site web (iframe)',
                'browse_map': 'Procurar',
                'save': 'Salvar',
                'cancel': 'Cancelar',
                'save_changes': 'Salvar alteraÃ§Ãµes',
                
                # Messages
                'error': 'Erro',
                'success': 'Sucesso',
                'game_saved': 'Jogo salvo com sucesso',
                'fill_required_fields': 'Por favor, preencha todos os campos obrigatÃ³rios',
                'invalid_image': 'Formato de imagem invÃ¡lido',
                'invalid_url': 'URL invÃ¡lida',
                'select_image': 'Selecionar imagem',
                'select_map': 'Selecionar mapa',
                'image_files': 'Arquivos de imagem',
                'all_files': 'Todos os arquivos',
                
                # About window
                'about_title': 'Sobre Avilon',
                'about_description': 'Avilon Ã© um programa projetado e programado por uma Ãºnica pessoa, onde vocÃª pode gerenciar mapas dos seus jogos favoritos',
                'close': 'Fechar',
                
                # Configuration
                'config_title': 'ConfiguraÃ§Ãµes',
                'config_subtitle': 'Personalize sua experiÃªncia de jogo',
                'language_label': 'Idioma:',
                'theme_label': 'Tema:',
                'spanish': 'EspaÃ±ol',
                'english': 'English',
                'french': 'FranÃ§ais',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'PortuguÃªs',
                'dutch': 'Nederlands',
                'russian': 'Ð ÑƒÑÑÐºÐ¸Ð¹',
                'japanese': 'æ—¥æœ¬èªž',
                'chinese': 'ä¸­æ–‡',
                'theme_slate': 'ArdÃ³sia',
                'theme_dark': 'Escuro',
                'theme_light': 'Claro',
                'theme_blue': 'Azul',
                'theme_green': 'Verde',
                'apply': 'Aplicar',
                'config_saved': 'ConfiguraÃ§Ãµes salvas com sucesso',
                
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
                'no': 'NÃ£o',
                
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
                'startup_disabled': 'Programa removido do inÃ­cio automÃ¡tico',
                'startup_error': 'Erro ao configurar o inÃ­cio automÃ¡tico'
            },
            
            'nl': {
                # Menus
                'file_menu': 'Bestand',
                'help_menu': 'Help',
                'config_menu': 'Instellingen',
                'about_menu': 'Over',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': 'Spel toevoegen',
                'add_game_button': '+ Spel toevoegen',
                'library': 'BIBLIOTHEEK',
                'games_count': 'spellen',
                'game_singular': 'spel',
                'no_games': 'Geen spellen in je bibliotheek.\nGa naar "Bestand" â†’ "Spel toevoegen" om te beginnen.',
                'search_placeholder': 'Zoek spellen... (favorieten altijd zichtbaar)',
                
                # Add game form
                'add_game_title': 'Nieuw spel toevoegen',
                'game_name': 'Spelnaam:',
                'game_image': 'Spelafbeelding:',
                'browse_image': 'Afbeelding bladeren',
                'map_content': 'Kaart pad/URL:',
                'map_type_label': 'Kaart type:',
                'map_type_image': 'Afbeelding',
                'map_type_web': 'Website (iframe)',
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
                'about_description': 'Avilon is een programma ontworpen en geprogrammeerd door Ã©Ã©n persoon, waar je kaarten voor je favoriete spellen kunt beheren',
                'close': 'Sluiten',
                
                # Configuration
                'config_title': 'Instellingen',
                'config_subtitle': 'Pas je spelervaring aan',
                'language_label': 'Taal:',
                'theme_label': 'Thema:',
                'spanish': 'EspaÃ±ol',
                'english': 'English',
                'french': 'FranÃ§ais',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'PortuguÃªs',
                'dutch': 'Nederlands',
                'russian': 'Ð ÑƒÑÑÐºÐ¸Ð¹',
                'japanese': 'æ—¥æœ¬èªž',
                'chinese': 'ä¸­æ–‡',
                'theme_slate': 'Lei',
                'theme_dark': 'Donker',
                'theme_light': 'Licht',
                'theme_blue': 'Blauw',
                'theme_green': 'Groen',
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
                'file_menu': 'Ð¤Ð°Ð¹Ð»',
                'help_menu': 'Ð¡Ð¿Ñ€Ð°Ð²ÐºÐ°',
                'config_menu': 'ÐÐ°ÑÑ‚Ñ€Ð¾Ð¹ÐºÐ¸',
                'about_menu': 'Ðž Ð¿Ñ€Ð¾Ð³Ñ€Ð°Ð¼Ð¼Ðµ',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': 'Ð”Ð¾Ð±Ð°Ð²Ð¸Ñ‚ÑŒ Ð¸Ð³Ñ€Ñƒ',
                'add_game_button': '+ Ð”Ð¾Ð±Ð°Ð²Ð¸Ñ‚ÑŒ Ð¸Ð³Ñ€Ñƒ',
                'library': 'Ð‘Ð˜Ð‘Ð›Ð˜ÐžÐ¢Ð•ÐšÐ',
                'games_count': 'Ð¸Ð³Ñ€',
                'game_singular': 'Ð¸Ð³Ñ€Ð°',
                'no_games': 'ÐÐµÑ‚ Ð¸Ð³Ñ€ Ð² Ð²Ð°ÑˆÐµÐ¹ Ð±Ð¸Ð±Ð»Ð¸Ð¾Ñ‚ÐµÐºÐµ.\nÐŸÐµÑ€ÐµÐ¹Ð´Ð¸Ñ‚Ðµ Ð² "Ð¤Ð°Ð¹Ð»" â†’ "Ð”Ð¾Ð±Ð°Ð²Ð¸Ñ‚ÑŒ Ð¸Ð³Ñ€Ñƒ", Ñ‡Ñ‚Ð¾Ð±Ñ‹ Ð½Ð°Ñ‡Ð°Ñ‚ÑŒ.',
                'search_placeholder': 'ÐŸÐ¾Ð¸ÑÐº Ð¸Ð³Ñ€... (Ð¸Ð·Ð±Ñ€Ð°Ð½Ð½Ñ‹Ðµ Ð²ÑÐµÐ³Ð´Ð° Ð²Ð¸Ð´Ð¸Ð¼Ñ‹)',
                
                # Add game form
                'add_game_title': 'Ð”Ð¾Ð±Ð°Ð²Ð¸Ñ‚ÑŒ Ð½Ð¾Ð²ÑƒÑŽ Ð¸Ð³Ñ€Ñƒ',
                'game_name': 'ÐÐ°Ð·Ð²Ð°Ð½Ð¸Ðµ Ð¸Ð³Ñ€Ñ‹:',
                'game_image': 'Ð˜Ð·Ð¾Ð±Ñ€Ð°Ð¶ÐµÐ½Ð¸Ðµ Ð¸Ð³Ñ€Ñ‹:',
                'browse_image': 'Ð’Ñ‹Ð±Ñ€Ð°Ñ‚ÑŒ Ð¸Ð·Ð¾Ð±Ñ€Ð°Ð¶ÐµÐ½Ð¸Ðµ',
                'map_content': 'ÐŸÑƒÑ‚ÑŒ/URL ÐºÐ°Ñ€Ñ‚Ñ‹:',
                'map_type_label': 'Ð¢Ð¸Ð¿ ÐºÐ°Ñ€Ñ‚Ñ‹:',
                'map_type_image': 'Ð˜Ð·Ð¾Ð±Ñ€Ð°Ð¶ÐµÐ½Ð¸Ðµ',
                'map_type_web': 'Ð’ÐµÐ±-ÑÐ°Ð¹Ñ‚ (iframe)',
                'browse_map': 'ÐžÐ±Ð·Ð¾Ñ€',
                'save': 'Ð¡Ð¾Ñ…Ñ€Ð°Ð½Ð¸Ñ‚ÑŒ',
                'cancel': 'ÐžÑ‚Ð¼ÐµÐ½Ð°',
                'save_changes': 'Ð¡Ð¾Ñ…Ñ€Ð°Ð½Ð¸Ñ‚ÑŒ Ð¸Ð·Ð¼ÐµÐ½ÐµÐ½Ð¸Ñ',
                
                # Messages
                'error': 'ÐžÑˆÐ¸Ð±ÐºÐ°',
                'success': 'Ð£ÑÐ¿ÐµÑ…',
                'game_saved': 'Ð˜Ð³Ñ€Ð° ÑƒÑÐ¿ÐµÑˆÐ½Ð¾ ÑÐ¾Ñ…Ñ€Ð°Ð½ÐµÐ½Ð°',
                'fill_required_fields': 'ÐŸÐ¾Ð¶Ð°Ð»ÑƒÐ¹ÑÑ‚Ð°, Ð·Ð°Ð¿Ð¾Ð»Ð½Ð¸Ñ‚Ðµ Ð²ÑÐµ Ð¾Ð±ÑÐ·Ð°Ñ‚ÐµÐ»ÑŒÐ½Ñ‹Ðµ Ð¿Ð¾Ð»Ñ',
                'invalid_image': 'ÐÐµÐ²ÐµÑ€Ð½Ñ‹Ð¹ Ñ„Ð¾Ñ€Ð¼Ð°Ñ‚ Ð¸Ð·Ð¾Ð±Ñ€Ð°Ð¶ÐµÐ½Ð¸Ñ',
                'invalid_url': 'ÐÐµÐ²ÐµÑ€Ð½Ñ‹Ð¹ URL',
                'select_image': 'Ð’Ñ‹Ð±Ñ€Ð°Ñ‚ÑŒ Ð¸Ð·Ð¾Ð±Ñ€Ð°Ð¶ÐµÐ½Ð¸Ðµ',
                'select_map': 'Ð’Ñ‹Ð±Ñ€Ð°Ñ‚ÑŒ ÐºÐ°Ñ€Ñ‚Ñƒ',
                'image_files': 'Ð¤Ð°Ð¹Ð»Ñ‹ Ð¸Ð·Ð¾Ð±Ñ€Ð°Ð¶ÐµÐ½Ð¸Ð¹',
                'all_files': 'Ð’ÑÐµ Ñ„Ð°Ð¹Ð»Ñ‹',
                
                # About window
                'about_title': 'Ðž Avilon',
                'about_description': 'Avilon - ÑÑ‚Ð¾ Ð¿Ñ€Ð¾Ð³Ñ€Ð°Ð¼Ð¼Ð°, Ñ€Ð°Ð·Ñ€Ð°Ð±Ð¾Ñ‚Ð°Ð½Ð½Ð°Ñ Ð¸ Ð·Ð°Ð¿Ñ€Ð¾Ð³Ñ€Ð°Ð¼Ð¼Ð¸Ñ€Ð¾Ð²Ð°Ð½Ð½Ð°Ñ Ð¾Ð´Ð½Ð¸Ð¼ Ñ‡ÐµÐ»Ð¾Ð²ÐµÐºÐ¾Ð¼, Ð³Ð´Ðµ Ð²Ñ‹ Ð¼Ð¾Ð¶ÐµÑ‚Ðµ ÑƒÐ¿Ñ€Ð°Ð²Ð»ÑÑ‚ÑŒ ÐºÐ°Ñ€Ñ‚Ð°Ð¼Ð¸ Ð²Ð°ÑˆÐ¸Ñ… Ð»ÑŽÐ±Ð¸Ð¼Ñ‹Ñ… Ð¸Ð³Ñ€',
                'close': 'Ð—Ð°ÐºÑ€Ñ‹Ñ‚ÑŒ',
                
                # Configuration
                'config_title': 'ÐÐ°ÑÑ‚Ñ€Ð¾Ð¹ÐºÐ¸',
                'config_subtitle': 'ÐÐ°ÑÑ‚Ñ€Ð¾Ð¹Ñ‚Ðµ ÑÐ²Ð¾Ð¹ Ð¸Ð³Ñ€Ð¾Ð²Ð¾Ð¹ Ð¾Ð¿Ñ‹Ñ‚',
                'language_label': 'Ð¯Ð·Ñ‹Ðº:',
                'theme_label': 'Ð¢ÐµÐ¼Ð°:',
                'spanish': 'EspaÃ±ol',
                'english': 'English',
                'french': 'FranÃ§ais',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'PortuguÃªs',
                'dutch': 'Nederlands',
                'russian': 'Ð ÑƒÑÑÐºÐ¸Ð¹',
                'japanese': 'æ—¥æœ¬èªž',
                'chinese': 'ä¸­æ–‡',
                'theme_slate': 'Ð¡Ð»Ð°Ð½ÐµÑ†',
                'theme_dark': 'Ð¢Ñ‘Ð¼Ð½Ð°Ñ',
                'theme_light': 'Ð¡Ð²ÐµÑ‚Ð»Ð°Ñ',
                'theme_blue': 'Ð¡Ð¸Ð½ÑÑ',
                'theme_green': 'Ð—ÐµÐ»Ñ‘Ð½Ð°Ñ',
                'apply': 'ÐŸÑ€Ð¸Ð¼ÐµÐ½Ð¸Ñ‚ÑŒ',
                'config_saved': 'ÐÐ°ÑÑ‚Ñ€Ð¾Ð¹ÐºÐ¸ ÑƒÑÐ¿ÐµÑˆÐ½Ð¾ ÑÐ¾Ñ…Ñ€Ð°Ð½ÐµÐ½Ñ‹',
                
                # Game buttons
                'view_map': 'ÐŸÐ¾ÑÐ¼Ð¾Ñ‚Ñ€ÐµÑ‚ÑŒ ÐºÐ°Ñ€Ñ‚Ñƒ',
                'edit': 'Ð ÐµÐ´Ð°ÐºÑ‚Ð¸Ñ€Ð¾Ð²Ð°Ñ‚ÑŒ',
                'delete': 'Ð£Ð´Ð°Ð»Ð¸Ñ‚ÑŒ',
                'delete_game': 'Ð£Ð´Ð°Ð»Ð¸Ñ‚ÑŒ Ð¸Ð³Ñ€Ñƒ',
                'edit_game': 'Ð ÐµÐ´Ð°ÐºÑ‚Ð¸Ñ€Ð¾Ð²Ð°Ñ‚ÑŒ Ð¸Ð³Ñ€Ñƒ',
                'no_image': 'ÐÐµÑ‚ Ð¸Ð·Ð¾Ð±Ñ€Ð°Ð¶ÐµÐ½Ð¸Ñ',
                'confirm_delete': 'Ð’Ñ‹ ÑƒÐ²ÐµÑ€ÐµÐ½Ñ‹, Ñ‡Ñ‚Ð¾ Ñ…Ð¾Ñ‚Ð¸Ñ‚Ðµ ÑƒÐ´Ð°Ð»Ð¸Ñ‚ÑŒ ÑÑ‚Ñƒ Ð¸Ð³Ñ€Ñƒ?',
                'confirm_title': 'ÐŸÐ¾Ð´Ñ‚Ð²ÐµÑ€Ð´Ð¸Ñ‚ÑŒ',
                'yes': 'Ð”Ð°',
                'no': 'ÐÐµÑ‚',
                
                # Edit game
                'edit_game_title': 'Ð ÐµÐ´Ð°ÐºÑ‚Ð¸Ñ€Ð¾Ð²Ð°Ñ‚ÑŒ Ð¸Ð³Ñ€Ñƒ',
                
                # Window titles
                'map_window_title': 'ÐšÐ°Ñ€Ñ‚Ð°',
                
                # Favorites system
                'all_games': 'Ð’ÑÐµ',
                'favorites': 'Ð˜Ð·Ð±Ñ€Ð°Ð½Ð½Ñ‹Ðµ',
                'add_to_favorites': 'Ð”Ð¾Ð±Ð°Ð²Ð¸Ñ‚ÑŒ Ð² Ð¸Ð·Ð±Ñ€Ð°Ð½Ð½Ð¾Ðµ',
                'remove_from_favorites': 'Ð£Ð´Ð°Ð»Ð¸Ñ‚ÑŒ Ð¸Ð· Ð¸Ð·Ð±Ñ€Ð°Ð½Ð½Ð¾Ð³Ð¾',
                
                # Startup
                'startup_label': 'Ð—Ð°Ð¿ÑƒÑÐº Ñ Windows:',
                'startup_enabled': 'ÐŸÑ€Ð¾Ð³Ñ€Ð°Ð¼Ð¼Ð° Ð½Ð°ÑÑ‚Ñ€Ð¾ÐµÐ½Ð° Ð´Ð»Ñ Ð·Ð°Ð¿ÑƒÑÐºÐ° Ñ Windows',
                'startup_disabled': 'ÐŸÑ€Ð¾Ð³Ñ€Ð°Ð¼Ð¼Ð° ÑƒÐ´Ð°Ð»ÐµÐ½Ð° Ð¸Ð· Ð°Ð²Ñ‚Ð¾Ð·Ð°Ð¿ÑƒÑÐºÐ°',
                'startup_error': 'ÐžÑˆÐ¸Ð±ÐºÐ° Ð½Ð°ÑÑ‚Ñ€Ð¾Ð¹ÐºÐ¸ Ð°Ð²Ñ‚Ð¾Ð·Ð°Ð¿ÑƒÑÐºÐ°'
            },
            
            'ja': {
                # Menus
                'file_menu': 'ãƒ•ã‚¡ã‚¤ãƒ«',
                'help_menu': 'ãƒ˜ãƒ«ãƒ—',
                'config_menu': 'è¨­å®š',
                'about_menu': 'ã«ã¤ã„ã¦',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': 'ã‚²ãƒ¼ãƒ ã‚’è¿½åŠ ',
                'add_game_button': '+ ã‚²ãƒ¼ãƒ ã‚’è¿½åŠ ',
                'library': 'ãƒ©ã‚¤ãƒ–ãƒ©ãƒª',
                'games_count': 'ã‚²ãƒ¼ãƒ ',
                'game_singular': 'ã‚²ãƒ¼ãƒ ',
                'no_games': 'ãƒ©ã‚¤ãƒ–ãƒ©ãƒªã«ã‚²ãƒ¼ãƒ ãŒã‚ã‚Šã¾ã›ã‚“ã€‚\nã€Œãƒ•ã‚¡ã‚¤ãƒ«ã€â†’ã€Œã‚²ãƒ¼ãƒ ã‚’è¿½åŠ ã€ã‹ã‚‰å§‹ã‚ã¦ãã ã•ã„ã€‚',
                'search_placeholder': 'ã‚²ãƒ¼ãƒ ã‚’æ¤œç´¢... (ãŠæ°—ã«å…¥ã‚Šã¯å¸¸ã«è¡¨ç¤º)',
                
                # Add game form
                'add_game_title': 'æ–°ã—ã„ã‚²ãƒ¼ãƒ ã‚’è¿½åŠ ',
                'game_name': 'ã‚²ãƒ¼ãƒ å:',
                'game_image': 'ã‚²ãƒ¼ãƒ ç”»åƒ:',
                'browse_image': 'ç”»åƒã‚’å‚ç…§',
                'map_content': 'ãƒžãƒƒãƒ—ãƒ‘ã‚¹/URL:',
                'map_type_label': 'ãƒžãƒƒãƒ—ã‚¿ã‚¤ãƒ—:',
                'map_type_image': 'ç”»åƒ',
                'map_type_web': 'ã‚¦ã‚§ãƒ–ã‚µã‚¤ãƒˆ (iframe)',
                'browse_map': 'å‚ç…§',
                'save': 'ä¿å­˜',
                'cancel': 'ã‚­ãƒ£ãƒ³ã‚»ãƒ«',
                'save_changes': 'å¤‰æ›´ã‚’ä¿å­˜',
                
                # Messages
                'error': 'ã‚¨ãƒ©ãƒ¼',
                'success': 'æˆåŠŸ',
                'game_saved': 'ã‚²ãƒ¼ãƒ ãŒæ­£å¸¸ã«ä¿å­˜ã•ã‚Œã¾ã—ãŸ',
                'fill_required_fields': 'å¿…é ˆé …ç›®ã‚’ã™ã¹ã¦å…¥åŠ›ã—ã¦ãã ã•ã„',
                'invalid_image': 'ç„¡åŠ¹ãªç”»åƒå½¢å¼',
                'invalid_url': 'ç„¡åŠ¹ãªURL',
                'select_image': 'ç”»åƒã‚’é¸æŠž',
                'select_map': 'ãƒžãƒƒãƒ—ã‚’é¸æŠž',
                'image_files': 'ç”»åƒãƒ•ã‚¡ã‚¤ãƒ«',
                'all_files': 'ã™ã¹ã¦ã®ãƒ•ã‚¡ã‚¤ãƒ«',
                
                # About window
                'about_title': 'Avilonã«ã¤ã„ã¦',
                'about_description': 'Avilonã¯ä¸€äººã§è¨­è¨ˆãƒ»ãƒ—ãƒ­ã‚°ãƒ©ãƒ ã•ã‚ŒãŸãƒ—ãƒ­ã‚°ãƒ©ãƒ ã§ã€ãŠæ°—ã«å…¥ã‚Šã®ã‚²ãƒ¼ãƒ ã®ãƒžãƒƒãƒ—ã‚’ç®¡ç†ã§ãã¾ã™',
                'close': 'é–‰ã˜ã‚‹',
                
                # Configuration
                'config_title': 'è¨­å®š',
                'config_subtitle': 'ã‚²ãƒ¼ãƒ ä½“é¨“ã‚’ã‚«ã‚¹ã‚¿ãƒžã‚¤ã‚º',
                'language_label': 'è¨€èªž:',
                'theme_label': 'ãƒ†ãƒ¼ãƒž:',
                'spanish': 'EspaÃ±ol',
                'english': 'English',
                'french': 'FranÃ§ais',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'PortuguÃªs',
                'dutch': 'Nederlands',
                'russian': 'Ð ÑƒÑÑÐºÐ¸Ð¹',
                'japanese': 'æ—¥æœ¬èªž',
                'chinese': 'ä¸­æ–‡',
                'theme_slate': 'ã‚¹ãƒ¬ãƒ¼ãƒˆ',
                'theme_dark': 'ãƒ€ãƒ¼ã‚¯',
                'theme_light': 'ãƒ©ã‚¤ãƒˆ',
                'theme_blue': 'ãƒ–ãƒ«ãƒ¼',
                'theme_green': 'ã‚°ãƒªãƒ¼ãƒ³',
                'apply': 'é©ç”¨',
                'config_saved': 'è¨­å®šãŒæ­£å¸¸ã«ä¿å­˜ã•ã‚Œã¾ã—ãŸ',
                
                # Game buttons
                'view_map': 'ãƒžãƒƒãƒ—ã‚’è¡¨ç¤º',
                'edit': 'ç·¨é›†',
                'delete': 'å‰Šé™¤',
                'delete_game': 'ã‚²ãƒ¼ãƒ ã‚’å‰Šé™¤',
                'edit_game': 'ã‚²ãƒ¼ãƒ ã‚’ç·¨é›†',
                'no_image': 'ç”»åƒãªã—',
                'confirm_delete': 'ã“ã®ã‚²ãƒ¼ãƒ ã‚’å‰Šé™¤ã—ã¦ã‚‚ã‚ˆã‚ã—ã„ã§ã™ã‹ï¼Ÿ',
                'confirm_title': 'ç¢ºèª',
                'yes': 'ã¯ã„',
                'no': 'ã„ã„ãˆ',
                
                # Edit game
                'edit_game_title': 'ã‚²ãƒ¼ãƒ ã‚’ç·¨é›†',
                
                # Window titles
                'map_window_title': 'ãƒžãƒƒãƒ—',
                
                # Favorites system
                'all_games': 'ã™ã¹ã¦',
                'favorites': 'ãŠæ°—ã«å…¥ã‚Š',
                'add_to_favorites': 'ãŠæ°—ã«å…¥ã‚Šã«è¿½åŠ ',
                'remove_from_favorites': 'ãŠæ°—ã«å…¥ã‚Šã‹ã‚‰å‰Šé™¤',
                
                # Startup
                'startup_label': 'Windowsã¨ä¸€ç·’ã«èµ·å‹•:',
                'startup_enabled': 'ãƒ—ãƒ­ã‚°ãƒ©ãƒ ãŒWindowsã¨ä¸€ç·’ã«èµ·å‹•ã™ã‚‹ã‚ˆã†è¨­å®šã•ã‚Œã¾ã—ãŸ',
                'startup_disabled': 'ãƒ—ãƒ­ã‚°ãƒ©ãƒ ãŒè‡ªå‹•èµ·å‹•ã‹ã‚‰å‰Šé™¤ã•ã‚Œã¾ã—ãŸ',
                'startup_error': 'è‡ªå‹•èµ·å‹•ã®è¨­å®šã§ã‚¨ãƒ©ãƒ¼ãŒç™ºç”Ÿã—ã¾ã—ãŸ'
            },
            
            'zh': {
                # Menus
                'file_menu': 'æ–‡ä»¶',
                'help_menu': 'å¸®åŠ©',
                'config_menu': 'è®¾ç½®',
                'about_menu': 'å…³äºŽ',
                
                # Main window
                'window_title': 'Avilon',
                'add_game': 'æ·»åŠ æ¸¸æˆ',
                'add_game_button': '+ æ·»åŠ æ¸¸æˆ',
                'library': 'æ¸¸æˆåº“',
                'games_count': 'æ¸¸æˆ',
                'game_singular': 'æ¸¸æˆ',
                'no_games': 'æ‚¨çš„æ¸¸æˆåº“ä¸­æ²¡æœ‰æ¸¸æˆã€‚\nè¯·å‰å¾€"æ–‡ä»¶"â†’"æ·»åŠ æ¸¸æˆ"å¼€å§‹ã€‚',
                'search_placeholder': 'æœç´¢æ¸¸æˆ... (æ”¶è—å¤¹å§‹ç»ˆå¯è§)',
                
                # Add game form
                'add_game_title': 'æ·»åŠ æ–°æ¸¸æˆ',
                'game_name': 'æ¸¸æˆåç§°:',
                'game_image': 'æ¸¸æˆå›¾åƒ:',
                'browse_image': 'æµè§ˆå›¾åƒ',
                'map_content': 'åœ°å›¾è·¯å¾„/URL:',
                'map_type_label': 'åœ°å›¾ç±»åž‹:',
                'map_type_image': 'å›¾åƒ',
                'map_type_web': 'ç½‘ç«™ (iframe)',
                'browse_map': 'æµè§ˆ',
                'save': 'ä¿å­˜',
                'cancel': 'å–æ¶ˆ',
                'save_changes': 'ä¿å­˜æ›´æ”¹',
                
                # Messages
                'error': 'é”™è¯¯',
                'success': 'æˆåŠŸ',
                'game_saved': 'æ¸¸æˆä¿å­˜æˆåŠŸ',
                'fill_required_fields': 'è¯·å¡«å†™æ‰€æœ‰å¿…å¡«å­—æ®µ',
                'invalid_image': 'æ— æ•ˆçš„å›¾åƒæ ¼å¼',
                'invalid_url': 'æ— æ•ˆçš„URL',
                'select_image': 'é€‰æ‹©å›¾åƒ',
                'select_map': 'é€‰æ‹©åœ°å›¾',
                'image_files': 'å›¾åƒæ–‡ä»¶',
                'all_files': 'æ‰€æœ‰æ–‡ä»¶',
                
                # About window
                'about_title': 'å…³äºŽAvilon',
                'about_description': 'Avilonæ˜¯ä¸€ä¸ªç”±å•äººè®¾è®¡å’Œç¼–ç¨‹çš„ç¨‹åºï¼Œæ‚¨å¯ä»¥åœ¨å…¶ä¸­ç®¡ç†æ‚¨æœ€å–œæ¬¢çš„æ¸¸æˆåœ°å›¾',
                'close': 'å…³é—­',
                
                # Configuration
                'config_title': 'è®¾ç½®',
                'config_subtitle': 'è‡ªå®šä¹‰æ‚¨çš„æ¸¸æˆä½“éªŒ',
                'language_label': 'è¯­è¨€:',
                'theme_label': 'ä¸»é¢˜:',
                'spanish': 'EspaÃ±ol',
                'english': 'English',
                'french': 'FranÃ§ais',
                'german': 'Deutsch',
                'italian': 'Italiano',
                'portuguese': 'PortuguÃªs',
                'dutch': 'Nederlands',
                'russian': 'Ð ÑƒÑÑÐºÐ¸Ð¹',
                'japanese': 'æ—¥æœ¬èªž',
                'chinese': 'ä¸­æ–‡',
                'theme_slate': 'æ¿å²©',
                'theme_dark': 'æ·±è‰²',
                'theme_light': 'æµ…è‰²',
                'theme_blue': 'è“è‰²',
                'theme_green': 'ç»¿è‰²',
                'apply': 'åº”ç”¨',
                'config_saved': 'è®¾ç½®ä¿å­˜æˆåŠŸ',
                
                # Game buttons
                'view_map': 'æŸ¥çœ‹åœ°å›¾',
                'edit': 'ç¼–è¾‘',
                'delete': 'åˆ é™¤',
                'delete_game': 'åˆ é™¤æ¸¸æˆ',
                'edit_game': 'ç¼–è¾‘æ¸¸æˆ',
                'no_image': 'æ— å›¾åƒ',
                'confirm_delete': 'æ‚¨ç¡®å®šè¦åˆ é™¤è¿™ä¸ªæ¸¸æˆå—ï¼Ÿ',
                'confirm_title': 'ç¡®è®¤',
                'yes': 'æ˜¯',
                'no': 'å¦',
                
                # Edit game
                'edit_game_title': 'ç¼–è¾‘æ¸¸æˆ',
                
                # Window titles
                'map_window_title': 'åœ°å›¾',
                
                # Favorites system
                'all_games': 'å…¨éƒ¨',
                'favorites': 'æ”¶è—å¤¹',
                'add_to_favorites': 'æ·»åŠ åˆ°æ”¶è—å¤¹',
                'remove_from_favorites': 'ä»Žæ”¶è—å¤¹ä¸­åˆ é™¤',
                
                # Startup
                'startup_label': 'éšWindowså¯åŠ¨:',
                'startup_enabled': 'ç¨‹åºå·²é…ç½®ä¸ºéšWindowså¯åŠ¨',
                'startup_disabled': 'ç¨‹åºå·²ä»Žè‡ªåŠ¨å¯åŠ¨ä¸­åˆ é™¤',
                'startup_error': 'é…ç½®è‡ªåŠ¨å¯åŠ¨æ—¶å‡ºé”™'
            }
        }
    
    def load_config(self):
        """Cargar configuraciÃ³n desde archivo"""
        try:
            import json
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config
        except:
            return {'language': 'es', 'theme': 'slate', 'startup': False}  # ConfiguraciÃ³n por defecto
    
    def save_config(self):
        """Guardar configuraciÃ³n a archivo"""
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
        # Asegurar que las traducciones estÃ©n cargadas
        if not hasattr(self, 'translations') or not self.translations:
            self.translations = self.load_translations()
        
        translation = self.translations.get(self.current_language, {}).get(key, None)
        
        # Si no se encuentra la traducciÃ³n, intentar con el idioma por defecto
        if translation is None:
            translation = self.translations.get('es', {}).get(key, key)
        
        return translation
    
    def set_startup_registry(self, enable):
        """Configurar inicio automÃ¡tico en el registro de Windows"""
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "Avilon"
        
        try:
            # Obtener la ruta del ejecutable actual
            if getattr(sys, 'frozen', False):
                # Si es un .exe compilado
                app_path = sys.executable
            else:
                # Si es un script de Python
                app_path = f'python "{os.path.abspath(__file__)}"'
            
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
            print(f"Error al configurar inicio automÃ¡tico: {e}")
            return False
        finally:
            try:
                winreg.CloseKey(key)
            except:
                pass
    
    def check_startup_status(self):
        """Verificar si el programa estÃ¡ configurado para iniciar con Windows"""
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "Avilon"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            try:
                value, _ = winreg.QueryValueEx(key, app_name)
                return True
            except FileNotFoundError:
                return False
        except Exception as e:
            print(f"Error al verificar estado de inicio automÃ¡tico: {e}")
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
            }
        }
    
    def create_menu_bar(self):
        """Crear barra de menÃº"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # MenÃº Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.get_text('file_menu'), menu=file_menu)
        file_menu.add_command(label=self.get_text('add_game'), command=self.show_add_game_dialog)
        file_menu.add_command(label=self.get_text('config_menu'), command=self.show_config_dialog)
        
        # MenÃº Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.get_text('help_menu'), menu=help_menu)
        help_menu.add_command(label=self.get_text('how_to_use_menu'), command=self.show_user_guide_dialog)
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
        
        # TÃ­tulo
        title_label = ttk.Label(main_frame, 
                               text="Avilon", 
                               style='Dark.TLabel',
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # DescripciÃ³n
        description_label = ttk.Label(main_frame,
                                     text=self.get_text('about_description'),
                                     style='Dark.TLabel',
                                     font=('Arial', 10),
                                     wraplength=350,
                                     justify='center')
        description_label.pack(pady=(0, 10))
        
        # VersiÃ³n
        version_label = ttk.Label(main_frame,
                                 text="VersiÃ³n 1.5.0",
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
            # Si PIL no estÃ¡ disponible, intentar con el mÃ©todo nativo de Tkinter
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
                                    text="ðŸŽ®",
                                    bg=self.colors['bg_dark'],
                                    fg=self.colors['text'],
                                    font=('Arial', 24))
                logo_text.pack(pady=(5, 15))
        except:
            # Si hay cualquier otro error al cargar el logo
            logo_text = tk.Label(main_frame,
                                text="ðŸŽ®",
                                bg=self.colors['bg_dark'],
                                fg=self.colors['text'],
                                font=('Arial', 24))
            logo_text.pack(pady=(5, 15))
        
        # Centrar la ventana en la pantalla
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() - about_window.winfo_width()) // 2
        y = (about_window.winfo_screenheight() - about_window.winfo_height()) // 2
        about_window.geometry(f"+{x}+{y}")
        
        # Mostrar la ventana una vez que estÃ¡ completamente configurada
        about_window.deiconify()
    
    def show_user_guide_dialog(self):
        """Mostrar ventana de GuÃ­a de Usuario con diseÃ±o ultra moderno"""
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
        
        # Importar el mÃ³dulo ttk para las pestaÃ±as
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
            # Crear un gradiente mÃ¡s sofisticado
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
        # CÃ­rculos decorativos con transparencia
        for x, y, size, alpha in [(150, 30, 40, 0.1), (850, 40, 60, 0.08), (750, 80, 30, 0.12)]:
            color = self.blend_colors('#ffffff', self.colors['accent'], alpha)
            header_canvas.create_oval(x, y, x+size, y+size, fill=color, outline='')
        
        # Icono principal del header
        header_canvas.create_text(80, 60, text="ðŸ“š", font=('Segoe UI Emoji', 32), fill='white')
        
        # TÃ­tulo principal del header con sombra
        # Sombra del texto
        header_canvas.create_text(502, 47, text=self.get_text('user_guide_title'),
                                 fill='#000000', font=('Segoe UI', 24, 'bold'), anchor='center')
        # Texto principal
        header_canvas.create_text(500, 45, text=self.get_text('user_guide_title'),
                                 fill='white', font=('Segoe UI', 24, 'bold'), anchor='center')
        
        # SubtÃ­tulo estilizado
        header_canvas.create_text(500, 75, text=self.get_text('guide_subtitle'),
                                 fill='#e5e7eb', font=('Segoe UI', 12), anchor='center')
        
        # LÃ­nea decorativa
        header_canvas.create_line(350, 95, 650, 95, fill='#ffffff', width=2)
        
        # Frame contenedor principal con padding mejorado
        main_container = tk.Frame(guide_window, bg=self.colors['bg_dark'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(15, 20))
        
        # Crear el Notebook con estilo personalizado sin afectar el tema global
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Guardar el tema actual para restaurarlo despuÃ©s
        style = ttk.Style()
        original_theme = style.theme_use()
        
        # Configurar estilos Ãºnicos solo para esta ventana
        try:
            # Crear estilos Ãºnicos que no interfieran con los existentes
            style.configure('GuideWindow.TNotebook', 
                           background=self.colors['bg_dark'], 
                           borderwidth=0,
                           tabmargins=[0, 0, 0, 0])
            
            # Estilo Ãºnico para las pestaÃ±as de la guÃ­a
            style.configure('GuideWindow.TNotebook.Tab',
                           padding=[30, 15],
                           font=('Segoe UI', 11, 'bold'),
                           focuscolor='none',
                           background=self.colors['bg_medium'],
                           foreground=self.colors['text_secondary'],
                           borderwidth=0,
                           relief='flat')
            
            # Mapeo de estados para pestaÃ±as de la guÃ­a
            style.map('GuideWindow.TNotebook.Tab',
                     background=[('selected', self.colors['accent']),
                               ('active', self.colors['bg_light'])],
                     foreground=[('selected', 'white'),
                               ('active', self.colors['text'])])
            
            notebook.configure(style='GuideWindow.TNotebook')
            
        except Exception as e:
            # Si hay error con los estilos, usar el notebook bÃ¡sico
            print(f"Warning: Could not apply custom styles: {e}")
        
        # FunciÃ³n para restaurar tema cuando se cierre la ventana
        def on_guide_window_close():
            try:
                # Restaurar el tema original
                style.theme_use(original_theme)
            except:
                pass
            guide_window.destroy()
        
        guide_window.protocol("WM_DELETE_WINDOW", on_guide_window_close)
        
        # Crear las pestaÃ±as con iconos mejorados
        games_frame = tk.Frame(notebook, bg=self.colors['bg_dark'])
        notebook.add(games_frame, text="ðŸŽ®  " + self.get_text('guide_tab_games').upper())
        
        maps_frame = tk.Frame(notebook, bg=self.colors['bg_dark'])
        notebook.add(maps_frame, text="ðŸ—ºï¸  " + self.get_text('guide_tab_maps').upper())
        
        features_frame = tk.Frame(notebook, bg=self.colors['bg_dark'])
        notebook.add(features_frame, text="âœ¨  " + self.get_text('guide_tab_features').upper())
        
        tips_frame = tk.Frame(notebook, bg=self.colors['bg_dark'])
        notebook.add(tips_frame, text="ðŸ’¡  " + self.get_text('guide_tab_tips').upper())
        
        # Crear contenido moderno para cada pestaÃ±a
        self.create_modern_guide_games_tab(games_frame)
        self.create_modern_guide_maps_tab(maps_frame)
        self.create_modern_guide_features_tab(features_frame)
        self.create_modern_guide_tips_tab(tips_frame)
        
        # Agregar animaciÃ³n de entrada
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
        """AnimaciÃ³n de entrada suave para la ventana de guÃ­a"""
        def animate_scale(scale=0.95):
            if scale <= 1.0:
                # No hay una forma directa de escalar en tkinter, asÃ­ que usamos el efecto de transparencia
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
        """Crear una tarjeta moderna e interactiva para la guÃ­a"""
        if icon_bg is None:
            icon_bg = self.colors['accent']
        
        # Frame contenedor principal con margen
        container_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        container_frame.pack(fill=tk.X, padx=25, pady=15)
        
        # Frame principal de la tarjeta sin canvas - mÃ¡s simple y funcional
        card_frame = tk.Frame(container_frame, bg=self.colors['bg_medium'], relief='solid', bd=1)
        card_frame.pack(fill=tk.X, pady=5)
        
        # Configurar borde sutil
        border_color = self.blend_colors(self.colors['accent'], self.colors['bg_medium'], 0.3)
        card_frame.configure(highlightbackground=border_color, highlightthickness=1, bd=0)
        
        # Padding interno
        inner_frame = tk.Frame(card_frame, bg=self.colors['bg_medium'])
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Header con icono y tÃ­tulo
        header_frame = tk.Frame(inner_frame, bg=self.colors['bg_medium'])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Icono con efecto visual
        icon_frame = tk.Frame(header_frame, bg=self.colors['bg_medium'])
        icon_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        # Canvas solo para el icono (mÃ¡s pequeÃ±o y controlado)
        icon_canvas = tk.Canvas(icon_frame, width=60, height=60, bg=self.colors['bg_medium'], 
                               highlightthickness=0, bd=0)
        icon_canvas.pack()
        
        # Efecto glow para el icono
        glow_color = self.blend_colors(icon_bg, self.colors['bg_medium'], 0.3)
        icon_canvas.create_oval(5, 5, 55, 55, fill=glow_color, outline='', width=0)
        icon_canvas.create_oval(8, 8, 52, 52, fill=icon_bg, outline='', width=0)
        icon_canvas.create_text(30, 30, text=icon, fill='white', font=('Segoe UI Emoji', 20, 'bold'))
        
        # Ãrea de texto
        text_frame = tk.Frame(header_frame, bg=self.colors['bg_medium'])
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # TÃ­tulo principal
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
                              height=4,  # Altura en lÃ­neas
                              cursor='arrow',
                              selectbackground=self.colors['accent'],
                              selectforeground='white')
        content_text.pack(fill=tk.BOTH, expand=True)
        content_text.insert('1.0', content)
        content_text.config(state='disabled')  # Solo lectura
        
        # BotÃ³n de acciÃ³n opcional
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
            
            # Efectos hover para el botÃ³n
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
        
        # FunciÃ³n recursiva para aplicar hover a todos los widgets hijos
        def bind_hover_events(widget):
            widget.bind('<Enter>', on_card_enter)
            widget.bind('<Leave>', on_card_leave)
            for child in widget.winfo_children():
                if child != content_text:  # No aplicar a content_text para evitar interferir con la selecciÃ³n
                    bind_hover_events(child)
        
        bind_hover_events(card_frame)
        
        return card_frame
    
    def create_professional_card(self, parent, icon, title, content, icon_bg=None):
        """Crear una tarjeta profesional para la guÃ­a"""
        if icon_bg is None:
            icon_bg = self.colors['accent']
            
        # Frame principal de la tarjeta
        card_frame = tk.Frame(parent, bg=self.colors['bg_medium'], relief='flat', bd=0)
        card_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Crear efecto de sombra/elevaciÃ³n
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
        
        # Dibujar cÃ­rculo de fondo para el icono
        icon_canvas.create_oval(5, 5, 45, 45, fill=icon_bg, outline='', width=0)
        icon_canvas.create_text(25, 25, text=icon, fill='white', font=('Segoe UI', 18, 'bold'))
        
        # TÃ­tulo de la tarjeta
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
        """Crear el contenido profesional de la pestaÃ±a Juegos"""
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
        
        # TÃ­tulo con descripciÃ³n
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
            "ðŸ“",
            self.get_text('guide_games_add_title'),
            self.get_text('guide_games_add_content'),
            '#4f46e5'  # Color azul
        )
        
        # Tarjeta: Gestionar juegos
        self.create_professional_card(
            scrollable_frame,
            "âš™ï¸",
            self.get_text('guide_games_manage_title'),
            self.get_text('guide_games_manage_content'),
            '#059669'  # Color verde
        )
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratÃ³n - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el Ã¡rbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # TambiÃ©n bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_guide_maps_tab_professional(self, parent):
        """Crear el contenido profesional de la pestaÃ±a Mapas"""
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
        
        # TÃ­tulo con descripciÃ³n
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=20, padx=30)
        
        intro_text = tk.Label(intro_frame,
                             text="Configura mapas de imagen y web para tener acceso rÃ¡pido a la informaciÃ³n de tus juegos",
                             bg=self.colors['bg_dark'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 12),
                             wraplength=800)
        intro_text.pack()
        
        # Tarjeta: Mapas de imagen
        self.create_professional_card(
            scrollable_frame,
            "ðŸ–¼ï¸",
            self.get_text('guide_maps_image_title'),
            self.get_text('guide_maps_image_content'),
            '#dc2626'  # Color rojo
        )
        
        # Tarjeta: Mapas web
        self.create_professional_card(
            scrollable_frame,
            "ðŸŒ",
            self.get_text('guide_maps_web_title'),
            self.get_text('guide_maps_web_content'),
            '#2563eb'  # Color azul fuerte
        )
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratÃ³n - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el Ã¡rbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # TambiÃ©n bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_guide_features_tab_professional(self, parent):
        """Crear el contenido profesional de la pestaÃ±a CaracterÃ­sticas"""
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
        
        # TÃ­tulo con descripciÃ³n
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=20, padx=30)
        
        intro_text = tk.Label(intro_frame,
                             text="Descubre todas las caracterÃ­sticas que hacen de Avilon una herramienta potente y personalizable",
                             bg=self.colors['bg_dark'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 12),
                             wraplength=800)
        intro_text.pack()
        
        # Tarjeta: Sistema de bÃºsqueda
        self.create_professional_card(
            scrollable_frame,
            "ðŸ”",
            self.get_text('guide_features_search_title'),
            self.get_text('guide_features_search_content'),
            '#7c3aed'  # Color pÃºrpura
        )
        
        # Tarjeta: Temas y personalizaciÃ³n
        self.create_professional_card(
            scrollable_frame,
            "ðŸŽ¨",
            self.get_text('guide_features_themes_title'),
            self.get_text('guide_features_themes_content'),
            '#ea580c'  # Color naranja
        )
        
        # Tarjeta: Inicio automÃ¡tico
        self.create_professional_card(
            scrollable_frame,
            "ðŸš€",
            self.get_text('guide_features_startup_title'),
            self.get_text('guide_features_startup_content'),
            '#0891b2'  # Color cyan
        )
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratÃ³n - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el Ã¡rbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # TambiÃ©n bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_guide_tips_tab_professional(self, parent):
        """Crear el contenido profesional de la pestaÃ±a Consejos"""
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
        
        # TÃ­tulo con descripciÃ³n
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=20, padx=30)
        
        intro_text = tk.Label(intro_frame,
                             text="Consejos prÃ¡cticos para aprovechar al mÃ¡ximo Avilon y optimizar tu experiencia",
                             bg=self.colors['bg_dark'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 12),
                             wraplength=800)
        intro_text.pack()
        
        # Tarjeta: OrganizaciÃ³n
        self.create_professional_card(
            scrollable_frame,
            "ðŸ“š",
            self.get_text('guide_tips_organization_title'),
            self.get_text('guide_tips_organization_content'),
            '#16a34a'  # Color verde claro
        )
        
        # Tarjeta: Mejores prÃ¡cticas para imÃ¡genes
        self.create_professional_card(
            scrollable_frame,
            "ðŸ–¼ï¸",
            self.get_text('guide_tips_images_title'),
            self.get_text('guide_tips_images_content'),
            '#c026d3'  # Color magenta
        )
        
        # Tarjeta: Consejos para mapas
        self.create_professional_card(
            scrollable_frame,
            "ðŸ—ºï¸",
            self.get_text('guide_tips_maps_title'),
            self.get_text('guide_tips_maps_content'),
            '#0369a1'  # Color azul oscuro
        )
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratÃ³n - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el Ã¡rbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # TambiÃ©n bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_guide_games_tab(self, parent):
        """Crear el contenido de la pestaÃ±a Juegos"""
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
        
        # TÃ­tulo principal
        title_label = ttk.Label(scrollable_frame, 
                               text=self.get_text('guide_games_title'),
                               style='Dark.TLabel',
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(10, 20), padx=20, anchor='w')
        
        # SecciÃ³n: Agregar juegos
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
        
        # SecciÃ³n: Gestionar juegos
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
        
        # Configurar scroll con rueda del ratÃ³n - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el Ã¡rbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # TambiÃ©n bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_guide_maps_tab(self, parent):
        """Crear el contenido de la pestaÃ±a Mapas"""
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
        
        # TÃ­tulo principal
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
        
        # Configurar scroll con rueda del ratÃ³n - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el Ã¡rbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # TambiÃ©n bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_guide_features_tab(self, parent):
        """Crear el contenido de la pestaÃ±a CaracterÃ­sticas"""
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
        
        # TÃ­tulo principal
        title_label = ttk.Label(scrollable_frame, 
                               text=self.get_text('guide_features_title'),
                               style='Dark.TLabel',
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(10, 20), padx=20, anchor='w')
        
        # Sistema de bÃºsqueda
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
        
        # Inicio automÃ¡tico
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
        
        # Configurar scroll con rueda del ratÃ³n - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el Ã¡rbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # TambiÃ©n bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_guide_tips_tab(self, parent):
        """Crear el contenido de la pestaÃ±a Consejos"""
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
        
        # TÃ­tulo principal
        title_label = ttk.Label(scrollable_frame, 
                               text=self.get_text('guide_tips_title'),
                               style='Dark.TLabel',
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(10, 20), padx=20, anchor='w')
        
        # OrganizaciÃ³n
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
        
        # ImÃ¡genes
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
        
        # Configurar scroll con rueda del ratÃ³n - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el Ã¡rbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # TambiÃ©n bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_modern_guide_games_tab(self, parent):
        """Crear el contenido moderno de la pestaÃ±a Juegos"""
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
        
        # Header de introducciÃ³n moderno
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=(30, 40), padx=30)
        
        intro_title = tk.Label(intro_frame,
                              text="ðŸŽ® " + self.get_text('guide_games_title'),
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
            "âž•",
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
            "ðŸ“š",
            self.get_text('guide_games_manage_title'),
            self.get_text('guide_games_manage_content'),
            '#3b82f6',  # Azul moderno
        )
        
        # Tarjeta: GestiÃ³n avanzada - usando contenido existente
        self.create_modern_card(
            scrollable_frame,
            "âš™ï¸",
            self.get_text('guide_features_title'),
            self.get_text('guide_features_search_content'),
            '#8b5cf6',  # PÃºrpura moderno
        )
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratÃ³n - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el Ã¡rbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # TambiÃ©n bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_modern_guide_maps_tab(self, parent):
        """Crear el contenido moderno de la pestaÃ±a Mapas"""
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
        
        # Header de introducciÃ³n
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=(30, 40), padx=30)
        
        intro_title = tk.Label(intro_frame,
                              text="ðŸ—ºï¸ " + self.get_text('guide_maps_title'),
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
            "ðŸ–¼ï¸",
            self.get_text('guide_maps_image_title'),
            self.get_text('guide_maps_image_content'),
            '#f59e0b',  # Ãmbar
        )
        
        # Tarjeta: Mapas web
        self.create_modern_card(
            scrollable_frame,
            "ðŸŒ",
            self.get_text('guide_maps_web_title'),
            self.get_text('guide_maps_web_content'),
            '#ef4444',  # Rojo moderno
        )
        
        # Tarjeta: Consejos para mapas
        self.create_modern_card(
            scrollable_frame,
            "ðŸ”",
            self.get_text('guide_tips_maps_title'),
            self.get_text('guide_tips_maps_content'),
            '#06b6d4',  # Cian
        )
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratÃ³n - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el Ã¡rbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # TambiÃ©n bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_modern_guide_features_tab(self, parent):
        """Crear el contenido moderno de la pestaÃ±a CaracterÃ­sticas"""
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
        
        # Header de introducciÃ³n
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=(30, 40), padx=30)
        
        intro_title = tk.Label(intro_frame,
                              text="âœ¨ " + self.get_text('guide_features_title'),
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
        
        # Tarjeta: Sistema de bÃºsqueda
        self.create_modern_card(
            scrollable_frame,
            "ðŸ”",
            self.get_text('guide_features_search_title'),
            self.get_text('guide_features_search_content'),
            '#8b5cf6',  # PÃºrpura
        )
        
        # Tarjeta: Temas personalizables
        self.create_modern_card(
            scrollable_frame,
            "ðŸŽ¨",
            self.get_text('guide_features_themes_title'),
            self.get_text('guide_features_themes_content'),
            '#10b981',  # Verde
            {
                'text': self.get_text('config_button'),
                'command': self.show_config_dialog
            }
        )
        
        # Tarjeta: Consejos para imÃ¡genes
        self.create_modern_card(
            scrollable_frame,
            "ðŸ–¼ï¸",
            self.get_text('guide_tips_images_title'),
            self.get_text('guide_tips_images_content'),
            '#f59e0b',  # Ãmbar
        )
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratÃ³n - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el Ã¡rbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # TambiÃ©n bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_modern_guide_tips_tab(self, parent):
        """Crear el contenido moderno de la pestaÃ±a Consejos"""
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
        
        # Header de introducciÃ³n
        intro_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
        intro_frame.pack(fill=tk.X, pady=(30, 40), padx=30)
        
        intro_title = tk.Label(intro_frame,
                              text="ðŸ’¡ " + self.get_text('guide_tips_title'),
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
        
        # Tarjeta: OrganizaciÃ³n eficiente
        self.create_modern_card(
            scrollable_frame,
            "ðŸ“‹",
            self.get_text('guide_tips_organization_title'),
            self.get_text('guide_tips_organization_content'),
            '#3b82f6',  # Azul
        )
        
        # Tarjeta: Mejores prÃ¡cticas para imÃ¡genes
        self.create_modern_card(
            scrollable_frame,
            "ðŸ–¼ï¸",
            self.get_text('guide_tips_images_title'),
            self.get_text('guide_tips_images_content'),
            '#ef4444',  # Rojo
        )
        
        # Tarjeta: Consejos para mapas
        self.create_modern_card(
            scrollable_frame,
            "ðŸ—ºï¸",
            self.get_text('guide_tips_maps_title'),
            self.get_text('guide_tips_maps_content'),
            '#10b981',  # Verde
        )
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del ratÃ³n - sistema mejorado
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Sistema de scroll mejorado - bind directo al canvas y sus hijos
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Aplicar scroll a todo el Ã¡rbol de widgets
        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable_frame)
        
        # TambiÃ©n bind directo al canvas principal
        canvas.bind("<MouseWheel>", _on_mousewheel)

    def show_config_dialog(self):
        """Mostrar ventana de configuraciÃ³n con diseÃ±o profesional"""
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
        
        # Header con tÃ­tulo y subtÃ­tulo
        header_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # TÃ­tulo principal
        title_label = tk.Label(header_frame, 
                              text=self.get_text('config_title'), 
                              bg=self.colors['bg_dark'],
                              fg=self.colors['text_primary'],
                              font=('Segoe UI', 18, 'bold'))
        title_label.pack(anchor='center')
        
        # SubtÃ­tulo
        subtitle_label = tk.Label(header_frame, 
                                 text=self.get_text('config_subtitle'), 
                                 bg=self.colors['bg_dark'],
                                 fg=self.colors['text_secondary'],
                                 font=('Segoe UI', 10))
        subtitle_label.pack(anchor='center', pady=(5, 0))
        
        # Separador
        separator1 = tk.Frame(main_frame, bg=self.colors['accent'], height=2)
        separator1.pack(fill=tk.X, pady=(0, 25))
        
        # === SECCIÃ“N DE IDIOMA ===
        self.create_config_section(main_frame, "ðŸŒ", self.get_text('language_label'), 
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
        
        # Variable para almacenar solo el cÃ³digo del idioma
        self.temp_language = tk.StringVar(value=self.current_language)
        
        language_combo = ttk.Combobox(language_card,
                                     state='readonly',
                                     width=25,
                                     font=('Segoe UI', 10))
        
        # Configurar valores y selecciÃ³n actual
        lang_display_values = {lang[0]: lang[1] for lang in languages}
        language_combo['values'] = list(lang_display_values.values())
        language_combo.set(lang_display_values.get(self.current_language, self.get_text('spanish')))
        
        # Manejar cambio de selecciÃ³n de idioma
        def on_language_change(event):
            selected_display = language_combo.get()
            for code, display in lang_display_values.items():
                if display == selected_display:
                    self.temp_language.set(code)
                    break
        
        language_combo.bind('<<ComboboxSelected>>', on_language_change)
        language_combo.pack(pady=10)
        
        # === SECCIÃ“N DE TEMA ===
        self.create_config_section(main_frame, "ðŸŽ¨", self.get_text('theme_label'), 
                                  "Elige el tema visual de la aplicaciÃ³n")
        
        theme_card = self.create_config_card(main_frame)
        
        # Combobox para seleccionar tema
        themes = [
            ('slate', self.get_text('theme_slate')),
            ('dark', self.get_text('theme_dark')),
            ('light', self.get_text('theme_light')),
            ('blue', self.get_text('theme_blue')),
            ('green', self.get_text('theme_green'))
        ]
        
        # Variable para almacenar solo el cÃ³digo del tema
        self.temp_theme = tk.StringVar(value=self.current_theme)
        
        theme_combo = ttk.Combobox(theme_card,
                                  state='readonly',
                                  width=25,
                                  font=('Segoe UI', 10))
        
        # Configurar valores y selecciÃ³n actual
        theme_display_values = {theme[0]: theme[1] for theme in themes}
        theme_combo['values'] = list(theme_display_values.values())
        theme_combo.set(theme_display_values.get(self.current_theme, self.get_text('theme_slate')))
        
        # Manejar cambio de selecciÃ³n de tema
        def on_theme_change(event):
            selected_display = theme_combo.get()
            for code, display in theme_display_values.items():
                if display == selected_display:
                    self.temp_theme.set(code)
                    break
        
        theme_combo.bind('<<ComboboxSelected>>', on_theme_change)
        theme_combo.pack(pady=10)
        
        # === SECCIÃ“N DE INICIO AUTOMÃTICO ===
        self.create_config_section(main_frame, "ðŸš€", self.get_text('startup_label'), 
                                  "Inicia Avilon automÃ¡ticamente con Windows")
        
        startup_card = self.create_config_card(main_frame)
        
        # Variable para el checkbox del inicio automÃ¡tico
        actual_startup_status = self.check_startup_status()
        self.temp_startup = tk.BooleanVar(value=actual_startup_status)
        
        # CHECKBOX con diseÃ±o integrado
        startup_checkbox = tk.Checkbutton(startup_card,
                                         text=" âœ“ Iniciar automÃ¡ticamente con Windows",
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
        
        # === ÃREA DE BOTONES REDISEÃ‘ADA ===
        
        # Frame principal para botones con el mismo fondo que la ventana
        button_area = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        button_area.pack(fill=tk.X, pady=(25, 30))
        
        # Frame interno para botones
        button_container = tk.Frame(button_area, bg=self.colors['bg_dark'])
        button_container.pack(pady=15, padx=20)
        
        # BOTÃ“N CANCELAR - mÃ¡s pequeÃ±o
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
        
        # BOTÃ“N GUARDAR CAMBIOS - mÃ¡s pequeÃ±o
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
               
        # Efectos hover para los botones rediseÃ±ados
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
        
        # Mostrar la ventana una vez que estÃ¡ completamente configurada
        config_window.deiconify()
    
    def create_config_section(self, parent, icon, title, description):
        """Crear una secciÃ³n de configuraciÃ³n con tÃ­tulo e icono"""
        section_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Frame para el tÃ­tulo con icono
        title_frame = tk.Frame(section_frame, bg=self.colors['bg_dark'])
        title_frame.pack(fill=tk.X)
        
        # Icono
        icon_label = tk.Label(title_frame,
                             text=icon,
                             bg=self.colors['bg_dark'],
                             fg=self.colors['accent'],
                             font=('Segoe UI', 16))
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Contenedor para tÃ­tulo y descripciÃ³n
        text_frame = tk.Frame(title_frame, bg=self.colors['bg_dark'])
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # TÃ­tulo
        title_label = tk.Label(text_frame,
                              text=title,
                              bg=self.colors['bg_dark'],
                              fg=self.colors['text_primary'],
                              font=('Segoe UI', 12, 'bold'))
        title_label.pack(anchor='w')
        
        # DescripciÃ³n
        desc_label = tk.Label(text_frame,
                             text=description,
                             bg=self.colors['bg_dark'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 9))
        desc_label.pack(anchor='w')
        
        return section_frame
    
    def create_config_card(self, parent):
        """Crear una tarjeta de configuraciÃ³n estilizada"""
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
        
        # Programar el binding despuÃ©s de que se agreguen los widgets hijos
        card_frame.after(1, lambda: bind_hover_to_children(card_frame))
        
        return card_frame
    
    def apply_config_changes(self, config_window, language_combo=None, theme_combo=None, 
                           lang_display_values=None, theme_display_values=None,
                           title_label=None, subtitle_label=None, save_btn=None, cancel_btn=None):
        """Aplicar cambios de configuraciÃ³n"""
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
            self.current_theme = new_theme
            changes_made = True
        
        # Manejar cambios en el inicio automÃ¡tico
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
            
            # Si cambiÃ³ el idioma, actualizar la ventana de configuraciÃ³n primero
            if language_changed and title_label and subtitle_label and save_btn and cancel_btn:
                # Actualizar tÃ­tulo de la ventana
                config_window.title(self.get_text('config_title'))
                
                # Actualizar etiquetas principales
                title_label.configure(text=self.get_text('config_title'))
                subtitle_label.configure(text=self.get_text('config_subtitle'))
                
                # Actualizar botones
                save_btn.configure(text=self.get_text('save_changes'))
                cancel_btn.configure(text=self.get_text('cancel'))
                
                # Actualizar comboboxes si estÃ¡n disponibles
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
            
            # Preparar mensaje de confirmaciÃ³n
            config_message = self.get_text('config_saved')
            if startup_message:
                config_message += f"\n{startup_message}"
            
            # Mostrar mensaje de confirmaciÃ³n
            import tkinter.messagebox as messagebox
            messagebox.showinfo(self.get_text('success'), config_message)
            
            # Cerrar ventana de configuraciÃ³n solo despuÃ©s de actualizar todo
            config_window.destroy()
            
            # Si no hubo cambio de idioma, actualizar la interfaz
            if not language_changed:
                self.refresh_interface()
        else:
            # Si solo se cambiÃ³ el inicio automÃ¡tico sin otros cambios
            if startup_message:
                import tkinter.messagebox as messagebox
                messagebox.showinfo(self.get_text('success'), startup_message)
            config_window.destroy()
    
    def refresh_interface(self):
        """Actualizar toda la interfaz con el nuevo idioma y tema"""
        # Recargar traducciones por si cambiÃ³ el idioma
        self.translations = self.load_translations()
        
        # Reconfigurar estilos con el nuevo tema
        self.setup_styles()
        
        # Actualizar color de fondo de la ventana principal
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Actualizar tÃ­tulo de la ventana con el nuevo idioma
        self.root.title(self.get_text('window_title'))
        
        # Limpiar la barra de menÃº actual
        self.root.config(menu="")
        
        # Recrear la barra de menÃº con las nuevas traducciones
        self.create_menu_bar()
        
        # Actualizar la interfaz principal
        # Destruir y recrear los elementos principales
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.destroy()
        
        # Recrear la interfaz
        self.create_main_interface()
        self.refresh_games_display()
        
        # Actualizar colores de la barra de bÃºsqueda despuÃ©s de recrear la interfaz
        self.root.after(100, self.update_search_bar_colors)
    
    def create_main_interface(self):
        """Crear la interfaz principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Ãrea de contenido principal (sin sidebar)
        self.create_content_area(main_frame)
    

    
    def create_content_area(self, parent):
        """Crear Ã¡rea de contenido principal"""
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
        
        # Barra de bÃºsqueda en la esquina superior derecha
        self.create_search_bar(top_frame)
        
        # TÃ­tulo AVILON centrado en su propia lÃ­nea
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
        
        # BotÃ³n "Todos" con contador
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
        
        # BotÃ³n "Favoritos" con contador  
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
        """Crear barra de bÃºsqueda mejorada con efectos y transiciones"""
        # Variable para el texto de bÃºsqueda
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        # Container principal alineado a la derecha en el top_frame
        container = ttk.Frame(parent, style='Dark.TFrame')
        container.pack(side=tk.RIGHT, padx=(0, 10), pady=(5, 0))  # Alineado a la derecha del top_frame
        
        # Frame de la barra de bÃºsqueda con efectos visuales usando colores del tema
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
        
        # Ãcono de bÃºsqueda animado
        self.search_icon = tk.Label(inner_frame, 
                                   text="ðŸ”",
                                   bg=self.colors['bg_light'],
                                   fg=self.colors['text_muted'],
                                   font=('Segoe UI', 11))
        self.search_icon.pack(side=tk.LEFT, padx=(0, 6))
        
        # Campo de entrada con estilo mejorado usando colores del tema
        # Configurar colores especÃ­ficos para cada tema con mejor contraste
        if self.current_theme == 'light':
            entry_bg = '#ffffff'
            entry_fg = '#333333'
            insert_color = '#333333'
            select_bg = '#0078d4'
            select_fg = '#ffffff'
        elif self.current_theme == 'slate':
            entry_bg = '#484c52'  # Fondo mÃ¡s claro que el tema para mejor contraste
            entry_fg = '#ffffff'  # Texto blanco
            insert_color = '#ffffff'  # Cursor blanco
            select_bg = '#7289da'
            select_fg = '#ffffff'
        elif self.current_theme == 'dark':
            entry_bg = '#505050'  # Fondo mÃ¡s claro que el tema para mejor contraste
            entry_fg = '#ffffff'  # Texto blanco
            insert_color = '#ffffff'  # Cursor blanco
            select_bg = '#4a9eff'
            select_fg = '#ffffff'
        elif self.current_theme == 'blue':
            entry_bg = '#4f7bc7'  # Fondo mÃ¡s claro que el tema
            entry_fg = '#ffffff'
            insert_color = '#ffffff'
            select_bg = '#60a5fa'
            select_fg = '#ffffff'
        elif self.current_theme == 'green':
            entry_bg = '#0d8f6b'  # Fondo mÃ¡s claro que el tema
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
        
        # BotÃ³n limpiar con efectos hover usando colores del tema
        self.clear_button = tk.Button(inner_frame,
                                     text="âœ—",
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
        
        # Actualizar visualizaciÃ³n de juegos
        self.refresh_games_display()
    
    def update_search_bar_colors(self):
        """Actualizar colores de la barra de bÃºsqueda segÃºn el tema actual"""
        if hasattr(self, 'search_entry') and self.search_entry.winfo_exists():
            # Configurar colores especÃ­ficos para cada tema con mejor contraste
            if self.current_theme == 'light':
                entry_bg = '#ffffff'
                entry_fg = '#333333'
                insert_color = '#333333'
                select_bg = '#0078d4'
                select_fg = '#ffffff'
            elif self.current_theme == 'slate':
                entry_bg = '#484c52'  # Fondo mÃ¡s claro que el tema para mejor contraste
                entry_fg = '#ffffff'  # Texto blanco
                insert_color = '#ffffff'  # Cursor blanco
                select_bg = '#7289da'
                select_fg = '#ffffff'
            elif self.current_theme == 'dark':
                entry_bg = '#505050'  # Fondo mÃ¡s claro que el tema para mejor contraste
                entry_fg = '#ffffff'  # Texto blanco
                insert_color = '#ffffff'  # Cursor blanco
                select_bg = '#4a9eff'
                select_fg = '#ffffff'
            elif self.current_theme == 'blue':
                entry_bg = '#4f7bc7'  # Fondo mÃ¡s claro que el tema
                entry_fg = '#ffffff'
                insert_color = '#ffffff'
                select_bg = '#60a5fa'
                select_fg = '#ffffff'
            elif self.current_theme == 'green':
                entry_bg = '#0d8f6b'  # Fondo mÃ¡s claro que el tema
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
            
            # Actualizar tambiÃ©n los colores del frame de la barra de bÃºsqueda
            if hasattr(self, 'search_bar_frame') and self.search_bar_frame.winfo_exists():
                self.search_bar_frame.configure(
                    bg=self.colors['bg_light'],
                    highlightcolor=self.colors['accent'],
                    highlightbackground=self.colors['bg_dark']
                )
            
            # Actualizar Ã­cono de bÃºsqueda
            if hasattr(self, 'search_icon') and self.search_icon.winfo_exists():
                self.search_icon.configure(
                    bg=self.colors['bg_light'],
                    fg=self.colors['text_muted']
                )
            
            # Actualizar botÃ³n de limpiar
            if hasattr(self, 'clear_button') and self.clear_button.winfo_exists():
                self.clear_button.configure(
                    bg=self.colors['bg_light'],
                    fg=self.colors['text_muted']
                )
    
    def setup_search_effects(self):
        """Configurar efectos visuales para la barra de bÃºsqueda"""
        # Efectos de hover para el frame de bÃºsqueda
        def on_search_hover_enter(event):
            self.search_bar_frame.config(highlightcolor=self.colors['accent'], highlightbackground=self.colors['accent'])
            self.animate_search_icon('ðŸ”', self.colors['accent'])
            
        def on_search_hover_leave(event):
            if self.search_entry != self.root.focus_get():
                self.search_bar_frame.config(highlightcolor=self.colors['bg_dark'], highlightbackground=self.colors['bg_dark'])
                self.animate_search_icon('ðŸ”', self.colors['text_muted'])
        
        # Efectos de focus
        def on_search_focus_enter(event):
            self.search_bar_frame.config(highlightcolor=self.colors['accent'], highlightbackground=self.colors['accent'])
            self.animate_search_icon('ðŸ”', self.colors['accent'])
            self.on_search_focus_in(event)
            
        def on_search_focus_leave(event):
            self.search_bar_frame.config(highlightcolor=self.colors['bg_dark'], highlightbackground=self.colors['bg_dark'])
            self.animate_search_icon('ðŸ”', self.colors['text_muted'])
            self.on_search_focus_out(event)
        
        # Efectos para el botÃ³n limpiar
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
                # No bloquear el evento, permitir que el carÃ¡cter se escriba
                return None
            elif event.keysym == 'BackSpace' and not self.is_placeholder_active:
                # Si se borra todo el contenido, podrÃ­amos restaurar placeholder despuÃ©s
                self.root.after(1, self.check_empty_field)
                
        def on_key_release(event):
            # Verificar si el campo estÃ¡ vacÃ­o despuÃ©s de una pulsaciÃ³n de tecla
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
        
        # Efecto de pulsaciÃ³n suave en Enter
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
        """Restaurar el placeholder cuando el campo estÃ© vacÃ­o"""
        if not self.is_placeholder_active and not self.search_entry.get().strip():
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, self.placeholder_text)
            self.search_entry.config(fg=self.colors['text_muted'])
            self.is_placeholder_active = True
    
    def check_empty_field(self):
        """Verificar si el campo estÃ¡ vacÃ­o y restaurar placeholder si es necesario"""
        if not self.is_placeholder_active and not self.search_entry.get().strip():
            # Solo restaurar placeholder si el campo no tiene foco
            if self.search_entry != self.root.focus_get():
                self.restore_placeholder()
    
    def animate_search_icon(self, icon, color):
        """Animar el Ã­cono de bÃºsqueda con transiciÃ³n de color"""
        try:
            self.search_icon.config(fg=color)
            # Efecto de pulsaciÃ³n sutil
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
        """Crear efecto de pulsaciÃ³n en la barra de bÃºsqueda"""
        original_bg = self.search_bar_frame.cget('highlightbackground')
        
        # Secuencia de colores para el efecto de pulsaciÃ³n usando el color de acento del tema
        accent_color = self.colors['accent']
        colors = [accent_color, accent_color, accent_color, original_bg, original_bg]
        
        def pulse_step(step=0):
            if step < len(colors):
                self.search_bar_frame.config(highlightcolor=colors[step], highlightbackground=colors[step])
                self.root.after(50, lambda: pulse_step(step + 1))
        
        pulse_step()
    
    def on_search_focus_in(self, event):
        """Manejar cuando el campo de bÃºsqueda recibe el foco con efectos"""
        self.search_focused = True
    # Solo eliminar placeholder si estÃ¡ activo, pero no automÃ¡ticamente
        # Esperar a que el usuario empiece a escribir
        
            
    def on_search_focus_out(self, event):
        """Manejar cuando el campo de bÃºsqueda pierde el foco con efectos"""
        self.search_focused = False
        
        # Restaurar placeholder si el campo estÃ¡ vacÃ­o
        if not self.is_placeholder_active and not self.search_entry.get().strip():
            # AnimaciÃ³n de apariciÃ³n del placeholder
            self.animate_placeholder_fade_in()
            self.restore_placeholder()
    
    def clear_search(self):
        """Limpiar la bÃºsqueda con efectos de animaciÃ³n"""
        # Efecto de pulsaciÃ³n en el botÃ³n
        self.animate_clear_button_press()
        
        # Limpiar el contenido
        self.search_var.set('')
        self.search_entry.delete(0, tk.END)
        
        # Restaurar placeholder con animaciÃ³n
        self.animate_placeholder_fade_in()
        self.restore_placeholder()
        
        # Actualizar la vista de juegos para mostrar todos
        self.refresh_games_display()
        
        # Focus en el campo con efecto
        self.search_entry.focus()
        self.animate_search_pulse()
    
    def animate_placeholder_fade_out(self):
        """Animar desapariciÃ³n del placeholder"""
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
        """Animar apariciÃ³n del placeholder"""
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
        """Animar pulsaciÃ³n del botÃ³n limpiar"""
        original_bg = self.clear_button.cget('bg')
        
        # Secuencia de colores para simular pulsaciÃ³n
        self.clear_button.config(bg='#ff4444', fg='white')
        self.root.after(100, lambda: self.clear_button.config(bg='#ff6666'))
        self.root.after(200, lambda: self.clear_button.config(bg=original_bg, fg='#888888'))
    
    def on_search_change(self, *args):
        """Manejar cambios en el texto de bÃºsqueda con efectos mejorados"""
        search_text = self.search_var.get()
        
        # Si hay placeholder activo, ignorar cambios hasta que se escriba algo real
        if self.is_placeholder_active:
            return
            
        # Solo procesar bÃºsquedas reales
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
            # Brillo sutil en el Ã­cono mientras se escribe
            self.search_icon.config(fg='#00ccff')
            self.root.after(300, lambda: self.search_icon.config(fg='#00aaff' if self.search_focused else '#888888'))
        except:
            pass
    
    def create_scrollable_games_area(self, parent):
        """Crear Ã¡rea scrollable para los juegos"""
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
        # Obtener color hover dinÃ¡mico
        if self.current_theme == 'light':
            hover_color = '#e8e8e8'
        else:
            hover_color = '#4f545c'
            
        # Configurar eventos hover para el frame y todos sus hijos
        def on_enter(event):
            # Cambiar color de fondo del frame al hacer hover
            card_frame.configure(style='GameHover.TFrame')
            # Cambiar tambiÃ©n el fondo del nombre para que coincida
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
        # Colores hover mÃ¡s sutiles y elegantes
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
            
            # Efecto sutil en la sombra (mÃ¡s discreto)
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
        
        # TambiÃ©n aplicar a la imagen si existe
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
        """Mostrar diÃ¡logo para aÃ±adir juego"""
        dialog = tk.Toplevel(self.root)
        dialog.title(self.get_text('add_game_title'))
        dialog.geometry("600x550")  # MÃ¡s grande para mejor visualizaciÃ³n
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)  # Evitar redimensionado
        self.apply_window_icon(dialog)
        
        # Centrar diÃ¡logo
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
        """Crear formulario para aÃ±adir juego"""
        # Frame principal del formulario
        form_frame = ttk.Frame(parent, style='Dark.TFrame')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # TÃ­tulo
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
        
        # Agregar funcionalidad de Enter para guardar
        def on_enter_key(event):
            self.save_game(parent)
        
        # Binding del evento Enter al diálogo
        parent.bind('<Return>', on_enter_key)
        parent.focus_set()  # Asegurar que el diálogo tenga foco
    
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
        """Validar que el archivo sea una imagen vÃ¡lida"""
        if not file_path:
            return False, "No se ha seleccionado ningÃºn archivo"
        
        if not os.path.exists(file_path):
            return False, "El archivo no existe"
        
        # Verificar extensiÃ³n
        valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in valid_extensions:
            return False, f"Formato de imagen no vÃ¡lido. Use: {', '.join(valid_extensions)}"
        
        # Intentar abrir la imagen para verificar que es vÃ¡lida
        try:
            with Image.open(file_path) as img:
                img.verify()  # Verificar que la imagen no estÃ© corrupta
            return True, "Imagen vÃ¡lida"
        except Exception as e:
            return False, f"La imagen estÃ¡ corrupta o no es vÃ¡lida: {str(e)}"
    
    def copy_image_to_local(self, source_path, game_name, image_type="game"):
        """Copiar imagen al directorio local del programa"""
        if not source_path or not os.path.exists(source_path):
            return None
        
        try:
            # Obtener extensiÃ³n original
            file_ext = os.path.splitext(source_path)[1].lower()
            
            # Crear nombre Ãºnico para evitar conflictos
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
        """Crear imagen por defecto profesional con gradientes y diseÃ±o moderno"""
        try:
            # Crear imagen con gradiente elegante segÃºn el tema
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
                
                # Dibujar Ã­cono de juego grande centrado
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
                    # Intentar fuentes mÃ¡s modernas
                    font_title = ImageFont.truetype("segoeui.ttf", 14)
                    font_subtitle = ImageFont.truetype("segoeui.ttf", 10)
                except:
                    try:
                        font_title = ImageFont.truetype("arial.ttf", 14)
                        font_subtitle = ImageFont.truetype("arial.ttf", 10)
                    except:
                        font_title = ImageFont.load_default()
                        font_subtitle = ImageFont.load_default()
                
                # TÃ­tulo principal
                title_bbox = draw.textbbox((0, 0), text, font=font_title)
                title_width = title_bbox[2] - title_bbox[0]
                title_x = (width - title_width) // 2
                title_y = icon_y + icon_size + 20
                
                draw.text((title_x, title_y), text, fill=text_color, font=font_title)
                
                # SubtÃ­tulo
                subtitle = "ðŸŽ® Imagen no disponible"
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
                # Fallback si PIL no estÃ¡ completo
            
                pass
            
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error creando imagen por defecto: {str(e)}")
            return None
    
    def cleanup_unused_images(self):
        """Limpiar imÃ¡genes no utilizadas del directorio local"""
        if not os.path.exists(self.images_dir):
            return
        
        try:
            # Obtener todas las rutas de imÃ¡genes utilizadas actualmente
            used_images = set()
            for game in self.games:
                image_path = game.get('image_path', '')
                map_content = game.get('map_content', '')
                
                # Agregar imagen del juego si estÃ¡ en el directorio local
                if image_path and image_path.startswith(self.images_dir):
                    used_images.add(os.path.basename(image_path))
                
                # Agregar imagen del mapa si es de tipo imagen y estÃ¡ en el directorio local
                if (game.get('map_type') == 'image' and map_content and 
                    map_content.startswith(self.images_dir)):
                    used_images.add(os.path.basename(map_content))
            
            # Obtener todas las imÃ¡genes en el directorio local
            local_images = set()
            for filename in os.listdir(self.images_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    local_images.add(filename)
            
            # Eliminar imÃ¡genes no utilizadas
            unused_images = local_images - used_images
            for unused_image in unused_images:
                unused_path = os.path.join(self.images_dir, unused_image)
                try:
                    os.remove(unused_path)
                    print(f"Imagen no utilizada eliminada: {unused_image}")
                except Exception as e:
                    print(f"Error eliminando imagen {unused_image}: {str(e)}")
                    
        except Exception as e:
            print(f"Error durante la limpieza de imÃ¡genes: {str(e)}")
    
    def migrate_existing_games(self):
        """Migrar juegos existentes para usar el directorio local de imÃ¡genes"""
        changes_made = False
        
        for i, game in enumerate(self.games):
            try:
                # Migrar imagen del juego si no estÃ¡ en el directorio local
                image_path = game.get('image_path', '')
                if image_path and not image_path.startswith(self.images_dir) and os.path.exists(image_path):
                    new_image_path = self.copy_image_to_local(image_path, game['name'], "game")
                    if new_image_path and new_image_path != image_path:
                        self.games[i]['image_path'] = new_image_path
                        changes_made = True
                        print(f"Migrada imagen del juego '{game['name']}'")
                
                # Migrar imagen del mapa si es de tipo imagen y no estÃ¡ en el directorio local
                map_content = game.get('map_content', '')
                if (game.get('map_type') == 'image' and map_content and 
                    not map_content.startswith(self.images_dir) and os.path.exists(map_content)):
                    new_map_path = self.copy_image_to_local(map_content, game['name'], "map")
                    if new_map_path and new_map_path != map_content:
                        self.games[i]['map_content'] = new_map_path
                        changes_made = True
                        print(f"Migrada imagen del mapa del juego '{game['name']}'")
                
                # AÃ±adir campo favorite si no existe
                if 'favorite' not in game:
                    self.games[i]['favorite'] = False
                    changes_made = True
                        
            except Exception as e:
                print(f"Error migrando juego '{game.get('name', 'Sin nombre')}': {str(e)}")
        
        # Guardar cambios si se hicieron migraciones
        if changes_made:
            self.save_games()
            print("MigraciÃ³n completada")
    
    def validate_url(self, url):
        """Validar que la URL sea vÃ¡lida"""
        if not url:
            return False, "No se ha introducido ninguna URL"
        
        # Verificar que empiece con http:// o https://
        if not url.startswith(('http://', 'https://')):
            return False, "La URL debe comenzar con http:// o https://"
        
        # Validar formato bÃ¡sico de URL
        try:
            result = urllib.parse.urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False, "Formato de URL no vÃ¡lido"
            return True, "URL vÃ¡lida"
        except Exception as e:
            return False, f"URL no vÃ¡lida: {str(e)}"
    
    def save_game(self, dialog):
        """Guardar juego nuevo con validaciones mejoradas"""
        name = self.game_name_var.get().strip()
        image_path = self.game_image_path.get().strip()
        map_type = self.map_type_var.get()
        map_content = self.map_content_var.get().strip()
        
        # ValidaciÃ³n del nombre
        if not name:
            messagebox.showerror("Campo obligatorio", "El nombre del juego es obligatorio")
            return
        
        if len(name) < 2:
            messagebox.showerror("Nombre invÃ¡lido", "El nombre del juego debe tener al menos 2 caracteres")
            return
        
        # ValidaciÃ³n de la imagen del juego
        if not image_path:
            messagebox.showerror("Campo obligatorio", "Debe seleccionar una imagen para el juego")
            return
        
        is_valid_image, image_message = self.validate_image_file(image_path)
        if not is_valid_image:
            messagebox.showerror("Imagen invÃ¡lida", f"Error en la imagen del juego:\n{image_message}")
            return
        
        # ValidaciÃ³n del contenido del mapa
        if not map_content:
            messagebox.showerror("Campo obligatorio", "Debe especificar el contenido del mapa")
            return
        
        if map_type == "image":
            # Validar imagen del mapa
            is_valid_map_image, map_image_message = self.validate_image_file(map_content)
            if not is_valid_map_image:
                messagebox.showerror("Imagen del mapa invÃ¡lida", f"Error en la imagen del mapa:\n{map_image_message}")
                return
        else:
            # Validar URL del iframe
            is_valid_url, url_message = self.validate_url(map_content)
            if not is_valid_url:
                messagebox.showerror("URL invÃ¡lida", f"Error en la URL del mapa:\n{url_message}")
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
        
        # AÃ±adir a la lista
        self.games.append(game)
        
        # Guardar en archivo
        self.save_games()
        
        # Actualizar interfaz
        self.refresh_games_display()
        
        # Cerrar diÃ¡logo
        dialog.destroy()
        
        messagebox.showinfo(self.get_text('success'), self.get_text('game_saved'))
    
    def refresh_games_display(self):
        """Actualizar la visualizaciÃ³n de juegos"""
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
                message = "No se encontraron juegos que coincidan con la bÃºsqueda"
            
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
        
        # Calcular columnas dinÃ¡micamente basado en el ancho de la ventana
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
            
            # Aplicar bÃºsqueda dentro de favoritos si hay texto
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
        
        # Si hay bÃºsqueda activa
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
                
                # Orden: Favoritos que coinciden â†’ Favoritos que no coinciden â†’ No-favoritos que coinciden
                return matching_favorites + non_matching_favorites + matching_non_favorites
        
        # Sin bÃºsqueda: Favoritos primero, luego el resto
        return favorites + non_favorites
    
    def create_game_card(self, parent, game, row, col):
        """Crear tarjeta de juego con diseÃ±o profesional y moderno"""
        # Frame principal con efecto de elevaciÃ³n
        main_container = tk.Frame(parent, bg=self.colors['bg_dark'])
        main_container.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
        # Frame de sombra para efecto de profundidad
        shadow_frame = tk.Frame(main_container, 
                               bg=self.card_shadow_color,
                               height=2)
        shadow_frame.pack(side='bottom', fill='x')
        
        # Frame principal de la tarjeta con mejor diseÃ±o
        card_frame = ttk.Frame(main_container, style='Game.TFrame')
        card_frame.pack(fill='both', expand=True)
        
        # Header de la tarjeta con tÃ­tulo y favorito
        header_frame = tk.Frame(card_frame, bg=self.colors['bg_light'], height=45)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Nombre del juego con mejor tipografÃ­a
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
        star_text = 'â­' if is_favorite else 'â˜†'
        
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
                favorite_star.config(fg='#FF6B35', text='â­')  # Naranja para quitar
            else:
                favorite_star.config(fg='#FFD700', text='â­')  # Dorado para agregar
        
        def on_star_leave(event):
            current_favorite = game.get('favorite', False)
            star_color = '#FFD700' if current_favorite else '#B0B0B0'
            star_text = 'â­' if current_favorite else 'â˜†'
            favorite_star.config(fg=star_color, text=star_text)
        
        favorite_star.bind("<Enter>", on_star_enter)
        favorite_star.bind("<Leave>", on_star_leave)
        favorite_star.bind("<Button-1>", lambda e, g=game: self.toggle_favorite(g))
        
        # Contenedor de imagen con mejor diseÃ±o
        image_container = tk.Frame(card_frame, bg=self.colors['bg_light'])
        image_container.pack(pady=(0, 15), padx=15)
        
        try:
            # Cargar y redimensionar imagen con bordes redondeados simulados
            image = Image.open(game['image_path'])
            image = image.resize((240, 270), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Label de imagen con mejor presentaciÃ³n
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
            # Imagen por defecto con mejor diseÃ±o
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
                                            text="ðŸŽ®\n" + self.get_text('no_image'),
                                            bg=self.colors['bg_light'],
                                            fg=self.colors['text_muted'],
                                            font=('Segoe UI', 20),
                                            width=30, height=17,
                                            relief='solid',
                                            bd=1)
            
            placeholder_label.pack()
            placeholder_label.bind("<Button-1>", lambda e, g=game: self.open_game_map(g))
        
        # Frame para botones con mejor diseÃ±o
        buttons_frame = tk.Frame(card_frame, bg=self.colors['bg_light'])
        buttons_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # BotÃ³n de editar mejorado con Ã­cono
        edit_button = tk.Button(buttons_frame, 
                               text="âœï¸ " + self.get_text('edit_game'), 
                               bg=self.colors['warning'], 
                               fg='white',
                               font=('Segoe UI', 9, 'bold'),
                               relief='flat',
                               cursor='hand2',
                               pady=8,
                               command=lambda g=game: self.edit_game(g))
        edit_button.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # BotÃ³n de eliminar mejorado con Ã­cono
        delete_button = tk.Button(buttons_frame, 
                                 text="ðŸ—‘ï¸ " + self.get_text('delete_game'), 
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
        
        # Actualizar visualizaciÃ³n con animaciÃ³n sutil
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
        
        # Configurar colores segÃºn si es favorito o no
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
        
        # Auto-cerrar despuÃ©s de 2 segundos
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
            # Para imÃ¡genes, crear ventana tkinter normal
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
        
        # MÃ©todo directo usando webview - sin ventana tkinter intermedia
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
            # Si webview no estÃ¡ disponible, crear ventana tkinter como fallback
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
        
        # Usar el mÃ©todo de fallback HTML
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
            window.update_idletasks()  # Asegurar que la ventana estÃ© actualizada
            window_width = window.winfo_width() - 20  # Dejar margen pequeÃ±o
            window_height = window.winfo_height() - 20
            
            # Si las dimensiones no estÃ¡n disponibles, usar valores por defecto
            if window_width <= 20:
                window_width = 980
            if window_height <= 20:
                window_height = 680
                
            img_width, img_height = image.size
            
            # Calcular tamaÃ±o de visualizaciÃ³n manteniendo ratio
            ratio = min(window_width/img_width, window_height/img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            # Si la imagen es mÃ¡s pequeÃ±a que la ventana, mostrarla a tamaÃ±o original
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
            
            # Configurar regiÃ³n de scroll
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
            
            # FunciÃ³n para redimensionar imagen cuando cambie el tamaÃ±o de ventana
            def resize_image_to_window():
                try:
                    # Obtener nuevas dimensiones de la ventana
                    window.update_idletasks()
                    new_window_width = window.winfo_width() - 20
                    new_window_height = window.winfo_height() - 20
                    
                    # Verificar que las dimensiones sean vÃ¡lidas
                    if new_window_width <= 20 or new_window_height <= 20:
                        return
                    
                    # Si no hay zoom manual, ajustar automÃ¡ticamente
                    if not canvas.is_manual_zoom:
                        # Calcular nuevo ratio para ajustar a la ventana
                        ratio = min(new_window_width/img_width, new_window_height/img_height)
                        new_width = int(img_width * ratio)
                        new_height = int(img_height * ratio)
                        
                        # Si la imagen es mÃ¡s pequeÃ±a que la ventana, mostrarla a tamaÃ±o original
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
            
            # FunciÃ³n para manejar el evento de redimensionamiento de ventana
            def on_window_resize(event):
                # Solo responder al evento de la ventana principal, no del canvas
                if event.widget == window:
                    # Usar after para evitar mÃºltiples llamadas rÃ¡pidas
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
            
            # FunciÃ³n para resetear zoom (doble click)
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
                                       text=f"Error al cargar imagen del mapa:\n{str(e)}\n\nVerifica que el archivo de imagen existe y es vÃ¡lido.",
                                       style='Dark.TLabel',
                                       justify='center')
                error_label.pack(expand=True)
    
    def show_iframe_map(self, window, game):
        """Mostrar mapa web en ventana integrada del programa"""
        print(f"Abriendo mapa web: {game['map_content']}")  # Debug
        
        # MÃ©todo directo usando webview en la misma ventana
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
            print("webview no disponible, intentando mÃ©todo HTML directo...")
            self.show_html_browser(window, game)
        except Exception as e:
            print(f"Error con webview: {e}")
            self.show_html_browser(window, game)
    
    def show_html_browser(self, window, game):
        """MÃ©todo de fallback usando tkinterweb con HTML optimizado"""
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
                '<h3>âš ï¸ Error de carga</h3><p>El sitio puede tener restricciones</p>' +
                '<p><a href="{game['map_content']}" target="_blank" style="color: {self.colors['accent']};">Abrir en navegador</a></p>';
        }}
        
        // Ocultar loading despuÃ©s de 5 segundos como mÃ¡ximo
        setTimeout(function() {{
            document.getElementById('loading').style.display = 'none';
        }}, 5000);
        
        // Verificar si el iframe estÃ¡ cargando
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
        """MÃ©todo mÃ¡s simple - crear archivo HTML temporal y abrirlo"""
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
            
            # Programar eliminaciÃ³n del archivo temporal
            def cleanup():
                try:
                    os.unlink(temp_file)
                except:
                    pass
            
            # Eliminar archivo despuÃ©s de 30 segundos
            import threading
            timer = threading.Timer(30.0, cleanup)
            timer.start()
            
            print(f"Archivo temporal creado y abierto: {temp_file}")
            
        except Exception as e:
            print(f"Error con redirect simple: {e}")
            # Fallback final - el mÃ©todo original
            self.show_webview_fallback_in_frame(window, game)
    
    def show_alternative_browser(self, window, game):
        """MÃ©todo alternativo usando pywebview embebido correctamente"""
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
                        title=f"ðŸ—ºï¸ Mapa - {game['name']}",
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
                    
                    # Cuando webview se cierre, cerrar tambiÃ©n la ventana de tkinter
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
        """MÃ©todo alternativo para embeber contenido web usando HTML/iframe bÃ¡sico"""
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
            print("tkinterweb no disponible, usando fallback bÃ¡sico")
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
                             text="âš ï¸ Error al cargar el mapa web",
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
        
        # DescripciÃ³n
        desc_label = tk.Label(container,
                             text="Haz clic en el botÃ³n de abajo para abrir el mapa en tu navegador:",
                             bg=self.colors['bg_dark'],
                             fg=self.colors['text_muted'],
                             font=('Arial', 10))
        desc_label.pack(pady=(0, 30))
        
        # BotÃ³n para abrir en navegador
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
                                 text="ðŸŒ Abrir en navegador",
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
        """Mostrar diÃ¡logo para editar juego"""
        dialog = tk.Toplevel(self.root)
        dialog.title(self.get_text('edit_game_title'))
        dialog.geometry("600x550")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Configurar icono del diÃ¡logo de ediciÃ³n
        self.apply_window_icon(dialog)
        
        # Centrar diÃ¡logo
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
        
        # Configurar icono del diÃ¡logo de ediciÃ³n (segunda funciÃ³n)
        self.apply_window_icon(dialog)
        
        # Crear formulario de ediciÃ³n
        self.create_edit_game_form(dialog)
    
    def create_edit_game_form(self, parent):
        """Crear formulario para editar juego"""
        # Frame principal del formulario
        form_frame = ttk.Frame(parent, style='Dark.TFrame')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # TÃ­tulo
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
        """Explorar imagen para el juego (modo ediciÃ³n)"""
        filename = filedialog.askopenfilename(
            title="Seleccionar imagen del juego",
            filetypes=[("Archivos de imagen", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if filename:
            self.edit_game_image_path.set(filename)
    
    def browse_edit_map_content(self):
        """Explorar contenido del mapa (modo ediciÃ³n)"""
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
            messagebox.showerror("Error", "El nombre del juego no puede estar vacÃ­o")
            return
        
        image_path = self.edit_game_image_path.get().strip()
        map_content = self.edit_map_content_var.get().strip()
        map_type = self.edit_map_type_var.get()
        
        # Validar imagen si se cambiÃ³
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
        
        # Copiar imagen del juego si cambiÃ³
        local_image_path = image_path
        if image_path and image_path != self.edit_original_game['image_path']:
            local_image_path = self.copy_image_to_local(image_path, name, "game")
            if not local_image_path:
                messagebox.showerror("Error", "No se pudo copiar la nueva imagen del juego")
                return
        elif not image_path:
            # Si no se especificÃ³ imagen, mantener la original
            local_image_path = self.edit_original_game['image_path']
        
        # Copiar imagen del mapa si cambiÃ³ y es de tipo imagen
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
        
        # Limpiar imÃ¡genes no utilizadas
        self.cleanup_unused_images()
        
        messagebox.showinfo("Ã‰xito", f"Juego '{name}' actualizado correctamente")
        dialog.destroy()
    
    def delete_game(self, game):
        """Eliminar juego"""
        confirm_title = self.get_text('confirm_title')
        confirm_message = self.get_text('confirm_delete').replace('este juego', f"'{game['name']}'").replace('this game', f"'{game['name']}'")
        
        if messagebox.askyesno(confirm_title, confirm_message):
            self.games.remove(game)
            self.save_games()
            self.refresh_games_display()
            
            # Limpiar imÃ¡genes no utilizadas despuÃ©s de eliminar
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
            # Usar after para evitar mÃºltiples llamadas rÃ¡pidas durante el redimensionamiento
            if hasattr(self, '_resize_job'):
                self.root.after_cancel(self._resize_job)
            self._resize_job = self.root.after(300, self.refresh_games_display)
    
    def on_closing(self):
        """MÃ©todo llamado al cerrar la aplicaciÃ³n para limpiar recursos"""
        try:
            # Limpiar CEF si estÃ¡ inicializado
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
            # Cerrar la aplicaciÃ³n
            self.root.quit()
            self.root.destroy()

    def edit_game(self, game):
        """Mostrar diï¿½logo para editar juego"""
        dialog = tk.Toplevel(self.root)
        dialog.title(self.get_text('edit_game_title'))
        dialog.geometry("600x550")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Configurar icono del diÃ¡logo de ediciÃ³n
        try:
            dialog.iconbitmap("logo.ico")
        except:
            pass
        
        # Centrar diï¿½logo
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
        
        # Crear formulario de ediciï¿½n
        self.create_edit_game_form(dialog)

def main():
    def start_main_app():
        """Iniciar la aplicaciÃ³n principal despuÃ©s del splash"""
        root = tk.Tk()
        app = AvalonGameManager(root)
        root.mainloop()
    
    # Mostrar splash screen con callback
    splash = SplashScreen()
    splash.show(on_complete=start_main_app)

if __name__ == "__main__":
    main()

