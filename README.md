# mesonfe

A PyQt5 GUI frontend for browsing and editing [Meson](https://mesonbuild.com/) build options.

## Features

- Displays all build options with their current values and descriptions
- Highlights options that differ from their defaults (from `meson_options.txt` and `meson-private/cmd_line.txt`)
- Filter options by name or description
- Apply changes via `meson configure`
- **Build menu**
  - Save current non-default options to `.mesonferc`
  - Run `meson setup` using saved options from `.mesonferc`, with a preview of what will be applied and what will be reset
- **Tests menu** — select and run tests with optional verbose output:
  - Default (all tests)
  - Individual suites
  - Named test setups (`add_test_setup`)
  - Sequential output streamed in a single window

## Dependencies

- Python 3
- PyQt5
- meson

## Usage

```sh
mesonfe                    # auto-detect build directory via .mesonferc or builddir/
mesonfe /path/to/builddir  # explicit build directory
```

The build directory must already exist (run `meson setup` first).

## Configuration

Place `.mesonferc` in your project root or its parent. `mesonfe` walks up one directory level when searching for it.

```ini
defaultbuilddirdir = builddir
```

The **Build → Save options to .mesonferc** action adds an `[options]` section to this file:

```ini
defaultbuilddirdir = builddir

[options]
b_sanitize = address,undefined
gen_protobuf = true
```

**Build → Setup from .mesonferc** runs `meson setup` with these options as `-D` flags, showing a confirmation first so you can see what will be applied and what currently-set options are not in the file (and will reset to default).

## Build & install

```sh
meson setup builddir
meson install -C builddir
```

Installs `mesonfe` to `bindir` (default `/usr/local/bin`). Requires `pytest` for `ninja test`.
