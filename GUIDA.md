# Guida al repository `docs` — da zero

Questa guida spiega **passo per passo** come scrivere e consegnare i documenti del Git Push Team.
Non serve conoscere LaTeX né Git: seguite le ricette e copiate i comandi così come sono.

> **Come leggere i blocchi di comandi**: le righe in grigio si copiano nel **terminale**
> (in VS Code: menu *Terminale → Nuovo terminale*). Su **Windows** scrivete `python` dove
> qui c'è `python3`. Tutti i comandi si lanciano dalla **cartella principale del repository**
> (quella che contiene `README.md`).

## Indice

0. [Le parole da conoscere](#0-le-parole-da-conoscere)
1. [Prima volta: preparare il computer](#1-prima-volta-preparare-il-computer)
2. [Mappa del repository: cosa si tocca e cosa no](#2-mappa-del-repository-cosa-si-tocca-e-cosa-no)
3. [Il giro completo in 7 passi](#3-il-giro-completo-in-7-passi)
4. [Ricette](#4-ricette)
    - [R1. Scrivere un verbale interno](#r1-scrivere-un-verbale-interno)
    - [R2. Scrivere un verbale esterno](#r2-scrivere-un-verbale-esterno)
    - [R3. Correggere un documento già approvato](#r3-correggere-un-documento-già-approvato)
    - [R4. Creare un documento (Norme, Piani, Analisi…)](#r4-creare-un-documento-norme-piani-analisi)
    - [R5. Dividere un documento lungo in capitoli](#r5-dividere-un-documento-lungo-in-capitoli)
    - [R6. Scrivere una lettera](#r6-scrivere-una-lettera)
    - [R7. Inserire un'immagine](#r7-inserire-unimmagine)
    - [R8. Inserire una tabella](#r8-inserire-una-tabella)
    - [R9. Testo: elenchi, grassetto, link, glossario, note](#r9-testo-elenchi-grassetto-link-glossario-note)
    - [R10. Fare la release di una consegna (RTB, PB)](#r10-fare-la-release-di-una-consegna-rtb-pb)
    - [R11. Cambiare i dati del gruppo](#r11-cambiare-i-dati-del-gruppo)
    - [R12. Verificare il lavoro di un altro (Verificatore)](#r12-verificare-il-lavoro-di-un-altro-verificatore)
    - [R13. Passare alla milestone successiva](#r13-passare-alla-milestone-successiva)
    - [R14. Caricare un verbale esterno firmato](#r14-caricare-un-verbale-esterno-firmato)
    - [R15. Aggiornare il sito: milestone, diapositive, gruppo](#r15-aggiornare-il-sito-milestone-diapositive-gruppo)
    - [R16. Il Glossario: crearlo, aggiungere termini, marcarli](#r16-il-glossario-crearlo-aggiungere-termini-marcarli)
5. [Le versioni: la regola semplice](#5-le-versioni-la-regola-semplice)
6. [Prontuario dei comandi](#6-prontuario-dei-comandi)
7. [Quando qualcosa va storto](#7-quando-qualcosa-va-storto)
8. [Impostazioni da fare una volta sola (Amministratori)](#8-impostazioni-da-fare-una-volta-sola-amministratori)
9. [Cosa è cambiato rispetto alla versione precedente](#9-cosa-è-cambiato-rispetto-alla-versione-precedente)

---

## 0. Le parole da conoscere

| Parola | Cosa vuol dire, in pratica |
| --- | --- |
| **Repository** (repo) | La cartella del progetto, salvata su GitHub con tutta la sua storia. |
| **Issue** | Un compito da fare, scritto su GitHub (es. "Scrivere il verbale del 26/10"). Ha un numero: `#12`. |
| **Branch** | Una copia di lavoro separata. Si lavora sempre in un branch, mai direttamente su `main`. |
| **`main`** | Il branch "ufficiale": quello che finisce sul sito. |
| **Commit** | Un salvataggio delle modifiche, con un messaggio che dice cosa avete fatto. |
| **Push** | Mandare i vostri commit su GitHub. |
| **Pull request** (PR) | La richiesta di unire il vostro branch a `main`. Lì il Verificatore controlla. |
| **Merge** | L'unione della PR in `main`. Dopo il merge il sito si aggiorna da solo. |
| **CI** / **Action** | I controlli automatici di GitHub: compilano i PDF e li commentano nella PR. |
| **Milestone** | Una delle tre consegne: **Candidatura**, **RTB** (Requirements and Technology Baseline), **PB** (Product Baseline). Ognuna ha la sua cartella. |
| **Chiave** | Il nome breve di una persona usato nei documenti: `guglielmo`, `corro`… (elenco in `template/dati-gruppo.tex`). |
| **Preambolo** | La parte del `.tex` **prima** di `\begin{document}`: lì si scrivono titolo, data, persone, registro. |
| **Registro delle modifiche** | La tabella con tutte le versioni del documento. Si scrive con le righe `\modifica{...}`. |

---

## 1. Prima volta: preparare il computer

Si fa **una volta sola**. Installate, in quest'ordine:

| Programma | Windows | macOS | Linux (Ubuntu/Debian) |
| --- | --- | --- | --- |
| **Git** | [git-scm.com](https://git-scm.com/download/win) (lasciate le opzioni predefinite) | nel terminale: `xcode-select --install` | `sudo apt install git` |
| **Python 3.9+** | [python.org](https://www.python.org/downloads/): spuntate **"Add python.exe to PATH"** | già incluso con il comando qui sopra | già presente (`python3`) |
| **TeX Live** | [TeX Live per Windows](https://tug.org/texlive/windows.html) (`install-tl-windows.exe`) | [MacTeX](https://tug.org/mactex/) | vedi comando qui sotto |
| **VS Code** | [code.visualstudio.com](https://code.visualstudio.com/) | idem | idem |

Su Linux, TeX Live si installa così:

```bash
sudo apt install latexmk texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended texlive-lang-italian texlive-pictures poppler-utils
```

(`poppler-utils` serve solo a vedere, nel sito di prova, l'anteprima della prima pagina dei documenti. Su Windows e macOS se ne può fare a meno: al posto dell'anteprima compare un riquadro con le iniziali. Sul sito vero le anteprime ci sono sempre.)

> ⚠️ Su Windows usate **TeX Live**, non MiKTeX: TeX Live include già Perl, che serve a `latexmk`.
> Se usate MiKTeX dovete installare anche [Strawberry Perl](https://strawberryperl.com/).

**Dite a Git chi siete** (con il vostro nome e la mail del vostro account GitHub):

```bash
git config --global user.name "Nome Cognome"
git config --global user.email "la.vostra@mail.it"
```

**Accesso a GitHub** (serve per fare push):

- **Windows**: niente da fare; la prima volta che fate push si apre il browser per l'accesso.
- **macOS / Linux**: installate [GitHub CLI](https://cli.github.com/) (`brew install gh` oppure `sudo apt install gh`), poi lanciate `gh auth login` e rispondete: *GitHub.com → HTTPS → Yes → Login with a web browser*.

**Scaricate il repository** (crea la cartella `docs` dove vi trovate):

```bash
git clone https://github.com/Git-Push-Team/docs.git
cd docs
```

**Apritelo in VS Code**: *File → Apri cartella…* e scegliete la cartella `docs`.
In basso a destra VS Code propone le **estensioni consigliate**: installatele (la più importante è *LaTeX Workshop*).

**Prova finale**: nel terminale di VS Code scrivete

```bash
python3 scripts/build.py
```

Deve finire con `Fatto: N PDF in site/`. Aprite il file `site/index.html` con il browser: vedete il sito con i PDF, divisi per milestone. Se funziona, siete pronti. ✅

---

## 2. Mappa del repository: cosa si tocca e cosa no

I documenti stanno in **tre cartelle, una per milestone**, tutte fatte allo stesso modo:

```text
docs/
├── Candidatura/
│   ├── documenti/
│   │   ├── esterni/      documenti a uso esterno (lettera di candidatura, preventivo…)
│   │   └── interni/      documenti a uso interno
│   └── verbali/
│       ├── esterni/      VE-AAAA-MM-GG.tex  (incontri con proponenti o docenti)
│       └── interni/      VI-AAAA-MM-GG.tex  (riunioni del gruppo)
├── RTB/                  stessa struttura
└── PB/                   stessa struttura
```

**Dove metto il mio file?** Rispondete a tre domande, una per livello di cartella:

| Domanda | Risposta → cartella |
| --- | --- |
| 1. Per quale consegna è? | `Candidatura/`, `RTB/` o `PB/` (quella **in corso**) |
| 2. È il verbale di un incontro? | sì → `verbali/`; no (Norme, Piani, lettere…) → `documenti/` |
| 3. Chi lo legge? | solo il gruppo → `interni/`; proponente o docenti → `esterni/` |

Esempi: riunione del gruppo del 3 novembre durante l'RTB → `RTB/verbali/interni/VI-2026-11-03.tex`; Norme di Progetto → `RTB/documenti/interni/norme-di-progetto/norme-di-progetto.tex`; lettera di presentazione per la PB → `PB/documenti/esterni/lettera-presentazione-pb.tex`.

Dentro queste cartelle potete creare sottocartelle a piacere (per esempio una per ogni documento con capitoli). I nomi `Candidatura`, `RTB`, `PB` vanno scritti **esattamente così**, maiuscole comprese: una cartella `rtb/` verrebbe ignorata (la PR ve lo segnala).

**E il PDF?** Non lo create voi. Dopo il merge la CI compila il documento e **salva il PDF accanto al `.tex`**, con lo stesso nome: accanto a `RTB/verbali/interni/VI-2026-11-03.tex` compare `VI-2026-11-03.pdf` (con un commit del bot *"Aggiorna i PDF accanto ai sorgenti"*). Lo stesso PDF va sul sito, con la versione nel nome. Il PDF che vedete mentre lavorate (VS Code o `build.py`) è una prova e resta in `build/`.

| Percorso | Cos'è | Si tocca? |
| --- | --- | --- |
| `Candidatura/`, `RTB/`, `PB/` | i `.tex` dei documenti e dei verbali, divisi come sopra | ✅ sì, i `.tex` |
| i `.pdf` accanto ai `.tex` | li crea e li aggiorna la CI dopo il merge | ❌ mai a mano (unica eccezione: [R14](#r14-caricare-un-verbale-esterno-firmato)) |
| `allegati/` | immagini usate nei documenti, in sottocartelle | ✅ sì |
| `template/modelli/` | i file **da copiare** per iniziare un documento | 👀 si copiano, non si modificano |
| `template/esempi/` | esempi completi da guardare quando non sapete come fare una cosa | 👀 solo da guardare |
| `template/dati-gruppo.tex` | nome, email e membri del gruppo | ⚠️ solo Amministratori ([R11](#r11-cambiare-i-dati-del-gruppo)) |
| `template/sito.toml` | impostazioni del sito: stato delle milestone, link extra, capitolato, account GitHub | ⚠️ solo Amministratori ([R15](#r15-aggiornare-il-sito-milestone-diapositive-gruppo)) |
| `<Milestone>/diapositive/` | PDF delle presentazioni e dei diari di bordo, fatti fuori da LaTeX | ✅ sì ([R15](#r15-aggiornare-il-sito-milestone-diapositive-gruppo)) |
| `template/gpt.cls` | la classe LaTeX: decide l'aspetto di tutti i documenti | ⚠️ solo Amministratori |
| `scripts/build.py`, `scripts/sito.py`, `latexmkrc`, `.github/`, `.vscode/` | compilazione, pagina del sito e automazioni | ⚠️ solo Amministratori |
| `build/`, `site/` | file generati dalla compilazione sul vostro computer (PDF di prova, sito di prova): si possono cancellare | ❌ non si caricano su GitHub (sono ignorati) |

Ecco come vengono i tre tipi di documento:

![Anteprima dei tipi di documento](template/anteprime/tipi-di-documento.png)

---

## 3. Il giro completo in 7 passi

Ogni lavoro, piccolo o grande, segue questo giro. L'esempio usa la issue `#12`.

**Passo 1 — La issue.** Su GitHub, scheda *Issues*: aprite la issue del vostro compito (o createla con *New issue → Attività*) e a destra in *Assignees* mettete voi stessi.

**Passo 2 — Aggiornate `main`.**

```bash
git checkout main
git pull
```

**Passo 3 — Create il vostro branch** (numero della issue + due parole, senza spazi):

```bash
git checkout -b doc/12-verbale-26-ottobre
```

**Passo 4 — Lavorate.** Seguite la ricetta giusta (sezione 4). Per vedere il PDF:

- in **VS Code**: salvate il file (`Ctrl+S`, su Mac `Cmd+S`); il PDF si apre in una scheda accanto (se non si apre: icona con la lente in alto a destra, *View LaTeX PDF*);
- oppure dal **terminale**: `python3 scripts/build.py Candidatura/verbali/interni/VI-2026-10-26.tex` → il PDF di prova è in `build/Candidatura/verbali/interni/` (e, con la versione nel nome, in `site/`).

Nessuno dei due mette il PDF accanto al `.tex`: quello lo fa la CI dopo il merge.

**Passo 5 — Salvate su GitHub** (commit + push):

```bash
git add -A
git commit -m "Verbale del 26/10: prima stesura"
git push -u origin doc/12-verbale-26-ottobre
```

Le volte successive, nello stesso branch, bastano `git add -A`, `git commit -m "..."` e `git push`.

**Passo 6 — Aprite la pull request.** Dopo il push, GitHub stampa un link `.../pull/new/doc/12-...`: apritelo (oppure sul sito del repo cliccate il pulsante giallo *Compare & pull request*). Poi:

1. nel testo, dopo `Closes #`, scrivete il numero della issue (`Closes #12`);
2. spuntate la *Checklist dell'autore*;
3. a destra, in *Reviewers*, scegliete il **Verificatore** (diverso da voi);
4. cliccate *Create pull request*.

**Passo 7 — Aspettate il commento automatico** (2–4 minuti). Nella scheda *Conversation* della PR compare il commento **📄 Anteprima dei documenti** con:

- la tabella dei documenti toccati, con ✅ o ❌;
- il link **Apri il PDF** (se avete cambiato un solo documento si apre nel browser; se sono di più, scaricate lo zip);
- se c'è un ❌, le righe d'errore con file e numero di riga: correggete, poi rifate il passo 5 (commit + push) e il commento si aggiorna da solo.

Quando il Verificatore approva (vedi [R12](#r12-verificare-il-lavoro-di-un-altro-verificatore)), si clicca **Merge pull request**. Dopo qualche minuto:

- il PDF è sul sito <https://git-push-team.github.io/docs/>, nella sezione della sua milestone; 🎉
- nel repository, accanto al vostro `.tex`, compare il `.pdf` con lo stesso nome (lo salva il bot).

Per questo, prima di iniziare un nuovo lavoro, rifate sempre il passo 2 (`git pull`): così avete anche i PDF aggiornati.

> 💡 Se nella PR compare *"This branch is out-of-date with the base branch"*, cliccate **Update branch**.

---

## 4. Ricette

### R1. Scrivere un verbale interno

**1. Copiate il modello** nella cartella `verbali/interni/` della milestone in corso, dandogli come nome la data della riunione (`VI-AAAA-MM-GG.tex`):

```bash
cp template/modelli/verbale-interno.tex Candidatura/verbali/interni/VI-2026-10-26.tex
```

(Durante l'RTB la cartella sarà `RTB/verbali/interni/`, durante la PB `PB/verbali/interni/`.)

(Su Windows potete anche copiare e rinominare il file da Esplora risorse.)

**2. Aprite il file e cambiate il preambolo** (le righe prima di `\begin{document}`):

| Riga | Cosa scrivere | Esempio |
| --- | --- | --- |
| `\titolo{...}` | di cosa si è parlato, in poche parole | `\titolo{Pianificazione dello sprint}` |
| `\data{...}` | data della riunione, **AAAA-MM-GG** | `\data{2026-10-26}` |
| `\orario{...}{...}` | ora di inizio e di fine | `\orario{21:00}{22:15}` |
| `\luogo{...}` | dove | `\luogo{Discord}` |
| `\redattore{...}` | **chiave** di chi scrive | `\redattore{mazzurana}` |
| `\verificatore{...}` | **chiave** di chi controlla (un Verificatore, diverso dal redattore) | `\verificatore{corro}` |
| `\componenti{...}` | chi faceva parte del gruppo quel giorno: **lasciatelo com'è** | (già pronto) |
| `\assenti{...}` | chiavi di chi mancava, separate da virgole; vuoto se c'erano tutti | `\assenti{spagnoli}` |
| `\modifica{0.1.0}{...}` | prima riga del registro: data di oggi e la vostra chiave | `\modifica{0.1.0}{2026-10-26}{mazzurana}{--}{Prima stesura}` |

> Le chiavi sono in `template/dati-gruppo.tex`: `biasini`, `cescobolla`, `corro`, `guglielmo`, `mazzurana`, `spagnoli`.
> Se ne scrivete una sbagliata, la compilazione si ferma e vi dice quali sono quelle giuste.

**3. Scrivete il contenuto** dopo `\begin{document}`. Il modello ha già le sezioni; i comandi speciali sono:

```latex
\section{Decisioni}
\begin{decisioni}
  \decisione{Le riunioni ordinarie si tengono il lunedì alle 21:00.}
  \decisione{Il template dei verbali è quello del repository docs.}
\end{decisioni}

\section{Azioni da intraprendere}
\begin{azioni}
  % \azione[numero issue]{cosa fare}{chi (chiavi)}{entro quando}
  \azione[\#14]{Preparare la bozza delle Norme.}{guglielmo,biasini}{02/11/2026}
  \azione{Studiare GitHub.}{tutti}{02/11/2026}
\end{azioni}
```

Le decisioni si numerano da sole (D1, D2…), le azioni pure (A1, A2…). `tutti` stampa "Tutto il gruppo".

**4. Consegnate** con il giro dei 7 passi. Quando il Verificatore approva, aggiunge lui in cima al registro la riga `1.0.0` (vedi [R12](#r12-verificare-il-lavoro-di-un-altro-verificatore)).

👀 Esempio completo: `template/esempi/esempio-verbale-interno.tex`.

---

### R2. Scrivere un verbale esterno

Come R1, ma con il modello esterno e il nome `VE-...`:

```bash
cp template/modelli/verbale-esterno.tex Candidatura/verbali/esterni/VE-2026-10-22.tex
```

In più rispetto al verbale interno, nel preambolo:

```latex
\esterno{Mariano Sciacco}{IoT \& Cloud Engineer, Vimar S.p.A.}   % una riga per persona esterna
\firma{Mariano Sciacco}{Vimar S.p.A.}                               % chi firma per l'azienda
\destinatari{Prof.~Tullio Vardanega\newline Prof.~Riccardo Cardin\newline Vimar S.p.A.}
```

e nel testo le domande con le risposte:

```latex
\section{Domande e risposte}
\domanda{Il deploy su AWS è obbligatorio?}{No, basta un'infrastruttura Docker Compose.}
```

In fondo al PDF compare da solo il riquadro **Approvazione** con lo spazio per la firma.

> ⚠️ **Firma dell'azienda**: dopo il merge, mandate all'azienda il PDF che la CI ha salvato accanto al `.tex`. Quando torna firmato, caricatelo accanto con un nome diverso: [R14](#r14-caricare-un-verbale-esterno-firmato). Il sito pubblica la versione compilata (senza firma).

👀 Esempio completo: `template/esempi/esempio-verbale-esterno.tex`.

---

### R3. Correggere un documento già approvato

Esempio: nel verbale `VI-2026-10-19` (versione `1.0.0`) c'è un nome sbagliato.

1. Giro dei 7 passi, passi 1–3 (issue, `main` aggiornato, branch `doc/15-correzione-verbale-19-10`).
2. Correggete il testo.
3. Aggiungete **in cima** al registro una riga con la versione nuova (regola nella [sezione 5](#5-le-versioni-la-regola-semplice)):

   ```latex
   \modifica{1.0.1}{2026-10-28}{guglielmo}{--}{Corretto il nome del responsabile}
   \modifica{1.0.0}{2026-10-19}{guglielmo}{corro}{Verifica e approvazione}
   \modifica{0.1.0}{2026-10-19}{guglielmo}{--}{Prima stesura}
   ```

4. Passi 5–7. Il Verificatore controlla e, se va bene, mette la sua chiave al posto di `--` nella riga nuova.

> La versione del PDF (copertina, piè di pagina e nome del file) cambia da sola: è sempre quella della **prima** riga.
> Non c'è nessun `\versione{}` da aggiornare.

---

### R4. Creare un documento (Norme, Piani, Analisi…)

**1. Create la cartella e copiate il modello.** La cartella va in `documenti/interni/` o `documenti/esterni/` della milestone in corso; il nome del file diventa il nome del PDF.

```bash
mkdir RTB/documenti/interni/norme-di-progetto
cp template/modelli/documento.tex RTB/documenti/interni/norme-di-progetto/norme-di-progetto.tex
```

Nomi suggeriti: `norme-di-progetto`, `piano-di-progetto`, `piano-di-qualifica`, `analisi-dei-requisiti`, `glossario`, `specifica-tecnica`, `manuale-utente`.

**2. Cambiate il preambolo:**

| Riga | Cosa scrivere |
| --- | --- |
| `\titolo{...}` | il nome del documento: `\titolo{Norme di Progetto}` |
| `\uso{...}` | `interno` o `esterno`, **come la cartella** (`documenti/interni/` → `interno`). Se non coincidono la PR ve lo segnala |
| `\responsabile{...}` | la chiave del Responsabile, che approva il documento |
| `\modifica{0.1.0}{...}` | la prima riga del registro |

**Registro dei documenti: più persone e approvatore.**

- In autore e verificatore potete mettere **più chiavi separate da virgole**: `\modifica{0.2.0}{2026-11-10}{mazzurana, biasini}{cescobolla}{Stesura sezione 2}`. In copertina ognuno compare una volta sola tra *Redattori* e *Verificatori*.
- Solo nei documenti, chi **approva** si scrive **in fondo alla riga, tra parentesi quadre** (anche più persone):

  ```latex
  \modifica{1.0.0}{2026-11-19}{--}{--}{Approvazione documento}[spagnoli]
  \modifica{0.3.0}{2026-11-17}{mazzurana}{corro}{Stesura sezione 3}
  ```

  La colonna **Approvatore** compare nel registro solo se almeno una riga ha le parentesi quadre; nelle altre righe c'è un trattino. Se non le usate mai, il registro resta a cinque colonne. Nei verbali l'approvatore non si usa: la compilazione si ferma e ve lo dice.

**Si fanno da soli**: copertina (con versione, data dell'ultima modifica, **redattori e verificatori presi dal registro**), registro delle modifiche, **indice**, elenco delle figure e delle tabelle (solo se ce ne sono), intestazioni e numeri di pagina.

**3. Scrivete** con `\section{...}`, `\subsection{...}`, `\subsubsection{...}`: compaiono da sole nell'indice.

**4. Consegnate** con il giro dei 7 passi. A ogni modifica successiva: nuova riga in cima al registro.

👀 Esempio completo: `template/esempi/esempio-documento/`.

---

### R5. Dividere un documento lungo in capitoli

Per documenti lunghi (Norme, Analisi) conviene **un file per capitolo**: si lavora in tanti senza pestarsi i piedi.

```text
RTB/documenti/interni/norme-di-progetto/
├── norme-di-progetto.tex        <- file principale: preambolo + elenco dei capitoli
└── capitoli/
    ├── introduzione.tex
    └── processi-di-supporto.tex
```

Nel file principale, dopo `\begin{document}`:

```latex
\input{capitoli/introduzione}
\input{capitoli/processi-di-supporto}
```

I file dei capitoli contengono **solo il testo** (niente `\documentclass`, niente `\begin{document}`). Mettete come **prima riga** di ogni capitolo:

```latex
% !TEX root = ../norme-di-progetto.tex
```

così, quando salvate un capitolo in VS Code, viene compilato il documento intero.

> Non serve fare altro: la CI capisce da sola che modificare un capitolo cambia il documento principale, lo compila e mette il suo PDF nel commento della PR.

---

### R6. Scrivere una lettera

Una lettera è un documento esterno: va in `documenti/esterni/` della sua milestone.

```bash
cp template/modelli/lettera.tex RTB/documenti/esterni/lettera-presentazione-rtb.tex
```

Preambolo:

| Riga | Cosa scrivere |
| --- | --- |
| `\titolo{...}` | nome della lettera (sito e PDF): `\titolo{Lettera di presentazione RTB}` |
| `\oggetto{...}` | la riga "Oggetto:" (se manca, si usa il titolo) |
| `\data{...}` e `\luogo{...}` | data (AAAA-MM-GG) e città: compaiono come "Padova, 15 gennaio 2027" |
| `\responsabile{...}` | chi firma: il Responsabile |
| `\destinatari{...}` | facoltativo: se manca valgono i due docenti di `dati-gruppo.tex` |

Dopo `\begin{document}` scrivete solo il testo, dal saluto iniziale in poi. Carta intestata, data, destinatari, oggetto, "Cordiali saluti," e firma si aggiungono da soli. La lettera **non ha registro**.

👀 Esempio completo: `template/esempi/esempio-lettera.tex`.

---

### R7. Inserire un'immagine

1. Mettete l'immagine (PNG, JPG o PDF) in una sottocartella di `allegati/`, per esempio `allegati/2026-10-26/schema-architettura.png`. Nomi **senza spazi né accenti**.
2. Nel testo, indicate il percorso **a partire da `allegati/`**:

```latex
\figura{2026-10-26/schema-architettura.png}{Schema dell'architettura proposta}
```

- larghezza diversa (frazione della riga, predefinito 0.85): `\figura[0.5]{...}{...}`
- senza cornice (foto, loghi): `\figurasenzabordo{...}{...}`
- per citarla nel testo, aggiungete un'etichetta nella didascalia e usate `\ref`:

```latex
\figura{2026-10-26/schema-architettura.png}{Schema dell'architettura\label{fig:architettura}}
Come si vede in Figura~\ref{fig:architettura}, ...
```

Le figure si numerano da sole; nei documenti compare anche l'*Elenco delle figure*.

---

### R8. Inserire una tabella

Copiate questo blocco e cambiate il contenuto. `&` separa le colonne, `\\` chiude la riga.

```latex
\begin{table}[H]
  \centering
  \caption{Ore previste per ruolo\label{tab:ore}}
  \begin{tabular}{@{}lr@{}}
    \toprule
    \intestazione{Ruolo} & \intestazione{Ore} \\
    \midrule
    Responsabile  & 10 \\
    Verificatore  & 25 \\
    \bottomrule
  \end{tabular}
\end{table}
```

- `{@{}lr@{}}` = due colonne: la prima allineata a sinistra (`l`), la seconda a destra (`r`); `c` = centrata.
- Per colonne con testo lungo che va a capo usate `p{4cm}` al posto di `l`.
- Citatela con `Tabella~\ref{tab:ore}`. Nei documenti compare anche l'*Elenco delle tabelle*.

👀 Esempio: `template/esempi/esempio-documento/capitoli/processi.tex`.

---

### R9. Testo: elenchi, grassetto, link, glossario, note

```latex
\textbf{grassetto}   \emph{corsivo}

\begin{itemize}          % elenco puntato
  \item primo
  \item secondo
\end{itemize}

\begin{enumerate}        % elenco numerato
  \item primo
  \item secondo
\end{enumerate}

\url{https://git-push-team.github.io/docs/}          % link
\href{https://github.com/Git-Push-Team}{il nostro GitHub}   % link con testo

\glo{repository}         % termine del Glossario: aggiunge la G a pedice
\glo[pull request]{pull requests}   % testo diverso dalla voce (plurale): R16

\begin{nota}[Attenzione]
Un riquadro colorato per mettere in evidenza qualcosa.
\end{nota}

\nome{spagnoli}          % stampa "Gaetano Spagnoli"
\nomi{guglielmo,corro}   % stampa "Francesco Guglielmo, Alessio Corrò"
```

Altre regole utili:

- **Una riga vuota** = nuovo paragrafo. Andare a capo nel file non basta.
- Le lettere accentate si scrivono normalmente: `è`, `perché`, `Corrò`.
- Questi caratteri vanno scritti con la barra davanti: `\%` `\&` `\_` `\#` `\$`.
  Attenzione soprattutto a `%`: senza la barra, **tutto il resto della riga sparisce** (diventa un commento).
- Per non spezzare a fine riga "Prof. Rossi" o "Figura 3" usate la tilde: `Prof.~Rossi`, `Figura~\ref{...}`.

---

### R10. Fare la release di una consegna (RTB, PB)

Quando tutto per la consegna è unito in `main` e il sito è aggiornato, un Amministratore lancia:

```bash
git checkout main
git pull
git tag rtb-v1
git push origin rtb-v1
```

Dopo qualche minuto, nella pagina del repository, sezione *Releases*, compare **"Consegna rtb-v1"** con i PDF della cartella `RTB/` allegati uno per uno e uno zip che mantiene le cartelle (`documenti/esterni`, `verbali/interni`…). È la "fotografia" ufficiale della consegna, e resta lì anche quando i documenti cambieranno per la PB. Il sito ha in fondo il link *Archivio delle consegne* che porta a questa pagina.

- Il nome del tag sceglie la cartella: `candidatura…` → `Candidatura/`, `rtb…` → `RTB/`, `pb…` → `PB/` (es. `candidatura-v1`, `rtb-v1`, `pb-v1`).
- ⚠️ Create **solo il tag** con i comandi qui sopra: non create la release a mano dal sito, altrimenti l'automazione trova la release già esistente e si ferma.

---

### R11. Cambiare i dati del gruppo

Tutti questi casi riguardano gli **Amministratori** e vanno fatti con una pull request.

**Entra un nuovo membro.**

1. In `template/dati-gruppo.tex` aggiungete una riga: `\membro{rossi}{Mario Rossi}{2150000}` (chiave minuscola, senza spazi né accenti).
2. Aggiungete la chiave a `\componenti{...}` in `template/modelli/verbale-interno.tex` e `template/modelli/verbale-esterno.tex`.

**Qualcuno lascia il gruppo.**

1. **Non** cancellate la sua riga da `template/dati-gruppo.tex`: i verbali vecchi la usano ancora (e se la cancellate, non compilano più).
2. Togliete la sua chiave da `\componenti{...}` nei due modelli dei verbali: dai verbali nuovi in poi non comparirà più.

**Dopo l'assegnazione del capitolato.**

1. Nei modelli (`template/modelli/*.tex`) togliete il `%` davanti alla riga `\capitolato{...}` e scrivete il capitolato vero, es. `\capitolato{C2 -- NEXUM Concierge (Eggon S.r.l.)}`.
2. Fate lo stesso nei documenti scritti **da quel momento in poi**.
3. **Mai** in `template/dati-gruppo.tex`: cambierebbe anche i verbali vecchi. (La compilazione si ferma se ci provate.)

**Cambiano i destinatari predefiniti**: riga `\destinatari{...}` in `template/dati-gruppo.tex`. Un singolo documento può avere destinatari diversi scrivendo `\destinatari{...}` nel suo preambolo.

---

### R12. Verificare il lavoro di un altro (Verificatore)

Vi arriva una richiesta di revisione (mail o campanella di GitHub).

1. Aprite la PR. Nella scheda **Conversation** trovate il commento **📄 Anteprima dei documenti**: cliccate **Apri il PDF** e leggetelo **per intero**.
2. Nella scheda **Files changed** vedete le righe modificate (verde = aggiunto, rosso = tolto). Per segnalare un problema su una riga, passateci sopra col mouse e cliccate il **+** blu.
3. Seguite la *Checklist del Verificatore* nella descrizione della PR.
4. **Se ci sono cose da correggere**: *Review changes* (o *Submit review*) → **Request changes** → spiegate cosa sistemare. L'autore corregge e fa push; voi rileggete.
5. **Se è tutto a posto**, registrate la verifica nel registro, direttamente dal sito:
    - in *Files changed*, sul file `.tex`, menu **⋯** → **Edit file**;
    - **prima approvazione** (il documento è a `0.x.0`): in cima al registro aggiungete

      ```latex
      \modifica{1.0.0}{2026-10-27}{mazzurana}{corro}{Verifica e approvazione}
      ```

      (versione `1.0.0`, data di oggi, chiave dell'autore, **la vostra chiave**);
    - **modifica a un documento già approvato** (es. riga `1.1.0` con `--`): scrivete la vostra chiave al posto di `--` nella riga in cima;
    - in basso, *Commit changes* (lasciate "Commit directly to the doc/… branch").
6. Aspettate che il commento automatico torni ✅ con la nuova versione, poi *Review changes* → **Approve** → *Submit review*.
7. Cliccate **Merge pull request** → *Confirm merge*. Fatto: il sito si aggiorna da solo e il bot salva il PDF accanto al `.tex`.

---

### R13. Passare alla milestone successiva

Ogni file vive in **una sola cartella**: non si fanno copie (due copie dello stesso documento finirebbero per divergere).

- **Verbali**: restano dove sono. I verbali dell'RTB stanno in `RTB/verbali/`; dalla prima riunione dopo l'RTB si scrive in `PB/verbali/`.
- **Documenti che continuano** (Norme, Piani, Analisi, Glossario…): all'inizio dei lavori per la milestone nuova, un Amministratore li **sposta** con una PR, per esempio:

  ```bash
  git checkout main
  git pull
  git checkout -b doc/40-norme-verso-pb
  git mv RTB/documenti/interni/norme-di-progetto PB/documenti/interni/norme-di-progetto
  git commit -m "Norme di Progetto: si lavora per la PB"
  git push -u origin doc/40-norme-verso-pb
  ```

  Dopo il merge il bot mette il PDF nella cartella nuova e toglie quello rimasto nella vecchia. La versione consegnata all'RTB non si perde: è nella release *Consegna rtb-…* ([R10](#r10-fare-la-release-di-una-consegna-rtb-pb)) e nella storia di Git.
- **Il Glossario è uno solo** e si sposta come gli altri documenti che continuano (cartella intera, con `capitoli/`). Se per sbaglio ne restano due copie, la PR lo segnala.
- **Prima di spostare**, assicuratevi che la release della milestone appena chiusa sia stata fatta.

---

### R14. Caricare un verbale esterno firmato

L'unico PDF che si carica a mano è la copia firmata dal proponente. Salvatela **accanto al `.tex`** con `-firmato` in fondo al nome:

```text
RTB/verbali/esterni/VE-2026-11-05.tex           <- scritto da voi
RTB/verbali/esterni/VE-2026-11-05.pdf           <- creato dal bot
RTB/verbali/esterni/VE-2026-11-05-firmato.pdf   <- la scansione firmata, caricata da voi
```

Poi il solito giro (branch, commit, push, PR). Il bot non tocca mai i file `-firmato.pdf`, e la PR non li segnala come errore. Sul sito, accanto al verbale compare il pulsante **Firmato** che apre la copia firmata.

---

### R15. Aggiornare il sito: milestone, diapositive, gruppo

Il sito si costruisce da solo dai documenti. Le poche cose che nei documenti non ci sono si scrivono in **`template/sito.toml`** (con una PR, come sempre). Il file è commentato riga per riga.

**Cosa mostra il sito**, dall'alto:

1. il **grafo delle milestone**: Candidatura → RTB → PB, con un pallino per ogni verbale. Cliccando una milestone si va ai suoi documenti;
2. la **milestone in corso**: la lettera di presentazione in evidenza, poi documenti esterni e interni con l'anteprima della prima pagina, poi i verbali esterni e interni;
3. le **diapositive**, se ce ne sono;
4. l'**archivio**: le altre milestone con documenti, ognuna in un riquadro che si apre;
5. **il gruppo** (membri, capitolato) e i **contatti**.

In alto c'è la **ricerca** (tasto `/` per andarci): filtra documenti e verbali mentre scrivete.

**Cambiare la milestone in corso** (per esempio dopo la consegna della candidatura). In `template/sito.toml`:

```toml
[milestone.Candidatura]
stato = "conclusa"

[milestone.RTB]
stato = "in corso"
```

La Candidatura passa nell'archivio e l'RTB va in cima. Gli stati possibili sono `"da iniziare"`, `"in corso"` e `"conclusa"`.

**Aggiungere un pulsante a una milestone** (Proof of Concept, MVP, glossario online…):

```toml
[milestone.RTB]
stato = "in corso"
link = [ { testo = "Proof of Concept", url = "https://github.com/Git-Push-Team/poc" } ]
```

**Dopo l'assegnazione del capitolato**: compilate `capitolato`, `proponente` e, se volete, `descrizione` nella sezione `[progetto]`. Compaiono nella sezione *Il gruppo*.

**Foto dei membri**: nella sezione `[github]` scrivete il nome utente GitHub di ognuno (senza `@`), es. `guglielmo = "fguglielmo"`. Chi resta vuoto ha le iniziali al posto della foto.

**Diapositive e diari di bordo**: sono PDF fatti fuori da LaTeX (Google Slides, PowerPoint…). Esportateli in PDF e metteteli in `diapositive/` dentro la milestone:

```text
RTB/diapositive/presentazione-rtb.pdf    -> "Presentazione RTB", con anteprima
RTB/diapositive/diario-2026-11-14.pdf    -> "Diario di bordo, 14 novembre 2026"
```

I file che iniziano con `diario` (oppure `DDB`, es. `DDB-2026-10-26.pdf`) e contengono una data finiscono tra i *Diari di bordo*; tutti gli altri tra le *Presentazioni*, con il titolo preso dal nome del file. Questi PDF si caricano normalmente con commit e PR: la CI non li tocca.

---

### R16. Il Glossario: crearlo, aggiungere termini, marcarli

Il Glossario è **un solo documento**, nella milestone in corso, con **una lettera per file**. Da lì nascono tre cose: il PDF del Glossario, i controlli nelle PR e la pagina **Glossario** del sito.

**Crearlo (una volta sola, un Amministratore).** Copiate l'intera cartella del modello nella milestone in corso:

```bash
cp -r template/modelli/glossario RTB/documenti/esterni/glossario
```

Viene fuori così:

```text
RTB/documenti/esterni/glossario/
├── glossario.tex      <- il documento: titolo, registro, nient'altro da toccare
└── capitoli/
    ├── a.tex          <- le voci che iniziano per A
    └── r.tex          <- ... per R (cancellate le voci di esempio)
```

**Aggiungere un termine.**

1. Aprite il file della sua lettera, per esempio `capitoli/p.tex`. Se non esiste, copiate `capitoli/a.tex` con il nome della lettera e cambiate la riga `\letteraglossario{A}` in `\letteraglossario{P}`. Non serve toccare `glossario.tex`: le lettere nuove si includono da sole.
2. Aggiungete la voce **al suo posto in ordine alfabetico**:

   ```latex
   \termine{Pull request}{Richiesta di unire le modifiche di un branch al
     branch principale, dopo la verifica di un altro membro del gruppo.}
   ```

3. Nella definizione potete usare `\emph{}`, `\textbf{}`, `\url{}` e `\glo{}` (se anche quel termine è nel Glossario: sul sito diventa un link). Niente tabelle, immagini o elenchi.
4. Aggiungete una riga in cima al registro di `glossario.tex`, come per ogni documento.

**Marcare un termine nei documenti.** Dove il termine compare nel testo:

```latex
Ogni modifica passa da una \glo{pull request}.            % stessa forma della voce
Abbiamo aperto tre \glo[pull request]{pull requests}.     % forma diversa: la voce va tra [ ]
```

Maiuscole e spazi non contano: `\glo{Pull Request}` e `\glo{pull request}` sono la stessa voce. Quante volte marcare un termine (ogni volta, o solo la prima in ogni documento) lo decidono le Norme di Progetto.

**Il termine nuovo va nel Glossario nella stessa PR in cui lo marcate.** Nella PR il commento automatico ha una parte **📖 Glossario** che segnala:

| Messaggio | Cosa fare |
| --- | --- |
| *"…" è marcato con \glo in `file:riga` ma non è nel Glossario* | aggiungete la voce, oppure controllate di averla scritta uguale (o usate `\glo[voce]{testo}`) |
| *La voce "…" è ripetuta* | tenete una sola delle due definizioni |
| *Le voci non sono in ordine alfabetico* / *è nella lettera sbagliata* | spostate la voce al suo posto |
| *La voce "…" non ha una definizione* | scrivetela |
| *C'è più di un Glossario* | è rimasta una copia (succede spostandolo di milestone): cancellate quella vecchia |
| *Voci del Glossario non marcate in nessun documento* (in corsivo) | solo un'informazione: va bene se sono termini utili |

Come funzionano i controlli:

- nelle PR normali si controllano solo i file toccati; se la PR cambia il Glossario si controllano tutti i documenti;
- le milestone segnate `"conclusa"` in `template/sito.toml` non si controllano: i documenti già consegnati non danno avvisi;
- **per ora gli avvisi non bloccano la PR.** Quando il Glossario è a regime, per esempio prima dell'RTB, un Amministratore può renderli bloccanti: in `scripts/glossario.py` cambia `BLOCCANTE = False` in `BLOCCANTE = True`. Da quel momento termini mancanti, voci ripetute e Glossari doppi rendono rossa la PR.

**Sul sito**: appena il Glossario esiste, nella barra in alto compare **Glossario**. È una pagina con le lettere, le voci in ordine, la ricerca e il link al PDF. Ogni voce ha il suo indirizzo, per esempio `…/glossario.html#pull-request`: si può mandare il link a un termine preciso.

---

## 5. Le versioni: la regola semplice

La versione ha tre numeri `X.Y.Z` ed è **sempre quella della prima riga del registro**. Regola proposta (confermatela nelle Norme di Progetto):

| Quando | Versione nuova | Esempio di riga |
| --- | --- | --- |
| Prima stesura | `0.1.0` | `\modifica{0.1.0}{2026-10-26}{guglielmo}{--}{Prima stesura}` |
| Ogni modifica prima della verifica | `0.2.0`, `0.3.0`, … | `\modifica{0.2.0}{2026-10-27}{guglielmo}{--}{Aggiunta sezione 2}` |
| Verifica e approvazione | `1.0.0` | `\modifica{1.0.0}{2026-10-28}{guglielmo}{corro}{Verifica e approvazione}` |
| Modifica dopo l'approvazione | `1.1.0`, `1.2.0`, … | `\modifica{1.1.0}{2026-11-10}{biasini}{corro}{Aggiunti i casi d'uso}` |
| Correzione piccolissima (refuso) | `1.1.1` | `\modifica{1.1.1}{2026-11-12}{biasini}{corro}{Corretto un refuso}` |
| Nuova approvazione per una consegna successiva | `2.0.0` | `\modifica{2.0.0}{2027-03-01}{...}{...}{Approvazione per la PB}` |

Nei **documenti** chi approva si può indicare in fondo alla riga, tra parentesi quadre: `\modifica{1.0.0}{2026-11-19}{--}{--}{Approvazione documento}[spagnoli]` (vedi [R4](#r4-creare-un-documento-norme-piani-analisi)). Autore e verificatore possono essere più persone, separate da virgole.

Cosa controlla la classe da sola: che la versione abbia tre numeri, che la data sia `AAAA-MM-GG`, che **ogni riga sia più vecchia di quella sopra** e che nessuna versione sia ripetuta. Se sbagliate, la compilazione si ferma e vi dice cosa correggere.

---

## 6. Prontuario dei comandi

**Nel preambolo** (prima di `\begin{document}`):

| Comando | Dove | Esempio | Cosa fa |
| --- | --- | --- | --- |
| `\documentclass[...]{gpt}` | tutti | `\documentclass[verbale=interno]{gpt}` | sceglie il tipo: `verbale=interno`, `verbale=esterno`, `documento`, `lettera` |
| `\titolo{}` | tutti | `\titolo{Analisi dei Requisiti}` | titolo (copertina, sito, PDF) |
| `\data{}` | verbali, lettere | `\data{2026-10-26}` | data della riunione o della lettera |
| `\orario{}{}` | verbali | `\orario{21:00}{22:30}` | inizio e fine |
| `\luogo{}` | verbali, lettere | `\luogo{Discord}` | luogo (nella lettera, la città) |
| `\redattore{}` `\verificatore{}` | verbali | `\redattore{corro}` | chi scrive e chi controlla |
| `\componenti{}` | verbali | `\componenti{biasini,...}` | chi faceva parte del gruppo quel giorno |
| `\assenti{}` | verbali | `\assenti{corro,spagnoli}` | chi mancava |
| `\esterno{}{}` | verbali esterni | `\esterno{Nome}{Ruolo, Azienda}` | una persona esterna presente |
| `\firma{}{}` | verbali esterni | `\firma{Nome}{Azienda}` | chi firma per l'azienda |
| `\uso{}` | documenti | `\uso{interno}` | `interno` o `esterno` |
| `\responsabile{}` | documenti, lettere | `\responsabile{spagnoli}` | chi approva (documento) o firma (lettera) |
| `\oggetto{}` `\chiusura{}` | lettere | `\oggetto{Candidatura}` | riga "Oggetto:" e saluto finale |
| `\capitolato{}` | tutti, facoltativo | `\capitolato{C2 -- NEXUM Concierge}` | riga "Capitolato" in copertina |
| `\destinatari{}` | tutti, facoltativo | `\destinatari{A\newline B}` | cambia i destinatari predefiniti |
| `\modifica{}{}{}{}{}` | verbali, documenti | `\modifica{0.1.0}{2026-10-26}{corro, biasini}{--}{Prima stesura}` | una riga del registro (la più recente in cima); più persone separate da virgole |
| `\modifica{}{}{}{}{}[]` | solo documenti | `\modifica{1.0.0}{2026-11-19}{--}{--}{Approvazione}[spagnoli]` | come sopra, con l'approvatore tra `[ ]`: aggiunge la colonna *Approvatore* |

**Nel testo** (dopo `\begin{document}`):

| Comando | Cosa fa |
| --- | --- |
| `\section{}` `\subsection{}` `\subsubsection{}` | titoli numerati (finiscono nell'indice) |
| `\begin{decisioni} \decisione{...} \end{decisioni}` | tabella delle decisioni D1, D2… |
| `\begin{azioni} \azione[\#12]{cosa}{chi}{quando} \end{azioni}` | tabella delle azioni A1, A2… |
| `\domanda{domanda}{risposta}` | domanda e risposta (verbali esterni) |
| `\figura[0.6]{cartella/file.png}{didascalia}` | immagine con cornice (da `allegati/`) |
| `\figurasenzabordo{...}{...}` | immagine senza cornice |
| `\begin{nota}[Titolo] ... \end{nota}` | riquadro di nota |
| `\glo{termine}` / `\glo[voce]{testo}` | termine del Glossario (G a pedice); tra `[ ]` la voce, se il testo è diverso ([R16](#r16-il-glossario-crearlo-aggiungere-termini-marcarli)) |
| `\letteraglossario{A}` / `\termine{Voce}{Definizione}` | solo nel Glossario: titolo di una lettera e una voce ([R16](#r16-il-glossario-crearlo-aggiungere-termini-marcarli)) |
| `\nome{chiave}` / `\nomi{a,b}` | nome e cognome dei membri |
| `\intestazione{Testo}` | intestazione di colonna nello stile delle tabelle del gruppo |
| `\datariunione` / `\codiceverbale` | data lunga e codice del verbale (es. VI 2026-10-26) |

**Nel terminale**:

| Comando | Cosa fa |
| --- | --- |
| `python3 scripts/build.py` | compila tutti i documenti e crea il sito in `site/` |
| `python3 scripts/build.py percorso/file.tex` | compila un solo documento (PDF di prova in `build/`) |
| `python3 scripts/build.py RTB` | compila solo i documenti di una cartella (qui: tutta la milestone RTB) |
| `python3 scripts/build.py --esempi` | compila anche modelli ed esempi (utile dopo aver toccato la classe) |
| `python3 scripts/build.py --list` | elenca i documenti trovati, con versione, milestone e sezione del sito |
| `python3 scripts/build.py --clean` | cancella `build/` e `site/` e ricompila tutto da capo |

---

## 7. Quando qualcosa va storto

Dove leggere l'errore: nella **PR**, nel commento automatico (righe `file:riga: messaggio`); in **VS Code**, nel pannello *Problemi* (`Ctrl+Shift+M`); nel **terminale**, in fondo all'output di `build.py`. La riga che inizia con `l.` seguito da un numero mostra il punto esatto del testo.

**Messaggi della nostra classe** (iniziano con `Class gpt Error:`):

| Messaggio (in breve) | Cosa fare |
| --- | --- |
| `Membro "xyz" sconosciuto. Chiavi valide: ...` | Chiave scritta male: copiatela dall'elenco nel messaggio. |
| `Registro delle modifiche in ordine sbagliato` | La riga più recente va **in cima**; ogni versione una volta sola. |
| `la versione "..." non va bene. Scrivetela cosi': X.Y.Z` | Tre numeri separati da punti: `1.0.0`, non `1.0`. |
| `la data "..." non va bene. Scrivetela cosi': AAAA-MM-GG` | `2026-10-06`, non `6/10/2026` né `2026-10-6`. |
| `\versione non serve piu'` | Cancellate la riga `\versione{...}`: la versione si prende dal registro. |
| `Manca l'elenco dei componenti` | Copiate la riga `\componenti{...}` dal modello del verbale. |
| `"xyz" e' in \assenti ma non in \componenti` | Chi è assente deve comparire anche tra i componenti. |
| `Manca il titolo` / `Manca la data` / `Il registro delle modifiche e' vuoto` | Aggiungete la riga che manca nel preambolo (vedete il modello). |
| `\uso: scrivete interno oppure esterno` | Solo queste due parole. |
| `Opzione "verbale=..." non valida` | Prima riga: `[verbale=interno]` o `[verbale=esterno]`. |
| `\capitolato non va in dati-gruppo.tex` | Scrivetelo nel singolo documento ([R11](#r11-cambiare-i-dati-del-gruppo)). |
| `L'approvatore [...] si usa solo nei documenti, non nei verbali` | Togliete la parte tra parentesi quadre in fondo alla riga `\modifica` del verbale. |

**Errori classici di LaTeX:**

| Messaggio | Causa probabile | Cosa fare |
| --- | --- | --- |
| `Undefined control sequence` | comando scritto male (es. `\sectoin`) | guardate la riga `l.NN`: correggete il comando |
| `Missing $ inserted` | `_` o `^` nel testo normale | scrivete `\_` |
| `Misplaced alignment tab character &` | `&` nel testo normale | scrivete `\&` |
| `File '...png' not found` | percorso dell'immagine sbagliato | il percorso parte da `allegati/` (vedi [R7](#r7-inserire-unimmagine)) |
| `Runaway argument` / `File ended while scanning` / `Paragraph ended before ...` | manca una `}` | contate le graffe nella riga indicata |
| `Extra }, or forgotten \endgroup` | una `}` di troppo | togliete la graffa in più |
| `\begin{...} ended by \end{document}` | manca un `\end{...}` | chiudete l'ambiente (`itemize`, `azioni`…) |
| `There's no line here to end` | `\\` usato per andare a capo nel testo | lasciate una riga vuota |
| Un pezzo di testo sparisce | c'è un `%` senza barra | scrivete `\%` |

**Problemi di Git e GitHub:**

| Problema | Cosa fare |
| --- | --- |
| `! [rejected] ... (fetch first)` facendo push | prima `git pull`, poi di nuovo `git push` |
| `Your local changes would be overwritten` | fate prima commit (`git add -A` e `git commit -m "..."`) |
| La PR dice *out-of-date with the base branch* | pulsante **Update branch** nella PR |
| La PR ha un **conflitto** | chiedete a un Amministratore: è normale, si risolve in due minuti |
| Il commento dice ⚠️ *Documenti NON toccati da questa pull request che però non compilano* | non è colpa vostra: avvisate gli Amministratori (`main` ha un problema) |
| Il commento dice ❌ *Questa pull request contiene PDF che crea da sola la CI* | avete caricato un PDF che fa il bot (succede se compilate con un editor diverso da VS Code, che mette il PDF accanto al `.tex`). **Cancellate quel PDF**: sul computer eliminatelo dalla cartella, poi commit e push; oppure sul sito di GitHub aprite il file nel vostro branch → **⋯** → *Delete file* → *Commit changes*. Dopo il merge il bot lo rigenera |
| Il commento dice ⚠️ *Da controllare* | il file è in una cartella che non torna col contenuto (es. un verbale interno in `verbali/esterni/`, o `\uso{esterno}` in `documenti/interni/`), oppure è fuori da `Candidatura/`, `RTB/`, `PB/`. Non blocca la PR, ma sistematelo: spostate il file o correggete la riga indicata |
| GitHub Desktop / `git status` mostra un `.pdf` modificato accanto a un `.tex` | l'avete ricompilato con un altro editor. Annullate la modifica: in GitHub Desktop tasto destro sul file → *Discard changes*; da terminale `git restore percorso/file.pdf` |
| Dopo il merge il PDF accanto al `.tex` non compare | nella scheda *Actions*, esecuzione *Pubblica il sito*: se c'è l'avviso *PDF non salvati*, manca la configurazione della chiave del bot ([sezione 8](#8-impostazioni-da-fare-una-volta-sola-amministratori), passi A–F). Il sito invece è aggiornato |

**Problemi del computer:**

| Problema | Cosa fare |
| --- | --- |
| `latexmk non trovato` / `latexmk is not recognized` | TeX Live non è installato, oppure il terminale era aperto prima dell'installazione: chiudete e riaprite VS Code |
| `python: command not found` | su macOS/Linux scrivete `python3`; su Windows provate `py` |
| In VS Code (con TeX Live 2025 o più recente) compare `ignored error: Infinite glue shrinkage found in box being split` | è un avviso innocuo di LaTeX quando una tabella lunga va a capo pagina: il PDF è corretto, ignoratelo |

**Problemi del sito:**

| Problema | Cosa fare |
| --- | --- |
| `Errore in template/sito.toml: ...` (nel terminale o nella scheda *Actions*) | c'è un errore di scrittura nella riga indicata: di solito manca una virgoletta (`"testo"`) o una parentesi. Confrontate con le righe vicine ([R15](#r15-aggiornare-il-sito-milestone-diapositive-gruppo)) |
| `Attenzione: con Python più vecchio del 3.11 il sito usa le impostazioni predefinite` | succede solo in locale: il vostro sito di prova ignora `sito.toml`. Installate Python 3.11 o più recente (oppure `pip install tomli`). Il sito vero non ha questo problema |
| Nel sito di prova, al posto dell'anteprima dei documenti c'è un riquadro con le iniziali | manca `pdftoppm` sul vostro computer: è normale su Windows e macOS (su Linux: `sudo apt install poppler-utils`). Il sito vero ha sempre le anteprime |
| In cima al sito compare la milestone sbagliata | in `template/sito.toml` cambiate lo `stato` delle milestone: quella mostrata in cima è la prima `"in corso"` ([R15](#r15-aggiornare-il-sito-milestone-diapositive-gruppo)) |
| Un membro non ha la foto | il suo nome utente GitHub manca o è sbagliato nella sezione `[github]` di `template/sito.toml` (senza `@`) |
| Una presentazione finisce tra i diari di bordo (o viceversa) | contano solo il nome del file e la cartella: i diari di bordo iniziano con `diario` e contengono la data (`diario-2026-11-14.pdf`), e tutti stanno in `<Milestone>/diapositive/` |
| Nelle *Actions*, il passo *Compila* dice `Nessun documento da compilare` e il sito è vuoto | i `.tex` non sono dentro `Candidatura/`, `RTB/` o `PB/` (scritte esattamente così, maiuscole comprese): per esempio sono ancora nelle vecchie cartelle `verbali/`, `documenti/`. Gli avvisi gialli nella pagina dell'Action dicono quali file spostare |
| La voce **Glossario** non compare nel menu del sito | il Glossario non esiste ancora, oppure non ha voci `\termine{…}{…}` ([R16](#r16-il-glossario-crearlo-aggiungere-termini-marcarli)) |
| Il commento della PR ha una parte **📖 Glossario** | termini marcati che mancano nel Glossario, voci doppie o fuori ordine: la tabella in [R16](#r16-il-glossario-crearlo-aggiungere-termini-marcarli) dice cosa fare |
| Il pulsante **Firmato** non compare | la copia firmata deve stare accanto al `.tex` con lo stesso nome più `-firmato`: `VE-2026-11-05-firmato.pdf` accanto a `VE-2026-11-05.tex` ([R14](#r14-caricare-un-verbale-esterno-firmato)) |

---

## 8. Impostazioni da fare una volta sola (Amministratori)

Sul sito di GitHub, nella pagina del repository `docs`, scheda **Settings**:

1. **Pages** → *Build and deployment* → *Source*: **GitHub Actions**. Senza questo il sito non si pubblica. (Con il piano gratuito di GitHub, Pages funziona solo se il repository è **pubblico**.)
2. **Issues → Labels** (dalla scheda *Issues*, pulsante *Labels*): create le etichette `documentazione` ed `errore`, usate dai modelli delle issue.
3. **La chiave del bot e la protezione di `main`**: passi A–F qui sotto.

### La chiave del bot e la protezione di `main`

`main` è protetto: si cambia solo con una pull request approvata. Il bot che salva i PDF accanto ai `.tex` però scrive su `main` **dopo** il merge, senza PR, quindi gli serve un permesso speciale. GitHub non lo concede al bot normale delle Actions: lo si dà a una **chiave di deployment** (*deploy key*) che solo il bot conosce. Se saltate questa parte non si rompe niente: il sito si aggiorna lo stesso, solo che i PDF non compaiono accanto ai `.tex` (nella scheda *Actions* compare un avviso).

**A. Create la coppia di chiavi** (sul vostro computer, una volta sola). Nel terminale (su Windows va bene PowerShell o *Git Bash*), in una cartella **fuori** dal repository, per esempio il Desktop:

```bash
ssh-keygen -t ed25519 -C "bot-pdf-docs" -f chiave-pdf
```

Quando chiede la *passphrase* premete **Invio due volte** (deve restare vuota). Nascono due file: `chiave-pdf.pub` (la parte pubblica) e `chiave-pdf` (la parte segreta).

**B. Date a GitHub la parte pubblica.** Nel repository `docs`: *Settings → Deploy keys → Add deploy key*.

- *Title*: `Bot PDF`
- *Key*: aprite `chiave-pdf.pub` con un editor di testo (anche VS Code) e incollate tutto il contenuto (una riga che inizia con `ssh-ed25519`)
- spuntate **Allow write access** → *Add key*

**C. Date al bot la parte segreta.** *Settings → Secrets and variables → Actions → New repository secret*.

- *Name*: `CHIAVE_PDF` (esattamente così)
- *Secret*: aprite il file `chiave-pdf` (quello **senza** `.pub`) e incollate tutto, comprese le righe `-----BEGIN OPENSSH PRIVATE KEY-----` e `-----END OPENSSH PRIVATE KEY-----` → *Add secret*

Poi **cancellate i due file** dal computer: non servono più e la parte segreta non deve girare.

**D. Proteggete `main` con un *ruleset*** (le vecchie *branch protection rules* non permettono di fare eccezioni per una chiave). *Settings → Rules → Rulesets → New ruleset → New branch ruleset*:

- *Ruleset name*: `Proteggi main`; *Enforcement status*: **Active**
- *Bypass list* → **Add bypass** → spuntate **Deploy keys** → *Add selected*. Solo la chiave del bot potrà scrivere su `main` senza PR
- *Target branches* → **Add target** → **Include default branch**
- *Rules*, spuntate:
  - **Restrict deletions** e **Block force pushes** (già spuntate di solito);
  - **Require a pull request before merging**, con *Required approvals* = **1**;
  - **Require status checks to pass** → *Add checks* → scrivete e scegliete **Compila i documenti** (compare dopo che la prima PR l'ha eseguito). **Non** spuntate *Require branches to be up to date before merging*: il bot aggiorna `main` a ogni merge e vi costringerebbe a premere *Update branch* di continuo
- *Create*

**E. Togliete la vecchia regola**, se c'era: *Settings → Branches* → accanto alla regola per `main`, **Delete**. Le due protezioni si sommano e quella vecchia bloccherebbe il bot.

**F. Provate**: fate il merge di una PR qualsiasi (o *Actions → Pubblica il sito → Run workflow*). Nell'esecuzione, il passo *Salva i PDF nel repository* deve dire `PDF salvati nel repository.`, e su `main` compare il commit *"Aggiorna i PDF accanto ai sorgenti [skip ci]"*. La prima volta salva i PDF di tutti i documenti; da lì in poi solo quelli cambiati.

> Se al passo B GitHub non vi lascia aggiungere la chiave, o al passo D in *Bypass list* non compare **Deploy keys**, probabilmente l'organizzazione ha disattivato le deploy key: chiedete a un proprietario dell'organizzazione `Git-Push-Team` di riattivarle nelle impostazioni dell'organizzazione.

---

## 9. Cosa è cambiato rispetto alla versione precedente

**Ultime novità nel registro delle modifiche.**

- Autore e verificatore possono essere più persone, separate da virgole (anche in copertina compaiono i nomi completi).
- Nei documenti si può indicare l'approvatore in fondo alla riga, tra parentesi quadre: la colonna *Approvatore* compare solo se usata ([R4](#r4-creare-un-documento-norme-piani-analisi)).
- Copertine senza ripetizioni: la versione dei documenti è sotto il titolo, l'uso nella scritta in alto.

**Le cartelle per milestone.**

- I documenti stanno in `Candidatura/`, `RTB/` e `PB/`, ognuna con `documenti/` e `verbali/`, a loro volta divise in `interni/` ed `esterni/` ([sezione 2](#2-mappa-del-repository-cosa-si-tocca-e-cosa-no)). Le vecchie cartelle `verbali/`, `documenti/`, `lettere/` e `candidatura/` non ci sono più; i tre verbali di ottobre sono in `Candidatura/verbali/interni/`.
- Dopo il merge il bot **salva il PDF accanto a ogni `.tex`** cambiato. Serve la configurazione della [sezione 8](#8-impostazioni-da-fare-una-volta-sola-amministratori).
- Il sito è stato rifatto: grafo delle milestone in cima, lettera di presentazione in evidenza, anteprime della prima pagina, verbali con la data a colpo d'occhio, copie firmate, diapositive, archivio, membri e ricerca. Le impostazioni sono in `template/sito.toml` ([R15](#r15-aggiornare-il-sito-milestone-diapositive-gruppo)).
- La release di un tag `rtb…` contiene solo la cartella `RTB/` (lo stesso per `candidatura…` e `pb…`).
- Le PR segnalano i PDF caricati a mano (errore) e i file in una cartella che non torna col contenuto (avviso).
- **Branch aperti prima di questa novità**: dopo *Update branch*, spostate il vostro `.tex` nella cartella nuova giusta (anche trascinandolo in VS Code), poi commit e push.

Novità della versione precedente, per chi usava il template ancora prima:

- **Prima riga**: `\documentclass[interno]{gpt}` diventa `\documentclass[verbale=interno]{gpt}` (la vecchia forma funziona ancora).
- **`\versione{}` non esiste più**: la versione si legge dalla prima riga `\modifica{}` del registro. Se c'è ancora, la compilazione si ferma e vi dice di cancellarla.
- **`\componenti{...}` è obbligatorio nei verbali**: elenca chi faceva parte del gruppo quel giorno, così i verbali vecchi non cambiano se il gruppo cambia.
- **Il capitolato si scrive nel singolo documento**, non più in `dati-gruppo.tex`.
- **Nuovi tipi** `[documento]` (con indice ed elenchi automatici) e `[lettera]`.
- **Il registro delle modifiche va a pagina nuova da solo**: regge anche centinaia di righe.
- **Modelli** spostati in `template/modelli/`; esempi completi in `template/esempi/`.
- **CI**: nelle pull request si compila sempre **tutto** (anche modelli ed esempi) e si commentano solo i documenti toccati; con un solo PDF il link lo apre direttamente nel browser. L'opzione `--changed` di `build.py` non c'è più.
- **Stessa compilazione ovunque**: `build.py` lancia latexmk dalla cartella del documento, come VS Code; i percorsi come `\input{capitoli/...}` funzionano uguali in locale e in CI.

**Branch aperti prima di questa versione**: dopo aver aggiornato il branch (*Update branch*), nei vostri `.tex` togliete `\versione{...}` e, se è un verbale, aggiungete la riga `\componenti{...}` copiandola dal modello.
