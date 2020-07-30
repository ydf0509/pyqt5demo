# -*- mode: python -*-

block_cipher = None


a = Analysis(['qt_app.py'],
             pathex=['F:\\minicondadir\\Miniconda2\\envs\\py36\\Lib\\site-packages', 'F:\\coding2\\ydfhome\\pyqtÏîÄ¿\\pyqt5demo'],
             binaries=[],
             datas=[],
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
          [],
          name='qt_app',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True , icon='logo1.ico')
