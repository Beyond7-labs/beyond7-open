#!/usr/bin/env bash
# Der ordentliche Ordner plus je Signal ein bis zwei eingebaute Funde.
# Erwartet (9 Funde):
#   notizdatei:     kunden/acme/wissen/ideen.md, notes.md, projekte/umzug/MIGRATION_LOG.md
#   kopie:          kunden/beta/angebote/angebot Kopie.md, preise.md doppelt (kunden/gamma/wissen + projekte)
#   verweis:        kunden/delta/README.md → wissen/protokoll-alt.md
#   ueberbleibsel:  kunden/epsilon/__MACOSX/, .playwright-mcp/
#   daneben:        kunden/acme/
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$HERE/ordentlich.sh"

printf '# Ideen\n\n- Workshop für Acme\n' > kunden/acme/wissen/ideen.md
printf '# Notizen\n\nAlles Mögliche.\n' > notes.md
mkdir -p projekte/umzug
printf '# Migration\n\nSchritt 1 erledigt.\n' > projekte/umzug/MIGRATION_LOG.md

cp kunden/beta/angebote/2026-09_angebot.md "kunden/beta/angebote/angebot Kopie.md"
preise='# Preise

- Workshop halbtags: 1.800 Euro netto
- Workshop ganztags: 3.000 Euro netto
- Begleitung: 1.400 Euro pro Tag, abrechnung monatlich
- Reisekosten nach Aufwand, Bahn zweite Klasse
- Absage bis 14 Tage vorher kostenlos, danach 50 Prozent
'
printf '%s' "$preise" > kunden/gamma/wissen/preise.md
printf '%s' "$preise" > projekte/preise.md

printf '# delta\n\nSiehe [Protokoll](wissen/protokoll-alt.md).\n' > kunden/delta/README.md

mkdir -p kunden/epsilon/__MACOSX
printf 'x' > kunden/epsilon/__MACOSX/._angebot
mkdir -p .playwright-mcp
printf 'x\n' > .playwright-mcp/page-2026-10-21.yml

printf 'Rechnung\n' > kunden/acme/rechnung.txt
printf '# Stichpunkte\n' > kunden/acme/stichpunkte.md
printf 'pdf' > kunden/acme/Angebot_alt.pdf

git add -A
git -c user.name=Test -c user.email=test@example.com commit -qm "Wildwuchs"
