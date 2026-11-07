#Requires -Version 5.1
# Unit checks for hooks/laconic.ps1. No framework: explicit asserts, the same
# cases tests/test_laconic.sh runs against the bash hook, in the same order and
# under the same numbering, so a divergence between the two implementations
# shows up as the same numbered case failing on one platform only.
$ErrorActionPreference = 'SilentlyContinue'

$Utf8NoBom = New-Object System.Text.UTF8Encoding $false
try { [Console]::OutputEncoding = $Utf8NoBom } catch {}

$Root   = Split-Path -Parent $PSScriptRoot
$Script = Join-Path $Root 'hooks\laconic.ps1'

# Windows PowerShell 5.1 is the shipped-with-the-OS target, so prefer it; fall
# back to pwsh so the suite is runnable on a machine that only has PowerShell 7.
$Host_ = if (Get-Command powershell -ErrorAction SilentlyContinue) { 'powershell' } else { 'pwsh' }

function New-TempDir {
  $p = Join-Path ([System.IO.Path]::GetTempPath()) ('laconic-' + [Guid]::NewGuid().ToString('N'))
  New-Item -ItemType Directory -Path $p -Force | Out-Null
  return $p
}

$env:CLAUDE_CONFIG_DIR = New-TempDir
$Flag = Join-Path $env:CLAUDE_CONFIG_DIR '.laconic-level'

# Pin the project directory rather than letting it fall back to the working
# directory. Without this the suite would read whatever .claude/.laconic-level
# happens to sit in the directory it was invoked from, so a developer with a
# project flag set would see unrelated failures.
$env:CLAUDE_PROJECT_DIR = New-TempDir
$ProjectDir  = Join-Path $env:CLAUDE_PROJECT_DIR '.claude'
$ProjectFlag = Join-Path $ProjectDir '.laconic-level'

# No case below wants an inherited default; the two that test seeding set it inline.
Remove-Item Env:\LACONIC_DEFAULT -ErrorAction SilentlyContinue

$script:fails = 0
$script:out = ''
$script:err = ''
$script:rc  = 0

function Fail([string]$Name) { Write-Host "FAIL $Name"; $script:fails++ }
function Ok([string]$Name)   { Write-Host "ok   $Name" }

function Assert-Empty([string]$Name, [string]$Value) {
  if ([string]::IsNullOrEmpty($Value)) { Ok $Name } else { Fail "$Name — expected no output, got: $Value" }
}
function Assert-Has([string]$Name, [string]$Needle, [string]$Haystack) {
  if ($null -ne $Haystack -and $Haystack.Contains($Needle)) { Ok $Name } else { Fail "$Name — output missing: $Needle" }
}
function Assert-Lacks([string]$Name, [string]$Needle, [string]$Haystack) {
  if ($null -ne $Haystack -and $Haystack.Contains($Needle)) { Fail "$Name — output should not contain: $Needle" } else { Ok $Name }
}

