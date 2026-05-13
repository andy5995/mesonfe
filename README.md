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

To set up a new build from scratch, use **File → Open Project Directory…** to
select a source directory. This enables the **Setup** tab, where you can specify
a build directory and extra args before running `meson setup`. After a successful
setup, the new build directory is opened automatically.

## Configuration

Place `.mesonferc` in your project root or its parent. `mesonfe` walks up one
directory level when searching for it.

```ini
default_builddir = _build

[options]
# buildtype = debugoptimized
# prefix = /usr
```

On first run, a template `default.mesonferc` is written to the mesonfe
configuration directory. The **Create .mesonferc** button in the Setup tab
copies it into the current source directory. **Load .mesonferc** reads the file
and populates the build directory and extra args fields.

**Tools → Save options to .mesonferc** saves the current non-default build
options to `.mesonferc` so they can be reproduced later.

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
