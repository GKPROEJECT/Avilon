# -*- mode: python ; coding: utf-8 -*-
import os
import sys

project_dir = SPECPATH
app_icon = os.path.join(project_dir, 'logo.ico' if sys.platform == 'win32' else 'logo.png')
a = Analysis(
    [os.path.join(project_dir, 'Avilon_clean.py')],
    pathex=[project_dir],
    binaries=[],
    datas=[
        (os.path.join(project_dir, 'logo.png'), '.'),
        (os.path.join(project_dir, 'logo.ico'), '.'),
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
    icon=app_icon,
)