# Capture stdout, stderr, and exit status together. Checking stdout alone is not
# enough for the silent cases: a missing script, a syntax error, or a crash all
# produce empty stdout too, so an assert that only reads stdout passes against a
# script that never ran. That is the one guarantee this suite exists to prove.
function Invoke-Hook([string]$Mode, [string]$StdIn = '') {
  $inFile  = Join-Path $env:CLAUDE_CONFIG_DIR '.stdin'
  $outFile = Join-Path $env:CLAUDE_CONFIG_DIR '.stdout'
  $errFile = Join-Path $env:CLAUDE_CONFIG_DIR '.stderr'
  [System.IO.File]::WriteAllText($inFile, $StdIn, $Utf8NoBom)
  $p = Start-Process -FilePath $Host_ `
    -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $Script, $Mode) `
    -RedirectStandardInput $inFile -RedirectStandardOutput $outFile -RedirectStandardError $errFile `
    -NoNewWindow -Wait -PassThru
  $p.WaitForExit()
  $script:out = [System.IO.File]::ReadAllText($outFile)
  $script:err = [System.IO.File]::ReadAllText($errFile)
  $script:rc  = $p.ExitCode
  # The capture files live in CLAUDE_CONFIG_DIR, which some cases enumerate.
  # Leaving them is harmless — nothing reads that directory by wildcard — but
  # the flag-file asserts below are clearer with only the flag present.
  Remove-Item -LiteralPath $inFile, $outFile, $errFile -Force -ErrorAction SilentlyContinue
}

function Assert-Silent([string]$Name) { # deliberate silence, not a crash
  Assert-Empty "$Name (stdout)" $script:out
  Assert-Empty "$Name (stderr)" $script:err
  if ($script:rc -eq 0) { Ok "$Name (rc=0)" } else { Fail "$Name — rc=$($script:rc)" }
}

function Set-Level([string]$Value) { [System.IO.File]::WriteAllText($Flag, $Value, $Utf8NoBom) }
function Set-ProjectLevel([string]$Value) {
  New-Item -ItemType Directory -Path $ProjectDir -Force | Out-Null
  [System.IO.File]::WriteAllText($ProjectFlag, $Value, $Utf8NoBom)
}
function Clear-Project { Remove-Item -LiteralPath $ProjectDir -Recurse -Force -ErrorAction SilentlyContinue }
function Get-FlagText([string]$Path) {
  try { return [System.IO.File]::ReadAllText($Path) } catch { return '' }
}
# A symlink needs SeCreateSymbolicLinkPrivilege, which the GitHub Actions Windows
# runner has. Fail loudly rather than skipping if it is unavailable: the symlink
# refusal is an acceptance criterion, and a silently skipped security assert is
# indistinguishable from a passing one.
function New-Link([string]$Path, [string]$Target, [string]$Name) {
  New-Item -ItemType SymbolicLink -Path $Path -Value $Target -Force -ErrorAction SilentlyContinue | Out-Null
  if (-not (Test-Path -LiteralPath $Path)) {
    Fail "$Name — could not create a symlink to test with (privilege missing)"
    return $false
  }
  return $true
}

# 1. No flag file and no default: the plugin is inert.
Remove-Item -LiteralPath $Flag -Force -ErrorAction SilentlyContinue
Invoke-Hook 'start'
Assert-Silent 'no flag file'

# 2. off means off. The off-switch regression.
Set-Level 'off'
Invoke-Hook 'start'
Assert-Silent 'level off'

# 3. Garbage in the flag file is rejected by the whitelist, not echoed.
Set-Level 'ultra; rm -rf /'
Invoke-Hook 'start'
Assert-Silent 'malformed level'

# 4. lite gets the shared and lite blocks only.
Set-Level 'lite'
Invoke-Hook 'start'
Assert-Has   'lite has shared block'  'fewer claims' $out
Assert-Has   'lite has lite block'    'No preamble' $out
Assert-Lacks 'lite omits full block'  'One recommendation, not a survey' $out
Assert-Lacks 'lite omits ultra block' 'The answer alone' $out

# 5. full gets shared + lite + full, not ultra.
Set-Level 'full'
Invoke-Hook 'start'
Assert-Has   'full has lite block'    'No preamble' $out
Assert-Has   'full has full block'    'One recommendation, not a survey' $out
Assert-Lacks 'full omits ultra block' 'The answer alone' $out

# 6. ultra is cumulative: all three blocks.
Set-Level 'ultra'
Invoke-Hook 'start'
Assert-Has 'ultra has lite block'  'No preamble' $out
Assert-Has 'ultra has full block'  'One recommendation, not a survey' $out
Assert-Has 'ultra has ultra block' 'The answer alone' $out

# 7. subagent is not a mode. It was one until issue #6 measured the path and
# found the injected slice bought nothing a parent model could use, so the
# script must now treat it exactly like any other unknown argument: silence.
# Asserted rather than assumed, because the mode gate fails open by design and
# a reinstated mode would otherwise show no symptom.
Invoke-Hook 'subagent'
Assert-Lacks 'subagent emits no rules' 'The answer alone' $out
if ([string]::IsNullOrEmpty($out)) { Ok 'subagent emits nothing at all' } else { Fail 'subagent emits nothing at all' }

# 8. remind is one line, not the whole rule set.
Set-Level 'full'
Invoke-Hook 'remind' '{"prompt":"fix the test"}'
Assert-Has   'remind names the level' 'LACONIC MODE ACTIVE (full)' $out
Assert-Lacks 'remind is not the rules' 'No preamble' $out
# The per-turn reminder itself must not be a telegraphic fragment — the exact
# defect this plugin exists to avoid, repeated on every single turn.
Assert-Has 'reminder text is a full sentence, not a fragment' `
  'Make fewer claims and keep normal grammar' $out
# The reminder is model context, so it must end in a bare newline. PowerShell's
# own output pipeline would write CRLF here and the carriage return would be
# noise in the prompt.
Assert-Lacks 'reminder line has no carriage return' "`r" $out

# 9. A /laconic switch in the payload persists.
Invoke-Hook 'remind' '{"prompt":"/laconic ultra"}'
Assert-Has 'switch persists to flag' 'ultra' (Get-FlagText $Flag)
Assert-Has 'switch reports new level' 'LACONIC MODE ACTIVE (ultra)' $out

# 10. /laconic off both persists and silences in the same turn. The central
# promise of the whole plugin, so it gets full stdout/stderr/exit coverage
# rather than a stdout-only check.
Invoke-Hook 'remind' '{"prompt":"/laconic off"}'
Assert-Has    'off persists to flag' 'off' (Get-FlagText $Flag)
Assert-Silent 'off silences immediately'

# 11. /laconic status must not be mistaken for a level.
Set-Level 'full'
Invoke-Hook 'remind' '{"prompt":"/laconic status"}'
Assert-Has 'status leaves level alone' 'full' (Get-FlagText $Flag)

# 12. LACONIC_DEFAULT seeds the flag when absent.
Remove-Item -LiteralPath $Flag -Force -ErrorAction SilentlyContinue
$env:LACONIC_DEFAULT = 'full'
Invoke-Hook 'start'
Remove-Item Env:\LACONIC_DEFAULT -ErrorAction SilentlyContinue
Assert-Has 'default seeds flag' 'full' (Get-FlagText $Flag)
Assert-Has 'default emits rules' 'One recommendation, not a survey' $out

# 12b. The seeded flag carries no byte-order mark. Set-Content and Out-File both
# add one on PowerShell 5.1, and a BOM would be invisible in an editor while the
# whitelist rejected the file forever.
$seeded = [System.IO.File]::ReadAllBytes($Flag)
if ($seeded.Length -eq 4 -and $seeded[0] -eq [byte][char]'f') {
  Ok 'seeded flag file has no BOM'
} else {
  Fail "seeded flag file should be the 4 ASCII bytes of 'full', got $($seeded.Length) bytes starting 0x$('{0:X2}' -f $seeded[0])"
}

# 13. A symlinked flag is refused rather than dereferenced.
Remove-Item -LiteralPath $Flag -Force -ErrorAction SilentlyContinue
$decoy = Join-Path $env:CLAUDE_CONFIG_DIR 'decoy'
[System.IO.File]::WriteAllText($decoy, 'full', $Utf8NoBom)
if (New-Link $Flag $decoy 'symlinked flag emits nothing') {
  Invoke-Hook 'start'
  Assert-Silent 'symlinked flag emits nothing'
}
Remove-Item -LiteralPath $Flag -Force -ErrorAction SilentlyContinue

# 14. The remind-mode write guard: never write THROUGH a symlinked flag. Without
# this, /laconic ultra would clobber the link target and the read-path check
# would then exit silently, so no other assert in this suite would notice. The
# refusal is reported rather than silent, or the model confirms the switch (#426).
[System.IO.File]::WriteAllText($decoy, 'keep', $Utf8NoBom)
if (New-Link $Flag $decoy 'symlinked flag on remind') {
  Invoke-Hook 'remind' '{"prompt":"/laconic ultra"}'
  Assert-Has 'symlinked flag on remind reports the refusal' `
    "the switch to ultra was not applied, because $Flag is a symlink" $out
  Assert-Empty 'symlinked flag on remind (stderr)' $err
  Assert-Has 'symlinked flag not written through' 'keep' (Get-FlagText $decoy)
}
Remove-Item -LiteralPath $Flag -Force -ErrorAction SilentlyContinue

# 15. Prose mentioning the command must not switch the level. A prompt that only
# talks about /laconic — including one asking whether "off" works — must leave
# the stored level alone. Otherwise prompt text can re-enable the mode after
# off, which is the exact defect this plugin exists to avoid.
Set-Level 'full'
Invoke-Hook 'remind' '{"prompt":"does /laconic off actually work?"}'
Assert-Has 'prose does not switch level' 'full' (Get-FlagText $Flag)
Invoke-Hook 'remind' '{"prompt":"the docs say run /laconic lite to switch"}'
Assert-Has 'prose mid-sentence does not switch' 'full' (Get-FlagText $Flag)
Invoke-Hook 'remind' '{"cwd":"/home/jordan/projects/laconic","prompt":"off topic"}'
Assert-Has 'path containing laconic does not switch' 'full' (Get-FlagText $Flag)

# 16. A real slash command still switches, including with extra spaces.
Invoke-Hook 'remind' '{"session_id":"x","prompt":"/laconic  lite"}'
Assert-Has 'real command still switches' 'lite' (Get-FlagText $Flag)

# 17. An invalid LACONIC_DEFAULT must not create a flag file at all — a persisted
# typo would be rejected by the whitelist forever with no way to re-seed.
Remove-Item -LiteralPath $Flag -Force -ErrorAction SilentlyContinue
$env:LACONIC_DEFAULT = 'fulll'
Invoke-Hook 'start'
Remove-Item Env:\LACONIC_DEFAULT -ErrorAction SilentlyContinue
Assert-Silent 'invalid default emits nothing'
if (Test-Path -LiteralPath $Flag) { Fail 'invalid default must not create the flag file' } else { Ok 'invalid default leaves no flag file' }

# 18. An unknown mode does nothing rather than falling through to the rule slice.
Set-Level 'ultra'
Invoke-Hook 'bogus'
Assert-Silent 'unknown mode'

# 19. The level alternation must not prefix-match: an unrecognized argument that
# merely starts with a real level word must not switch anything. Without a
# trailing boundary, "/laconic fullscreen" would set "full" and "/laconic
# offline" would re-enable the mode right after the user turned it off.
Set-Level 'full'
Invoke-Hook 'remind' '{"prompt":"/laconic fullscreen"}'
Assert-Has 'fullscreen does not switch' 'full' (Get-FlagText $Flag)
Invoke-Hook 'remind' '{"prompt":"/laconic ultraviolet"}'
Assert-Has 'ultraviolet does not switch' 'full' (Get-FlagText $Flag)
Invoke-Hook 'remind' '{"prompt":"/laconic offline"}'
Assert-Has 'offline does not switch (re-enable-after-off case)' 'full' (Get-FlagText $Flag)

# 20. A real switch still works with the trailing-boundary fix in place.
Set-Level 'ultra'
Invoke-Hook 'remind' '{"prompt":"/laconic full"}'
Assert-Has 'full still switches' 'full' (Get-FlagText $Flag)
Invoke-Hook 'remind' '{"prompt":"/laconic  lite"}'
Assert-Has 'two-space lite still switches' 'lite' (Get-FlagText $Flag)

# 21. A leading space before the slash command still switches (pasted text).
Set-Level 'ultra'
Invoke-Hook 'remind' '{"prompt":" /laconic full"}'
Assert-Has 'leading-space command still switches' 'full' (Get-FlagText $Flag)

# --- project-level flag ---
# A repository may run a different level from the machine default. The project
# flag wins; everything the global flag already promised applies to it too.

# 22. The project flag overrides the global one.
Clear-Project
Set-Level 'lite'
Set-ProjectLevel 'ultra'
Invoke-Hook 'start'
Assert-Has   'project flag wins over global' 'The answer alone' $out
Assert-Lacks 'global level not used when project flag is set' `
  'Lite is normal professional prose' $out

# 23. Project off beats global full. The off-switch regression, per project:
# a repository where you want full explanations must be able to say so even
# though the machine default is on.
Set-Level 'full'
Set-ProjectLevel 'off'
Invoke-Hook 'start'
Assert-Silent 'project off overrides global full'

# 24. Global still applies when the project has no flag. The existing behavior
# must survive the new lookup.
Clear-Project
Set-Level 'full'
Invoke-Hook 'start'
Assert-Has 'global level still applies with no project flag' `
  'One recommendation, not a survey' $out

# 25. "/laconic <level> project" writes the project flag and leaves the machine
# flag alone.
Clear-Project
Set-Level 'full'
Invoke-Hook 'remind' '{"prompt":"/laconic ultra project"}'
Assert-Has 'project scope writes the project flag' 'ultra' (Get-FlagText $ProjectFlag)
Assert-Has 'project scope leaves the global flag alone' 'full' (Get-FlagText $Flag)
Assert-Has 'project scope reports the project level' 'LACONIC MODE ACTIVE (ultra)' $out

# 26. Without the suffix the write still goes to the machine flag, so existing
# muscle memory keeps working.
Clear-Project
Set-Level 'full'
Invoke-Hook 'remind' '{"prompt":"/laconic lite"}'
Assert-Has 'unscoped switch writes the global flag' 'lite' (Get-FlagText $Flag)
if (Test-Path -LiteralPath $ProjectFlag) {
  Fail 'unscoped switch must not create a project flag'
} else {
  Ok 'unscoped switch creates no project flag'
}

# 27. Garbage in the project flag is rejected by the whitelist and never echoed,
# exactly as it is in the global flag. It also fails closed rather than falling
# through to a valid global level — a project flag that exists is the answer,
# even when its contents are junk.
Clear-Project
Set-Level 'full'
Set-ProjectLevel 'ultra; rm -rf /'
Invoke-Hook 'start'
Assert-Silent 'malformed project level'

# 28. A symlinked project flag is refused, and refusal wins over a valid global
# flag. Falling through would let a planted symlink downgrade the guarantee to
# whatever the machine default happens to be.
Clear-Project
Set-Level 'full'
New-Item -ItemType Directory -Path $ProjectDir -Force | Out-Null
$projectDecoy = Join-Path $env:CLAUDE_PROJECT_DIR 'decoy'
[System.IO.File]::WriteAllText($projectDecoy, 'ultra', $Utf8NoBom)
if (New-Link $ProjectFlag $projectDecoy 'symlinked project flag emits nothing') {
  Invoke-Hook 'start'
  Assert-Silent 'symlinked project flag emits nothing'

  # 29. The remind-mode write guard applies to the project path too. Without it,
  # "/laconic ultra project" would clobber the link target.
  Invoke-Hook 'remind' '{"prompt":"/laconic lite project"}'
  Assert-Has 'symlinked project flag on remind reports the refusal' `
    "the switch to lite was not applied, because $ProjectFlag is a symlink" $out
  Assert-Has 'symlinked project flag not written through' 'ultra' (Get-FlagText $projectDecoy)
}
Clear-Project
Remove-Item -LiteralPath $projectDecoy -Force -ErrorAction SilentlyContinue

# 30. LACONIC_DEFAULT seeds the machine flag only. Seeding the project flag
# would drop a file into the user's working tree that they never asked for.
Clear-Project
Remove-Item -LiteralPath $Flag -Force -ErrorAction SilentlyContinue
$env:LACONIC_DEFAULT = 'full'
Invoke-Hook 'start'
Remove-Item Env:\LACONIC_DEFAULT -ErrorAction SilentlyContinue
Assert-Has 'default still seeds the global flag' 'full' (Get-FlagText $Flag)
if (Test-Path -LiteralPath $ProjectFlag) {
  Fail 'LACONIC_DEFAULT must not create a project flag'
} else {
  Ok 'LACONIC_DEFAULT creates no project flag'
}

# 31. The scope suffix needs the same trailing boundary the level words have.
# "projectile" must not be read as "project", or an unscoped switch would
# silently write into the repository instead of the machine flag.
Clear-Project
Set-Level 'full'
Invoke-Hook 'remind' '{"prompt":"/laconic ultra projectile"}'
Assert-Has 'projectile switches the global flag' 'ultra' (Get-FlagText $Flag)
if (Test-Path -LiteralPath $ProjectFlag) {
  Fail 'projectile must not be read as project scope'
} else {
  Ok 'projectile is not project scope'
}

# 32. Prose naming the scope must not switch anything either.
Set-Level 'full'
Invoke-Hook 'remind' '{"prompt":"can I run /laconic ultra project in one repo only?"}'
Assert-Has 'prose naming the scope does not switch' 'full' (Get-FlagText $Flag)
Clear-Project

# --- statusline badge install ---
# Claude Code reads statusLine from settings and rejects the field in a plugin
# manifest, so the settings.json edit cannot be automated. Owning the script can
# be, and that is what removes the versioned plugin path from the user's
# settings. These asserts cover the part the plugin is responsible for.
$BadgeSrc = Join-Path $Root 'hooks\laconic-statusline.ps1'
$BadgeDst = Join-Path $env:CLAUDE_CONFIG_DIR 'laconic-statusline.ps1'

function Test-SameBytes([string]$A, [string]$B) {
  try {
    $x = [System.IO.File]::ReadAllBytes($A)
    $y = [System.IO.File]::ReadAllBytes($B)
    if ($x.Length -ne $y.Length) { return $false }
    for ($i = 0; $i -lt $x.Length; $i++) { if ($x[$i] -ne $y[$i]) { return $false } }
    return $true
  } catch { return $false }
}

# 33. start installs the badge while a level is active, byte for byte.
Clear-Project
Remove-Item -LiteralPath $BadgeDst -Force -ErrorAction SilentlyContinue
Set-Level 'full'
Invoke-Hook 'start'
if (Test-SameBytes $BadgeSrc $BadgeDst) { Ok 'start installs the badge script' } else { Fail 'start did not install the badge script' }

# 34. A stale copy is refreshed rather than left alone. This is the whole reason
# the plugin owns the file: a user who wired up the badge once must not be stuck
# on the logic that shipped with whichever version they installed first.
[System.IO.File]::WriteAllText($BadgeDst, "stale`n", $Utf8NoBom)
Invoke-Hook 'start'
if (Test-SameBytes $BadgeSrc $BadgeDst) { Ok 'start refreshes a stale badge script' } else { Fail 'start left a stale badge script in place' }

# 35. Nothing is installed when the plugin is switched off. Writing files for a
# user who turned the mode off is exactly the kind of lingering state /laconic
# off promises not to leave.
Remove-Item -LiteralPath $BadgeDst -Force -ErrorAction SilentlyContinue
Set-Level 'off'
Invoke-Hook 'start'
Assert-Silent 'off installs nothing (still silent)'
if (Test-Path -LiteralPath $BadgeDst) { Fail 'off must not install the badge' } else { Ok 'off installs no badge' }

# 36. Same with no flag at all: an inert plugin touches nothing.
Remove-Item -LiteralPath $Flag, $BadgeDst -Force -ErrorAction SilentlyContinue
Invoke-Hook 'start'
Assert-Silent 'no flag installs nothing (still silent)'
if (Test-Path -LiteralPath $BadgeDst) { Fail 'inert plugin must not install the badge' } else { Ok 'inert plugin installs no badge' }

# 37. A linked target is refused, not written through — same discipline the flag
# file gets, and for the same reason.
Remove-Item -LiteralPath $BadgeDst -Force -ErrorAction SilentlyContinue
Set-Level 'full'
$badgeDecoy = Join-Path $env:CLAUDE_CONFIG_DIR 'badge-decoy'
[System.IO.File]::WriteAllText($badgeDecoy, 'keep', $Utf8NoBom)
if (New-Link $BadgeDst $badgeDecoy 'symlinked badge target not written through') {
  Invoke-Hook 'start'
  Assert-Has 'symlinked badge target not written through' 'keep' (Get-FlagText $badgeDecoy)
}
Remove-Item -LiteralPath $BadgeDst, $badgeDecoy -Force -ErrorAction SilentlyContinue

# 38. The install never breaks the rule slice, which is the hook's actual job.
# A destination the copy cannot write must not cost the user their rules. The
# bash suite makes the config directory unwritable; on Windows the equivalent is
# an exclusive handle on the destination, which makes Copy-Item fail with a
# sharing violation.
Set-Level 'full'
[System.IO.File]::WriteAllText($BadgeDst, "locked`n", $Utf8NoBom)
$lock = [System.IO.File]::Open($BadgeDst, [System.IO.FileMode]::Open,
                               [System.IO.FileAccess]::ReadWrite,
                               [System.IO.FileShare]::None)
Invoke-Hook 'start'
$lock.Close()
Assert-Has 'rules still emitted when the badge cannot be written' `
  'One recommendation, not a survey' $out
Remove-Item -LiteralPath $BadgeDst -Force -ErrorAction SilentlyContinue

# 39. remind does not install. Only SessionStart owns the file, so the write
# happens once per session rather than once per prompt — remind runs on every
# turn, and installing there would mean a file comparison per keystroke-batch.
Remove-Item -LiteralPath $BadgeDst -Force -ErrorAction SilentlyContinue
Set-Level 'full'
Invoke-Hook 'remind' '{"prompt":"hello"}'
if (Test-Path -LiteralPath $BadgeDst) { Fail 'remind must not install the badge' } else { Ok 'remind installs no badge' }

# 40. A CRLF rules file still slices. This side has stripped carriage returns
# since the port; the bash hook did not until #424, when a CRLF clone delivered
# every level at once. The rules are converted here rather than relying on this
# checkout's own endings, and the suite's hook path is pointed at the copy for
# the one invocation.
$crlfDir = New-TempDir
New-Item -ItemType Directory -Path (Join-Path $crlfDir 'hooks'), (Join-Path $crlfDir 'rules') -Force | Out-Null
Copy-Item -LiteralPath $Script -Destination (Join-Path $crlfDir 'hooks\laconic.ps1')
$lfRules = [System.IO.File]::ReadAllText((Join-Path $Root 'rules\laconic.md'), $Utf8NoBom) -replace "`r", ''
[System.IO.File]::WriteAllText((Join-Path $crlfDir 'rules\laconic.md'), ($lfRules -replace "`n", "`r`n"), $Utf8NoBom)
$savedScript = $Script
$Script = Join-Path $crlfDir 'hooks\laconic.ps1'
Set-Level 'lite'
Invoke-Hook 'start'
$Script = $savedScript
Assert-Has   'CRLF rules: lite slice is delivered'                '## Level: lite'  $out
Assert-Lacks 'CRLF rules: lite slice omits the full block'        '## Level: full'  $out
Assert-Lacks 'CRLF rules: lite slice omits the ultra block'       '## Level: ultra' $out
Assert-Lacks 'CRLF rules: no marker line reaches the model'       '<!-- level:'     $out
Assert-Lacks 'CRLF rules: no carriage return reaches the model'   "`r"              $out
Remove-Item -LiteralPath $crlfDir -Recurse -Force -ErrorAction SilentlyContinue

# 41. A bare /laconic sets full, as the help card's first row promises, and a
# bare /laconic project sets it for the project (#433). The level starts at lite
# so a no-op cannot pass. Anything else after /laconic must still write nothing:
# status is not a level, an unknown word is not full, and a quoted argument is
# not the end of the prompt.
Clear-Project
Set-Level 'lite'
Invoke-Hook 'remind' '{"prompt":"/laconic"}'
Assert-Has 'bare /laconic writes full' 'full' (Get-FlagText $Flag)
Assert-Has 'bare /laconic reports full' 'LACONIC MODE ACTIVE (full)' $out
Set-Level 'lite'
Invoke-Hook 'remind' '{"prompt":"/laconic project"}'
Assert-Has 'bare /laconic project writes the project flag' 'full' (Get-FlagText $ProjectFlag)
Assert-Has 'bare /laconic project leaves the machine flag' 'lite' (Get-FlagText $Flag)
Clear-Project
foreach ($p in @('/laconic status', '/laconic max', '/laconic \"x\"')) {
  Invoke-Hook 'remind' ('{"prompt":"' + $p + '"}')
  Assert-Has "$p writes nothing" 'lite' (Get-FlagText $Flag)
}
Invoke-Hook 'switch' '{"prompt":"/laconic"}'
Assert-Has 'switch acknowledges a bare /laconic as full' 'level set to full.' $out

# 43. Whitespace that JSON escapes still counts as whitespace beside the command
# (#425). This side decodes the payload before matching, so it always accepted
# these; laconic.sh greps the raw JSON and had to learn the escapes. The cases
# are the bash suite's, so a divergence fails one platform only. An escaped
# backslash before n is not a newline, a backspace is not whitespace to .NET,
# and an unknown word stays unknown.
Clear-Project
foreach ($p in @('/laconic off\nthanks', '/laconic off\n', '\n/laconic off', '\t/laconic off',
                 '/laconic off\r\nthanks', '/laconic off\tnow', '/laconic off\fnow', '\u000b/laconic off')) {
  Set-Level 'full'
  Invoke-Hook 'remind' ('{"prompt":"' + $p + '"}')
  Assert-Has "$p switches to off" 'off' (Get-FlagText $Flag)
  Assert-Empty "$p prints nothing once off" $out
}
foreach ($p in @('/laconic lite project\nnow', '/laconic lite project\u000Bnow')) {
  Clear-Project
  Set-Level 'full'
  Invoke-Hook 'remind' ('{"prompt":"' + $p + '"}')
  Assert-Has "$p writes the project flag" 'lite' (Get-FlagText $ProjectFlag)
  Assert-Has "$p leaves the machine flag" 'full' (Get-FlagText $Flag)
}
Invoke-Hook 'switch' '{"prompt":"/laconic lite project\nnow"}'
Assert-Has 'switch acknowledges the project scope after a newline' 'level set to lite for this project.' $out
Clear-Project
Set-Level 'lite'
Invoke-Hook 'remind' '{"prompt":"/laconic\n"}'
Assert-Has 'bare /laconic then a newline writes full' 'full' (Get-FlagText $Flag)
Set-Level 'lite'
Invoke-Hook 'remind' '{"prompt":"\t/laconic project\r\n"}'
Assert-Has 'bare /laconic project between escapes writes the project flag' 'full' (Get-FlagText $ProjectFlag)
Clear-Project
foreach ($p in @('/laconic ultraviolet\n', '/laconic off\\nthanks', '/laconic\\n', '\\n/laconic off', '/laconic off\bnow')) {
  Set-Level 'lite'
  Invoke-Hook 'remind' ('{"prompt":"' + $p + '"}')
  Assert-Has "$p writes nothing" 'lite' (Get-FlagText $Flag)
}

# 44. A switch that could not be written says so rather than letting the model
# confirm it (#426). Remind otherwise prints the reminder for the level still in
# force, or nothing when that level is off. The notice replaces the reminder, so
# under LACONIC_JSON_PATH it is still one object. The read-only attribute stops
# an elevated process too, so nothing here skips; a .claude that is a file
# blocks the project write.
$notice = 'was not applied, because'
$tailText = 'could not be written. Tell the user the switch failed, and do not change that file yourself.'
Clear-Project
Set-Level 'full'
Set-ItemProperty -LiteralPath $Flag -Name IsReadOnly -Value $true
Invoke-Hook 'remind' '{"prompt":"/laconic off"}'
Assert-Has 'read-only flag: /laconic off reports the failure' "the switch to off $notice $Flag $tailText" $out
Assert-Lacks 'read-only flag: no reminder for the old level' 'LACONIC MODE ACTIVE' $out
Assert-Empty 'read-only flag (stderr)' $err
Assert-Has 'read-only flag stays full' 'full' (Get-FlagText $Flag)
$env:LACONIC_JSON_PATH = 'a.b'
Invoke-Hook 'remind' '{"prompt":"/laconic off"}'
Remove-Item Env:\LACONIC_JSON_PATH -ErrorAction SilentlyContinue
$parsed = $null
try { $parsed = ConvertFrom-Json $out } catch {}
if ($null -ne $parsed -and $parsed.a.b -ceq "laconic: the switch to off $notice $Flag $tailText") {
  Ok 'the notice is one object under LACONIC_JSON_PATH'
} else {
  Fail "the notice under LACONIC_JSON_PATH — got: $out"
}
Invoke-Hook 'remind' '{"prompt":"/laconic full"}'
Assert-Has 'read-only flag already at the level: the reminder, no notice' 'LACONIC MODE ACTIVE (full)' $out
Set-ItemProperty -LiteralPath $Flag -Name IsReadOnly -Value $false
Set-Level 'off'
Set-ItemProperty -LiteralPath $Flag -Name IsReadOnly -Value $true
Invoke-Hook 'remind' '{"prompt":"/laconic full"}'
Assert-Has 'read-only off: /laconic full reports the failure' "the switch to full $notice" $out
Set-ItemProperty -LiteralPath $Flag -Name IsReadOnly -Value $false
Set-Level 'full'
[System.IO.File]::WriteAllText($ProjectDir, 'x', $Utf8NoBom)
Invoke-Hook 'remind' '{"prompt":"/laconic ultra project"}'
Assert-Has 'unwritable project dir reports the failure' "the switch to ultra $notice $ProjectFlag $tailText" $out
Assert-Empty 'unwritable project dir (stderr)' $err
Assert-Has 'unwritable project dir leaves the machine flag' 'full' (Get-FlagText $Flag)
Clear-Project
Invoke-Hook 'remind' '{"prompt":"/laconic lite"}'
Assert-Has 'a written switch prints the reminder' 'LACONIC MODE ACTIVE (lite)' $out
Assert-Lacks 'a written switch prints no notice' $notice $out
Set-Level 'full'
Invoke-Hook 'remind' '{"prompt":"/laconic off"}'
Assert-Silent 'a written off prints nothing'

# 45. Kimi Code sends the prompt as an array of content parts, not a string, and
# the switch has to parse out of the first part's text. Only the first part
# counts, as only the start of a string prompt does: a switch in a later part,
# behind a first part that is not text, or after an escaped quote inside the
# text writes nothing. The level starts at lite so a no-op cannot pass.
Clear-Project
Set-Level 'lite'
Invoke-Hook 'remind' '{"hook_event_name":"UserPromptSubmit","session_id":"s","cwd":"/w","client_type":"kimi_code_cli","prompt":[{"type":"text","text":"/laconic ultra"}],"is_steer":false}'
Assert-Has 'array prompt: /laconic ultra writes the flag' 'ultra' (Get-FlagText $Flag)
Assert-Has 'array prompt: the reminder names the new level' 'LACONIC MODE ACTIVE (ultra)' $out
Set-Level 'lite'
Invoke-Hook 'remind' '{"prompt": [ {"text": "/laconic off\nthanks", "type": "text"} ]}'
Assert-Has 'array prompt: spacing, key order and an escaped newline still switch' 'off' (Get-FlagText $Flag)
Set-Level 'lite'
Invoke-Hook 'remind' '{"prompt":[{"type":"text","text":"/laconic"}]}'
Assert-Has 'array prompt: a bare /laconic writes full' 'full' (Get-FlagText $Flag)
Set-Level 'lite'
Invoke-Hook 'remind' '{"prompt":[{"type":"text","text":"/laconic ultra project"}]}'
Assert-Has 'array prompt: project scope writes the project flag' 'ultra' (Get-FlagText $ProjectFlag)
Assert-Has 'array prompt: project scope leaves the machine flag' 'lite' (Get-FlagText $Flag)
Clear-Project
foreach ($p in @(
    '[{"type":"text","text":"does /laconic off actually work?"}]',
    '[{"type":"text","text":"hello"},{"type":"text","text":"/laconic off"}]',
    '[{"type":"image_url","image_url":{"url":"x"}},{"type":"text","text":"/laconic off"}]',
    '[{"type":"text","text":"x \"text\":\"/laconic off"}]',
    '["/laconic off"]', '[]')) {
  Set-Level 'lite'
  Invoke-Hook 'remind' "{`"prompt`":$p}"
  Assert-Has "array prompt $p writes nothing" 'lite' (Get-FlagText $Flag)
  Assert-Empty "array prompt $p (stderr)" $err
}
Invoke-Hook 'switch' '{"prompt":[{"type":"text","text":"/laconic ultra"}]}'
Assert-Has 'switch acknowledges an array prompt' 'level set to ultra.' $out

# 46. A project rooted where the machine configuration lives has no project
# flag of its own (#427): both paths name one file, so a scoped switch there is
# refused with a notice instead of changing every project, and an unscoped one
# still sets the machine level. The trailing separator on the config directory
# is the form a string comparison alone would miss.
$savedConfig = $env:CLAUDE_CONFIG_DIR
$savedProject = $env:CLAUDE_PROJECT_DIR
$H = New-TempDir
$HConfig = Join-Path $H '.claude'
$HFlag = Join-Path $HConfig '.laconic-level'
New-Item -ItemType Directory -Path $HConfig -Force | Out-Null
[System.IO.File]::WriteAllText($HFlag, 'full', $Utf8NoBom)
$env:CLAUDE_CONFIG_DIR = $HConfig + '\'
$env:CLAUDE_PROJECT_DIR = $H
Invoke-Hook 'remind' '{"prompt":"/laconic off project"}'
Assert-Has 'home: a project switch reports the refusal' 'the switch to off was not applied, because ' $out
Assert-Has 'home: the refusal names the shared flag' 'is also the machine flag here' $out
Assert-Has 'home: the machine flag stays full' 'full' (Get-FlagText $HFlag)
Invoke-Hook 'switch' '{"prompt":"/laconic ultra project"}'
Assert-Lacks 'home: switch mode acknowledges no project scope' 'for this project' $out
Assert-Has 'home: switch mode leaves the machine flag' 'full' (Get-FlagText $HFlag)
Invoke-Hook 'remind' '{"prompt":"/laconic ultra"}'
Assert-Has 'home: an unscoped switch still sets the machine level' 'ultra' (Get-FlagText $HFlag)
$env:CLAUDE_CONFIG_DIR = $savedConfig
$env:CLAUDE_PROJECT_DIR = $savedProject
Remove-Item -LiteralPath $H -Recurse -Force -ErrorAction SilentlyContinue

# 47. A Unicode space is whitespace beside the command too (#491). .NET's \s
# always counted every one, but stdin was decoded with the console code page,
# which on Windows is not UTF-8 by default, so U+00A0 arrived as two other
# characters, the scope was dropped and the machine flag took the level. The
# code points are the bash suite's, so a divergence fails one platform only.
# The runner's console already reads UTF-8, which hid the bug, so the console
# the hook shares is set to cp437 for this case and put back after it.
$savedInput = $null
try {
  $savedInput = [Console]::InputEncoding
  [Console]::InputEncoding = [System.Text.Encoding]::GetEncoding(437)
  Ok 'the console input code page is cp437 for case 47'
} catch {
  Fail "the console input code page is cp437 for case 47 — $($_.Exception.Message)"
}
foreach ($cp in @(0x0085, 0x00A0, 0x1680, 0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005, 0x2006,
                  0x2007, 0x2008, 0x2009, 0x200A, 0x2028, 0x2029, 0x202F, 0x205F, 0x3000)) {
  $u = 'U+{0:X4}' -f $cp
  Clear-Project
  Set-Level 'full'
  Invoke-Hook 'remind' ('{"prompt":"/laconic lite project' + [char]$cp + 'now"}')
  Assert-Has "$u after project writes the project flag" 'lite' (Get-FlagText $ProjectFlag)
  Assert-Has "$u after project leaves the machine flag" 'full' (Get-FlagText $Flag)
}
foreach ($cp in @(0x00A0, 0x3000)) {
  $u = 'U+{0:X4}' -f $cp
  Clear-Project
  Set-Level 'full'
  Invoke-Hook 'remind' ('{"prompt":"' + [char]$cp + '/laconic project' + [char]$cp + '"}')
  Assert-Has "$u around a bare /laconic project writes full there" 'full' (Get-FlagText $ProjectFlag)
  Invoke-Hook 'switch' ('{"prompt":"/laconic lite project' + [char]$cp + 'now"}')
  Assert-Has "switch acknowledges the project scope before $u" 'level set to lite for this project.' $out
}
Clear-Project
Set-Level 'full'
Invoke-Hook 'remind' ('{"prompt":"/laconic lite project' + [char]0x200B + 'now"}')
Assert-Has 'U+200B after project is not a boundary' 'lite' (Get-FlagText $Flag)
if (Test-Path -LiteralPath $ProjectFlag) { Fail 'U+200B after project writes no project flag' } else { Ok 'U+200B after project writes no project flag' }
Clear-Project
if ($null -ne $savedInput) { try { [Console]::InputEncoding = $savedInput } catch {} }

# --- hooks.json ---
# The TOML asserts the bash suite runs stay there: PowerShell 5.1 has no TOML
# parser, and the ubuntu job covers them on the same commit.
$Hooks = Join-Path $Root 'hooks\hooks.json'
if (Test-Path -LiteralPath $Hooks) { Ok 'hooks.json exists' } else { Fail 'hooks.json exists' }
$manifest = $null
try { $manifest = ConvertFrom-Json ([System.IO.File]::ReadAllText($Hooks)) } catch {}
if ($null -ne $manifest) { Ok 'hooks.json is valid JSON' } else { Fail 'hooks.json is valid JSON' }

# commandWindows is Codex's field, and Claude Code reads no such key: on Windows
# it runs `command` through Git Bash, so this port never runs under Claude Code.
# A hooks.json that carries the key again would promise a path that does not
# exist (#423). The bash suite checks the same thing from the Linux job.
if ($null -ne $manifest) {
  $stray = 0
  foreach ($ev in $manifest.hooks.PSObject.Properties) {
    foreach ($group in $ev.Value) {
      foreach ($h in $group.hooks) {
        if ($null -ne $h.PSObject.Properties['commandWindows']) { $stray++ }
      }
    }
  }
  if ($stray -eq 0) { Ok 'hooks.json carries no commandWindows (Claude Code does not read it, #423)' } else { Fail "hooks.json carries no commandWindows (Claude Code does not read it, #423; found $stray)" }
  # SubagentStart must stay absent. The loop above only checks the events that
  # are wired, so a reinstated subagent hook would pass every assertion in this
  # file without this one. Issue #6 measured that path: no accuracy change in
  # any arm and a 6-16% cost increase per subagent call.
  if ($null -ne $manifest.hooks.PSObject.Properties['SubagentStart']) {
    Fail 'hooks.json must not wire SubagentStart (see issue #6)'
  } else {
    Ok 'hooks.json does not wire SubagentStart'
  }
}

# --- statusline ---
$Badge = Join-Path $Root 'hooks\laconic-statusline.ps1'
function Invoke-Badge {
  $outFile = Join-Path $env:CLAUDE_CONFIG_DIR '.badge-out'
  $p = Start-Process -FilePath $Host_ `
    -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $Badge) `
    -RedirectStandardOutput $outFile -NoNewWindow -Wait -PassThru
  $p.WaitForExit()
  $text = [System.IO.File]::ReadAllText($outFile)
  Remove-Item -LiteralPath $outFile -Force -ErrorAction SilentlyContinue
  return $text
}

Clear-Project
Remove-Item -LiteralPath $Flag -Force -ErrorAction SilentlyContinue
Assert-Empty 'badge silent with no flag' (Invoke-Badge)
Set-Level 'off'
Assert-Empty 'badge silent when off' (Invoke-Badge)
Set-Level 'full'
Assert-Has 'badge shows plain name at full' '[LACONIC]' (Invoke-Badge)
Set-Level 'ultra'
Assert-Has 'badge shows level when not full' '[LACONIC:ULTRA]' (Invoke-Badge)

# The badge resolves the flag the same way the hook does. A badge that names a
# level the session is not running is worse than no badge, because nothing else
# would reveal the mismatch.
Set-Level 'full'
Set-ProjectLevel 'ultra'
Assert-Has 'badge follows the project flag, not the global one' '[LACONIC:ULTRA]' (Invoke-Badge)
Set-ProjectLevel 'off'
Assert-Empty 'badge silent when the project flag is off' (Invoke-Badge)
Clear-Project
Remove-Item -LiteralPath $Flag -Force -ErrorAction SilentlyContinue

# --- cross-platform state sharing ---
# The one case a per-platform suite cannot reach: a user with WSL or Git Bash on
# the same machine runs both hooks against the same ~/.claude. A flag file
# written by one must be accepted by the other, in both directions. Skipping
# this when bash is missing would hide exactly the failure it exists to catch,
# so it is a hard failure on any host that has bash.
#
# Windows itself ships no bash — that absence is the reason this port exists.
# What supplies it here is the GitHub Actions windows-latest image, which
# installs Git for Windows. That is an image detail, not a platform guarantee,
# so it is required rather than assumed: skipping is allowed on a developer's
# Windows box, and is a hard failure under CI. A green run that quietly stopped
# checking the state-sharing case would be worse than a red one.
$bash = Get-Command bash -ErrorAction SilentlyContinue
if ($null -eq $bash) {
  if ([string]::IsNullOrEmpty($env:CI)) {
    Write-Host 'skip cross-platform state sharing — no bash on this host'
  } else {
    Fail 'cross-platform state sharing — no bash on the CI runner, so the case went unchecked'
  }
} else {
  # MSYS bash reads C:/path but not C:\path.
  $shScript  = (Join-Path $Root 'hooks\laconic.sh') -replace '\\', '/'
  $shConfig  = $env:CLAUDE_CONFIG_DIR -replace '\\', '/'
  $shProject = $env:CLAUDE_PROJECT_DIR -replace '\\', '/'

  # PowerShell writes, bash reads.
  Set-Level 'full'
  Invoke-Hook 'remind' '{"prompt":"/laconic ultra"}'
  $fromBash = & bash -c "CLAUDE_CONFIG_DIR='$shConfig' CLAUDE_PROJECT_DIR='$shProject' bash '$shScript' remind </dev/null"
  Assert-Has 'bash accepts a flag written by PowerShell' 'LACONIC MODE ACTIVE (ultra)' ($fromBash -join "`n")

  # bash writes, PowerShell reads.
  & bash -c "CLAUDE_CONFIG_DIR='$shConfig' CLAUDE_PROJECT_DIR='$shProject' printf '%s' lite > '$shConfig/.laconic-level'"
  Invoke-Hook 'remind' '{"prompt":"just a normal turn"}'
  Assert-Has 'PowerShell accepts a flag written by bash' 'LACONIC MODE ACTIVE (lite)' $out

  # Same rule slice from both implementations, byte for byte. A divergence here
  # means the two hooks feed the model different context for the same level.
  Set-Level 'full'
  Invoke-Hook 'start'
  $shOut = & bash -c "CLAUDE_CONFIG_DIR='$shConfig' CLAUDE_PROJECT_DIR='$shProject' bash '$shScript' start </dev/null"
  # PowerShell's pipeline splits the child's stdout into lines and drops the
  # trailing newline, so compare on that normalization rather than raw bytes.
  $psLines = ($out -replace "`r", '').TrimEnd("`n")
  $shLines = (($shOut -join "`n") -replace "`r", '').TrimEnd("`n")
  if ($psLines -ceq $shLines) {
    Ok 'both implementations emit the same rule slice'
  } else {
    Fail 'rule slice differs between bash and PowerShell'
  }
}

