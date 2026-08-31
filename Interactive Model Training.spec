# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from glob import glob
from PyInstaller.utils.hooks import collect_all

# Collect all binaries, data, and submodules for mlx and mlx_lm
mlx_datas, mlx_binaries, mlx_hiddenimports = collect_all('mlx')
mlx_lm_datas, mlx_lm_binaries, mlx_lm_hiddenimports = collect_all('mlx_lm')

# Find the site-packages directory from the current active python environment
site_packages = next(p for p in sys.path if p.endswith('site-packages'))
metallib_pattern = os.path.join(site_packages, 'mlx', '**', '*.metallib')
metallib_files = glob(metallib_pattern, recursive=True)
extra_binaries = [(f, '.') for f in metallib_files]


a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=mlx_binaries + mlx_lm_binaries + extra_binaries,
    datas=mlx_datas + mlx_lm_datas + [('assets', 'assets')],
    hiddenimports=mlx_hiddenimports + mlx_lm_hiddenimports,
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
    name='Interactive Model Training',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    name='Interactive Model Training',
)
app = BUNDLE(
    coll,
    name='Interactive Model Training.app',
    icon='assets/references/icon.icns',
    bundle_identifier=None,
)
