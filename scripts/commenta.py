#!/usr/bin/env python3
"""
commenta.py -- scrive (o aggiorna) un commento del bot in una pull request.

    python3 scripts/commenta.py --pr 12 --marcatore anteprima-pdf --file commento.md

Ogni automazione ha il suo marcatore, nascosto nel commento: così ognuna
aggiorna sempre e solo il proprio commento, senza sovrascrivere quelli
delle altre. Servono GH_TOKEN e GITHUB_REPOSITORY (nelle Actions ci sono).
"""
import argparse
import sys
from pathlib import Path

import registro


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pr", type=int, required=True)
    p.add_argument("--marcatore", required=True)
    p.add_argument("--file", required=True)
    args = p.parse_args()
    testo = Path(args.file).read_text(encoding="utf-8")
    registro.GitHub().commenta(args.pr, testo, marcatore=f"<!-- {args.marcatore} -->")
    return 0


if __name__ == "__main__":
    sys.exit(main())
