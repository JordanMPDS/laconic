#Requires -Version 5.1
# laconic — emit the active rule set for Claude Code hooks (native Windows).
# Usage: laconic.ps1 start|remind|switch
#   start   print the rule slice for the active level
#   remind  persist any "/laconic <level> [project]" on stdin, print one line
#   switch  persist the same switch and acknowledge it by refusing the turn,
#           for a hook system with no per-turn injection (#16). Prints nothing
#           at all when the prompt is not a switch.
# Prints nothing at all unless a valid level is active.
#
# There is deliberately no subagent mode; see hooks/laconic.sh and issue #6.
#
# This is a port of hooks/laconic.sh and has to stay byte-identical to it in
# behavior: both implementations read and write the same ~/.claude/.laconic-level,
# and a user may switch between WSL and native Windows against the same config
# directory. See docs/windows-support-spec.md for the contract.
param([string]$Mode = '')

$ErrorActionPreference = 'SilentlyContinue'

# The rule slice carries em dashes and arrows, and the flag file must never gain
# a BOM. Pin both ends of the encoding rather than inheriting the console code
# page, which on Windows is still cp1252 by default.
$Utf8NoBom = New-Object System.Text.UTF8Encoding $false
try { [Console]::OutputEncoding = $Utf8NoBom } catch {}

# Write through [Console]::Out, not Write-Output: the output becomes model
# context and PowerShell's own output pipeline would terminate every line with
# CRLF. Stray carriage returns are noise in the prompt.
#
# LACONIC_JSON_PATH wraps the same bytes as a JSON string nested at a dotted key
# path, for hook systems that read a field rather than stdout. Unset or empty is
# the raw path, byte for byte. Kept in step with laconic.sh, which does this in
# awk; see that file's header for why the path is a parameter rather than a
# fixed shape.
#
# ConvertTo-Json does the escaping. It is in PowerShell 5.1, which is what CI
# tests and what ships with Windows, and it handles the quotes, backslashes and
# newlines the rule slice contains on every level. The single trailing newline is
# dropped first so the field carries the text and not the line terminator, which
# is what the awk side does by construction.
function Emit([string]$Text) {
  $path = $env:LACONIC_JSON_PATH
  if ([string]::IsNullOrEmpty($path)) { [Console]::Out.Write($Text); return }
  if ($Text.EndsWith("`n")) { $Text = $Text.Substring(0, $Text.Length - 1) }
  $value = ConvertTo-Json -InputObject $Text -Compress
  $keys = $path -split '\.'
  $pre = ''
  $post = ''
  foreach ($k in $keys) {
    $pre += '{' + (ConvertTo-Json -InputObject $k -Compress) + ':'
    $post += '}'
  }
  [Console]::Out.Write($pre + $value + $post + "`n")
}

# Case-sensitive, like the bash case statement: "Start" is not a mode.
if (@('start', 'remind', 'switch') -cnotcontains $Mode) { exit 0 }

$configDir = if ([string]::IsNullOrEmpty($env:CLAUDE_CONFIG_DIR)) {
  Join-Path $HOME '.claude'
} else {
  $env:CLAUDE_CONFIG_DIR
}
$globalFlag = Join-Path $configDir '.laconic-level'

# The project flag lets one repository run a different level from the machine
# default. CLAUDE_PROJECT_DIR is what Claude Code exports to hooks; $PWD is the
# fallback because Claude Code spawns hooks from the project root anyway, and it
# is what the test suite and a hand-run invocation both see.
$projectDir = if ([string]::IsNullOrEmpty($env:CLAUDE_PROJECT_DIR)) {
  (Get-Location).Path
} else {
  $env:CLAUDE_PROJECT_DIR
}
$projectConfigDir = Join-Path $projectDir '.claude'
$projectFlag = Join-Path $projectConfigDir '.laconic-level'

$rules = Join-Path (Split-Path -Parent $PSScriptRoot) 'rules\laconic.md'

# A symlink on Windows is a reparse point, and so is a directory junction. Test
# the attribute rather than LinkType: the attribute is present on every
# supported PowerShell version and it still reports true for a link whose target
# has been deleted, which is the case the read guard below must not fall through.
function Test-IsLink([string]$Path) {
  try {
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    return (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)
  } catch {
    return $false
  }
}

function Test-IsFile([string]$Path) {
  return (Test-Path -LiteralPath $Path -PathType Leaf)
}

