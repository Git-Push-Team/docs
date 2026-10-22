"""
sito.py -- costruisce la pagina del sito (site/index.html).

Lo chiama build.py dopo aver compilato i documenti: non serve lanciarlo
a mano. Cosa mostra la pagina:

  - in alto il "grafo" delle milestone (Candidatura -> RTB -> PB), con un
    pallino per ogni verbale, che porta alle sezioni;
  - la milestone in corso: lettera di presentazione in evidenza, documenti
    esterni e interni con l'anteprima della prima pagina, verbali;
  - le diapositive (PDF in <Milestone>/diapositive/);
  - l'archivio delle milestone precedenti;
  - il gruppo (membri, capitolato) e i contatti.

Le impostazioni che non stanno nei documenti (stato delle milestone, link
extra, account GitHub) sono in template/sito.toml.
"""

from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
        "agosto", "settembre", "ottobre", "novembre", "dicembre"]

MILESTONE = [
    ("Candidatura", "Candidatura"),
    ("RTB", "Requirements and Technology Baseline"),
    ("PB", "Product Baseline"),
]
STATI = ("da iniziare", "in corso", "conclusa")

e = html.escape


# --------------------------------------------------------------------------
#  Dati: impostazioni, membri, file
# --------------------------------------------------------------------------
def carica_impostazioni(root: Path) -> dict:
    percorso = root / "template" / "sito.toml"
    if not percorso.exists():
        return {}
    try:
        import tomllib                      # Python 3.11+
    except ModuleNotFoundError:
        try:
            import tomli as tomllib         # pip install tomli (Python 3.9-3.10)
        except ModuleNotFoundError:
            print("Attenzione: con Python più vecchio del 3.11 il sito usa le "
                  "impostazioni predefinite (template/sito.toml ignorato).")
            return {}
    try:
        return tomllib.loads(percorso.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as errore:
        raise SystemExit(f"Errore in template/sito.toml: {errore}\n"
                         "Controllate virgolette e parentesi nella riga indicata.")


def leggi_gruppo(root: Path) -> dict:
    """Nome, numero, email, anno e membri da template/dati-gruppo.tex."""
    gruppo = {"nome": "Git Push Team", "numero": "", "email": "", "anno": "",
              "membri": []}
    percorso = root / "template" / "dati-gruppo.tex"
    if not percorso.exists():
        return gruppo
    testo = "\n".join(re.sub(r"(?<!\\)%.*", "", r)
                      for r in percorso.read_text(encoding="utf-8").splitlines())
    for chiave, comando in (("nome", "nomegruppo"), ("numero", "numerogruppo"),
                            ("email", "emailgruppo"), ("anno", "annoaccademico")):
        m = re.search(r"\\" + comando + r"\{([^}]*)\}", testo)
        if m:
            gruppo[chiave] = m.group(1).strip()
    gruppo["membri"] = [{"chiave": k, "nome": n}
                        for k, n, _ in re.findall(r"\\membro\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}", testo)]
    return gruppo


def anteprima_pdf(pdf: Path, png: Path) -> bool:
    """Immagine della prima pagina (serve pdftoppm, del pacchetto poppler).
    Se manca, il sito mostra un riquadro al posto dell'anteprima."""
    if png.exists() and png.stat().st_mtime >= pdf.stat().st_mtime:
        return True
    if shutil.which("pdftoppm") is None:
        return False
    esito = subprocess.run(["pdftoppm", "-png", "-r", "72", "-f", "1", "-l", "1",
                            "-singlefile", str(pdf), str(png.with_suffix(""))],
                           capture_output=True)
    return esito.returncode == 0 and png.exists()


def data_lunga(iso: str) -> str:
    try:
        a, m, g = (int(x) for x in iso.split("-"))
        return f"{g} {MESI[m - 1]} {a}"
    except (ValueError, IndexError):
        return iso


def data_breve(iso: str) -> tuple[str, str]:
    """('19', 'ott 2026') per la colonna data dei verbali."""
    try:
        a, m, g = (int(x) for x in iso.split("-"))
        return str(g), f"{MESI[m - 1][:3]} {a}"
    except (ValueError, IndexError):
        return iso, ""


def titolo_da_nome(nome: str) -> str:
    """'presentazione-rtb' -> 'Presentazione RTB'; 'diario-2026-11-10' ->
    'Diario di bordo, 10 novembre 2026'."""
    data = re.search(r"(\d{4}-\d{2}-\d{2})", nome)
    if nome.lower().startswith("diario") and data:
        return f"Diario di bordo, {data_lunga(data.group(1))}"
    parole = re.split(r"[-_ ]+", nome)
    sigle = {"rtb": "RTB", "pb": "PB", "tb": "TB", "mvp": "MVP", "poc": "PoC"}
    testo = " ".join(sigle.get(p.lower(), p) for p in parole if p)
    return testo[:1].upper() + testo[1:]


# --------------------------------------------------------------------------
#  Pezzi di pagina
# --------------------------------------------------------------------------
def testo_cerca(*parti: str) -> str:
    return e(" ".join(p for p in parti if p).lower(), quote=True)


def scheda_documento(d, site: Path, grande: bool = False) -> str:
    """Documento con anteprima della prima pagina (lettere, Norme, Piani...)."""
    href = d.pdf_sito.relative_to(site).as_posix()
    png = d.pdf_sito.with_name(d.sorgente.stem + ".anteprima.png")
    if anteprima_pdf(d.pdf_sito, png):
        figura = (f'<img src="{e(png.relative_to(site).as_posix())}" alt="" '
                  f'loading="lazy" width="210" height="297">')
    else:
        iniziali = "".join(p[0] for p in d.titolo.split()[:3] if p[0].isalnum()).upper()
        figura = f'<span class="segnaposto" aria-hidden="true">{e(iniziali)}</span>'
    meta = []
    if d.versione:
        meta.append(f'<span class="ver">v{e(d.versione)}</span>')
    if d.data:
        meta.append(f"<span>{e(data_lunga(d.data))}</span>")
    sotto = f'<p class="sotto">{e(d.sottotitolo)}</p>' if d.sottotitolo else ""
    classe = "scheda grande" if grande else "scheda"
    azione = '<span class="azione">Apri il PDF</span>' if grande else ""
    return (f'<a class="{classe}" href="{e(href)}" data-cerca="{testo_cerca(d.titolo, d.sottotitolo, d.milestone)}">'
            f'<span class="foglio">{figura}</span>'
            f'<span class="testo"><span class="titolo">{e(d.titolo)}</span>{sotto}'
            f'<span class="meta">{"".join(meta)}</span>{azione}</span></a>')


def riga_verbale(d, site: Path, firmato: str) -> str:
    giorno, mese = data_breve(d.data)
    href = d.pdf_sito.relative_to(site).as_posix()
    firma = (f'<a class="firmato" href="{e(firmato)}" title="Copia firmata dal proponente">'
             "Firmato</a>") if firmato else ""
    ver = f'<span class="ver">v{e(d.versione)}</span>' if d.versione else ""
    return (f'<li data-cerca="{testo_cerca(d.titolo, d.data, data_lunga(d.data), d.milestone)}">'
            f'<time datetime="{e(d.data)}"><b>{e(giorno)}</b><span>{e(mese)}</span></time>'
            f'<a class="titolo" href="{e(href)}">{e(d.titolo)}</a>'
            f'<span class="coda">{firma}{ver}</span></li>')


def blocco_milestone(chiave: str, voci: list, site: Path, firmati: dict,
                     link: list[dict]) -> str:
    """Il contenuto di una milestone: lettera, documenti, verbali."""
    parti = []
    lettere = [d for d in voci if d.tipo == "lettera"]
    documenti = [d for d in voci if d.categoria == "documenti" and d.tipo != "lettera"]

    pulsanti = "".join(f'<a class="pulsante" href="{e(str(l.get("url", "")))}">'
                       f'{e(str(l.get("testo", "Link")))}</a>'
                       for l in link if isinstance(l, dict) and l.get("url"))
    if lettere or pulsanti:
        in_evidenza = "".join(scheda_documento(d, site, grande=True)
                              for d in sorted(lettere, key=lambda d: d.titolo.lower()))
        parti.append(f'<div class="evidenza">{in_evidenza}'
                     f'{f"<div class=pulsanti>{pulsanti}</div>" if pulsanti else ""}</div>')

    for visibilita, titolo in (("esterni", "Documenti esterni"), ("interni", "Documenti interni")):
        gruppo = sorted((d for d in documenti if d.visibilita == visibilita),
                        key=lambda d: d.titolo.lower())
        if gruppo:
            parti.append(f'<div class="gruppo"><h3>{titolo}</h3><div class="schede">'
                         f'{"".join(scheda_documento(d, site) for d in gruppo)}</div></div>')

    colonne = []
    for visibilita, titolo in (("esterni", "Verbali esterni"), ("interni", "Verbali interni")):
        gruppo = sorted((d for d in voci if d.categoria == "verbali" and d.visibilita == visibilita),
                        key=lambda d: d.data, reverse=True)
        if gruppo:
            righe = "".join(riga_verbale(d, site, firmati.get(d.sorgente, "")) for d in gruppo)
            colonne.append(f'<div class="gruppo"><h3>{titolo} <small>{len(gruppo)}</small></h3>'
                           f'<ol class="verbali">{righe}</ol></div>')
    if colonne:
        parti.append(f'<div class="colonne">{"".join(colonne)}</div>')
    return "".join(parti)


def grafo(milestone: list[dict]) -> str:
    """Il grafo in cima: un nodo per milestone, un pallino per verbale."""
    nodi = []
    for m in milestone:
        pallini = "".join('<i></i>' for _ in range(min(m["verbali"], 30)))
        conteggio = (f'{m["documenti"]} documenti, {m["verbali"]} verbali'
                     if m["documenti"] or m["verbali"] else "nessun documento")
        nodi.append(
            f'<li class="nodo {m["classe"]}">'
            f'<a href="#{m["ancora"]}" {"" if m["ha_contenuto"] else "tabindex=-1"}>'
            f'<span class="punto" aria-hidden="true"></span>'
            f'<span class="nome">{e(m["chiave"])}</span>'
            f'<span class="stato">{e(m["stato"].capitalize())}</span>'
            f'<span class="conta">{conteggio}</span></a>'
            f'<span class="binario" aria-hidden="true">{pallini}</span></li>')
    return f'<ol class="grafo" aria-label="Avanzamento delle milestone">{"".join(nodi)}</ol>'


def membri_html(gruppo: dict, account: dict) -> str:
    schede = []
    for m in gruppo["membri"]:
        utente = str(account.get(m["chiave"], "") or "").strip().lstrip("@")
        iniziali = "".join(p[0] for p in m["nome"].split()[:2]).upper()
        if utente:
            foto = (f'<img src="https://github.com/{e(utente)}.png?size=128" alt="" '
                    f'loading="lazy" width="56" height="56">')
            nome = (f'<a href="https://github.com/{e(utente)}">{e(m["nome"])}</a>'
                    f'<span>@{e(utente)}</span>')
        else:
            foto = f'<span class="iniziali" aria-hidden="true">{e(iniziali)}</span>'
            nome = f'<b>{e(m["nome"])}</b>'
        schede.append(f'<li>{foto}<span class="chi">{nome}</span></li>')
    return f'<ul class="membri">{"".join(schede)}</ul>'


# --------------------------------------------------------------------------
#  La pagina
# --------------------------------------------------------------------------
def scrivi(documenti: list, root: Path, site: Path) -> None:
    site.mkdir(parents=True, exist_ok=True)
    for nome in ("logo.png", "logo-bianco.png"):
        logo = root / "template" / "img" / nome
        if logo.exists():
            shutil.copy2(logo, site / nome)

    impostazioni = carica_impostazioni(root)
    gruppo = leggi_gruppo(root)
    pubblicati = [d for d in documenti if d.pdf_sito.exists() and d.milestone]

    # verbali firmati: <nome>-firmato.pdf accanto al .tex
    firmati: dict = {}
    for d in pubblicati:
        firmato = d.sorgente.with_name(d.sorgente.stem + "-firmato.pdf")
        if firmato.exists():
            destinazione = d.pdf_sito.parent / firmato.name
            shutil.copy2(firmato, destinazione)
            firmati[d.sorgente] = destinazione.relative_to(site).as_posix()

    # diapositive: PDF caricati a mano in <Milestone>/diapositive/
    presentazioni, diari = [], []
    for chiave, _ in MILESTONE:
        cartella = root / chiave / "diapositive"
        if not cartella.is_dir():
            continue
        for pdf in sorted(cartella.rglob("*.pdf")):
            destinazione = site / pdf.relative_to(root)
            destinazione.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pdf, destinazione)
            voce = {"titolo": titolo_da_nome(pdf.stem), "milestone": chiave,
                    "href": destinazione.relative_to(site).as_posix(), "pdf": destinazione,
                    "data": (re.search(r"\d{4}-\d{2}-\d{2}", pdf.stem) or [""])[0]}
            (diari if pdf.stem.lower().startswith("diario") else presentazioni).append(voce)

    # stato delle milestone e quale mostrare per prima
    conf_milestone = impostazioni.get("milestone", {})
    milestone = []
    for chiave, esteso in MILESTONE:
        conf = conf_milestone.get(chiave, {}) if isinstance(conf_milestone, dict) else {}
        stato = str(conf.get("stato", "da iniziare")).strip().lower()
        stato = stato if stato in STATI else "da iniziare"
        voci = [d for d in pubblicati if d.milestone == chiave]
        milestone.append({
            "chiave": chiave, "esteso": esteso, "stato": stato, "voci": voci,
            "ancora": chiave.lower(), "link": conf.get("link", []) or [],
            "verbali": sum(1 for d in voci if d.categoria == "verbali"),
            "documenti": sum(1 for d in voci if d.categoria == "documenti"),
            "ha_contenuto": bool(voci) or bool(conf.get("link")),
            "classe": {"conclusa": "fatto", "in corso": "ora", "da iniziare": "poi"}[stato],
        })
    in_corso = next((m for m in milestone if m["stato"] == "in corso"), None)
    if in_corso is None:     # nessuna "in corso": l'ultima con dei documenti
        in_corso = next((m for m in reversed(milestone) if m["ha_contenuto"]), milestone[0])
    archivio = [m for m in reversed(milestone) if m is not in_corso and m["ha_contenuto"]]

    # ---- sezioni -------------------------------------------------------
    sezioni, menu = [], []
    corpo = blocco_milestone(in_corso["chiave"], in_corso["voci"], site, firmati, in_corso["link"])
    sezioni.append(
        f'<section id="{in_corso["ancora"]}" class="milestone attuale">'
        f'<header class="testata"><h2>{e(in_corso["chiave"])}</h2>'
        f'<p>{e(in_corso["esteso"]) if in_corso["chiave"] != "Candidatura" else "Documenti per la candidatura al capitolato"}'
        f' <span class="badge {in_corso["classe"]}">{e(in_corso["stato"])}</span></p></header>'
        f'{corpo or "<p class=vuoto>I documenti compariranno qui dopo il primo merge.</p>"}</section>')
    menu.append((in_corso["ancora"], in_corso["chiave"]))

    if presentazioni or diari:
        parti = []
        if presentazioni:
            schede = []
            for p in presentazioni:
                png = p["pdf"].with_name(p["pdf"].stem + ".anteprima.png")
                figura = (f'<img src="{e(png.relative_to(site).as_posix())}" alt="" loading="lazy" '
                          f'width="297" height="210">' if anteprima_pdf(p["pdf"], png)
                          else '<span class="segnaposto" aria-hidden="true"></span>')
                schede.append(f'<a class="scheda orizzontale" href="{e(p["href"])}" '
                              f'data-cerca="{testo_cerca(p["titolo"], p["milestone"])}">'
                              f'<span class="foglio">{figura}</span><span class="testo">'
                              f'<span class="titolo">{e(p["titolo"])}</span>'
                              f'<span class="meta"><span>{e(p["milestone"])}</span></span></span></a>')
            parti.append(f'<div class="gruppo"><h3>Presentazioni</h3><div class="schede larghe">'
                         f'{"".join(schede)}</div></div>')
        if diari:
            righe = []
            for dd in sorted(diari, key=lambda x: x["data"], reverse=True):
                giorno, mese = data_breve(dd["data"])
                righe.append(f'<li data-cerca="{testo_cerca(dd["titolo"], dd["milestone"])}">'
                             f'<time datetime="{e(dd["data"])}"><b>{e(giorno)}</b><span>{e(mese)}</span></time>'
                             f'<a class="titolo" href="{e(dd["href"])}">{e(dd["titolo"])}</a>'
                             f'<span class="coda"><span class="ver">{e(dd["milestone"])}</span></span></li>')
            parti.append(f'<div class="gruppo"><h3>Diari di bordo <small>{len(diari)}</small></h3>'
                         f'<ol class="verbali">{"".join(righe)}</ol></div>')
        sezioni.append(f'<section id="diapositive"><header class="testata"><h2>Diapositive</h2>'
                       f'<p>Presentazioni delle revisioni e diari di bordo</p></header>'
                       f'{"".join(parti)}</section>')
        menu.append(("diapositive", "Diapositive"))

    if archivio:
        cassetti = []
        for m in archivio:
            corpo = blocco_milestone(m["chiave"], m["voci"], site, firmati, m["link"])
            conteggio = f'{m["documenti"]} documenti e {m["verbali"]} verbali'
            cassetti.append(
                f'<details id="{m["ancora"]}" class="milestone">'
                f'<summary><span class="nome">{e(m["chiave"])}</span>'
                f'<span class="dettaglio">{e(m["esteso"]) if m["chiave"] != "Candidatura" else "Candidatura al capitolato"}</span>'
                f'<span class="badge {m["classe"]}">{e(m["stato"])}</span>'
                f'<span class="conta">{conteggio}</span></summary>'
                f'<div class="dentro">{corpo}</div></details>')
        sezioni.append(f'<section id="archivio"><header class="testata"><h2>Archivio</h2>'
                       f'<p>Le milestone precedenti, con i documenti com\'erano alla loro chiusura</p>'
                       f'</header>{"".join(cassetti)}</section>')
        menu.append(("archivio", "Archivio"))

    # ---- il gruppo -----------------------------------------------------
    progetto = impostazioni.get("progetto", {}) or {}
    capitolato = str(progetto.get("capitolato", "")).strip()
    proponente = str(progetto.get("proponente", "")).strip()
    descrizione = str(progetto.get("descrizione", "")).strip()
    n = len(gruppo["membri"])
    righe_gruppo = [f"<p>Siamo {n} studenti del corso di Ingegneria del Software "
                    f"dell'Università degli Studi di Padova, anno accademico {e(gruppo['anno'])}.</p>"]
    if capitolato:
        da = f", proposto da {e(proponente)}" if proponente else ""
        righe_gruppo.append(f'<p class="capitolato">Capitolato: <b>{e(capitolato)}</b>{da}.</p>')
    if descrizione:
        righe_gruppo += [f"<p>{e(p.strip())}</p>" for p in descrizione.split("\n\n") if p.strip()]
    sezioni.append(f'<section id="gruppo"><header class="testata"><h2>Il gruppo</h2></header>'
                   f'<div class="due"><div class="prosa">{"".join(righe_gruppo)}</div>'
                   f'{membri_html(gruppo, impostazioni.get("github", {}) or {})}</div></section>')
    menu.append(("gruppo", "Il gruppo"))

    repo = os.environ.get("GITHUB_REPOSITORY", "Git-Push-Team/docs")
    try:
        from zoneinfo import ZoneInfo
        adesso = datetime.now(ZoneInfo("Europe/Rome"))
    except Exception:            # niente fusi orari installati (Windows)
        adesso = datetime.now()
    aggiornato = f"{data_lunga(adesso.date().isoformat())}, ore {adesso:%H:%M}"
    contatti = [f'<li><span>Email</span><a href="mailto:{e(gruppo["email"])}">{e(gruppo["email"])}</a></li>',
                f'<li><span>Sorgenti</span><a href="https://github.com/{e(repo)}">github.com/{e(repo)}</a></li>',
                f'<li><span>Consegne</span><a href="https://github.com/{e(repo)}/releases">'
                "Archivio delle release</a></li>"]
    sezioni.append(f'<section id="contatti"><header class="testata"><h2>Contatti</h2></header>'
                   f'<ul class="contatti">{"".join(contatti)}</ul>'
                   f'<p class="aggiornato">Ultimo aggiornamento: {e(aggiornato)}</p></section>')
    menu.append(("contatti", "Contatti"))

    # ---- documenti.json (per chi vuole riusare l'elenco) ---------------
    (site / "documenti.json").write_text(json.dumps([{
        "titolo": d.titolo, "versione": d.versione, "data": d.data, "tipo": d.tipo,
        "milestone": d.milestone, "sezione": f"{d.categoria}/{d.visibilita}",
        "sorgente": d.relativo.as_posix(), "pdf": d.pdf_sito.relative_to(site).as_posix(),
        "firmato": firmati.get(d.sorgente, ""),
    } for d in pubblicati], ensure_ascii=False, indent=2), encoding="utf-8")

    descrizione_sito = str((impostazioni.get("sito", {}) or {}).get(
        "descrizione", "Documentazione del progetto didattico di Ingegneria del Software"))
    voci_menu = "".join(f'<a href="#{a}">{e(t)}</a>' for a, t in menu)
    pagina = MODELLO.format(
        nome=e(gruppo["nome"]), numero=e(gruppo["numero"]), anno=e(gruppo["anno"]),
        descrizione=e(descrizione_sito), menu=voci_menu, grafo=grafo(milestone),
        sezioni="".join(sezioni), css=CSS, js=JS)
    (site / "index.html").write_text(pagina, encoding="utf-8")


