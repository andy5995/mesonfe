# mesonfe

A PyQt5 GUI frontend for the [Meson](https://mesonbuild.com/) build system.
Browse and edit build options, run compile and install steps, and execute test
suites — all without leaving a graphical interface.

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

## Configuration

Place `.mesonferc` in your project root or its parent. `mesonfe` walks up one
directory level when searching for it.

```ini
default_builddir = _build
```

**Build → Save options to .mesonferc** adds an `[options]` section with the
current non-default values. **Build → Setup from .mesonferc** runs `meson setup`
using those options, with a confirmation preview.

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
