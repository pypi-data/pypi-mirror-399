# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['decoder/acp/entrypoint.py'],
    pathex=[],
    binaries=[],
    datas=[
        # By default, pyinstaller doesn't include the .md files
        ('decoder/core/prompts/*.md', 'decoder/core/prompts'),
        ('decoder/core/tools/builtins/prompts/*.md', 'decoder/core/tools/builtins/prompts'),
        # We also need to add all setup files
        ('decoder/setup/*', 'decoder/setup'),
        # This is necessary because tools are dynamically called in decoder, meaning there is no static reference to those files
        ('decoder/core/tools/builtins/*.py', 'decoder/core/tools/builtins'),
        ('decoder/acp/tools/builtins/*.py', 'decoder/acp/tools/builtins'),
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
    name='decoder-acp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
