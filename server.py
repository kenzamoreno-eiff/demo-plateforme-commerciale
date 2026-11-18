"""Serveur de la démo : sert l'interface et une petite API JSON.

Lancement :   python backend/server.py
Options   :   --port 8000   --reset (repart des données de démonstration)

Aucune installation : uniquement la bibliothèque standard de Python (3.9 ou plus).
Le serveur joue le rôle de SharePoint (stockage) et de Power Automate
(règles, notifications) le temps de la démonstration.
"""

import argparse
import datetime
import json
import mimetypes
import sqlite3
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))

import actions  # noqa: E402
import db  # noqa: E402

RACINE = ICI.parent
FRONT = RACINE / "frontend"
DONNEES = RACINE / "data"
CHEMIN_DB = DONNEES / "plateforme.db"
VERSION = "demo-1"
VERROU = threading.Lock()
SEED = db.lire_seed(FRONT / "seed.js")


def contexte():
    maintenant = datetime.datetime.now()
    return {"aujourdhui": maintenant.strftime("%Y-%m-%d"),
            "maintenant": maintenant.strftime("%Y-%m-%d %H:%M"), "seed": SEED}


def preparer_base(reset=False):
    DONNEES.mkdir(exist_ok=True)
    conn = db.ouvrir(CHEMIN_DB)
    if reset or db.est_vide(conn):
        db.sauver(conn, actions.etat_initial(SEED))
    conn.close()


class Gestionnaire(BaseHTTPRequestHandler):
    server_version = "DemoPlateforme/1"

    def log_message(self, fmt, *args):
        sys.stderr.write("  " + (fmt % args) + "\n")

    # ---------- réponses ----------
    def envoyer(self, code, corps, type_mime, entetes=None):
        donnees = corps.encode("utf-8") if isinstance(corps, str) else corps
        self.send_response(code)
        self.send_header("Content-Type", type_mime)
        self.send_header("Content-Length", str(len(donnees)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (entetes or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(donnees)

    def json(self, obj, code=200):
        self.envoyer(code, json.dumps(obj, ensure_ascii=False), "application/json; charset=utf-8")

    # ---------- GET ----------
    def do_GET(self):
        chemin = urlparse(self.path).path
        if chemin == "/api/health":
            return self.json({"ok": True, "mode": "python", "version": VERSION})
        if chemin == "/api/etat":
            with VERROU:
                conn = db.ouvrir(CHEMIN_DB)
                st = db.charger(conn)
                conn.close()
            return self.json(st)
        if chemin.startswith("/api/export/") and chemin.endswith(".csv"):
            table = chemin[len("/api/export/"):-4]
            try:
                with VERROU:
                    conn = db.ouvrir(CHEMIN_DB)
                    texte = db.exporter_csv(conn, table)
                    conn.close()
            except KeyError:
                return self.json({"erreur": "Liste inconnue : " + table}, 404)
            return self.envoyer(200, texte, "text/csv; charset=utf-8",
                                {"Content-Disposition": f'attachment; filename="{table}.csv"'})
        return self.fichier(chemin)

    def fichier(self, chemin):
        if chemin in ("", "/"):
            chemin = "/index.html"
        cible = (FRONT / chemin.lstrip("/")).resolve()
        if FRONT not in cible.parents or not cible.is_file():
            return self.json({"erreur": "Introuvable"}, 404)
        type_mime = mimetypes.guess_type(cible.name)[0] or "application/octet-stream"
        if type_mime.startswith("text/") or type_mime == "application/javascript":
            type_mime += "; charset=utf-8"
        self.envoyer(200, cible.read_bytes(), type_mime)

    # ---------- POST ----------
    def do_POST(self):
        chemin = urlparse(self.path).path
        if not chemin.startswith("/api/action/"):
            return self.json({"erreur": "Introuvable"}, 404)
        nom = chemin[len("/api/action/"):]
        fonction = actions.ACTIONS.get(nom)
        if fonction is None:
            return self.json({"erreur": "Action inconnue : " + nom}, 404)
        try:
            longueur = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(longueur) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self.json({"erreur": "Requête illisible"}, 400)
        with VERROU:
            conn = db.ouvrir(CHEMIN_DB)
            try:
                st = db.charger(conn)
                resultat = fonction(st, payload, contexte())
                db.sauver(conn, st)  # sauvegarde seulement si l'action a réussi
            except actions.ErreurAction as e:
                conn.close()
                return self.json({"erreur": str(e)}, 400)
            except sqlite3.Error as e:
                conn.close()
                return self.json({"erreur": "Base de données : " + str(e)}, 500)
            conn.close()
        resultat["etat"] = st
        return self.json(resultat)


def main():
    ap = argparse.ArgumentParser(description="Démo de la plateforme commerciale")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--reset", action="store_true", help="repartir des données de démonstration")
    ap.add_argument("--sans-navigateur", action="store_true", help="ne pas ouvrir le navigateur")
    args = ap.parse_args()

    preparer_base(args.reset)
    serveur = ThreadingHTTPServer(("127.0.0.1", args.port), Gestionnaire)
    url = f"http://localhost:{args.port}"
    print(f"\n  Plateforme commerciale (démo) : {url}")
    print(f"  Base de données : {CHEMIN_DB}")
    print("  Ctrl+C pour arrêter.\n")
    if not args.sans_navigateur:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        print("\n  Serveur arrêté.")


if __name__ == "__main__":
    main()
