#!/usr/bin/env bash
set -euo pipefail
bash "$(dirname "${BASH_SOURCE[0]}")/../_fixtures/ordentlich.sh"
cat > ordnungs-check-2026-01-01.md <<'EOF'
# Ordnungs-Check vom 01.01.2026

> Arbeitszettel: Lösche diese Datei, wenn du aufgeräumt hast.

- `notes.md`
EOF
