# mesonfe

PyQt5 GUI frontend for the [Meson](https://mesonbuild.com/) build system.
Intended for developers already familiar with Meson. Supports viewing and
editing build options, per-project user-configurable presets, running compile
and install steps and executing test suites.

* [Downloads](https://github.com/andy5995/mesonfe/releases/latest)

## Disclaimer

This project is not affiliated with or endorsed by the Meson project or its
developers.

## Dependencies

- Python 3
- PyQt5
- platformdirs
- meson

## Usage

```sh
mesonfe                    # auto-detect build directory via .mesonferc or open picker
mesonfe /path/to/builddir  # explicit build directory
```

If no build directory is found automatically, the window opens and you can use
**File → Open Build Directory…** to select one.

To set up a new build from scratch, use **File → Open Project Directory…**
to select a source directory. This enables the **Setup** tab, where you can
specify a build directory and extra args before running `meson setup`. After
a successful setup, the new build directory is opened automatically.

## Configuration

`mesonfe` looks for `.mesonferc` in the current directory or one level up. On
first run a template is written to the mesonfe configuration directory; the
Setup tab's **Create .mesonferc** copies it into the current source directory.

```ini
default_builddir=_build

[options]
# buildtype=debugoptimized

[config:debug]
builddir=_build-debug
# buildtype=debug

[config:release]
builddir=_build-release
# buildtype=release
# prefix=/usr
```

Named configurations appear in the Setup tab's **Configuration** combo.
Selecting one fills in the build directory and merges base `[options]` with
the config's own options.

## Running without installing

Clone the repository and run the script directly:

```sh
./mesonfe
```

## Build & install

A build step is only needed for a system-wide install:

```sh
meson setup _build
meson install -C _build
```

Installs `mesonfe` to `bindir` (default `/usr/local/bin`), a `mesonfe` Python
package to the Python site-packages directory, and a `.desktop` file and icon
for desktop launcher integration. Requires `pytest` for `ninja test`.
