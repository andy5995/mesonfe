import importlib.machinery
import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Stub out PyQt5 before importing the module under test
for mod in [
    'PyQt5', 'PyQt5.QtWidgets', 'PyQt5.QtCore', 'PyQt5.QtGui',
]:
    sys.modules.setdefault(mod, MagicMock())

_path = str(Path(__file__).resolve().parent.parent / 'mesonfe')
_loader = importlib.machinery.SourceFileLoader('mesonfe', _path)
_spec = importlib.util.spec_from_loader('mesonfe', _loader)
_mod = importlib.util.module_from_spec(_spec)
_loader.exec_module(_mod)

read_json = _mod.read_json
find_builddir = _mod.find_builddir
parse_defaults = _mod.parse_defaults
parse_cmd_line = _mod.parse_cmd_line
find_test_suites = _mod.find_test_suites
find_test_setups = _mod.find_test_setups
load_project_data = _mod.load_project_data
load_mesonferc_options = _mod.load_mesonferc_options
load_mesonferc = _mod.load_mesonferc
save_mesonferc_options = _mod.save_mesonferc_options


# ---------------------------------------------------------------------------
# read_json
# ---------------------------------------------------------------------------

def test_read_json_valid(tmp_path):
    f = tmp_path / 'data.json'
    f.write_text('{"key": 42}')
    assert read_json(f) == {'key': 42}


def test_read_json_missing(tmp_path):
    assert read_json(tmp_path / 'nope.json') is None


def test_read_json_invalid(tmp_path):
    f = tmp_path / 'bad.json'
    f.write_text('not json{')
    assert read_json(f) is None


# ---------------------------------------------------------------------------
# find_builddir
# ---------------------------------------------------------------------------

def test_find_builddir_from_argv(tmp_path):
    with patch.object(sys, 'argv', ['mesonfe', str(tmp_path)]):
        assert find_builddir() == tmp_path


def test_find_builddir_detects_cwd_as_build_dir(tmp_path, monkeypatch):
    (tmp_path / 'meson-info').mkdir()
    monkeypatch.chdir(tmp_path)
    with patch.object(sys, 'argv', ['mesonfe']):
        assert find_builddir() == Path('.')


def test_find_builddir_from_rc_in_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rc = tmp_path / '.mesonferc'
    rc.write_text('default_builddir = mybuild\n')
    with patch.object(sys, 'argv', ['mesonfe']):
        assert find_builddir() == Path('mybuild')


def test_find_builddir_from_rc_in_parent(tmp_path, monkeypatch):
    child = tmp_path / 'subdir'
    child.mkdir()
    monkeypatch.chdir(child)
    (tmp_path / 'meson.build').write_text('')
    rc = tmp_path / '.mesonferc'
    rc.write_text('default_builddir = out\n')
    with patch.object(sys, 'argv', ['mesonfe']):
        assert find_builddir() == Path('../out')


def test_find_builddir_rc_with_quoted_value(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / '.mesonferc').write_text('default_builddir = "_build"\n')
    with patch.object(sys, 'argv', ['mesonfe']):
        assert find_builddir() == Path('_build')


def test_find_builddir_rc_default_fallback(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / '.mesonferc').write_text('# no builddir key\n')
    with patch.object(sys, 'argv', ['mesonfe']):
        assert find_builddir() == Path('_build')


