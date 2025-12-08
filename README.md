# Avilon


Avilon es un **programa para gestionar mapas, guías, rutas, secretos y contenido auxiliar de videojuegos multiplataforma**. Su objetivo es centralizar toda la información útil de distintos juegos en una sola aplicación rápida, clara y fácil de usar, permitiendo al jugador acceder a datos de manera ordenada y visual.


> 🎮 **Tu biblioteca universal de mapas y guías para cualquier juego.**


Incluye opciones para buscar localizaciones, registrar progreso, consultar mapas interactivos y almacenar información personalizada del jugador.


## 🚀 Características principales
- 🗺️ **Gestión de mapas multijuego:** Soporte para organizar y visualizar mapas de distintos videojuegos.
- 📘 **Guías centralizadas:** Acceso rápido a misiones, coleccionables, secretos y walkthroughs.
- 🔍 **Buscador inteligente:** Encuentra zonas, objetos o rutas dentro de cualquier juego registrado.
- 💾 **Sistema de progreso:** Guarda avances, notas, marcadores y zonas completadas.
- 🖥️ **Interfaz moderna y atractiva**, con iconos, emojis y estilo visual agradable.
- ⚡ **Arquitectura optimizada** para permitir la expansión a más juegos sin romper nada.
- 🪟 **Compatibilidad total con Windows** y ejecución sencilla.
- 🔄 **Actualizaciones fáciles** gracias al control de versiones mediante Git.


## 📂 Estructura del proyecto
```
Avilon/
├── src/ # Código fuente de avilon
├── avilon_clean.spec/ # Archivo de cfg para crear el exe
├── Avilon_config/ # array donde se almacena la cfg que ponga el usuario final en el programa
├── Avilon_games/ # array donde se almacena los juegos que añada a Avilon el usurio final de el programa
├── requirements.txt # Dependencias del proyecto
└── avilon_clean.py # Archivo principal de ejecución y con el que se trabaja
```


## 🔧 Instalación
  1. Clona este repositorio:
  ```
  git clone https://github.com/GKPROEJECT/Avilon.git
  ```
2. Entra en la carpeta del proyecto:
```
cd Avilon
```
3. Instala las dependencias necesarias:
  - PILLOW
  - WEBVIEW
  


## ▶️ Ejecución
Para iniciar Avilon:
  - Usa cualquier editor de codigo
  - Instala todas las dependencias necesarias para que funcione el programa en tu editor de codigo, tal y como se indica el Para instalar las dependencias, revisa [requirements.txt](requirements.txt)
.
  - ejecuta [avilon_clean.py](avilon_clean.py) en la terminal



## 🤝 Contribuciones
Las aportaciones son bienvenidas. Para colaborar:
1. Haz un fork del repositorio.
2. Crea una nueva rama:
```
git checkout -b mi-mejora
```
3. Realiza los cambios y el commit:
```
git commit -m "Descripción de la mejora"
```
4. Envía un pull request.


## 🛠 Tecnologías utilizadas
- Python 3.13.9
- HTML
- Librerías específicas (PILLOW, WEBVIEW(PyInstaller si lo usas))
- Git y GitHub para control de versiones


## 📄 Licencia
Este proyecto está bajo la licencia MIT. Puedes usarlo, modificarlo y distribuirlo libremente sin problema alguno.
