"""Tests für drift_scan.py gegen die Testordner aus evals/_fixtures.

Aufruf aus dem Marketplace-Ordner: python3 -m unittest discover tests
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "drift-check"
SCAN = PLUGIN / "scripts" / "drift_scan.py"
FIXTURES = PLUGIN / "evals" / "_fixtures"


def scan_fixture(name, extra=None):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["bash", str(FIXTURES / f"{name}.sh")], cwd=tmp, check=True)
        if extra:
            extra(Path(tmp))
        out = subprocess.run([sys.executable, str(SCAN), tmp], capture_output=True, text=True, check=True)
        return json.loads(out.stdout)


def pairs(result):
    return {(f["signal"], f["path"]) for f in result["findings"]}


class Ordentlich(unittest.TestCase):
    def test_findet_nichts(self):
        r = scan_fixture("ordentlich")
        self.assertEqual(r["findings"], [])
        self.assertEqual(r["suggestions"], [])
        self.assertTrue(r["git"])

    def test_ohne_git_gilt_gitignore(self):
        r = scan_fixture("ordentlich", lambda p: shutil.rmtree(p / ".git"))
        self.assertFalse(r["git"])
        self.assertEqual(r["findings"], [])

    def test_alter_report_ist_kein_fund(self):
        def add_report(p):
            (p / "ordnungs-check-2026-01-01.md").write_text("# Ordnungs-Check\n\n- notes.md\n")
        r = scan_fixture("ordentlich", add_report)
        self.assertEqual(r["findings"], [])
        self.assertEqual(r["old_reports"], ["ordnungs-check-2026-01-01.md"])


class Wildwuchs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = scan_fixture("wildwuchs")

    def test_notizdateien(self):
        for p in ["kunden/acme/wissen/ideen.md", "notes.md", "projekte/umzug/MIGRATION_LOG.md"]:
            self.assertIn(("notizdatei", p), pairs(self.r))

    def test_kopien(self):
        self.assertIn(("kopie", "kunden/beta/angebote/angebot Kopie.md"), pairs(self.r))
        dup = [f for f in self.r["findings"] if f["signal"] == "kopie" and "preise.md" in f["path"]]
        self.assertEqual(len(dup), 1)

    def test_verweis_ins_leere(self):
        self.assertIn(("verweis", "kunden/delta/README.md"), pairs(self.r))

    def test_ueberbleibsel(self):
        self.assertIn(("ueberbleibsel", "kunden/epsilon/__MACOSX/"), pairs(self.r))
        self.assertIn(("ueberbleibsel", ".playwright-mcp/"), pairs(self.r))

    def test_daneben(self):
        self.assertIn(("daneben", "kunden/acme/"), pairs(self.r))

    def test_nichts_sonst(self):
        self.assertEqual(len(self.r["findings"]), 9, json.dumps(self.r["findings"], indent=1, ensure_ascii=False))
        self.assertEqual(self.r["suggestions"], [])


class Gewohnheit(unittest.TestCase):
    def test_genau_ein_vorschlag(self):
        r = scan_fixture("gewohnheit")
        self.assertEqual(r["findings"], [])
        self.assertEqual(len(r["suggestions"]), 1, r["suggestions"])
        s = r["suggestions"][0]
        self.assertEqual(s["kind"], "gewohnheit-ohne-regel")
        self.assertIn("ausgang", s["detail"])


if __name__ == "__main__":
    unittest.main()
