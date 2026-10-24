#!/usr/bin/env python3
"""drift_scan.py: Teil des Plugins drift-check („Ordnungs-Check (Drift)“).

Liest einen Arbeitsordner und meldet Stellen, an denen er seine Ordnung verliert.
Ändert nichts. Ausgabe ist JSON auf stdout, die Sprache für Menschen macht der Skill.

Aufruf: python3 drift_scan.py [ordner]
"""
import collections
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import PurePosixPath as P
from urllib.parse import unquote

VERSION = 1
MAX_FILES = 20000

SKIP_DIRS = {".git", "node_modules", ".claude"}
ARCHIVE_RE = re.compile(r"(?i)(^|/)_?(archiv|archive|old|alt)(/|$)")
BUILD_RE = re.compile(r"(^|/)(public|assets|static|dist|build)/")
REPORT_RE = re.compile(r"^ordnungs-check-\d{4}-\d{2}-\d{2}\.md$")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}|\d{4}_\d{2}_\d{2}|\d{8}")
STRUCT_FILES = {"readme.md", "claude.md", "agents.md", "index.md", "index.html"}

NOTE_EXACT = {
    "notes", "notizen", "ideas", "ideen", "todo", "todos",
    "memory", "memories", "misc", "sonstiges", "scratch", "temp", "tmp", "inbox",
    "untitled", "unbenannt", "migration", "learnings",
}
NOTE_SUFFIX_RE = re.compile(r"(?i)[-_ ](notes|notizen|ideas|ideen|todo|todos|log)$")
COPY_RE = re.compile(r"(?i)((^|[\s_\-(])(kopie|copy)(\s*\(?\d*\)?)$|^(kopie von|copy of)\s|\(\d+\)$)")
ART_DIRS = {"__MACOSX", ".playwright-mcp", "__pycache__", ".pytest_cache", ".ipynb_checkpoints"}
ART_FILE_RE = re.compile(r"(?i)(\.log$|\.tmp$|^~\$|^\.~lock|^thumbs\.db$)")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
CODEBLOCK_RE = re.compile(r"```.*?```", re.S)
INFO_RE = re.compile(r"(?i)^[a-z0-9]+_info\.md$")


def fail(code, **info):
    print(json.dumps({"version": VERSION, "error": code, **info}, ensure_ascii=False))
    sys.exit(2)


def git(root, *args, stdin=None):
    try:
        r = subprocess.run(["git", "-C", root, *args], input=stdin, capture_output=True, text=True)
    except FileNotFoundError:
        return None
    return r.stdout if r.returncode == 0 else None


def skipped(path):
    return any(part in SKIP_DIRS for part in P(path).parts)


def archived(path):
    return bool(ARCHIVE_RE.search(path))


def ignore_patterns(root):
    """Einfache Muster aus der .gitignore im Hauptordner, für Ordner ohne nutzbares Git."""
    pats = []
    for line in read_text(root, ".gitignore").splitlines():
        line = line.strip()
        if line and not line.startswith(("#", "!")):
            pats.append(line.strip("/"))
    return pats


def ignored_by(path, pats):
    path = path.rstrip("/")
    for pat in pats:
        if "/" in pat:
            if fnmatch.fnmatch(path, pat) or path.startswith(pat + "/"):
                return True
        elif any(fnmatch.fnmatch(part, pat) for part in path.split("/")):
            return True
    return False


def list_files(root):
    """Alle Dateien relativ zu root. Mit Git: getrackt plus neu und nicht ignoriert."""
    out = git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    if out is not None:
        files = [f for f in out.split("\0") if f and not f.endswith("/")]
        files = [f for f in set(files) if os.path.isfile(os.path.join(root, f))]
        return sorted(f for f in files if not skipped(f)), True
    pats = ignore_patterns(root)
    files = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not os.path.exists(os.path.join(dp, d, ".git"))]
        for fn in fns:
            rel = os.path.relpath(os.path.join(dp, fn), root).replace(os.sep, "/")
            if not ignored_by(rel, pats):
                files.append(rel)
    return sorted(files), False


