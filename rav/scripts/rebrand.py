#!/usr/bin/env python3
"""Rename scrcpy identifiers to TainuiTech.

The same rules are used for the one-time rename of this repository and for
porting upstream scrcpy patches (see port-upstream.sh), so the two never drift.

URLs are left untouched: they point at upstream resources (issues, releases,
articles) that keep their original names.

Usage:
    rebrand.py --stdin            # filter text from stdin to stdout
    rebrand.py --repo             # rename tracked files and contents in place
"""

import re
import subprocess
import sys

# Order matters: the Java package must be handled before the bare name.
RULES = [
    # Thread names are limited to 15 chars (asserted in sc_thread_create), so
    # "scrcpy-receiver" becomes "tt-receiver", not "tainuitech-receiver".
    (re.compile(r'(sc_thread_create\([^;]*?)"scrcpy-'), r'\1"tt-'),
    (re.compile(r"com\.genymobile\.scrcpy"), "com.tainuitech"),
    (re.compile(r"com/genymobile/scrcpy"), "com/tainuitech"),
    (re.compile(r"com\.genymobile\b"), "com.tainuitech"),
    (re.compile(r"SCRCPY"), "TAINUITECH"),
    (re.compile(r"Scrcpy"), "TainuiTech"),
    (re.compile(r"scrcpy"), "tainuitech"),
]

URL = re.compile(r"""https?://[^\s)>\]"'`]+""")

# Kept as is: upstream legal text and this tool's own references to upstream.
EXCLUDED_PREFIXES = ("LICENSE", "NOTICE", "rav/")


def rebrand_text(text):
    out = []
    pos = 0
    for m in URL.finditer(text):
        out.append(_apply(text[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(_apply(text[pos:]))
    return "".join(out)


def _apply(chunk):
    for pattern, repl in RULES:
        chunk = pattern.sub(repl, chunk)
    return chunk


def _git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True,
                          text=True).stdout


def rebrand_repo():
    files = [f for f in _git("ls-files", "-z").split("\0")
             if f and not f.startswith(EXCLUDED_PREFIXES)]

    for path in files:
        with open(path, "rb") as f:
            data = f.read()
        if b"\0" in data:
            continue  # binary
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        new = rebrand_text(text)
        if new != text:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(new)

    for path in files:
        new_path = _apply(path)
        if new_path != path:
            parent = new_path.rsplit("/", 1)[0] if "/" in new_path else ""
            if parent:
                subprocess.run(["mkdir", "-p", parent], check=True)
            _git("mv", path, new_path)


def main():
    if sys.argv[1:] == ["--stdin"]:
        sys.stdout.write(rebrand_text(sys.stdin.read()))
    elif sys.argv[1:] == ["--repo"]:
        rebrand_repo()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
