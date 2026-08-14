# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# Packages that require full collection of data, binaries and hidden imports
packages_to_collect = ['torch', 'transformers']
all_datas = []
all_binaries = []
all_hidden = []

for pkg in packages_to_collect:
    d, b, h = collect_all(pkg)
    all_datas.extend(d)
    all_binaries.extend(b)
    all_hidden.extend(h)

a = Analysis(
    ['src/rag/__main__.py'],
    pathex=[],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hidden + ['rag.utils.config', 'rag.utils.logcat'],
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
    [],
    exclude_binaries=True,
    name='rag',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='rag',
)
