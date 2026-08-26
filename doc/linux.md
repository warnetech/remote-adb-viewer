# On Linux

## Install

### From source

TainuiTech has no prebuilt releases yet. Packages and downloads named `scrcpy` install upstream scrcpy, whose server is not compatible with TainuiTech (different Java package and socket names).


To install the latest release from `master`, follow this simplified process.

First, you need to install the required packages:

```bash
# for Debian/Ubuntu
sudo apt install ffmpeg libsdl3-0 libusb-1.0-0 adb wget va-driver-all \
                 gcc git pkg-config meson ninja-build libsdl3-dev \
                 libavcodec-dev libavdevice-dev libavformat-dev libavutil-dev \
                 libswresample-dev libusb-1.0-0-dev libv4l-dev libdrm-dev
```

The server is built from source, so you also need Java and the Android SDK
(`ANDROID_SDK_ROOT` set; see [build.md](build.md)).

Then clone the repo and execute the installation script
([source](/install_release.sh)):

```bash
git clone https://github.com/warnetech/remote-adb-viewer tainuitech
cd tainuitech
./install_release.sh
```

When a new release is out, update the repo and reinstall:

```bash
git pull
./install_release.sh
```

To uninstall:

```bash
sudo ninja -Cbuild-auto uninstall
```

_Note that this simplified process only works for released versions (it
downloads a prebuilt server binary), so for example you can't use it for testing
the development branch (`dev`)._

_See [build.md](build.md) to build and install the app manually._


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