# --------------------------------------------------------------------------
#  HTML, CSS e JavaScript della pagina
# --------------------------------------------------------------------------
MODELLO = """<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{nome} · Documentazione</title>
<meta name="description" content="{descrizione}, gruppo {numero}, Università degli Studi di Padova">
<link rel="icon" href="logo.png" media="(prefers-color-scheme: light)">
<link rel="icon" href="logo-bianco.png" media="(prefers-color-scheme: dark)">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<a class="salta" href="#contenuto">Vai ai documenti</a>
<nav class="barra" aria-label="Sezioni">
  <a class="marchio" href="#">
    <picture><source srcset="logo-bianco.png" media="(prefers-color-scheme: dark)"><img src="logo.png" alt="" width="32" height="32"></picture>
    <span>{nome}</span>
  </a>
  <div class="voci">{menu}</div>
  <label class="cerca"><span class="nascosto">Cerca un documento</span>
    <input id="cerca" type="search" placeholder="Cerca un documento" autocomplete="off"></label>
</nav>
<header class="eroe">
  <div class="intro">
    <picture><source srcset="logo-bianco.png" media="(prefers-color-scheme: dark)"><img class="logo" src="logo.png" alt="Logo del {nome}" width="132" height="132"></picture>
    <div>
      <h1>{nome}</h1>
      <p class="motto">--force &amp; pray</p>
      <p class="descrizione">{descrizione}. Gruppo {numero}, Università degli Studi di Padova, anno accademico {anno}.</p>
    </div>
  </div>
  {grafo}
</header>
<main id="contenuto">
<p id="nessuno" class="vuoto" hidden>Nessun documento corrisponde alla ricerca.</p>
{sezioni}
</main>
<script>{js}</script>
</body>
</html>
"""

