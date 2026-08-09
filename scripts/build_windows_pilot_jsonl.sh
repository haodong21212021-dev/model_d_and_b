#!/usr/bin/env bash
# Materialize a pilot task bundle and convert it for the Windows AGS runner.
set -euo pipefail

ROOT="${1:-/home/tione/notebook/agent_data/skillforge_pilot}"
GUI_AGENT="${2:-/home/tione/notebook/agent/gui-agent}"
CALENDAR_URL="${CUA_GYM_MOCK_LAUNCH_URL:-}"

cd "$GUI_AGENT"

python3 testcase/cua_gym/build_cua_gym_jsonl.py \
  --artifacts-root "$ROOT/artifacts" \
  --dataset-root "$ROOT" \
  --output "$ROOT/pilot_hosted.jsonl" \
  --materialize

python3 testcase/cua_gym/build_windows_ags_jsonl.py \
  --input "$ROOT/pilot_hosted.jsonl" \
  --output "$ROOT/pilot_windows_ags.jsonl" \
  --artifact-prefix-from "$ROOT" \
  --artifact-prefix-to "$ROOT" \
  --windows-artifact-dir "$ROOT/windows_ags_artifacts"

# The Windows converter disables the Linux browser launch inside initial_setup.py
# but does not add a Windows equivalent, so the agent would start on an empty
# desktop. Rewrite the setup steps to run Windows Python and open the task's
# own mock URL using the session id the setup script persisted.
CUA_GYM_MOCK_LAUNCH_URL="$CALENDAR_URL" python3 - "$ROOT/pilot_windows_ags.jsonl" <<'PY'
import json
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
url_pattern = re.compile(r"BASE_URL\s*=\s*['\"]([^'\"]+)['\"]")

for row in rows:
    artifact = None
    for step in row.get("setup", []):
        for entry in (step.get("parameters", {}).get("files") or []):
            if str(entry.get("path", "")).endswith("initial_setup.py"):
                artifact = Path(str(entry.get("local", "")))
    base_url = ""
    if artifact and artifact.exists():
        match = url_pattern.search(artifact.read_text(encoding="utf-8", errors="ignore"))
        base_url = match.group(1).rstrip("/") if match else ""
    if not base_url:
        raise SystemExit(f"cannot resolve mock base url for task {row.get('task_id')}")

    setup = [step for step in row.get("setup", []) if step.get("type") != "shell"]
    setup.append(
        {
            "type": "shell",
            "parameters": {"command": 'python "C:\\tmp\\initial_setup.py"'},
        }
    )
    setup.append(
        {
            "type": "shell",
            "parameters": {
                "command": (
                    "powershell -NoProfile -Command \""
                    "$sid=Get-Content 'C:\\tmp\\task_web_sid'; "
                    f"Start-Process msedge ('{base_url}/?sid='+$sid); "
                    "Start-Sleep -Seconds 3\""
                )
            },
        }
    )
    row["setup"] = setup

with path.open("w", encoding="utf-8") as handle:
    for row in rows:
        print(json.dumps(row, ensure_ascii=False), file=handle)
print(f"rewrote {len(rows)} tasks in {path}")
PY
