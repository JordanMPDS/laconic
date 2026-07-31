#Requires -Version 5.1
# laconic — optional statusline badge (native Windows). The SessionStart hook
# installs and refreshes a copy of this file at a stable path, so point
# settings.json there rather than into the plugin, whose path carries a version:
#   "statusLine": { "type": "command",
#                   "command": "powershell -NoProfile -ExecutionPolicy Bypass -File \"%USERPROFILE%\\.claude\\laconic-statusline.ps1\"" }
# Do not reference it through ${CLAUDE_PLUGIN_ROOT}: Claude Code resolves that
# variable for plugin hooks only, and a statusLine command containing it raises
# an error that is logged and swallowed, so the badge silently renders nothing.
$ErrorActionPreference = 'SilentlyContinue'

$configDir = if ([string]::IsNullOrEmpty($env:CLAUDE_CONFIG_DIR)) {
  Join-Path $HOME '.claude'
} else {
  $env:CLAUDE_CONFIG_DIR
}
$globalFlag = Join-Path $configDir '.laconic-level'

$projectDir = if ([string]::IsNullOrEmpty($env:CLAUDE_PROJECT_DIR)) {
  (Get-Location).Path
} else {
  $env:CLAUDE_PROJECT_DIR
}
$projectFlag = Join-Path (Join-Path $projectDir '.claude') '.laconic-level'

# Same resolution and hardening as the hook: project flag first, never
# dereference a linked flag, never echo bytes that failed the whitelist. The
# order has to match laconic.ps1 exactly — a badge that names a level the session
# is not running is worse than no badge, because the error is invisible.
$flag = ''
foreach ($candidate in @($projectFlag, $globalFlag)) {
  try {
    $item = Get-Item -LiteralPath $candidate -Force -ErrorAction Stop
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) { exit 0 }
  } catch {}
  if (Test-Path -LiteralPath $candidate -PathType Leaf) { $flag = $candidate; break }
}
if ($flag -eq '') { exit 0 }

$mode = ''
try {
  $bytes = [System.IO.File]::ReadAllBytes($flag)
  $take = [Math]::Min(16, $bytes.Length)
  $mode = [System.Text.Encoding]::ASCII.GetString($bytes, 0, $take) -creplace '[^a-z]', ''
} catch {
  exit 0
}
if (@('lite', 'full', 'ultra') -cnotcontains $mode) { exit 0 }

$color = if ($mode -ceq 'ultra') { 173 } else { 108 }
$esc = [char]27
$label = if ($mode -ceq 'full') { '[LACONIC]' } else { "[LACONIC:$($mode.ToUpperInvariant())]" }

try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false } catch {}
[Console]::Out.Write("$esc[38;5;${color}m$label$esc[0m")
exit 0
