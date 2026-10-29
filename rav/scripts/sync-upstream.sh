#!/usr/bin/env bash
# Pull upstream scrcpy changes into the current branch.
#
# Usage:
#   rav/scripts/sync-upstream.sh            # show what upstream has that we don't
#   rav/scripts/sync-upstream.sh --merge    # merge upstream/dev into the current branch
#   rav/scripts/sync-upstream.sh --pr 7019  # merge the latest head of an upstream PR
#
# A merge (never a rebase) keeps our own commits and their hashes intact.
set -euo pipefail

UPSTREAM_URL="https://github.com/Genymobile/scrcpy.git"
UPSTREAM_BRANCH="dev"

cd "$(git rev-parse --show-toplevel)"

if ! git remote get-url upstream >/dev/null 2>&1; then
    git remote add upstream "$UPSTREAM_URL"
    echo "Added remote 'upstream' -> $UPSTREAM_URL"
fi

case "${1:-}" in
    "")
        git fetch upstream "$UPSTREAM_BRANCH" --no-tags
        count=$(git rev-list --count "HEAD..upstream/$UPSTREAM_BRANCH")
        echo "upstream/$UPSTREAM_BRANCH has $count commit(s) not in $(git branch --show-current)."
        git log --oneline "HEAD..upstream/$UPSTREAM_BRANCH" | head -20
        [ "$count" -gt 0 ] && echo "Run with --merge to bring them in."
        ;;
    --merge)
        git fetch upstream "$UPSTREAM_BRANCH" --no-tags
        git merge --no-edit "upstream/$UPSTREAM_BRANCH"
        ;;
    --pr)
        pr="${2:?usage: $0 --pr <number>}"
        git fetch upstream "refs/pull/$pr/head:refs/remotes/upstream/pr-$pr" --no-tags
        git merge --no-edit "upstream/pr-$pr"
        ;;
    *)
        echo "unknown option: $1" >&2
        exit 2
        ;;
esac
