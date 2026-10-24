#!/usr/bin/env bash
# Sechs Kundenordner, vier davon mit `ausgang/`, das in keiner Regel steht.
# Erwartet: keine Funde, genau ein Vorschlag „Gewohnheit ohne Regel“ für ausgang.
set -euo pipefail

cat > CLAUDE.md <<'EOF'
# Arbeitsordner

- `kunden/{name}/`: pro Kunde ein `README.md` (Steckbrief) und `wissen/` für Notizen
EOF

i=0
for k in acme beta gamma delta epsilon zeta; do
  i=$((i + 1))
  mkdir -p "kunden/$k/wissen"
  printf '# %s\n\nSteckbrief.\n' "$k" > "kunden/$k/README.md"
  printf '# Erstgespräch\n' > "kunden/$k/wissen/2026-09-01_erstgespraech.md"
  if [ "$i" -le 4 ]; then
    mkdir -p "kunden/$k/ausgang"
    printf 'Hallo,\n\nanbei das Angebot.\n' > "kunden/$k/ausgang/2026-10-0${i}_mail-angebot.md"
  fi
done

git init -q
git add -A
git -c user.name=Test -c user.email=test@example.com commit -qm "Ausgangsstand"