def test_find_builddir_no_rc(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with patch.object(sys, 'argv', ['mesonfe']):
        assert find_builddir() is None


# ---------------------------------------------------------------------------
# parse_defaults
# ---------------------------------------------------------------------------

def test_parse_defaults_boolean(tmp_path):
    (tmp_path / 'meson.options').write_text(
        "option('enable_foo', type: 'boolean', value: true)\n"
        "option('enable_bar', type: 'boolean', value: false)\n"
    )
    d = parse_defaults(tmp_path)
    assert d == {'enable_foo': True, 'enable_bar': False}


def test_parse_defaults_integer(tmp_path):
    (tmp_path / 'meson.options').write_text(
        "option('threads', type: 'integer', value: 4)\n"
    )
    assert parse_defaults(tmp_path) == {'threads': 4}


def test_parse_defaults_string(tmp_path):
    (tmp_path / 'meson.options').write_text(
        "option('prefix', type: 'string', value: '/usr/local')\n"
    )
    assert parse_defaults(tmp_path) == {'prefix': '/usr/local'}


def test_parse_defaults_prefers_meson_options_over_txt(tmp_path):
    (tmp_path / 'meson.options').write_text(
        "option('x', type: 'integer', value: 1)\n"
    )
    (tmp_path / 'meson_options.txt').write_text(
        "option('x', type: 'integer', value: 99)\n"
    )
    assert parse_defaults(tmp_path)['x'] == 1


def test_parse_defaults_falls_back_to_txt(tmp_path):
    (tmp_path / 'meson_options.txt').write_text(
        "option('y', type: 'integer', value: 7)\n"
    )
    assert parse_defaults(tmp_path)['y'] == 7


def test_parse_defaults_empty(tmp_path):
    assert parse_defaults(tmp_path) == {}


# ---------------------------------------------------------------------------
# parse_cmd_line
# ---------------------------------------------------------------------------

def test_parse_cmd_line_basic(tmp_path):
    priv = tmp_path / 'meson-private'
    priv.mkdir()
    (priv / 'cmd_line.txt').write_text(
        '[options]\n'
        'b_sanitize = address,undefined\n'
        'gen_protobuf = true\n'
        '[properties]\n'
    )
    assert parse_cmd_line(tmp_path) == {'b_sanitize', 'gen_protobuf'}


def test_parse_cmd_line_skips_subproject_options(tmp_path):
    priv = tmp_path / 'meson-private'
    priv.mkdir()
    (priv / 'cmd_line.txt').write_text(
        '[options]\n'
        'b_sanitize = address\n'
        'sub:b_sanitize = address\n'
    )
    assert parse_cmd_line(tmp_path) == {'b_sanitize'}


def test_parse_cmd_line_missing_file(tmp_path):
    assert parse_cmd_line(tmp_path) == set()


def test_parse_cmd_line_no_options_section(tmp_path):
    priv = tmp_path / 'meson-private'
    priv.mkdir()
    (priv / 'cmd_line.txt').write_text('[properties]\nfoo = bar\n')
    assert parse_cmd_line(tmp_path) == set()


# ---------------------------------------------------------------------------
# load_mesonferc_options / save_mesonferc_options
# ---------------------------------------------------------------------------

def test_load_mesonferc_options_basic(tmp_path):
    rc = tmp_path / '.mesonferc'
    rc.write_text('default_builddir = _build\n\n[options]\nb_sanitize = address,undefined\ngen_protobuf = true\n')
    assert load_mesonferc_options(rc) == {'b_sanitize': 'address,undefined', 'gen_protobuf': 'true'}


def test_load_mesonferc_options_missing_file(tmp_path):
    assert load_mesonferc_options(tmp_path / '.mesonferc') == {}


def test_load_mesonferc_options_no_section(tmp_path):
    rc = tmp_path / '.mesonferc'
    rc.write_text('default_builddir = _build\n')
    assert load_mesonferc_options(rc) == {}


def test_save_mesonferc_options_creates_file(tmp_path):
    rc = tmp_path / '.mesonferc'
    save_mesonferc_options(rc, {'b_sanitize': 'address', 'gen_protobuf': 'true'})
    assert '[options]' in rc.read_text()
    assert 'b_sanitize = address' in rc.read_text()


def test_save_mesonferc_options_preserves_top_keys(tmp_path):
    rc = tmp_path / '.mesonferc'
    rc.write_text('default_builddir = _build\n')
    save_mesonferc_options(rc, {'b_sanitize': 'address'})
    text = rc.read_text()
    assert 'default_builddir = _build' in text
    assert 'b_sanitize = address' in text


def test_save_mesonferc_options_replaces_existing_section(tmp_path):
    rc = tmp_path / '.mesonferc'
    rc.write_text('default_builddir = _build\n\n[options]\nold_opt = old\n')
    save_mesonferc_options(rc, {'new_opt': 'new'})
    text = rc.read_text()
    assert 'old_opt' not in text
    assert 'new_opt = new' in text
    assert 'default_builddir = _build' in text


# ---------------------------------------------------------------------------
# find_test_suites
# ---------------------------------------------------------------------------

def test_find_test_suites_basic(tmp_path):
    info = tmp_path / 'meson-info'
    info.mkdir()
    tests = [
        {'name': 't1', 'suite': ['myproject:core']},
        {'name': 't2', 'suite': ['myproject:core']},
        {'name': 't3', 'suite': ['myproject:utils']},
    ]
    (info / 'intro-tests.json').write_text(json.dumps(tests))
    assert find_test_suites(tmp_path) == ['myproject:core', 'myproject:utils']


def test_find_test_suites_preserves_order(tmp_path):
    info = tmp_path / 'meson-info'
    info.mkdir()
    tests = [
        {'name': 't1', 'suite': ['proj:b']},
        {'name': 't2', 'suite': ['proj:a']},
    ]
    (info / 'intro-tests.json').write_text(json.dumps(tests))
    assert find_test_suites(tmp_path) == ['proj:b', 'proj:a']


def test_find_test_suites_missing_file(tmp_path):
    (tmp_path / 'meson-info').mkdir()
    assert find_test_suites(tmp_path) == []


# ---------------------------------------------------------------------------
# find_test_setups
# ---------------------------------------------------------------------------

def test_find_test_setups_basic(tmp_path):
    info = tmp_path / 'meson-info'
    info.mkdir()
    mb = tmp_path / 'meson.build'
    mb.write_text("add_test_setup('valgrind', timeout_multiplier: 2)\n")
    (info / 'intro-buildsystem_files.json').write_text(json.dumps([str(mb)]))
    assert find_test_setups(tmp_path) == ['valgrind']


def test_find_test_setups_multiple(tmp_path):
    info = tmp_path / 'meson-info'
    info.mkdir()
    mb = tmp_path / 'meson.build'
    mb.write_text(
        "add_test_setup('valgrind')\n"
        "add_test_setup(\"asan\", env: e)\n"
    )
    (info / 'intro-buildsystem_files.json').write_text(json.dumps([str(mb)]))
    assert find_test_setups(tmp_path) == ['valgrind', 'asan']


def test_find_test_setups_no_buildsystem_files(tmp_path):
    (tmp_path / 'meson-info').mkdir()
    assert find_test_setups(tmp_path) == []


def test_find_test_setups_missing_source_file(tmp_path):
    info = tmp_path / 'meson-info'
    info.mkdir()
    (info / 'intro-buildsystem_files.json').write_text(
        json.dumps([str(tmp_path / 'nonexistent.build')])
    )
    assert find_test_setups(tmp_path) == []


# ---------------------------------------------------------------------------
# load_project_data
# ---------------------------------------------------------------------------

def _make_info_dir(tmp_path, options=None, meson_info=None, build_files=None, project_info=None):
    info = tmp_path / 'meson-info'
    info.mkdir(exist_ok=True)
    (info / 'intro-buildoptions.json').write_text(json.dumps(options or []))
    (info / 'meson-info.json').write_text(json.dumps(meson_info or {}))
    (info / 'intro-buildsystem_files.json').write_text(json.dumps(build_files or []))
    if project_info is not None:
        (info / 'intro-projectinfo.json').write_text(json.dumps(project_info))
    return info


def test_load_project_data_full(tmp_path):
    mb = tmp_path / 'meson.build'
    mb.write_text("add_test_setup('One_pass')\n")
    options = [{'name': 'opt1', 'type': 'boolean', 'value': True}]
    meson_info = {'directories': {'source': str(tmp_path / 'src')}}
    _make_info_dir(tmp_path, options=options, meson_info=meson_info, build_files=[str(mb)],
                   project_info={'descriptive_name': 'myproject'})

    opts, ts, src, name = load_project_data(tmp_path)
    assert opts == options
    assert ts == ['One_pass']
    assert src == tmp_path / 'src'
    assert name == 'myproject'


def test_load_project_data_missing_files(tmp_path):
    (tmp_path / 'meson-info').mkdir()
    opts, ts, src, name = load_project_data(tmp_path)
    assert opts == []
    assert ts == []
    assert src is None
    assert name is None


def test_load_project_data_no_source_dir_key(tmp_path):
    _make_info_dir(tmp_path, meson_info={'directories': {}})
    _, _, src, _ = load_project_data(tmp_path)
    assert src is None


# ---------------------------------------------------------------------------
# load_mesonferc
# ---------------------------------------------------------------------------

def test_load_mesonferc_missing_file(tmp_path):
    result = load_mesonferc(tmp_path / '.mesonferc')
    assert result == {'default_builddir': None, 'options': {}, 'configs': {}}


def test_load_mesonferc_default_builddir(tmp_path):
    rc = tmp_path / '.mesonferc'
    rc.write_text('default_builddir = _build\n')
    assert load_mesonferc(rc)['default_builddir'] == '_build'


def test_load_mesonferc_quoted_builddir(tmp_path):
    rc = tmp_path / '.mesonferc'
    rc.write_text('default_builddir = "_build"\n')
    assert load_mesonferc(rc)['default_builddir'] == '_build'


def test_load_mesonferc_base_options(tmp_path):
    rc = tmp_path / '.mesonferc'
    rc.write_text('default_builddir = _build\n\n[options]\nbuildtype = debugoptimized\n')
    result = load_mesonferc(rc)
    assert result['options'] == {'buildtype': 'debugoptimized'}


def test_load_mesonferc_ignores_comments(tmp_path):
    rc = tmp_path / '.mesonferc'
    rc.write_text('[options]\n# buildtype = debug\nbuildtype = release\n')
    assert load_mesonferc(rc)['options'] == {'buildtype': 'release'}


def test_load_mesonferc_named_config(tmp_path):
    rc = tmp_path / '.mesonferc'
    rc.write_text(
        'default_builddir = _build\n\n'
        '[config:release]\n'
        'builddir = _build-release\n'
        'buildtype = release\n'
    )
    result = load_mesonferc(rc)
    assert 'release' in result['configs']
    assert result['configs']['release']['builddir'] == '_build-release'
    assert result['configs']['release']['options'] == {'buildtype': 'release'}


def test_load_mesonferc_config_inherits_base_options(tmp_path):
    rc = tmp_path / '.mesonferc'
    rc.write_text(
        '[options]\nprefix = /usr\n\n'
        '[config:debug]\nbuilddir = _build-debug\nbuildtype = debug\n'
    )
    result = load_mesonferc(rc)
    # Caller merges base + config options; verify they are stored separately
    assert result['options'] == {'prefix': '/usr'}
    assert result['configs']['debug']['options'] == {'buildtype': 'debug'}


def test_load_mesonferc_multiple_configs(tmp_path):
    rc = tmp_path / '.mesonferc'
    rc.write_text(
        '[config:debug]\nbuilddir = _build-debug\n\n'
        '[config:release]\nbuilddir = _build-release\n'
    )
    result = load_mesonferc(rc)
    assert set(result['configs']) == {'debug', 'release'}
