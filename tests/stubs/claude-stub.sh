#!/usr/bin/env bash
# Fake `claude` for offline harness tests. Emits one canned CLI JSON object.
# STUB_TEXT overrides the answer; STUB_FAIL=1 exits non-zero.
[ "${STUB_FAIL:-0}" = "1" ] && exit 3
# Escape backslashes and double quotes so STUB_TEXT can't break the JSON it's
# interpolated into (e.g. a quote character in the answer).
text="${STUB_TEXT:-stub answer}"
text="${text//\\/\\\\}"
text="${text//\"/\\\"}"
cat <<JSON
{"is_error":false,"result":"${text}","num_turns":1,
"total_cost_usd":0.001,"duration_ms":1234,
"usage":{"input_tokens":10,"output_tokens":7,
"cache_creation_input_tokens":100,"cache_read_input_tokens":200}}
JSON
