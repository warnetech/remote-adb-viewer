# On Windows

## Install

### From source

TainuiTech has no prebuilt releases yet. Packages and downloads named `scrcpy` install upstream scrcpy, whose server is not compatible with TainuiTech (different Java package and socket names).

See [build.md](build.md) to build and install the app.


## Run

_Make sure that your device meets the [prerequisites](/README.md#prerequisites)._

TainuiTech is a command line application: it is mainly intended to be executed from
a terminal with command line arguments.

To open a terminal at the expected location, double-click on
`open_a_terminal_here.bat` in your tainuitech directory, then type your command. For
example, without arguments:

```bash
tainuitech
```

or with arguments (here to disable audio and record to `file.mkv`):

```bash
tainuitech --no-audio --record=file.mkv
```

Documentation for command line arguments is available:
 - `tainuitech --help`
 - on [github](/README.md)

If you plan to always use the same arguments, create a file `mytainuitech.bat`
(enable [show file extensions] to avoid confusion) containing your command, For
example:

```bash
tainuitech --prefer-text --turn-screen-off --stay-awake
```

Add `--pause-on-exit=if-error` if you want the console to remain open when
tainuitech fails:

```bash
tainuitech --prefer-text --turn-screen-off --stay-awake --pause-on-exit=if-error
```

[show file extensions]: https://www.howtogeek.com/205086/beginner-how-to-make-windows-show-file-extensions/

Then just double-click on that file to run it.

To start tainuitech without opening a terminal, double-click `tainuitech-noconsole.vbs`
(note that errors won't be shown). To pass arguments, edit (a copy of)
`tainuitech-noconsole.vbs` and add the desired arguments.
