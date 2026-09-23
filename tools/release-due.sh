#!/usr/bin/env bash
# Is a release owed?
#
# The loop's exit condition was a round, not a release. An accept merged and the
# next iteration registered round N+1, so nothing anywhere asked whether the
# thing that just passed every gate had reached a user. On 2026-09-08 round 55
# accepted — the first accept in its family, three bars and two bounds, 1,080
# generations — and its edit sat in master for six days until 0.3.0 swept it up
# for unrelated reasons. Nineteen days and 37 rounds separated 0.2.3 from 0.3.0.
# A rule edit that is merged and unreleased has not improved anything for
# anyone; it is a passing test.
#
# Continuity in this loop is the repository rather than a context window, which
# is what makes throwing the window away free. So the signal has to be legible
# to a fresh process with no memory of the accept: the shipped tree has moved
# since the last release tag. That is one diff. It needs no state file, no issue
# label and no bookkeeping step anyone can forget, and it cannot disagree with
# what actually shipped, because it is computed from what actually shipped.
#
#   bash tools/release-due.sh            # exit 1 if a release is owed
#   bash tools/release-due.sh --selftest
#
# Shipped means what a user installs and runs: rules/, hooks/, skills/,
# commands/ and the manifest. README.md and docs/ are deliberately outside it.
# Prose about the plugin is not the plugin, and a signal that fires on every
# typo is a signal that gets ignored — which is the failure this replaces, not
# a different one.
set -uo pipefail

SHIPPED=(rules hooks skills commands .claude-plugin)
TAG_GLOB='laconic--v*'

# A shipped file added or removed is a new surface — a platform, a hook, a
# skill, a command — and that is a minor. Editing files in place is a patch.
# This reproduces both calls already in the log rather than inventing a third
# rule: 0.3.0 was cut minor because it added three hook files for Codex, Gemini
# and Cursor ("this ships three new agents, not just a rule edit"), and 0.2.3
# was a patch because it changed one line of rules/laconic.md.
bump_kind() { # reads `git diff --name-status` on stdin
  local status rest kind=patch
  while read -r status rest; do
    case "$status" in A*|D*|R*) kind=minor ;; esac
  done
  printf '%s' "$kind"
}

next_version() { # <current> <patch|minor> -> next
  local cur=$1 kind=$2 major minor patch
  major=${cur%%.*}
  patch=${cur##*.}
  minor=${cur#*.}; minor=${minor%.*}
  case "$kind" in
    minor) minor=$((minor + 1)); patch=0 ;;
    patch) patch=$((patch + 1)) ;;
    *) return 1 ;;
  esac
  printf '%s.%s.%s' "$major" "$minor" "$patch"
}

# One field out of one file. `jq` is not a dependency of this repository and is
# not going to become one for this, and the description field carries an escaped
# em dash that a naive whole-file parse has mangled before.
plugin_version() { # <ref>
  git show "$1:.claude-plugin/plugin.json" \
    | sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1
}

# Shipped means merged, so the question is asked of master and never of HEAD.
# On 2026-09-23 the loop started with HEAD on round 76's unmerged branch, which
# carries the candidate edit, and this script reported a release owed: obeying
# it would have shipped an edit no bar had passed. origin/master comes first
# because it is what was pushed, and tools/loop.sh fetches it at the top of
# every iteration; master and then HEAD cover a clone with no remote.
release_ref() {
  local ref
  for ref in origin/master master HEAD; do
    git rev-parse -q --verify "$ref^{commit}" >/dev/null && { echo "$ref"; return; }
  done
}

