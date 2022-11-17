# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = [('assets\\*', 'assets\\.')]
datas += collect_data_files('sv_ttk')


block_cipher = None


a = Analysis(
    ['src\\gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['vtkmodules', 'vtkmodules.all', 'vtkmodules.qt.QVTKRenderWindowInteractor', 'vtkmodules.util', 'vtkmodules.util.numpy_support', 'vtkmodules.numpy_interface.dataset_adapter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='gui',
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
    icon=['assets\\icon.ico'],
)
