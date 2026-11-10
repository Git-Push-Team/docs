#!/usr/bin/env python3
"""
registro.py -- il registro delle modifiche e la versione dei documenti,
scritti in automatico a partire dalle pull request.

Come funziona (GUIDA.md, sezione 5):

  - le righe \\modifica di un documento stanno in un file accanto al .tex,
    con lo stesso nome e ".registro.tex" in fondo:
        RTB/documenti/esterni/piano-di-progetto.registro.tex
    La classe gpt.cls lo legge da sola: nel .tex non si scrive più nulla;
  - dopo il merge di una pull request con un'ETICHETTA di versione, il bot
    aggiunge in cima al registro di ogni documento toccato una riga con:
        versione      la precedente aumentata secondo l'etichetta
        data          il giorno del merge
        autore        chi ha aperto la PR e chi vi ha fatto commit
        verificatore  chi ha approvato la PR (revisione "Approve")
        descrizione   la riga "Descrizione:" della PR (se manca, il titolo)
        approvatore   solo per l'approvazione dei documenti: il Responsabile
  - le etichette:
        correzione    0.2.0 -> 0.2.1
        contenuto     0.2.1 -> 0.3.0
        approvazione  0.3.0 -> 1.0.0   (nei documenti la mette il Responsabile)
    Senza etichetta il registro non cambia: utile per le correzioni minime.

Uso:

    python3 scripts/registro.py migra [FILE.tex ...]
        sposta le righe \\modifica scritte a mano nei .tex nel file
        .registro.tex accanto (senza argomenti: tutti i documenti).

    python3 scripts/registro.py aggiorna
        solo CI, dopo il merge su main: aggiunge le righe delle PR unite
        di recente che non sono ancora nel registro, e fa un commit.

    python3 scripts/registro.py anteprima --pr N [--scrivi]
        solo CI, nelle pull request: scrive in build/registro.md le righe
        che il bot aggiungerà al merge; con --scrivi le mette anche nei
        file .registro.tex della copia di lavoro, così il PDF di anteprima
        mostra già la versione nuova (non si salva nulla nel repository).

Per le prove automatiche: scripts/test_registro.py.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

try:                                    # Python 3.11 e successivi
    import tomllib
except ModuleNotFoundError:             # Python 3.9-3.10: serve solo al bot (in CI),
    try:                                # non per compilare i documenti
        import tomli as tomllib
    except ModuleNotFoundError:
        tomllib = None

ROOT = Path(__file__).resolve().parent.parent
MILESTONE = ("Candidatura", "RTB", "PB")
FUSO = ZoneInfo("Europe/Rome")

# etichetta -> quale numero di X.Y.Z aumenta. Se una PR ne ha più d'una
# vale la più "forte" (l'approvazione comprende le ultime modifiche).
ETICHETTE = {
    "approvazione": (0, "Approvazione: la versione passa al numero intero successivo (0.4.2 → 1.0.0)",
                     "0e8a16"),
    "contenuto": (1, "Contenuto nuovo: aumenta il numero centrale (0.2.1 → 0.3.0)", "1d76db"),
    "correzione": (2, "Correzione piccola: aumenta l'ultimo numero (0.2.0 → 0.2.1)", "fbca04"),
}

# quante pull request unite si riguardano a ogni esecuzione: così una
# esecuzione saltata o fallita viene recuperata da quella dopo
GIORNI_DA_CONTROLLARE = 21

MARCATORE_PR = "% PR #"                         # in fondo a ogni riga scritta dal bot
MARCATORE_COMMENTO = "<!-- registro-delle-modifiche -->"
MESSAGGIO_COMMIT = "Registro delle modifiche aggiornato dal bot [skip ci]"

INTESTAZIONE = """\
% =====================================================================
%  REGISTRO DELLE MODIFICHE di {nome}
%
%  Le righe le aggiunge il bot dopo il merge di una pull request con
%  un'etichetta di versione (correzione, contenuto, approvazione):
%  GUIDA.md, sezione 5. La riga più recente è in cima.
%  Si può correggere a mano (per esempio un refuso in una descrizione)
%  con una pull request SENZA etichetta. La classe legge questo file da
%  sola: nel .tex non serve scrivere nulla.
% =====================================================================
"""

PUNTATORE = """\
% Registro delle modifiche: le righe sono nel file
%     {file}
% accanto a questo, e le aggiunge il bot dopo il merge in base
% all'etichetta della pull request (GUIDA.md, sezione 5).
% Qui non si scrive nulla.
"""


# --------------------------------------------------------------------------
#  Lettura delle righe \modifica
# --------------------------------------------------------------------------
@dataclass
class Riga:
    versione: str
    data: str
    autore: str
    verificatore: str
    descrizione: str
    approvatore: str = ""
    inizio: int = 0          # posizione nel testo (per spostarla)
    fine: int = 0
    pr: int | None = None    # PR da cui l'ha scritta il bot

    def latex(self) -> str:
        appr = f"[{self.approvatore}]" if self.approvatore else ""
        coda = f"{MARCATORE_PR}{self.pr}" if self.pr else ""
        return (f"\\modifica{{{self.versione}}}{{{self.data}}}{{{self.autore}}}"
                f"{{{self.verificatore}}}{{{self.descrizione}}}{appr}{coda}")


def maschera_commenti(testo: str) -> str:
    """Sostituisce i commenti (da % non preceduto da \\ a fine riga) con
    spazi: le posizioni restano quelle del testo originale."""
    def via(m: re.Match) -> str:
        return " " * len(m.group(0))
    return "\n".join(re.sub(r"(?<!\\)%.*", via, r) for r in testo.split("\n"))


def _argomento(testo: str, i: int) -> tuple[str, int] | None:
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
    return testo[inizio:i - 1].strip(), i


def leggi_righe(testo: str, solo_preambolo: bool = True) -> list[Riga]:
    """Le righe \\modifica non commentate, nell'ordine in cui sono scritte."""
    mascherato = maschera_commenti(testo)
    fine_ricerca = len(testo)
    if solo_preambolo:
        m = re.search(r"\\begin\s*\{document\}", mascherato)
        fine_ricerca = m.start() if m else len(testo)
    righe = []
    for m in re.finditer(r"\\modifica(?![A-Za-z@])", mascherato[:fine_ricerca]):
        i, valori = m.end(), []
        while len(valori) < 5:
            arg = _argomento(mascherato, i)
            if arg is None:
                break
            valori.append(testo[i:arg[1]].strip()[1:-1].strip())
            i = arg[1]
        if len(valori) < 5:
            continue
        approvatore = ""
        ma = re.match(r"[ \t]*\[([^\]]*)\]", mascherato[i:])
        if ma:
            approvatore = ma.group(1).strip()
            i += ma.end()
        pr = None
        resto = testo[i:testo.find("\n", i) if "\n" in testo[i:] else len(testo)]
        mp = re.match(r"\s*" + re.escape(MARCATORE_PR) + r"(\d+)", resto)
        if mp:
            pr = int(mp.group(1))
        righe.append(Riga(*valori, approvatore=approvatore, inizio=m.start(), fine=i, pr=pr))
    return righe