# `bash tools/release-due.sh --selftest` — the two decisions driven directly,
# then the whole script against a scratch repository. The end-to-end half is
# what catches the bug class that matters here: tag discovery and the diff
# pathspec are the parts that fail silently by reporting "nothing owed".
if [ "${1:-}" = "--selftest" ]; then
  failed=0
  check() { # name, expected-grep, actual
    if printf '%s' "$3" | grep -qE "$2"; then return 0; fi
    failed=$((failed + 1))
    printf 'FAIL %s\n  wanted /%s/ in:\n%s\n' "$1" "$2" "$3"
  }
  checkst() { # name, expected-status, actual-status
    if [ "$2" = "$3" ]; then return 0; fi
    failed=$((failed + 1))
    printf 'FAIL %s\n  wanted exit %s, got %s\n' "$1" "$2" "$3"
  }

  check "an added shipped file is a minor" '^minor$' \
    "$(printf 'M\trules/laconic.md\nA\thooks/cursor-hooks.json\n' | bump_kind)"
  check "a removed shipped file is a minor too" '^minor$' \
    "$(printf 'D\thooks/gemini-settings.json\n' | bump_kind)"
  check "files modified in place are a patch" '^patch$' \
    "$(printf 'M\trules/laconic.md\nM\trules/dist/laconic-full.md\n' | bump_kind)"
  check "a rename carries its similarity score and still reads as a minor" '^minor$' \
    "$(printf 'R100\thooks/old.json\thooks/new.json\n' | bump_kind)"
  check "a minor resets the patch component" '^0\.4\.0$' "$(next_version 0.3.7 minor)"
  check "a patch increments the last component" '^0\.3\.1$' "$(next_version 0.3.0 patch)"
  # Version components are numbers. A string sort would put 0.9 above 0.10.
  check "a two-digit component is arithmetic, not a string" '^0\.10\.0$' \
    "$(next_version 0.9.12 minor)"

  tmp=$(mktemp -d) || exit 1
  trap 'rm -rf "$tmp"' EXIT
  r=$tmp/repo
  mkdir -p "$r/tools" "$r/rules/dist" "$r/hooks" "$r/skills" "$r/commands" \
           "$r/.claude-plugin"
  cp "$0" "$r/tools/release-due.sh"
  printf '{\n  "name": "laconic",\n  "version": "0.3.0"\n}\n' \
    > "$r/.claude-plugin/plugin.json"
  echo 'rule text' > "$r/rules/laconic.md"
  echo 'generated' > "$r/rules/dist/laconic-full.md"
  echo 'prose about the plugin' > "$r/README.md"
  git -C "$r" init -q -b master
  git -C "$r" config user.email selftest@example.invalid
  git -C "$r" config user.name selftest
  git -C "$r" add -A && git -C "$r" commit -qm 'release 0.3.0'
  git -C "$r" tag laconic--v0.3.0
  due() { bash "$r/tools/release-due.sh" 2>&1; }

  out=$(due); st=$?
  check "a tree at its tag owes nothing" 'no release owed' "$out"
  checkst "and says so by exiting 0" 0 "$st"

  echo 'more prose' >> "$r/README.md"
  git -C "$r" commit -qam 'readme'
  out=$(due); st=$?
  check "a README change does not owe a release" 'no release owed' "$out"
  checkst "and still exits 0" 0 "$st"

  # A round branch carries its candidate edit until every bar passes. Checked
  # out, it is HEAD, and it is not shipped.
  git -C "$r" checkout -qb round-99
  echo 'the unaccepted candidate' >> "$r/rules/laconic.md"
  git -C "$r" commit -qam 'round 99 registration'
  out=$(due); st=$?
  check "an unmerged round branch owes nothing" 'no release owed' "$out"
  checkst "and exits 0 with the candidate checked out" 0 "$st"
  git -C "$r" checkout -q master

  # The case this whole script exists for: an accepted edit merged to master.
  echo 'the accepted edit' >> "$r/rules/laconic.md"
  echo 'regenerated' >> "$r/rules/dist/laconic-full.md"
  git -C "$r" add -A && git -C "$r" commit -qm 'round 55 accept'
  out=$(due); st=$?
  check "a merged rule edit owes a release" 'release owed' "$out"
  check "and names the file that moved" 'rules/laconic\.md' "$out"
  check "and recommends a patch" 'recommended bump: patch, 0\.3\.0 to 0\.3\.1' "$out"
  checkst "and exits 1 so a caller can branch on it" 1 "$st"

  echo '{}' > "$r/hooks/cursor-hooks.json"
  git -C "$r" add -A && git -C "$r" commit -qm 'cursor port'
  out=$(due)
  check "a new shipped file makes it a minor" \
    'recommended bump: minor, 0\.3\.0 to 0\.4\.0' "$out"

  # Half a release: the version bumped, the tag never cut. The diff alone reads
  # this as an ordinary patch, so it is tested separately from the diff.
  sed -i 's/0\.3\.0/0.4.0/' "$r/.claude-plugin/plugin.json"
  git -C "$r" commit -qam 'release 0.4.0'
  out=$(due); st=$?
  check "a bump with no tag says to tag it, not to bump again" \
    'no tag laconic--v0\.4\.0' "$out"
  checkst "and owes a release until the tag exists" 1 "$st"

  git -C "$r" tag laconic--v0.4.0
  out=$(due); st=$?
  check "tagging it settles the debt" 'no release owed' "$out"
  checkst "and exits 0" 0 "$st"

  git -C "$r" tag -d laconic--v0.3.0 >/dev/null
  git -C "$r" tag -d laconic--v0.4.0 >/dev/null
  out=$(due); st=$?
  check "a history with no release tag owes one" 'nothing has ever been released' "$out"
  checkst "and exits 1" 1 "$st"

  # A tag that is not ours must not be mistaken for a release. This repository
  # carries `round-29-preregistration` and `preregistration--unread-asks-v2`.
  git -C "$r" tag round-99-preregistration
  out=$(due)
  check "a preregistration tag is not a release" 'nothing has ever been released' "$out"

  [ "$failed" -eq 0 ] && echo "release-due.sh selftest: 24/24 passed" \
    || echo "release-due.sh selftest: $failed failed"
  exit $([ "$failed" -eq 0 ] && echo 0 || echo 1)
