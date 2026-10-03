# Avilon - Características de Overlay Global

## Novo: Overlay Global con Hotkey

Ahora puedes presionar **Alt + Shift + O** en cualquier momento (incluso cuando el programa Avilon no está en foco) para mostrar un overlay transparente con los objetivos del juego actualmente abierto.

### Características del Overlay:

1. **Detección automática de juegos**: El overlay detecta automáticamente qué juego tienes abierto basándose en el nombre de la ventana.

2. **Muestra objetivos en tiempo real**: Si tienes un mapa de juego abierto, el overlay mostrará:
   - Nombre del juego
   - Lista de objetivos/tareas
   - Cantidad de objetivos completados vs total
   - Estado visual (✓ completado, ○ pendiente)

3. **Overlay vacío elegante**: Si no tienes ningún mapa de juego abierto, el overlay mostrará un mensaje indicándolo.

4. **Interfaz pulida**:
   - Diseño oscuro compatible con gaming
   - Posicionado en la esquina inferior derecha
   - Transparencia controlada
   - Siempre encima de otras ventanas (topmost)

### Cómo usar:

1. **Abre Avilon** y configura tus juegos con sus objetivos
2. **Abre el mapa de un juego** (una ventana con el nombre del juego)
3. **Presiona Alt + Shift + O** para mostrar el overlay
4. **Presiona ESC** o haz clic en "ESC para cerrar" para ocultarlo

### Requisitos:

- El programa Avilon debe estar ejecutándose
- El nombre de la ventana del juego debe coincidir (al menos parcialmente) con el nombre del juego en Avilon
- Se requieren las librerías `pynput` y `pygetwindow` (ya instaladas)

### Ejemplo:

```
Avilon (juego guardado como "V Rising")
└─ Abre V Rising en tu navegador o aplicación
└─ Presiona Alt + Shift + O
└─ El overlay muestra:
   - Juego: V Rising
   - 📋 Objetivos (3/5)
   - ✓ Completar misión principal
   - ○ Encontrar todos los tesoros
   - ○ Derrotar boss final
   - (etc...)
```

### Notas técnicas:

- El hotkey es global y funciona incluso cuando Avilon está minimizado
- La detección de juegos es case-insensitive (mayúsculas/minúsculas no importan)
- El overlay se posiciona automáticamente en la esquina inferior derecha
- Los objetivos se sincronizan en tiempo real desde tu configuración de Avilon
