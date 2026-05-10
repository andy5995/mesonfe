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
load_project_data = _mod.load_project_data


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
        assert find_builddir() == Path('_build')


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
# load_project_data
# ---------------------------------------------------------------------------

def test_load_project_data_full(tmp_path):
    info = tmp_path / 'meson-info'
    info.mkdir()

    options = [{'name': 'opt1', 'type': 'boolean', 'value': True}]
    setups = {'valgrind': {'exe_wrapper': []}}
    meson_info = {'directories': {'source': str(tmp_path / 'src')}}

    (info / 'intro-buildoptions.json').write_text(json.dumps(options))
    (info / 'intro-test-setups.json').write_text(json.dumps(setups))
    (info / 'meson-info.json').write_text(json.dumps(meson_info))

    opts, ts, src = load_project_data(tmp_path)
    assert opts == options
    assert ts == setups
    assert src == tmp_path / 'src'


def test_load_project_data_missing_files(tmp_path):
    (tmp_path / 'meson-info').mkdir()
    opts, ts, src = load_project_data(tmp_path)
    assert opts == []
    assert ts == {}
    assert src is None


def test_load_project_data_no_source_dir_key(tmp_path):
    info = tmp_path / 'meson-info'
    info.mkdir()
    (info / 'intro-buildoptions.json').write_text('[]')
    (info / 'intro-test-setups.json').write_text('{}')
    (info / 'meson-info.json').write_text('{"directories": {}}')
    _, _, src = load_project_data(tmp_path)
    assert src is None
