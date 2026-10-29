# Staying in sync with upstream scrcpy

This repo is a fork of [Genymobile/scrcpy](https://github.com/Genymobile/scrcpy) (`dev` branch). It includes [PR #7019](https://github.com/Genymobile/scrcpy/pull/7019) (power on the device for a new virtual display). RAV's own code lives under `rav/` so upstream merges stay conflict-free.

## One-time setup (per clone)

```bash
git remote add upstream https://github.com/Genymobile/scrcpy.git
```

The sync script does this for you if the remote is missing.

## Commands

```bash
rav/scripts/sync-upstream.sh            # list upstream commits we don't have yet
rav/scripts/sync-upstream.sh --merge    # merge upstream/dev into the current branch
rav/scripts/sync-upstream.sh --pr 7019  # merge the latest revision of an upstream PR
```

Then push as usual. The script always **merges** rather than rebasing, so pushed history is never rewritten.

## Notes
- Tags are not fetched (`--no-tags`). Upstream release tags aren't needed here.
- If PR #7019 is merged upstream, `--merge` brings in the final version, and git resolves the duplicate change automatically in most cases.
- License: scrcpy is Apache-2.0. Keep `LICENSE` and upstream copyright notices intact.
