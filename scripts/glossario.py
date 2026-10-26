"""
glossario.py -- legge il Glossario e lo confronta con i termini marcati.

Lo usano build.py (controlli nelle pull request) e sito.py (pagina
glossario.html del sito): non serve lanciarlo a mano.

Come funziona:
  - il Glossario è il documento che contiene le voci \\termine{Voce}{...}
    (di solito <Milestone>/documenti/esterni/glossario/, una lettera per
    file in capitoli/). Deve essercene UNO solo;
  - nei documenti i termini si marcano con \\glo{termine}, oppure con
    \\glo[voce]{testo} quando il testo è diverso dalla voce (plurali...);
  - maiuscole, spazi in più e formattazione non contano nel confronto.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

# Se True, nelle pull request i termini marcati ma assenti dal Glossario,
# le voci ripetute e i Glossari doppi rendono ROSSA la compilazione.
# Se False sono solo avvisi. Consiglio: False all'inizio, True prima
# della consegna dell'RTB.
BLOCCANTE = False

COMMENTO = re.compile(r"(?<!\\)%.*")


@dataclass
class Voce:
    termine: str            # come scritto nel Glossario (LaTeX)
    definizione: str        # LaTeX
    file: str               # percorso relativo al repository
    riga: int
    lettera: str = ""       # la lettera del file (\letteraglossario)

    @property
    def chiave(self) -> str:
        return chiave(self.termine)


@dataclass
class Glossario:
    voci: list[Voce] = field(default_factory=list)
    principale: Path | None = None     # il .tex principale del Glossario
    cartella: Path | None = None       # la sua cartella (con capitoli/)
    doppi: list[str] = field(default_factory=list)   # altri Glossari trovati

    def __bool__(self) -> bool:
        return bool(self.voci)


@dataclass
class Esito:
    bloccanti: list[str] = field(default_factory=list)   # errori veri
    avvisi: list[str] = field(default_factory=list)      # da sistemare
    note: list[str] = field(default_factory=list)        # solo informazioni

    def righe_markdown(self) -> list[str]:
        if not (self.bloccanti or self.avvisi or self.note):
            return []
        segno = "❌" if self.bloccanti and BLOCCANTE else "📖"
        righe = ["", f"{segno} **Glossario:**"]
        righe += [f"- {r}" for r in self.bloccanti + self.avvisi]
        righe += [f"- _{r}_" for r in self.note]
        return righe


# --------------------------------------------------------------------------
#  Lettura del testo LaTeX
# --------------------------------------------------------------------------
def senza_commenti(testo: str) -> str:
    """Toglie i commenti ma lascia le righe al loro posto (numeri di riga)."""
    return "\n".join(COMMENTO.sub("", r) for r in testo.splitlines())


def _graffa(testo: str, i: int) -> tuple[str, int] | None:
    """Legge {...} che inizia (dopo eventuali spazi) alla posizione i."""
    while i < len(testo) and testo[i] in " \t\r\n":
        i += 1
    if i >= len(testo) or testo[i] != "{":
        return None
    livello, inizio = 1, i + 1
    i += 1
    while i < len(testo) and livello:
        if testo[i] == "\\":
            i += 2
            continue
        livello += {"{": 1, "}": -1}.get(testo[i], 0)
        i += 1
    return testo[inizio:i - 1], i


def occorrenze(testo: str, comando: str, quanti: int) -> list[tuple[str, list[str], int]]:
    """Tutte le occorrenze di \\comando[opzionale]{arg}...{arg}:
    restituisce (opzionale, argomenti, numero di riga)."""
    trovate = []
    for m in re.finditer(r"\\" + comando + r"(?![A-Za-z@])", testo):
        i, opzionale = m.end(), ""
        ms = re.match(r"\s*\[([^\]]*)\]", testo[i:])
        if ms:
            opzionale, i = ms.group(1), i + ms.end()
        argomenti = []
        for _ in range(quanti):
            letto = _graffa(testo, i)
            if letto is None:
                break
            argomenti.append(letto[0])
            i = letto[1]
        if len(argomenti) == quanti:
            trovate.append((opzionale, argomenti, testo.count("\n", 0, m.start()) + 1))
    return trovate


def testo_semplice(latex: str) -> str:
    """'\\emph{Pull}~request' -> 'Pull request'."""
    t = latex.replace("~", " ").replace("\\-", "")
    t = re.sub(r"\\[a-zA-Z@]+\*?\s*(\[[^\]]*\])?", "", t)
    t = re.sub(r"\\(.)", r"\1", t)
    return re.sub(r"\s+", " ", t.replace("{", "").replace("}", "")).strip()


def senza_accenti(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t)
                   if unicodedata.category(c) != "Mn")


def chiave(termine: str) -> str:
    """La forma usata per confrontare: niente formattazione, minuscole."""
    return testo_semplice(termine).lower()


def ordinamento(termine: str) -> str:
    return senza_accenti(chiave(termine))


def ancora(termine: str) -> str:
    """'Pull request' -> 'pull-request' (indirizzo della voce sul sito)."""
    t = re.sub(r"[^a-z0-9]+", "-", senza_accenti(chiave(termine)))
    return t.strip("-") or "voce"


# --------------------------------------------------------------------------
#  Ricerca del Glossario
# --------------------------------------------------------------------------
def _file_tex(root: Path, milestone: list[str]) -> list[Path]:
    trovati: list[Path] = []
    for nome in milestone:
        if (root / nome).is_dir():
            trovati.extend(sorted((root / nome).rglob("*.tex")))
    return trovati


def _ha_documentclass(p: Path) -> bool:
    return "\\documentclass" in senza_commenti(p.read_text(encoding="utf-8", errors="replace"))


def _documento_di(file: Path, root: Path) -> Path:
    """Il .tex principale a cui appartiene un capitolo: il primo .tex con
    \\documentclass risalendo le cartelle (fino alla cartella milestone)."""
    if _ha_documentclass(file):
        return file
    cartella = file.parent
    while cartella != root and cartella.parent != root:
        principali = [p for p in sorted(cartella.glob("*.tex")) if _ha_documentclass(p)]
        if principali:
            return principali[0]
        cartella = cartella.parent
    return file


def leggi(root: Path, milestone: list[str]) -> Glossario:
    """Trova il Glossario dentro le cartelle delle milestone e ne legge le voci."""
    per_documento: dict[Path, list[Voce]] = {}
    for f in _file_tex(root, milestone):
        testo = senza_commenti(f.read_text(encoding="utf-8", errors="replace"))
        if "\\termine" not in testo:
            continue
        lettera = occorrenze(testo, "letteraglossario", 1)
        lettera_file = testo_semplice(lettera[0][1][0]) if lettera else ""
        voci = [Voce(termine=a[0].strip(), definizione=a[1].strip(),
                     file=f.relative_to(root).as_posix(), riga=r, lettera=lettera_file)
                for _, a, r in occorrenze(testo, "termine", 2)]
        if voci:
            per_documento.setdefault(_documento_di(f, root), []).extend(voci)

    g = Glossario()
    if not per_documento:
        return g
    # se ce n'è più di uno, vale quello con più voci; gli altri sono "doppi"
    ordinati = sorted(per_documento.items(), key=lambda kv: -len(kv[1]))
    g.principale, g.voci = ordinati[0]
    g.cartella = g.principale.parent
    g.doppi = [p.relative_to(root).as_posix() for p, _ in ordinati[1:]]
    return g


def termini_marcati(root: Path, file: list[Path]) -> dict[str, list[tuple[str, int, str]]]:
    """chiave -> [(file, riga, testo marcato)] per tutti i \\glo dei file."""
    usi: dict[str, list[tuple[str, int, str]]] = {}
    for f in file:
        if not f.exists():
            continue
        testo = senza_commenti(f.read_text(encoding="utf-8", errors="replace"))
        for opzionale, (mostrato,), riga in occorrenze(testo, "glo", 1):
            voce = opzionale or mostrato
            usi.setdefault(chiave(voce), []).append(
                (f.relative_to(root).as_posix(), riga, testo_semplice(voce)))
    return usi


# --------------------------------------------------------------------------
#  Controlli
# --------------------------------------------------------------------------
def controlla(g: Glossario, root: Path, milestone: list[str],
              da_controllare: list[Path], completo: bool) -> Esito:
    """da_controllare: i .tex in cui cercare termini marcati ma assenti.
    completo: controlla anche le voci (doppioni, ordine...) e segnala quelle
    mai usate. Si fa nella build completa e nelle PR che toccano il Glossario."""
    esito = Esito()
    tutti = _file_tex(root, milestone)

    if not g:
        usi = termini_marcati(root, da_controllare)
        if usi and da_controllare:
            esito.note.append(f"Ci sono {len(usi)} termini marcati con \\glo ma il Glossario "
                              "non esiste ancora: verranno controllati quando ci sarà.")
        return esito

    for altro in g.doppi:
        esito.bloccanti.append(f"C'è più di un Glossario: oltre a `{g.principale.relative_to(root).as_posix()}` "
                               f"ci sono voci anche in `{altro}`. Il Glossario è uno solo: "
                               "toglietene una copia (GUIDA.md, ricetta 16).")

    # voci ripetute
    viste: dict[str, Voce] = {}
    for v in g.voci:
        if v.chiave in viste and completo:
            prima = viste[v.chiave]
            esito.bloccanti.append(f"La voce \"{testo_semplice(v.termine)}\" è ripetuta: "
                                   f"`{prima.file}:{prima.riga}` e `{v.file}:{v.riga}`.")
        else:
            viste[v.chiave] = v

    # definizioni vuote, lettera sbagliata, ordine alfabetico
    per_file: dict[str, list[Voce]] = {}
    for v in (g.voci if completo else []):
        per_file.setdefault(v.file, []).append(v)
        if not testo_semplice(v.definizione) or testo_semplice(v.definizione) in ("...", "…", "TODO"):
            esito.avvisi.append(f"La voce \"{testo_semplice(v.termine)}\" non ha una definizione "
                                f"(`{v.file}:{v.riga}`).")
        iniziale = ordinamento(v.termine)[:1].upper()
        if len(v.lettera) == 1 and iniziale.isalpha() and iniziale != v.lettera.upper():
            esito.avvisi.append(f"La voce \"{testo_semplice(v.termine)}\" inizia per {iniziale} "
                                f"ma è nella lettera {v.lettera.upper()} (`{v.file}:{v.riga}`).")
    for file, voci in per_file.items():
        for a, b in zip(voci, voci[1:]):
            if ordinamento(b.termine) < ordinamento(a.termine):
                esito.avvisi.append(f"In `{file}` le voci non sono in ordine alfabetico: "
                                    f"\"{testo_semplice(b.termine)}\" (riga {b.riga}) va prima di "
                                    f"\"{testo_semplice(a.termine)}\".")
                break

    # termini marcati ma assenti
    usi = termini_marcati(root, da_controllare)
    for voce, dove in sorted(usi.items()):
        if voce in viste:
            continue
        file, riga, mostrato = dove[0]
        altri = f" (e altre {len(dove) - 1} volte)" if len(dove) > 1 else ""
        esito.bloccanti.append(f"\"{mostrato}\" è marcato con \\glo in `{file}:{riga}`{altri} "
                               "ma non è nel Glossario.")

    # voci mai usate (solo informazione)
    if completo:
        usate = set(termini_marcati(root, tutti))
        inutili = [testo_semplice(v.termine) for v in g.voci if v.chiave not in usate]
        if inutili:
            elenco = ", ".join(inutili[:15]) + (" ..." if len(inutili) > 15 else "")
            esito.note.append(f"Voci del Glossario non marcate in nessun documento ({len(inutili)}): "
                              f"{elenco}. Va bene se sono termini utili comunque.")
    return esito
