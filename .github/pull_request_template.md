## Cosa cambia

<!-- Una o due righe: quale documento e cosa è stato modificato. -->

Closes #<!-- numero della issue -->

## Checklist dell'autore

- [ ] Ho modificato un solo documento o un solo argomento.
- [ ] Il `.tex` è nella cartella giusta: `Candidatura/`, `RTB/` o `PB/`, poi `documenti/` o `verbali/`, poi `interni/` o `esterni/`.
- [ ] Non ho caricato PDF: quello accanto al `.tex` lo crea la CI dopo il merge.
- [ ] Ho aggiunto **in cima** al registro una riga `\modifica{...}` con la nuova versione (la versione si legge da lì: non va scritta da nessun'altra parte).
- [ ] I termini tecnici nuovi sono marcati con `\glo{}` e aggiunti al Glossario.
- [ ] Ho scelto come revisore il Verificatore, diverso da me.

## Checklist del Verificatore

- [ ] Ho aperto il PDF dal commento automatico e l'ho letto per intero.
- [ ] Il contenuto è corretto e coerente con gli altri documenti e con le decisioni prese.
- [ ] Ortografia, date, nomi e riferimenti sono corretti.
- [ ] Ho registrato la verifica nel registro: riga `\modifica{1.0.0}{AAAA-MM-GG}{autore}{verificatore}{Verifica e approvazione}` per la prima approvazione, oppure la mia chiave al posto di `--` nella riga in cima (vedi GUIDA.md, R12).
- [ ] La compilazione automatica è verde.
