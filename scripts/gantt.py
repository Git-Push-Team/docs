#!/usr/bin/env python3
"""
gantt.py -- genera in automatico i diagrammi di Gantt in LaTeX (pgfgantt)
a partire da gestione/pianificazione.toml (repository .github) e dalle issue
del GitHub Project "GIT PUSH TEAM", seguendo lo stesso meccanismo di
scripts/registro.py.

File generati in RTB/documenti/esterni/tabelle/:
  - gantt-progetto.tex      (Gantt macroscopico dell'intero progetto, Sprint 1..10)
  - gantt-sprint-<N>.tex    (Mini-Gantt operativo dei 14 giorni dello sprint N)

Uso:
    PIANIFICAZIONE=.gestione/gestione/pianificazione.toml python3 scripts/gantt.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore
    except ModuleNotFoundError:
        tomllib = None  # type: ignore


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "RTB" / "documenti" / "esterni" / "tabelle"


def carica_pianificazione() -> dict:
    percorso = os.environ.get("PIANIFICAZIONE", "")
    if not percorso or not Path(percorso).is_file():
        candidati = [
            ROOT / ".gestione" / "gestione" / "pianificazione.toml",
            ROOT.parent / ".github" / "gestione" / "pianificazione.toml",
        ]
        for c in candidati:
            if c.is_file():
                percorso = str(c)
                break
    if not percorso or not Path(percorso).is_file():
        print("::warning::File pianificazione.toml non trovato: uso valori predefiniti.", file=sys.stderr)
        return {}
    if tomllib is None:
        print("::warning::tomllib non disponibile (serve Python 3.11+): uso valori predefiniti.", file=sys.stderr)
        return {}
    with open(percorso, "rb") as f:
        return tomllib.load(f)


def estrai_lista_sprint(pianificazione: dict) -> list[dict]:
    """Supporta sia [[sprint]] (lista) sia [sprint.1] (dizionario) in pianificazione.toml."""
    raw = pianificazione.get("sprint", [])
    risultato = []
    if isinstance(raw, list):
        for idx, item in enumerate(raw, start=1):
            d = dict(item)
            d.setdefault("numero", idx)
            risultato.append(d)
    elif isinstance(raw, dict):
        for k, item in raw.items():
            d = dict(item)
            try:
                d.setdefault("numero", int(re.sub(r"\D", "", str(k))))
            except ValueError:
                d.setdefault("numero", len(risultato) + 1)
            risultato.append(d)
    risultato.sort(key=lambda x: int(x["numero"]))
    return risultato


def carica_issue_project(owner: str, token: str) -> list[dict]:
    """Legge le issue con data inizio, scadenza, sprint e stato dal GitHub Project v2."""
    if not token:
        return []
    query = """
    query($owner: String!) {
      organization(login: $owner) {
        projectsV2(first: 5) {
          nodes {
            title
            items(first: 100) {
              nodes {
                content {
                  ... on Issue {
                    number
                    title
                    state
                    createdAt
                    closedAt
                  }
                }
                fieldValues(first: 20) {
                  nodes {
                    ... on ProjectV2ItemFieldTextValue {
                      text
                      field { ... on ProjectV2FieldCommon { name } }
                    }
                    ... on ProjectV2ItemFieldSingleSelectValue {
                      name
                      field { ... on ProjectV2FieldCommon { name } }
                    }
                    ... on ProjectV2ItemFieldDateValue {
                      date
                      field { ... on ProjectV2FieldCommon { name } }
                    }
                    ... on ProjectV2ItemFieldIterationValue {
                      title
                      startDate
                      duration
                      field { ... on ProjectV2FieldCommon { name } }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"owner": owner}}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "gpt-gantt-bot",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"::warning::Impossibile interrogare GitHub Project per i Gantt: {exc}", file=sys.stderr)
        return []

    projects = (
        payload.get("data", {})
        .get("organization", {})
        .get("projectsV2", {})
        .get("nodes", [])
    )
    risultato = []
    for proj in projects:
        if "GIT PUSH TEAM" not in proj.get("title", "").upper():
            continue
        for item in proj.get("items", {}).get("nodes", []):
            content = item.get("content") or {}
            if not content.get("number"):
                continue
            campi = {}
            for fv in item.get("fieldValues", {}).get("nodes", []):
                fname = (fv.get("field") or {}).get("name", "")
                if not fname:
                    continue
                if "date" in fv:
                    campi[fname.lower()] = fv["date"]
                elif "name" in fv:
                    campi[fname.lower()] = fv["name"]
                elif "text" in fv:
                    campi[fname.lower()] = fv["text"]
                elif "title" in fv:
                    campi[fname.lower()] = fv["title"]
            risultato.append({
                "number": content["number"],
                "title": content["title"],
                "state": content["state"],
                "created_at": content["createdAt"][:10],
                "closed_at": (content.get("closedAt") or "")[:10],
                "campi": campi,
            })
    return risultato


def escape_latex(testo: str) -> str:
    testo = re.sub(r"^\[[^\]]+\]\s*", "", testo).strip()
    sostituzioni = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    for k, v in sostituzioni.items():
        testo = testo.replace(k, v)
    if len(testo) > 42:
        testo = testo[:39].rstrip() + "..."
    return testo


def genera_gantt_progetto(sprint_list: list[dict]) -> str:
    tot_sprint = max(10, len(sprint_list))
    rtb_count = sum(1 for s in sprint_list if str(s.get("fase", "RTB")).upper() == "RTB")
    rtb_end = rtb_count if len(sprint_list) >= 10 and rtb_count > 0 else 6

    return rf"""% File generato automaticamente da scripts/gantt.py -- non modificare a mano
\begin{{figure}}[H]
  \centering
  \begin{{ganttchart}}[
    hgrid,
    vgrid={{*1{{gptlinea, dotted}}}},
    x unit=0.92cm,
    y unit title=0.52cm,
    y unit chart=0.52cm,
    title/.style={{fill=gptsfondo, draw=gptlinea}},
    title label font=\sffamily\footnotesize\bfseries,
    bar/.style={{fill=gptaccento!80, draw=gptaccento, rounded corners=1.5pt}},
    bar label font=\sffamily\footnotesize,
    group/.style={{fill=gptinchiostro, draw=gptinchiostro}},
    group label font=\sffamily\footnotesize\bfseries,
    milestone/.style={{fill=gptaccento, draw=gptaccento}},
    milestone label font=\sffamily\footnotesize\bfseries,
    link/.style={{->, >=stealth, gptgrigio, thick}}
  ]{{1}}{{{tot_sprint}}}
    \gantttitle{{2026}}{{4}} \gantttitle{{2027}}{{{tot_sprint - 4}}} \\
    \gantttitlelist{{1,...,{tot_sprint}}}{{1}} \\

    \ganttgroup{{Fase RTB (Sprint 1--{rtb_end})}}{{1}}{{{rtb_end}}} \\
    \ganttbar{{Norme, Infrastruttura e Pianificazione}}{{1}}{{2}} \\
    \ganttbar{{Analisi dei Requisiti e Casi d'Uso}}{{1}}{{3}} \\
    \ganttbar{{Sperimentazione tecnologica e \glo{{PoC}}}}{{2}}{{5}} \\
    \ganttbar{{Verifica e consolidamento RTB}}{{5}}{{{rtb_end}}} \\
    \ganttmilestone{{Candidatura RTB (25/01)}}{{{rtb_end}}} \\

    \ganttgroup{{Fase PB (Sprint {rtb_end + 1}--{tot_sprint})}}{{{rtb_end + 1}}}{{{tot_sprint}}} \\
    \ganttbar{{Architettura e progettazione \glo{{MVP}}}}{{{rtb_end + 1}}}{{{rtb_end + 1}}} \\
    \ganttbar{{Sviluppo \glo{{MVP}} (4 capacità \textit{{Concierge}})}}{{{rtb_end + 1}}}{{{tot_sprint - 1}}} \\
    \ganttbar{{Testing, collaudo e Manuale Utente}}{{{tot_sprint - 1}}}{{{tot_sprint}}} \\
    \ganttmilestone{{Consegna PB (23/03)}}{{{tot_sprint}}}

    \ganttlink{{elem2}}{{elem3}}
    \ganttlink{{elem3}}{{elem4}}
    \ganttlink{{elem4}}{{elem5}}
    \ganttlink{{elem5}}{{elem7}}
    \ganttlink{{elem7}}{{elem8}}
    \ganttlink{{elem8}}{{elem9}}
    \ganttlink{{elem9}}{{elem10}}
  \end{{ganttchart}}
  \caption{{Diagramma di Gantt di massima del progetto (suddivisione per sprint)\label{{fig:gantt-progetto}}}}
\end{{figure}}
"""


def genera_gantt_sprint(sprint_cfg: dict, issues: list[dict]) -> str:
    num = int(sprint_cfg["numero"])
    inizio = date.fromisoformat(str(sprint_cfg["inizio"]))
    fine = date.fromisoformat(str(sprint_cfg["fine"]))
    giorni_tot = (fine - inizio).days + 1

    issue_sprint = []
    for iss in issues:
        campi = iss["campi"]
        sp_val = str(campi.get("sprint", "")).strip().lower()
        if sp_val in {f"sprint {num}", str(num)}:
            issue_sprint.append(iss)

    righe_barre = []
    for iss in issue_sprint[:8]:
        campi = iss["campi"]
        d_ini_str = campi.get("data inizio") or campi.get("start date") or iss["created_at"]
        d_fin_str = campi.get("scadenza") or campi.get("end date") or iss["closed_at"] or str(fine)
        try:
            d_ini = max(inizio, min(fine, date.fromisoformat(str(d_ini_str)[:10])))
            d_fin = max(d_ini, min(fine, date.fromisoformat(str(d_fin_str)[:10])))
        except ValueError:
            d_ini, d_fin = inizio, fine

        g_ini = (d_ini - inizio).days + 1
        g_fin = (d_fin - inizio).days + 1
        etichetta = escape_latex(iss["title"])
        righe_barre.append(f"    \\ganttbar{{{etichetta}}}{{{g_ini}}}{{{g_fin}}} \\\\")

    if not righe_barre:
        for idx, ob in enumerate(sprint_cfg.get("obiettivi", [])[:6]):
            testo = ob if isinstance(ob, str) else ob.get("titolo", f"Attività {idx + 1}")
            g_ini = min(giorni_tot, 1 + idx * 2)
            g_fin = min(giorni_tot, g_ini + 5)
            righe_barre.append(f"    \\ganttbar{{{escape_latex(testo)}}}{{{g_ini}}}{{{g_fin}}} \\\\")

    # Milestone automatiche dei mercoledì (call con Eggon + riunione interna)
    cur = inizio
    while cur <= fine:
        if cur.weekday() == 2:
            g_mer = (cur - inizio).days + 1
            righe_barre.append(
                f"    \\ganttmilestone{{Call Eggon + Riunione ({cur.day:02d}/{cur.month:02d})}}{{{g_mer}}} \\\\"
            )
        cur += timedelta(days=1)

    if righe_barre:
        righe_barre[-1] = righe_barre[-1].rstrip(" \\")

    sett1_fine = inizio + timedelta(days=6)
    sett2_ini = inizio + timedelta(days=7)
    corpo = "\n".join(righe_barre)

    return rf"""% File generato automaticamente da scripts/gantt.py -- non modificare a mano
\begin{{figure}}[H]
  \centering
  \begin{{ganttchart}}[
    hgrid,
    vgrid={{*1{{gptlinea, dotted}}}},
    x unit=0.66cm,
    y unit title=0.48cm,
    y unit chart=0.48cm,
    title/.style={{fill=gptsfondo, draw=gptlinea}},
    title label font=\sffamily\scriptsize\bfseries,
    bar/.style={{fill=gptaccento!75, draw=gptaccento, rounded corners=1.5pt}},
    bar label font=\sffamily\scriptsize,
    milestone/.style={{fill=gptaccento, draw=gptaccento}},
    milestone label font=\sffamily\scriptsize\bfseries,
    link/.style={{->, >=stealth, gptgrigio}}
  ]{{1}}{{{giorni_tot}}}
    \gantttitle{{Settimana 1 ({inizio.day}--{sett1_fine.day}/{sett1_fine.month:02d})}}{{7}}
    \gantttitle{{Settimana 2 ({sett2_ini.day}--{fine.day}/{fine.month:02d})}}{{{giorni_tot - 7}}} \\
    \gantttitlelist{{1,...,{giorni_tot}}}{{1}} \\

{corpo}
  \end{{ganttchart}}
  \caption{{Sprint {num} -- Pianificazione temporale delle attività\label{{fig:gantt-sprint-{num}}}}}
\end{{figure}}
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pianificazione = carica_pianificazione()
    sprint_list = estrai_lista_sprint(pianificazione)
    owner = os.environ.get("GITHUB_REPOSITORY_OWNER", "Git-Push-Team")
    token = os.environ.get("GH_TOKEN", "")
    issues = carica_issue_project(owner, token)

    (OUT_DIR / "gantt-progetto.tex").write_text(
        genera_gantt_progetto(sprint_list), encoding="utf-8"
    )

    for sp in sprint_list:
        num = int(sp["numero"])
        (OUT_DIR / f"gantt-sprint-{num}.tex").write_text(
            genera_gantt_sprint(sp, issues), encoding="utf-8"
        )

    print(f"Diagrammi di Gantt aggiornati in {OUT_DIR}")


if __name__ == "__main__":
    main()
