# Instrucciones para crear el ejecutable de Avilon

## ¿Qué se ha modificado?

Se han realizado los siguientes cambios para solucionar el problema del logo.ico en el ejecutable:

1. **Nueva función `resource_path()`**: Maneja correctamente las rutas de recursos tanto en modo desarrollo (.py) como en ejecutable (.exe).

2. **Archivo Avilon.spec personalizado**: Le dice específicamente a PyInstaller que incluya el logo.ico como recurso interno.

3. **Nuevo archivo build_avilon.bat**: Utiliza el archivo .spec personalizado para una compilación más precisa.

4. **Corrección de todas las referencias**: Todas las ventanas ahora usan la ruta correcta del logo.

## Cómo compilar el ejecutable

### Opción 1: Usar el nuevo archivo .bat (RECOMENDADO)
```bash
build_avilon.bat
```

### Opción 2: Comando manual
```bash
python -m PyInstaller Avilon.spec --clean --noconfirm
```

## Archivos necesarios en la carpeta

Asegúrate de que estos archivos estén en la misma carpeta:
- `Avilon_clean.py` (código principal)
- `logo.ico` (icono del programa)
- `Avilon.spec` (configuración de PyInstaller)
- `build_avilon.bat` (script de compilación)

## ¿Qué problemas soluciona?

✅ Logo.ico aparece correctamente en todas las ventanas del .exe
✅ Splash screen muestra el logo correcto en lugar del cohete
✅ Ventana "Acerca de" muestra el logo correcto
✅ Ventana de configuración muestra el logo correcto
✅ Ventana de añadir juego muestra el logo correcto
✅ Ventana del mapa muestra el logo correcto
✅ Las imágenes de los juegos se mantienen aunque borres las originales

## Notas importantes

- El ejecutable se generará en la carpeta `dist/`
- El logo.ico se incluye internamente en el .exe
- Las configuraciones y imágenes de juegos se guardan en la misma carpeta que el .exe
- Ya no necesitas mantener el logo.ico junto al .exe, está integrado internamente