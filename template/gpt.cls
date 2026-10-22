% =====================================================================
%  gpt.cls  --  Classe LaTeX di TUTTI i documenti del Git Push Team
%               Gruppo 9 - Ingegneria del Software - Università di Padova
% =====================================================================
%
%  PER CHI SCRIVE I DOCUMENTI: questo file NON si modifica.
%  Il tipo di documento si sceglie nella PRIMA riga del vostro .tex:
%
%     \documentclass[verbale=interno]{gpt}   riunione del solo gruppo
%     \documentclass[verbale=esterno]{gpt}   incontro con proponente o docenti
%     \documentclass[documento]{gpt}         Norme, Piani, Analisi, Glossario...
%     \documentclass[lettera]{gpt}           lettera di presentazione/candidatura
%
%  Copertina, registro delle modifiche, indice, presenze, intestazioni
%  e numeri di pagina si fanno da soli. Dove trovare il resto:
%     - modelli pronti da copiare ...... template/modelli/
%     - esempi completi ................ template/esempi/
%     - dati del gruppo ................ template/dati-gruppo.tex
%     - guida passo passo .............. GUIDA.md
%
%  PER GLI AMMINISTRATORI: il file è diviso in SEZIONI numerate
%  (cercate la parola SEZIONE). Ogni modifica va in una pull request:
%  la CI ricompila tutti i documenti, i modelli e gli esempi e vi dice
%  subito se qualcosa si rompe.
% =====================================================================
\NeedsTeXFormat{LaTeX2e}[2020/10/01]
\ProvidesClass{gpt}[2026/10/20 v2.0 Documenti Git Push Team]


