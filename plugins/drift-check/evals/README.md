# Evals für drift-check

Qualitätskontrolle für uns als Entwickler, nicht für Nutzer. Die Evals prüfen, ob das Plugin zuverlässig findet, was da ist, und schweigt, wo nichts ist. Nutzer brauchen dafür nichts: Der Ordner wird mitinstalliert, tut bei ihnen aber nichts.

## Ausführen

```bash
# Schnelltest des Skripts, ohne Modell, kostenlos, unter 1 Sekunde (aus dem Marketplace-Ordner)
python3 -m unittest discover tests

# Alle Evals (aus plugins/drift-check), etwa 2,50 $ pro Lauf mit 3 Durchläufen je Fall
claude plugin eval . --runs 3 --ablation none -j 3 --scaffold --trust-plugin --no-publish \
  --max-cost-usd 6 --allow-tools Write "Bash(python3 *)" "Bash(python *)"
```

Vor jeder Veröffentlichung beides laufen lassen. Ergebnisse landen in `results/<zeitstempel>/report.html` (nicht im Git). Zum Nachsehen eines Laufs `--keep-temp` anhängen.

## Wie ein Lauf funktioniert

1. Claude Code legt für jeden einzelnen Durchlauf einen leeren Ordner im Temp-Verzeichnis an.
2. Das `scaffold.sh` des Falls baut dort den Testordner auf (nur mit `--scaffold`, es läuft mit deinen Rechten).
3. Eine frische Claude-Session mit nur diesem Plugin bekommt die Frage aus `case.yaml`.
4. Die Prüfer in `case.yaml` werten aus, danach wird der Ordner gelöscht.

## Aufbau

| Pfad | Inhalt |
|---|---|
| `_fixtures/ordentlich.sh` | Grundordner, in dem nichts gefunden werden darf |
| `_fixtures/wildwuchs.sh` | ordentlich plus eingebaute Funde, erwartete Liste steht oben im Skript |
| `_fixtures/gewohnheit.sh` | Kundenordner mit einer Gewohnheit, die nirgends als Regel steht |
| `<fall>/case.yaml` | Frage, Limits, erlaubte Tools, Prüfer |
| `<fall>/scaffold.sh` | ruft den passenden Bauplan auf |
| `../../../tests/test_drift_scan.py` | nutzt dieselben Baupläne, prüft nur das Skript |

## Regeln für Testordner

1. **Nur künstliche Daten.** Das Repo ist öffentlich: keine echten Kunden, keine Inhalte aus echten Arbeitsordnern.
2. **Klein.** So viele Dateien, dass jedes Signal etwas zu finden hat, nicht mehr (derzeit rund 40).
3. **Fest statt zufällig.** Feste Namen, feste Daten, Git-Repo mit Commit. Jeder Durchlauf sieht exakt gleich aus.
4. **`ordentlich` enthält alles, was nicht gemeldet werden darf.** Grundlage sind die Fehlalarme aus den Messungen vom 23.10.2026: Journal-Serie, datierte Meeting-Notizen, Archiv mit totem Link, gleicher Dateiname als Gewohnheit, Projekt mit Skript, ignorierte Dateien.
5. **`wildwuchs` ist `ordentlich` plus ein bis zwei eingebaute Funde pro Signal.** Die erwartete Liste steht oben im Skript und in den Tests.
6. **Der Testordner wächst mit der Praxis.**
   - Fehlalarm in echter Nutzung → das Muster in `ordentlich.sh` einbauen.
   - Übersehener Fund → in `wildwuchs.sh` einbauen und die erwartete Liste ergänzen.
   - Neues Signal → einbauen in `wildwuchs.sh`, Erwartung in `tests/test_drift_scan.py` und im Prüfer von `findet-wildwuchs/case.yaml` ergänzen.