CSS = """
:root {
  --carta: #f4f6fa; --superficie: #ffffff; --inchiostro: #12213a; --tenue: #5b6a82;
  --linea: #d8dee9; --blu: #14457a; --blu-chiaro: #e3ecf7; --ambra: #c9861a;
  --ambra-chiaro: #fbf0dc; --ombra: 0 1px 2px rgb(18 33 58 / .06), 0 8px 24px -12px rgb(18 33 58 / .18);
  --display: "Bricolage Grotesque", "Segoe UI", system-ui, sans-serif;
  --testo: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
  color-scheme: light dark;
}
@media (prefers-color-scheme: dark) {
  :root { --carta: #0f1828; --superficie: #16223a; --inchiostro: #e7edf6; --tenue: #93a3bb;
          --linea: #273550; --blu: #86b4ea; --blu-chiaro: #1b2d4b; --ambra: #f0b44f;
          --ambra-chiaro: #33291a; --ombra: 0 1px 2px rgb(0 0 0 / .3), 0 10px 30px -14px rgb(0 0 0 / .7); }
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; scroll-padding-top: 84px; }
body { margin: 0; background: var(--carta); color: var(--inchiostro);
       font: 17px/1.55 var(--testo); -webkit-font-smoothing: antialiased; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--blu); outline-offset: 3px; border-radius: 4px; }
.nascosto { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); }
.salta { position: absolute; left: 16px; top: -48px; background: var(--blu); color: var(--carta);
         padding: 8px 14px; border-radius: 6px; z-index: 20; }
.salta:focus { top: 12px; }

/* barra in alto */
.barra { position: sticky; top: 0; z-index: 10; display: flex; align-items: center; gap: 24px;
         padding: 10px max(16px, calc((100vw - 1120px) / 2));
         background: color-mix(in srgb, var(--carta) 82%, transparent);
         backdrop-filter: saturate(1.4) blur(14px); -webkit-backdrop-filter: saturate(1.4) blur(14px);
         border-bottom: 1px solid color-mix(in srgb, var(--linea) 70%, transparent); }
.marchio { display: flex; align-items: center; gap: 10px; text-decoration: none;
           font: 700 17px var(--display); white-space: nowrap; }
.marchio img { width: 32px; height: 32px; object-fit: contain; }
.voci { display: flex; gap: 4px; flex: 1; overflow-x: auto; scrollbar-width: none; }
.voci a { padding: 6px 12px; border-radius: 8px; text-decoration: none; color: var(--tenue);
          white-space: nowrap; font-weight: 600; font-size: 15px; transition: color .2s, background .2s; }
.voci a:hover, .voci a.attiva { color: var(--inchiostro); background: var(--blu-chiaro); }
.cerca input { width: 220px; font: inherit; font-size: 15px; color: inherit; padding: 7px 12px;
               border: 1px solid var(--linea); border-radius: 8px; background: var(--superficie); }
.cerca input:focus { outline: 2px solid var(--blu); outline-offset: 0; border-color: transparent; }

/* intestazione */
.eroe { max-width: 1120px; margin: 0 auto; padding: 64px 16px 40px; }
.intro { display: flex; align-items: center; gap: 32px; }
.logo { width: 132px; height: 132px; object-fit: contain; flex: none; }
h1 { font: 800 clamp(44px, 7vw, 84px)/0.95 var(--display); letter-spacing: -0.035em; margin: 0; }
.motto { font: 500 18px var(--display); color: var(--blu); margin: 10px 0 0; letter-spacing: .01em; }
.descrizione { color: var(--tenue); margin: 10px 0 0; max-width: 60ch; }

/* il grafo delle milestone */
.grafo { list-style: none; margin: 56px 0 0; padding: 0; display: grid;
         grid-template-columns: repeat(3, 1fr); }
.nodo { position: relative; }
.nodo > a { display: grid; gap: 2px; text-decoration: none; padding-top: 34px; position: relative; }
.nodo > a[tabindex="-1"] { pointer-events: none; }
.punto { position: absolute; top: 0; left: 0; width: 22px; height: 22px; border-radius: 50%;
         background: var(--carta); border: 3px solid var(--linea); z-index: 1; }
.fatto .punto { background: var(--blu); border-color: var(--blu); }
.ora .punto { background: var(--ambra); border-color: var(--ambra);
              box-shadow: 0 0 0 6px var(--ambra-chiaro); }
.binario { position: absolute; top: 9px; left: 22px; right: 0; height: 4px;
           display: flex; align-items: center; justify-content: space-evenly; padding: 0 14px;
           background: var(--linea); border-radius: 2px; transform-origin: left; }
.fatto .binario { background: var(--blu); }
.ora .binario { background: linear-gradient(90deg, var(--ambra), var(--linea)); }
.nodo:last-child .binario { right: 24%; }
.binario i { width: 8px; height: 8px; border-radius: 50%; background: var(--superficie);
             border: 2px solid currentColor; color: var(--blu); flex: none; margin: 0 -2px; }
.ora .binario i { color: var(--ambra); }
.nome { font: 700 26px/1.1 var(--display); letter-spacing: -0.02em; }
.nodo > a:hover .nome { color: var(--blu); }
.stato { font-weight: 600; color: var(--tenue); font-size: 15px; }
.ora .stato { color: var(--ambra); }
.conta { color: var(--tenue); font-size: 14px; }

/* unica animazione automatica: il grafo si disegna all'apertura */
@media (prefers-reduced-motion: no-preference) {
  .binario { animation: traccia .9s cubic-bezier(.3,.7,.2,1) both; }
  .punto { animation: compare .45s cubic-bezier(.3,1.5,.5,1) both; }
  .nodo:nth-child(2) .binario { animation-delay: .5s; } .nodo:nth-child(2) .punto { animation-delay: .4s; }
  .nodo:nth-child(3) .binario { animation-delay: 1s; } .nodo:nth-child(3) .punto { animation-delay: .9s; }
  @keyframes traccia { from { transform: scaleX(0); } }
  @keyframes compare { from { transform: scale(0); } }
}

/* sezioni */
main { max-width: 1120px; margin: 0 auto; padding: 0 16px 96px; }
section { padding-top: 72px; }
.testata { display: flex; align-items: baseline; gap: 16px; flex-wrap: wrap;
           border-bottom: 1px solid var(--linea); padding-bottom: 14px; margin-bottom: 28px; }
h2 { font: 800 clamp(32px, 4.5vw, 48px)/1 var(--display); letter-spacing: -0.03em; margin: 0; }
.testata p { margin: 0; color: var(--tenue); display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
h3 { font: 700 20px var(--display); letter-spacing: -0.01em; margin: 0 0 14px; }
h3 small { font: 600 14px var(--testo); color: var(--tenue); margin-left: 6px; }
.gruppo { margin-bottom: 40px; }
.badge { font-size: 13px; font-weight: 600; padding: 2px 10px; border-radius: 999px;
         background: var(--blu-chiaro); color: var(--blu); white-space: nowrap; }
.badge.ora { background: var(--ambra-chiaro); color: var(--ambra); }
.badge.poi { background: transparent; border: 1px dashed var(--linea); color: var(--tenue); }
.vuoto { color: var(--tenue); padding: 24px 0; }

/* documenti con anteprima: fogli di carta */
.schede { display: grid; grid-template-columns: repeat(auto-fill, minmax(176px, 1fr)); gap: 28px 22px; }
.schede.larghe { grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
.scheda { display: flex; flex-direction: column; gap: 12px; text-decoration: none; }
.foglio { display: block; aspect-ratio: 210 / 297; background: var(--superficie); border-radius: 4px;
          overflow: hidden; box-shadow: var(--ombra); outline: 1px solid var(--linea);
          transition: transform .25s cubic-bezier(.3,.7,.2,1), box-shadow .25s; position: relative; }
.orizzontale .foglio { aspect-ratio: 297 / 210; }
.foglio img { width: 100%; height: 100%; object-fit: cover; object-position: top; display: block; }
@media (prefers-color-scheme: dark) { .foglio img { filter: brightness(.92); } }
.scheda:hover .foglio, .scheda:focus-visible .foglio {
  transform: translateY(-4px) rotate(-0.6deg);
  box-shadow: 0 2px 4px rgb(18 33 58 / .08), 0 22px 40px -18px rgb(18 33 58 / .45); }
.segnaposto { position: absolute; inset: 0; display: grid; place-items: center;
              font: 800 34px var(--display); color: var(--blu);
              background: repeating-linear-gradient(180deg, transparent 0 22px, var(--blu-chiaro) 22px 23px); }
.testo { display: grid; gap: 2px; }
.titolo { font-weight: 600; line-height: 1.3; }
.scheda:hover .titolo { color: var(--blu); }
.sotto { margin: 2px 0 0; color: var(--tenue); font-size: 15px; }
.meta { display: flex; gap: 10px; flex-wrap: wrap; color: var(--tenue); font-size: 14px; }
.ver { font-variant-numeric: tabular-nums; font-weight: 600; color: var(--blu); }

/* in evidenza: la lettera di presentazione */
.evidenza { display: flex; gap: 22px; flex-wrap: wrap; align-items: stretch; margin-bottom: 44px; }
.scheda.grande { flex-direction: row; align-items: center; gap: 28px; flex: 1 1 460px;
                 background: var(--superficie); border: 1px solid var(--linea); border-radius: 14px;
                 padding: 22px 26px 22px 22px; box-shadow: var(--ombra); }
.scheda.grande .foglio { width: 132px; flex: none; }
.scheda.grande .titolo { font: 700 26px/1.15 var(--display); letter-spacing: -0.02em; }
.azione { margin-top: 12px; justify-self: start; font-weight: 600; font-size: 15px; color: var(--superficie);
          background: var(--blu); padding: 8px 16px; border-radius: 8px; }
.pulsanti { display: flex; flex-direction: column; gap: 10px; justify-content: center; }
.pulsante { text-decoration: none; font-weight: 600; padding: 12px 20px; border-radius: 10px;
            border: 1px solid var(--linea); background: var(--superficie); transition: border-color .2s; }
.pulsante:hover { border-color: var(--blu); color: var(--blu); }

/* verbali: un registro con la data a sinistra */
.colonne { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 0 44px; }
.verbali { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--linea); }
.verbali li { display: grid; grid-template-columns: 64px 1fr auto; align-items: center; gap: 14px;
              padding: 12px 6px; border-bottom: 1px solid var(--linea); position: relative;
              transition: background .2s; }
.verbali li:hover { background: color-mix(in srgb, var(--blu-chiaro) 55%, transparent); }
.verbali time { display: grid; line-height: 1.05; }
.verbali time b { font: 700 24px var(--display); letter-spacing: -0.02em; }
.verbali time span { font-size: 13px; color: var(--tenue); }
.verbali .titolo { text-decoration: none; }
.verbali .titolo::after { content: ""; position: absolute; inset: 0; }
.verbali .titolo:hover { color: var(--blu); }
.coda { display: flex; gap: 10px; align-items: center; }
.firmato { position: relative; z-index: 1; font-size: 13px; font-weight: 600; text-decoration: none;
           color: var(--blu); border: 1px solid currentColor; border-radius: 999px; padding: 1px 9px; }
.firmato:hover { background: var(--blu); color: var(--superficie); }

/* archivio */
details.milestone { border: 1px solid var(--linea); border-radius: 14px; background: var(--superficie);
                    margin-bottom: 14px; box-shadow: var(--ombra); }
details.milestone summary { display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
                            padding: 20px 24px; cursor: pointer; list-style: none; }
details.milestone summary::-webkit-details-marker { display: none; }
details.milestone summary::after { content: ""; margin-left: auto; width: 10px; height: 10px;
  border-right: 2px solid var(--tenue); border-bottom: 2px solid var(--tenue);
  transform: rotate(45deg); transition: transform .25s; }
details[open].milestone summary::after { transform: rotate(-135deg); }
summary .nome { font-size: 24px; }
summary .dettaglio { color: var(--tenue); }
.dentro { padding: 8px 24px 12px; border-top: 1px solid var(--linea); }
.dentro > .gruppo:first-child, .dentro > .evidenza:first-child { margin-top: 20px; }

/* gruppo e contatti */
.due { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr); gap: 44px; }
.prosa { max-width: 62ch; }
.prosa p { margin: 0 0 14px; }
.capitolato b { color: var(--blu); }
.membri { list-style: none; margin: 0; padding: 0; display: grid;
          grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 14px; }
.membri li { display: flex; align-items: center; gap: 14px; padding: 12px; border-radius: 12px;
             background: var(--superficie); border: 1px solid var(--linea); }
.membri img, .iniziali { width: 56px; height: 56px; border-radius: 50%; flex: none; }
.iniziali { display: grid; place-items: center; background: var(--blu-chiaro); color: var(--blu);
            font: 700 19px var(--display); }
.chi { display: grid; line-height: 1.3; }
.chi a { font-weight: 600; text-decoration: none; }
.chi a:hover { color: var(--blu); }
.chi span { color: var(--tenue); font-size: 14px; }
.contatti { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
.contatti li { display: grid; grid-template-columns: 110px 1fr; gap: 14px; }
.contatti span { color: var(--tenue); }
.contatti a { font-weight: 600; text-decoration-color: var(--linea); text-underline-offset: 4px; }
.contatti a:hover { color: var(--blu); text-decoration-color: currentColor; }
.aggiornato { color: var(--tenue); font-size: 14px; margin-top: 40px; }

/* ricerca */
[data-cerca].fuori, .gruppo.fuori, .evidenza.fuori, section.fuori, details.fuori { display: none; }

@media (max-width: 760px) {
  .barra { flex-wrap: wrap; gap: 8px 16px; }
  .voci { order: 3; flex-basis: 100%; }
  .cerca { margin-left: auto; }
  .cerca input { width: 150px; }
  .intro { flex-direction: column; align-items: flex-start; gap: 18px; }
  .logo { width: 88px; height: 88px; }
  .eroe { padding-top: 36px; }
  .grafo .nome { font-size: 17px; }
  .grafo .stato { font-size: 13px; }
  .nodo > a { padding-right: 6px; }
  .conta { display: none; }
  .due { grid-template-columns: 1fr; }
  .scheda.grande { flex: 1 1 100%; padding: 16px; gap: 18px; }
  .scheda.grande .foglio { width: 92px; }
  .scheda.grande .titolo { font-size: 21px; }
  .schede { grid-template-columns: repeat(2, 1fr); gap: 22px 16px; }
  .colonne { grid-template-columns: 1fr; }
  .verbali li { grid-template-columns: 52px 1fr; }
  .coda { grid-column: 2; }
}
"""

