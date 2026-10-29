# On macOS

## Install

### From source

TainuiTech has no prebuilt releases yet. Packages and downloads named `scrcpy` install upstream scrcpy, whose server is not compatible with TainuiTech (different Java package and socket names).

See [build.md](build.md) to build and install the app.


## Run

_Make sure that your device meets the [prerequisites](/README.md#prerequisites)._

Once installed, run from a terminal:

```bash
tainuitech
```

or with arguments (here to disable audio and record to `file.mkv`):

```bash
tainuitech --no-audio --record=file.mkv
```

Documentation for command line arguments is available:
 - `man tainuitech`
 - `tainuitech --help`
 - on [github](/README.md)
