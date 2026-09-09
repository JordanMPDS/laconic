#!/usr/bin/env bash
# Fake `claude` for offline harness tests. Emits one canned CLI stream, in the
# --output-format stream-json shape call() now asks for: one JSON object per
# line, closing with the result event and a system event after it.
# STUB_TEXT overrides the answer; STUB_FAIL=1 exits non-zero.
# STUB_TOOLS, a space-separated list of tool names, emits one assistant
# tool_use event per name so a test can assert on the captured tool list.
# STUB_ARGV_OUT, if set, records how this stub was invoked - the isolation
# env vars call() is supposed to set, then the full argv - so tests can
# assert on the invocation itself, not just its output.
# `claude --version` is its own invocation and must not fall through to the
# canned stream or to the argv capture below - run.py reads it once per
# generation since #272, so a test asserting on argv would otherwise see the
# version probe instead of the call it meant to inspect. STUB_VERSION_FILE
# names a file whose contents are the version, so a test can flip the release
# in the middle of a pass the way an upgrade does.
if [ "$1" = "--version" ]; then
  if [ -n "${STUB_VERSION_FILE:-}" ] && [ -f "${STUB_VERSION_FILE}" ]; then
    cat "${STUB_VERSION_FILE}"
  else
    printf '%s\n' "${STUB_VERSION:-0.0.0-stub (Claude Code)}"
  fi
  exit 0
fi
if [ -n "${STUB_ARGV_OUT:-}" ]; then
  {
    printf 'SAFE_MODE=%s\n' "${CLAUDE_CODE_SAFE_MODE:-<unset>}"
    if [ -n "${LACONIC_DEFAULT+x}" ]; then
      printf 'LACONIC_DEFAULT=<set>\n'
    else
      printf 'LACONIC_DEFAULT=<unset>\n'
    fi
    printf 'ARGV:\n'
    for a in "$@"; do printf '%s\n' "$a"; done
  } > "$STUB_ARGV_OUT"
fi
[ "${STUB_FAIL:-0}" = "1" ] && exit 3
# Escape backslashes and double quotes so STUB_TEXT can't break the JSON it's
# interpolated into (e.g. a quote character in the answer).
text="${STUB_TEXT:-stub answer}"
text="${text//\\/\\\\}"
text="${text//\"/\\\"}"
echo '{"type":"system","subtype":"init"}'
for tool in ${STUB_TOOLS:-}; do
  printf '%s\n' "{\"type\":\"assistant\",\"message\":{\"content\":[{\"type\":\"tool_use\",\"name\":\"${tool}\",\"input\":{}}]}}"
  echo '{"type":"user","message":{"content":[{"type":"tool_result"}]}}'
done
printf '%s\n' "{\"type\":\"assistant\",\"message\":{\"content\":[{\"type\":\"text\",\"text\":\"${text}\"}]}}"
printf '%s\n' "{\"type\":\"result\",\"subtype\":\"success\",\"is_error\":false,\"result\":\"${text}\",\"num_turns\":1,\"total_cost_usd\":0.001,\"duration_ms\":1234,\"usage\":{\"input_tokens\":10,\"output_tokens\":7,\"cache_creation_input_tokens\":100,\"cache_read_input_tokens\":200}}"
echo '{"type":"system","subtype":"task_summary"}'
