#!/usr/bin/env bash
# End-to-end demo on the synthetic sample. Runs fully offline (--mock).
set -euo pipefail
cd "$(dirname "$0")"

echo "=== 1. connect (mock, offline) ==="
python3 -m agent connect --mock data/ticket-sample.json --redact --project ticket-sample

echo; echo "=== 2. learn (profile + propose taxonomy) ==="
python3 -m agent learn data/ticket-sample.canonical.json

echo; echo "=== 3. learn --approve (human gate) ==="
python3 -m agent learn --approve

echo; echo "=== 4. triage (clusters + effective priority) ==="
python3 -m agent triage data/ticket-sample.canonical.json

echo; echo "=== 5. solve (root cause + playbook) ==="
python3 -m agent solve

echo; echo "=== 6. report ==="
python3 -m agent report data/ticket-sample.canonical.json --format terminal

echo; echo "=== 7. learn --eval (F1 against cluster_hint labels) ==="
python3 -m agent learn --eval data/ticket-sample.json
