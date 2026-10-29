#!/usr/bin/env python3
"""
build.py -- compila i documenti LaTeX e prepara il sito con i PDF.

I documenti stanno nelle cartelle delle milestone: Candidatura/, RTB/, PB/
(dentro: documenti/ e verbali/, ognuna con interni/ ed esterni/).

Si lancia dalla cartella principale del repository:

    python scripts/build.py                  compila tutti i documenti e crea site/
    python scripts/build.py FILE.tex [...]   compila solo i file indicati
    python scripts/build.py RTB              compila solo i documenti di una cartella
    python scripts/build.py --esempi         compila anche modelli ed esempi
    python scripts/build.py --list           elenca i documenti trovati
    python scripts/build.py --clean          cancella build/ e site/, poi compila

Le automazioni (CI) usano in più:

    python scripts/build.py --anteprima origin/main
        nelle pull request: compila TUTTO (documenti, modelli ed esempi),
        così nessun errore sfugge, e prepara il commento con i soli
        documenti toccati.

    python scripts/build.py --pdf-accanto
        dopo il merge su main: mette il PDF accanto a ogni .tex cambiato
        (es. RTB/verbali/interni/VI-2026-11-03.pdf). Lo usa solo la CI:
        in locale non serve, il vostro PDF di prova è in build/.

Dove finiscono i file:
    build/   file temporanei di LaTeX e PDF di prova (si possono cancellare)
    site/    i PDF con la versione nel nome e index.html: è il sito
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
SITE = ROOT / "site"
ANTEPRIMA = BUILD / "anteprima"
LATEXMKRC = ROOT / "latexmkrc"

# Le cartelle delle milestone, nell'ordine in cui compaiono sul sito.
# I documenti si cercano SOLO qui dentro (in qualunque sottocartella).
MILESTONE = [
    ("Candidatura", "Candidatura"),
    ("RTB", "RTB · Requirements and Technology Baseline"),
    ("PB", "PB · Product Baseline"),
]
NOMI_MILESTONE = [nome for nome, _ in MILESTONE]

# Dentro ogni milestone il sito divide i documenti in queste sezioni
SEZIONI = [
    ("documenti", "esterni", "Documenti esterni"),
    ("documenti", "interni", "Documenti interni"),
    ("verbali", "esterni", "Verbali esterni"),
    ("verbali", "interni", "Verbali interni"),
]

# Cartelle in cui NON si cercano documenti fuori posto (vedi fuori_posto)
CARTELLE_SISTEMA = {"template", "scripts", "build", "site", "allegati",
                    "node_modules"}

# Modelli ed esempi: si compilano nelle pull request, per controllare che
# la classe funzioni ancora, ma non finiscono sul sito
CARTELLE_ESEMPI = ("template/modelli", "template/esempi")

# Messaggio dei commit con cui la CI salva i PDF accanto ai .tex.
# "[skip ci]" evita che quel commit faccia ripartire le automazioni.
MESSAGGIO_BOT = "Aggiorna i PDF accanto ai sorgenti [skip ci]"

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
        "agosto", "settembre", "ottobre", "novembre", "dicembre"]


@dataclass
class Documento:
    sorgente: Path                  # percorso assoluto del .tex
    esempio: bool = False           # modello/esempio: si compila ma non si pubblica
    titolo: str = ""
    versione: str = ""              # dalla PRIMA riga \modifica del registro
    data: str = ""                  # AAAA-MM-GG
    tipo: str = ""                  # verbale interno/esterno, documento, lettera
    uso: str = ""                   # interno/esterno (come stampato in copertina)
    sottotitolo: str = ""           # lettere: la riga "Oggetto" (per il sito)
    ok: bool = False                # compilato senza errori?
    errori: list[str] = field(default_factory=list)
    dipendenze: set[str] = field(default_factory=set)  # file letti da LaTeX
    registro: list[str] = field(default_factory=list)  # problemi del registro

    @property
    def relativo(self) -> Path:
        return self.sorgente.relative_to(ROOT)

    @property
    def milestone(self) -> str:
        """Candidatura, RTB o PB: la prima cartella del percorso."""
        parti = self.relativo.parts
        return parti[0] if len(parti) > 1 and parti[0] in NOMI_MILESTONE else ""

    @property
    def categoria(self) -> str:
        """documenti/verbali: dalla cartella; se manca, dal tipo."""
        parti = self.relativo.parts[1:-1]
        for c in ("verbali", "documenti"):
            if c in parti:
                return c
        return "verbali" if self.tipo.startswith("verbale") else "documenti"

    @property
    def visibilita(self) -> str:
        """interni/esterni: dalla cartella; se manca, da \\uso."""
        parti = self.relativo.parts[1:-1]
        for v in ("interni", "esterni"):
            if v in parti:
                return v
        return "interni" if self.uso == "interno" else "esterni"

    @property
    def avvisi(self) -> list[str]:
        """Incoerenze tra la cartella e il contenuto (non bloccano nulla)."""
        if self.esempio or not self.milestone:
            return []
        parti = self.relativo.parts[1:-1]
        dove = self.relativo.as_posix()
        trovati = []
        if "verbali" in parti and not self.tipo.startswith("verbale"):
            trovati.append(f"`{dove}` è nella cartella `verbali` ma non è un verbale.")
        if "documenti" in parti and self.tipo.startswith("verbale"):
            trovati.append(f"`{dove}` è un verbale ma è nella cartella `documenti`.")
        cartella = next((v for v in ("interni", "esterni") if v in parti), "")
        atteso = "interni" if self.uso == "interno" else "esterni"
        if cartella and cartella != atteso:
            if self.tipo.startswith("verbale"):
                rimedio = f"la prima riga dice `verbale={self.uso}`"
            else:
                rimedio = f"in copertina c'è scritto uso {self.uso} (comando `\\uso`)"
            trovati.append(f"`{dove}` è nella cartella `{cartella}` ma {rimedio}.")
        trovati += [f"`{dove}`, registro delle modifiche: {r}" for r in self.registro]
        return trovati

    @property
    def nome_pdf(self) -> str:
        suffisso = f"_v{self.versione}" if self.versione else ""
        return f"{self.sorgente.stem}{suffisso}.pdf"

    @property
    def pdf_build(self) -> Path:
        return BUILD / self.relativo.parent / f"{self.sorgente.stem}.pdf"

    @property
    def pdf_sito(self) -> Path:
        return SITE / self.relativo.parent / self.nome_pdf

    @property
    def pdf_accanto(self) -> Path:
        """Il PDF salvato nel repository, accanto al .tex (lo scrive la CI)."""
        return self.sorgente.with_suffix(".pdf")


# --------------------------------------------------------------------------
#  Lettura dei dati dal sorgente .tex
# --------------------------------------------------------------------------
COMMENTO = re.compile(r"(?<!\\)%.*")


def senza_commenti(testo: str) -> str:
    """Toglie i commenti LaTeX (da % a fine riga, ma non \\%)."""
    return "\n".join(COMMENTO.sub("", riga) for riga in testo.splitlines())


def argomenti(testo: str, comando: str, quanti: int = 1) -> list[str]:
    """Primi `quanti` argomenti {...} della PRIMA occorrenza di \\comando."""
    m = re.search(r"\\" + comando + r"(?![A-Za-z@])", testo)
    if not m:
        return []
    i, risultato = m.end(), []
    while len(risultato) < quanti:
        while i < len(testo) and testo[i] in " \t\r\n":
            i += 1
        if i >= len(testo) or testo[i] != "{":
            break
        livello, inizio = 1, i + 1
        i += 1
        while i < len(testo) and livello:
            if testo[i] == "\\":        # salta \{ e \}
                i += 2
                continue
            if testo[i] == "{":
                livello += 1
            elif testo[i] == "}":
                livello -= 1
            i += 1
        risultato.append(testo[inizio:i - 1].strip())
    return risultato


def righe_registro(testo: str) -> list[dict]:
    """Tutte le righe \\modifica{versione}{data}{autore}{verificatore}{descrizione}[approvatore]
    del registro, nell'ordine in cui sono scritte (la più recente in cima)."""
    righe = []
    for m in re.finditer(r"\\modifica(?![A-Za-z@])", testo):
        i, valori = m.end(), []
        while len(valori) < 5:                  # i cinque argomenti {...}
            while i < len(testo) and testo[i] in " \t\r\n":
                i += 1
            if i >= len(testo) or testo[i] != "{":
                break
            livello, inizio = 1, i + 1
            i += 1
            while i < len(testo) and livello:
                if testo[i] == "\\":
                    i += 2
                    continue
                livello += {"{": 1, "}": -1}.get(testo[i], 0)
                i += 1
            valori.append(testo[inizio:i - 1].strip())
        if len(valori) < 5:
            continue
        approvatore = re.match(r"\s*\[([^\]]*)\]", testo[i:])   # l'eventuale [approvatore]
        righe.append(dict(zip(("versione", "data", "autore", "verificatore", "descrizione"), valori),
                          approvatore=approvatore.group(1).strip() if approvatore else ""))
    return righe


