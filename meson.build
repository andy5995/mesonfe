project('mesonfe', version: '0.0.1', license: 'MIT', meson_version: '>= 0.57.0')

install_data(
    meson.project_name(),
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

py = import('python').find_installation(
    'python3',
    modules: ['PyQt5', 'platformdirs'],
)

_version_py = configure_file(
    input: 'src/mesonfe/_version.py.in',
    output: '_version.py',
    configuration: {'VERSION': meson.project_version()},
)
py.install_sources(
    ['src/mesonfe/__init__.py', _version_py],
    subdir: 'mesonfe',
)

install_data(
    'data/@0@.svg'.format(meson.project_name()),
    install_dir: get_option('datadir') / 'icons' / 'hicolor' / 'scalable' / 'apps',
)

configure_file(
    input: 'data/mesonfe.desktop.in',
    output: '@0@.desktop'.format(meson.project_name()),
    configuration: {'NAME': meson.project_name()},
    install: true,
    install_dir: get_option('datadir') / 'applications',
)

gnome = import('gnome')
gnome.post_install(
    update_desktop_database: true,
)

pytest = find_program('pytest', required: false)
if pytest.found()
    test(
        'pytest',
        pytest,
        args: ['tests/'],
        workdir: meson.project_source_root(),
    )
endif
