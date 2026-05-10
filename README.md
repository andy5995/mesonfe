# mesonfe

A PyQt5 GUI frontend for browsing and editing [Meson](https://mesonbuild.com/) build options.

## Features

- Displays all build options with their current values and descriptions
- Highlights options changed from their defaults
- Filter options by name or description
- Applies changes via `meson configure`
- Runs named test setups with live output streaming

## Dependencies

- Python 3
- PyQt5
- meson

## Usage

```sh
mesonfe                    # auto-detect build directory via .mesonferc or _build/
mesonfe /path/to/builddir  # explicit build directory
```

The build directory must already exist (run `meson setup` first).

## Configuration

Place `.mesonferc` in your project root or its parent. Supported keys:

```ini
default_builddir = _build
```

If not set, `_build` is used. `mesonfe` walks up one directory level when searching for `.mesonferc`.

## Build & install

```sh
meson setup _build
meson install -C _build
```

Installs `mesonfe` to `bindir` (default `/usr/local/bin`).