def persone(campo: str) -> set[str]:
    """'mazzurana, biasini' -> {'mazzurana', 'biasini'}; '--' o vuoto -> {}."""
    return {p.strip() for p in campo.split(",") if p.strip() not in ("", "--", "-")}


def controlla_registro(testo: str, tipo: str, data_riunione: str) -> list[str]:
    """Le regole delle versioni (GUIDA.md, sezione 5) che la classe non può
    controllare da sola. Sono solo avvisi: non bloccano la compilazione."""
    problemi = []
    righe = righe_registro(testo)
    for n, r in enumerate(righe):
        v = r["versione"]
        if not persone(r["autore"]):
            problemi.append(f"nella riga {v} manca l'autore: ogni riga è una modifica fatta da qualcuno "
                            "(niente righe di sola \"Verifica\").")
        if not persone(r["verificatore"]):
            problemi.append(f"la riga {v} non è ancora verificata (`--`). Prima del merge il Verificatore "
                            "scrive la sua chiave al posto di `--`: una versione esiste solo se è verificata.")
        elif persone(r["autore"]) & persone(r["verificatore"]):
            problemi.append(f"nella riga {v} chi verifica è anche autore: serve un'altra persona.")
        if re.fullmatch(r"[1-9]\d*\.0\.0", v) and tipo == "documento" and not r["approvatore"]:
            problemi.append(f"la riga {v} è un'approvazione ma manca l'approvatore: aggiungete in fondo "
                            "`[chiave del Responsabile]`.")
        if n + 1 < len(righe) and r["data"] < righe[n + 1]["data"]:
            problemi.append(f"la riga {v} ({r['data']}) è più vecchia della riga sotto, "
                            f"{righe[n + 1]['versione']} ({righe[n + 1]['data']}): le date non possono "
                            "tornare indietro salendo.")
        if tipo.startswith("verbale") and data_riunione and r["data"] < data_riunione:
            problemi.append(f"la riga {v} ha data {r['data']}, prima della riunione ({data_riunione}).")
    return problemi


