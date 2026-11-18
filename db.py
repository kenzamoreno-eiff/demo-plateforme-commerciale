"""Base de données SQLite : une table par liste SharePoint du cahier des charges.

Les colonnes reprennent le modèle de données (volet 2). Les champs composés
(réponses du pré-diagnostic, chiffrage, historique…) sont stockés en JSON,
comme le ferait une colonne « texte multiligne » dans SharePoint.
Le fichier plateforme.db peut s'ouvrir avec « DB Browser for SQLite ».
"""

import json
import re
import sqlite3
from pathlib import Path

# type : TEXT, REAL, INTEGER, BOOL (0/1), JSON (texte JSON)
SCHEMA = {
    "annuaire": [("id", "TEXT"), ("service", "TEXT"), ("role", "TEXT"), ("nom", "TEXT"), ("email", "TEXT"),
                 ("etapes", "JSON"), ("offres", "JSON")],
    "clients": [("id", "TEXT"), ("nom", "TEXT"), ("site", "TEXT"), ("adresse", "TEXT"), ("lat", "REAL"),
                ("lon", "REAL"), ("secteur", "TEXT"), ("statut", "TEXT"), ("agence", "TEXT")],
    "contacts": [("id", "TEXT"), ("clientId", "TEXT"), ("nom", "TEXT"), ("fonction", "TEXT"), ("email", "TEXT"),
                 ("telephone", "TEXT"), ("referentEnergie", "BOOL")],
    "installations": [("id", "TEXT"), ("clientId", "TEXT"), ("type", "TEXT"), ("puissance", "REAL"),
                      ("unite", "TEXT"), ("annee", "INTEGER"), ("marque", "TEXT"), ("note", "TEXT")],
    "produits": [("id", "TEXT"), ("categorie", "TEXT"), ("marque", "TEXT"), ("reference", "TEXT"),
                 ("designation", "TEXT"), ("protocole", "TEXT"), ("prixAchat", "REAL")],
    "aides": [("id", "TEXT"), ("nom", "TEXT"), ("type", "TEXT"), ("coefKwhc", "REAL"), ("uniteQte", "TEXT"),
              ("note", "TEXT")],
    "regles": [("id", "TEXT"), ("titre", "TEXT"), ("offre", "TEXT"), ("priorite", "TEXT"), ("echeance", "TEXT"),
               ("declencheur", "TEXT"), ("actif", "BOOL"), ("conditions", "JSON")],
    "prediagnostics": [("id", "TEXT"), ("ref", "TEXT"), ("clientId", "TEXT"), ("date", "TEXT"),
                       ("auditeur", "TEXT"), ("energyExpert", "TEXT"), ("valeurs", "JSON")],
    "opportunites": [("id", "TEXT"), ("clientId", "TEXT"), ("prediagId", "TEXT"), ("regleId", "TEXT"),
                     ("titre", "TEXT"), ("offre", "TEXT"), ("priorite", "TEXT"), ("echeance", "TEXT"),
                     ("statut", "TEXT"), ("origine", "TEXT"), ("date", "TEXT")],
    "affaires": [("id", "TEXT"), ("clientId", "TEXT"), ("oppId", "TEXT"), ("titre", "TEXT"), ("offre", "TEXT"),
                 ("etape", "TEXT"), ("avancement", "INTEGER"), ("reserve", "TEXT"), ("chiffrage", "JSON"),
                 ("resultat", "JSON"), ("interlocuteurs", "JSON"), ("historique", "JSON")],
    "journal": [("id", "TEXT"), ("date", "TEXT"), ("flux", "TEXT"), ("message", "TEXT"), ("niveau", "TEXT")],
}
SQL_TYPE = {"TEXT": "TEXT", "REAL": "REAL", "INTEGER": "INTEGER", "BOOL": "INTEGER", "JSON": "TEXT"}


def lire_seed(chemin_seed_js):
    """Lit frontend/seed.js (window.SEED = {...};) : une seule source pour JS et Python."""
    texte = Path(chemin_seed_js).read_text(encoding="utf-8")
    m = re.search(r"window\.SEED\s*=\s*(\{.*\})\s*;?\s*$", texte, re.S)
    if not m:
        raise RuntimeError("seed.js illisible")
    return json.loads(m.group(1))


def ouvrir(chemin):
    conn = sqlite3.connect(chemin)
    for table, cols in SCHEMA.items():
        defs = ", ".join(f'"{c}" {SQL_TYPE[t]}' for c, t in cols)
        conn.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({defs}, PRIMARY KEY ("id"))')
    conn.execute('CREATE TABLE IF NOT EXISTS "parametres" ("cle" TEXT PRIMARY KEY, "valeur" TEXT)')
    conn.commit()
    return conn


def est_vide(conn):
    return conn.execute('SELECT COUNT(*) FROM "parametres"').fetchone()[0] == 0


def _ecrire(v, t):
    if v is None:
        return None
    if t == "JSON":
        return json.dumps(v, ensure_ascii=False)
    if t == "BOOL":
        return 1 if v else 0
    return v


def _lire(v, t):
    if v is None:
        return None
    if t == "JSON":
        return json.loads(v)
    if t == "BOOL":
        return bool(v)
    return v


def sauver(conn, st):
    """Réécrit toutes les listes (suffisant pour une démo de quelques centaines de lignes)."""
    with conn:
        for table, cols in SCHEMA.items():
            conn.execute(f'DELETE FROM "{table}"')
            noms = ", ".join(f'"{c}"' for c, _ in cols)
            trous = ", ".join("?" for _ in cols)
            conn.executemany(f'INSERT INTO "{table}" ({noms}) VALUES ({trous})',
                             [tuple(_ecrire(it.get(c), t) for c, t in cols) for it in st[table]])
        conn.execute('DELETE FROM "parametres"')
        conn.executemany('INSERT INTO "parametres" VALUES (?, ?)',
                         [(k, json.dumps(v)) for k, v in st["parametres"].items()]
                         + [("version", json.dumps(st.get("version")))])


def charger(conn):
    st = {}
    for table, cols in SCHEMA.items():
        noms = ", ".join(f'"{c}"' for c, _ in cols)
        st[table] = [{c: _lire(v, t) for (c, t), v in zip(cols, ligne)}
                     for ligne in conn.execute(f'SELECT {noms} FROM "{table}" ORDER BY rowid')]
    params = {k: json.loads(v) for k, v in conn.execute('SELECT cle, valeur FROM "parametres"')}
    st["version"] = params.pop("version", None)
    st["parametres"] = params
    return st


def exporter_csv(conn, table):
    """Export d'une liste au format CSV lisible par Excel (séparateur ;)."""
    import csv
    import io
    if table not in SCHEMA:
        raise KeyError(table)
    cols = SCHEMA[table]
    out = io.StringIO()
    w = csv.writer(out, delimiter=";")
    w.writerow([c for c, _ in cols])
    noms = ", ".join(f'"{c}"' for c, _ in cols)
    for ligne in conn.execute(f'SELECT {noms} FROM "{table}" ORDER BY rowid'):
        w.writerow(["" if v is None else v for v in ligne])
    return "﻿" + out.getvalue()
