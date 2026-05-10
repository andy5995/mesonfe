# mesonfe

A PyQt5 GUI frontend for browsing and editing [Meson](https://mesonbuild.com/) build options.

## Features

- Displays all build options with their current values and descriptions
- Filter options by name or description
- Apply changes via `meson configure`
- Dockable panel showing options that differ from their defaults
- File, Build, Meson, Tests, and Help menus
- Recently opened build directories

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
default_builddir = builddir
```

**Build → Save options to .mesonferc** adds an `[options]` section with the
current non-default values. **Build → Setup from .mesonferc** runs `meson setup`
using those options, with a confirmation preview.

## Build & install

```sh
meson setup builddir
meson install -C builddir
```

Installs `mesonfe` to `bindir` (default `/usr/local/bin`), a `mesonfe` Python
package to the Python site-packages directory, and a `.desktop` file and icon
for desktop launcher integration. Requires `pytest` for `ninja test`.