def file_registro(tex: Path) -> Path:
    return tex.with_name(tex.stem + ".registro.tex")


def righe_documento(tex: Path) -> list[Riga]:
    """Tutte le righe di un documento, come le vede la classe: prima quelle
    scritte a mano nel .tex (se ce ne sono ancora), poi quelle del file
    .registro.tex. La prima è la versione attuale."""
    righe = leggi_righe(tex.read_text(encoding="utf-8"))
    reg = file_registro(tex)
    if reg.exists():
        righe += leggi_righe(reg.read_text(encoding="utf-8"), solo_preambolo=False)
    return righe


def testo_registro(tex: Path) -> str:
    """Il contenuto del file .registro.tex (vuoto se non c'è)."""
    reg = file_registro(tex)
    return reg.read_text(encoding="utf-8") if reg.exists() else ""


# --------------------------------------------------------------------------
#  Spostamento delle righe scritte a mano nel file .registro.tex
# --------------------------------------------------------------------------
def migra(tex: Path) -> bool:
    """Sposta le righe \\modifica del preambolo di `tex` in cima al file
    .registro.tex (le righe a mano sono le più recenti). Restituisce True
    se ha cambiato qualcosa. Il testo delle righe resta identico."""
    testo = tex.read_text(encoding="utf-8")
    righe = leggi_righe(testo)
    if not righe:
        return False
    reg = file_registro(tex)
    spostate = [testo[r.inizio:r.fine] for r in righe]
    esistente = reg.read_text(encoding="utf-8") if reg.exists() else ""
    if not esistente:
        esistente = INTESTAZIONE.format(nome=tex.name)
    corpo_vecchio = esistente.split("\n")
    # le nuove righe vanno dopo l'intestazione (commenti iniziali)
    n = 0
    while n < len(corpo_vecchio) and corpo_vecchio[n].startswith("%"):
        n += 1
    nuovo = corpo_vecchio[:n] + spostate + [r for r in corpo_vecchio[n:]]
    reg.write_text("\n".join(nuovo).rstrip("\n") + "\n", encoding="utf-8")

    # dal .tex: via le righe; al posto della prima, il puntatore al file
    righe_testo = testo.split("\n")
    def numero_riga(pos: int) -> int:
        return testo.count("\n", 0, pos)
    da_togliere = set()
    for r in righe:
        a, b = numero_riga(r.inizio), numero_riga(r.fine)
        prima = righe_testo[a][:r.inizio - (testo.rfind("\n", 0, r.inizio) + 1)]
        dopo_fine = testo.find("\n", r.fine)
        dopo = testo[r.fine:dopo_fine if dopo_fine != -1 else len(testo)]
        if prima.strip() or (dopo.strip() and not dopo.strip().startswith("%")):
            raise SystemExit(f"{tex}: la riga \\modifica {r.versione} è sulla stessa riga di "
                             "altro testo: spostatela a mano.")
        da_togliere.update(range(a, b + 1))
    primo = min(da_togliere)
    # il vecchio commento sopra le righe ("Registro delle modifiche ...
    # la riga più recente va in cima", con la sintassi di \modifica) ora
    # direbbe il contrario di come si lavora: lo togliamo
    k = primo - 1
    blocco = []
    while k >= 0 and (righe_testo[k].lstrip().startswith("%") or not righe_testo[k].strip()):
        blocco.append(k)
        k -= 1
    titolo = next((j for j in blocco if re.search(r"registro\s+delle\s+modifiche",
                                                  righe_testo[j], re.I)), None)
    if titolo is not None:
        inizio = titolo
        if inizio - 1 in blocco and re.fullmatch(r"\s*%\s*[-=]{10,}\s*", righe_testo[inizio - 1]):
            inizio -= 1
        da_togliere.update(j for j in range(inizio, primo) if righe_testo[j].strip())
        primo = inizio
    puntatore = PUNTATORE.format(file=reg.name).rstrip("\n").split("\n")
    gia = any("accanto a questo, e le aggiunge il bot" in r for r in righe_testo)
    risultato = []
    for i, riga in enumerate(righe_testo):
        if i == primo and not gia:
            risultato += puntatore
        if i not in da_togliere:
            risultato.append(riga)
    tex.write_text("\n".join(risultato), encoding="utf-8")
    return True