# --- LACONIC_JSON_PATH and the Gemini CLI fragment (#13) ---
#
# Raw stdout is what Claude Code consumes and must not move, so the first check
# is that it is unchanged once the variable is cleared again. The rest cover the
# failure mode raw stdout never had: the rule slice carries double quotes and
# newlines on every level, so a wrapper escaping neither would ship malformed
# JSON. ConvertTo-Json does the escaping here, awk does it on the bash side, and
# the two are only interchangeable if both are actually exercised — before this
# block the PowerShell Emit path had no coverage at all.
Clear-Project
Remove-Item Env:\LACONIC_JSON_PATH -ErrorAction SilentlyContinue
Set-Level 'full'
Invoke-Hook 'start'
$rawStart = $script:out

$env:LACONIC_JSON_PATH = 'hookSpecificOutput.additionalContext'
Invoke-Hook 'start'
$jsonStart = $script:out
Invoke-Hook 'remind'
$jsonRemind = $script:out
Remove-Item Env:\LACONIC_JSON_PATH -ErrorAction SilentlyContinue

Invoke-Hook 'start'
if ($script:out -ceq $rawStart) {
  Ok 'an unset LACONIC_JSON_PATH is the raw path, byte for byte'
} else {
  Fail 'an unset LACONIC_JSON_PATH is the raw path, byte for byte'
}

