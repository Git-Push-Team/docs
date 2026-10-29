## Cosa cambia

<!-- Una o due righe: quale documento e cosa è stato modificato. -->

Closes #<!-- numero della issue -->

## Checklist dell'autore

- [ ] Ho modificato un solo documento o un solo argomento.
- [ ] Il `.tex` è nella cartella giusta: `Candidatura/`, `RTB/` o `PB/`, poi `documenti/` o `verbali/`, poi `interni/` o `esterni/`.
- [ ] Non ho caricato PDF: quello accanto al `.tex` lo crea la CI dopo il merge.
- [ ] Ho aggiunto **in cima** al registro una riga `\modifica{...}` con la nuova versione, la mia chiave, `--` al posto del verificatore e una descrizione che dice **cosa** è cambiato e **dove** (GUIDA.md, sezione 5).
- [ ] I termini tecnici nuovi sono marcati con `\glo{}` e aggiunti al Glossario.
- [ ] Ho scelto come revisore il Verificatore, diverso da me.

## Checklist del Verificatore

- [ ] Ho aperto il PDF dal commento automatico e l'ho letto per intero.
- [ ] Il contenuto è corretto e coerente con gli altri documenti e con le decisioni prese.
- [ ] Ortografia, date, nomi e riferimenti sono corretti.
- [ ] Ho registrato la verifica: la mia chiave al posto di `--` nella riga in cima al registro, con la data di oggi (niente righe di sola "Verifica"; vedi GUIDA.md, R12).
- [ ] Se un documento arriva a `1.0.0` (o `2.0.0`…), il Responsabile ha aggiunto `[spagnoli]` in fondo alla riga.
- [ ] Il commento automatico non ha avvisi sul registro (sotto *Da controllare*).
- [ ] La compilazione automatica è verde.