def read_text(root, path):
    try:
        with open(os.path.join(root, path), encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def tree(files):
    """Ordner → direkte Unterordner und Dateien."""
    t = collections.defaultdict(lambda: {"dirs": set(), "files": set()})
    for f in files:
        parts = P(f).parts
        for i in range(len(parts)):
            parent = "/".join(parts[:i]) or "."
            if i == len(parts) - 1:
                t[parent]["files"].add(parts[i])
            else:
                t[parent]["dirs"].add(parts[i])
    return t


def join(parent, name):
    return name if parent == "." else f"{parent}/{name}"


def scan_notes(files):
    found = []
    for f in files:
        if P(f).suffix.lower() not in (".md", ".txt") or archived(f):
            continue
        stem = P(f).stem
        if stem.lower() in NOTE_EXACT:
            found.append((f, "Notizdatei ohne festen Platz"))
        elif not DATE_RE.search(stem) and NOTE_SUFFIX_RE.search(stem):
            found.append((f, "Notizdatei ohne festen Platz"))
    return found


def scan_copies(root, files):
    found = {}
    for f in files:
        if not archived(f) and COPY_RE.search(P(f).stem):
            found[f] = "Name sagt: Kopie"
    groups = collections.defaultdict(list)
    for f in files:
        if P(f).suffix.lower() not in (".md", ".txt", ".html") or archived(f) or BUILD_RE.search(f):
            continue
        full = os.path.join(root, f)
        try:
            if os.path.getsize(full) < 200:
                continue
            with open(full, "rb") as fh:
                groups[hashlib.sha1(fh.read()).hexdigest()].append(f)
        except OSError:
            continue
    for group in groups.values():
        if len(group) < 2:
            continue
        group.sort(key=lambda x: (x in found, len(x), x))
        for dup in group[1:]:
            found.setdefault(dup, f"gleicher Inhalt wie {group[0]}")
    return sorted(found.items())


def scan_links(root, files):
    found = []
    for f in files:
        if P(f).suffix.lower() != ".md" or archived(f):
            continue
        dead = []
        for target in LINK_RE.findall(CODEBLOCK_RE.sub("", read_text(root, f))):
            if re.match(r"^(https?:|mailto:|#|tel:|data:|/|~)", target) or any(c in target for c in "{}<>*$"):
                continue
            target = unquote(target.split("#")[0].split("?")[0])
            if not target or not (re.search(r"\.[A-Za-z0-9]{1,6}$", target) or target.endswith("/")):
                continue
            near = os.path.normpath(os.path.join(root, str(P(f).parent), target))
            top = os.path.normpath(os.path.join(root, target))
            if not os.path.exists(near) and not os.path.exists(top) and target not in dead:
                dead.append(target)
        if dead:
            found.append((f, "zeigt ins Leere: " + ", ".join(dead)))
    return found


def scan_leftovers(root, use_git):
    found = []
    for dp, dns, fns in os.walk(root):
        rel = os.path.relpath(dp, root).replace(os.sep, "/")
        rel = "" if rel == "." else rel + "/"
        keep = []
        for d in dns:
            if d in SKIP_DIRS or (os.path.exists(os.path.join(dp, d, ".git"))):
                continue
            if d in ART_DIRS:
                found.append(rel + d + "/")
            else:
                keep.append(d)
        dns[:] = keep
        found += [rel + fn for fn in fns if ART_FILE_RE.search(fn)]
    found = [x for x in found if not archived(x)]
    if use_git and found:
        out = git(root, "check-ignore", "--stdin", stdin="\n".join(x.rstrip("/") for x in found)) or ""
        ignored = set(out.split("\n"))
        found = [x for x in found if x.rstrip("/") not in ignored]
    elif found:
        pats = ignore_patterns(root)
        found = [x for x in found if not ignored_by(x, pats)]
    return [(x, "Überbleibsel eines Programms") for x in sorted(found)]


def loose_files(t, folder):
    return sorted(
        f for f in t[folder]["files"]
        if f.lower() not in STRUCT_FILES and not INFO_RE.match(f) and not f.startswith(".") and not REPORT_RE.match(f)
    )


def child_dirs(t, parent):
    return [d for d in t[parent]["dirs"] if d not in ART_DIRS and not archived(join(parent, d))]


def scan_beside(t):
    found = []
    for parent in list(t):
        kids = child_dirs(t, parent)
        if len(kids) < 5 or archived(parent):
            continue
        paths = [join(parent, k) for k in kids]
        clean = sum(1 for p in paths if not loose_files(t, p)) / len(paths)
        structured = sum(1 for p in paths if child_dirs(t, p)) / len(paths)
        if clean < 0.7 or structured < 0.7:
            continue
        for p in paths:
            loose = loose_files(t, p)
            if len(loose) >= 2:
                found.append((p + "/", f"{len(loose)} Dateien liegen neben den Unterordnern: " + ", ".join(loose)))
    return sorted(found)


def rule_texts(root, files):
    texts = [read_text(root, f) for f in files if P(f).name == "CLAUDE.md"]
    if "README.md" in files:
        texts.append(read_text(root, "README.md"))
    rules = os.path.join(root, ".claude", "rules")
    if os.path.isdir(rules):
        for fn in sorted(os.listdir(rules)):
            if fn.endswith(".md"):
                texts.append(read_text(root, f".claude/rules/{fn}"))
    return "\n".join(texts)


def mentioned(name, text):
    return re.search(rf"(?i)(?<![A-Za-z0-9_-]){re.escape(name)}(?![A-Za-z0-9_-])", text) is not None


def scan_habits(t, rules):
    suggestions = []
    for parent in sorted(t):
        kids = child_dirs(t, parent)
        if len(kids) < 3 or archived(parent):
            continue
        counts = collections.Counter()
        where = collections.defaultdict(list)
        for k in kids:
            for sub in child_dirs(t, join(parent, k)):
                if not sub.startswith("."):
                    counts[sub] += 1
                    where[sub].append(join(join(parent, k), sub) + "/")
        for sub, n in sorted(counts.items()):
            if n >= 3 and not mentioned(sub, rules):
                suggestions.append({
                    "kind": "gewohnheit-ohne-regel",
                    "detail": f"`{sub}/` gibt es in {n} von {len(kids)} Ordnern unter `{parent}/`, aufgeschrieben ist das nirgends",
                    "examples": where[sub][:3],
                })
    return suggestions


def profile_patterns(t, folder):
    """Steckbrief-Dateien eines Ordners: direkt oder eine Ebene tiefer."""
    pats = set()
    for f in t[folder]["files"]:
        if f.lower() == "readme.md" or INFO_RE.match(f):
            pats.add(f)
    for sub in child_dirs(t, folder):
        for f in t[join(folder, sub)]["files"]:
            if f.lower() == "readme.md" or INFO_RE.match(f):
                pats.add(f"{sub}/{f}")
    return pats


def scan_competing(t):
    suggestions = []
    for parent in sorted(t):
        kids = child_dirs(t, parent)
        if len(kids) < 5 or archived(parent):
            continue
        has = {k: profile_patterns(t, join(parent, k)) for k in kids}
        counts = collections.Counter(p for pats in has.values() for p in pats)
        common = [p for p, n in counts.most_common() if n >= 2 and n / len(kids) >= 0.1]
        for i, a in enumerate(common):
            for b in common[i + 1:]:
                both = sum(1 for pats in has.values() if a in pats and b in pats)
                if both < 0.5 * min(counts[a], counts[b]):
                    suggestions.append({
                        "kind": "zwei-gewohnheiten",
                        "detail": f"Unter `{parent}/` gibt es zwei Arten Steckbrief: `{a}` ({counts[a]} von {len(kids)}) und `{b}` ({counts[b]} von {len(kids)})",
                        "examples": [join(join(parent, k), b) for k in kids if b in has[k]][:3],
                    })
    return suggestions


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    if not os.path.isdir(root):
        fail("not_a_folder", root=root)
    files, use_git = list_files(root)
    old_reports = sorted(f for f in files if "/" not in f and REPORT_RE.match(f))
    files = [f for f in files if not REPORT_RE.match(P(f).name)]
    if len(files) > MAX_FILES:
        fail("too_many_files", root=root, files=len(files), limit=MAX_FILES)

    t = tree(files)
    findings = []
    for signal, items in [
        ("notizdatei", scan_notes(files)),
        ("kopie", scan_copies(root, files)),
        ("verweis", scan_links(root, files)),
        ("ueberbleibsel", scan_leftovers(root, use_git)),
        ("daneben", scan_beside(t)),
    ]:
        findings += [{"signal": signal, "path": p, "detail": d} for p, d in items]

    suggestions = scan_habits(t, rule_texts(root, files)) + scan_competing(t)
    print(json.dumps({
        "version": VERSION,
        "root": root,
        "git": use_git,
        "files_scanned": len(files),
        "findings": findings,
        "suggestions": suggestions,
        "old_reports": old_reports,
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