# --------------------------------------------------------------------------
#  Versioni
# --------------------------------------------------------------------------
def versione_successiva(versione: str, etichetta: str) -> str:
    parti = [int(x) for x in versione.split(".")] if versione else [0, 0, 0]
    indice = ETICHETTE[etichetta][0]
    parti[indice] += 1
    for j in range(indice + 1, 3):
        parti[j] = 0
    return ".".join(str(p) for p in parti)


def etichetta_della_pr(nomi: list[str]) -> str | None:
    """La più forte tra le etichette di versione (None = nessuna)."""
    presenti = [n.strip().lower() for n in nomi]
    for nome in ETICHETTE:            # in ordine di forza
        if nome in presenti:
            return nome
    return None


def escape_latex(testo: str) -> str:
    sostituzioni = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
                    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
                    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    testo = re.sub(r"\s+", " ", testo.replace("`", "")).strip()
    return "".join(sostituzioni.get(c, c) for c in testo)


def descrizione_della_pr(corpo: str | None, titolo: str) -> str:
    """La riga "Descrizione: ..." della PR; se manca o è vuota, il titolo."""
    testo = re.sub(r"<!--.*?-->", "", corpo or "", flags=re.S)
    m = re.search(r"^[ \t>*_-]*Descrizione(?: per il registro)?[ \t*_]*:[ \t*_]*(.+?)\s*$",
                  testo, flags=re.M | re.I)
    scelta = m.group(1).strip() if m and m.group(1).strip() else titolo
    return escape_latex(scelta).rstrip(" .")


