#!/usr/bin/env python3
"""
Script para probar las validaciones del programa Avilon
Este script crea algunos archivos de prueba para testing
"""

import os
from PIL import Image

# Crear directorio de pruebas si no existe
test_dir = "test_images"
if not os.path.exists(test_dir):
    os.makedirs(test_dir)

# Crear una imagen de prueba válida
test_image = Image.new('RGB', (100, 100), color='red')
test_image.save(os.path.join(test_dir, "test_game.png"))

# Crear una imagen de mapa de prueba
map_image = Image.new('RGB', (500, 300), color='blue')
map_image.save(os.path.join(test_dir, "test_map.jpg"))

# Crear un archivo de texto (que no debería ser válido como imagen)
with open(os.path.join(test_dir, "not_an_image.txt"), 'w') as f:
    f.write("Este es un archivo de texto, no una imagen")

print("Archivos de prueba creados en el directorio 'test_images':")
print("- test_game.png (imagen válida para juego)")
print("- test_map.jpg (imagen válida para mapa)")
print("- not_an_image.txt (archivo inválido)")
print("\nURLs de prueba para iframes:")
print("- https://www.google.com/maps (válida)")
print("- google.com (inválida - sin protocolo)")
print("- not-a-real-url (inválida)")