# ASCII, no byte-order mark. PowerShell 5.1's Set-Content and Out-File both add
# one by default, and a BOM would be invisible in an editor while making the
# whitelist reject a flag file that looks correct to the eye.
function Write-Flag([string]$Path, [string]$Dir, [string]$Value) {
  try {
    if (-not (Test-Path -LiteralPath $Dir)) {
      New-Item -ItemType Directory -Path $Dir -Force -ErrorAction Stop | Out-Null
    }
    [System.IO.File]::WriteAllText($Path, $Value, $Utf8NoBom)
    return $true
  } catch {
    return $false
  }
}

# On UserPromptSubmit the hook payload arrives on stdin as JSON. The bash script
# greps the raw payload because jq is not present on many target machines;
# ConvertFrom-Json ships with PowerShell 3.0+, so the Windows side gets a real
# parser for free and the match runs against the prompt field's value alone.
# Anchoring still matters: only a prompt that STARTS with the slash command
# switches the level, so prose like "does /laconic off actually work?" cannot
# flip it, and cannot re-enable the mode after the user set off. "status" is
# absent from the alternation so it cannot be stored. The trailing boundary
# stops "/laconic fullscreen" from being read as "full".
if ($Mode -eq 'remind' -or $Mode -eq 'switch') {
  $switch = ''
  $scoped = $false
  $applied = ''
  try {
    $payload = [Console]::In.ReadToEnd()
    $prompt = (ConvertFrom-Json $payload).prompt
    if ($prompt -is [string]) {
      $m = [regex]::Match($prompt, '^\s*/laconic +(lite|full|ultra|off)( +project)?(\s|$)')
      if ($m.Success) {
        $switch = $m.Groups[1].Value
        $scoped = $m.Groups[2].Success
      }
    }
  } catch {
    $switch = ''
  }

  $target = $globalFlag
  $targetDir = $configDir
  if ($scoped) { $target = $projectFlag; $targetDir = $projectConfigDir }

  # This write precedes the read-path link check below, so it needs its own
  # guard: without it, /laconic ultra against a symlinked flag would write
  # through the link into an attacker-chosen file.
  #
  # Only switch mode reads the result: its acknowledgment is a claim that the
  # level is on disk, so a write that failed, or one refused because the flag is
  # a link, must not produce one. laconic.sh reads the flag back for the same
  # reason, its redirect having no status to test.
  if ($switch -ne '' -and -not (Test-IsLink $target)) {
    if (Write-Flag $target $targetDir $switch) { $applied = $switch }
  }
}

# switch mode ends here, before the level whitelist, because the one switch that
# most needs acknowledging is "off" — and past this point an inactive level is
# silence by design.
#
# Cursor's beforeSubmitPrompt is the only per-turn hook laconic can reach there
# and it injects nothing: it reads `continue`, and a `user_message` shown to the
# user only when the submission is blocked. So the one thing that event can do
# is refuse the /laconic turn and say what happened. That beats writing the flag
# silently — a switch nothing confirms is a weaker form of the silent no-op #2
# exists to eliminate, and under Cursor the new level genuinely does not take
# effect until the next session, which is the part a user has to be told.
#
# Anything that is not a switch prints nothing, and an empty stdout blocks
# nothing. The blast radius of this mode is exactly the prompts that begin
# "/laconic lite|full|ultra|off". The JSON is written out rather than built with
# ConvertTo-Json so that it stays byte-identical to the bash side's printf.
if ($Mode -eq 'switch') {
  if ($applied -eq '') { exit 0 }
  $scope = ''
  if ($scoped) { $scope = ' for this project' }
  [Console]::Out.Write('{"continue":false,"user_message":"laconic: level set to ' +
    $applied + $scope +
    '. Cursor delivers the rules at session start, so open a new chat for it to take effect."}' + "`n")
  exit 0
}

# Resolve which flag is in force. The project flag wins so a repository can run
# a different level from the machine default, including "off".
#
# Never read through a symlinked flag. The whitelist below already stops foreign
# bytes from reaching stdout; this check's real job is the write guard above.
# Do not delete it as redundant. A link at either path fails closed and silences
# the plugin rather than falling through to the other one — the conservative
# direction, and the same behavior the bash script has.
$flag = ''
foreach ($candidate in @($projectFlag, $globalFlag)) {
  if (Test-IsLink $candidate) { exit 0 }
  if (Test-IsFile $candidate) { $flag = $candidate; break }
}

