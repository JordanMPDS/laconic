#!/usr/bin/env bash
# Reclaim the scratch worktrees a round leaves behind.
#
# A round that compares an edit against master generates both sides at once, so
# it adds a second worktree and generates the control from there. The skill has
# told rounds to put it under /tmp since round 57. **On this machine /tmp is
# tmpfs, so that worktree is RAM** — 145 MiB of it, held until something removes
# the directory, and nothing did. On 2026-09-15 seven mutation copies and two
# spent control worktrees held 1.7 GiB of a 7.6 GiB machine, and the supervisor
# was killed for low memory at 04:58 with no generation shard running at all.
#
# A round cannot clean up after itself, because the way a round ends badly is
# being killed, and a killed process runs no trap. So the reclaim belongs to the
# next process rather than the last one — the same reasoning that puts the
# release check and the candidate cap in a command the loop runs at the top of
# an iteration rather than in a paragraph asking it to remember.
#
#   bash tools/reclaim-scratch.sh            # reclaim what is safe, report the rest
#   bash tools/reclaim-scratch.sh --dry-run  # say what would go, remove nothing
#   bash tools/reclaim-scratch.sh --selftest
#
# A worktree is reclaimed only when all four hold, and the reasons a tree is
# kept are printed rather than swallowed:
#
#   1. It is a registered worktree of this repository and not the main one.
#   2. No process has its working directory inside it. This is the liveness
#      check and it is exact: a round generating from a control worktree has a
#      run.py cwd'd there for hours, and that round is the thing most expensive
#      to destroy in this repository.
#   3. It holds no untracked files. Modified tracked files are reproducible from
#      git and a control worktree always has some; an untracked file is the one
#      thing in a scratch tree that may exist nowhere else.
#   4. Its HEAD is an ancestor of origin/master, so it carries no commit that
#      has not landed.
set -uo pipefail

