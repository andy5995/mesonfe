project('mesonfe', version: '0.1.0', license: 'MIT')

install_data(
  'mesonfe',
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x',
)

install_data(
  'README.md',
  'LICENSE',
  install_dir: get_option('datadir') / 'doc' / meson.project_name(),
)

py = import('python').find_installation('python3')
pyqt5 = py.find_python_module('PyQt5', required: false)

if pyqt5.found()
  install_data(
    'mesonfe-qt',
    install_dir: get_option('bindir'),
    install_mode: 'rwxr-xr-x',
  )
else
  warning('PyQt5 not found; mesonfe-qt will not be installed')
endif