def pulisci(latex: str) -> str:
    """Rende leggibile un titolo LaTeX per la pagina web."""
    t = latex.replace("~", " ").replace("--", "–").replace("\\&", "&")
    t = re.sub(r"\\[a-zA-Z]+\*?\s*", "", t)
    return re.sub(r"[{}]", "", t).strip()


def tipo_documento(testo: str) -> str:
    m = re.search(r"\\documentclass\s*\[([^\]]*)\]\s*\{gpt\}", testo)
    opzioni = [o.replace(" ", "") for o in m.group(1).split(",")] if m else []
    if "documento" in opzioni:
        return "documento"
    if "lettera" in opzioni:
        return "lettera"
    if "verbale=esterno" in opzioni or "esterno" in opzioni:
        return "verbale esterno"
    return "verbale interno"


def leggi(sorgente: Path, esempio: bool = False) -> Documento:
    testo = senza_commenti(sorgente.read_text(encoding="utf-8"))
    d = Documento(sorgente, esempio=esempio)
    titolo = argomenti(testo, "titolo")
    d.titolo = (pulisci(titolo[0]) if titolo else "") or sorgente.stem
    # versione e data dell'ultima modifica: la PRIMA riga del registro
    # (la classe gpt.cls fa esattamente la stessa cosa)
    modifica = argomenti(testo, "modifica", 2)
    d.versione = modifica[0] if modifica else ""
    data = argomenti(testo, "data")
    d.data = data[0] if data else (modifica[1] if len(modifica) > 1 else "")
    d.tipo = tipo_documento(testo)
    d.registro = controlla_registro(testo, d.tipo, data[0] if data else "")
    oggetto = argomenti(testo, "oggetto")
    if oggetto:
        d.sottotitolo = pulisci(oggetto[0])
    # uso: come fa la classe, per i verbali vale il tipo, per gli altri
    # \uso{...} e, se manca, "esterno"
    uso = argomenti(testo, "uso")
    if d.tipo.startswith("verbale"):
        d.uso = d.tipo.split()[1]
    else:
        d.uso = uso[0] if uso and uso[0] in ("interno", "esterno") else "esterno"
    return d