$startObj = $null
try { $startObj = ConvertFrom-Json $jsonStart } catch {}
if ($null -ne $startObj) { Ok 'start emits well-formed JSON when a path is set' } else { Fail 'start emits well-formed JSON when a path is set' }

$remindObj = $null
try { $remindObj = ConvertFrom-Json $jsonRemind } catch {}
if ($null -ne $remindObj) { Ok 'remind emits well-formed JSON when a path is set' } else { Fail 'remind emits well-formed JSON when a path is set' }

# The payload must be the raw slice exactly, minus the single trailing newline:
# the field carries the text, not the line terminator.
$field = ''
if ($null -ne $startObj) { $field = [string]$startObj.hookSpecificOutput.additionalContext }
$wantRaw = $rawStart
if ($wantRaw.EndsWith("`n")) { $wantRaw = $wantRaw.Substring(0, $wantRaw.Length - 1) }
if ($field -ceq $wantRaw) {
  Ok 'the JSON payload round-trips to the raw slice'
} else {
  Fail 'the JSON payload round-trips to the raw slice'
}

# The escaping the raw path never needed. The shipped slice contains both, so
# this asserts against real content rather than a synthetic string.
if ($field.Contains('"') -and $field.Contains("`n")) {
  Ok 'quotes and newlines survive the JSON round-trip'
} else {
  Fail 'quotes and newlines survive the JSON round-trip'
}

