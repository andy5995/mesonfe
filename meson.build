project('mesonfe', version: '0.1.0', license: 'MIT', meson_version: '>= 0.56.0')

install_data(
    'mesonfe',
    install_dir: get_option('bindir'),
    install_mode: 'rwxr-xr-x',
)

_docdir = get_option('docdir')
if _docdir == ''
    _docdir = get_option('datadir') / 'doc' / meson.project_name()
endif
install_data(
    'README.md',
    'LICENSE',
    install_dir: _docdir,
)

py = import('python').find_installation('python3')
pyqt5_check = run_command(py, '-c', 'import PyQt5', check: false)
if pyqt5_check.returncode() != 0
    warning('PyQt5 not found; mesonfe requires PyQt5 to run')
endif

pytest = find_program('pytest', required: false)
if pytest.found()
    test(
        'pytest',
        pytest,
        args: ['tests/'],
        workdir: meson.project_source_root(),
    )
endif
