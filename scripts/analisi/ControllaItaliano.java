// Controllo grammaticale e ortografico in italiano con LanguageTool.
//
// Lo lancia scripts/analisi_testo.py: non serve usarlo a mano.
//     java -cp textidote.jar ControllaItaliano.java [--disattiva R1,R2] a.txt b.txt ...
//
// LanguageTool (con i dizionari italiano e inglese) e' dentro textidote.jar:
// https://github.com/sylvainhalle/textidote (licenza GPL 3), scaricato
// dalla CI o con: python3 scripts/analisi_testo.py --scarica-lt
//
// Per ogni problema stampa una riga separata da tabulazioni:
//     file  inizio  fine  regola  categoria  inglese  messaggio  suggerimenti
// file = indice del file negli argomenti; inizio e fine = posizioni nel
// testo (in unita' UTF-16, come le stringhe Java); inglese = 1 se la parola
// segnalata come errore di battitura e' una parola inglese corretta.

import java.io.FileDescriptor;
import java.io.FileOutputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.languagetool.JLanguageTool;
import org.languagetool.language.AmericanEnglish;
import org.languagetool.language.Italian;
import org.languagetool.rules.Rule;
import org.languagetool.rules.RuleMatch;
import org.languagetool.rules.spelling.SpellingCheckRule;

public class ControllaItaliano {
    private static String pulisci(String s) {
        if (s == null) return "";
        return s.replaceAll("</?suggestion>", "\"").replaceAll("[\\t\\r\\n]+", " ").trim();
    }

    public static void main(String[] args) throws Exception {
        Logger.getLogger("").setLevel(Level.SEVERE);
        PrintStream out = new PrintStream(new FileOutputStream(FileDescriptor.out), false,
                                          StandardCharsets.UTF_8);
        List<String> disattiva = new ArrayList<>();
        List<Path> file = new ArrayList<>();
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--disattiva") && i + 1 < args.length) {
                for (String id : args[++i].split(",")) {
                    if (!id.isBlank()) disattiva.add(id.strip());
                }
            } else {
                file.add(Path.of(args[i]));
            }
        }

        JLanguageTool it = new JLanguageTool(new Italian());
        for (String id : disattiva) it.disableRule(id);

        // Solo il correttore ortografico inglese: serve a non segnalare come
        // errori le parole inglesi del mestiere (commit, branch, deploy...).
        JLanguageTool en = new JLanguageTool(new AmericanEnglish());
        for (Rule r : en.getAllRules()) {
            if (!(r instanceof SpellingCheckRule)) en.disableRule(r.getId());
        }
        Map<String, Boolean> inglese = new HashMap<>();

        for (int n = 0; n < file.size(); n++) {
            String testo = Files.readString(file.get(n), StandardCharsets.UTF_8);
            for (RuleMatch m : it.check(testo)) {
                Rule r = m.getRule();
                boolean eng = false;
                if (r instanceof SpellingCheckRule) {
                    String parola = testo.substring(m.getFromPos(), m.getToPos());
                    Boolean noto = inglese.get(parola);
                    if (noto == null) {
                        noto = en.check(parola).isEmpty();
                        inglese.put(parola, noto);
                    }
                    eng = noto;
                }
                List<String> sugg = m.getSuggestedReplacements();
                String s = String.join("|", sugg.subList(0, Math.min(3, sugg.size())));
                out.print(n + "\t" + m.getFromPos() + "\t" + m.getToPos() + "\t"
                          + r.getId() + "\t" + r.getCategory().getId() + "\t"
                          + (eng ? 1 : 0) + "\t" + pulisci(m.getMessage()) + "\t"
                          + pulisci(s) + "\n");
            }
        }
        out.flush();
    }
}
