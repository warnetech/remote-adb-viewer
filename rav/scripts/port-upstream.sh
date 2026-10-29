#!/usr/bin/env bash
# Port upstream scrcpy commits into TainuiTech.
#
# Upstream patches use scrcpy names, so they are rewritten with the same rules
# as the original rename (rebrand.py) and applied with `git am -3`.
#
# Usage:
#   rav/scripts/port-upstream.sh            # list upstream commits not yet ported
#   rav/scripts/port-upstream.sh --apply    # port them onto the current branch
#   rav/scripts/port-upstream.sh --pr 7019  # port the commits of an upstream PR
#
# rav/UPSTREAM_BASE records the last upstream/dev commit that was ported.
set -euo pipefail

UPSTREAM_URL="https://github.com/Genymobile/scrcpy.git"
UPSTREAM_BRANCH="dev"

cd "$(git rev-parse --show-toplevel)"
here=rav/scripts
base=$(cat rav/UPSTREAM_BASE)

if ! git remote get-url upstream >/dev/null 2>&1; then
    git remote add upstream "$UPSTREAM_URL"
fi

port() {
    git format-patch --stdout "$1" | python3 "$here/rebrand.py" --stdin | git am -3
}

case "${1:-}" in
    "")
        git fetch -q upstream "$UPSTREAM_BRANCH" --no-tags
        echo "Upstream commits not yet ported ($base..upstream/$UPSTREAM_BRANCH):"
        git log --oneline "$base..upstream/$UPSTREAM_BRANCH"
        ;;
    --apply)
        git fetch -q upstream "$UPSTREAM_BRANCH" --no-tags
        target=$(git rev-parse "upstream/$UPSTREAM_BRANCH")
        # Written first so it survives a conflict; commit it after `git am --continue`.
        echo "$target" > rav/UPSTREAM_BASE
        port "$base..$target"
        git commit -q -m "Record upstream scrcpy port base ${target:0:8}" rav/UPSTREAM_BASE
        ;;
    --pr)
        pr="${2:?usage: $0 --pr <number>}"
        git fetch -q upstream "refs/pull/$pr/head:refs/remotes/upstream/pr-$pr" --no-tags
        port "$(git merge-base "upstream/pr-$pr" "upstream/$UPSTREAM_BRANCH")..upstream/pr-$pr"
        ;;
    *)
        echo "unknown option: $1" >&2
        exit 2
        ;;
esac