# A single-segment path must not be nested, and a deep one must nest all the
# way: Codex and Copilot do not put the field where Gemini does (#14, #15).
$env:LACONIC_JSON_PATH = 'context'
Invoke-Hook 'remind'
if ($script:out.StartsWith('{"context":"LACONIC MODE ACTIVE')) {
  Ok 'a single-segment path is not nested'
} else {
  Fail "a single-segment path is not nested — got: $($script:out)"
}

$env:LACONIC_JSON_PATH = 'a.b.c'
Invoke-Hook 'remind'
$deep = ''
try { $deep = [string](ConvertFrom-Json $script:out).a.b.c } catch {}
if ($deep.StartsWith('LACONIC MODE ACTIVE')) {
  Ok 'a dotted path nests every segment'
} else {
  Fail "a dotted path nests every segment — got: $($script:out)"
}

# The level whitelist still gates it. JSON mode must not become a way to emit
# something when no level is active.
$env:LACONIC_JSON_PATH = 'hookSpecificOutput.additionalContext'
Remove-Item -LiteralPath $Flag -Force -ErrorAction SilentlyContinue
Invoke-Hook 'start'
Assert-Empty 'no level active emits nothing even with a JSON path set' $script:out
Set-Level 'off'
Invoke-Hook 'start'
Assert-Empty 'level off emits nothing even with a JSON path set' $script:out
Remove-Item Env:\LACONIC_JSON_PATH -ErrorAction SilentlyContinue

