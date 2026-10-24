---
name: check
description: Ordnungs-Check (Drift) für einen Arbeitsordner. Zeigt in Alltagssprache, wo der Ordner seine Ordnung verliert (Notizdateien ohne festen Platz, Kopien, Verweise ins Leere, Überbleibsel von Programmen, lose Dateien, Gewohnheiten ohne Regel), und schreibt einen Report zum Abarbeiten. Nutzen bei „Ist mein Ordner noch in Ordnung?“, „Ordnungs-Check“, „Drift-Check“, „Wildwuchs“, „hier liegt alles durcheinander“, „was müsste ich aufräumen?“, „drift check“. Nicht für das Aufräumen einer einzelnen, konkret genannten Datei.
---

# Ordnungs-Check (Drift)

Du prüfst, ob dieser Arbeitsordner seine eigene Ordnung verliert, und schreibst dazu einen Report. Wer das nutzt, ist meist kein Entwickler. Schreib so, wie du es einer Kollegin erklären würdest, in der Sprache, in der der Nutzer mit dir spricht (Standard: Deutsch).

„Drift“ heißt: Ein Ordner entfernt sich Stück für Stück von seiner eigenen Ordnung, meist weil eine Information keinen festen Platz hatte. Das ist normal und kein Versagen.

## Ablauf

1. **Alter Report.** Liegt im Hauptordner schon eine `ordnungs-check-*.md`, erwähne das ganz oben in deiner Antwort und frag, ob sie weg kann. Lösch sie nicht selbst. Mach mit dem Check trotzdem weiter.
2. **Scan.** Führe aus:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/drift_scan.py" .
   ```
   Klappt `python3` nicht, versuch `python`. Das Skript ändert nichts und gibt JSON aus.
   - `"error": "too_many_files"`: Der Ordner ist zu groß. Schlag vor, einen Unterordner zu prüfen (Pfad statt `.` angeben).
   - Kein Python oder ein Fehler: Sag das offen. Such dann mit Glob nur nach Notizdateien (`**/notes.md`, `**/notizen.md`, `**/ideas.md`, `**/ideen.md`, `**/todo.md`), Kopien (`**/* Kopie*`, `**/*(1)*`) und Überbleibseln (`**/__MACOSX`, `**/.playwright-mcp`) und schreib in den Report, dass nur ein Teil geprüft wurde.
3. **Kontext.** Gibt es eine `CLAUDE.md` im Hauptordner, lies sie. Du nutzt sie nur, um für jeden Fund einen passenden Platz vorzuschlagen. Ohne CLAUDE.md schlägst du einen naheliegenden Ort aus der vorhandenen Ordnerstruktur vor.
4. **Report.** Schreib ihn als `ordnungs-check-JJJJ-MM-TT.md` (heutiges Datum) in den Hauptordner, nach der Vorlage unten. Darfst du dort nicht schreiben, gib ihn im Chat aus.
5. **Chat.** Höchstens fünf Zeilen: wie viele Funde, die wichtigste Gruppe, wo der Report liegt, und dass man ihn nach dem Aufräumen löschen soll.
6. **Sonst nichts ändern.** Nicht aufräumen, nichts verschieben, nichts löschen, solange der Nutzer nicht darum bittet.

## Wenn der Nutzer aufräumen will

- Eine Gruppe nach der anderen. Vorher zeigen, was genau passiert: welche Datei wohin.
- Löschen und Verschieben erst nach einem ausdrücklichen Ja.
- Inhalte aus Notizdateien nicht wegwerfen: erst dort einarbeiten, wo sie hingehören, dann die Notizdatei löschen.
- Vorschläge für Regeln: eine Formulierung für die CLAUDE.md vorschlagen und erst nach Zustimmung eintragen.

## Was die Signale bedeuten

Funde (`findings`):

| `signal` | Überschrift im Report | Warum das stört |
|---|---|---|
| `notizdatei` | Notizdateien ohne festen Platz | Sie sammeln alles, was sonst nirgends hinpasst. Mit der Zeit weiß niemand mehr, was darin steht, und die nächste landet daneben. |
| `kopie` | Kopien | Zwei Fassungen derselben Sache: Irgendwann ist unklar, welche gilt. |
| `verweis` | Verweise ins Leere | Eine Datei zeigt auf etwas, das es nicht mehr gibt, meist nach einem Umzug. |
| `ueberbleibsel` | Überbleibsel von Programmen | Reste, die Programme beim Arbeiten liegen lassen. Für dich steht nichts darin. |
| `daneben` | Dateien neben ihren Ordnern | Die Ordner auf dieser Ebene sind sauber sortiert, hier liegen Dateien lose daneben. |

Vorschläge (`suggestions`), im Report als Fragen, nicht als Fehler:

| `kind` | Überschrift im Report | Warum das wichtig ist |
|---|---|---|
| `gewohnheit-ohne-regel` | Gewohnheit ohne Regel | Es wird schon so gemacht, aufgeschrieben ist es nirgends. Als Regel bleibt es auch künftig so. |
| `zwei-gewohnheiten` | Zwei Gewohnheiten für dasselbe | Für dieselbe Sache gibt es zwei Arten. Wer neu dazukommt, auch Claude, weiß nicht, welche gilt. |

## Vorlage für den Report

```markdown
# Ordnungs-Check vom TT.MM.JJJJ

> Arbeitszettel: Lösche diese Datei, wenn du aufgeräumt hast.

**Kurz:** An N Stellen verliert dein Ordner seine Ordnung. <Einordnung in einem Satz, z. B. „Nichts davon ist dringend.“>
„Drift“ heißt: Ein Ordner entfernt sich Stück für Stück von seiner eigenen Ordnung,
meist weil eine Information keinen festen Platz hatte.

## <Überschrift der Gruppe> (Anzahl)
<Warum das stört, ein Satz.>
- `pfad` → Vorschlag: <wohin oder was tun>

## Vorschläge für deine Regeln
- <Vorschlag als Frage, z. B. „In 4 von 6 Kundenordnern gibt es `ausgang/`, aufgeschrieben ist das nirgends. Soll das eine Regel in deiner CLAUDE.md werden?“>

## So gehst du vor
1. Gruppe für Gruppe durchgehen. Claude hilft dabei, z. B. „Räum die Kopien auf“.
2. Vorschläge für Regeln in die CLAUDE.md übernehmen oder verwerfen.
3. Diese Datei löschen.
```

Leere Gruppen lässt du weg. Ohne Funde und Vorschläge schreibst du einen kurzen Report „Alles in Ordnung“ mit Datum und der Zeile zum Löschen.

## Sprache

- Keine Fachbegriffe ohne Übersetzung. Nicht: Repo, Repository, Artefakt, Regex, Konvention, Commit, JSON. Stattdessen: Ordner, Überbleibsel, Gewohnheit.
- Pfade in Backticks, damit man sie wiederfindet.
- Höchstens 10 Einträge pro Gruppe, dann „+ N weitere“.
- Mehrere Funde im selben Ordner zusammenfassen, z. B. „4 Dateien in `kunden/acme/alt/` sind Kopien“.
- Ruhiger Ton. Nicht alarmieren, nicht belehren.
