# -*- mode: python -*-

block_cipher = None

appname = 'NTLoggerTool_v051'

print('------------------------------------------------\n')
print(' pyinstaller builds '+appname+'\n')
print('------------------------------------------------')

a = Analysis([appname+'.py'],
             pathex=['C:\\Users\\Olli\\Documents\\PyQT\\NTLoggerTool'],
             binaries=[],
             datas=[('resources/icons' , 'resources/icons') , ('*.py', '.') , ('*.ui', '.')  ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['pandas','babel','django','IPython','jupyter','PySide2','scipy','matplotlib','notebook','numba','tk',
                       'bottleneck','docutils','h5py','PIL','shiboken2','markupsafe'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name=appname,
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='resources/icons/logo-storm32-ntlogger1.ico' )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=appname)
