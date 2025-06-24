# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pianc-ship-dimensions-gui.py'],
    pathex=[],
    binaries=[],
    datas=[('wg121_database.txt', '.'), ('wg235_database.txt', '.')],
    hiddenimports=['scipy.special', 'scipy.special._cdflib', 'scipy._lib.messagestream', 'scipy._cyutility'],
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
    name='pianc-ship-dimensions-gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
