## Cosa cambia

<!-- Una o due righe: quale documento e cosa è stato modificato. -->

Closes #<!-- numero della issue -->

## Registro delle modifiche

<!--
Il registro lo scrive il bot dopo il merge (GUIDA.md, sezione 5).
1. Scrivete qui sotto, dopo "Descrizione:", COSA è cambiato e DOVE: è il testo della riga del registro.
   Esempio: Descrizione: Stesura della sezione 3, Gestione dei rischi
   Se la lasciate vuota, il bot usa il titolo della PR.
2. A destra, in "Labels", scegliete l'etichetta di versione:
   - contenuto     prima stesura o parti nuove     0.2.1 -> 0.3.0
   - correzione    correzioni piccole               0.2.0 -> 0.2.1
   - approvazione  versione approvata               0.3.0 -> 1.0.0
                   in una PR separata; la mette il Responsabile dello sprint.
                   Nella riga c'è solo il Responsabile, senza verificatore
   - stesura-e-approvazione   contenuto e approvazione nella stessa PR: due righe,
                   0.1.0 con autore e verificatore, poi 1.0.0 con il Responsabile
                   (la mette il Responsabile dello sprint)
   - nessuna       ritocchi che non meritano una versione: il registro non cambia
Il commento "📝 Registro delle modifiche" qui sotto mostra la riga prima del merge.
-->

Descrizione: 

## Checklist dell'autore

- [ ] Ho modificato un solo documento o un solo argomento.
- [ ] Il `.tex` è nella cartella giusta: `Candidatura/`, `RTB/` o `PB/`, poi `documenti/` o `verbali/`, poi `interni/` o `esterni/`.
- [ ] Non ho caricato PDF: quello accanto al `.tex` lo crea la CI dopo il merge.
- [ ] Ho scritto la `Descrizione:` (**cosa** è cambiato e **dove**) e messo l'etichetta di versione (`contenuto` o `correzione`; nessuna per i ritocchi minimi). Non ho scritto righe `\modifica` nel `.tex`.
- [ ] I termini tecnici nuovi sono marcati con `\glo{}` e aggiunti al Glossario.
- [ ] Ho scelto come revisore il Verificatore, diverso da me.

## Checklist del Verificatore

- [ ] Ho aperto il PDF dal commento automatico e l'ho letto per intero.
- [ ] Il contenuto è corretto e coerente con gli altri documenti e con le decisioni prese.
- [ ] Ortografia, date, nomi e riferimenti sono corretti (aiuta il commento **🔎 Analisi dei testi**, che però non sostituisce la lettura).
- [ ] Nel commento **📝 Registro delle modifiche** etichetta e descrizione sono giuste (GUIDA.md, R12).
- [ ] Se il documento va approvato (`1.0.0`, `2.0.0`…), l'etichetta `approvazione` l'ha messa il Responsabile.
- [ ] Il commento automatico non ha avvisi sul registro (sotto *Da controllare*).
- [ ] La compilazione automatica è verde.
- [ ] Ho approvato con *Review changes* → **Approve**: è così che il bot mi registra come verificatore.