# The fragment itself. Gemini reads a field out of a JSON object rather than raw
# stdout, so the fragment is only useful if it sets LACONIC_JSON_PATH to the
# exact path Gemini looks in. One that dropped the variable would still be valid
# JSON, would still run the hook, and would inject nothing at all.
$Gemini = Join-Path $Root 'hooks\gemini-settings.json'
if (Test-Path -LiteralPath $Gemini) { Ok 'gemini-settings.json exists' } else { Fail 'gemini-settings.json exists' }
$gem = $null
try { $gem = ConvertFrom-Json ([System.IO.File]::ReadAllText($Gemini)) } catch {}
if ($null -ne $gem) { Ok 'gemini-settings.json is valid JSON' } else { Fail 'gemini-settings.json is valid JSON' }

if ($null -ne $gem) {
  foreach ($pair in @(@('SessionStart', 'start'), @('BeforeAgent', 'remind'))) {
    $ev = $pair[0]; $mode = $pair[1]
    $found = @()
    foreach ($group in $gem.hooks.$ev) {
      foreach ($h in $group.hooks) { $found += ($h.command -split ' ')[-1] }
    }
    $got = ($found -join ' ')
    if ($got -ceq $mode) { Ok "gemini-settings.json wires $ev -> $mode" } else { Fail "gemini-settings.json wires $ev -> $mode (got: $got)" }
  }

  $paths = @()
  $times = @()
  foreach ($prop in $gem.hooks.PSObject.Properties) {
    foreach ($group in $prop.Value) {
      foreach ($h in $group.hooks) {
        $times += [int]$h.timeout
        foreach ($tok in ($h.command -split ' ')) {
          if ($tok.StartsWith('LACONIC_JSON_PATH=')) { $paths += $tok.Substring(18) }
        }
      }
    }
  }
  # Force an array: Sort-Object -Unique returns a bare string for one result,
  # and indexing a string yields its first character rather than the value.
  $unique = @($paths | Sort-Object -Unique)
  if ($unique.Count -eq 1 -and $unique[0] -ceq 'hookSpecificOutput.additionalContext') {
    Ok 'gemini-settings.json sets the JSON path Gemini reads, on every hook'
  } else {
    Fail "gemini-settings.json JSON path (got: $($unique -join ', '))"
  }

  # Gemini's timeouts are milliseconds; hooks.json's are seconds. Copying the 5
  # across would give a 5 ms budget and kill the hook before it read the flag.
  if ($times.Count -gt 0 -and -not ($times | Where-Object { $_ -lt 1000 })) {
    Ok 'gemini-settings.json timeouts are in milliseconds'
  } else {
    Fail 'gemini-settings.json timeouts are in milliseconds'
  }

  # End to end against the fragment's own path rather than a literal, so the
  # fragment and the hook cannot drift apart silently. This is a schema check
  # and nothing more: per #13, a well-formed object is not evidence that Gemini
  # loads it, and no Gemini install has confirmed that yet.
  Set-Level 'full'
  $env:LACONIC_JSON_PATH = $unique[0]
  foreach ($mode in @('start', 'remind')) {
    Invoke-Hook $mode
    $value = ''
    try { $value = [string](ConvertFrom-Json $script:out).hookSpecificOutput.additionalContext } catch {}
    if (-not [string]::IsNullOrEmpty($value.Trim())) {
      Ok "$mode fills additionalContext where Gemini reads it"
    } else {
      Fail "$mode fills additionalContext where Gemini reads it"
    }
  }
  Remove-Item Env:\LACONIC_JSON_PATH -ErrorAction SilentlyContinue
}
Remove-Item -LiteralPath $Flag -Force -ErrorAction SilentlyContinue

