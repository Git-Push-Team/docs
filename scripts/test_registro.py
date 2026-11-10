#!/usr/bin/env python3
"""
Prove automatiche del registro delle modifiche automatico.

    python3 scripts/test_registro.py

Non usano la rete: GitHub è simulato. Lavorano in una cartella temporanea
con un piccolo repository finto, quindi non toccano i vostri file.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registro as R  # noqa: E402

TOML = """
[membri]
biasini    = { nome = "Enrico Biasini",      github = "enricobiasini" }
corro      = { nome = "Alessio Corrò",       github = "alec0r" }
guglielmo  = { nome = "Francesco Guglielmo", github = "firestone109" }
spagnoli   = { nome = "Gaetano Spagnoli",    github = "gaexxx" }

[[sprint]]
numero = 1
inizio = 2026-11-02
fine = 2026-11-15
[sprint.ruoli]
spagnoli = { Responsabile = 4.5 }
corro = { Verificatore = 9.5 }
"""

DOCUMENTO = r"""\documentclass[documento]{gpt}
\titolo{Piano di progetto}

% ---------------------------------------------------------------------
% Registro delle modifiche
% ---------------------------------------------------------------------
% Sintassi: \modifica{versione}{AAAA-MM-GG}{autore}{verificatore}{descrizione}
\modifica{0.2.0}{2026-11-04}{spagnoli, guglielmo}{corro}{Stesura della sezione 2}
\modifica{0.1.0}{2026-11-02}{spagnoli}{corro}{Prima stesura}

