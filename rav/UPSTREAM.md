# Staying in sync with upstream scrcpy

TainuiTech is a renamed fork of [Genymobile/scrcpy](https://github.com/Genymobile/scrcpy) (`dev` branch). It includes [PR #7019](https://github.com/Genymobile/scrcpy/pull/7019) (power on the device for a new virtual display).

Because every file, path and identifier was renamed (`scrcpy` → `tainuitech`, `com.genymobile.scrcpy` → `com.tainuitech`), upstream commits can't be merged directly. Instead they are **ported**: each upstream patch is rewritten with the same rules as the original rename (`rav/scripts/rebrand.py`), then applied with `git am -3`.

## Commands

```bash
rav/scripts/port-upstream.sh            # list upstream commits not yet ported
rav/scripts/port-upstream.sh --apply    # port them onto the current branch
rav/scripts/port-upstream.sh --pr 7019  # port the commits of an upstream PR
```

`rav/UPSTREAM_BASE` holds the last upstream `dev` commit that was ported. `--apply` updates it.

## When a patch doesn't apply
`git am` stops on the failing commit. Resolve the conflict, `git add` the files, then `git am --continue`. Use `git am --skip` to drop a commit, for example when upstream merges PR #7019, which is already here. To give up, run `git am --abort`.

Expect conflicts on upstream release commits ("Update links to X"): they edit download links and install sections that TainuiTech removed. Keep our version of those sections and update only the version in the README title.

## Notes
- URLs in patches are not rewritten, so links to upstream issues stay valid.
- Thread names use the short `tt-` prefix, because names are limited to 15 characters.
- License: scrcpy is Apache-2.0. Keep `LICENSE`, `NOTICE` and upstream copyright notices intact.
