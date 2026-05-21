#!/usr/bin/env bash
# Start Streamlit demo reachable from phone on same Wi‑Fi.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -d venv ]]; then
  echo "Create venv first: python3 -m venv venv && ./venv/bin/pip install -r requirements.txt"
  exit 1
fi

if [[ ! -f data/processed/chunks.jsonl ]]; then
  echo "Building knowledge base..."
  ./venv/bin/python -m src.cli ingest
fi

IP=$(python3 -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 80))
print(s.getsockname()[0])
s.close()
" 2>/dev/null || echo "127.0.0.1")

echo ""
echo "  On your phone (same Wi‑Fi), open:"
echo "  http://${IP}:8081"
echo ""

exec ./venv/bin/streamlit run demo_app.py
