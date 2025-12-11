# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['C:\\Users\\gimen\\Desktop\\GKPROJECT\\Avilon\\Avilon_clean.py'],
    pathex=['C:\\Users\\gimen\\Desktop\\GKPROJECT\\Avilon'],
    binaries=[],
    datas=[
        ('C:\\Users\\gimen\\Desktop\\GKPROJECT\\Avilon\\logo.ico', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Avilon_clean',
    debug=False,  # Cambia a True si quieres ver consola para depuración
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Poner True si quieres depurar en consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\gimen\\Desktop\\GKPROJECT\\Avilon\\logo.ico'],
)