% =====================================================================
%  SEZIONE 1 - Tipo di documento (l'opzione tra [ ] di \documentclass)
% =====================================================================
\RequirePackage{kvoptions}
\SetupKeyvalOptions{family=gpt,prefix=gpt@opt@}
\def\gpt@tipo{verbale}       % verbale | documento | lettera
\def\gpt@sottotipo{interno}  % interno | esterno   (solo per i verbali)
\define@key{gpt}{verbale}[interno]{\def\gpt@tipo{verbale}\def\gpt@sottotipo{#1}}
\DeclareVoidOption{documento}{\def\gpt@tipo{documento}}
\DeclareVoidOption{lettera}{\def\gpt@tipo{lettera}}
% vecchia sintassi, ancora accettata: [interno] e [esterno]
\DeclareVoidOption{interno}{\def\gpt@tipo{verbale}\def\gpt@sottotipo{interno}}
\DeclareVoidOption{esterno}{\def\gpt@tipo{verbale}\def\gpt@sottotipo{esterno}}
% qualunque altra opzione (per esempio 12pt) passa alla classe article
\DeclareDefaultOption{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessKeyvalOptions*
\LoadClass[11pt,a4paper]{article}

% Interruttori comodi da usare nel resto del file
\newif\ifgpt@verbale     % è un verbale?
\newif\ifgpt@documento   % è un documento (Norme, Piani...)?
\newif\ifgpt@lettera     % è una lettera?
\newif\ifgpt@esterno     % è un verbale esterno?
\def\gpt@tmp{verbale}\ifx\gpt@tipo\gpt@tmp\gpt@verbaletrue\fi
\def\gpt@tmp{documento}\ifx\gpt@tipo\gpt@tmp\gpt@documentotrue\fi
\def\gpt@tmp{lettera}\ifx\gpt@tipo\gpt@tmp\gpt@letteratrue\fi
\ifgpt@verbale
  \def\gpt@tmp{esterno}%
  \ifx\gpt@sottotipo\gpt@tmp
    \gpt@esternotrue
  \else
    \def\gpt@tmp{interno}%
    \ifx\gpt@sottotipo\gpt@tmp\else
      \ClassError{gpt}{Opzione "verbale=\gpt@sottotipo" non valida: scrivete
        verbale=interno oppure verbale=esterno}{}%
    \fi
  \fi
\fi


% =====================================================================
%  SEZIONE 2 - Pacchetti
% =====================================================================
\RequirePackage[T1]{fontenc}
\RequirePackage[utf8]{inputenc}
\RequirePackage{charter}                 % testo: Bitstream Charter
\RequirePackage[scaled=0.92]{helvet}     % titoli: Helvetica
\RequirePackage{microtype}
\IfFileExists{italian.ldf}
  {\RequirePackage[italian]{babel}}
  {\ClassWarningNoLine{gpt}{babel-italian non installato:
     sillabazione italiana disattivata}}
\RequirePackage[a4paper,top=3cm,bottom=2.6cm,left=2.4cm,right=2.4cm,
                headheight=30pt,headsep=16pt,footskip=28pt]{geometry}
\RequirePackage[table]{xcolor}
\RequirePackage{graphicx}
\RequirePackage{etoolbox}
\RequirePackage{array,tabularx,booktabs,longtable}
\RequirePackage{enumitem}
\RequirePackage{titlesec}
\RequirePackage{fancyhdr}
\RequirePackage{lastpage}
\RequirePackage[most]{tcolorbox}
\RequirePackage{caption}
\RequirePackage{float}
\RequirePackage{needspace}
\PassOptionsToPackage{hyphens}{url}
\RequirePackage{hyperref}
\urlstyle{same}

% Immagini: prima la cartella img/ accanto al documento, poi allegati/
% (allegati/ la trova LaTeX grazie al file latexmkrc).
\graphicspath{{img/}}


% =====================================================================
%  SEZIONE 3 - Colori
% =====================================================================
\definecolor{gptinchiostro}{HTML}{1A1A1A}
\definecolor{gptaccento}{HTML}{14457A}
\definecolor{gptgrigio}{HTML}{6B7280}
\definecolor{gptlinea}{HTML}{CBD2DB}
\colorlet{gptsfondo}{gptaccento!5}
\color{gptinchiostro}

\hypersetup{colorlinks=true,linkcolor=gptaccento,urlcolor=gptaccento,
            citecolor=gptaccento}


% =====================================================================
%  SEZIONE 4 - Dati del gruppo (si impostano in template/dati-gruppo.tex)
% =====================================================================
\def\gpt@nomegruppo{Nome gruppo}
\def\gpt@motto{}
\def\gpt@numerogruppo{}
\def\gpt@email{}
\def\gpt@universita{Università degli Studi di Padova}
\def\gpt@corso{Ingegneria del Software}
\def\gpt@annoaccademico{}
\def\gpt@destinatari{}
\def\gpt@logo{logo.png}

\newcommand{\nomegruppo}[1]{\gdef\gpt@nomegruppo{#1}}
\newcommand{\motto}[1]{\gdef\gpt@motto{#1}}
\newcommand{\numerogruppo}[1]{\gdef\gpt@numerogruppo{#1}}
\newcommand{\emailgruppo}[1]{\gdef\gpt@email{#1}}
\newcommand{\universita}[1]{\gdef\gpt@universita{#1}}
\newcommand{\corso}[1]{\gdef\gpt@corso{#1}}
\newcommand{\annoaccademico}[1]{\gdef\gpt@annoaccademico{#1}}
\newcommand{\destinatari}[1]{\gdef\gpt@destinatari{#1}}
\newcommand{\logo}[1]{\gdef\gpt@logo{#1}}

% Vero mentre LaTeX legge dati-gruppo.tex (serve ai controlli qui sotto)
\newif\ifgpt@datigruppo

% \membro{chiave}{Nome Cognome}{matricola}
\newcommand{\membro}[3]{%
  \gpt@nuovomembro{#1}%
  \csgdef{gpt@nome@#1}{#2}%
  \csgdef{gpt@matr@#1}{#3}}
\csgdef{gpt@nome@tutti}{Tutto il gruppo}


% =====================================================================
%  SEZIONE 5 - Controlli automatici
%  Qui la classe verifica che chiavi dei membri, date e versioni siano
%  scritte bene. Se qualcosa non va, la compilazione si ferma con un
%  messaggio in italiano che dice cosa correggere.
%  (Questa parte usa la sintassi "expl3" di LaTeX: i nomi con _ e : sono
%  normali, e il simbolo ~ dentro i messaggi vuol dire "spazio".)
% =====================================================================
\ExplSyntaxOn
\clist_new:N \g__gpt_membri_clist        % chiavi di dati-gruppo.tex
\clist_new:N \g__gpt_componenti_clist    % \componenti del verbale
\clist_new:N \g__gpt_assenti_clist       % \assenti del verbale
\clist_new:N \g__gpt_autori_clist        % autori presenti nel registro
\clist_new:N \g__gpt_verificatori_clist  % verificatori presenti nel registro
\tl_new:N  \g__gpt_righepres_tl          % righe della tabella presenze
\tl_new:N  \g__gpt_versioneprec_tl       % versione della riga precedente
\tl_new:N  \l__gpt_tmp_tl
\seq_new:N \l__gpt_nomi_seq

\cs_new_protected:Npn \__gpt_errore:n #1 { \ClassError {gpt} {#1} {} }
\cs_new:Npn \__gpt_chiavi_valide: { \clist_use:Nn \g__gpt_membri_clist { ,~ } }

% ---- \membro: la chiave deve essere minuscola e unica ------------------
\cs_new_protected:Npn \gpt@nuovomembro #1
  {
    \regex_match:nnF { \A [a-z][a-z0-9]* \Z } {#1}
      {
        \__gpt_errore:n
          { In~dati-gruppo.tex~la~chiave~"#1"~non~va~bene:~usate~solo~
            lettere~minuscole~(e~cifre),~senza~spazi~ne'~accenti }
      }
    \clist_if_in:NnTF \g__gpt_membri_clist {#1}
      { \__gpt_errore:n { In~dati-gruppo.tex~la~chiave~"#1"~compare~due~volte } }
      { \clist_gput_right:Nn \g__gpt_membri_clist {#1} }
  }

% ---- chiave OBBLIGATORIA: deve esistere in dati-gruppo.tex -------------
\cs_new_protected:Npn \gpt@controllamembro #1
  {
    \clist_if_in:NnF \g__gpt_membri_clist {#1}
      {
        \__gpt_errore:n
          { Membro~"#1"~sconosciuto.~Chiavi~valide~(da~template/dati-gruppo.tex):~
            \__gpt_chiavi_valide: }
      }
  }

% ---- chiave TOLLERANTE: se sembra una chiave (minuscole) deve esistere;
%      altrimenti è testo libero, per esempio "Mariano Sciacco" o "--"
\cs_new_protected:Npn \gpt@controllachiave #1
  {
    \regex_match:nnT { \A [a-z][a-z0-9]* \Z } {#1}
      { \str_if_eq:nnF {#1} {tutti} { \gpt@controllamembro {#1} } }
  }

% ---- data nel formato AAAA-MM-GG ---------------------------------------
% \gpt@impostadata{data}: controlla e imposta la data del documento
\cs_new_protected:Npn \gpt@impostadata #1
  {
    \tl_set:Nx \l__gpt_tmp_tl { \tl_trim_spaces:n {#1} }
    \exp_args:NnV \regex_match:nnTF { \A \d{4} - \d{2} - \d{2} \Z } \l__gpt_tmp_tl
      { \exp_after:wN \__gpt_leggi_data:w \l__gpt_tmp_tl \q_stop }
      {
        \__gpt_errore:n
          { \token_to_str:N \data :~la~data~"#1"~non~va~bene.~Scrivetela~
            cosi':~AAAA-MM-GG,~per~esempio~2026-10-26 }
      }
  }
\cs_new_protected:Npn \__gpt_leggi_data:w #1 - #2 - #3 \q_stop
  {
    \tl_gset:Nn \gpt@anno   {#1}
    \tl_gset:Nn \gpt@mese   {#2}
    \tl_gset:Nn \gpt@giorno {#3}
  }
% \gpt@controlladata{data}{versione}: controlla una data del registro
\cs_new_protected:Npn \gpt@controlladata #1#2
  {
    \tl_set:Nx \l__gpt_tmp_tl { \tl_trim_spaces:n {#1} }
    \exp_args:NnV \regex_match:nnF { \A \d{4} - \d{2} - \d{2} \Z } \l__gpt_tmp_tl
      {
        \__gpt_errore:n
          { Registro~delle~modifiche,~riga~#2:~la~data~"#1"~non~va~bene.~
            Scrivetela~cosi':~AAAA-MM-GG,~per~esempio~2026-10-26 }
      }
  }

% ---- versione X.Y.Z e ordine del registro (più recente IN CIMA) -------
\cs_new:Npn \__gpt_numero_versione:w #1 . #2 . #3 \q_stop
  { (#1) * 100000000 + (#2) * 10000 + (#3) }
\cs_new_protected:Npn \gpt@controllaversione #1
  {
    \tl_set:Nx \l__gpt_tmp_tl { \tl_trim_spaces:n {#1} }
    \exp_args:NnV \regex_match:nnTF { \A \d+ \. \d+ \. \d+ \Z } \l__gpt_tmp_tl
      {
        \tl_if_empty:NF \g__gpt_versioneprec_tl
          {
            \fp_compare:nNnF
              { \exp_after:wN \__gpt_numero_versione:w \l__gpt_tmp_tl \q_stop }
              <
              { \exp_after:wN \__gpt_numero_versione:w \g__gpt_versioneprec_tl \q_stop }
              {
                \__gpt_errore:n
                  { Registro~delle~modifiche~in~ordine~sbagliato:~la~riga~
                    \l__gpt_tmp_tl \c_space_tl e'~sotto~la~riga~\g__gpt_versioneprec_tl ,~
                    ma~non~e'~piu'~vecchia.~La~riga~piu'~recente~va~IN~CIMA~
                    e~ogni~versione~compare~una~sola~volta }
              }
          }
        \tl_gset_eq:NN \g__gpt_versioneprec_tl \l__gpt_tmp_tl
        \tl_gset_eq:NN \gpt@versioneletta \l__gpt_tmp_tl
      }
      {
        \__gpt_errore:n
          { Registro~delle~modifiche:~la~versione~"#1"~non~va~bene.~
            Scrivetela~cosi':~X.Y.Z,~per~esempio~0.1.0~oppure~1.0.0 }
      }
  }

% ---- valore di \uso -------------------------------------------------------
\cs_new_protected:Npn \gpt@controllauso #1
  {
    \str_case:nnF {#1} { {interno} {} {esterno} {} }
      {
        \__gpt_errore:n
          { \token_to_str:N \uso :~scrivete~interno~oppure~esterno~(non~"#1") }
      }
  }

% ---- \componenti e \assenti (verbali) ----------------------------------
\cs_new_protected:Npn \gpt@impostacomponenti #1
  {
    \clist_gclear:N \g__gpt_componenti_clist
    \clist_map_inline:nn {#1}
      {
        \gpt@controllamembro {##1}
        \clist_gput_right:Nn \g__gpt_componenti_clist {##1}
      }
  }
\cs_new_protected:Npn \gpt@impostaassenti #1
  {
    \clist_map_inline:nn {#1}
      {
        \gpt@controllamembro {##1}
        \clist_gput_right:Nn \g__gpt_assenti_clist {##1}
      }
  }
\cs_new:Npn \gpt@secomponentivuoti #1#2
  { \clist_if_empty:NTF \g__gpt_componenti_clist {#1} {#2} }
\cs_new_protected:Npn \gpt@seassente #1#2#3
  { \clist_if_in:NnTF \g__gpt_assenti_clist {#1} {#2} {#3} }
\cs_new_protected:Npn \gpt@controllaassenti
  {
    \clist_map_inline:Nn \g__gpt_assenti_clist
      {
        \clist_if_in:NnF \g__gpt_componenti_clist {##1}
          {
            \__gpt_errore:n
              { "##1"~e'~in~\token_to_str:N \assenti \c_space_tl ma~non~in~
                \token_to_str:N \componenti :~aggiungetelo~ai~componenti~
                oppure~toglietelo~dagli~assenti }
          }
      }
  }
% righe della tabella presenze, nell'ordine scritto in \componenti
\cs_new_protected:Npn \gpt@preparapresenze
  {
    \tl_gclear:N \g__gpt_righepres_tl
    \clist_map_inline:Nn \g__gpt_componenti_clist
      { \tl_gput_right:Nn \g__gpt_righepres_tl { \gpt@rigapres {##1} } }
  }
\cs_new:Npn \gpt@righepresenze { \g__gpt_righepres_tl }

% ---- \nomi{a,b,c} -> "Nome A, Nome B, Nome C" ---------------------------
\cs_new_protected:Npn \gpt@nomi #1
  {
    \seq_clear:N \l__gpt_nomi_seq
    \clist_map_inline:nn {#1} { \seq_put_right:Nn \l__gpt_nomi_seq { \nome {##1} } }
    \seq_use:Nn \l__gpt_nomi_seq { ,~ }
  }

% ---- redattori e verificatori raccolti dal registro (copertina documenti)
\cs_new_protected:Npn \__gpt_aggiungi_unico:Nn #1#2
  {
    \tl_set:Nx \l__gpt_tmp_tl { \tl_trim_spaces:n {#2} }
    \bool_lazy_or:nnF
      { \tl_if_empty_p:N \l__gpt_tmp_tl }
      { \str_if_eq_p:Vn \l__gpt_tmp_tl { -- } }
      { \clist_if_in:NVF #1 \l__gpt_tmp_tl { \clist_gput_right:NV #1 \l__gpt_tmp_tl } }
  }
\cs_new_protected:Npn \gpt@registrapersone #1#2
  {
    \__gpt_aggiungi_unico:Nn \g__gpt_autori_clist {#1}
    \__gpt_aggiungi_unico:Nn \g__gpt_verificatori_clist {#2}
  }
% stampa le persone nell'ordine di dati-gruppo.tex (poi gli eventuali esterni)
\cs_new_protected:Npn \__gpt_stampa_persone:N #1
  {
    \seq_clear:N \l__gpt_nomi_seq
    \clist_map_inline:Nn \g__gpt_membri_clist
      { \clist_if_in:NnT #1 {##1} { \seq_put_right:Nn \l__gpt_nomi_seq { \nome {##1} } } }
    \clist_map_inline:Nn #1
      { \clist_if_in:NnF \g__gpt_membri_clist {##1} { \seq_put_right:Nn \l__gpt_nomi_seq {##1} } }
    \seq_if_empty:NTF \l__gpt_nomi_seq { -- } { \seq_use:Nn \l__gpt_nomi_seq { ,~ } }
  }
\cs_new_protected:Npn \gpt@stampaautori { \__gpt_stampa_persone:N \g__gpt_autori_clist }
\cs_new_protected:Npn \gpt@stampaverificatori { \__gpt_stampa_persone:N \g__gpt_verificatori_clist }
\ExplSyntaxOff


% =====================================================================
%  SEZIONE 6 - Dati del documento (comandi da usare nel preambolo)
% =====================================================================
\def\gpt@titolo{}
\def\gpt@giorno{}\def\gpt@mese{}\def\gpt@anno{}
\def\gpt@orainizio{--}\def\gpt@orafine{--}
\def\gpt@luogo{}
\def\gpt@redattore{--}
\def\gpt@verificatore{--}
\def\gpt@responsabile{}
\def\gpt@capitolato{}
\def\gpt@uso{}
\def\gpt@oggetto{}
\def\gpt@chiusura{Cordiali saluti,}
\def\gpt@righeesterni{}
\newif\ifgpt@haesterni
\def\gpt@firmanome{}
\def\gpt@firmaente{}

\newcommand{\titolo}[1]{\gdef\gpt@titolo{#1}}
\newcommand{\data}[1]{\gpt@impostadata{#1}}
\newcommand{\orario}[2]{\gdef\gpt@orainizio{#1}\gdef\gpt@orafine{#2}}
\newcommand{\luogo}[1]{\gdef\gpt@luogo{#1}}
\newcommand{\redattore}[1]{\gpt@controllachiave{#1}\gdef\gpt@redattore{#1}}
\newcommand{\verificatore}[1]{\gpt@controllachiave{#1}\gdef\gpt@verificatore{#1}}
\newcommand{\responsabile}[1]{\gpt@controllachiave{#1}\gdef\gpt@responsabile{#1}}
\newcommand{\uso}[1]{\gpt@controllauso{#1}\gdef\gpt@uso{#1}}
\newcommand{\oggetto}[1]{\gdef\gpt@oggetto{#1}}
\newcommand{\chiusura}[1]{\gdef\gpt@chiusura{#1}}

% Il capitolato si scrive nel SINGOLO documento, mai in dati-gruppo.tex:
% così i documenti scritti prima dell'assegnazione non cambiano.
\newcommand{\capitolato}[1]{%
  \ifgpt@datigruppo
    \ClassError{gpt}{\string\capitolato\space non va in dati-gruppo.tex:
      scrivetelo nel singolo documento, cosi' i PDF vecchi non cambiano}{}%
  \else
    \gdef\gpt@capitolato{#1}%
  \fi}

% Chi faceva parte del gruppo il giorno della riunione (solo verbali).
% Si scrive in OGNI verbale: se il gruppo cambia, i verbali vecchi
% restano come erano.
\newcommand{\componenti}[1]{%
  \ifgpt@datigruppo
    \ClassError{gpt}{\string\componenti\space va scritto nel singolo
      verbale, non in dati-gruppo.tex}{}%
  \else
    \gpt@impostacomponenti{#1}%
  \fi}
\newcommand{\assenti}[1]{\gpt@impostaassenti{#1}}

% \esterno{Nome Cognome}{Ruolo, Azienda}     (partecipanti esterni)
\newcommand{\esterno}[2]{%
  \gappto\gpt@righeesterni{#1 & #2 \\}\global\gpt@haesternitrue}
% \firma{Nome Cognome}{Azienda}              (solo verbali esterni)
\newcommand{\firma}[2]{\gdef\gpt@firmanome{#1}\gdef\gpt@firmaente{#2}}

% \versione{} non si usa più: la versione si legge dal registro.
\newcommand{\versione}[1]{%
  \ClassError{gpt}{\string\versione\space non serve piu': la versione
    e' quella della PRIMA riga \string\modifica\space del registro.
    Cancellate la riga \string\versione\string{#1\string}}{}}

% \nome{chiave} -> Nome Cognome    (testo libero: lo stampa com'è)
\DeclareRobustCommand{\nome}[1]{%
  \gpt@controllachiave{#1}%
  \ifcsdef{gpt@nome@#1}{\csuse{gpt@nome@#1}}{#1}}
% \nomi{chiave1,chiave2} -> Nome1, Nome2
\DeclareRobustCommand{\nomi}[1]{\gpt@nomi{#1}}

% ---- Date ---------------------------------------------------------------
\newcommand{\gpt@nomemese}[1]{\ifcase\numexpr#1\relax\or gennaio\or febbraio\or
  marzo\or aprile\or maggio\or giugno\or luglio\or agosto\or settembre\or
  ottobre\or novembre\or dicembre\fi}
\newcommand{\gpt@datacorta}{\gpt@giorno/\gpt@mese/\gpt@anno}
\newcommand{\gpt@datalunga}{\number\numexpr\gpt@giorno\relax\
  \gpt@nomemese{\gpt@mese}\ \gpt@anno}
% \gpt@datalungada{2026-10-20} -> 20 ottobre 2026
\newcommand{\gpt@datalungada}[1]{\expandafter\gpt@datalungada@#1\@nil}
\def\gpt@datalungada@#1-#2-#3\@nil{\number\numexpr#3\relax\
  \gpt@nomemese{#2}\ #1}

\newcommand{\gpt@sigla}{\ifgpt@esterno VE\else VI\fi}
\newcommand{\gpt@id}{\gpt@sigla\,\gpt@anno-\gpt@mese-\gpt@giorno}
% "Interno" / "Esterno" con la maiuscola
\newcommand{\gpt@Uso}{\ifdefstring{\gpt@uso}{interno}{Interno}{Esterno}}

% Comandi pubblici utili nel testo
\newcommand{\datariunione}{\gpt@datalunga}
\newcommand{\codiceverbale}{\gpt@id}


% =====================================================================
%  SEZIONE 7 - Registro delle modifiche e versione automatica
%
%  \modifica{versione}{AAAA-MM-GG}{autore}{verificatore}{descrizione}
%  - la riga più recente va IN CIMA;
%  - la versione del documento è quella della PRIMA riga: si usa in
%    copertina, a piè di pagina e nel nome del PDF (scripts/build.py
%    la legge allo stesso modo).
% =====================================================================
\def\gpt@versione{}
\def\gpt@dataversione{}
\def\gpt@versioneletta{}
\def\gpt@righemodifiche{}
\newcommand{\modifica}[5]{%
  \gpt@controllaversione{#1}%
  \gpt@controlladata{#2}{#1}%
  \gpt@controllachiave{#3}%
  \gpt@controllachiave{#4}%
  \ifdefempty{\gpt@versione}{%
    \xdef\gpt@versione{\gpt@versioneletta}%
    \gdef\gpt@dataversione{#2}}{}%
  \gpt@registrapersone{#3}{#4}%
  \gappto\gpt@righemodifiche{#1 & #2 & \nome{#3} & \nome{#4} & #5 \\}}


% =====================================================================
%  SEZIONE 8 - Impaginazione generale
% =====================================================================
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.6em plus 0.2em}
\renewcommand{\arraystretch}{1.25}
\setlength{\aboverulesep}{0pt}
\setlength{\belowrulesep}{0pt}
\setlength{\LTpre}{0.4em}
\setlength{\LTpost}{0.4em}

\newcommand{\gpt@etichetta}[1]{%
  \leavevmode{\sffamily\scriptsize\bfseries\color{gptgrigio}\textls[90]{\MakeUppercase{#1}}}}
\newcommand{\gpt@intest}[1]{\gpt@etichetta{#1}}
% Intestazione di colonna per le vostre tabelle: \intestazione{Voti}
\newcommand{\intestazione}[1]{\gpt@etichetta{#1}}

% longtable fa sempre +1 al contatore delle tabelle, anche quando non ha
% didascalia. Per le nostre tabelle senza titolo (registro, decisioni,
% azioni) lo rimettiamo a posto: così "Tabella 1" è davvero la prima
% tabella del testo e l'elenco delle tabelle conta solo quelle vere.
% (\theHtable diverso evita nomi di collegamento doppi nel PDF.)
\newcounter{gptlt}
\newcommand{\gpt@primalt}{%
  \stepcounter{gptlt}\def\theHtable{gptlt.\arabic{gptlt}}}
\newcommand{\gpt@dopolt}{\addtocounter{table}{-1}}

% Titoli di sezione
\titleformat{\section}
  {\sffamily\Large\bfseries\color{gptinchiostro}}
  {\color{gptaccento}\thesection}{0.7em}{}
  [{\color{gptaccento}\vspace{3pt}\titlerule[1.2pt]}]
\titleformat{\subsection}
  {\sffamily\large\bfseries\color{gptinchiostro}}
  {\color{gptaccento}\thesubsection}{0.7em}{}
\titleformat{\subsubsection}
  {\sffamily\normalsize\bfseries\color{gptaccento}}
  {\thesubsubsection}{0.7em}{}
\titlespacing*{\section}{0pt}{1.6em}{0.9em}
% evita titoli isolati in fondo alla pagina
\AtBeginDocument{%
  \preto\section{\par\needspace{14\baselineskip}}%
  \preto\subsection{\par\needspace{6\baselineskip}}}
\titlespacing*{\subsection}{0pt}{1.2em}{0.4em}
\titlespacing*{\subsubsection}{0pt}{1em}{0.2em}

% Elenchi
\setlist{itemsep=0.2em,topsep=0.3em,parsep=0pt}
\setlist[itemize,1]{label={\color{gptaccento}\textbullet}}
\setlist[itemize,2]{label={\color{gptgrigio}--}}
\setlist[enumerate,1]{label={\color{gptaccento}\sffamily\bfseries\arabic*.}}

% Didascalie
\DeclareCaptionFont{gptacc}{\color{gptaccento}}
\DeclareCaptionFont{gptgr}{\color{gptgrigio}}
\captionsetup{font={small,sf,gptgr},labelfont={bf,gptacc},labelsep=period,
              justification=centering}
\captionsetup[table]{position=top}


% =====================================================================
%  SEZIONE 9 - Intestazione e piè di pagina
% =====================================================================
% testo a destra dell'intestazione
\newcommand{\gpt@testatadx}{%
  \ifgpt@verbale
    Verbale \gpt@sottotipo\ \textperiodcentered\ \gpt@datacorta
  \else
    \gpt@titolo
  \fi}
% testo a sinistra del piè di pagina
\newcommand{\gpt@piedesx}{%
  \ifgpt@verbale
    \gpt@id\ifx\gpt@versione\@empty\else\ \textperiodcentered\ v\gpt@versione\fi
  \else\ifgpt@documento
    \ifx\gpt@versione\@empty\else v\gpt@versione\ \textperiodcentered\ \fi
    Uso \gpt@uso
  \fi\fi}

\fancypagestyle{gpt}{%
  \fancyhf{}%
  \fancyhead[L]{\raisebox{-0.32\height}{\includegraphics[height=24pt]{\gpt@logo}}%
    \hspace{7pt}{\sffamily\small\bfseries\gpt@nomegruppo}}%
  \fancyhead[R]{\sffamily\small\color{gptgrigio}\gpt@testatadx}%
  \fancyfoot[L]{\sffamily\footnotesize\color{gptgrigio}\gpt@piedesx}%
  \fancyfoot[R]{\sffamily\footnotesize\color{gptgrigio}%
    Pagina \thepage\ di \pageref*{LastPage}}%
  \renewcommand{\headrulewidth}{0.4pt}%
  \renewcommand{\headrule}{{\color{gptlinea}%
    \hrule\@height\headrulewidth\@width\headwidth\vskip-\headrulewidth}}%
  \renewcommand{\footrulewidth}{0pt}}
\pagestyle{gpt}


% =====================================================================
%  SEZIONE 10 - Copertine (verbali e documenti)
% =====================================================================
\newcommand{\gpt@rigacop}[2]{\gpt@etichetta{#1} & #2 \\[2pt]}

% fascia in fondo alla copertina: gruppo, università, email, corso
\newcommand{\gpt@piedecopertina}{%
  {\color{gptlinea}\rule{\linewidth}{0.4pt}}\par\vspace{2pt}
  {\sffamily\footnotesize\color{gptgrigio}%
    \begin{tabularx}{\linewidth}{@{}X>{\raggedleft\arraybackslash}X@{}}
      \textbf{\color{gptinchiostro}\gpt@nomegruppo}%
        \ifdefempty{\gpt@numerogruppo}{}{\ \textperiodcentered\ Gruppo \gpt@numerogruppo}
      & \gpt@universita \\
      \ifdefempty{\gpt@email}{}{\href{mailto:\gpt@email}{\gpt@email}}
      & \gpt@corso\ifdefempty{\gpt@annoaccademico}{}{\ \textperiodcentered\
          A.A.~\gpt@annoaccademico}
    \end{tabularx}}}

% parte alta della copertina: logo, etichetta, titolo, sottotitolo
\newcommand{\gpt@testacopertina}[3]{% #1 etichetta, #2 dimensione titolo, #3 sottotitolo
  \begin{center}
    \vspace*{0.4cm}
    \includegraphics[width=6.4cm]{\gpt@logo}\par
    \vspace{1.4cm}
    {\sffamily\small\bfseries\color{gptaccento}%
      \textls[260]{\MakeUppercase{#1}}\par}
    \vspace{0.5cm}
    {\sffamily\bfseries\fontsize{#2}{\numexpr#2*5/4\relax}\selectfont\gpt@titolo\par}
    \vspace{0.45cm}
    {\large\color{gptgrigio}#3\par}
    \vspace{0.25cm}
    {\color{gptaccento}\rule{2.2cm}{1.2pt}\par}
  \end{center}}

\newcommand{\gpt@inizioschede}{%
  \begin{center}
    \begin{tabular}{@{}>{\raggedleft\arraybackslash}p{3.6cm}
                       @{\hspace{1.2em}}>{\raggedright\arraybackslash}p{7.6cm}@{}}}
\newcommand{\gpt@fineschede}{\end{tabular}\end{center}}

\newcommand{\gpt@copertinaverbale}{%
  \thispagestyle{empty}%
  \gpt@testacopertina{Verbale \gpt@sottotipo}{25}{\gpt@datalunga}%
  \vfill
  \gpt@inizioschede
      \gpt@rigacop{Identificativo}{\gpt@id}
      \gpt@rigacop{Versione}{\gpt@versione}
      \gpt@rigacop{Uso}{\gpt@Uso}
      \gpt@rigacop{Redattore}{\nome{\gpt@redattore}}
      \gpt@rigacop{Verificatore}{\nome{\gpt@verificatore}}
      \ifdefempty{\gpt@capitolato}{}{\gpt@rigacop{Capitolato}{\gpt@capitolato}}
      \ifdefempty{\gpt@destinatari}{}{\gpt@rigacop{Destinatari}{\gpt@destinatari}}
  \gpt@fineschede
  \vfill
  \gpt@piedecopertina
  \newpage}

\newcommand{\gpt@copertinadocumento}{%
  \thispagestyle{empty}%
  \gpt@testacopertina{Documento a uso \gpt@uso}{28}{Versione \gpt@versione}%
  \vfill
  \gpt@inizioschede
      \gpt@rigacop{Versione}{\gpt@versione}
      \gpt@rigacop{Ultima modifica}{\gpt@datalungada{\gpt@dataversione}}
      \gpt@rigacop{Uso}{\gpt@Uso}
      \ifdefempty{\gpt@responsabile}{}{\gpt@rigacop{Responsabile}{\nome{\gpt@responsabile}}}
      \gpt@rigacop{Redattori}{\gpt@stampaautori}
      \gpt@rigacop{Verificatori}{\gpt@stampaverificatori}
      \ifdefempty{\gpt@capitolato}{}{\gpt@rigacop{Capitolato}{\gpt@capitolato}}
      \ifdefempty{\gpt@destinatari}{}{\gpt@rigacop{Destinatari}{\gpt@destinatari}}
  \gpt@fineschede
  \vfill
  \gpt@piedecopertina
  \newpage}


% =====================================================================
%  SEZIONE 11 - Parti automatiche: registro, presenze, indice
% =====================================================================
% Registro delle modifiche: una tabella che va a capo pagina da sola
% (longtable), quindi regge anche le centinaia di righe delle Norme.
\newcommand{\gpt@intestregistro}{%
  \gpt@intest{Versione} & \gpt@intest{Data} & \gpt@intest{Autore}
    & \gpt@intest{Verificatore} & \gpt@intest{Descrizione} \\}
\newcommand{\gpt@registro}{%
  \pdfbookmark[1]{Registro delle modifiche}{gpt-registro}%
  \section*{Registro delle modifiche}
  \begingroup
  \gpt@primalt
  \setlength{\LTpost}{0pt}%
  \begin{longtable}{@{}p{1.6cm}p{2cm}>{\raggedright\arraybackslash}p{3.3cm}
      >{\raggedright\arraybackslash}p{3.3cm}
      >{\raggedright\arraybackslash}p{\dimexpr\linewidth-10.2cm-8\tabcolsep\relax}@{}}
    \toprule\gpt@intestregistro\midrule\endfirsthead
    \toprule\gpt@intestregistro\midrule\endhead
    \bottomrule\endfoot
    \gpt@righemodifiche
  \end{longtable}%
  \endgroup
  \gpt@dopolt}

% Informazioni sulla riunione e presenze (solo verbali)
\tcbset{gptinfo/.style={enhanced,breakable,sharp corners,boxrule=0pt,
  colback=gptsfondo,frame hidden,left=12pt,right=10pt,top=8pt,bottom=8pt,
  borderline west={2.5pt}{0pt}{gptaccento},before skip=0.6em,after skip=0.8em}}

\newcommand{\gpt@rigapres}[1]{%
  \nome{#1} & \csuse{gpt@matr@#1} & \leavevmode
  \gpt@seassente{#1}{{\color{gptgrigio}\itshape Assente}}%
    {{\color{gptaccento}\textbullet}\ Presente} \\}

\newcommand{\gpt@informazioni}{%
  \pdfbookmark[1]{Informazioni sulla riunione}{gpt-informazioni}%
  \section*{Informazioni sulla riunione}
  \begin{tcolorbox}[gptinfo]
    \begin{tabularx}{\linewidth}{@{}p{2.5cm}>{\raggedright\arraybackslash}X
                                   p{2.5cm}>{\raggedright\arraybackslash}X@{}}
      \gpt@etichetta{Data} & \gpt@datalunga
        & \gpt@etichetta{Orario} & \gpt@orainizio\,--\,\gpt@orafine \\
      \gpt@etichetta{Luogo} & \gpt@luogo
        & \gpt@etichetta{Tipo} & Verbale \gpt@sottotipo \\
      \gpt@etichetta{Redattore} & \nome{\gpt@redattore}
        & \gpt@etichetta{Verificatore} & \nome{\gpt@verificatore}
    \end{tabularx}
  \end{tcolorbox}
  \subsection*{Partecipanti del gruppo}
  \gpt@preparapresenze
  \begin{tabularx}{\linewidth}{@{}Xp{3cm}p{3cm}@{}}
    \toprule
    \gpt@intest{Membro} & \gpt@intest{Matricola} & \gpt@intest{Presenza} \\
    \midrule
    \gpt@righepresenze
    \bottomrule
  \end{tabularx}\par
  \ifgpt@haesterni
    \subsection*{Partecipanti esterni}
    \begin{tabularx}{\linewidth}{@{}p{5cm}>{\raggedright\arraybackslash}X@{}}
      \toprule
      \gpt@intest{Nome} & \gpt@intest{Ruolo e organizzazione} \\
      \midrule
      \gpt@righeesterni
      \bottomrule
    \end{tabularx}\par
  \fi}

% Indice ed elenchi (solo documenti). Gli elenchi di figure e tabelle
% compaiono da soli se il documento ne contiene almeno una: il numero
% viene salvato nel file .aux alla fine della compilazione precedente
% (latexmk ricompila da solo tutte le volte che serve).
\def\gpt@nfigure{0}\def\gpt@ntabelle{0}
\newcommand{\gpt@contatori}[2]{\gdef\gpt@nfigure{#1}\gdef\gpt@ntabelle{#2}}
\newcommand{\gpt@salvacontatori}{%
  \if@filesw
    \immediate\write\@auxout{\string\gpt@contatori{\the\c@figure}{\the\c@table}}%
  \fi}
\newcommand{\gpt@indice}{%
  \clearpage
  \pdfbookmark[1]{\contentsname}{gpt-indice}%
  {\hypersetup{linkcolor=gptinchiostro}\tableofcontents}%
  \ifnum\gpt@nfigure>0
    \pdfbookmark[1]{\listfigurename}{gpt-figure}%
    {\hypersetup{linkcolor=gptinchiostro}\listoffigures}%
  \fi
  \ifnum\gpt@ntabelle>0
    \pdfbookmark[1]{\listtablename}{gpt-tabelle}%
    {\hypersetup{linkcolor=gptinchiostro}\listoftables}%
  \fi
  \clearpage}


% =====================================================================
%  SEZIONE 12 - Lettera
% =====================================================================
\newcommand{\gpt@aperturalettera}{%
  \thispagestyle{empty}%
  % carta intestata
  \noindent
  \begin{minipage}[c]{2.1cm}\includegraphics[width=2.1cm]{\gpt@logo}\end{minipage}%
  \hspace{0.6cm}%
  \begin{minipage}[c]{\dimexpr\linewidth-2.7cm\relax}
    {\sffamily\LARGE\bfseries\gpt@nomegruppo\par}\vspace{3pt}
    {\sffamily\small\color{gptgrigio}%
      \ifdefempty{\gpt@numerogruppo}{}{Gruppo \gpt@numerogruppo\ \textperiodcentered\ }%
      \gpt@corso\ \textperiodcentered\ \gpt@universita\par
      \ifdefempty{\gpt@email}{}{\href{mailto:\gpt@email}{\gpt@email}}\par}
  \end{minipage}\par
  \vspace{0.35cm}{\color{gptaccento}\rule{\linewidth}{1.2pt}}\par
  \vspace{0.9cm}
  % luogo e data, destinatari, oggetto
  {\raggedleft\gpt@luogo, \gpt@datalunga\par}
  \vspace{0.6cm}
  \ifdefempty{\gpt@destinatari}{}{%
    \begin{minipage}[t]{0.62\linewidth}\raggedright\gpt@destinatari\end{minipage}\par
    \vspace{0.9cm}}%
  \noindent{\sffamily\bfseries\color{gptaccento}Oggetto:}\ %
    \textbf{\ifdefempty{\gpt@oggetto}{\gpt@titolo}{\gpt@oggetto}}\par
  \vspace{0.5cm}}

\newcommand{\gpt@chiusuralettera}{%
  \par\vspace{0.4cm}%
  \needspace{7\baselineskip}%
  \gpt@chiusura\par
  \vspace{0.6cm}%
  \hfill
  \begin{minipage}[t]{7cm}\centering
    \ifdefempty{\gpt@responsabile}
      {\textbf{\gpt@nomegruppo}}
      {\textbf{\nome{\gpt@responsabile}}\par
       {\small\color{gptgrigio}Responsabile del \gpt@nomegruppo}}%
  \end{minipage}\par}


% =====================================================================
%  SEZIONE 13 - Firma del proponente (solo verbali esterni)
% =====================================================================
\newcommand{\gpt@lineafirma}[2]{%
  \begin{minipage}[t]{0.42\linewidth}
    \vspace{1.6cm}
    {\color{gptinchiostro}\rule{\linewidth}{0.5pt}}\par\vspace{2pt}
    {\sffamily\footnotesize\color{gptgrigio}#1}\par
    {\small #2}
  \end{minipage}}
\newcommand{\gpt@approvazione}{%
  \par\vspace{1em}
  \needspace{14\baselineskip}
  \pdfbookmark[1]{Approvazione}{gpt-approvazione}%
  \section*{Approvazione}
  Il presente verbale è stato letto e approvato dal proponente%
  \ifdefempty{\gpt@firmaente}{}{ (\gpt@firmaente)}.\par
  \noindent\gpt@lineafirma{Luogo e data}{}\hfill
  \gpt@lineafirma{Firma}{\gpt@firmanome%
    \ifdefempty{\gpt@firmaente}{}{\ifdefempty{\gpt@firmanome}{}{, }\gpt@firmaente}}\par}


% =====================================================================
%  SEZIONE 14 - Comandi per il testo
% =====================================================================
% Decisioni:  \begin{decisioni} \decisione{...} \end{decisioni}
\newcounter{gptdecisione}
\newenvironment{decisioni}{%
  \setcounter{gptdecisione}{0}%
  \gpt@primalt
  \begin{longtable}{@{}p{1.1cm}
      >{\raggedright\arraybackslash}p{\dimexpr\linewidth-1.1cm-2\tabcolsep\relax}@{}}
    \toprule
    \gpt@intest{ID} & \gpt@intest{Decisione} \\
    \midrule\endhead
    \bottomrule\endfoot}
  {\end{longtable}\gpt@dopolt}
\newcommand{\decisione}[1]{%
  \stepcounter{gptdecisione}%
  \leavevmode{\sffamily\bfseries\color{gptaccento}D\thegptdecisione} & #1 \\}

% Azioni:  \begin{azioni} \azione[#12]{attività}{responsabili}{scadenza} \end{azioni}
\newcounter{gptazione}
\newenvironment{azioni}{%
  \setcounter{gptazione}{0}%
  \gpt@primalt
  \begin{longtable}{@{}p{1cm}
      >{\raggedright\arraybackslash}p{\dimexpr\linewidth-1cm-3.7cm-2.15cm-1.45cm-8\tabcolsep\relax}
      >{\raggedright\arraybackslash}p{3.7cm}p{2.15cm}p{1.45cm}@{}}
    \toprule
    \gpt@intest{ID} & \gpt@intest{Attività} & \gpt@intest{Responsabile}
      & \gpt@intest{Scadenza} & \gpt@intest{Ticket} \\
    \midrule\endhead
    \bottomrule\endfoot}
  {\end{longtable}\gpt@dopolt}
\newcommand{\azione}[4][--]{%
  \stepcounter{gptazione}%
  \leavevmode{\sffamily\bfseries\color{gptaccento}A\thegptazione} & #2 & \nomi{#3} & #4 &
  \leavevmode{\color{gptgrigio}#1} \\}

% Domande e risposte:  \domanda{domanda}{risposta}
\newcommand{\gpt@qa}[1]{{\sffamily\bfseries\color{gptaccento}#1}}
\newcommand{\domanda}[2]{%
  \begin{itemize}[leftmargin=2em,labelwidth=1.2em,labelsep=0.8em,align=left,
                  itemsep=0.15em,topsep=0.5em]
    \item[\gpt@qa{D}] {\bfseries #1}
    \item[\gpt@qa{R}] #2
  \end{itemize}}

% Riquadro di nota:  \begin{nota}[Titolo] ... \end{nota}
\newtcolorbox{nota}[1][Nota]{enhanced,breakable,sharp corners,boxrule=0pt,
  frame hidden,colback=gptsfondo,left=12pt,right=10pt,top=6pt,bottom=6pt,
  borderline west={2.5pt}{0pt}{gptaccento},
  fonttitle=\sffamily\small\bfseries,coltitle=gptaccento,
  attach title to upper={\par\vspace{2pt}},title={#1}}

% Immagini:  \figura[larghezza]{cartella/file.png}{didascalia}
%   larghezza in frazione della riga, es. 0.6  (predefinito 0.85)
\newcommand{\figura}[3][0.85]{%
  \begin{figure}[H]
    \centering
    {\setlength{\fboxsep}{0pt}\setlength{\fboxrule}{0.4pt}\color{gptlinea}%
      \fbox{\includegraphics[width=#1\linewidth]{#2}}}
    \caption{#3}
  \end{figure}}
% stessa cosa ma senza cornice (per foto o loghi)
\newcommand{\figurasenzabordo}[3][0.85]{%
  \begin{figure}[H]
    \centering\includegraphics[width=#1\linewidth]{#2}
    \caption{#3}
  \end{figure}}

% Termine di glossario:  \glo{termine}  ->  termine con pedice G
\newcommand{\glo}[1]{#1\textsubscript{\sffamily\bfseries\color{gptaccento}G}}


% =====================================================================
%  SEZIONE 15 - Montaggio automatico del documento
% =====================================================================
% Controlli finali: partono a \begin{document}, quando il preambolo è
% stato letto tutto.
\newcommand{\gpt@controllifinali}{%
  \ifdefempty{\gpt@titolo}{\ClassError{gpt}{Manca il titolo: scrivete
    \string\titolo\string{...\string} nel preambolo}{}}{}%
  \ifgpt@lettera\else
    \ifdefempty{\gpt@versione}{\ClassError{gpt}{Il registro delle modifiche
      e' vuoto: aggiungete almeno la riga
      \string\modifica\string{0.1.0\string}\string{AAAA-MM-GG\string}%
      \string{autore\string}\string{--\string}\string{Prima stesura\string}}{}}{}%
  \fi
  \ifgpt@documento\else
    \ifdefempty{\gpt@anno}{\ClassError{gpt}{Manca la data: scrivete
      \string\data\string{AAAA-MM-GG\string} nel preambolo}{}}{}%
  \fi
  \ifgpt@verbale
    \gpt@secomponentivuoti{\ClassError{gpt}{Manca l'elenco dei componenti:
      scrivete \string\componenti\string{...\string} (copiatelo dal modello in
      template/modelli/)}{}}{}%
    \gpt@controllaassenti
  \fi}

\AtBeginDocument{%
  % valori predefiniti che dipendono dal tipo di documento
  \ifdefempty{\gpt@uso}{%
    \ifgpt@verbale\global\let\gpt@uso\gpt@sottotipo\else\gdef\gpt@uso{esterno}\fi}{}%
  \ifdefempty{\gpt@luogo}{%
    \ifgpt@lettera\gdef\gpt@luogo{Padova}\else\gdef\gpt@luogo{--}\fi}{}%
  % nomi in italiano anche se babel-italian manca
  \renewcommand{\figurename}{Figura}%
  \renewcommand{\tablename}{Tabella}%
  \providecommand{\contentsname}{}\renewcommand{\contentsname}{Indice}%
  \providecommand{\listfigurename}{}\renewcommand{\listfigurename}{Elenco delle figure}%
  \providecommand{\listtablename}{}\renewcommand{\listtablename}{Elenco delle tabelle}%
  % proprietà del PDF
  \ifgpt@verbale
    \hypersetup{pdftitle={Verbale \gpt@sottotipo\ \gpt@datacorta\ -- \gpt@titolo}}%
  \else
    \hypersetup{pdftitle={\gpt@titolo\ifx\gpt@versione\@empty\else\space v\gpt@versione\fi}}%
  \fi
  \hypersetup{pdfauthor={\gpt@nomegruppo},pdfsubject={\gpt@corso}}}

% Le parti fisse si inseriscono da sole subito dopo \begin{document}
\AfterEndPreamble{%
  \gpt@controllifinali
  \ifgpt@lettera
    \gpt@aperturalettera
  \else
    \ifgpt@documento\gpt@copertinadocumento\else\gpt@copertinaverbale\fi
    \gpt@registro
    \ifgpt@verbale\gpt@informazioni\fi
    \ifgpt@documento\gpt@indice\fi
  \fi}

% ...e alla fine del documento
\AtEndDocument{%
  \ifgpt@esterno\gpt@approvazione\fi
  \ifgpt@lettera\gpt@chiusuralettera\fi
  \gpt@salvacontatori}


% =====================================================================
%  SEZIONE 16 - Dati del gruppo (template/dati-gruppo.tex)
% =====================================================================
\gpt@datigruppotrue
\InputIfFileExists{dati-gruppo.tex}{}
  {\ClassError{gpt}{File dati-gruppo.tex non trovato: compilate con
     scripts/build.py oppure da VS Code (serve il file latexmkrc)}{}}
\gpt@datigruppofalse

\endinput
