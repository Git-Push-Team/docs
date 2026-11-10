#!/usr/bin/env python3
"""
analisi_testo.py -- controlla come sono scritti i documenti: ortografia,
grammatica, tipografia e leggibilità (indice Gulpease).

NON blocca niente: segnala e basta. Nelle pull request lo lancia il
workflow "Analisi dei testi" e il risultato arriva come commento
(🔎 Analisi dei testi); ad ogni merge su main analizza tutti i documenti
e mette il riepilogo nella pagina dell'Action.

Uso a mano (dalla cartella del repository):
    python3 scripts/analisi_testo.py                     tutti i documenti
    python3 scripts/analisi_testo.py RTB/documenti/esterni/piano-di-progetto.tex
    python3 scripts/analisi_testo.py --pr origin/main    solo i documenti cambiati
    python3 scripts/analisi_testo.py --solo-gulpease     solo l'indice, in un attimo
    python3 scripts/analisi_testo.py --scarica-lt        scarica LanguageTool (una volta)

Cosa controlla:
  - ortografia e grammatica con LanguageTool (serve Java e il file
    .cache/textidote.jar, che contiene LanguageTool: se manca, questi due
    controlli si saltano e gli altri si fanno lo stesso);
  - tipografia ed errori tipici dell'italiano scritto: E' al posto di È,
    perchè, un pò, qual'è, parole ripetute, spazi prima della punteggiatura,
    virgolette dritte, trattini, nomi di mesi e giorni con la maiuscola,
    plurali inglesi (le issues -> le issue)...;
  - leggibilità: indice Gulpease di ogni documento e delle sue sezioni, e
    frasi troppo lunghe.

Parole da non segnalare come errori (nomi, sigle, termini del progetto):
scripts/analisi/parole.txt, una per riga. Non serve aggiungere le voci del
Glossario, i nomi del gruppo, le parole inglesi e quelle in corsivo: quelle
si ignorano da sole.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import registro  # noqa: E402  (documenti toccati da una PR)

MILESTONE = ("Candidatura", "RTB", "PB")

# --- Soglie --------------------------------------------------------------
# Indice Gulpease (0-100, più alto = più facile). Per chi ha un diploma un
# testo sotto 40 è difficile, sopra 60 è facile. Se il Piano di Qualifica
# fissa soglie diverse, cambiatele qui.
GULPEASE_ACCETTABILE = 40
GULPEASE_OTTIMO = 60
PAROLE_MINIME = 100          # sotto, l'indice di un testo non è affidabile
FRASE_LUNGA = 40             # parole oltre le quali una frase si segnala

# --- LanguageTool --------------------------------------------------------
LT_URL = "https://github.com/sylvainhalle/textidote/releases/download/v0.8.3/textidote.jar"
LT_SHA256 = "04862cc03ad5a8d101f89f53c01d05a29f800bcaaf3e8e7728653b8aea42eed9"
LT_JAR = ROOT / ".cache" / "textidote.jar"
LT_JAVA = Path(__file__).resolve().parent / "analisi" / "ControllaItaliano.java"
PAROLE = Path(__file__).resolve().parent / "analisi" / "parole.txt"
# Regole di LanguageTool spente: dopo l'estrazione dal LaTeX darebbero solo
# falsi allarmi (spazi, elenchi che iniziano in minuscolo) o doppioni dei
# controlli fatti qui.
LT_SPENTE = ["WHITESPACE_RULE", "UPPERCASE_SENTENCE_START", "ITALIAN_WORD_REPEAT_RULE",
             "COMMA_PARENTHESIS_WHITESPACE", "DOUBLE_PUNCTUATION"]
LT_ORTOGRAFIA = "TYPOS"
# Categorie di LanguageTool (le CATn sono quelle delle regole italiane);
# quelle non elencate valgono "Grammatica".
CATEGORIE_LT = {"TYPOS": "Ortografia", "GRAMMAR": "Grammatica",
                "PUNCTUATION": "Punteggiatura", "TYPOGRAPHY": "Tipografia",
                "CASING": "Maiuscole", "CONFUSED_WORDS": "Grammatica",
                "REDUNDANCY": "Stile", "STYLE": "Stile", "SEMANTICS": "Coerenza",
                "CAT6": "Punteggiatura", "CAT8": "Stile", "CAT9": "Stile", "CAT10": "Stile",
                "CAT11": "Stile", "CAT12": "Ortografia", "CAT13": "Ortografia"}

MARCATORE = "analisi-testo"
MAX_PER_DOCUMENTO = 60       # problemi elencati per documento nel commento
MAX_COMMENTO = 60000         # GitHub accetta commenti fino a 65536 caratteri
MAX_ANNOTAZIONI = 10         # GitHub ne mostra al massimo 10 per passo


# ==========================================================================
#  1. Dal LaTeX al testo, ricordando da quale riga viene ogni carattere
# ==========================================================================
@dataclass
class Sorgente:
    percorso: Path
    testo: str                      # con i commenti sostituiti da spazi
    inizi: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.inizi = [0] + [m.end() for m in re.finditer(r"\n", self.testo)]

    def riga(self, pos: int) -> int:
        return bisect.bisect_right(self.inizi, pos)

    @property
    def nome(self) -> str:
        try:
            return self.percorso.relative_to(ROOT).as_posix()
        except ValueError:
            return self.percorso.as_posix()


def maschera_commenti(testo: str) -> str:
    """I commenti (% fino a fine riga) diventano spazi: le posizioni restano."""
    out = list(testo)
    i, n = 0, len(testo)
    while i < n:
        c = testo[i]
        if c == "\\":
            i += 2
            continue
        if c == "%":
            j = testo.find("\n", i)
            j = n if j < 0 else j
            out[i:j] = " " * (j - i)
            i = j
            continue
        i += 1
    return "".join(out)


# Comandi che stampano il loro argomento nel testo, così com'è.
IN_LINEA = {"textbf", "textit", "emph", "textsl", "textsc", "textsf", "textrm",
            "textup", "textmd", "textnormal", "underline", "uline", "mbox", "text",
            "textsuperscript", "textsubscript", "hbox", "enquote", "ped", "apice"}
CORSIVO = {"textit", "emph", "textsl"}
# Titoli: si controllano ma non contano per la leggibilità.
TITOLI = {"part", "chapter", "section", "subsection", "subsubsection", "paragraph",
          "subparagraph", "subsubsubsection", "letteraglossario", "caption",
          "intestazione", "title", "frametitle"}
# Riferimenti: diventano una parola segnaposto (così "vedi \ref{x}." resta una frase).
SEGNAPOSTO = {"ref": "1", "pageref": "1", "autoref": "sezione 1", "cref": "sezione 1",
              "Cref": "Sezione 1", "eqref": "(1)", "cite": "[1]", "nameref": "titolo",
              "url": "link", "nolinkurl": "link", "texttt": "codice", "verb": "codice",
              "path": "codice"}
# Simboli senza argomenti.
SIMBOLI = {"texteuro": "€", "euro": "€", "LaTeX": "LaTeX", "TeX": "TeX", "LaTeXe": "LaTeX",
           "ldots": "…", "dots": "…", "textellipsis": "…", "S": "§", "P": "¶",
           "textbackslash": "\\", "textendash": "–", "textemdash": "—",
           "textquoteright": "’", "textquoteleft": "‘", "textasciitilde": "~",
           "textdegree": "°", "copyright": "©", "textregistered": "®",
           "texttrademark": "™", "today": "oggi", "guillemotleft": "«",
           "guillemotright": "»", "textless": "<", "textgreater": ">", "textbar": "|",
           "i": "i", "ss": "ß", "&": "&", "textunderscore": "_", "textpercent": "%"}
# Comandi da saltare con i loro argomenti obbligatori (numero tra parentesi).
SALTA = {"label": 1, "includegraphics": 1, "vspace": 1,
         "hspace": 1, "addvspace": 1, "vskip": 0, "setlength": 2, "addtolength": 2,
         "setcounter": 2, "addtocounter": 2, "stepcounter": 1, "refstepcounter": 1,
         "color": 1, "rowcolor": 1, "cellcolor": 1, "rule": 2, "addcontentsline": 3,
         "newcommand": 2, "renewcommand": 2, "providecommand": 2, "DeclareRobustCommand": 2,
         "newenvironment": 3, "renewenvironment": 3, "def": 0, "pagestyle": 1,
         "thispagestyle": 1, "bibliography": 1, "bibliographystyle": 1, "cline": 1,
         "cmidrule": 1, "hypersetup": 1, "graphicspath": 1, "usetikzlibrary": 1,
         "tikzset": 1, "pgfplotsset": 1, "definecolor": 3, "captionsetup": 1,
         "setlist": 1, "linespread": 1, "fontsize": 2, "selectfont": 0,
         "phantomsection": 0, "addlinespace": 0, "arraybackslash": 0}
# Comandi il cui ultimo argomento è testo, gli altri si saltano.
ULTIMO_ARGOMENTO = {"textcolor": 2, "colorbox": 2, "href": 2, "pdfdoc": 2,
                    "hyperlink": 2, "hypertarget": 2, "resizebox": 3, "scalebox": 2,
                    "multicolumn": 3, "multirow": 3, "makebox": 1, "parbox": 2,
                    "raisebox": 2, "fbox": 1, "framebox": 1, "hyperref": 1,
                    "foreignlanguage": 2, "textlang": 2}
# Comandi senza argomenti (dichiarazioni, spaziature, filetti...).
DICHIARAZIONI = {"centering", "raggedright", "raggedleft", "noindent", "indent", "small",
                 "footnotesize", "scriptsize", "tiny", "large", "Large", "LARGE", "huge",
                 "Huge", "normalsize", "bfseries", "itshape", "sffamily", "ttfamily",
                 "rmfamily", "mdseries", "upshape", "scshape", "slshape", "em", "bf", "it",
                 "tt", "sf", "rm", "hfill", "vfill", "newpage", "clearpage",
                 "cleardoublepage", "pagebreak", "nopagebreak", "medskip", "smallskip",
                 "bigskip", "par", "leavevmode", "toprule", "midrule", "bottomrule", "hline",
                 "endhead", "endfoot", "endfirsthead", "endlastfoot", "maketitle",
                 "tableofcontents", "listoffigures", "listoftables", "appendix", "protect",
                 "relax", "strut", "null", "nobreak", "frontmatter", "mainmatter",
                 "backmatter", "normalfont", "hrule", "hrulefill", "dotfill", "quad",
                 "qquad", "enspace", "thinspace", "negthinspace", "ignorespaces",
                 "unskip", "allowbreak", "linebreak", "newline", "break", "footnoterule",
                 "noalign", "tabularnewline", "item"}
# Ambienti da saltare per intero.
SALTA_AMBIENTI = {"tikzpicture", "equation", "equation*", "align", "align*", "gather",
                  "gather*", "multline", "multline*", "math", "displaymath", "verbatim",
                  "Verbatim", "lstlisting", "minted", "comment", "forest", "pgfpicture",
                  "circuitikz", "mermaid"}
# Argomenti obbligatori di \begin{ambiente} (specifiche delle colonne...).
ARGOMENTI_AMBIENTE = {"tabular": 1, "tabular*": 2, "tabularx": 2, "tabulary": 2,
                      "longtable": 1, "array": 1, "minipage": 1, "multicols": 1,
                      "wrapfigure": 2, "wraptable": 2, "adjustbox": 1, "xltabular": 2,
                      "tblr": 1, "longtblr": 1}
ACCENTI = {"'": "\u0301", "`": "\u0300", "^": "\u0302", '"': "\u0308", "~": "\u0303",
           "=": "\u0304", ".": "\u0307", "c": "\u0327", "v": "\u030c", "u": "\u0306",
           "H": "\u030b", "r": "\u030a", "k": "\u0328"}


@dataclass
class Testo:
    """Il testo di un documento, pronto da controllare."""
    documento: Path
    sorgenti: list[Sorgente] = field(default_factory=list)
    caratteri: list[str] = field(default_factory=list)
    origine: list[tuple[int, int]] = field(default_factory=list)   # (sorgente, posizione)
    zone: dict[str, list[tuple[int, int]]] = field(default_factory=dict)
    sezioni: list[tuple[int, str]] = field(default_factory=list)   # (inizio, titolo)
    corsivo: set[str] = field(default_factory=set)                  # parole in corsivo
    _testo: str | None = None

    @property
    def testo(self) -> str:
        if self._testo is None or len(self._testo) != len(self.caratteri):
            self._testo = "".join(self.caratteri)
        return self._testo

    def dove(self, pos: int) -> tuple[str, int]:
        pos = min(max(pos, 0), len(self.origine) - 1)
        s, p = self.origine[pos]
        src = self.sorgenti[s]
        return src.nome, src.riga(p)

    def in_zona(self, tipo: str, a: int, b: int | None = None) -> bool:
        b = a + 1 if b is None else b
        return any(x < b and a < y for x, y in self.zone.get(tipo, []))


class Estrattore:
    def __init__(self, documento: Path, nomi: dict[str, str]):
        self.t = Testo(documento=documento)
        self.nomi = nomi
        self.visti: set[Path] = set()
        self.note: list[tuple[int, int, int]] = []     # note a piè di pagina, in fondo
        self.eventi: dict[int, tuple[list[int], list[int]]] = {}   # tabelle aperte

    # ---- uscita --------------------------------------------------------
    def emetti(self, testo: str, s: int, pos: int) -> None:
        for c in testo:
            self.t.caratteri.append(c)
            self.t.origine.append((s, pos))

    def spazio(self, s: int, pos: int) -> None:
        if self.t.caratteri and self.t.caratteri[-1] not in " \n":
            self.emetti(" ", s, pos)

    def confine(self, s: int, pos: int) -> None:
        """Fine di un blocco (paragrafo, cella, voce di elenco, titolo)."""
        c, o = self.t.caratteri, self.t.origine
        while c and c[-1] == " ":
            c.pop()
            o.pop()
        if not c:
            return
        while not (len(c) >= 2 and c[-1] == "\n" and c[-2] == "\n"):
            self.emetti("\n", s, pos)

    def zona(self, tipo: str, a: int) -> None:
        b = len(self.t.caratteri)
        if b > a:
            self.t.zone.setdefault(tipo, []).append((a, b))

    # ---- lettura degli argomenti ------------------------------------
    @staticmethod
    def chiusa(t: str, i: int, apre: str, chiude: str, fine: int) -> int:
        """Posizione della parentesi che chiude quella in t[i] (o fine)."""
        livello = 0
        j = i
        while j < fine:
            c = t[j]
            if c == "\\":
                j += 2
                continue
            if c == apre:
                livello += 1
            elif c == chiude:
                livello -= 1
                if livello == 0:
                    return j
            j += 1
        return fine

    @staticmethod
    def salta_spazi(t: str, k: int, fine: int) -> int:
        """Spazi e un solo a capo (una riga vuota chiude gli argomenti)."""
        a_capo = 0
        while k < fine and t[k] in " \t\r\n":
            if t[k] == "\n":
                a_capo += 1
                if a_capo > 1:
                    break
            k += 1
        return k

    def opzionale(self, t: str, k: int, fine: int) -> tuple[tuple[int, int] | None, int]:
        j = self.salta_spazi(t, k, fine)
        if j < fine and t[j] == "[":
            e = self.chiusa(t, j, "[", "]", fine)
            return (j + 1, e), min(e + 1, fine)
        return None, k

    def obbligatorio(self, t: str, k: int, fine: int) -> tuple[tuple[int, int] | None, int]:
        j = self.salta_spazi(t, k, fine)
        if j < fine and t[j] == "{":
            e = self.chiusa(t, j, "{", "}", fine)
            return (j + 1, e), min(e + 1, fine)
        if j < fine and t[j] == "\\":           # \textbf\foo: argomento senza graffe
            m = re.match(r"\\([A-Za-z@]+|.)", t[j:fine])
            if m:
                return (j, j + m.end()), j + m.end()
        if j < fine and t[j] not in "}]":       # \textbf x: un solo carattere
            return (j, j + 1), j + 1
        return None, k

    def opzionali(self, t: str, k: int, fine: int) -> int:
        while True:
            arg, k2 = self.opzionale(t, k, fine)
            if arg is None:
                return k
            k = k2

    # ---- file ------------------------------------------------------------
    def aggiungi_sorgente(self, percorso: Path) -> int:
        testo = percorso.read_text(encoding="utf-8", errors="replace")
        self.t.sorgenti.append(Sorgente(percorso, maschera_commenti(testo)))
        return len(self.t.sorgenti) - 1

    def documento(self) -> Testo:
        p = self.t.documento
        self.visti.add(p.resolve())
        s = self.aggiungi_sorgente(p)
        t = self.t.sorgenti[s].testo
        m = re.search(r"\\begin\s*\{document\}", t)
        inizio = m.end() if m else 0
        m2 = re.search(r"\\end\s*\{document\}", t)
        fine = m2.start() if m2 else len(t)
        self.blocco(s, inizio, fine)
        # le note a piè di pagina in fondo, ognuna un blocco a sé
        while self.note:
            ns, a, b = self.note.pop(0)
            self.confine(ns, a)
            self.blocco(ns, a, b)
        self.confine(s, fine)
        return self.t

    def includi(self, nome: str, s: int, pos: int) -> None:
        nome = nome.strip()
        if not nome:
            return
        candidati = []
        for base in (self.t.documento.parent, self.t.sorgenti[s].percorso.parent):
            p = base / nome
            candidati += [p, p.with_name(p.name + ".tex")]
        for p in candidati:
            if p.is_file() and p.suffix == ".tex":
                if p.resolve() in self.visti:
                    return
                self.visti.add(p.resolve())
                ns = self.aggiungi_sorgente(p)
                self.confine(s, pos)
                self.blocco(ns, 0, len(self.t.sorgenti[ns].testo))
                self.confine(s, pos)
                return

    # ---- il testo ------------------------------------------------------
    def blocco(self, s: int, i: int, fine: int) -> None:
        t = self.t.sorgenti[s].testo
        while i < fine:
            c = t[i]
            if c == "\\":
                i = self.comando(s, i, fine)
            elif c in "{}":
                i += 1
            elif c == "$":
                doppio = t.startswith("$$", i)
                chiude = t.find("$$" if doppio else "$", i + (2 if doppio else 1), fine)
                while chiude > 0 and t[chiude - 1] == "\\":
                    chiude = t.find("$", chiude + 1, fine)
                chiude = fine if chiude < 0 else chiude
                if doppio:
                    self.confine(s, i)
                else:
                    self.emetti("1", s, i)
                i = chiude + (2 if doppio else 1)
            elif c == "~":
                self.spazio(s, i)
                i += 1
            elif c == "&":
                self.confine(s, i)
                i += 1
            elif c == "\n":
                j = i + 1
                while j < fine and t[j] in " \t\r":
                    j += 1
                if j < fine and t[j] == "\n":
                    self.confine(s, i)
                    while j < fine and t[j] in " \t\r\n":
                        j += 1
                    i = j
                else:
                    self.spazio(s, i)
                    i += 1
            elif c in " \t\r":
                self.spazio(s, i)
                i += 1
            elif t.startswith("---", i):
                self.emetti("—", s, i)
                i += 3
            elif t.startswith("--", i):
                self.emetti("–", s, i)
                i += 2
            elif t.startswith("``", i):
                self.emetti("“", s, i)
                i += 2
            elif t.startswith("''", i):
                self.emetti("”", s, i)
                i += 2
            elif c == "`":
                self.emetti("‘", s, i)
                i += 1
            else:
                self.emetti(c, s, i)
                i += 1

    def argomento_come_blocco(self, s: int, arg: tuple[int, int] | None, tipo: str | None = None) -> None:
        if arg is None:
            return
        self.confine(s, arg[0])
        inizio = len(self.t.caratteri)
        self.blocco(s, arg[0], arg[1])
        if tipo:
            self.zona(tipo, inizio)
        self.confine(s, arg[1])

    def argomento_in_linea(self, s: int, arg: tuple[int, int] | None, tipo: str | None = None) -> None:
        if arg is None:
            return
        inizio = len(self.t.caratteri)
        self.blocco(s, arg[0], arg[1])
        if tipo:
            self.zona(tipo, inizio)

    def comando(self, s: int, i: int, fine: int) -> int:
        t = self.t.sorgenti[s].testo
        j = i + 1
        if j >= fine:
            return fine
        if not (t[j].isalpha() or t[j] == "@"):
            return self.simbolo(s, i, fine)
        k = j
        while k < fine and (t[k].isalpha() or t[k] == "@"):
            k += 1
        nome = t[j:k]
        stella = k < fine and t[k] == "*"
        if stella:
            k += 1

        if nome in ("begin", "end"):
            arg, k = self.obbligatorio(t, k, fine)
            amb = t[arg[0]:arg[1]].strip() if arg else ""
            if nome == "end":
                self.confine(s, i)
                return k
            if amb in SALTA_AMBIENTI:
                m = re.compile(r"\\end\s*\{" + re.escape(amb) + r"\}").search(t, k, fine)
                self.confine(s, i)
                return m.end() if m else fine
            self.confine(s, i)
            titolo, k2 = self.opzionale(t, k, fine)
            if titolo and amb in ("nota", "tcolorbox", "scheda"):
                self.argomento_come_blocco(s, titolo, "titolo")
            k = self.opzionali(t, k2 if titolo else k, fine)
            for _ in range(ARGOMENTI_AMBIENTE.get(amb, 0)):
                k = self.opzionali(t, k, fine)
                _, k = self.obbligatorio(t, k, fine)
            return k

        if nome == "item":
            self.confine(s, i)
            etichetta, k = self.opzionale(t, k, fine)
            if etichetta:
                self.argomento_in_linea(s, etichetta)
                self.spazio(s, k)
            return k

        if nome in TITOLI:
            k = self.opzionali(t, k, fine)
            arg, k = self.obbligatorio(t, k, fine)
            inizio = len(self.t.caratteri)
            self.argomento_come_blocco(s, arg, "titolo")
            if nome in ("section", "chapter") and arg:
                titolo = "".join(self.t.caratteri[inizio:])
                self.t.sezioni.append((inizio, re.sub(r"\s+", " ", titolo).strip()))
            return k

        if nome == "termine":                    # voce del Glossario
            voce, k = self.obbligatorio(t, k, fine)
            definizione, k = self.obbligatorio(t, k, fine)
            self.argomento_come_blocco(s, voce, "titolo")
            self.argomento_come_blocco(s, definizione)
            return k

        if nome in ("figura", "figurasenzabordo"):   # \figura[larghezza]{file}{didascalia}
            k = self.opzionali(t, k, fine)
            _, k = self.obbligatorio(t, k, fine)
            didascalia, k = self.obbligatorio(t, k, fine)
            self.argomento_come_blocco(s, didascalia, "titolo")
            return k

        if nome in ("input", "include", "subfile", "import", "InputIfFileExists"):
            arg, k = self.obbligatorio(t, k, fine)
            if nome == "InputIfFileExists":       # \InputIfFileExists{file}{se c'è}{se no}
                _, k = self.obbligatorio(t, k, fine)
                _, k = self.obbligatorio(t, k, fine)
            if arg:
                self.includi(t[arg[0]:arg[1]], s, i)
            return k

        if nome == "footnote":
            k = self.opzionali(t, k, fine)
            arg, k = self.obbligatorio(t, k, fine)
            if arg:
                self.note.append((s, arg[0], arg[1]))
            return k

        if nome == "glo":
            _, k = self.opzionale(t, k, fine)
            arg, k = self.obbligatorio(t, k, fine)
            self.argomento_in_linea(s, arg, "termine")
            return k

        if nome in ("nome", "nomi"):
            arg, k = self.obbligatorio(t, k, fine)
            if arg:
                chiavi = [c.strip() for c in t[arg[0]:arg[1]].split(",") if c.strip()]
                inizio = len(self.t.caratteri)
                self.emetti(", ".join(self.nomi.get(c, c) for c in chiavi), s, arg[0])
                self.zona("nome", inizio)
            return k

        if nome == "azione":                     # \azione[#issue]{attività}{chi}{scadenza}
            _, k = self.opzionale(t, k, fine)
            attivita, k = self.obbligatorio(t, k, fine)
            chi, k = self.obbligatorio(t, k, fine)
            scadenza, k = self.obbligatorio(t, k, fine)
            self.argomento_come_blocco(s, attivita)
            if chi:
                self.confine(s, chi[0])
                inizio = len(self.t.caratteri)
                chiavi = [c.strip() for c in t[chi[0]:chi[1]].split(",") if c.strip()]
                self.emetti(", ".join(self.nomi.get(c, c) for c in chiavi), s, chi[0])
                self.zona("nome", inizio)
                self.confine(s, chi[1])
            self.argomento_come_blocco(s, scadenza, "titolo")
            return k

        if nome in SEGNAPOSTO:
            k = self.opzionali(t, k, fine)
            if nome == "verb" and k < fine:
                delim = t[k]
                e = t.find(delim, k + 1, fine)
                k = fine if e < 0 else e + 1
            else:
                _, k = self.obbligatorio(t, k, fine)
            inizio = len(self.t.caratteri)
            self.emetti(SEGNAPOSTO[nome], s, i)
            self.zona("codice", inizio)
            return k

        if nome in IN_LINEA:
            k = self.opzionali(t, k, fine)
            arg, k = self.obbligatorio(t, k, fine)
            inizio = len(self.t.caratteri)
            if nome == "enquote":
                self.emetti("“", s, i)
            self.argomento_in_linea(s, arg, "corsivo" if nome in CORSIVO else None)
            if nome == "enquote":
                self.emetti("”", s, k - 1)
            if nome in CORSIVO:
                for p in re.findall(r"[^\W\d_]+", "".join(self.t.caratteri[inizio:])):
                    self.t.corsivo.add(p.lower())
            return k

        if nome in SIMBOLI:
            self.emetti(SIMBOLI[nome], s, i)
            if k < fine and t[k] == "{" and k + 1 < fine and t[k + 1] == "}":
                k += 2                           # \LaTeX{}
            return k

        if nome in ULTIMO_ARGOMENTO:
            quanti = ULTIMO_ARGOMENTO[nome]
            ultimo = None
            for _ in range(quanti):
                k = self.opzionali(t, k, fine)
                ultimo, k = self.obbligatorio(t, k, fine)
            self.argomento_in_linea(s, ultimo)
            return k

        if nome in SALTA:
            if nome == "def":                     # \def\nome#1{...}
                m = re.compile(r"\{").search(t, k, fine)
                if m:
                    return min(self.chiusa(t, m.start(), "{", "}", fine) + 1, fine)
                return k
            k = self.opzionali(t, k, fine)
            for _ in range(SALTA[nome]):
                k = self.opzionali(t, k, fine)
                _, k = self.obbligatorio(t, k, fine)
            return k

        if nome in DICHIARAZIONI:
            if nome in ("linebreak", "newline", "tabularnewline"):
                self.confine(s, i) if nome == "tabularnewline" else self.spazio(s, i)
            return self.opzionali(t, k, fine) if nome in ("addlinespace", "linebreak") else k

        # Comando sconosciuto (anche quelli definiti nel documento, come
        # \rischio): si salta il nome e si leggono gli argomenti tra graffe.
        # Uno solo: testo in linea. Più di uno: ognuno è un blocco a sé.
        k = self.opzionali(t, k, fine)
        argomenti = []
        while True:
            j = self.salta_spazi(t, k, fine)
            if j < fine and t[j] == "{":
                e = self.chiusa(t, j, "{", "}", fine)
                argomenti.append((j + 1, e))
                k = min(e + 1, fine)
            else:
                break
        if len(argomenti) == 1:
            self.argomento_in_linea(s, argomenti[0])
        else:
            for a in argomenti:
                self.argomento_come_blocco(s, a)
        return k

    def simbolo(self, s: int, i: int, fine: int) -> int:
        """\\%, \\&, \\\\, \\, , accenti..."""
        t = self.t.sorgenti[s].testo
        c = t[i + 1]
        k = i + 2
        if c in "%&_#${}":
            self.emetti(c, s, i)
        elif c == "\\":
            self.confine(s, i) if self.dentro_tabella(s, i) else self.spazio(s, i)
            if k < fine and t[k] == "*":
                k += 1
            k = self.opzionali(t, k, fine)
        elif c in ",;:! >":
            self.spazio(s, i)
        elif c in ACCENTI and k < fine:
            if t[k] == "{":
                e = self.chiusa(t, k, "{", "}", fine)
                base = t[k + 1:e].strip().lstrip("\\") or " "
                k = e + 1
            else:
                base = t[k]
                k += 1
            self.emetti(unicodedata.normalize("NFC", base[0] + ACCENTI[c]) + base[1:], s, i)
        elif c == "(":
            e = t.find("\\)", k, fine)
            self.emetti("1", s, i)
            k = fine if e < 0 else e + 2
        elif c == "[":
            e = t.find("\\]", k, fine)
            self.confine(s, i)
            k = fine if e < 0 else e + 2
        return k

    TABELLE = re.compile(r"\\(begin|end)\s*\{(tabular\*?|tabularx|tabulary|longtable|"
                         r"array|xltabular|tblr|longtblr|azioni|decisioni)\}")

    def dentro_tabella(self, s: int, i: int) -> bool:
        """Un \\\\ chiude una riga di tabella (un blocco) o va a capo nel testo."""
        t = self.t.sorgenti[s].testo
        if s not in self.eventi:
            posizioni, livelli, livello = [], [], 0
            for m in self.TABELLE.finditer(t):
                livello += 1 if m.group(1) == "begin" else -1
                posizioni.append(m.start())
                livelli.append(livello)
            self.eventi[s] = (posizioni, livelli)
        posizioni, livelli = self.eventi[s]
        n = bisect.bisect_left(posizioni, i)
        return (n > 0 and livelli[n - 1] > 0) or "&" in t[t.rfind("\n", 0, i) + 1:i]


def nomi_del_gruppo() -> dict[str, str]:
    p = ROOT / "template" / "dati-gruppo.tex"
    try:
        testo = maschera_commenti(p.read_text(encoding="utf-8"))
    except OSError:
        return {}
    return {m.group(1).strip(): m.group(2).strip()
            for m in re.finditer(r"\\membro\s*\{([^}]*)\}\s*\{([^}]*)\}", testo)}


def estrai(documento: Path, nomi: dict[str, str] | None = None) -> Testo:
    return Estrattore(documento, nomi if nomi is not None else nomi_del_gruppo()).documento()


# ==========================================================================
#  2. Frasi, parole e indice Gulpease
# ==========================================================================
PAROLA = re.compile(r"[^\W_]+(?:['’][^\W_]+)*")
FINE_FRASE = re.compile(r"[.!?…]+[\"”»’)\]]*(?=\s|$)")
ABBREVIAZIONI = {"es", "cfr", "pag", "pagg", "p", "pp", "n", "nn", "art", "sig", "sigg",
                 "dott", "dr", "prof", "ing", "avv", "geom", "rag", "vs", "ca", "cap",
                 "fig", "figg", "tab", "sez", "e.g", "i.e", "s.r.l", "s.p.a", "s.n.c",
                 "s.a.s", "max", "min", "ver", "v", "vol", "ed", "op", "cit", "ss", "sg",
                 "nr", "tel", "rif", "all", "doc", "c.a", "a.a", "u.c", "spett", "egr",
                 "gent", "c.d", "cd", "ecc", "etc"}


@dataclass
class Frase:
    inizio: int
    fine: int
    parole: int
    lettere: int
    finita: bool           # termina con . ! ? …


def blocchi(testo: Testo) -> list[tuple[int, int]]:
    """I blocchi di prosa: si escludono titoli, intestazioni e didascalie."""
    risultato = []
    for m in re.finditer(r"[^\n]+(?:\n(?!\n)[^\n]+)*", testo.testo):
        a, b = m.start(), m.end()
        if not testo.in_zona("titolo", a, b) or not all(
                testo.in_zona("titolo", x) for x in (a, b - 1)):
            risultato.append((a, b))
    return risultato


def fine_di_frase(testo: str, m: re.Match, limite: int) -> bool:
    if "." not in m.group(0) or m.group(0).startswith(("!", "?", "…")):
        return True
    prima = re.search(r"([^\W\d_](?:[^\W\d_.]|\.(?=[^\W\d_]))*)$",
                      testo[max(0, m.start() - 30):m.start()])
    parola = prima.group(1).lower() if prima else ""
    dopo = re.match(r"\s*(\S)?", testo[m.end():min(limite, m.end() + 10)])
    seguente = dopo.group(1) if dopo else None
    if seguente and seguente.islower():
        return False               # "ecc. e altro", "es. il gruppo"
    if parola in ABBREVIAZIONI and parola not in ("ecc", "etc"):
        return False
    if len(parola) == 1 and parola.isalpha() and prima and prima.group(1).isupper():
        return False               # iniziale di un nome: "F. Guglielmo"
    return True


def frasi(testo: Testo) -> list[Frase]:
    risultato: list[Frase] = []
    t = testo.testo
    for a, b in blocchi(testo):
        inizio = a
        for m in FINE_FRASE.finditer(t, a, b):
            if not fine_di_frase(t, m, b):
                continue
            risultato.append(misura(t, inizio, m.end(), True))
            inizio = m.end()
        if t[inizio:b].strip():
            risultato.append(misura(t, inizio, b, False))
    # via i pezzi vuoti e i frammenti brevi senza punto (celle, voci di una parola)
    return [f for f in risultato if f.parole and (f.finita or f.parole >= 6)]


def misura(t: str, a: int, b: int, finita: bool) -> Frase:
    while a < b and t[a].isspace():
        a += 1
    parole = PAROLA.findall(t, a, b)
    return Frase(a, b, len(parole), sum(len(re.sub(r"['’]", "", p)) for p in parole), finita)


def gulpease(elenco: list[Frase]) -> float | None:
    parole = sum(f.parole for f in elenco)
    if not parole:
        return None
    lettere = sum(f.lettere for f in elenco)
    return min(100.0, max(0.0, 89 + (300 * len(elenco) - 10 * lettere) / parole))


def giudizio(g: float | None, parole: int) -> str:
    if g is None:
        return "—"
    if parole < PAROLE_MINIME:
        return "⚪ testo breve"
    if g >= GULPEASE_OTTIMO:
        return "🟢 facile"
    if g >= GULPEASE_ACCETTABILE:
        return "🟡 accettabile"
    return "🔴 difficile"


@dataclass
class Leggibilita:
    indice: float | None
    frasi: int
    parole: int
    sezioni: list[tuple[str, float, int]]          # (titolo, indice, parole)
    lunghe: list[Frase]


def leggibilita(testo: Testo) -> Leggibilita:
    elenco = frasi(testo)
    sezioni = []
    confini = testo.sezioni + [(len(testo.testo), "")]
    for (a, titolo), (b, _) in zip(confini, confini[1:]):
        dentro = [f for f in elenco if a <= f.inizio < b]
        g = gulpease(dentro)
        if g is not None:
            sezioni.append((titolo, g, sum(f.parole for f in dentro)))
    return Leggibilita(gulpease(elenco), len(elenco), sum(f.parole for f in elenco),
                       sezioni, [f for f in elenco if f.parole > FRASE_LUNGA])


# ==========================================================================
#  3. I controlli
# ==========================================================================
@dataclass
class Problema:
    file: str
    riga: int
    categoria: str
    messaggio: str
    estratto: str = ""
    suggerimento: str = ""
    regola: str = ""
    contesto: str = ""

    def chiave(self) -> tuple:
        return (self.file, self.riga, self.regola, self.estratto)


MESI_GIORNI = ("Gennaio|Febbraio|Marzo|Aprile|Maggio|Giugno|Luglio|Agosto|Settembre|"
               "Ottobre|Novembre|Dicembre|Lunedì|Martedì|Mercoledì|Giovedì|Venerdì|"
               "Sabato|Domenica")
PLURALI_INGLESI = ("issues|commits|branches|pull requests|merge requests|sprints|meetings|"
                   "reviews|code reviews|workflows|files|tools|tests|bugs|features|templates|"
                   "tasks|milestones|labels|repositories|repos|releases|links|slides|mockups|"
                   "teams|tags|tickets|stakeholders|frameworks|containers|requirements|"
                   "use cases|deadlines|reports|feedbacks|badges|pipelines|jobs|runners|"
                   "users|deploys|backlogs|checklists|boards|endpoints|prompts|"
                   "tokens|embeddings|chatbots|plugins|widgets|dashboards|screenshots")
def singolare(parola: str) -> str:
    """issues -> issue, repositories -> repository, branches -> branch."""
    minuscola = parola.lower()
    if minuscola.endswith("ies"):
        return parola[:-3] + "y"
    if minuscola.endswith(("ches", "shes")):
        return parola[:-2]
    return parola[:-1]


RIPETIZIONI_AMMESSE = {"via", "piano", "poco", "così", "quasi", "ora", "subito", "pian",
                       "man", "tanto", "bene", "forte", "adagio", "1"}

# (regola, espressione, categoria, messaggio, suggerimento: testo o funzione)
REGOLE = [
    ("E_APOSTROFO", re.compile(r"(?<![^\W\d_])([Ee])['’](?=\s)"), "Tipografia",
     "«E'» con l'apostrofo: il verbo essere si scrive con l'accento.",
     lambda m: "È" if m.group(1) == "E" else "è"),
    ("ACCENTO_CHE", re.compile(r"\b([^\W\d_]*ch)è\b", re.I), "Ortografia",
     "Accento sbagliato: le parole in -ché vogliono l'accento acuto.",
     lambda m: m.group(1) + "é"),
    ("ACCENTO_NE_SE", re.compile(r"\b([NnSs])è\b"), "Ortografia",
     "Accento sbagliato: si scrive con l'accento acuto.", lambda m: m.group(1) + "é"),
    ("ACCENTO_TRE", re.compile(r"\b([^\W\d_]+tr)è\b", re.I), "Ortografia",
     "Accento sbagliato: i composti di tre vogliono l'accento acuto (ventitré).",
     lambda m: m.group(1) + "é"),
    ("PO", re.compile(r"\b([Pp])[òó](?![^\W\d_])"), "Ortografia",
     "«po'» (troncamento di «poco») si scrive con l'apostrofo, non con l'accento.",
     lambda m: m.group(1) + "o'"),
    ("QUAL_E", re.compile(r"\b([Qq]ual)['’](?=(?:è|era|erano|e)\b)"), "Ortografia",
     "«qual è» si scrive senza apostrofo (è un troncamento, non un'elisione).",
     lambda m: m.group(1) + " "),
    ("UN_APOSTROFO", re.compile(r"\b([Uu]n)['’]((?!auto\b|eco\b)[aeiouhAEIOUH][^\W\d_]*o)\b"),
     "Ortografia", "Davanti a un nome maschile «un» non vuole l'apostrofo.",
     lambda m: f"{m.group(1)} {m.group(2)}"),
    ("ACCENTO_MONOSILLABI", re.compile(r"\b(fà|stà|và|quì|quà|sù|blù|trè)\b", re.I),
     "Ortografia", "Questo monosillabo non vuole l'accento.",
     lambda m: unicodedata.normalize("NFC", "".join(
         c for c in unicodedata.normalize("NFD", m.group(1)) if unicodedata.category(c) != "Mn"))),
    ("SPAZIO_PRIMA_PUNTEGGIATURA", re.compile(r"(?<=[^\W_])[ \t]+([,;:.!?])(?=\s|$)"),
     "Tipografia", "Spazio prima della punteggiatura.", lambda m: m.group(1)),
    ("SPAZIO_DOPO_PUNTEGGIATURA", re.compile(r"(?<=[a-zà-ù]{2})([,;:]|\.(?=[A-ZÀ-Ú][a-zà-ù]))(?=[^\W\d_])"),
     "Tipografia", "Manca lo spazio dopo la punteggiatura.", lambda m: m.group(1) + " "),
    ("SPAZIO_PARENTESI", re.compile(r"\( +| +\)"), "Tipografia",
     "Spazio dopo la parentesi aperta o prima di quella chiusa.",
     lambda m: m.group(0).strip()),
    ("VIRGOLETTE_DRITTE", re.compile(r"\"[^\"\n]{1,200}\"|\""), "Tipografia",
     "Virgolette dritte: in LaTeX si scrivono ``così'' (o «così»).", ""),
    ("TRATTINO", re.compile(r"(?<= )-(?= )"), "Tipografia",
     "Trattino corto usato come lineetta: in LaTeX si scrive -- (–).", "--"),
    ("PUNTINI", re.compile(r"(?<!\.)\.\.\.(?!\.)"), "Tipografia",
     "Tre punti: in LaTeX si scrive \\dots (…), con la spaziatura giusta.", "\\dots"),
    ("MESI_GIORNI_MAIUSCOLI", re.compile(r"(?<=[^\W_] )(" + MESI_GIORNI + r")\b"),
     "Stile", "Nomi di mesi e giorni in italiano vanno in minuscolo.",
     lambda m: m.group(1).lower()),
    ("DATA_NUMERICA", re.compile(r"\b\d{1,2}/\d{1,2}/(?:\d{4}|\d{2})\b|"
                                 r"\b\d{1,2}[.-]\d{1,2}[.-]\d{4}\b"), "Stile",
     "Data in formato numerico: per uniformità scrivetela per esteso (12 novembre 2026) "
     "o come AAAA-MM-GG.", ""),
    ("PLURALE_INGLESE", re.compile(r"(?<!GitHub )\b(" + PLURALI_INGLESI + r")\b", re.I),
     "Stile", "In italiano le parole straniere non prendono la -s del plurale "
     "(«le issue», «i commit»).",
     lambda m: singolare(m.group(1))),
]


INIZIO_ERRORE, FINE_ERRORE = "\x01", "\x02"   # segnano il pezzo sbagliato nel contesto


def contesto(t: str, a: int, b: int, ampiezza: int = 35) -> str:
    sx = t[max(0, a - ampiezza):a].replace("\n", " ")
    dx = t[b:b + ampiezza].replace("\n", " ")
    sx = ("…" + sx.split(" ", 1)[-1]) if a > ampiezza and " " in sx else sx
    dx = (dx.rsplit(" ", 1)[0] + "…") if len(t) > b + ampiezza and " " in dx else dx
    return f"{sx.lstrip()}{INIZIO_ERRORE}{t[a:b]}{FINE_ERRORE}{dx.rstrip()}"


def controlli_tipografici(testo: Testo) -> list[Problema]:
    t = testo.testo
    trovati = []
    for regola, espr, categoria, messaggio, sugg in REGOLE:
        for m in espr.finditer(t):
            a, b = m.span()
            if testo.in_zona("codice", a, b):
                continue
            if regola in ("MESI_GIORNI_MAIUSCOLI", "DATA_NUMERICA") and \
                    testo.in_zona("titolo", a, b):
                continue                  # titoli, intestazioni, scadenze delle azioni
            if regola == "PLURALE_INGLESE" and m.group(1)[0].isupper():
                continue                  # nomi propri: Microsoft Teams, Cron Jobs
            if regola == "SPAZIO_DOPO_PUNTEGGIATURA" and m.group(1) == ".":
                parola = re.search(r"\S*$", t[max(0, a - 40):a]).group(0) + \
                    re.match(r"\S*", t[a:a + 40]).group(0)
                if parola.count(".") > 1:
                    continue              # nomi con più punti: Major.Minor.Patch
            file, riga = testo.dove(a)
            s = sugg(m) if callable(sugg) else sugg
            trovati.append(Problema(file, riga, categoria, messaggio, m.group(0).strip(),
                                    s, regola, contesto(t, a, b)))
    # parole ripetute: "il il", "che che"
    for m in re.finditer(r"(?<![^\W_])([^\W\d_]+)\s+(\1)(?![^\W_])", t, re.I):
        parola = m.group(1).lower()
        if parola in RIPETIZIONI_AMMESSE or testo.in_zona("codice", *m.span()):
            continue
        if m.group(1)[0].islower() and m.group(2)[0].isupper():
            continue                      # "in In Progress": la seconda è un nome
        if "\n\n" in t[m.start():m.end()]:
            continue                      # fine di un blocco e inizio del successivo
        file, riga = testo.dove(m.start(2))
        trovati.append(Problema(file, riga, "Ortografia", "Parola ripetuta.",
                                m.group(0), m.group(1), "PAROLA_RIPETUTA",
                                contesto(t, *m.span())))
    return trovati


def controlli_leggibilita(testo: Testo, lett: Leggibilita) -> list[Problema]:
    trovati = []
    for f in lett.lunghe:
        file, riga = testo.dove(f.inizio)
        inizio = " ".join(testo.testo[f.inizio:f.fine].split()[:8])
        trovati.append(Problema(file, riga, "Leggibilità",
                                f"Frase molto lunga ({f.parole} parole): spezzarla la rende "
                                "più chiara e alza l'indice Gulpease.",
                                "", "", "FRASE_LUNGA", inizio + " …"))
    return trovati


# ---- LanguageTool -------------------------------------------------------
def parole_da_ignorare() -> set[str]:
    parole: set[str] = set()
    try:
        for r in PAROLE.read_text(encoding="utf-8").splitlines():
            r = r.split("#", 1)[0].strip()
            if r:
                parole.update(p.lower() for p in PAROLA.findall(r))
    except OSError:
        pass
    for nome in nomi_del_gruppo().values():
        parole.update(p.lower() for p in PAROLA.findall(nome))
    try:
        import glossario
        g = glossario.leggi(ROOT, list(MILESTONE))
        for v in g.voci:
            parole.update(p.lower() for p in PAROLA.findall(glossario.testo_semplice(v.termine)))
    except Exception:  # noqa: BLE001  (il Glossario è un di più: non deve fermare l'analisi)
        pass
    return parole


def utf16(testo: str) -> list[int] | None:
    """Le posizioni di Java contano le unità UTF-16: per i caratteri fuori dal
    piano base (emoji) servono le conversioni."""
    if all(ord(c) <= 0xFFFF for c in testo):
        return None
    pos, acc = [], 0
    for c in testo:
        pos.append(acc)
        acc += 2 if ord(c) > 0xFFFF else 1
    return pos


def trova_java() -> str | None:
    for candidato in (os.environ.get("JAVA"), shutil.which("java")):
        if candidato:
            return candidato
    return None


def esegui_languagetool(testi: list[Testo], jar: Path) -> tuple[list[list[tuple]], str]:
    """[(inizio, fine, regola, categoria, inglese, messaggio, suggerimenti)] per
    ogni testo, più una nota se LanguageTool non è disponibile."""
    vuoto = [[] for _ in testi]
    java = trova_java()
    if not java:
        return vuoto, "Java non trovato: ortografia e grammatica non controllate."
    if not jar.is_file():
        return vuoto, ("LanguageTool non trovato: ortografia e grammatica non controllate "
                       "(per averlo: `python3 scripts/analisi_testo.py --scarica-lt`).")
    with tempfile.TemporaryDirectory() as cartella:
        file = []
        for n, t in enumerate(testi):
            p = Path(cartella) / f"{n}.txt"
            p.write_text(t.testo, encoding="utf-8")
            file.append(str(p))
        try:
            esito = subprocess.run([java, "-Xss4m", "-cp", str(jar), str(LT_JAVA),
                                    "--disattiva", ",".join(LT_SPENTE), *file],
                                   capture_output=True, timeout=1200)
        except (OSError, subprocess.TimeoutExpired) as e:
            return vuoto, f"LanguageTool non è partito ({e.__class__.__name__}): ortografia e grammatica non controllate."
    if esito.returncode != 0:
        errore = esito.stderr.decode("utf-8", "replace").strip().splitlines()
        motivo = next((r for r in reversed(errore) if r.strip() and "JAVA_TOOL_OPTIONS" not in r), "")
        return vuoto, f"LanguageTool si è fermato con un errore ({motivo[:200]}): ortografia e grammatica non controllate."
    risultati = vuoto
    for riga in esito.stdout.decode("utf-8", "replace").splitlines():
        campi = riga.split("\t")
        if len(campi) < 8 or not campi[0].isdigit():
            continue
        n, a, b = int(campi[0]), int(campi[1]), int(campi[2])
        if n < len(testi):
            risultati[n].append((a, b, campi[3], campi[4], campi[5] == "1", campi[6], campi[7]))
    return risultati, ""


def problemi_languagetool(testo: Testo, risultati: list[tuple], ignora: set[str]) -> list[Problema]:
    t = testo.testo
    conversione = utf16(t)
    trovati = []
    for a, b, regola, categoria, inglese, messaggio, suggerimenti in risultati:
        if conversione:
            a = bisect.bisect_left(conversione, a)
            b = bisect.bisect_left(conversione, b)
        parola = t[a:b]
        if testo.in_zona("codice", a, b) or testo.in_zona("nome", a, b):
            continue
        if categoria == LT_ORTOGRAFIA:
            minuscola = parola.lower()
            if (inglese or minuscola in ignora or minuscola in testo.corsivo
                    or testo.in_zona("corsivo", a, b) or testo.in_zona("termine", a, b)
                    or any(ch.isdigit() for ch in parola)
                    or any(ch.isupper() for ch in parola[1:])          # sigle, CamelCase
                    or (parola[:1].isupper() and not inizio_frase(t, a))):  # nomi propri
                continue
        file, riga = testo.dove(a)
        trovati.append(Problema(file, riga, CATEGORIE_LT.get(categoria, "Grammatica"),
                                messaggio, parola,
                                " / ".join(s for s in suggerimenti.split("|") if s),
                                regola, contesto(t, a, b)))
    return trovati


def inizio_frase(t: str, a: int) -> bool:
    prima = t[max(0, a - 20):a].rstrip(" “\"«(‘")
    return not prima or prima[-1] in ".!?…:\n"


# ==========================================================================
#  4. Il resoconto
# ==========================================================================
@dataclass
class Analisi:
    documento: Path
    leggibilita: Leggibilita
    problemi: list[Problema]

    @property
    def nome(self) -> str:
        return self.documento.relative_to(ROOT).as_posix()


def analizza(documenti: list[Path], usa_lt: bool, jar: Path, solo_gulpease: bool = False
             ) -> tuple[list[Analisi], str]:
    nomi = nomi_del_gruppo()
    testi = [estrai(d, nomi) for d in documenti]
    letture = [leggibilita(t) for t in testi]
    if solo_gulpease:
        return [Analisi(d, l, []) for d, l in zip(documenti, letture)], ""
    nota = ""
    risultati_lt: list[list[tuple]] = [[] for _ in testi]
    if usa_lt:
        risultati_lt, nota = esegui_languagetool(testi, jar)
    ignora = parole_da_ignorare()
    analisi = []
    for d, t, l, r in zip(documenti, testi, letture, risultati_lt):
        problemi = problemi_languagetool(t, r, ignora) + controlli_tipografici(t) + \
            controlli_leggibilita(t, l)
        unici = {p.chiave(): p for p in problemi}
        problemi = sorted(unici.values(), key=lambda p: (p.file != d.relative_to(ROOT).as_posix(),
                                                         p.file, p.riga, p.categoria))
        analisi.append(Analisi(d, l, problemi))
    return analisi, nota


def md(testo: str) -> str:
    """Testo sicuro dentro una riga di Markdown."""
    return re.sub(r"([\\`*_\[\]<>|#])", r"\\\1", testo)


def contesto_md(p: Problema) -> str:
    """Il contesto con il pezzo sbagliato in grassetto (gli spazi si vedono: ␣)."""
    if INIZIO_ERRORE not in p.contesto:
        return md(p.contesto)
    sx, resto = p.contesto.split(INIZIO_ERRORE, 1)
    errore, dx = resto.split(FINE_ERRORE, 1)
    if p.regola.startswith("SPAZIO") or not errore.strip():
        errore = errore.replace(" ", "␣")
    return f"{md(sx)}<b>{md(errore)}</b>{md(dx)}"


def contesto_semplice(p: Problema) -> str:
    return p.contesto.replace(INIZIO_ERRORE, "«").replace(FINE_ERRORE, "»")


def riga_problema(p: Problema) -> str:
    parti = [f"`{p.riga}` **{p.categoria}**"]
    if p.contesto:
        parti.append(contesto_md(p))
    if p.suggerimento:
        parti.append(f"→ *{md(p.suggerimento)}*")
    return f"- {' '.join(parti[:1])}: {' '.join(parti[1:])} — {md(p.messaggio)}"


def tabella_gulpease(analisi: list[Analisi]) -> list[str]:
    righe = ["| Documento | Gulpease | Frasi | Parole | Parole per frase | |",
             "| --- | ---: | ---: | ---: | ---: | --- |"]
    for a in analisi:
        l = a.leggibilita
        indice = f"{l.indice:.0f}" if l.indice is not None else "—"
        media = f"{l.parole / l.frasi:.1f}".replace(".", ",") if l.frasi else "—"
        righe.append(f"| `{md(a.nome)}` | **{indice}** | {l.frasi} | {l.parole} | {media} | "
                     f"{giudizio(l.indice, l.parole)} |")
    difficili = []
    for a in analisi:
        for titolo, g, parole in a.leggibilita.sezioni:
            if parole >= 150 and g < GULPEASE_ACCETTABILE:
                difficili.append(f"- `{md(Path(a.nome).stem)}`, sezione *{md(titolo)}*: "
                                 f"**{g:.0f}** ({parole} parole)")
    if difficili:
        righe += ["", "Sezioni più difficili da leggere (sotto "
                  f"{GULPEASE_ACCETTABILE}):", *difficili]
    righe += ["", "<details><summary>Come si legge l'indice Gulpease</summary>", "",
              "Misura la leggibilità di un testo italiano da 0 a 100 (più alto = più facile): "
              "`89 + (300 × frasi − 10 × lettere) / parole`. Lo abbassano le frasi lunghe e le "
              "parole lunghe. Per chi ha un diploma un testo è difficile sotto "
              f"{GULPEASE_ACCETTABILE} e facile sopra {GULPEASE_OTTIMO}. Titoli, intestazioni "
              "di tabella e didascalie non contano; ogni cella di tabella o voce di elenco è "
              "una frase.", "", "</details>"]
    return righe


def conta(problemi: list[Problema]) -> str:
    per = {}
    for p in problemi:
        per[p.categoria] = per.get(p.categoria, 0) + 1
    return ", ".join(f"{n} {c.lower()}" for c, n in sorted(per.items(), key=lambda x: -x[1]))


def resoconto(analisi: list[Analisi], nota: str, cambiate: dict[str, set[int]] | None,
              solo_gulpease: bool = False) -> str:
    righe = ["## 🔎 Analisi dei testi", "",
             "_Non blocca il merge: sono suggerimenti da valutare. Un falso allarme? Se è un "
             "nome o un termine giusto, aggiungetelo a `scripts/analisi/parole.txt`._", "",
             "### Leggibilità", "", *tabella_gulpease(analisi)]
    if solo_gulpease:
        return "\n".join(righe) + "\n"
    righe += ["", "### Ortografia, grammatica e stile", ""]
    if nota:
        righe += [f"> ⚠️ {nota}", ""]
    if not any(a.problemi for a in analisi):
        righe.append("Nessun problema trovato. 🎉")
    for a in analisi:
        if not a.problemi:
            continue
        if cambiate is not None:
            nuove = [p for p in a.problemi if p.riga in cambiate.get(p.file, set())]
            altre = [p for p in a.problemi if p not in nuove]
            righe += [f"#### `{md(a.nome)}`", ""]
            if nuove:
                righe += [f"**Nelle righe cambiate da questa PR** ({conta(nuove)}):", ""]
                righe += [riga_con_file(p, a) for p in nuove[:MAX_PER_DOCUMENTO]]
                if len(nuove) > MAX_PER_DOCUMENTO:
                    righe.append(f"- … e altri {len(nuove) - MAX_PER_DOCUMENTO}")
            else:
                righe.append("Nelle righe cambiate da questa PR: nessun problema. ✅")
            if altre:
                righe += ["", f"<details><summary>Nel resto del documento: {len(altre)} "
                          f"({conta(altre)})</summary>", ""]
                righe += [riga_con_file(p, a) for p in altre[:MAX_PER_DOCUMENTO]]
                if len(altre) > MAX_PER_DOCUMENTO:
                    righe.append(f"- … e altri {len(altre) - MAX_PER_DOCUMENTO}")
                righe += ["", "</details>"]
            righe.append("")
        else:
            righe += [f"<details><summary><code>{md(a.nome)}</code>: {len(a.problemi)} "
                      f"({conta(a.problemi)})</summary>", ""]
            righe += [riga_con_file(p, a) for p in a.problemi[:MAX_PER_DOCUMENTO * 2]]
            if len(a.problemi) > MAX_PER_DOCUMENTO * 2:
                righe.append(f"- … e altri {len(a.problemi) - MAX_PER_DOCUMENTO * 2}")
            righe += ["", "</details>", ""]
    testo = "\n".join(righe).rstrip() + "\n"
    if len(testo) > MAX_COMMENTO:
        testo = testo[:MAX_COMMENTO].rsplit("\n", 1)[0] + \
            "\n\n_… resoconto troncato: il testo completo è nella pagina dell'Action._\n"
    return testo


def riga_con_file(p: Problema, a: Analisi) -> str:
    """La riga del problema; se sta in un capitolo incluso, col nome del file."""
    r = riga_problema(p)
    if p.file != a.nome:
        r = r.replace(f"- `{p.riga}`", f"- `{md(Path(p.file).name)}:{p.riga}`", 1)
    return r


def annotazioni(analisi: list[Analisi], cambiate: dict[str, set[int]] | None) -> list[str]:
    """Avvisi di GitHub accanto alle righe (solo quelle cambiate nella PR)."""
    righe = []
    for a in analisi:
        for p in a.problemi:
            if cambiate is not None and p.riga not in cambiate.get(p.file, set()):
                continue
            testo = p.messaggio + (f" Suggerimento: {p.suggerimento}" if p.suggerimento else "")
            testo = testo.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
            righe.append(f"::notice file={p.file},line={p.riga},title={p.categoria}::{testo}")
    return righe[:MAX_ANNOTAZIONI]


# ==========================================================================
#  5. Quali documenti, quali righe
# ==========================================================================
def tutti_i_documenti() -> list[Path]:
    trovati = []
    for m in MILESTONE:
        if (ROOT / m).is_dir():
            trovati += [p for p in sorted((ROOT / m).rglob("*.tex"))
                        if not p.name.endswith(".registro.tex") and registro.ha_documentclass(p)]
    return trovati


def git(*argomenti: str) -> str:
    esito = subprocess.run(["git", "-c", "core.quotePath=false", *argomenti], cwd=ROOT,
                           capture_output=True)
    if esito.returncode != 0:
        raise SystemExit(f"Errore di git: {esito.stderr.decode('utf-8', 'replace').strip()}")
    return esito.stdout.decode("utf-8", "replace")


def righe_cambiate(base: str) -> dict[str, set[int]]:
    """file -> righe aggiunte o modificate rispetto a base."""
    cambiate: dict[str, set[int]] = {}
    file = None
    for r in git("diff", "-U0", "--no-color", "--no-ext-diff", f"{base}...HEAD").splitlines():
        if r.startswith("+++ "):
            nome = r[4:].rstrip("\t")
            file = nome[2:] if nome.startswith("b/") else None
            if file and file.startswith('"'):
                file = file.strip('"')
        elif r.startswith("@@") and file:
            m = re.match(r"@@ -\S+ \+(\d+)(?:,(\d+))? @@", r)
            if m:
                inizio, quante = int(m.group(1)), int(m.group(2) or 1)
                cambiate.setdefault(file, set()).update(range(inizio, inizio + quante))
    return cambiate


def scarica_lt(destinazione: Path = LT_JAR) -> int:
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    print(f"Scarico LanguageTool (dentro textidote.jar, circa 220 MB) da\n  {LT_URL}")
    temporaneo = destinazione.with_suffix(".part")
    with urllib.request.urlopen(LT_URL, timeout=300) as r, open(temporaneo, "wb") as f:
        shutil.copyfileobj(r, f)
    h = hashlib.sha256(temporaneo.read_bytes()).hexdigest()
    if h != LT_SHA256:
        temporaneo.unlink(missing_ok=True)
        print(f"Il file scaricato non è quello atteso (sha256 {h}): non lo uso.")
        return 1
    temporaneo.replace(destinazione)
    print(f"Fatto: {destinazione.relative_to(ROOT)}")
    return 0


def scrivi_output_github(**valori: str) -> None:
    uscita = os.environ.get("GITHUB_OUTPUT")
    if uscita:
        with open(uscita, "a", encoding="utf-8") as f:
            for k, v in valori.items():
                f.write(f"{k}={v}\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Analisi dei testi (non bloccante).")
    ap.add_argument("documenti", nargs="*", help="i .tex da controllare (predefinito: tutti)")
    ap.add_argument("--pr", metavar="BASE", help="solo i documenti cambiati rispetto a BASE "
                    "(es. origin/main), con in evidenza le righe cambiate")
    ap.add_argument("--solo-gulpease", action="store_true", help="solo la leggibilità")
    ap.add_argument("--senza-lt", action="store_true", help="senza LanguageTool")
    ap.add_argument("--lt", type=Path, default=Path(os.environ.get("TEXTIDOTE_JAR", LT_JAR)),
                    help="percorso di textidote.jar (contiene LanguageTool)")
    ap.add_argument("--scarica-lt", action="store_true", help="scarica LanguageTool ed esce")
    ap.add_argument("--uscita", type=Path, help="scrive il resoconto (Markdown) in questo file")
    ap.add_argument("--json", type=Path, help="scrive anche i problemi in JSON")
    ap.add_argument("--annotazioni", action="store_true",
                    help="avvisi di GitHub Actions accanto alle righe")
    a = ap.parse_args(argv)

    if a.scarica_lt:
        return scarica_lt()

    cambiate = None
    if a.pr:
        cambiate = righe_cambiate(a.pr)
        file = [f for f in git("diff", "--name-only", "-z", f"{a.pr}...HEAD").split("\0") if f]
        documenti = registro.documenti_toccati(file, ROOT)
    elif a.documenti:
        documenti = []
        for d in a.documenti:
            p = (Path.cwd() / d).resolve()
            documenti += ([x for x in sorted(p.rglob("*.tex")) if not x.name.endswith(".registro.tex")
                           and registro.ha_documentclass(x)] if p.is_dir() else [p])
    else:
        documenti = tutti_i_documenti()
    documenti = [d for d in documenti if d.is_file()]
    scrivi_output_github(documenti=str(len(documenti)))
    if not documenti:
        print("Nessun documento da analizzare.")
        return 0

    analisi, nota = analizza(documenti, not a.senza_lt, a.lt, a.solo_gulpease)
    testo = resoconto(analisi, nota, cambiate, a.solo_gulpease)
    if a.uscita:
        a.uscita.parent.mkdir(parents=True, exist_ok=True)
        a.uscita.write_text(testo, encoding="utf-8")
    else:
        print(testo)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps([{
            "documento": x.nome,
            "gulpease": None if x.leggibilita.indice is None else round(x.leggibilita.indice, 1),
            "frasi": x.leggibilita.frasi, "parole": x.leggibilita.parole,
            "problemi": [{**p.__dict__, "contesto": contesto_semplice(p)} for p in x.problemi]}
            for x in analisi],
            ensure_ascii=False, indent=1), encoding="utf-8")
    if a.annotazioni:
        for r in annotazioni(analisi, cambiate):
            print(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
