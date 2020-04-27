from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os

datas = collect_data_files('dockermake', subdir=os.path.join('registries', 'schemas'))
datas += collect_data_files('dockermake', subdir=os.path.join('config', 'validators', 'schemas'))

hiddenimports = collect_submodules("dockermake.dockerfile.instructions")