# Overridden by the selftest. Reading /proc is the whole implementation: a
# process that died left no cwd, which is exactly the tree we want to reclaim.
process_cwds() { readlink -f /proc/*/cwd 2>/dev/null; }

tree_is_live() { # <absolute path> -> 0 if some process sits inside it
  local d=$1 cwds
  cwds=$(process_cwds)
  printf '%s\n' "$cwds" | grep -qxF -- "$d" && return 0
  printf '%s\n' "$cwds" | grep -qF -- "$d/" && return 0
  return 1
}

# `git worktree list --porcelain` prints a `worktree <path>` line per tree, the
# main one first. Paths can contain spaces, so read the line rather than cut it.
other_worktrees() { # -> one absolute path per line, main worktree excluded
  git worktree list --porcelain 2>/dev/null \
    | sed -n 's/^worktree //p' \
    | tail -n +2
}

reclaimable() { # <path> -> 0 if safe to remove; prints the reason when not
  local d=$1
  if tree_is_live "$d"; then
    echo "  kept $d — a process is working inside it"
    return 1
  fi
  if [ -n "$(git -C "$d" ls-files --others --exclude-standard 2>/dev/null)" ]; then
    echo "  kept $d — it holds untracked files, which may exist nowhere else"
    return 1
  fi
  if ! git -C "$d" merge-base --is-ancestor HEAD origin/master 2>/dev/null; then
    echo "  kept $d — its HEAD is not an ancestor of origin/master"
    return 1
  fi
  return 0
}

if [ "${1:-}" = "--selftest" ]; then
  failed=0
  check() { # name, expected-grep, actual
    if printf '%s' "$3" | grep -qE "$2"; then return 0; fi
    failed=$((failed + 1))
    printf 'FAIL %s\n  wanted /%s/ in:\n%s\n' "$1" "$2" "$3"
  }
  checkno() { # name, forbidden-grep, actual
    if ! printf '%s' "$3" | grep -qE "$2"; then return 0; fi
    failed=$((failed + 1))
    printf 'FAIL %s\n  did not want /%s/ in:\n%s\n' "$1" "$2" "$3"
  }
  checkst() { # name, expected-status, actual-status
    if [ "$2" = "$3" ]; then return 0; fi
    failed=$((failed + 1))
    printf 'FAIL %s\n  wanted exit %s, got %s\n' "$1" "$2" "$3"
  }

  tmp=$(mktemp -d) || exit 1
  trap 'rm -rf "$tmp"' EXIT

  # A real repository with a real origin, because every predicate here is a git
  # question and a stub would only test the stub.
  export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t \
         GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
  git init -q --bare "$tmp/origin.git"
  git clone -q "$tmp/origin.git" "$tmp/repo" 2>/dev/null
  cd "$tmp/repo" || exit 1
  git config user.email t@t; git config user.name t
  echo one > a.txt; git add a.txt; git commit -q -m one
  git branch -M master; git push -q -u origin master 2>/dev/null
  mkdir -p tools; cp "$OLDPWD/$0" tools/reclaim-scratch.sh 2>/dev/null \
    || cp "$(dirname "$0")/reclaim-scratch.sh" tools/reclaim-scratch.sh
  # The loop works a round on its own branch, which is what leaves master free
  # for the control worktree to take. A main worktree sitting on master makes
  # every `git worktree add master` below fail, and the first version of this
  # selftest hid that under `-q` and built no fixtures at all.
  git checkout -q -b work

  for w in spent live untracked; do
    git worktree add -q --detach "$tmp/$w" master || { echo "FIXTURE $w"; exit 1; }
  done
  git worktree add -q -b ahead "$tmp/ahead" master || { echo "FIXTURE ahead"; exit 1; }

  # The shapes the archive actually produced: a control worktree whose tracked
  # files were edited, one with a file that exists nowhere else, and one holding
  # a commit that never landed.
  echo two > "$tmp/spent/a.txt"
  echo two > "$tmp/untracked/a.txt"; echo x > "$tmp/untracked/notes.md"
  echo three > "$tmp/ahead/a.txt"
  git -C "$tmp/ahead" commit -q -am ahead

  # The liveness check, driven directly. `sleep` in a selftest is a flake
  # waiting to happen, so the source of cwds is a function the test replaces.
  process_cwds() { printf '%s\n' "$tmp/live/evals/bench"; }
  tree_is_live "$tmp/live" && st=0 || st=1
  checkst "a process cwd deep inside a tree makes it live" 0 "$st"
  tree_is_live "$tmp/spent" && st=0 || st=1
  checkst "and a tree nothing sits in is not live" 1 "$st"
  # A tree whose path is a prefix of a live one is not itself live.
  process_cwds() { printf '%s\n' "$tmp/live-2"; }
  tree_is_live "$tmp/live" && st=0 || st=1
  checkst "a sibling whose name extends it does not make it live" 1 "$st"

  process_cwds() { printf '%s\n' "$tmp/live"; }
  out=$( (reclaimable "$tmp/spent" && echo YES) 2>&1 )
  check "a spent control worktree is reclaimable" 'YES' "$out"
  out=$( (reclaimable "$tmp/live" && echo YES) 2>&1 )
  check "a live one is kept" 'working inside it' "$out"
  checkno "and not reclaimed" 'YES' "$out"
  out=$( (reclaimable "$tmp/untracked" && echo YES) 2>&1 )
  check "an untracked file keeps the tree" 'untracked files' "$out"
  checkno "and it is not reclaimed" 'YES' "$out"
  out=$( (reclaimable "$tmp/ahead" && echo YES) 2>&1 )
  check "an unlanded commit keeps the tree" 'not an ancestor' "$out"
  checkno "and it is not reclaimed" 'YES' "$out"

  # End to end, which is where the failure that matters would show: a script
  # that reclaims nothing because it enumerated nothing reads exactly like one
  # with nothing to reclaim.
  out=$(PROCESS_CWDS_STUB="$tmp/live" bash tools/reclaim-scratch.sh 2>&1); st=$?
  checkst "a run with something to reclaim exits 0" 0 "$st"
  check "it names the tree it removed" "reclaimed $tmp/spent" "$out"
  check "it reports the megabytes" '[0-9]+ MiB' "$out"
  check "it keeps the live tree" "kept $tmp/live" "$out"
  check "it keeps the untracked tree" "kept $tmp/untracked" "$out"
  check "it keeps the unlanded tree" "kept $tmp/ahead" "$out"
  [ -d "$tmp/spent" ] && { failed=$((failed + 1)); echo "FAIL the spent tree is gone"; }
  [ -d "$tmp/live" ] || { failed=$((failed + 1)); echo "FAIL the live tree survived"; }
  [ -d "$tmp/untracked" ] || { failed=$((failed + 1)); echo "FAIL the untracked tree survived"; }

  out=$(PROCESS_CWDS_STUB="$tmp/live" bash tools/reclaim-scratch.sh 2>&1); st=$?
  check "a second run has nothing left to reclaim" 'nothing to reclaim' "$out"
  checkst "and still exits 0" 0 "$st"

  # --dry-run is the flag a person runs first, so it must not be the flag that
  # deletes the thing they were checking on.
  echo two > "$tmp/untracked/a.txt"; rm "$tmp/untracked/notes.md"
  out=$(PROCESS_CWDS_STUB="$tmp/live" bash tools/reclaim-scratch.sh --dry-run 2>&1)
  check "--dry-run says what would go" "would reclaim $tmp/untracked" "$out"
  [ -d "$tmp/untracked" ] || { failed=$((failed + 1)); echo "FAIL --dry-run deleted it"; }

  [ "$failed" -eq 0 ] && echo "reclaim-scratch.sh selftest: 20/20 passed" \
    || echo "reclaim-scratch.sh selftest: $failed failed"
  exit $([ "$failed" -eq 0 ] && echo 0 || echo 1)
fi

cd "$(dirname "$0")/.." || exit 1

# The selftest drives the real script end to end and needs the liveness answer
# to be deterministic; nothing else sets this. A function definition is not a
# command and cannot be the right-hand side of `&&`, which is how the first
# version of this line silently stopped overriding anything.
if [ -n "${PROCESS_CWDS_STUB:-}" ]; then
  process_cwds() { printf '%s\n' "$PROCESS_CWDS_STUB"; }
fi

dry=
[ "${1:-}" = "--dry-run" ] && dry=1

git fetch -q origin master 2>/dev/null
git worktree prune 2>/dev/null

freed=0
n=0
while IFS= read -r d; do
  [ -n "$d" ] || continue
  [ -d "$d" ] || continue
  if reclaimable "$d"; then
    mib=$(du -sm "$d" 2>/dev/null | cut -f1)
    mib=${mib:-0}
    if [ -n "$dry" ]; then
      echo "  would reclaim $d ($mib MiB)"
    else
      # No `rm -rf` fallback. Everything this script deletes was chosen by four
      # git predicates, so a git that refuses the removal is a reason to stop
      # rather than a reason to reach around it.
      if git worktree remove --force "$d" 2>/dev/null; then
        echo "  reclaimed $d ($mib MiB)"
      else
        echo "  kept $d — git refused to remove it"
        continue
      fi
    fi
    freed=$((freed + mib))
    n=$((n + 1))
  fi
done < <(other_worktrees)

git worktree prune 2>/dev/null

if [ "$n" -eq 0 ]; then
  echo "nothing to reclaim: no spent scratch worktree found."
else
  verb=$([ -n "$dry" ] && echo "would free" || echo "freed")
  echo "$n scratch worktree(s), $verb $freed MiB."
  echo "On this machine /tmp is tmpfs, so that is memory rather than disk."
fi
exit 0
