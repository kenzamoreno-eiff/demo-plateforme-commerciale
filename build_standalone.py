"""Construit la version autonome de la démo : un seul fichier HTML.

    python tools/build_standalone.py

Produit dist/demo_autonome.html : CSS, données et JavaScript intégrés.
Ce fichier s'ouvre par double-clic dans n'importe quel navigateur, sans
Python ni installation (utile sur un poste où les outils sont bloqués).

Option --artefact : produit dist/demo_artefact.html, sans les balises
<html>/<head>/<body> (format attendu pour une publication en page web hébergée).
"""

import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
FRONT = RACINE / "frontend"
DIST = RACINE / "dist"


def construire(artefact=False):
    html = (FRONT / "index.html").read_text(encoding="utf-8")
    css = (FRONT / "styles.css").read_text(encoding="utf-8")
    seed = (FRONT / "seed.js").read_text(encoding="utf-8")
    app = (FRONT / "app.js").read_text(encoding="utf-8")

    html = html.replace('<link rel="stylesheet" href="styles.css">', "<style>\n" + css + "\n</style>")
    html = html.replace('<script src="seed.js"></script>', "<script>\n" + seed + "\n</script>")
    html = html.replace('<script src="app.js"></script>', "<script>\n" + app + "\n</script>")

    if artefact:
        for motif in (r"<!doctype html>\s*", r"<html[^>]*>\s*", r"</html>\s*", r"<head>\s*", r"</head>\s*",
                      r"<body>\s*", r"</body>\s*", r'<meta charset="utf-8">\s*', r'<meta name="viewport"[^>]*>\s*'):
            html = re.sub(motif, "", html, flags=re.I)
        sortie = DIST / "demo_artefact.html"
    else:
        sortie = DIST / "demo_autonome.html"

    DIST.mkdir(exist_ok=True)
    sortie.write_text(html, encoding="utf-8")
    print(f"Écrit : {sortie} ({sortie.stat().st_size // 1024} Ko)")


if __name__ == "__main__":
    construire(artefact="--artefact" in sys.argv)
