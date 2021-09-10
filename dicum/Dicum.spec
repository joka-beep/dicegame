# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

resources = [
        ("resources/fonts", "resources/fonts"),
        ("resources/icons", "resources/icons"),
        ("resources/images/README","resources/images"),
        ("resources/images/bg.png","resources/images"),
        ("resources/js", "resources/js"),
        ("resources/templates", "resources/templates"),
        ("resources/styles", "resources/styles")]

a = Analysis(['Dicum.py'],
             pathex=['/home/jonas/Projects/dicum/Dicum'],
             binaries=[],
             datas=resources,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Dicum',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
