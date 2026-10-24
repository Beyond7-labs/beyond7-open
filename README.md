# Beyond7 Labs: Plugins für Claude Code

Werkzeuge für Arbeitsordner, in denen Claude Code mitarbeitet: Projekte, Kundenordner, Notizen, kein Software-Code nötig.

## Installation

In Claude Code:

```
/plugin marketplace add Beyond7-labs/marketplace
/plugin install drift-check@beyond7-labs
```

Oder im Terminal:

```bash
claude plugin marketplace add Beyond7-labs/marketplace
claude plugin install drift-check@beyond7-labs
```

## Plugins

| Plugin | Was es tut |
|---|---|
| **Ordnungs-Check (Drift)** · `drift-check` | Zeigt in Alltagssprache, wo dein Arbeitsordner seine Ordnung verliert: Notizdateien ohne festen Platz, Kopien, Verweise ins Leere, Überbleibsel von Programmen, lose Dateien und Gewohnheiten, die nirgends als Regel stehen. Schreibt einen Report zum Abarbeiten und ändert sonst nichts. Einfach fragen: „Ist mein Ordner noch in Ordnung?“ |

## Für Entwickler

Jedes Plugin bringt Tests und Evals mit, siehe [`plugins/drift-check/evals/README.md`](plugins/drift-check/evals/README.md).

---

Von [Hendrik Hemken](https://hendrikhemken.com) · [Beyond7](https://beyond7.ai) · Lizenz: MIT
