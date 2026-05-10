# mesonfe

A PyQt5 GUI frontend for browsing and editing [Meson](https://mesonbuild.com/) build options.

## Features

- Displays all build options with their current values and descriptions
- **Changed from defaults** — dockable panel (top or bottom) showing options that differ from their defaults; click a row to jump to it in the main table
- Filter options by name or description
- Apply changes via `meson configure`
- **File menu**
  - Open any build directory via a directory picker
  - Recently opened build directories (stored in `~/.config/mesonfe/recent.json`)
- **Build menu**
  - Save current non-default options to `.mesonferc`
  - Run `meson setup` using saved options from `.mesonferc`, with a preview of what will be applied and what will be reset
- **Tests menu** — select and run tests with optional verbose output:
  - Default (all tests)
  - Individual suites
  - Named test setups (`add_test_setup`)
  - Sequential output streamed in a single window
- **Help → About** — shows version

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

The **Build → Save options to .mesonferc** action adds an `[options]` section:

```ini
default_builddir = builddir

[options]
b_sanitize = address,undefined
gen_protobuf = true
```

**Build → Setup from .mesonferc** runs `meson setup` with these options as `-D`
flags, showing a confirmation first so you can see what will be applied and what
currently-set options are not in the file (and will reset to default).

## Build & install

```sh
meson setup builddir
meson install -C builddir
```

Installs `mesonfe` to `bindir` (default `/usr/local/bin`), a `mesonfe` Python
package (containing the version module) to the Python site-packages directory,
and a `.desktop` file to `datadir/applications` for desktop launcher integration.
Requires `pytest` for `ninja test`.