# --- codex-config.toml: the Windows half of the Codex CLI fragment (#14) ---
#
# Windows PowerShell 5.1 has no TOML parser and this project adds no dependency
# for one, so the bash suite owns the schema checks and this side owns the only
# claim a Windows machine can actually settle: that the commandWindows line
# Codex would run does deliver the rules. Codex reads a hook's raw stdout, so
# the assert is on the text itself rather than on a JSON field.
$Codex = Join-Path $Root 'hooks\codex-config.toml'
if (Test-Path -LiteralPath $Codex) { Ok 'codex-config.toml exists' } else { Fail 'codex-config.toml exists' }

if (Test-Path -LiteralPath $Codex) {
  Set-Level 'full'
  $text = [System.IO.File]::ReadAllText($Codex)
  foreach ($mode in @('start', 'remind')) {
    # Pull the -File argument and the mode out of the fragment's own line, so a
    # fragment that renamed either cannot pass by running something else.
    # No `$` anchor: a Windows checkout may have CRLF endings, and the closing
    # quote after the mode already pins the end of the value.
    $m = [regex]::Match($text, '(?m)^commandWindows = "[^"]*-File ([^"]+?) ' + $mode + '"')
    if (-not $m.Success) {
      Fail "codex-config.toml has a commandWindows line for $mode"
      continue
    }
    Ok "codex-config.toml has a commandWindows line for $mode"
    # TOML escapes the backslashes; the placeholder root becomes this clone.
    $path = $m.Groups[1].Value.Replace('\\', '\').Replace('C:\path\to\laconic', $Root)
    $outFile = Join-Path $env:CLAUDE_CONFIG_DIR '.codex-stdout'
    $inFile  = Join-Path $env:CLAUDE_CONFIG_DIR '.codex-stdin'
    [System.IO.File]::WriteAllText($inFile, '', $Utf8NoBom)
    $p = Start-Process -FilePath $Host_ `
      -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $path, $mode) `
      -RedirectStandardInput $inFile -RedirectStandardOutput $outFile `
      -NoNewWindow -Wait -PassThru
    $p.WaitForExit()
    $got = [System.IO.File]::ReadAllText($outFile)
    Remove-Item -LiteralPath $inFile, $outFile -Force -ErrorAction SilentlyContinue
    if ($got.Trim().Length -gt 0) {
      Ok "$mode delivers raw text through the fragment's own commandWindows"
    } else {
      Fail "$mode delivers raw text through the fragment's own commandWindows"
    }
  }
  Remove-Item -LiteralPath $Flag -Force -ErrorAction SilentlyContinue
}

# --- switch mode: the Cursor acknowledgment (#16) ---
#
# The bash suite owns the cursor-hooks.json schema checks; this side owns the
# behaviour, because a native-Windows Cursor runs laconic.ps1 and the two
# implementations have to emit the same bytes. The acknowledgment is asserted in
# full rather than by substring: it is a user-visible sentence that exists in two
# places, and a divergence between them would show up on one platform only.
$Ack = '{"continue":false,"user_message":"laconic: level set to ultra. ' +
       'Cursor delivers the rules at session start, so open a new chat for it to take effect."}'

Set-Level 'full'
Clear-Project
Invoke-Hook 'switch' '{"prompt":"fix the failing test"}'
Assert-Silent 'switch says nothing about an ordinary prompt'
Invoke-Hook 'switch' '{"prompt":"does /laconic off actually work?"}'
Assert-Silent 'switch says nothing about prose mentioning the command'
Assert-Has 'switch leaves the level alone on prose' 'full' (Get-FlagText $Flag)

Invoke-Hook 'switch' '{"prompt":"/laconic ultra"}'
Assert-Has 'switch persists the level' 'ultra' (Get-FlagText $Flag)
Assert-Lacks 'switch does not emit the rules' 'No preamble' $script:out
Assert-Lacks 'acknowledgment has no carriage return' "`r" $script:out
if ($script:out.TrimEnd("`n") -ceq $Ack) {
  Ok 'the acknowledgment is byte-identical to the bash side'
} else {
  Fail "the acknowledgment is byte-identical to the bash side — got: $($script:out)"
}

# off is the switch that most needs acknowledging, and it is the one the level
# whitelist would otherwise swallow: past that gate an inactive level is silence.
Invoke-Hook 'switch' '{"prompt":"/laconic off"}'
Assert-Has 'switch acknowledges off' 'level set to off' $script:out
Assert-Has 'off persists through switch mode' 'off' (Get-FlagText $Flag)

Set-Level 'full'
Invoke-Hook 'switch' '{"prompt":"/laconic lite project"}'
Assert-Has 'switch names the project scope' 'for this project' $script:out
Assert-Has 'switch writes the project flag' 'lite' (Get-FlagText $ProjectFlag)
Clear-Project

# A refused write must not be acknowledged. The link guard already stops the
# write; without checking its result the mode would still tell the user the level
# had changed, which is the one thing an acknowledgment exists not to do.
Remove-Item -LiteralPath $Flag -Force -ErrorAction SilentlyContinue
$decoy = Join-Path $env:CLAUDE_CONFIG_DIR 'switch-decoy'
[System.IO.File]::WriteAllText($decoy, 'keep', $Utf8NoBom)
if (New-Link $Flag $decoy 'linked flag on switch') {
  Invoke-Hook 'switch' '{"prompt":"/laconic ultra"}'
  Assert-Silent 'linked flag on switch'
  Assert-Has 'linked flag not written through on switch' 'keep' (Get-FlagText $decoy)
}
Remove-Item -LiteralPath $Flag -Force -ErrorAction SilentlyContinue

Set-Level 'full'
Invoke-Hook 'switch' '{"prompt":"/laconic fullscreen"}'
Assert-Silent 'switch does not prefix-match a level word'
Assert-Has 'fullscreen does not switch under switch mode' 'full' (Get-FlagText $Flag)
Remove-Item -LiteralPath $Flag -Force -ErrorAction SilentlyContinue

Clear-Project
Remove-Item -LiteralPath $env:CLAUDE_CONFIG_DIR -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $env:CLAUDE_PROJECT_DIR -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ''
Write-Host "$($script:fails) failure(s)"
if ($script:fails -ne 0) { exit 1 }
exit 0
