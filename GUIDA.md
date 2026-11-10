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
    - [R17. Segnare le ore (comando `/ore`)](#r17-segnare-le-ore-comando-ore)
    - [R18. Ortografia e leggibilità (🔎 Analisi dei testi)](#r18-ortografia-e-leggibilità--analisi-dei-testi)
5. [Le versioni: le regole del registro](#5-le-versioni-le-regole-del-registro)
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
| **Preambolo** | La parte del `.tex` **prima** di `\begin{document}`: lì si scrivono titolo, data, persone. |
| **Registro delle modifiche** | La tabella con tutte le versioni del documento. Le righe `\modifica{...}` le scrive il **bot** dopo il merge, nel file `nome.registro.tex` accanto al `.tex` ([sezione 5](#5-le-versioni-le-regole-del-registro)). |
| **Etichetta (label)** | Parola che si attacca a una PR (a destra, *Labels*). `contenuto`, `correzione` e `approvazione` dicono al bot come cambia la versione. |

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
| `scripts/analisi/parole.txt` | parole che l'analisi dei testi non deve segnalare come errori (nomi, sigle) | ✅ sì, una parola per riga ([R18](#r18-ortografia-e-leggibilità--analisi-dei-testi)) |
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
2. alla riga `Descrizione:` scrivete **cosa** è cambiato e **dove** (*"Stesura della sezione 3, Gestione dei rischi"*): è il testo che finirà nel registro;
3. a destra, in *Labels*, mettete l'**etichetta di versione**: `contenuto` (prima stesura o parti nuove) o `correzione` (correzioni piccole). Senza etichetta il registro non cambia ([sezione 5](#5-le-versioni-le-regole-del-registro));
4. spuntate la *Checklist dell'autore*;
5. a destra, in *Reviewers*, scegliete il **Verificatore** (diverso da voi);
6. cliccate *Create pull request*.

**Passo 7 — Aspettate il commento automatico** (2–4 minuti). Nella scheda *Conversation* della PR compare il commento **📄 Anteprima dei documenti** con:

- la tabella dei documenti toccati, con ✅ o ❌;
- il link **Apri il PDF** (se avete cambiato un solo documento si apre nel browser; se sono di più, scaricate lo zip);
- se c'è un ❌, le righe d'errore con file e numero di riga: correggete, poi rifate il passo 5 (commit + push) e il commento si aggiorna da solo.

Compare anche il commento **📝 Registro delle modifiche**, con la riga che il bot aggiungerà dopo il merge (versione, autore, verificatore, descrizione). Si aggiorna da solo quando cambiate etichetta o descrizione, o quando qualcuno approva.

E il commento **🔎 Analisi dei testi**: errori di ortografia, grammatica e tipografia trovati nelle righe che avete cambiato, e la leggibilità (indice Gulpease) del documento. Sono **suggerimenti**: non bloccano il merge ([R18](#r18-ortografia-e-leggibilità--analisi-dei-testi)).

Quando il Verificatore approva (vedi [R12](#r12-verificare-il-lavoro-di-un-altro-verificatore)), si clicca **Merge pull request**. Dopo qualche minuto:

- il PDF è sul sito <https://git-push-team.github.io/docs/>, nella sezione della sua milestone; 🎉
- nel repository, accanto al vostro `.tex`, compaiono il `.pdf` con lo stesso nome e, se la PR aveva un'etichetta di versione, la riga nuova in `nome.registro.tex` (li salva il bot).

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

**4. Consegnate** con il giro dei 7 passi. Il registro non si scrive a mano: lo compila il bot dopo il merge ([sezione 5](#5-le-versioni-le-regole-del-registro)). Per un verbale nuovo:

- se il Verificatore lo approva così com'è, oppure dopo le correzioni chieste nella stessa PR, mettete l'etichetta **`approvazione`** e come descrizione *"Stesura e approvazione del verbale"*: il bot scrive una sola riga, `1.0.0`;
- se invece volete registrare prima la stesura e approvarlo con una PR successiva, la prima PR ha l'etichetta **`contenuto`** (`0.1.0`, *"Stesura del verbale"*) e la seconda **`approvazione`** (`1.0.0`, *"Corrette le scadenze delle azioni e approvazione del verbale"*).

Autore è chi ha aperto la PR (e chi vi ha fatto commit), verificatore chi l'ha approvata. Un verbale è approvato quando ha la sua `1.0.0`; quello esterno poi va anche firmato dall'azienda ([R14](#r14-caricare-un-verbale-esterno-firmato)).

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
3. Passi 5–6 del giro, con l'etichetta **`correzione`** e la descrizione *"Corretto il nome del Responsabile nella sezione Ruoli"*.
4. Il Verificatore controlla e approva la PR. Dopo il merge il bot aggiunge in cima al registro:

   ```latex
   \modifica{1.0.1}{2026-10-28}{guglielmo}{corro}{Corretto il nome del Responsabile nella sezione Ruoli}% PR #15
   ```

   Se la correzione è minima e non merita una versione (un refuso nel codice LaTeX che non si vede nel PDF, un commento), non mettete nessuna etichetta: il registro non cambia.

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

Il registro non si scrive: finché il documento non è unito la copertina dice *Versione bozza*; la prima PR con etichetta `contenuto` crea la `0.1.0`.

**Registro dei documenti: più persone e approvatore.**

- Ogni PR con un'etichetta di versione fa aggiungere al bot **una riga** in cima ([sezione 5](#5-le-versioni-le-regole-del-registro)). Più autori o più verificatori compaiono separati da virgole; in copertina ognuno compare una volta sola tra *Redattori* e *Verificatori*.
- Quando il documento è pronto, la PR della sua ultima revisione riceve l'etichetta **`approvazione`**, messa dal **Responsabile** dello sprint. Il bot scrive la `1.0.0` (o `2.0.0`…) con il Responsabile **tra parentesi quadre** in fondo, nella colonna *Approvatore*:

  ```latex
  \modifica{1.0.0}{2026-11-19}{mazzurana}{corro}{Revisione finale della sezione 3 e approvazione del documento}[spagnoli]% PR #40
  \modifica{0.3.0}{2026-11-17}{mazzurana}{corro}{Stesura della sezione 3, Gestione dei rischi}% PR #38
  ```

  Se l'etichetta l'ha messa qualcun altro, il bot non scrive la riga e lo spiega nel commento della PR. La colonna **Approvatore** compare solo se almeno una riga ce l'ha; nei verbali l'approvatore non si usa.

**Si fanno da soli**: copertina (con versione, data dell'ultima modifica, **redattori e verificatori presi dal registro**), registro delle modifiche, **indice**, elenco delle figure e delle tabelle (solo se ce ne sono), intestazioni e numeri di pagina.

**3. Scrivete** con `\section{...}`, `\subsection{...}`, `\subsubsection{...}`: compaiono da sole nell'indice.

**4. Consegnate** con il giro dei 7 passi, con l'etichetta di versione giusta ([sezione 5](#5-le-versioni-le-regole-del-registro)).

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
3. Seguite la *Checklist del Verificatore* nella descrizione della PR. Il commento **🔎 Analisi dei testi** vi indica refusi e frasi difficili nelle righe cambiate: aiuta, ma non sostituisce la lettura ([R18](#r18-ortografia-e-leggibilità--analisi-dei-testi)).
4. **Se ci sono cose da correggere**: *Review changes* (o *Submit review*) → **Request changes** → spiegate cosa sistemare. L'autore corregge e fa push; voi rileggete.
5. **Se è tutto a posto**, controllate il commento **📝 Registro delle modifiche**:
    - l'**etichetta** è quella giusta (`contenuto` per parti nuove, `correzione` per correzioni piccole, `approvazione` solo per la versione approvata, messa dal Responsabile)? Se no, cambiatela a destra in *Labels*;
    - la **descrizione** dice **cosa** è cambiato e **dove** (non "Modifica" o "Fix")? Se no, chiedete all'autore di correggere la riga `Descrizione:` della PR (o correggetela voi: *⋯ → Edit* sulla descrizione).
    Non serve modificare il `.tex`: la verifica è la vostra approvazione.
6. *Review changes* → **Approve** → *Submit review*. Il commento del registro si aggiorna e vi mostra come verificatore.
7. Cliccate **Merge pull request** → *Confirm merge*. Fatto: il bot scrive la riga nel registro, aggiorna il sito e salva il PDF accanto al `.tex`.

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

Poi il solito giro (branch, commit, push, PR). Il bot non tocca mai i file `-firmato.pdf`, e la PR non li segnala come errore. Sul sito, accanto al verbale compare il pulsante **Firmato** che apre la copia firmata. Maiuscole e minuscole non contano: va bene anche `-Firmato.pdf`.

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
4. Nella PR mettete l'etichetta `contenuto` (voci nuove) o `correzione` e, come descrizione, quali voci avete aggiunto o cambiato: il bot aggiunge la riga al registro del Glossario.

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

### R17. Segnare le ore (comando `/ore`)

Le ore di lavoro si registrano **nei commenti** della issue su cui avete lavorato (o della PR che la chiude), alla fine di ogni blocco di lavoro.

Si scrive l'**orario**, non il totale: il bot calcola la durata. Un orario si può controllare, un numero no.

| Commento | Significato |
| --- | --- |
| `/ore 14:00-16:30` | dalle 14 alle 16:30 (2,5 ore), nel ruolo che avete nello sprint in corso |
| `/ore 9-11 verificatore` | dalle 9 alle 11, da Verificatore |
| `/ore 21:00-22:30 analista 2026-11-05` | lavoro fatto in un altro giorno |
| `/ore 23:30-00:30` | a cavallo della mezzanotte: conta nel giorno in cui avete iniziato |

- Vale ancora la forma con il solo totale (`/ore 2`, `/ore 1,5 verificatore`, `/ore 1h30 analista 2026-11-05`, `/ore 45m`): i commenti già scritti restano validi e le ore già contate non cambiano. Da ora usate l'orario.
- Le ore sono di **chi scrive il commento**: nessuno le segna per un altro. Più righe `/ore` nello stesso commento vanno bene (una per ogni blocco di lavoro).
- L'orario non può finire dopo il momento in cui scrivete il commento (c'è mezz'ora di margine): le ore si segnano a lavoro fatto. Per un altro giorno aggiungete la data.
- **Cose da controllare**: il bot segnala, nel riepilogo della issue (🔎 *Da controllare*) e ogni notte nel cruscotto (*Da sistemare*), due intervalli della stessa persona che si **sovrappongono**, **più di 8 ore** della stessa persona **in un giorno** e le ore segnate **più di 3 giorni dopo** il lavoro. Le ore contano lo stesso: se è tutto giusto si ignora, altrimenti correggete il commento. Le soglie sono in cima a `gestione/registro_ore.py` del repository `.github`.
- Il bot mette 👍 se il comando è valido, 😕 se c'è un errore, e tiene aggiornato un commento di riepilogo nella issue. Nel Project il campo *Ore effettive* della issue è il totale.
- **Per correggere** modificate o cancellate il vostro commento: tutto si ricalcola.
- **Verificatore**: scrivete `/ore 18:00-19:00 verificatore` in un commento della PR (nella conversazione, non nel riquadro della review): le ore vanno alla issue che la PR chiude con `Closes #numero`.
- **Riunioni**: ogni riunione ha la sua issue (modello **Riunione**); dopo la riunione ogni partecipante ci scrive l'orario, per esempio `/ore 21:00-22:30`.

Il ruolo di ognuno nello sprint, gli obiettivi e il preventivo sono nel file `gestione/pianificazione.toml` del repository [`.github`](https://github.com/Git-Push-Team/.github); il cruscotto con tutti i totali si vede, da membri, sulla pagina dell'organizzazione.

---

### R18. Ortografia e leggibilità (🔎 Analisi dei testi)

A ogni PR che tocca un documento parte da sola l'**Analisi dei testi**, e nella PR compare il commento **🔎 Analisi dei testi**. **Non blocca mai il merge**: segnala, poi decidete voi.

**Cosa controlla.**

| Parte | Cosa trova | Esempio |
| --- | --- | --- |
| **Ortografia** e **Grammatica** | refusi e concordanze, con [LanguageTool](https://languagetool.org) in italiano | *erori* → *errori* |
| **Tipografia** | gli errori tipici dell'italiano scritto | *E'* → *È*; *perchè* → *perché*; *un pò* → *un po'*; *qual'è* → *qual è*; *un'altro* → *un altro*; parole ripetute (*il il*); spazio prima di virgola e punto; virgolette dritte `"così"` (in LaTeX: ` ``così'' `); trattino ` - ` al posto di ` -- `; `...` al posto di `\dots` |
| **Stile** | scelte da uniformare | mesi e giorni con la maiuscola (*Lunedì 12 Ottobre*); date numeriche nel testo (*23/03/2027*); plurali inglesi (*le issues* → *le issue*, *i commits* → *i commit*) |
| **Leggibilità** | l'**indice Gulpease** del documento e delle sue sezioni, e le frasi oltre 40 parole | vedi sotto |

**L'indice Gulpease** misura quanto è facile leggere un testo italiano, da 0 a 100: `89 + (300 × frasi − 10 × lettere) / parole`. Lo abbassano frasi lunghe e parole lunghe. Per un lettore con il diploma: sotto **40** il testo è difficile, sopra **60** è facile. Nel commento: 🟢 facile, 🟡 accettabile, 🔴 difficile, ⚪ testo troppo breve per dirlo. Titoli, intestazioni di tabella e didascalie non contano. Per alzarlo: spezzate le frasi lunghe (il commento le elenca), un concetto per frase.

**Come si legge il commento.** Per ogni documento toccato: prima i problemi **nelle righe cambiate da questa PR** (con il numero di riga e, se sta in un capitolo, il nome del file), poi, chiusi in *Nel resto del documento*, quelli già presenti. Gli stessi avvisi compaiono anche accanto alle righe, nella scheda *Files changed*.

**Un falso allarme?** Un nome, una sigla o un termine giusto segnalato come errore: aggiungetelo a `scripts/analisi/parole.txt` (una parola per riga) nella stessa PR. Non serve per le voci del Glossario, i nomi del gruppo, le parole inglesi corrette e le parole in corsivo (`\textit{...}`): quelle si ignorano da sole. Gli altri falsi allarmi si ignorano e basta.

**Sul vostro computer** (facoltativo):

```bash
python3 scripts/analisi_testo.py RTB/documenti/esterni/piano-di-progetto.tex
python3 scripts/analisi_testo.py --solo-gulpease
```

La prima riga controlla un documento (o una cartella: `RTB`), la seconda dà in un attimo l'indice Gulpease di tutti. Senza LanguageTool si fanno tutti i controlli tranne ortografia e grammatica; per averlo serve Java, poi una volta sola `python3 scripts/analisi_testo.py --scarica-lt` (scarica circa 220 MB in `.cache/`, che non si carica su GitHub).

> Dopo ogni merge l'analisi gira su **tutti** i documenti: il riepilogo con l'indice Gulpease di ognuno è nella scheda *Actions → Analisi dei testi* (utile per le metriche del Piano di Qualifica). Le soglie 40 e 60 si cambiano in cima a `scripts/analisi_testo.py`.

---

## 5. Le versioni: le regole del registro

Il registro delle modifiche racconta la storia del documento: il committente lo legge e lo valuta. **Non si scrive a mano**: lo compila il bot a partire dalle pull request, così ogni riga corrisponde a una PR approvata e si può verificare su GitHub.

**Dove sta.** Accanto a ogni documento c'è un file con lo stesso nome e `.registro.tex` in fondo (`piano-di-progetto.tex` → `piano-di-progetto.registro.tex`). La classe lo legge da sola. Nel `.tex` non si scrive nessuna riga `\modifica`.

**Come nasce una riga.** Dopo il merge di una PR con un'**etichetta di versione**, il bot aggiunge in cima al registro di ogni documento toccato (anche tramite un capitolo o un'immagine della sua cartella) una riga con:

| Campo | Da dove lo prende il bot |
| --- | --- |
| versione | l'ultima del registro, aumentata secondo l'etichetta |
| data | il giorno del merge (per l'approvazione, il giorno in cui è stata messa l'etichetta, se dopo) |
| autore | chi ha aperto la PR e chi vi ha fatto commit (anche come co-autore), tranne chi l'ha approvata |
| verificatore | chi ha approvato la PR (*Review changes → Approve*), diverso dall'autore |
| descrizione | la riga `Descrizione:` della PR; se manca, il titolo della PR |
| approvatore | solo per l'approvazione dei documenti: il Responsabile che ha messo l'etichetta |

In fondo alla riga il bot scrive `% PR #numero`: così si risale sempre alla PR, alla revisione e alla discussione.

**Le etichette** (a destra nella PR, *Labels*; se una PR ne ha più d'una vale la più forte):

| Etichetta | Quando | Versione |
| --- | --- | --- |
| `contenuto` | prima stesura, parti nuove | `0.2.1` → `0.3.0` (la prima volta: `0.1.0`) |
| `correzione` | correzioni piccole | `0.2.0` → `0.2.1` |
| `approvazione` | versione approvata, pronta per la consegna. Nei **documenti** la mette il **Responsabile** dello sprint (il bot lo controlla in `pianificazione.toml`); nei **verbali** chiunque, dopo la verifica | `0.3.0` → `1.0.0`, `1.2.1` → `2.0.0` |
| *nessuna* | ritocchi che non meritano una versione (codice LaTeX che non cambia il PDF, commenti) | invariata, nessuna riga |

**Regole che restano.**

1. **Una riga = una modifica**: la descrizione dice **cosa** è cambiato e **dove** (*"Stesura della sezione 3, Gestione dei rischi"*, non *"Modifica"* o *"Fix"*).
2. **Una versione esiste solo se è verificata**: senza un'approvazione la riga avrebbe `--` come verificatore, e il commento della PR lo segnala.
3. **`1.0.0` è l'approvazione**: la revisione con cui il documento è pronto per la consegna.
4. **Le date**, salendo nel registro, non tornano indietro.

**Prima del merge** il commento **📝 Registro delle modifiche** nella PR mostra la riga che verrà aggiunta, e anche il PDF di anteprima ha già la versione nuova. **Dopo il merge** lo stesso commento diventa il resoconto di ciò che il bot ha scritto, con gli eventuali problemi (per esempio un'approvazione data da chi non è Responsabile: in quel caso il Responsabile toglie e rimette l'etichetta alla PR, anche chiusa, e si rilancia *Actions → Pubblica il sito → Run workflow*; il bot riguarda le PR delle ultime tre settimane).

**Correggere una riga già scritta** (per esempio un refuso nella descrizione): modificate il file `.registro.tex` in una PR **senza etichetta**.

**Cosa si controlla da solo.** La classe ferma la compilazione se una versione non ha tre numeri, se una data non è `AAAA-MM-GG` o se le versioni non scendono dall'alto in basso. Il commento della PR (sotto *Da controllare*) segnala le righe senza verificatore o con verificatore uguale all'autore, le date che tornano indietro, le approvazioni dei documenti senza approvatore e le righe `\modifica` rimaste a mano nel `.tex` (al primo merge con etichetta il bot le sposta nel `.registro.tex`).

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
| `\modifica{}{}{}{}{}` | file `.registro.tex` | `\modifica{0.1.0}{2026-10-26}{corro, biasini}{guglielmo}{Prima stesura}` | una riga del registro: versione, data, autore, verificatore, cosa è cambiato. **La scrive il bot** ([sezione 5](#5-le-versioni-le-regole-del-registro)) |
| `\modifica{}{}{}{}{}[]` | file `.registro.tex`, solo documenti | `\modifica{1.0.0}{2026-11-19}{corro}{guglielmo}{Revisione finale e approvazione del documento}[spagnoli]` | come sopra, con l'approvatore tra `[ ]`: aggiunge la colonna *Approvatore* |

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
| `python3 scripts/analisi_testo.py percorso/file.tex` | ortografia, tipografia e leggibilità di un documento (o di una cartella) ([R18](#r18-ortografia-e-leggibilità--analisi-dei-testi)) |
| `python3 scripts/analisi_testo.py --solo-gulpease` | l'indice Gulpease di tutti i documenti |

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
| `Manca il titolo` / `Manca la data` | Aggiungete la riga che manca nel preambolo (vedete il modello). |
| `\uso: scrivete interno oppure esterno` | Solo queste due parole. |
| `Opzione "verbale=..." non valida` | Prima riga: `[verbale=interno]` o `[verbale=esterno]`. |
| `\capitolato non va in dati-gruppo.tex` | Scrivetelo nel singolo documento ([R11](#r11-cambiare-i-dati-del-gruppo)). |
| `L'approvatore [...] si usa solo nei documenti, non nei verbali` | Togliete la parte tra parentesi quadre in fondo alla riga `\modifica` del verbale. |

**Avvisi sul registro** (nel commento della PR, sotto *Da controllare*; non bloccano, [sezione 5](#5-le-versioni-le-regole-del-registro)):

| Avviso (in breve) | Cosa fare |
| --- | --- |
| `ci sono righe \modifica scritte a mano nel .tex` | Toglietele: il registro lo scrive il bot. Se restano, al primo merge con etichetta il bot le sposta nel `.registro.tex`. |
| `la riga X non ha verificatore (--)` | La PR è stata unita senza approvazione: correggete il `.registro.tex` con una PR senza etichetta, mettendo la chiave di chi ha verificato. |
| `nella riga X chi verifica è anche autore` | Serve un'altra persona come verificatore. |
| `la riga X è più vecchia della riga sotto` | Le date, salendo, non tornano indietro: correggete la data nel `.registro.tex`. |
| `la riga X ha data ..., prima della riunione` | Un verbale non si scrive prima della riunione: correggete la data nel `.registro.tex`. |
| `la riga X è un'approvazione ma manca l'approvatore` | L'approvazione dei documenti la registra il bot quando il Responsabile mette l'etichetta `approvazione`. |

**Il commento 📝 Registro delle modifiche** (dopo il merge) segnala anche:

| Avviso (in breve) | Cosa fare |
| --- | --- |
| `l'etichetta approvazione l'ha messa X, ma il Responsabile dello sprint è Y` | Y toglie e rimette l'etichetta alla PR (anche chiusa), poi *Actions → Pubblica il sito → Run workflow*. |
| `X non è tra i membri di pianificazione.toml` | Aggiungete il suo username GitHub in `[membri]` di `pianificazione.toml` (repository `.github`). |
| `nessun membro ha approvato la PR` | Come sopra: correggete a mano il verificatore nel `.registro.tex`. |

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
| Il commento **🔎 Analisi dei testi** segnala come errore una parola giusta | se è un nome, una sigla o un termine del progetto, aggiungetelo a `scripts/analisi/parole.txt`; altrimenti ignoratelo: non blocca nulla ([R18](#r18-ortografia-e-leggibilità--analisi-dei-testi)) |
| Nel commento 🔎 compare *LanguageTool non trovato* o *si è fermato con un errore* | lo scaricamento o l'avvio di LanguageTool non è riuscito: ortografia e grammatica mancano, il resto c'è. Di solito si sistema da solo alla PR successiva; se resta, rilanciate l'Action (*Re-run jobs*) |
| Il pulsante **Firmato** non compare | la copia firmata deve stare accanto al `.tex` con lo stesso nome più `-firmato`: `VE-2026-11-05-firmato.pdf` accanto a `VE-2026-11-05.tex` ([R14](#r14-caricare-un-verbale-esterno-firmato)) |

---

## 8. Impostazioni da fare una volta sola (Amministratori)

Sul sito di GitHub, nella pagina del repository `docs`, scheda **Settings**:

1. **Pages** → *Build and deployment* → *Source*: **GitHub Actions**. Senza questo il sito non si pubblica. (Con il piano gratuito di GitHub, Pages funziona solo se il repository è **pubblico**.)
2. **Issues → Labels** (dalla scheda *Issues*, pulsante *Labels*): create le etichette `documentazione` ed `errore`, usate dai modelli delle issue. Le etichette di versione (`contenuto`, `correzione`, `approvazione`) le crea da solo il bot alla prima PR.
3. **La chiave del bot e la protezione di `main`**: passi A–F qui sotto.
4. **Il registro legge la pianificazione**: autore, verificatore e Responsabile il bot li ricava da `gestione/pianificazione.toml` del repository [`.github`](https://github.com/Git-Push-Team/.github), che deve restare **pubblico**. Se diventa privato, o un membro non ha il suo username GitHub in `[membri]`, le righe non si scrivono (lo dicono la pagina dell'Action e il commento della PR).

### La chiave del bot e la protezione di `main`

`main` è protetto: si cambia solo con una pull request approvata. Il bot che salva i PDF accanto ai `.tex` e le righe del registro però scrive su `main` **dopo** il merge, senza PR, quindi gli serve un permesso speciale. GitHub non lo concede al bot normale delle Actions: lo si dà a una **chiave di deployment** (*deploy key*) che solo il bot conosce. Se saltate questa parte il sito si aggiorna lo stesso (anche con le versioni nuove), ma PDF e righe del registro non vengono salvati nel repository (nella scheda *Actions* compare un avviso).

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
  - **Require status checks to pass** → *Add checks* → scrivete e scegliete **Compila i documenti** (compare dopo che la prima PR l'ha eseguito). **Non** aggiungete *Analisi dei testi* né *Anteprima del registro*: sono solo suggerimenti. **Non** spuntate *Require branches to be up to date before merging*: il bot aggiorna `main` a ogni merge e vi costringerebbe a premere *Update branch* di continuo
- *Create*

**E. Togliete la vecchia regola**, se c'era: *Settings → Branches* → accanto alla regola per `main`, **Delete**. Le due protezioni si sommano e quella vecchia bloccherebbe il bot.

**F. Provate**: fate il merge di una PR qualsiasi (o *Actions → Pubblica il sito → Run workflow*). Nell'esecuzione, il passo *Salva registro e PDF nel repository* deve dire `Registro e PDF salvati nel repository.`, e su `main` compare il commit *"Aggiorna i PDF accanto ai sorgenti [skip ci]"* (e, se la PR aveva un'etichetta di versione, *"Registro delle modifiche aggiornato dal bot [skip ci]"*). La prima volta salva i PDF di tutti i documenti; da lì in poi solo quelli cambiati.

> Se al passo B GitHub non vi lascia aggiungere la chiave, o al passo D in *Bypass list* non compare **Deploy keys**, probabilmente l'organizzazione ha disattivato le deploy key: chiedete a un proprietario dell'organizzazione `Git-Push-Team` di riattivarle nelle impostazioni dell'organizzazione.

---

## 9. Cosa è cambiato rispetto alla versione precedente

**Ultime novità: il registro delle modifiche automatico.**

- Le righe `\modifica` non si scrivono più: le aggiunge il bot dopo il merge, nel file `nome.registro.tex` accanto al documento, in base all'**etichetta** della PR (`contenuto`, `correzione`, `approvazione`). Autore e verificatore li prende da GitHub: chi ha fatto la PR e chi l'ha approvata ([sezione 5](#5-le-versioni-le-regole-del-registro)).
- Senza etichetta la versione non cambia: per i ritocchi minimi.
- Le righe già esistenti sono state spostate nei file `.registro.tex`, identiche: i PDF non cambiano.
- Nella PR il commento **📝 Registro delle modifiche** mostra in anticipo la riga, e il PDF di anteprima ha già la versione nuova.
- Un documento nuovo, prima del suo primo merge, ha in copertina *Versione bozza*.
- **Branch aperti prima di questa novità**: dopo *Update branch* togliete dal `.tex` le righe `\modifica` che avevate aggiunto e mettete etichetta e descrizione alla PR (se le lasciate, il bot le sposta da solo).
- **Ore con l'orario**: `/ore 14:00-16:30` al posto di `/ore 2,5`; il bot calcola la durata e segnala sovrapposizioni, giorni oltre 8 ore e ore segnate in ritardo ([R17](#r17-segnare-le-ore-comando-ore)). La vecchia forma vale ancora.
- **Analisi dei testi**: nelle PR il commento **🔎 Analisi dei testi** segnala errori di ortografia, grammatica e tipografia e dà l'indice Gulpease dei documenti. Non blocca nulla ([R18](#r18-ortografia-e-leggibilità--analisi-dei-testi)).

**Novità precedenti: le regole delle versioni.**

- Ogni riga del registro ha autore **e** verificatore: `--` vuol dire "non verificata" (oggi verificatore e approvatore li scrive il bot). Niente più righe di sola "Verifica"; la `1.0.0` è la revisione approvata, nei documenti con `[spagnoli]` ([sezione 5](#5-le-versioni-le-regole-del-registro)).
- Il commento automatico della PR segnala i problemi del registro (righe non verificate, date che tornano indietro, approvazioni senza approvatore…): [sezione 7](#7-quando-qualcosa-va-storto).
- I registri della Candidatura sono stati sistemati con queste regole.
- Sul sito ogni PDF (documenti, verbali, copie firmate, diapositive) e ogni link esterno si apre in una **scheda nuova**, e la scheda mostra il titolo del documento invece del nome del file.

**Novità precedenti nel registro delle modifiche.**

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
