"""Moteur de la plateforme : règles d'opportunités, calculette, affectation.

Ce fichier a un jumeau en JavaScript (objet `Moteur` dans frontend/app.js).
Les deux doivent rester identiques : la même entrée donne le même résultat,
que la démo tourne dans le navigateur seul ou avec le serveur Python.
Dans Power Apps, cette logique deviendra des formules (calculette) et des
flux Power Automate (règles, affectation).
"""

import math
import unicodedata

ETAPES = ["A", "B", "C", "D"]
NOMS_ETAPES = {
    "A": "Audit et diagnostic",
    "B": "Plan pluriannuel d'investissement",
    "C": "Conception et réalisation",
    "D": "Exploitation et amélioration continue",
}


# ---------- utilitaires ----------

def num(x):
    """Convertit une saisie en nombre ('8,3' -> 8.3). Vide ou invalide -> None."""
    if x is None or x == "" or isinstance(x, bool):
        return None
    try:
        n = float(str(x).replace(",", "."))
    except ValueError:
        return None
    return n if math.isfinite(n) else None


def arrondi(x):
    """Arrondi au centime, identique à Math.floor(x * 100 + 0.5) / 100 en JS."""
    return math.floor(x * 100 + 0.5) / 100


def norm(s):
    """Minuscules sans accents, pour comparer des mots-clés."""
    s = unicodedata.normalize("NFD", str(s or ""))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


def fmt_euros(x):
    """1234567.8 -> '1 234 568 €' (espaces insécables), comme en JS."""
    n = int(math.floor(x + 0.5))
    return f"{n:,}".replace(",", " ") + " €"


def fmt_nombre(x):
    if x == int(x):
        return str(int(x))
    return str(round(x, 4))


# ---------- règles d'opportunités ----------

def valeurs_derivees(v):
    o = dict(v or {})
    e, g = num(o.get("consoElec")), num(o.get("consoGaz"))
    o["consoTotale"] = None if e is None and g is None else arrondi((e or 0) + (g or 0))
    return o


def tester_condition(c, v, parc, aujourdhui):
    x = v.get(c["champ"])
    op, val = c["op"], c["valeur"]
    if op in (">=", ">", "entre"):
        n = num(x)
        if n is None:
            return False
        if op == ">=":
            return n >= val
        if op == ">":
            return n > val
        return val[0] < n <= val[1]
    if op == "vrai":
        return x is True or x == "oui"
    if op == "contient":
        return norm(val) in norm(x)
    if op == "plusAncienQue":
        if not x:
            return True
        limite = str(int(aujourdhui[:4]) - val) + aujourdhui[4:]
        return str(x) < limite
    if op == "possede":
        return all(t in parc for t in val)
    if op == "nePossedePas":
        return all(t not in parc for t in val)
    return False


def evaluer(regles, valeurs, parc, aujourdhui, declencheur):
    """Renvoie les règles actives dont toutes les conditions sont vraies."""
    v = valeurs_derivees(valeurs)
    return [
        r for r in regles
        if r["actif"] and r["declencheur"] == declencheur
        and all(tester_condition(c, v, parc, aujourdhui) for c in r["conditions"])
    ]


# ---------- calculette ----------

def montant_aide(aide, saisie, prix_mwh_cumac):
    if aide["type"] == "cee":
        kwhc = aide["coefKwhc"] * (num(saisie.get("qte")) or 0)
        return {"kwhc": arrondi(kwhc), "montant": arrondi(kwhc / 1000 * prix_mwh_cumac)}
    return {"kwhc": 0, "montant": arrondi(num(saisie.get("montant")) or 0)}


def calculer(chiffrage, produits, aides, params):
    """Coût -> marge -> aides -> reste à charge.

    Marge avant aides : PV = C x (1 + m)          RAC = max(0, PV - somme des aides)
    Marge après aides : RAC = max(0, C - aides) x (1 + m)
    """
    prix = {p["id"]: p["prixAchat"] for p in produits}
    materiel = 0
    for l in chiffrage.get("lignes", []):
        materiel += prix.get(l.get("produitId"), 0) * (num(l.get("qte")) or 0)
    mo = num(chiffrage.get("mainOeuvre")) or 0
    cout = arrondi(materiel + mo)
    m = num(chiffrage.get("marge"))
    m = (params["margeDefaut"] if m is None else m) / 100

    detail, total_aides = [], 0
    for s in chiffrage.get("aides", []):
        a = next((x for x in aides if x["id"] == s.get("aideId")), None)
        if a is None:
            continue
        r = montant_aide(a, s, params["prixMWhCumac"])
        detail.append({"aideId": a["id"], "nom": a["nom"], "kwhc": r["kwhc"], "montant": r["montant"]})
        total_aides += r["montant"]
    total_aides = arrondi(total_aides)

    if chiffrage.get("base") == "apres":
        b = max(0, cout - total_aides)
        rac = arrondi(b * (1 + m))
        pv = arrondi(rac + total_aides)
        marge = arrondi(rac - b)
    else:
        pv = arrondi(cout * (1 + m))
        rac = arrondi(max(0, pv - total_aides))
        marge = arrondi(pv - cout)

    alertes = []
    if total_aides > cout and cout > 0:
        alertes.append({"niveau": "critique", "message": "Les aides dépassent le coût du projet : à corriger avant envoi."})
    if rac == 0 and total_aides > 0:
        alertes.append({"niveau": "attention", "message": "Reste à charge nul : validation de la cellule 3E obligatoire."})

    return {
        "materiel": arrondi(materiel), "mainOeuvre": arrondi(mo), "cout": cout,
        "pv": pv, "totalAides": total_aides, "rac": rac, "marge": marge,
        "detailAides": detail, "alertes": alertes,
    }


# ---------- affectation ----------

def interlocuteurs(etape, offre, annuaire):
    """Services à prévenir quand une affaire arrive à une étape."""
    return [
        {"serviceId": s["id"], "service": s["service"], "nom": s["nom"]}
        for s in annuaire
        if etape in s["etapes"] and (not s["offres"] or offre in s["offres"])
    ]
