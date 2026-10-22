# =====================================================================
#  latexmkrc  --  impostazioni di latexmk per tutto il repository
#
#  A cosa serve: dice a LaTeX dove trovare la classe (gpt.cls), i dati
#  del gruppo e il logo (cartella template/) e le immagini condivise
#  (cartella allegati/), qualunque sia la cartella del documento.
#
#  Non serve usarlo a mano: lo usano già scripts/build.py e VS Code,
#  entrambi facendo partire latexmk dalla cartella del documento.
#  Se proprio volete farlo a mano, dalla cartella del documento:
#     latexmk -r ../../latexmkrc VI-2026-10-26.tex
# =====================================================================
use File::Basename;
use Cwd 'abs_path';

# Cartella principale del repository = la cartella di questo file
# (latexmk tiene l'elenco dei file di configurazione che sta leggendo).
my $rc   = (@main::rc_files_read) ? $main::rc_files_read[-1] : 'latexmkrc';
my $root = dirname(abs_path($rc));
my $sep  = ($^O eq 'MSWin32') ? ';' : ':';

# Dove LaTeX cerca i file, in quest'ordine:
#   1. template/       la classe gpt.cls e dati-gruppo.tex
#   2. template/img/   il logo del gruppo
#   3. .               la cartella del documento (capitoli, immagini locali)
#   4. allegati/       le immagini condivise: \figura{cartella/file.png}
#   5. le cartelle standard di TeX (le aggiunge il separatore finale)
my $old = defined $ENV{'TEXINPUTS'} ? $ENV{'TEXINPUTS'} : '';
$old .= $sep if ($old ne '' && substr($old, -1) ne $sep);
$ENV{'TEXINPUTS'} = join($sep, "$root/template", "$root/template/img", '.',
                         "$root/allegati", '') . $old;

# PDF con pdflatex; in caso di errore si ferma subito e indica file e riga
$pdf_mode = 1;
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error -file-line-error %O %S';
