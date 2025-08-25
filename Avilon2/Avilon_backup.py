import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
from PIL import Image, ImageTk
import webbrowser
import tkinter.font as tkFont
import urllib.parse
import re
import time
import subprocess
import sys
import platform
import threading

class AvalonGameManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Avilon - Game Manager")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2f3136")
        
        # Archivo para almacenar los juegos
        self.games_file = "avilon_games.json"
        self.games = self.load_games()
        
        # Configurar estilo Discord-like
        self.setup_styles()
        
        # Crear la interfaz
        self.create_main_interface()
        
        # Cargar juegos existentes
        self.refresh_games_display()
    
    def setup_styles(self):
        """Configurar estilos tipo Discord"""
        style = ttk.Style()
        
        # Colores Discord-like
        self.colors = {
            'bg_dark': '#2f3136',
            'bg_light': '#36393f',
            'sidebar': '#2f3136',
            'accent': '#7289da',
            'text': '#ffffff',
            'text_muted': '#99aab5',
            'success': '#43b581',
            'danger': '#f04747',
            'warning': '#ff9500'
        }
        
        # Configurar ttk styles
        style.theme_use('clam')
        style.configure('Dark.TFrame', background=self.colors['bg_dark'])
        style.configure('Sidebar.TFrame', background=self.colors['sidebar'])
        style.configure('Game.TFrame', background=self.colors['bg_light'], relief='raised')
        
        style.configure('Dark.TLabel', 
                       background=self.colors['bg_dark'], 
                       foreground=self.colors['text'])
        style.configure('GameTitle.TLabel', 
                       background=self.colors['bg_light'], 
                       foreground=self.colors['text'],
                       font=('Segoe UI', 10, 'bold'))
        
        style.configure('Accent.TButton',
                       background=self.colors['accent'],
                       foreground=self.colors['text'],
                       borderwidth=0,
                       focuscolor='none')
        style.map('Accent.TButton',
                 background=[('active', '#677bc4')])
    
    def create_main_interface(self):
        """Crear la interfaz principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sidebar (izquierda)
        self.create_sidebar(main_frame)
        
        # Área de contenido principal
        self.create_content_area(main_frame)
    
    def create_sidebar(self, parent):
        """Crear sidebar estilo Discord"""
        sidebar = ttk.Frame(parent, style='Sidebar.TFrame', width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Título
        title_label = ttk.Label(sidebar, text="AVILON", 
                               style='Dark.TLabel',
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(20, 30))
        
        # Botón para añadir juegos
        add_button = ttk.Button(sidebar, text="+ Añadir Juego",
                               style='Accent.TButton',
                               command=self.show_add_game_dialog)
        add_button.pack(pady=10, padx=20, fill=tk.X)
        
        # Separador
        separator = ttk.Separator(sidebar, orient='horizontal')
        separator.pack(pady=20, padx=10, fill=tk.X)
        
        # Label para biblioteca
        library_label = ttk.Label(sidebar, text="BIBLIOTECA",
                                 style='Dark.TLabel',
                                 font=('Segoe UI', 12, 'bold'))
        library_label.pack(pady=(0, 10))
        
        # Contador de juegos
        self.games_count_label = ttk.Label(sidebar, 
                                          text=f"{len(self.games)} juegos",
                                          style='Dark.TLabel',
                                          foreground=self.colors['text_muted'])
        self.games_count_label.pack()
    
    def create_content_area(self, parent):
        """Crear área de contenido principal"""
        content_frame = ttk.Frame(parent, style='Dark.TFrame')
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(content_frame, style='Dark.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        library_title = ttk.Label(header_frame, text="Mi Biblioteca",
                                 style='Dark.TLabel',
                                 font=('Segoe UI', 20, 'bold'))
        library_title.pack(anchor=tk.W)
        
        # Frame scrollable para juegos
        self.create_scrollable_games_area(content_frame)
    
    def create_scrollable_games_area(self, parent):
        """Crear área scrollable para los juegos"""
        # Canvas y scrollbar para scroll
        self.canvas = tk.Canvas(parent, bg=self.colors['bg_dark'], 
                               highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", 
                                 command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style='Dark.TFrame')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def show_add_game_dialog(self):
        """Mostrar diálogo para añadir juego"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Añadir Nuevo Juego")
        dialog.geometry("600x550")  # Más grande para mejor visualización
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)  # Evitar redimensionado
        
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
        title_label = ttk.Label(form_frame, text="Nuevo Juego",
                               style='Dark.TLabel',
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Nombre del juego
        name_label = ttk.Label(form_frame, text="Nombre del juego:",
                              style='Dark.TLabel')
        name_label.pack(anchor=tk.W, pady=(0, 5))
        
        name_entry = tk.Entry(form_frame, textvariable=self.game_name_var,
                             bg=self.colors['bg_light'], fg=self.colors['text'],
                             font=('Segoe UI', 10), relief='flat',
                             insertbackground=self.colors['text'])
        name_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
        
        # Imagen del juego
        image_label = ttk.Label(form_frame, text="Imagen del juego:",
                               style='Dark.TLabel')
        image_label.pack(anchor=tk.W, pady=(0, 5))
        
        image_frame = ttk.Frame(form_frame, style='Dark.TFrame')
        image_frame.pack(fill=tk.X, pady=(0, 15))
        
        image_entry = tk.Entry(image_frame, textvariable=self.game_image_path,
                              bg=self.colors['bg_light'], fg=self.colors['text'],
                              font=('Segoe UI', 10), relief='flat',
                              insertbackground=self.colors['text'])
        image_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        browse_button = ttk.Button(image_frame, text="Examinar",
                                  command=self.browse_image)
        browse_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Tipo de mapa
        map_type_label = ttk.Label(form_frame, text="Tipo de mapa:",
                                  style='Dark.TLabel')
        map_type_label.pack(anchor=tk.W, pady=(0, 5))
        
        map_type_frame = ttk.Frame(form_frame, style='Dark.TFrame')
        map_type_frame.pack(fill=tk.X, pady=(0, 15))
        
        image_radio = tk.Radiobutton(map_type_frame, text="Imagen",
                                    variable=self.map_type_var, value="image",
                                    bg=self.colors['bg_dark'], fg=self.colors['text'],
                                    selectcolor=self.colors['bg_light'],
                                    activebackground=self.colors['bg_dark'])
        image_radio.pack(side=tk.LEFT)
        
        iframe_radio = tk.Radiobutton(map_type_frame, text="Página web (iframe)",
                                     variable=self.map_type_var, value="iframe",
                                     bg=self.colors['bg_dark'], fg=self.colors['text'],
                                     selectcolor=self.colors['bg_light'],
                                     activebackground=self.colors['bg_dark'])
        iframe_radio.pack(side=tk.LEFT, padx=(20, 0))
        
        # Contenido del mapa
        map_content_label = ttk.Label(form_frame, text="Ruta/URL del mapa:",
                                     style='Dark.TLabel')
        map_content_label.pack(anchor=tk.W, pady=(0, 5))
        
        map_content_frame = ttk.Frame(form_frame, style='Dark.TFrame')
        map_content_frame.pack(fill=tk.X, pady=(0, 20))
        
        map_content_entry = tk.Entry(map_content_frame, textvariable=self.map_content_var,
                                    bg=self.colors['bg_light'], fg=self.colors['text'],
                                    font=('Segoe UI', 10), relief='flat',
                                    insertbackground=self.colors['text'])
        map_content_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        browse_map_button = ttk.Button(map_content_frame, text="Examinar",
                                      command=self.browse_map_content)
        browse_map_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Botones
        button_frame = ttk.Frame(form_frame, style='Dark.TFrame')
        button_frame.pack(fill=tk.X)
        
        cancel_button = ttk.Button(button_frame, text="Cancelar",
                                  command=parent.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        save_button = ttk.Button(button_frame, text="Guardar Juego",
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
        
        # Crear objeto juego
        game = {
            'name': name,
            'image_path': image_path,
            'map_type': map_type,
            'map_content': map_content
        }
        
        # Añadir a la lista
        self.games.append(game)
        
        # Guardar en archivo
        self.save_games()
        
        # Actualizar interfaz
        self.refresh_games_display()
        
        # Cerrar diálogo
        dialog.destroy()
        
        messagebox.showinfo("Éxito", f"Juego '{name}' añadido correctamente")
    
    def refresh_games_display(self):
        """Actualizar la visualización de juegos"""
        # Limpiar frame scrollable
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Actualizar contador
        self.games_count_label.config(text=f"{len(self.games)} juegos")
        
        if not self.games:
            # Mostrar mensaje si no hay juegos
            no_games_label = ttk.Label(self.scrollable_frame,
                                      text="No tienes juegos en tu biblioteca",
                                      style='Dark.TLabel',
                                      font=('Segoe UI', 14))
            no_games_label.pack(pady=50)
            
            add_first_label = ttk.Label(self.scrollable_frame,
                                       text="Haz clic en '+ Añadir Juego' para comenzar",
                                       style='Dark.TLabel',
                                       foreground=self.colors['text_muted'])
            add_first_label.pack()
            return
        
        # Mostrar juegos en grid (estilo Steam)
        row = 0
        col = 0
        max_cols = 4
        
        for i, game in enumerate(self.games):
            self.create_game_card(self.scrollable_frame, game, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def create_game_card(self, parent, game, row, col):
        """Crear tarjeta de juego estilo Steam"""
        # Frame principal de la tarjeta
        card_frame = ttk.Frame(parent, style='Game.TFrame')
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Configurar grid weights
        parent.grid_columnconfigure(col, weight=1)
        
        try:
            # Cargar y redimensionar imagen (más alargada como Steam)
            image = Image.open(game['image_path'])
            image = image.resize((300, 140), Image.Resampling.LANCZOS)  # Más alargado
            photo = ImageTk.PhotoImage(image)
            
            # Label de imagen clickeable
            image_label = tk.Label(card_frame, image=photo, 
                                  bg=self.colors['bg_light'],
                                  cursor='hand2')
            image_label.image = photo  # Mantener referencia
            image_label.pack(pady=5)
            
            # Bind click en imagen
            image_label.bind("<Button-1>", 
                           lambda e, g=game: self.open_game_map(g))
            
        except Exception as e:
            # Si no se puede cargar la imagen, mostrar placeholder
            placeholder_label = tk.Label(card_frame, 
                                        text="Sin imagen",
                                        bg=self.colors['bg_light'],
                                        fg=self.colors['text_muted'],
                                        width=35, height=8)  # Ajustado al nuevo tamaño
            placeholder_label.pack(pady=5)
            placeholder_label.bind("<Button-1>", 
                                 lambda e, g=game: self.open_game_map(g))
        
        # Nombre del juego clickeable
        name_label = ttk.Label(card_frame, text=game['name'],
                              style='GameTitle.TLabel',
                              cursor='hand2')
        name_label.pack(pady=(5, 5))
        name_label.bind("<Button-1>", 
                       lambda e, g=game: self.open_game_map(g))
        
        # Botón de eliminar (debajo del nombre, ocupando todo el ancho)
        delete_button = tk.Button(card_frame, text="Borrar juego", 
                                 bg=self.colors['danger'], 
                                 fg=self.colors['text'],
                                 font=('Segoe UI', 9),
                                 relief='flat',
                                 cursor='hand2',
                                 command=lambda g=game: self.delete_game(g))
        delete_button.pack(fill=tk.X, pady=(5, 5), padx=5)

        # Bot�n de editar (debajo del bot�n borrar)
        edit_button = tk.Button(card_frame, text="Editar juego",
                               bg=self.colors['warning'],
                               fg=self.colors['text'],
                               font=('Segoe UI', 9),
                               relief='flat',
                               cursor='hand2',
                               command=lambda g=game: self.edit_game(g))
        edit_button.pack(fill=tk.X, pady=(0, 10), padx=5)
    
    def open_game_map(self, game):
        """Abrir ventana con el mapa del juego"""
        print(f"Abriendo mapa para {game['name']} - Tipo: {game['map_type']}")  # Debug
        
        if game['map_type'] == 'image':
            map_window = tk.Toplevel(self.root)
            map_window.title(f"Mapa - {game['name']}")
            map_window.geometry("1000x700")
            map_window.configure(bg=self.colors['bg_dark'])
            self.show_image_map(map_window, game)
        else:
            self.show_iframe_map(None, game)
    
    def show_image_map(self, window, game):
        """Mostrar mapa como imagen"""
        try:
            # Cargar imagen
            image = Image.open(game['map_content'])
            
            # Crear canvas scrollable para imagen grande
            canvas = tk.Canvas(window, bg=self.colors['bg_dark'])
            scrollbar_v = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
            scrollbar_h = ttk.Scrollbar(window, orient="horizontal", command=canvas.xview)
            
            canvas.configure(yscrollcommand=scrollbar_v.set, 
                           xscrollcommand=scrollbar_h.set)
            
            # Mantener ratio de aspecto pero ajustar a ventana
            window_width = 980
            window_height = 680
            img_width, img_height = image.size
            
            # Calcular tamaño de visualización
            ratio = min(window_width/img_width, window_height/img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            canvas.create_image(0, 0, anchor="nw", image=photo)
            canvas.image = photo  # Mantener referencia
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar_v.pack(side="right", fill="y")
            scrollbar_h.pack(side="bottom", fill="x")
            
        except Exception as e:
            error_label = ttk.Label(window, 
                                   text=f"Error al cargar imagen: {str(e)}",
                                   style='Dark.TLabel')
            error_label.pack(expand=True)
    
    def show_iframe_map(self, window, game):
        """Mostrar mapa web en ventana de navegador nativo"""
        print(f"Abriendo mapa web: {game['map_content']}")  # Debug
        
        # Crear script optimizado para webview
        webview_script = f'''
import webview
import threading
import time

    def edit_game(self, game):
        """Mostrar di�logo para editar juego"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Juego")
        dialog.geometry("600x550")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
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
    try:
        print("Iniciando navegador web...")
        
        # Crear ventana webview con configuración optimizada
        webview.create_window(
            title="🗺️ Mapa - {game['name']}",
            url="{game['map_content']}",
            width=1200,
            height=800,
            resizable=True,
            fullscreen=False,
            minimized=False,
            on_top=False,
            shadow=True,
            text_select=True,
            # Configuraciones adicionales para mejor rendimiento
            js_api=None
        )
        
        # Iniciar webview con configuración optimizada
        webview.start(
            debug=False,
            http_server=False,
            gui='edgechromium'  # Usar Edge WebView2 en Windows para mejor compatibilidad
        )
        
        print("Navegador cerrado")
        
    except Exception as e:
        print(f"Error en webview: {{e}}")
        # Fallback a navegador por defecto
        import webbrowser
        webbrowser.open("{game['map_content']}")

if __name__ == "__main__":
    main()
'''
        
        # Ejecutar webview en proceso separado
        script_path = f"webview_{{int(time.time())}}.py"  # Nombre único
        try:
            # Escribir script temporal
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(webview_script)
            
            # Ejecutar en proceso separado con configuración mejorada
            if platform.system() == "Windows":
                # En Windows, usar CREATE_NEW_PROCESS_GROUP para mejor aislamiento
                process = subprocess.Popen([
                    sys.executable, script_path
                ], 
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
                )
            else:
                # En otros sistemas
                process = subprocess.Popen([
                    sys.executable, script_path
                ])
            
            print(f"Navegador iniciado (PID: {{process.pid}})")  # Debug
            
            # Limpiar archivo temporal después de unos segundos
            def cleanup_script():
                time.sleep(5)  # Esperar más tiempo para asegurar que el proceso inicie
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                        print(f"Archivo temporal {{script_path}} eliminado")
                except Exception as cleanup_error:
                    print(f"Error al limpiar archivo: {{cleanup_error}}")
            
            # Ejecutar limpieza en hilo separado
            cleanup_thread = threading.Thread(target=cleanup_script, daemon=True)
            cleanup_thread.start()
            
        except Exception as e:
            print(f"Error al crear navegador: {{e}}")  # Debug
            
            # Limpiar archivo si existe
            try:
                if os.path.exists(script_path):
                    os.remove(script_path)
            except:
                pass
            
            # Fallback final: navegador por defecto
            try:
                webbrowser.open(game['map_content'])
                messagebox.showinfo(
                    "Navegador", 
                    f"El mapa de {{game['name']}} se abrió en tu navegador por defecto.\\n\\nSi prefieres una ventana integrada, considera actualizar pywebview."
                )
            except Exception as browser_error:
                messagebox.showerror(
                    "Error", 
                    f"No se pudo abrir el mapa:\\n{{browser_error}}"
                )
    

    
    def delete_game(self, game):
        """Eliminar juego"""
        if messagebox.askyesno("Confirmar", 
                              f"¿Estás seguro de que quieres eliminar '{game['name']}'?"):
            self.games.remove(game)
            self.save_games()
            self.refresh_games_display()
    
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

    def edit_game(self, game):
        """Mostrar di�logo para editar juego"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Juego")
        dialog.geometry("600x550")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
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
    root = tk.Tk()
    app = AvalonGameManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