\begin{document}
Testo con \modifica{9.9.9}{x}{y}{z}{nel corpo: non conta}
\end{document}
"""

VERBALE = r"""\documentclass[verbale=interno]{gpt}
\titolo{Riunione}
\data{2026-11-03}
\modifica{0.1.0}{2026-11-03}{guglielmo}{corro}{Stesura del verbale}
\begin{document}
\end{document}
"""


def pr(numero, etichette, autore="firestone109", titolo="Titolo della PR", corpo="",
       unita="2026-11-10T16:00:00Z"):
    return {"number": numero, "title": titolo, "body": corpo, "merged_at": unita,
            "user": {"login": autore}, "labels": [{"name": e} for e in etichette]}


def revisione(login, stato):
    return {"user": {"login": login}, "state": stato}


def etichettata(login, nome="approvazione", quando="2026-11-10T15:00:00Z"):
    return {"event": "labeled", "label": {"name": nome}, "actor": {"login": login},
            "created_at": quando}


class FintoGitHub:
    """Risponde come GitHub, con dati preparati dalle prove."""
    repo = "Git-Push-Team/docs"

    def __init__(self, prs):
        self.prs = prs                 # numero -> dict con pr, file, revisioni, commit, eventi
        self.commenti: dict[int, str] = {}

    def pr_unite(self, giorni):
        return sorted((v["pr"] for v in self.prs.values()), key=lambda p: p["merged_at"])

    def pr(self, n): return self.prs[n]["pr"]
    def file(self, n): return self.prs[n]["file"]
    def revisioni(self, n): return self.prs[n].get("revisioni", [])
    def commit(self, n): return self.prs[n].get("commit", [])
    def eventi(self, n): return self.prs[n].get("eventi", [])

    def commenta(self, n, testo, marcatore=R.MARCATORE_COMMENTO):
        self.commenti[n] = testo


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "RTB/documenti/esterni/capitoli").mkdir(parents=True)
        (self.root / "RTB/verbali/interni").mkdir(parents=True)
        self.doc = self.root / "RTB/documenti/esterni/piano-di-progetto.tex"
        self.doc.write_text(DOCUMENTO, encoding="utf-8")
        (self.root / "RTB/documenti/esterni/capitoli/rischi.tex").write_text("Rischi\n")
        self.verbale = self.root / "RTB/verbali/interni/VI-2026-11-03.tex"
        self.verbale.write_text(VERBALE, encoding="utf-8")
        (self.root / "RTB/verbali/interni/VI-2026-11-10.tex").write_text(
            VERBALE.replace("2026-11-03", "2026-11-10"), encoding="utf-8")
        toml = self.root / "pianificazione.toml"
        toml.write_text(TOML, encoding="utf-8")
        self.gruppo = R.carica_gruppo(toml) if R.tomllib else None

    def tearDown(self):
        self.tmp.cleanup()


class TestVersioni(unittest.TestCase):
    def test_versione_successiva(self):
        self.assertEqual(R.versione_successiva("0.2.0", "correzione"), "0.2.1")
        self.assertEqual(R.versione_successiva("0.2.1", "contenuto"), "0.3.0")
        self.assertEqual(R.versione_successiva("0.4.2", "approvazione"), "1.0.0")
        self.assertEqual(R.versione_successiva("1.0.3", "approvazione"), "2.0.0")
        self.assertEqual(R.versione_successiva("", "contenuto"), "0.1.0")
        self.assertEqual(R.versione_successiva("", "approvazione"), "1.0.0")

    def test_etichetta_piu_forte(self):
        self.assertEqual(R.etichetta_della_pr(["documentazione", "correzione"]), "correzione")
        self.assertEqual(R.etichetta_della_pr(["Contenuto", "correzione"]), "contenuto")
        self.assertEqual(R.etichetta_della_pr(["contenuto", "approvazione"]), "approvazione")
        self.assertIsNone(R.etichetta_della_pr(["documentazione"]))
        self.assertIsNone(R.etichetta_della_pr([]))

    def test_descrizione(self):
        corpo = "## Registro\n<!-- Descrizione: esempio da non usare -->\nDescrizione: Stesura della sezione 3, Rischi & mitigazioni.\n"
        self.assertEqual(R.descrizione_della_pr(corpo, "titolo"),
                         r"Stesura della sezione 3, Rischi \& mitigazioni")
        self.assertEqual(R.descrizione_della_pr("Descrizione:   \n", "Titolo_PR"), r"Titolo\_PR")
        self.assertEqual(R.descrizione_della_pr(None, "Usa `100%` dei casi"), r"Usa 100\% dei casi")


class TestMigrazione(Base):
    def test_sposta_le_righe_e_lascia_il_corpo(self):
        prima = R.righe_documento(self.doc)
        self.assertTrue(R.migra(self.doc))
        dopo = R.righe_documento(self.doc)
        self.assertEqual([r.latex() for r in prima], [r.latex() for r in dopo])
        testo = self.doc.read_text()
        self.assertNotIn("Sintassi", testo)                 # vecchio commento tolto
        self.assertIn("piano-di-progetto.registro.tex", testo)
        self.assertIn(r"\modifica{9.9.9}", testo)           # il corpo resta com'è
        self.assertEqual(R.leggi_righe(testo), [])          # nel preambolo non c'è più nulla
        self.assertFalse(R.migra(self.doc))                 # seconda volta: niente da fare

    def test_righe_a_mano_dopo_la_migrazione(self):
        R.migra(self.doc)
        testo = self.doc.read_text().replace(
            r"\begin{document}", "\\modifica{0.2.1}{2026-11-07}{biasini}{corro}{Refuso}\n\\begin{document}", 1)
        self.doc.write_text(testo)
        self.assertEqual(R.righe_documento(self.doc)[0].versione, "0.2.1")
        R.migra(self.doc)
        self.assertEqual([r.versione for r in R.righe_documento(self.doc)], ["0.2.1", "0.2.0", "0.1.0"])
        self.assertEqual(R.leggi_righe(self.doc.read_text()), [])


class TestDocumentiToccati(Base):
    def test_documento_capitolo_e_verbali(self):
        toccati = R.documenti_toccati([
            "RTB/documenti/esterni/capitoli/rischi.tex",     # capitolo -> il documento
            "RTB/verbali/interni/VI-2026-11-03.tex",          # verbale diretto
            "RTB/verbali/interni/immagine.png",               # cartella con più documenti: ambiguo
            "RTB/documenti/esterni/piano-di-progetto.pdf",    # PDF: ignorato
            "scripts/build.py",                               # fuori dalle milestone
        ], self.root)
        self.assertEqual(toccati, [self.doc, self.verbale])


@unittest.skipIf(R.tomllib is None, "il bot legge pianificazione.toml: serve Python 3.11+ (o tomli)")
class TestProposte(Base):
    def proponi(self, dati, **kw):
        return R.proponi(dati["pr"], dati["file"], dati.get("revisioni", []), dati.get("commit", []),
                         dati.get("eventi", []), self.gruppo, self.root, **kw)

    def test_senza_etichetta_nessuna_riga(self):
        self.assertEqual(self.proponi({"pr": pr(1, []), "file": ["RTB/verbali/interni/VI-2026-11-03.tex"]}), [])

    def test_contenuto(self):
        dati = {"pr": pr(5, ["contenuto"], corpo="Descrizione: Stesura della sezione 3"),
                "file": ["RTB/documenti/esterni/capitoli/rischi.tex"],
                "revisioni": [revisione("alec0r", "CHANGES_REQUESTED"), revisione("alec0r", "APPROVED"),
                              revisione("enricobiasini", "COMMENTED")],
                "commit": [{"author": {"login": "firestone109"}, "commit": {"message": "x"}},
                           {"author": {"login": "gaexxx"},
                            "commit": {"message": "y\n\nCo-authored-by: Enrico <123+enricobiasini@users.noreply.github.com>"}},
                           {"author": {"login": "github-actions[bot]"}, "commit": {"message": "z"}}]}
        [p] = self.proponi(dati)
        r = p.riga
        self.assertEqual((r.versione, r.data, r.autore, r.verificatore, r.descrizione, r.approvatore, r.pr),
                         ("0.3.0", "2026-11-10", "guglielmo, spagnoli, biasini", "corro",
                          "Stesura della sezione 3", "", 5))
        self.assertEqual(p.problemi, [])
        self.assertEqual(r.latex(), r"\modifica{0.3.0}{2026-11-10}{guglielmo, spagnoli, biasini}{corro}"
                                    r"{Stesura della sezione 3}% PR #5")

    def test_verificatore_che_ha_anche_scritto_non_e_autore(self):
        dati = {"pr": pr(6, ["correzione"]), "file": ["RTB/documenti/esterni/piano-di-progetto.tex"],
                "revisioni": [revisione("alec0r", "APPROVED")],
                "commit": [{"author": {"login": "alec0r"}, "commit": {"message": "fix"}}]}
        [p] = self.proponi(dati)
        self.assertEqual((p.riga.versione, p.riga.autore, p.riga.verificatore), ("0.2.1", "guglielmo", "corro"))

    def test_senza_approvazione_verificatore_vuoto(self):
        dati = {"pr": pr(7, ["correzione"]), "file": ["RTB/documenti/esterni/piano-di-progetto.tex"],
                "revisioni": [revisione("alec0r", "APPROVED"), revisione("alec0r", "DISMISSED")]}
        [p] = self.proponi(dati)
        self.assertEqual(p.riga.verificatore, "--")
        self.assertTrue(any("nessun membro ha approvato" in x for x in p.problemi))

    def test_approvazione_del_responsabile(self):
        dati = {"pr": pr(8, ["approvazione"]), "file": ["RTB/documenti/esterni/piano-di-progetto.tex"],
                "revisioni": [revisione("alec0r", "APPROVED")], "eventi": [etichettata("gaexxx")]}
        [p] = self.proponi(dati)
        self.assertEqual((p.riga.versione, p.riga.approvatore), ("1.0.0", "spagnoli"))
        self.assertTrue(p.riga.latex().endswith("[spagnoli]% PR #8"))

    def test_approvazione_di_chi_non_e_responsabile(self):
        dati = {"pr": pr(9, ["approvazione"]), "file": ["RTB/documenti/esterni/piano-di-progetto.tex"],
                "revisioni": [revisione("alec0r", "APPROVED")],
                "eventi": [etichettata("gaexxx"), etichettata("firestone109")]}   # vale l'ultima
        [p] = self.proponi(dati)
        self.assertIsNone(p.riga)
        self.assertTrue(any("Responsabile" in x for x in p.problemi))

    def test_approvazione_del_verbale_senza_approvatore(self):
        dati = {"pr": pr(10, ["approvazione"]), "file": ["RTB/verbali/interni/VI-2026-11-03.tex"],
                "revisioni": [revisione("alec0r", "APPROVED")], "eventi": [etichettata("firestone109")]}
        [p] = self.proponi(dati)
        self.assertEqual((p.riga.versione, p.riga.approvatore), ("1.0.0", ""))

    def test_etichetta_messa_dopo_il_merge_usa_quella_data(self):
        dati = {"pr": pr(11, ["approvazione"]), "file": ["RTB/documenti/esterni/piano-di-progetto.tex"],
                "revisioni": [revisione("alec0r", "APPROVED")],
                "eventi": [etichettata("gaexxx", quando="2026-11-12T09:00:00Z")]}
        [p] = self.proponi(dati)
        self.assertEqual(p.riga.data, "2026-11-12")

    def test_documento_nuovo(self):
        nuovo = self.root / "RTB/documenti/esterni/adr/analisi.tex"
        nuovo.parent.mkdir(parents=True)
        nuovo.write_text("\\documentclass[documento]{gpt}\n\\begin{document}\n\\end{document}\n")
        dati = {"pr": pr(12, ["contenuto"], titolo="Prima stesura dell'Analisi"),
                "file": ["RTB/documenti/esterni/adr/analisi.tex"], "revisioni": [revisione("alec0r", "APPROVED")]}
        [p] = self.proponi(dati)
        self.assertEqual((p.riga.versione, p.riga.descrizione), ("0.1.0", "Prima stesura dell'Analisi"))

    def test_autore_sconosciuto(self):
        dati = {"pr": pr(13, ["correzione"], autore="sconosciuto"),
                "file": ["RTB/documenti/esterni/piano-di-progetto.tex"], "revisioni": [revisione("alec0r", "APPROVED")]}
        [p] = self.proponi(dati)
        self.assertEqual(p.riga.autore, "--")
        self.assertTrue(any("sconosciuto" in x for x in p.problemi))


@unittest.skipIf(R.tomllib is None, "il bot legge pianificazione.toml: serve Python 3.11+ (o tomli)")
class TestAggiorna(Base):
    def setUp(self):
        super().setUp()
        for cmd in (["init", "-q", "-b", "main"], ["add", "-A"],
                    ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "inizio"]):
            subprocess.run(["git", *cmd], cwd=self.root, check=True)
        self.gh = FintoGitHub({
            20: {"pr": pr(20, [], unita="2026-11-09T10:00:00Z"),        # senza etichetta: niente
                 "file": ["RTB/documenti/esterni/piano-di-progetto.tex"]},
            21: {"pr": pr(21, ["contenuto"], corpo="Descrizione: Stesura dei rischi",
                          unita="2026-11-10T10:00:00Z"),
                 "file": ["RTB/documenti/esterni/capitoli/rischi.tex", "RTB/verbali/interni/VI-2026-11-03.tex"],
                 "revisioni": [revisione("alec0r", "APPROVED")]},
            22: {"pr": pr(22, ["correzione"], titolo="Refuso nei rischi", unita="2026-11-10T12:00:00Z"),
                 "file": ["RTB/documenti/esterni/piano-di-progetto.tex"],
                 "revisioni": [revisione("enricobiasini", "APPROVED")]},
        })
        os.environ.pop("GITHUB_STEP_SUMMARY", None)

    def git(self, *a):
        return subprocess.run(["git", *a], cwd=self.root, capture_output=True, text=True, check=True).stdout

    def test_aggiorna_e_non_ripete(self):
        R.comando_aggiorna(self.gh, self.gruppo, self.root)
        righe = R.righe_documento(self.doc)
        self.assertEqual([(r.versione, r.pr) for r in righe][:3], [("0.3.1", 22), ("0.3.0", 21), ("0.2.0", None)])
        self.assertEqual(R.righe_documento(self.verbale)[0].versione, "0.2.0")
        self.assertEqual(R.leggi_righe(self.doc.read_text()), [])          # spostate dal .tex
        self.assertIn("[skip ci]", self.git("log", "-1", "--format=%s"))
        self.assertEqual(self.git("status", "--porcelain"), "")              # tutto nel commit
        self.assertIn("0.3.0", self.gh.commenti[21])
        commit_prima = self.git("rev-parse", "HEAD")
        R.comando_aggiorna(self.gh, self.gruppo, self.root)                 # seconda esecuzione
        self.assertEqual(self.git("rev-parse", "HEAD"), commit_prima)
        self.assertEqual(len(R.righe_documento(self.doc)), 4)

    def test_la_riga_compila_come_prima(self):
        """La classe legge le righe nello stesso ordine di build.py."""
        R.comando_aggiorna(self.gh, self.gruppo, self.root)
        import build
        build.ROOT = self.root
        d = build.leggi(self.doc)
        self.assertEqual((d.versione, d.data), ("0.3.1", "2026-11-10"))
        self.assertFalse(any("a mano" in a for a in d.registro))


if __name__ == "__main__":
    unittest.main(verbosity=2)