if ($flag -eq '') {
  # Opt-in only: with no flag and no configured default, do nothing.
  if ([string]::IsNullOrEmpty($env:LACONIC_DEFAULT)) { exit 0 }
  # Validate before persisting. An unvalidated typo (LACONIC_DEFAULT=fulll)
  # would create a flag file the whitelist rejects forever, and because the file
  # now exists it would never be re-seeded — a silent, permanent brick.
  if (@('lite', 'full', 'ultra', 'off') -cnotcontains $env:LACONIC_DEFAULT) { exit 0 }
  # Seeds the machine flag only. LACONIC_DEFAULT is a per-machine preference,
  # and writing it into whichever repository happens to be open would put a file
  # in the user's working tree that they never asked for.
  if (-not (Write-Flag $globalFlag $configDir $env:LACONIC_DEFAULT)) { exit 0 }
  $flag = $globalFlag
}

# Cap the read and strip everything outside [a-z] so malformed contents cannot
# reach the terminal or the model. The whitelist below is the real gate.
# -creplace, not -replace: PowerShell's operator is case-insensitive by default,
# which would let uppercase bytes survive a filter meant to delete them.
$level = ''
try {
  $bytes = [System.IO.File]::ReadAllBytes($flag)
  $take = [Math]::Min(16, $bytes.Length)
  $level = [System.Text.Encoding]::ASCII.GetString($bytes, 0, $take) -creplace '[^a-z]', ''
} catch {
  exit 0
}

$rank = switch -CaseSensitive ($level) {
  'lite'  { 1 }
  'full'  { 2 }
  'ultra' { 3 }
  default { 0 }
}
if ($rank -eq 0) { exit 0 }

if ($Mode -eq 'remind') {
  Emit "LACONIC MODE ACTIVE ($level). Make fewer claims and keep normal grammar. Cut content, not words.`n"
  exit 0
}

# Keep the statusline badge installed at a stable, version-free path.
#
# Claude Code reads "statusLine" from settings only — a plugin cannot register
# one, and a statusLine command referencing ${CLAUDE_PLUGIN_ROOT} is rejected
# and swallowed, so the badge would silently render nothing. Wiring it up is
# therefore always one manual edit to settings.json. What the plugin can do is
# own the script, so the user's settings point at a path that never carries a
# version and never goes stale.
#
# Only on start, only while a level is active, and never fatal: this exists to
# save the user a copy-paste, so it must not be able to break the rule slice
# below. A linked target is refused for the same reason the flag file is.
if ($Mode -eq 'start') {
  $badgeSrc = Join-Path $PSScriptRoot 'laconic-statusline.ps1'
  $badgeDst = Join-Path $configDir 'laconic-statusline.ps1'
  if ((Test-IsFile $badgeSrc) -and -not (Test-IsLink $badgeDst)) {
    $same = $false
    try {
      if (Test-IsFile $badgeDst) {
        $a = [System.IO.File]::ReadAllBytes($badgeSrc)
        $b = [System.IO.File]::ReadAllBytes($badgeDst)
        $same = ($a.Length -eq $b.Length)
        if ($same) {
          for ($i = 0; $i -lt $a.Length; $i++) {
            if ($a[$i] -ne $b[$i]) { $same = $false; break }
          }
        }
      }
    } catch {
      $same = $false
    }
    if (-not $same) {
      try {
        if (-not (Test-Path -LiteralPath $configDir)) {
          New-Item -ItemType Directory -Path $configDir -Force -ErrorAction Stop | Out-Null
        }
        Copy-Item -LiteralPath $badgeSrc -Destination $badgeDst -Force -ErrorAction Stop
      } catch {}
    }
  }
}

if (-not (Test-IsFile $rules)) { exit 0 }

# Print the shared block (rank 0) plus every block up to the active level.
# ReadAllText, not Get-Content: PowerShell 5.1's Get-Content decodes a
# BOM-less file with the active ANSI code page, which mangles the em dashes.
try {
  $text = [System.IO.File]::ReadAllText($rules, $Utf8NoBom)
} catch {
  exit 0
}

# A trailing newline in the file would split into one empty element past the
# last line, and appending it would add a blank line awk never prints.
$text = ($text -replace "`r", '')
if ($text.EndsWith("`n")) { $text = $text.Substring(0, $text.Length - 1) }

$blockRank = 0
$out = New-Object System.Text.StringBuilder
foreach ($line in ($text -split "`n")) {
  if ($line -ceq '<!-- level:lite -->')  { $blockRank = 1; continue }
  if ($line -ceq '<!-- level:full -->')  { $blockRank = 2; continue }
  if ($line -ceq '<!-- level:ultra -->') { $blockRank = 3; continue }
  if ($blockRank -le $rank) { [void]$out.Append($line).Append("`n") }
}
Emit $out.ToString()
exit 0
