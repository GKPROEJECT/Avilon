# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['Avilon_clean.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('logo.png', '.'),
        ('logo.ico', '.'),
        ('avilon_config.json', '.'),
        ('avilon_games.json', '.'),
        ('games_images', 'games_images')
    ],
    hiddenimports=['tkinter', 'PIL', 'urllib'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Avilon',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.ico',
)
