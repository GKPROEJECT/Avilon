@echo off
echo Compilando Avilon con PyInstaller...
python -m PyInstaller Avilon.spec --clean --noconfirm
echo.
echo Compilacion completada!
echo El ejecutable se encuentra en la carpeta 'dist'
pause