fi

cd "$(dirname "$0")/.."

ref=$(release_ref)
version=$(plugin_version "$ref")
tag=$(git describe --tags --abbrev=0 --match "$TAG_GLOB" "$ref" 2>/dev/null) || tag=

if [ -z "$tag" ]; then
  echo "release owed: nothing has ever been released from this history — no $TAG_GLOB tag is reachable from $ref."
  echo "plugin.json says $version."
  exit 1
fi

# A version bumped without a tag is half a release, and the diff below cannot
# see it: if the bump is the only shipped change, the recommendation would read
# "cut 0.4.1" when what is actually missing is the tag for 0.4.0.
if [ "laconic--v$version" != "$tag" ] \
   && ! git rev-parse -q --verify "refs/tags/laconic--v$version" >/dev/null; then
  echo "release owed: plugin.json is $version and there is no tag laconic--v$version."
  echo "The version was bumped without being tagged. Tag it rather than bumping again:"
  echo "  git tag -a laconic--v$version -m 'laconic $version' $(git rev-parse --short "$ref") && git push origin laconic--v$version"
  exit 1
fi

changed=$(git diff --name-status "$tag" "$ref" -- "${SHIPPED[@]}")
if [ -z "$changed" ]; then
  echo "no release owed: $tag is current, and no shipped file has changed on $ref since it."
  exit 0
fi

kind=$(printf '%s\n' "$changed" | bump_kind)
next=$(next_version "$version" "$kind")
count=$(printf '%s\n' "$changed" | wc -l | tr -d ' ')
tagged=$(git log -1 --format=%ad --date=short "$tag")

case "$kind" in
  minor) why="a shipped file was added or removed, so this is a new surface and not only an edit" ;;
  patch) why="every shipped file was modified in place" ;;
esac

echo "release owed: $count shipped file(s) changed on $ref since $tag ($tagged)"
printf '%s\n' "$changed" | sed 's/^/  /'
echo
echo "recommended bump: $kind, $version to $next — $why"
echo "The recommendation is not the decision; say why in the release commit if you differ."
exit 1
