#!/usr/bin/env bash
# Ein ordentlicher Arbeitsordner. Hier darf drift-check nichts finden.
# Läuft im (leeren) aktuellen Ordner.
set -euo pipefail

cat > CLAUDE.md <<'EOF'
# Arbeitsordner

- `kunden/{name}/`: pro Kunde ein `README.md` (Steckbrief), `wissen/` (Notizen aus Gesprächen) und `angebote/`
- `journal/`: ein Eintrag pro Tag
- `projekte/{name}/`: eigene Projekte, Skripte liegen beim Projekt
- `kapitel/`: Schulungskapitel, je eine `KAPITEL.md`
- `archiv/`: Abgelegtes, wird nicht mehr gepflegt
EOF

cat > README.md <<'EOF'
# Mein Arbeitsordner

Einstieg: [Kunden](kunden/acme/README.md), [Journal](journal/).
EOF

for k in acme beta gamma delta epsilon; do
  mkdir -p "kunden/$k/wissen" "kunden/$k/angebote"
  printf '# %s\n\nSteckbrief. Notizen liegen in [wissen](wissen/).\n' "$k" > "kunden/$k/README.md"
  printf '# Erstgespräch %s\n\n- Ziel besprochen\n' "$k" > "kunden/$k/wissen/2026-09-01_erstgespraech.md"
  printf '# Angebot %s\n\nWorkshop, ein Tag.\n' "$k" > "kunden/$k/angebote/2026-09_angebot.md"
done

mkdir -p journal
for d in 01 02 03 04 05 06 07 08 09; do
  printf -- '---\ndate: 2026-10-%s\nmood: gut\n---\n\n# Tag\n' "$d" > "journal/2026-10-$d.md"
done

mkdir -p projekte/auswertung
printf '# Auswertung\n\nDas Skript `auswertung.py` erzeugt die Tabelle.\n' > projekte/auswertung/README.md
printf 'print("ok")\n' > projekte/auswertung/auswertung.py

mkdir -p archiv
printf '# Plan 2025\n\nSiehe [alter Plan](../gibt-es-nicht-mehr.md).\n' > archiv/2025-plan.md

for c in a b c d e f g; do
  mkdir -p "kapitel/$c"
  printf '# Kapitel %s\n' "$c" > "kapitel/$c/KAPITEL.md"
done

printf '.DS_Store\n*.log\n' > .gitignore
touch .DS_Store
printf 'debug\n' > debug.log

git init -q
git add -A
git -c user.name=Test -c user.email=test@example.com commit -qm "Ausgangsstand"
