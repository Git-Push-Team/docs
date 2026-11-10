#!/usr/bin/env python3
"""Test dell'analisi dei testi:  python3 scripts/test_analisi_testo.py"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analisi_testo as A  # noqa: E402

DOCUMENTO = r"""\documentclass[documento]{gpt}
\titolo{Prova}   % nel preambolo: non si legge
\begin{document}
\section{Introduzione}\label{sec:intro}
Questo è il testo principale, con un termine \glo[Pull request]{pull request}
e una parola \textit{straniera} e del codice \texttt{scripts/build.py}.
% un commento con erori che non conta
Vedi la sezione~\ref{sec:intro}.\footnote{Una nota a piè di pagina.}
La formula $a+b$ resta fuori.

\begin{tikzpicture}
  \node {disegno da saltare};
\end{tikzpicture}

\begin{tabular}{@{}ll@{}}
  Cella uno & Cella due \\
\end{tabular}

\begin{azioni}
  \azione[\#3]{Scrivere il capitolo}{corro, biasini}{19/10/2026}
\end{azioni}
\figura[0.5]{immagini/schema.png}{Una didascalia}
\input{capitoli/capitolo}
\end{document}
"""

CAPITOLO = r"""\subsection{Capitolo}
Prima riga del capitolo.
Seconda riga con erori.
"""


def scrivi_documento(cartella: Path) -> Path:
    (cartella / "capitoli").mkdir()
    (cartella / "capitoli" / "capitolo.tex").write_text(CAPITOLO, encoding="utf-8")
    doc = cartella / "prova.tex"
    doc.write_text(DOCUMENTO, encoding="utf-8")
    return doc


def testo_da(corpo: str) -> A.Testo:
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "x.tex"
        p.write_text("\\documentclass{gpt}\n\\begin{document}\n" + corpo + "\n\\end{document}\n",
                     encoding="utf-8")
        return A.estrai(p, {"corro": "Alessio Corrò"})


class Estrazione(unittest.TestCase):
    def setUp(self):
        self.cartella = tempfile.TemporaryDirectory()
        self.doc = scrivi_documento(Path(self.cartella.name))
        self.t = A.estrai(self.doc, {"corro": "Alessio Corrò", "biasini": "Enrico Biasini"})

    def tearDown(self):
        self.cartella.cleanup()

    def test_testo(self):
        t = self.t.testo
        self.assertIn("Questo è il testo principale, con un termine pull request", t)
        self.assertIn("Vedi la sezione 1.", t)
        self.assertIn("La formula 1 resta fuori.", t)
        self.assertIn("Una nota a piè di pagina.", t)
        self.assertIn("Alessio Corrò, Enrico Biasini", t)
        self.assertIn("Seconda riga con erori.", t)
        for assente in ("Prova", "commento", "disegno", "build.py", "schema.png", "sec:intro", "#3"):
            self.assertNotIn(assente, t)
        # celle e voci sono blocchi separati
        self.assertIn("\n\nCella uno\n\nCella due\n\n", t)

    def test_righe(self):
        t = self.t.testo
        self.assertEqual(self.t.dove(t.index("termine")), (self.doc.as_posix(), 5))
        file, riga = self.t.dove(t.index("erori"))
        self.assertTrue(file.endswith("capitoli/capitolo.tex"))
        self.assertEqual(riga, 3)

    def test_zone(self):
        t = self.t.testo
        self.assertTrue(self.t.in_zona("termine", t.index("pull request")))
        self.assertTrue(self.t.in_zona("corsivo", t.index("straniera")))
        self.assertTrue(self.t.in_zona("titolo", t.index("Introduzione")))
        self.assertTrue(self.t.in_zona("titolo", t.index("Una didascalia")))
        self.assertTrue(self.t.in_zona("codice", t.index("codice.")))
        self.assertIn("straniera", self.t.corsivo)
        self.assertEqual([s for _, s in self.t.sezioni], ["Introduzione"])

    def test_accenti_e_simboli(self):
        t = testo_da(r"Perch\'e no? Costa 10\,\texteuro{} e il 50\% -- circa. ``Bene''.")
        self.assertIn("Perché no? Costa 10 € e il 50% – circa. “Bene”.", t.testo)


def regole(corpo: str) -> list[str]:
    return [p.regola for p in A.controlli_tipografici(testo_da(corpo))]


class ControlliTipografici(unittest.TestCase):
    def test_errori(self):
        casi = {
            "E' importante.": "E_APOSTROFO",
            "Questo e' vero.": "E_APOSTROFO",
            "Lo facciamo perchè serve.": "ACCENTO_CHE",
            "Non serve nè questo.": "ACCENTO_NE_SE",
            "Sono ventitrè persone.": "ACCENTO_TRE",
            "Serve un pò di tempo.": "PO",
            "Qual'è il punto?": "QUAL_E",
            "Serve un'altro incontro.": "UN_APOSTROFO",
            "Il gruppo stà lavorando.": "ACCENTO_MONOSILLABI",
            "Abbiamo finito , poi altro.": "SPAZIO_PRIMA_PUNTEGGIATURA",
            "Abbiamo finito,poi altro.": "SPAZIO_DOPO_PUNTEGGIATURA",
            "Una nota ( questa ) qui.": "SPAZIO_PARENTESI",
            'Il file "docs" va bene.': "VIRGOLETTE_DRITTE",
            "Il gruppo - tutto - concorda.": "TRATTINO",
            "E poi... basta.": "PUNTINI",
            "La riunione di Lunedì scorso.": "MESI_GIORNI_MAIUSCOLI",
            "Entro il 23/03/2027 si consegna.": "DATA_NUMERICA",
            "Aprire le issues su GitHub.": "PLURALE_INGLESE",
            "Ne abbiamo parlato con il il gruppo.": "PAROLA_RIPETUTA",
        }
        for frase, regola in casi.items():
            with self.subTest(frase=frase):
                self.assertEqual(set(regole(frase)), {regola})

    def test_niente_falsi_allarmi(self):
        corretto = ("È vero: perché un po' di tempo serve. Qual è il punto? Un altro incontro e "
                    "un'altra idea, un'auto. Né questo né quello. Il 12 ottobre 2026, lunedì, "
                    "abbiamo aperto le issue e le pull request (versione 1.0.10, ore 21:30). "
                    "Il budget è di 13.000 €. Vedi ``qui'' -- e \\dots{} poi. "
                    "Usiamo GitHub Actions, Microsoft Teams e attività in \\textit{In Progress}. "
                    "Pian piano, via via. Si veda es. il punto 3. Fine.")
        self.assertEqual(regole(corretto), [])

    def test_titoli_e_scadenze_esclusi(self):
        self.assertEqual(regole(r"\section{Riunione di Lunedì}" "\nTesto."), [])
        self.assertEqual(regole(r"\begin{azioni}\azione{Fare}{corro}{19/10/2026}\end{azioni}"), [])

    def test_suggerimenti(self):
        p = A.controlli_tipografici(testo_da("Serve un pò di tempo, perchè sì, e le repositories."))
        self.assertEqual({x.regola: x.suggerimento for x in p},
                         {"PO": "po'", "ACCENTO_CHE": "perché", "PLURALE_INGLESE": "repository"})


class Gulpease(unittest.TestCase):
    def test_formula(self):
        t = testo_da("Il gruppo lavora bene. Il lavoro procede con ordine e con calma.")
        f = A.frasi(t)
        self.assertEqual(len(f), 2)
        parole = 4 + 8
        lettere = len("Ilgruppolavorabene") + len("Illavoroprocedeconordineeconcalma")
        self.assertAlmostEqual(A.gulpease(f), 89 + (300 * 2 - 10 * lettere) / parole)

    def test_abbreviazioni_e_numeri(self):
        t = testo_da("Si veda es. il punto 3. Il valore 1.5 conta. Lo dice F. Guglielmo. Fine.")
        self.assertEqual(len(A.frasi(t)), 4)

    def test_titoli_e_frammenti_non_contano(self):
        t = testo_da("\\section{Un titolo lungo che non conta per niente qui}\n"
                     "\\begin{tabular}{ll} Sì & No \\\\ \\end{tabular}\nUna frase vera.")
        f = A.frasi(t)
        self.assertEqual([t.testo[x.inizio:x.fine] for x in f], ["Una frase vera."])

    def test_frase_lunga(self):
        t = testo_da(" ".join(["parola"] * 45) + ".")
        l = A.leggibilita(t)
        self.assertEqual(len(l.lunghe), 1)
        self.assertEqual(A.controlli_leggibilita(t, l)[0].regola, "FRASE_LUNGA")

    def test_giudizio(self):
        self.assertIn("difficile", A.giudizio(35, 500))
        self.assertIn("accettabile", A.giudizio(50, 500))
        self.assertIn("facile", A.giudizio(65, 500))
        self.assertIn("breve", A.giudizio(65, 50))


class LanguageTool(unittest.TestCase):
    def test_filtri(self):
        t = testo_da("Uso \\textit{deploy} e \\glo{Backlog} con erori. Lo dice Vardanegaa oggi. "
                     "Il commit va. Errre all'inizio no. Nel 2026abc niente. Con ChatGPT.")
        s = t.testo
        risultati = []
        for parola, inglese in [("deploy", False), ("Backlog", False), ("erori", False),
                                ("Vardanegaa", False), ("commit", True), ("Errre", False),
                                ("2026abc", False), ("ChatGPT", False)]:
            a = s.index(parola)
            risultati.append((a, a + len(parola), "MORFOLOGIK_RULE_IT_IT", "TYPOS", inglese,
                              "Trovato un probabile errore di battitura.", "errori|eroi"))
        a = s.index("Il commit")
        risultati.append((a, a + 2, "REGOLA_GRAMMATICA", "GRAMMAR", False, "Concordanza.", ""))
        trovati = A.problemi_languagetool(t, risultati, set())
        self.assertEqual(sorted(p.estratto for p in trovati), ["Errre", "Il", "erori"])
        erori = next(p for p in trovati if p.estratto == "erori")
        self.assertEqual((erori.categoria, erori.suggerimento), ("Ortografia", "errori / eroi"))
        self.assertEqual(next(p for p in trovati if p.estratto == "Il").categoria, "Grammatica")
        # parole da ignorare (parole.txt, nomi, Glossario)
        self.assertEqual(len(A.problemi_languagetool(t, risultati[2:3], {"erori"})), 0)

    def test_senza_jar(self):
        risultati, nota = A.esegui_languagetool([testo_da("Testo.")], Path("/non/esiste.jar"))
        self.assertEqual(risultati, [[]])
        self.assertTrue(nota)

    def test_posizioni_utf16(self):
        t = testo_da("Emoji 😀 poi erori qui.")
        s = t.testo
        a16 = s.index("erori") + 1                  # l'emoji vale 2 unità in Java
        p = A.problemi_languagetool(t, [(a16, a16 + 5, "X", "TYPOS", False, "m", "")], set())
        self.assertEqual(p[0].estratto, "erori")


class Resoconto(unittest.TestCase):
    def test_pr(self):
        with tempfile.TemporaryDirectory() as d:
            doc = scrivi_documento(Path(d))
            t = A.estrai(doc, {})
            nome = doc.as_posix()
            problemi = [A.Problema(nome, 5, "Ortografia", "Errore.", "x", "y", "R",
                                   "prima \x01x\x02 dopo"),
                        A.Problema(nome, 9, "Tipografia", "Altro.", " ,", ",", "SPAZIO_PRIMA",
                                   "fine\x01 ,\x02 poi")]
            analisi = A.Analisi.__new__(A.Analisi)
            analisi.documento, analisi.leggibilita, analisi.problemi = doc, A.leggibilita(t), problemi
            A.Analisi.nome = property(lambda self: self.documento.as_posix())
            md = A.resoconto([analisi], "", {nome: {5}})
            self.assertIn("Nelle righe cambiate da questa PR", md)
            self.assertIn("prima <b>x</b> dopo", md)
            self.assertIn("fine<b>␣,</b> poi", md)
            self.assertIn("Nel resto del documento: 1", md)
            ann = A.annotazioni([analisi], {nome: {5}})
            self.assertEqual(len(ann), 1)
            self.assertTrue(ann[0].startswith(f"::notice file={nome},line=5,title=Ortografia::"))


class RigheCambiate(unittest.TestCase):
    def test_diff(self):
        with tempfile.TemporaryDirectory() as d:
            def git(*a):
                subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=d,
                               check=True, capture_output=True)
            git("init", "-q", "-b", "main")
            f = Path(d) / "Verbale con spazi è.tex"
            f.write_text("a\nb\nc\nd\n", encoding="utf-8")
            git("add", ".")
            git("commit", "-qm", "base")
            git("checkout", "-qb", "pr")
            f.write_text("a\nB\nc\nd\ne\n", encoding="utf-8")
            git("commit", "-qam", "pr")
            vecchio = A.ROOT
            A.ROOT = Path(d)
            try:
                self.assertEqual(A.righe_cambiate("main"), {"Verbale con spazi è.tex": {2, 5}})
            finally:
                A.ROOT = vecchio


class Documenti(unittest.TestCase):
    def test_tutti_analizzabili(self):
        """Ogni documento vero si estrae e ha un indice (nessuna eccezione)."""
        for d in A.tutti_i_documenti():
            with self.subTest(documento=d.name):
                l = A.leggibilita(A.estrai(d))
                self.assertIsNotNone(l.indice)


if __name__ == "__main__":
    unittest.main(verbosity=1)