JS = """
(() => {
  // voce del menu evidenziata mentre si scorre
  const voci = [...document.querySelectorAll('.voci a')];
  const sezioni = voci.map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);
  if ('IntersectionObserver' in window) {
    const osserva = new IntersectionObserver(eventi => {
      eventi.forEach(ev => {
        if (!ev.isIntersecting) return;
        voci.forEach(a => a.classList.toggle('attiva', a.getAttribute('href') === '#' + ev.target.id));
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    sezioni.forEach(s => osserva.observe(s));
  }

  // i link alle milestone dell'archivio aprono il cassetto
  document.querySelectorAll('a[href^="#"]').forEach(a => a.addEventListener('click', () => {
    const meta = document.querySelector(a.getAttribute('href'));
    if (meta && meta.tagName === 'DETAILS') meta.open = true;
  }));

  // ricerca: nasconde ciò che non corrisponde
  const campo = document.getElementById('cerca');
  const nessuno = document.getElementById('nessuno');
  const cassetti = [...document.querySelectorAll('details.milestone')];
  const statoCassetti = cassetti.map(d => d.open);
  campo.addEventListener('input', () => {
    const parole = campo.value.toLowerCase().trim().split(/\\s+/).filter(Boolean);
    let trovati = 0;
    document.querySelectorAll('[data-cerca]').forEach(el => {
      const ok = parole.every(p => el.dataset.cerca.includes(p));
      el.classList.toggle('fuori', !ok);
      if (ok) trovati++;
    });
    document.querySelectorAll('.gruppo, .evidenza, main > section, details.milestone').forEach(c => {
      const haVoci = c.querySelector('[data-cerca]');
      const visibili = c.querySelector('[data-cerca]:not(.fuori)');
      c.classList.toggle('fuori', parole.length > 0 && haVoci && !visibili);
    });
    cassetti.forEach((d, i) => { d.open = parole.length ? true : statoCassetti[i]; });
    nessuno.hidden = !(parole.length && trovati === 0);
  });
  document.addEventListener('keydown', ev => {
    if (ev.key === '/' && document.activeElement !== campo) { ev.preventDefault(); campo.focus(); }
  });
})();
"""