def ha_documentclass(percorso: Path) -> bool:
    try:
        return "\\documentclass" in senza_commenti(percorso.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return False


def trova_documenti() -> list[Path]:
    """I documenti da pubblicare: tutti i .tex con \\documentclass dentro
    Candidatura/, RTB/ e PB/ (i capitoli inclusi con \\input non ce l'hanno)."""
    candidati: list[Path] = []
    for nome in NOMI_MILESTONE:
        cartella = ROOT / nome
        if cartella.is_dir():
            candidati.extend(sorted(cartella.rglob("*.tex")))
    return [p for p in candidati if ha_documentclass(p)]


def trova_esempi() -> list[Path]:
    trovati: list[Path] = []
    for cartella in CARTELLE_ESEMPI:
        if (ROOT / cartella).is_dir():
            trovati.extend(p for p in sorted((ROOT / cartella).rglob("*.tex"))
                           if ha_documentclass(p))
    return trovati


def fuori_posto() -> list[Path]:
    """Documenti (.tex con \\documentclass) fuori da Candidatura/RTB/PB:
    non verrebbero né compilati né pubblicati. Succede, per esempio, con
    una cartella chiamata "rtb" invece di "RTB"."""
    trovati: list[Path] = []
    for voce in sorted(ROOT.iterdir()):
        if voce.name in NOMI_MILESTONE or voce.name in CARTELLE_SISTEMA \
                or voce.name.startswith("."):
            continue
        if voce.is_dir():
            trovati.extend(p for p in sorted(voce.rglob("*.tex")) if ha_documentclass(p))
        elif voce.suffix == ".tex" and ha_documentclass(voce):
            trovati.append(voce)
    return trovati


def avvisi_fuori_posto() -> list[str]:
    return [f"`{p.relative_to(ROOT).as_posix()}` è fuori dalle cartelle "
            f"{', '.join(NOMI_MILESTONE)} (scritte esattamente così): non viene "
            "compilato né pubblicato. Spostatelo dentro una di quelle cartelle."
            for p in fuori_posto()]


# --------------------------------------------------------------------------
#  Compilazione
# --------------------------------------------------------------------------
RIGA_ERRORE = re.compile(
    r"^(?P<file>.+?\.(?:tex|cls|sty|ldf|def|cfg|clo)):(?P<riga>\d+): (?P<msg>.*)$")


def percorso_leggibile(percorso: str, d: Documento) -> str:
    """Trasforma un percorso del log in uno relativo al repository."""
    p = Path(percorso)
    if not p.is_absolute():
        p = d.sorgente.parent / p
    try:
        return Path(os.path.normpath(p)).relative_to(ROOT).as_posix()
    except ValueError:
        return percorso


def estrai_errori(d: Documento, log: Path, uscita: str) -> list[str]:
    """Le righe utili del log: "file:riga: messaggio" e il testo incriminato."""
    righe = log.read_text(encoding="utf-8", errors="replace").splitlines() if log.exists() else []
    errori: list[str] = []
    for n, riga in enumerate(righe):
        # "ignored error": avviso innocuo di TeX Live 2025+ quando una tabella
        # lunga va a capo pagina; "Fatal error": ripete l'errore vero
        if "==> Fatal error occurred" in riga or "ignored error" in riga:
            continue
        m = RIGA_ERRORE.match(riga)
        if m:
            testo = f"{percorso_leggibile(m['file'], d)}:{m['riga']}: {m['msg']}"
        elif riga.startswith("! "):
            testo = riga
        else:
            continue
        if testo in errori:
            continue
        errori.append(testo)
        # la riga "l.12 ..." subito dopo mostra il punto esatto del testo
        for seguito in righe[n + 1:n + 8]:
            if re.match(r"^l\.\d+ ", seguito):
                errori.append("    " + seguito)
                break
    if not errori:  # niente nel log: mostro la fine dell'output di latexmk
        errori = [r for r in uscita.splitlines()
                  if r.strip() and "extra time" not in r and "not process it" not in r][-15:]
    return errori[:10]


def leggi_dipendenze(fls: Path) -> set[str]:
    """File del repository letti da LaTeX (dal file .fls di latexmk)."""
    trovati: set[str] = set()
    if not fls.exists():
        return trovati
    cartella = fls.parent
    for riga in fls.read_text(encoding="utf-8", errors="replace").splitlines():
        if riga.startswith("PWD "):
            cartella = Path(riga[4:])
        elif riga.startswith("INPUT "):
            p = Path(riga[6:])
            if not p.is_absolute():
                p = cartella / p
            try:
                rel = Path(os.path.realpath(p)).relative_to(ROOT)
            except ValueError:
                continue  # file di sistema (TeX Live)
            if rel.parts and rel.parts[0] not in ("build", "site"):
                trovati.add(rel.as_posix())
    return trovati


def compila(d: Documento) -> bool:
    outdir = BUILD / d.relativo.parent
    outdir.mkdir(parents=True, exist_ok=True)
    # latexmk parte dalla cartella del documento, esattamente come fa VS Code:
    # così \input{capitoli/...} e le immagini funzionano uguali dappertutto.
    comando = ["latexmk", "-r", str(LATEXMKRC), f"-outdir={outdir}", d.sorgente.name]
    ambiente = dict(os.environ, max_print_line="10000")  # errori su una riga sola
    esito = subprocess.run(comando, cwd=d.sorgente.parent, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", env=ambiente)
    d.dipendenze = leggi_dipendenze(outdir / f"{d.sorgente.stem}.fls")
    d.ok = esito.returncode == 0 and d.pdf_build.exists()
    if not d.ok:
        d.errori = estrai_errori(d, outdir / f"{d.sorgente.stem}.log",
                                 esito.stdout + esito.stderr)
    return d.ok


# --------------------------------------------------------------------------
#  Git
# --------------------------------------------------------------------------
def git(*argomenti_git: str) -> str:
    esito = subprocess.run(["git", *argomenti_git], cwd=ROOT, capture_output=True)
    if esito.returncode != 0:
        motivo = esito.stderr.decode("utf-8", "replace").strip()
        raise SystemExit(f"Errore di git ({' '.join(argomenti_git[:2])}): {motivo}")
    return esito.stdout.decode("utf-8", "replace")


def elenco_z(uscita: str) -> set[str]:
    return {p for p in uscita.split("\0") if p}


def file_cambiati(base: str, *filtro: str) -> set[str]:
    """File cambiati rispetto a `base` (-z: nomi con accenti senza sorprese)."""
    esito = subprocess.run(["git", "diff", "--name-only", "-z", *filtro, f"{base}...HEAD"],
                           cwd=ROOT, capture_output=True)
    if esito.returncode != 0:
        motivo = esito.stderr.decode("utf-8", "replace").strip()
        raise SystemExit(f"Errore: non riesco a confrontare con '{base}': {motivo}\n"
                         "Controllate che il ramo esista (per esempio con: git fetch origin).")
    return elenco_z(esito.stdout.decode("utf-8", "replace"))


def pdf_generati_nella_pr(base: str) -> list[str]:
    """PDF aggiunti o modificati dalla pull request che sono quelli generati
    dalla CI (stesso nome di un .tex della classe gpt accanto). Non vanno
    nella pull request: li rigenera la CI dopo il merge, e caricarli a mano
    crea conflitti. Un PDF con un altro nome (es. VE-...-firmato.pdf) va bene."""
    trovati = []
    for p in sorted(file_cambiati(base, "--diff-filter=AMR")):
        percorso = ROOT / p
        if percorso.suffix.lower() == ".pdf" and Path(p).parts[0] in NOMI_MILESTONE:
            tex = percorso.with_suffix(".tex")
            if tex.exists() and ha_documentclass(tex):
                trovati.append(p)
    return trovati


# --------------------------------------------------------------------------
#  PDF accanto ai .tex (solo CI, dopo il merge su main)
# --------------------------------------------------------------------------
def aggiorna_pdf_accanto(documenti: list[Documento]) -> list[str]:
    """Copia il PDF accanto al .tex solo se serve: il PDF non c'è ancora,
    oppure da quando è stato salvato l'ultima volta è cambiato un file da
    cui dipende (il .tex, un capitolo, un'immagine, la classe...).
    Così un merge non riscrive i PDF di tutti i documenti."""
    aggiornati: list[str] = []
    cambiati_dal: dict[str, set[str]] = {}
    for d in documenti:
        if d.esempio or not d.ok:
            continue
        rel = d.pdf_accanto.relative_to(ROOT).as_posix()
        ultimo = git("log", "-1", "--format=%H", "--", rel).strip()
        if d.pdf_accanto.exists() and ultimo:
            if ultimo not in cambiati_dal:
                cambiati_dal[ultimo] = elenco_z(git("diff", "--name-only", "-z", ultimo, "HEAD"))
            if not cambiati_dal[ultimo] & (d.dipendenze | {d.relativo.as_posix()}):
                continue   # niente di nuovo: il PDF salvato è ancora giusto
        shutil.copy2(d.pdf_build, d.pdf_accanto)
        git("add", "--force", "--", rel)    # --force: i PDF sono in .gitignore
        aggiornati.append(rel)

    # PDF rimasti orfani (il .tex è stato spostato o cancellato): si tolgono,
    # ma solo se li aveva salvati la CI. I PDF caricati da voi restano.
    salvati = elenco_z(git("ls-files", "-z", "--", *NOMI_MILESTONE))
    for rel in sorted(salvati):
        percorso = ROOT / rel
        if percorso.suffix.lower() != ".pdf" or percorso.with_suffix(".tex").exists():
            continue
        if git("log", "-1", "--format=%s", "--", rel).strip() == MESSAGGIO_BOT:
            git("rm", "--quiet", "--", rel)
            aggiornati.append(f"{rel} (tolto: il .tex non c'è più)")
    return aggiornati


# --------------------------------------------------------------------------
#  Sito
# --------------------------------------------------------------------------
def data_leggibile(iso: str) -> str:
    try:
        a, m, g = (int(x) for x in iso.split("-"))
        return f"{g} {MESI[m - 1]} {a}"
    except (ValueError, IndexError):
        return iso


def pdf_dello_stesso_documento(d: Documento) -> list[Path]:
    """Tutte le versioni di questo documento già presenti in site/."""
    cartella = d.pdf_sito.parent
    if not cartella.is_dir():
        return []
    schema = re.compile(re.escape(d.sorgente.stem) + r"(_v[0-9.]+)?\.pdf")
    return [p for p in cartella.iterdir() if schema.fullmatch(p.name)]


def copia_nel_sito(d: Documento) -> None:
    for vecchio in pdf_dello_stesso_documento(d):   # niente versioni vecchie
        vecchio.unlink()
    d.pdf_sito.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(d.pdf_build, d.pdf_sito)


def togli_dal_sito(d: Documento) -> None:
    """Se un documento non compila, il sito locale non mostra un PDF vecchio."""
    for vecchio in pdf_dello_stesso_documento(d):
        vecchio.unlink()


def scrivi_sito(documenti: list[Documento], voci_glossario=None) -> None:
    """La pagina del sito (index.html) la costruisce scripts/sito.py."""
    import sito    # sta nella stessa cartella di build.py
    sito.scrivi(documenti, root=ROOT, site=SITE, glossario=voci_glossario)


# --------------------------------------------------------------------------
#  Glossario (la logica è in scripts/glossario.py)
# --------------------------------------------------------------------------
def milestone_aperte() -> list[str]:
    """Le milestone non concluse secondo template/sito.toml: i controlli
    del Glossario non disturbano con i documenti già consegnati."""
    try:
        import sito
        stati = sito.carica_impostazioni(ROOT).get("milestone", {}) or {}
    except SystemExit:
        stati = {}
    return [m for m in NOMI_MILESTONE
            if str((stati.get(m) or {}).get("stato", "")).strip().lower() != "conclusa"]


def controlla_glossario(cambiati: set[str] | None):
    """cambiati = file della pull request (None = controlla tutto).
    Restituisce (glossario, esito)."""
    import glossario
    g = glossario.leggi(ROOT, NOMI_MILESTONE)
    aperte = milestone_aperte()
    tutti = [p for m in aperte if (ROOT / m).is_dir() for p in sorted((ROOT / m).rglob("*.tex"))]
    glossario_toccato = bool(g.cartella) and cambiati is not None and any(
        (ROOT / c).is_relative_to(g.cartella) for c in cambiati)
    if cambiati is None or glossario_toccato:
        da_controllare = tutti          # build completa, o PR che cambia il Glossario
    else:
        da_controllare = [p for p in tutti if p.relative_to(ROOT).as_posix() in cambiati]
    esito = glossario.controlla(g, ROOT, NOMI_MILESTONE, da_controllare,
                                completo=cambiati is None or glossario_toccato)
    return g, esito


# --------------------------------------------------------------------------
#  Riepiloghi (terminale, commento nella PR, pagina dell'Action)
# --------------------------------------------------------------------------
def riga_tabella(d: Documento) -> str:
    nota = " _(modello/esempio)_" if d.esempio else ""
    esito = "✅ compilato" if d.ok else "❌ errore"
    return f"| `{d.relativo.as_posix()}`{nota} | {d.versione or '—'} | {esito} |"


def blocchi_errori(falliti: list[Documento]) -> list[str]:
    righe: list[str] = []
    for d in falliti:
        righe += ["", f"**Errori in `{d.relativo.as_posix()}`:**", "```", *d.errori, "```"]
    return righe


def blocco_avvisi(avvisi: list[str]) -> list[str]:
    if not avvisi:
        return []
    return ["", "⚠️ **Da controllare** (non blocca nulla):", *[f"- {a}" for a in avvisi]]


def riepilogo_semplice(documenti: list[Documento], extra_avvisi: list[str]) -> str:
    righe = ["| Documento | Versione | Esito |", "| --- | --- | --- |"]
    righe += [riga_tabella(d) for d in documenti]
    righe += blocchi_errori([d for d in documenti if not d.ok])
    righe += blocco_avvisi([a for d in documenti for a in d.avvisi] + extra_avvisi)
    return "\n".join(righe)


def riepilogo_anteprima(toccati: list[Documento], falliti: list[Documento],
                        n_documenti: int, n_esempi: int,
                        pdf_vietati: list[str], extra_avvisi: list[str],
                        righe_glossario: list[str] | None = None,
                        glossario_rosso: bool = False) -> str:
    righe: list[str] = []
    if toccati:
        tabella = ["| Documento | Versione | Esito |", "| --- | --- | --- |"]
        tabella += [riga_tabella(d) for d in toccati]
        if len(toccati) > 8:   # elenco lungo (es. modifica alla classe): richiudibile
            righe += [f"<details><summary><b>{len(toccati)} documenti toccati da questa "
                      "pull request</b> (cliccate per vedere l'elenco)</summary>", "",
                      *tabella, "", "</details>"]
        else:
            righe += ["**Documenti toccati da questa pull request:**", "", *tabella]
    else:
        righe.append("Questa pull request non modifica nessun documento.")
    toccati_rel = {d.relativo for d in toccati}
    altri = [d for d in falliti if d.relativo not in toccati_rel]
    if altri:
        righe += ["", "⚠️ **Documenti NON toccati da questa pull request che però non compilano:**"]
        righe += [f"- `{d.relativo.as_posix()}`" for d in altri]
    righe += blocchi_errori(falliti)
    if pdf_vietati:
        righe += ["", "❌ **Questa pull request contiene PDF che crea da sola la CI.** "
                  "Il PDF accanto al `.tex` lo genera la CI dopo il merge: caricarlo a "
                  "mano crea conflitti. Cancellate questi file (dalla cartella sul "
                  "computer, poi commit e push; oppure sul sito di GitHub: aprite il "
                  "file nel vostro branch → ⋯ → *Delete file*). Dopo il merge la CI "
                  "li rigenera. Dettagli: GUIDA.md, sezione 7.",
                  *[f"- `{p}`" for p in pdf_vietati]]
    righe += blocco_avvisi([a for d in toccati for a in d.avvisi] + extra_avvisi)
    righe += righe_glossario or []
    if falliti:
        esito = f"{len(falliti)} con errori ❌"
    elif pdf_vietati:
        esito = "tutti compilati, ma ci sono PDF da togliere ❌"
    elif glossario_rosso:
        esito = "tutti compilati, ma il Glossario va sistemato ❌"
    else:
        esito = "nessun errore ✅"
    righe += ["", f"Controllo completo: compilati {n_documenti} documenti "
                  f"e {n_esempi} modelli/esempi, {esito}."]
    return "\n".join(righe)


def segnala(avvisi: list[str]) -> None:
    """Avvisi nel terminale e, nella CI, in evidenza nella pagina dell'Action."""
    for a in avvisi:
        testo = a.replace("`", "")
        print("Attenzione: " + testo, file=sys.stderr)
        if os.environ.get("GITHUB_ACTIONS"):
            print("::warning::" + testo)


def salva_riepilogo(testo: str) -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "riepilogo.md").write_text(testo + "\n", encoding="utf-8")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(testo + "\n")


def scrivi_output_github(**valori: str) -> None:
    """Valori letti dai passi successivi del workflow (steps.build.outputs.*)."""
    percorso = os.environ.get("GITHUB_OUTPUT")
    if percorso:
        with open(percorso, "a", encoding="utf-8") as f:
            for chiave, valore in valori.items():
                f.write(f"{chiave}={valore}\n")


# --------------------------------------------------------------------------
#  Modalità anteprima (pull request)
# --------------------------------------------------------------------------
def anteprima(base: str) -> int:
    cambiati = file_cambiati(base)
    pdf_vietati = pdf_generati_nella_pr(base)
    documenti = [leggi(p) for p in trova_documenti()]
    esempi = [leggi(p, esempio=True) for p in trova_esempi()]
    tutti = documenti + esempi
    for d in tutti:
        print(f"Compilo {d.relativo.as_posix()} ...", flush=True)
        compila(d)

    # toccato = il suo .tex è cambiato, oppure è cambiato un file che LaTeX
    # ha letto per compilarlo (capitoli, immagini, classe, dati del gruppo)
    toccati = [d for d in tutti
               if d.relativo.as_posix() in cambiati or d.dipendenze & cambiati]
    falliti = [d for d in tutti if not d.ok]

    shutil.rmtree(ANTEPRIMA, ignore_errors=True)
    pdf: list[Path] = []
    for d in toccati:
        if d.ok:
            destinazione = ANTEPRIMA / d.relativo.parent / d.nome_pdf
            destinazione.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(d.pdf_build, destinazione)
            pdf.append(destinazione)
    scrivi_output_github(
        quanti=str(len(pdf)),
        pdf=pdf[0].relative_to(ROOT).as_posix() if len(pdf) == 1 else "")

    # i documenti fuori posto si segnalano solo se li tocca questa PR
    extra = [a for a in avvisi_fuori_posto() if any(f"`{c}`" in a for c in cambiati)]

    # Glossario: termini marcati con \glo nei file della PR (tutti, se la PR
    # cambia il Glossario) confrontati con le voci \termine
    import glossario
    _, esito_g = controlla_glossario(cambiati)
    glossario_rosso = glossario.BLOCCANTE and bool(esito_g.bloccanti)

    testo = riepilogo_anteprima(toccati, falliti, len(documenti), len(esempi),
                                pdf_vietati, extra, esito_g.righe_markdown(), glossario_rosso)
    salva_riepilogo(testo)
    print()
    print(testo)
    return 1 if falliti or pdf_vietati or glossario_rosso else 0


# --------------------------------------------------------------------------
def main() -> int:
    for flusso in (sys.stdout, sys.stderr):   # emoji anche su console non UTF-8
        if hasattr(flusso, "reconfigure"):
            flusso.reconfigure(errors="replace")

    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file", nargs="*",
                   help="documenti o cartelle da compilare (predefinito: tutti)")
    p.add_argument("--esempi", action="store_true",
                   help="compila anche i modelli e gli esempi di template/")
    p.add_argument("--anteprima", metavar="BASE",
                   help="modalità pull request: compila tutto e riassume i documenti "
                        "toccati rispetto a BASE (es. origin/main)")
    p.add_argument("--pdf-accanto", action="store_true",
                   help="solo per la CI dopo il merge: salva nel repository il PDF "
                        "accanto a ogni .tex cambiato")
    p.add_argument("--list", action="store_true", help="elenca i documenti e termina")
    p.add_argument("--no-site", action="store_true", help="non generare il sito")
    p.add_argument("--clean", action="store_true", help="cancella build/ e site/ prima di iniziare")
    args = p.parse_args()

    if shutil.which("latexmk") is None and not args.list:
        print("Errore: latexmk non trovato. Installate TeX Live (vedi GUIDA.md).",
              file=sys.stderr)
        return 2

    if args.clean:
        shutil.rmtree(BUILD, ignore_errors=True)
        shutil.rmtree(SITE, ignore_errors=True)

    if args.anteprima:
        return anteprima(args.anteprima)

    pubblicabili = trova_documenti()
    da_pubblicare = set(pubblicabili)
    if args.file:
        scelti: list[Path] = []
        for f in args.file:
            percorso = Path(f).resolve()
            if percorso.is_dir() and (percorso == ROOT or ROOT in percorso.parents):
                dentro = [s for s in pubblicabili if percorso in s.parents]
                if not dentro:
                    print(f"Attenzione: nessun documento in {f}", file=sys.stderr)
                scelti.extend(dentro)
            elif percorso.is_file() and ROOT in percorso.parents:
                scelti.append(percorso)
            else:
                print(f"Errore: file o cartella non trovati nel repository: {f}",
                      file=sys.stderr)
                return 2
    else:
        scelti = pubblicabili + (trova_esempi() if args.esempi else [])

    documenti = [leggi(s, esempio=s not in da_pubblicare) for s in scelti]
    extra_avvisi = avvisi_fuori_posto()

    if args.list:
        for d in documenti:
            if d.esempio:
                dove = "(modello/esempio)"
            else:
                dove = f"{d.milestone} · {d.categoria} {d.visibilita}"
            versione = f"v{d.versione}" if d.versione else "—"
            print(f"{d.relativo.as_posix():56} {versione:9} {dove:28} {d.titolo}")
        segnala([a for d in documenti for a in d.avvisi] + extra_avvisi)
        return 0

    if not documenti:
        # Niente da compilare (es. repository appena creato, oppure .tex
        # ancora nelle cartelle vecchie): il sito si crea lo stesso, vuoto,
        # così la pubblicazione non si rompe.
        print("Nessun documento da compilare dentro " + ", ".join(NOMI_MILESTONE) + ".")
        segnala(extra_avvisi)
        if not args.no_site:
            scrivi_sito([])
        if args.pdf_accanto:
            scrivi_output_github(pdf_aggiornati="0", messaggio=MESSAGGIO_BOT)
        return 0

    for d in documenti:
        print(f"Compilo {d.relativo.as_posix()} ...", flush=True)
        compila(d)
        if d.esempio:
            continue
        if d.ok:
            copia_nel_sito(d)
        else:
            togli_dal_sito(d)

    # Glossario: controlli (solo avvisi, qui non blocca mai) e voci per il sito
    g, esito_g = controlla_glossario(None if not args.file else
                                     {Path(f).resolve().relative_to(ROOT).as_posix()
                                      for f in args.file if Path(f).resolve().is_file()})

    if not args.no_site:
        # l'indice elenca tutto ciò che c'è in site/, non solo questa esecuzione
        scrivi_sito([leggi(s) for s in pubblicabili], g)

    testo = riepilogo_semplice(documenti, extra_avvisi)
    if esito_g.righe_markdown():
        testo += "\n" + "\n".join(esito_g.righe_markdown())
    falliti = [d for d in documenti if not d.ok]

    if args.pdf_accanto and not falliti:
        aggiornati = aggiorna_pdf_accanto(documenti)
        testo += "\n\n" + ("**PDF salvati accanto ai sorgenti:**\n" +
                           "\n".join(f"- `{a}`" for a in aggiornati)
                           if aggiornati else "Nessun PDF da aggiornare nel repository.")
        scrivi_output_github(pdf_aggiornati=str(len(aggiornati)), messaggio=MESSAGGIO_BOT)

    salva_riepilogo(testo)
    print()
    print(testo)
    if falliti:
        print(f"\n{len(falliti)} documento/i con errori: leggete le righe qui sopra.",
              file=sys.stderr)
        return 1
    pubblicati = sum(1 for d in documenti if not d.esempio)
    print(f"\nFatto: {pubblicati} PDF in {SITE.relative_to(ROOT)}/ "
          f"(i file temporanei e i PDF di prova sono in {BUILD.relative_to(ROOT)}/)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
