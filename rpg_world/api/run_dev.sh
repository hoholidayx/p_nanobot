#!/usr/bin/env bash
# Start RPG World API (FastAPI) in development mode
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/settings.json'))['port'])")
cd "$SCRIPT_DIR/../.."  # project root
exec uv run uvicorn rpg_world.api.main:app --reload --host 127.0.0.1 --port "$PORT"