# --------------------------------------------------------------------------
#  Documenti toccati da una pull request
# --------------------------------------------------------------------------
def ha_documentclass(p: Path) -> bool:
    try:
        return "\\documentclass" in maschera_commenti(p.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return False


def tipo_documento(tex: Path) -> str:
    """documento, lettera o verbale (come build.py)."""
    m = re.search(r"\\documentclass\s*\[([^\]]*)\]\s*\{gpt\}",
                  maschera_commenti(tex.read_text(encoding="utf-8")))
    opzioni = [o.replace(" ", "") for o in m.group(1).split(",")] if m else []
    if "documento" in opzioni:
        return "documento"
    if "lettera" in opzioni:
        return "lettera"
    return "verbale"


def documenti_toccati(file_cambiati: list[str], root: Path = ROOT) -> list[Path]:
    """I documenti (.tex con \\documentclass in Candidatura/RTB/PB) toccati:
    il .tex stesso, oppure un file nella sua cartella o sotto (capitoli,
    immagini), se quella cartella contiene un solo documento."""
    trovati: list[Path] = []
    def aggiungi(p: Path) -> None:
        if p not in trovati:
            trovati.append(p)
    for rel in file_cambiati:
        p = root / rel
        parti = Path(rel).parts
        if not parti or parti[0] not in MILESTONE or p.name.endswith(".registro.tex"):
            continue
        if p.suffix == ".pdf":
            continue
        if p.suffix == ".tex" and p.exists() and ha_documentclass(p):
            aggiungi(p)
            continue
        cartella = p.parent
        while cartella != root and cartella.is_relative_to(root / parti[0]):
            documenti = [d for d in sorted(cartella.glob("*.tex")) if ha_documentclass(d)]
            if len(documenti) == 1:
                aggiungi(documenti[0])
                break
            if len(documenti) > 1:
                break           # cartella con più documenti (verbali): ambiguo
            cartella = cartella.parent
    return trovati


# --------------------------------------------------------------------------
#  Membri e Responsabili (da pianificazione.toml del repository .github)
# --------------------------------------------------------------------------
@dataclass
class Gruppo:
    github: dict[str, str]                       # username (minuscolo) -> chiave
    sprint: list[tuple[date, date, list[str]]]   # inizio, fine, responsabili

    def chiave(self, login: str | None) -> str | None:
        return self.github.get((login or "").lower())

    def responsabili(self, giorno: date) -> list[str] | None:
        """Chiavi dei Responsabili dello sprint di quel giorno (None se il
        giorno non è in nessuno sprint)."""
        for inizio, fine, resp in self.sprint:
            if inizio <= giorno <= fine:
                return resp
        return None


def carica_gruppo(percorso: str | os.PathLike | None) -> Gruppo:
    percorso = percorso or os.environ.get("PIANIFICAZIONE") or ".gestione/gestione/pianificazione.toml"
    if tomllib is None:
        raise OSError("per leggere pianificazione.toml serve Python 3.11 o più recente "
                      "(oppure: pip install tomli)")
    dati = tomllib.loads(Path(percorso).read_text(encoding="utf-8"))
    github = {str(v["github"]).lower(): k for k, v in (dati.get("membri") or {}).items()
              if isinstance(v, dict) and v.get("github")}
    sprint = []
    for s in dati.get("sprint") or []:
        resp = [k for k, ruoli in (s.get("ruoli") or {}).items()
                if any(str(r).lower() == "responsabile" for r in (ruoli or {}))]
        sprint.append((s["inizio"], s["fine"], resp))
    return Gruppo(github, sprint)


# --------------------------------------------------------------------------
#  GitHub (solo libreria standard)
# --------------------------------------------------------------------------
class GitHub:
    def __init__(self, token: str | None = None, repo: str | None = None):
        self.token = token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
        self.repo = repo or os.environ.get("GITHUB_REPOSITORY", "")
        if not self.token or not self.repo:
            raise SystemExit("Servono GH_TOKEN e GITHUB_REPOSITORY.")

    def _richiesta(self, metodo: str, url: str, dati=None):
        if not url.startswith("http"):
            url = f"https://api.github.com{url}"
        corpo = json.dumps(dati).encode() if dati is not None else None
        req = urllib.request.Request(url, data=corpo, method=metodo, headers={
            "Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "registro-gpt"})
        with urllib.request.urlopen(req, timeout=60) as r:
            testo = r.read().decode()
            return (json.loads(testo) if testo else None), r.headers.get("Link", "")

    def get(self, percorso: str, tutte: bool = True):
        url, risultati = percorso, []
        while url:
            dati, link = self._richiesta("GET", url)
            if not tutte or not isinstance(dati, list):
                return dati
            risultati += dati
            m = re.search(r'<([^>]+)>;\s*rel="next"', link or "")
            url = m.group(1) if m else None
        return risultati

    def post(self, percorso: str, dati):
        return self._richiesta("POST", percorso, dati)[0]

    def patch(self, percorso: str, dati):
        return self._richiesta("PATCH", percorso, dati)[0]

    # -- dati di una PR --------------------------------------------------
    def pr(self, numero: int) -> dict:
        return self.get(f"/repos/{self.repo}/pulls/{numero}", tutte=False)

    def pr_unite(self, giorni: int) -> list[dict]:
        limite = datetime.now(FUSO) - timedelta(days=giorni)
        trovate = []
        url = f"/repos/{self.repo}/pulls?state=closed&base=main&sort=updated&direction=desc&per_page=50"
        for pr in self.get(url, tutte=False) or []:
            if pr.get("merged_at") and _quando(pr["merged_at"]) >= limite:
                trovate.append(pr)
        return sorted(trovate, key=lambda p: p["merged_at"])

    def file(self, numero: int) -> list[str]:
        voci = self.get(f"/repos/{self.repo}/pulls/{numero}/files?per_page=100")
        nomi = []
        for v in voci:
            nomi.append(v["filename"])
            if v.get("previous_filename"):
                nomi.append(v["previous_filename"])
        return nomi

    def revisioni(self, numero: int) -> list[dict]:
        return self.get(f"/repos/{self.repo}/pulls/{numero}/reviews?per_page=100")

    def commit(self, numero: int) -> list[dict]:
        return self.get(f"/repos/{self.repo}/pulls/{numero}/commits?per_page=100")

    def eventi(self, numero: int) -> list[dict]:
        return self.get(f"/repos/{self.repo}/issues/{numero}/events?per_page=100")

    def commenta(self, numero: int, testo: str, marcatore: str = MARCATORE_COMMENTO) -> None:
        """Un solo commento del bot per PR (riconosciuto dal marcatore):
        se c'è già lo aggiorna, altrimenti lo crea."""
        corpo = f"{marcatore}\n{testo}"
        for c in self.get(f"/repos/{self.repo}/issues/{numero}/comments?per_page=100"):
            if marcatore in (c.get("body") or ""):
                if c["body"].strip() != corpo.strip():
                    self.patch(f"/repos/{self.repo}/issues/comments/{c['id']}", {"body": corpo})
                return
        self.post(f"/repos/{self.repo}/issues/{numero}/comments", {"body": corpo})


def _quando(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(FUSO)


def _bot(login: str | None) -> bool:
    return not login or login.endswith("[bot]")


# --------------------------------------------------------------------------
#  Dalla pull request alla riga del registro
# --------------------------------------------------------------------------
@dataclass
class Proposta:
    documento: Path
    riga: Riga | None
    etichetta: str
    problemi: list[str] = field(default_factory=list)


def approvatori(revisioni: list[dict], autore_pr: str) -> list[str]:
    """Login di chi ha approvato: per ogni persona conta l'ultima revisione
    che approva, chiede modifiche o viene annullata."""
    ultimo: dict[str, str] = {}
    for r in revisioni:
        login = (r.get("user") or {}).get("login")
        stato = r.get("state")
        if _bot(login) or login == autore_pr:
            continue
        if stato in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED"):
            ultimo[login] = stato
    return [l for l, s in ultimo.items() if s == "APPROVED"]


def autori(pr: dict, commit: list[dict], esclusi: set[str]) -> list[str]:
    """Login di chi ha aperto la PR e di chi vi ha fatto commit (anche come
    co-autore), tranne bot e verificatori."""
    trovati: list[str] = []
    def aggiungi(login: str | None) -> None:
        if login and not _bot(login) and login not in esclusi and login not in trovati:
            trovati.append(login)
    aggiungi((pr.get("user") or {}).get("login"))
    for c in commit:
        aggiungi((c.get("author") or {}).get("login"))
        for email in re.findall(r"^Co-authored-by:.*<([^>]+)>", (c.get("commit") or {}).get("message", ""),
                                flags=re.M | re.I):
            m = re.match(r"(?:\d+\+)?([^@]+)@users\.noreply\.github\.com", email.strip(), re.I)
            if m:
                aggiungi(m.group(1))
    return trovati


def ultimo_etichettatore(eventi: list[dict], etichetta: str) -> tuple[str | None, datetime | None]:
    chi, quando = None, None
    for e in eventi:
        if e.get("event") == "labeled" and ((e.get("label") or {}).get("name", "").lower() == etichetta):
            chi, quando = (e.get("actor") or {}).get("login"), _quando(e["created_at"])
    return chi, quando


def chiavi(logins: list[str], gruppo: Gruppo, problemi: list[str], ruolo: str) -> str:
    trovate = []
    for l in logins:
        k = gruppo.chiave(l)
        if k:
            trovate.append(k)
        else:
            problemi.append(f"`{l}` ({ruolo}) non è tra i membri di `pianificazione.toml`: "
                            "non compare nel registro.")
    return ", ".join(trovate) if trovate else "--"


def proponi(pr: dict, file: list[str], revisioni: list[dict], commit: list[dict],
            eventi: list[dict], gruppo: Gruppo, root: Path = ROOT,
            giorno: date | None = None) -> list[Proposta]:
    """Le righe da aggiungere per una PR (una per documento toccato)."""
    etichetta = etichetta_della_pr([l["name"] for l in pr.get("labels") or []])
    if not etichetta:
        return []
    autore_pr = (pr.get("user") or {}).get("login")
    verificatori_login = approvatori(revisioni, autore_pr)
    autori_login = autori(pr, commit, set(verificatori_login))
    chi_approva, quando_approva = (ultimo_etichettatore(eventi, "approvazione")
                                   if etichetta == "approvazione" else (None, None))
    if giorno is None:
        momento = _quando(pr["merged_at"]) if pr.get("merged_at") else datetime.now(FUSO)
        if quando_approva and quando_approva > momento:
            momento = quando_approva       # etichetta messa dopo il merge
        giorno = momento.date()
    descrizione = descrizione_della_pr(pr.get("body"), pr.get("title", ""))

    proposte = []
    for doc in documenti_toccati(file, root):
        problemi: list[str] = []
        tipo = tipo_documento(doc)
        nome = doc.relative_to(root).as_posix()
        if tipo == "lettera":
            continue                       # le lettere non hanno registro
        righe = righe_documento(doc)
        attuale = righe[0] if righe else None
        versione = versione_successiva(attuale.versione if attuale else "", etichetta)
        data = giorno.isoformat()
        if attuale and attuale.data > data:
            data = attuale.data
        autore = chiavi(autori_login, gruppo, problemi, "autore")
        verificatore = chiavi(verificatori_login, gruppo, problemi, "verificatore")
        if verificatore == "--":
            problemi.append("nessun membro ha approvato la PR: la riga ha `--` come verificatore.")
        approvatore = ""
        if etichetta == "approvazione" and tipo == "documento":
            k = gruppo.chiave(chi_approva)
            resp = gruppo.responsabili(giorno)
            if not k:
                problemi.append("l'etichetta `approvazione` deve metterla il Responsabile: "
                                "non trovo chi l'ha messa tra i membri. Riga non aggiunta.")
                proposte.append(Proposta(doc, None, etichetta, problemi))
                continue
            if resp is None or not resp:
                problemi.append("non posso controllare che l'etichetta `approvazione` l'abbia messa il "
                                "Responsabile: in `pianificazione.toml` lo sprint di oggi non ha un "
                                f"Responsabile. Ho registrato `{k}` come approvatore.")
            elif k not in resp:
                problemi.append(f"l'etichetta `approvazione` l'ha messa `{k}`, ma il Responsabile "
                                f"dello sprint è `{', '.join(resp) or 'nessuno'}`. Riga non aggiunta: "
                                "il Responsabile tolga e rimetta l'etichetta (anche a PR chiusa), "
                                "poi rilanciate *Pubblica il sito* dalla scheda Actions.")
                proposte.append(Proposta(doc, None, etichetta, problemi))
                continue
            approvatore = k
        riga = Riga(versione, data, autore, verificatore, descrizione, approvatore, pr=pr["number"])
        proposte.append(Proposta(doc, riga, etichetta, problemi))
        _ = nome
    return proposte


def gia_registrata(doc: Path, numero: int) -> bool:
    return any(r.pr == numero for r in righe_documento(doc))


def aggiungi_riga(doc: Path, riga: Riga) -> None:
    """Sposta le eventuali righe a mano e mette `riga` in cima al registro."""
    migra(doc)
    reg = file_registro(doc)
    esistente = reg.read_text(encoding="utf-8") if reg.exists() else INTESTAZIONE.format(nome=doc.name)
    righe = esistente.rstrip("\n").split("\n")
    n = 0
    while n < len(righe) and righe[n].startswith("%"):
        n += 1
    righe.insert(n, riga.latex())
    reg.write_text("\n".join(righe) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
#  Comandi
# --------------------------------------------------------------------------
def git(*args: str, root: Path = ROOT) -> str:
    esito = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    if esito.returncode != 0:
        raise SystemExit(f"git {' '.join(args[:2])}: {esito.stderr.strip()}")
    return esito.stdout


def scrivi_riepilogo(testo: str) -> None:
    print(testo)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(testo + "\n")


def tabella(proposte: list[Proposta], root: Path = ROOT) -> list[str]:
    righe = ["| Documento | Versione | Autore | Verificatore | Descrizione |",
             "| --- | --- | --- | --- | --- |"]
    for p in proposte:
        nome = p.documento.relative_to(root).as_posix()
        if p.riga:
            r = p.riga
            appr = f" (approvatore: {r.approvatore})" if r.approvatore else ""
            descr = r.descrizione.replace("|", "\\|")
            righe.append(f"| `{nome}` | **{r.versione}**{appr} | {r.autore} | {r.verificatore} | {descr} |")
        else:
            righe.append(f"| `{nome}` | — | | | riga non aggiunta |")
    return righe


def comando_aggiorna(gh: GitHub, gruppo: Gruppo, root: Path = ROOT,
                     giorni: int = GIORNI_DA_CONTROLLARE, commit: bool = True) -> int:
    scritte: list[str] = []
    resoconto: list[str] = ["### 📝 Registro delle modifiche", ""]
    for pr in gh.pr_unite(giorni):
        etichetta = etichetta_della_pr([l["name"] for l in pr.get("labels") or []])
        if not etichetta:
            continue
        numero = pr["number"]
        file = gh.file(numero)
        docs = [d for d in documenti_toccati(file, root) if not gia_registrata(d, numero)]
        if not docs:
            continue
        proposte = proponi(pr, file, gh.revisioni(numero), gh.commit(numero), gh.eventi(numero),
                           gruppo, root)
        proposte = [p for p in proposte if p.documento in docs]
        for p in proposte:
            if p.riga:
                aggiungi_riga(p.documento, p.riga)
                for f in (p.documento, file_registro(p.documento)):
                    git("add", "--", f.relative_to(root).as_posix(), root=root)
                scritte.append(f"{p.documento.stem} v{p.riga.versione}")
        resoconto += [f"**PR #{numero}** — {pr.get('title', '')} (etichetta `{etichetta}`)", "",
                      *tabella(proposte, root), ""]
        problemi = [f"- `{p.documento.relative_to(root).as_posix()}`: {x}" for p in proposte for x in p.problemi]
        resoconto += problemi + ([""] if problemi else [])
        # il commento della PR (quello dell'anteprima) diventa il resoconto finale
        testo = ["### 📝 Registro delle modifiche", "",
                 f"Dopo il merge il bot ha registrato (etichetta `{etichetta}`):", "",
                 *tabella(proposte, root)]
        if problemi:
            testo += ["", "⚠️ **Da sistemare:**", *problemi]
        try:
            gh.commenta(numero, "\n".join(testo))
        except (urllib.error.URLError, OSError) as e:
            print(f"Commento non riuscito sulla PR #{numero}: {e}", file=sys.stderr)
    if not scritte:
        resoconto.append("Nessuna riga nuova: le PR unite di recente senza etichetta di versione "
                         "non cambiano il registro.")
    elif commit:
        git("-c", "user.name=github-actions[bot]",
            "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
            "commit", "--quiet", "-m", f"{MESSAGGIO_COMMIT}\n\n" + "\n".join(scritte), root=root)
    scrivi_riepilogo("\n".join(resoconto))
    return 0


def comando_anteprima(gh: GitHub, gruppo: Gruppo | None, numero: int, scrivi: bool,
                      root: Path = ROOT, uscita: Path | None = None,
                      commenta: bool = False) -> int:
    pr = gh.pr(numero)
    etichetta = etichetta_della_pr([l["name"] for l in pr.get("labels") or []])
    file = gh.file(numero)
    docs = documenti_toccati(file, root)
    a_mano = [d for d in docs if leggi_righe(d.read_text(encoding="utf-8"))]
    righe = ["### 📝 Registro delle modifiche", ""]
    if not docs:
        righe.append("Questa pull request non tocca documenti: il registro non cambia.")
    elif not etichetta:
        righe += ["Nessuna etichetta di versione: dopo il merge **il registro non cambia** "
                  "(va bene solo per correzioni minime, come un refuso nel codice LaTeX).", "",
                  "Per registrare la modifica, a destra in *Labels* scegliete:",
                  *[f"- `{n}`: {d}" for n, (_, d, _c) in ETICHETTE.items()]]
    elif gruppo is None:
        righe.append(f"Etichetta `{etichetta}`: non riesco a leggere `pianificazione.toml`, "
                     "quindi non posso mostrare l'anteprima delle righe.")
    else:
        proposte = proponi(pr, file, gh.revisioni(numero), gh.commit(numero), gh.eventi(numero),
                           gruppo, root, giorno=datetime.now(FUSO).date())
        righe += [f"Etichetta `{etichetta}`: dopo il merge il bot aggiungerà queste righe "
                  "(il verificatore è chi approva la PR; la data sarà quella del merge).", "",
                  *tabella(proposte, root)]
        problemi = [f"- `{p.documento.relative_to(root).as_posix()}`: {x}"
                    for p in proposte for x in p.problemi]
        if problemi:
            righe += ["", "⚠️ **Da controllare** (non blocca nulla):", *problemi]
        if not re.search(r"^[ \t>*_-]*Descrizione[^:\n]*:[ \t*_]*\S", re.sub(r"<!--.*?-->", "", pr.get("body") or "", flags=re.S), re.M | re.I):
            righe += ["", "ℹ️ Nella descrizione della PR manca la riga `Descrizione: ...`: "
                      "nel registro andrà il titolo della PR."]
        if scrivi:
            for p in proposte:
                if p.riga:
                    aggiungi_riga(p.documento, p.riga)
    if a_mano:
        righe += ["", "ℹ️ Righe `\\modifica` scritte a mano nel `.tex` di "
                  + ", ".join(f"`{d.name}`" for d in a_mano)
                  + ": non servono più. Toglietele, oppure lasciatele: al merge il bot le "
                  "sposta nel file `.registro.tex`."]
    testo = "\n".join(righe)
    if commenta:
        try:
            gh.commenta(numero, testo)
        except (urllib.error.URLError, OSError) as e:
            print(f"Commento non riuscito: {e}", file=sys.stderr)
    destinazione = uscita or (root / "build" / "registro.md")
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    destinazione.write_text(testo + "\n", encoding="utf-8")
    print(testo)
    return 0


def comando_etichette(gh: GitHub) -> int:
    """Crea le etichette di versione nel repository, se mancano."""
    esistenti = {l["name"].lower() for l in gh.get(f"/repos/{gh.repo}/labels?per_page=100")}
    for nome, (_, descrizione, colore) in ETICHETTE.items():
        if nome not in esistenti:
            gh.post(f"/repos/{gh.repo}/labels",
                    {"name": nome, "color": colore, "description": descrizione[:100]})
            print(f"Creata l'etichetta {nome}")
    return 0


def comando_migra(file: list[str], root: Path = ROOT) -> int:
    if file:
        documenti = [Path(f).resolve() for f in file]
    else:
        documenti = [p for m in MILESTONE if (root / m).is_dir()
                     for p in sorted((root / m).rglob("*.tex")) if ha_documentclass(p)]
    for d in documenti:
        if migra(d):
            print(f"Spostato il registro di {d.relative_to(root).as_posix()} "
                  f"in {file_registro(d).name}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comando", required=True)
    m = sub.add_parser("migra")
    m.add_argument("file", nargs="*")
    sub.add_parser("aggiorna")
    sub.add_parser("etichette")
    a = sub.add_parser("anteprima")
    a.add_argument("--pr", type=int, required=True)
    a.add_argument("--scrivi", action="store_true")
    a.add_argument("--commenta", action="store_true")
    args = p.parse_args()

    if args.comando == "migra":
        return comando_migra(args.file)
    gh = GitHub()
    if args.comando == "etichette":
        return comando_etichette(gh)
    try:
        gruppo = carica_gruppo(None)
    except (OSError, ValueError, KeyError) as e:     # TOMLDecodeError è un ValueError
        if args.comando == "aggiorna":
            scrivi_riepilogo(f"### 📝 Registro delle modifiche\n\n❌ Non riesco a leggere "
                             f"`pianificazione.toml` ({e}): nessuna riga aggiunta. Le PR verranno "
                             "registrate alla prossima esecuzione.")
            print(f"::warning::Registro non aggiornato: pianificazione.toml illeggibile ({e})")
            return 0
        gruppo = None
    if args.comando == "aggiorna":
        return comando_aggiorna(gh, gruppo)
    return comando_anteprima(gh, gruppo, args.pr, args.scrivi, commenta=args.commenta)


if __name__ == "__main__":
    sys.exit(main())
