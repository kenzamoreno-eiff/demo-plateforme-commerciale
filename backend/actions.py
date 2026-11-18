"""Actions de la plateforme (jumelles de l'objet `Actions` dans frontend/app.js).

Chaque action reçoit l'état complet (dict), les paramètres envoyés par
l'interface et un contexte (date du jour, heure, données de départ).
Elle modifie l'état et renvoie un petit résultat pour l'interface.
Les messages du journal simulent les flux Power Automate du volet 10.
"""

import copy
import csv
import io
import math

import moteur

LISTES = ["parametres", "annuaire", "clients", "contacts", "installations", "produits",
          "aides", "regles", "prediagnostics", "opportunites", "affaires", "journal"]


class ErreurAction(ValueError):
    pass


# ---------- utilitaires ----------

def next_id(liste, prefixe, largeur):
    maxi = 0
    for it in liste:
        if it["id"].startswith(prefixe):
            try:
                maxi = max(maxi, int(it["id"][len(prefixe):]))
            except ValueError:
                pass
    return prefixe + str(maxi + 1).zfill(largeur)


def trouver(liste, ident, quoi):
    for it in liste:
        if it["id"] == ident:
            return it
    raise ErreurAction(f"{quoi} introuvable : {ident}")


def journaliser(st, ctx, flux, message, niveau="auto"):
    st["journal"].append({"id": next_id(st["journal"], "J-", 4), "date": ctx["maintenant"],
                          "flux": flux, "message": message, "niveau": niveau})


def parc_client(st, client_id):
    vus = []
    for i in st["installations"]:
        if i["clientId"] == client_id and i["type"] not in vus:
            vus.append(i["type"])
    return vus


def recalculer(st, a):
    a["resultat"] = moteur.calculer(a["chiffrage"], st["produits"], st["aides"], st["parametres"])


def creer_opps(st, ctx, client_id, prediag_id, regles):
    crees = []
    for r in regles:
        deja = any(o["clientId"] == client_id and o["regleId"] == r["id"] and o["statut"] != "Écartée"
                   for o in st["opportunites"])
        if deja:
            continue
        o = {"id": next_id(st["opportunites"], "OPP-", 4), "clientId": client_id, "prediagId": prediag_id,
             "regleId": r["id"], "titre": r["titre"], "offre": r["offre"], "priorite": r["priorite"],
             "echeance": r["echeance"], "statut": "Nouvelle", "origine": "Règle " + r["id"],
             "date": ctx["aujourdhui"]}
        st["opportunites"].append(o)
        crees.append(o["id"])
    return crees


def etat_initial(seed):
    st = {k: copy.deepcopy(seed[k]) for k in LISTES}
    st["version"] = seed["version"]
    for a in st["affaires"]:
        recalculer(st, a)
        a["interlocuteurs"] = moteur.interlocuteurs(a["etape"], a["offre"], st["annuaire"])
    return st


def lire_csv(texte):
    texte = texte.lstrip("﻿")
    premiere = texte.splitlines()[0] if texte else ""
    sep = ";" if premiere.count(";") >= premiere.count(",") else ","
    return [l for l in csv.reader(io.StringIO(texte), delimiter=sep) if any(x.strip() for x in l)]


# ---------- actions ----------

def enregistrer_prediag(st, p, ctx):
    c = trouver(st["clients"], p.get("clientId"), "Client")
    ident = next_id(st["prediagnostics"], "PD-", 4)
    ref = p.get("ref") or ident
    valeurs = p.get("valeurs") or {}
    st["prediagnostics"].append({"id": ident, "ref": ref, "clientId": c["id"],
                                 "date": p.get("date") or ctx["aujourdhui"],
                                 "auditeur": p.get("auditeur") or "", "energyExpert": p.get("energyExpert") or "",
                                 "valeurs": valeurs})
    regles = moteur.evaluer(st["regles"], valeurs, parc_client(st, c["id"]), ctx["aujourdhui"], "prediag")
    crees = creer_opps(st, ctx, c["id"], ident, regles)
    journaliser(st, ctx, "Règles d'opportunités",
                f"{c['nom']} : pré-diagnostic {ref} analysé, {len(crees)} opportunité(s) créée(s).")
    if crees:
        journaliser(st, ctx, "Notifications",
                    f"Energy Expert prévenu : {len(crees)} opportunité(s) à valider pour {c['nom']}.")
    return {"prediagId": ident, "crees": crees, "reglesDeclenchees": [r["id"] for r in regles]}


def ajouter_installation(st, p, ctx):
    c = trouver(st["clients"], p.get("clientId"), "Client")
    if not p.get("type"):
        raise ErreurAction("Choisissez le type d'installation.")
    ident = next_id(st["installations"], "INS-", 4)
    annee = moteur.num(p.get("annee"))
    st["installations"].append({"id": ident, "clientId": c["id"], "type": p["type"],
                                "puissance": moteur.num(p.get("puissance")), "unite": p.get("unite") or "",
                                "annee": None if annee is None else int(annee),
                                "marque": p.get("marque") or "", "note": p.get("note") or ""})
    regles = moteur.evaluer(st["regles"], {}, parc_client(st, c["id"]), ctx["aujourdhui"], "parc")
    crees = creer_opps(st, ctx, c["id"], None, regles)
    if crees:
        journaliser(st, ctx, "Ventes complémentaires",
                    f"{c['nom']} : {p['type']} ajouté au parc, {len(crees)} opportunité(s) de vente complémentaire.")
    return {"installationId": ident, "crees": crees}


def statut_opportunite(st, p, ctx):
    o = trouver(st["opportunites"], p.get("id"), "Opportunité")
    if p.get("statut") not in ("Nouvelle", "Validée", "Écartée"):
        raise ErreurAction("Statut non autorisé.")
    o["statut"] = p["statut"]
    if p["statut"] == "Validée":
        c = trouver(st["clients"], o["clientId"], "Client")
        journaliser(st, ctx, "Notifications",
                    f"Responsable d'affaires prévenu : « {o['titre']} » validée pour {c['nom']}.")
    return {}


def creer_affaire(st, p, ctx):
    o = None
    client_id, titre, offre = p.get("clientId"), p.get("titre"), p.get("offre")
    if p.get("oppId"):
        o = trouver(st["opportunites"], p["oppId"], "Opportunité")
        client_id, titre, offre = o["clientId"], o["titre"], o["offre"]
    c = trouver(st["clients"], client_id, "Client")
    ident = next_id(st["affaires"], f"AFF-{ctx['aujourdhui'][:4]}-", 3)
    a = {"id": ident, "clientId": c["id"], "oppId": o["id"] if o else None, "titre": titre, "offre": offre,
         "etape": "A", "avancement": 0, "reserve": "",
         "chiffrage": {"lignes": [], "mainOeuvre": 0, "marge": st["parametres"]["margeDefaut"],
                       "base": "avant", "aides": []},
         "resultat": None, "interlocuteurs": moteur.interlocuteurs("A", offre, st["annuaire"]),
         "historique": [{"date": ctx["maintenant"], "texte": "Affaire créée" + (" depuis " + o["id"] if o else "")}]}
    recalculer(st, a)
    st["affaires"].append(a)
    if o:
        o["statut"] = "En affaire"
    noms = ", ".join(i["service"] for i in a["interlocuteurs"])
    journaliser(st, ctx, "Affectation et notifications", f"{ident} créée pour {c['nom']} : {noms} prévenu(s).")
    return {"affaireId": ident}


def maj_chiffrage(st, p, ctx):
    a = trouver(st["affaires"], p.get("id"), "Affaire")
    a["chiffrage"] = p.get("chiffrage") or a["chiffrage"]
    recalculer(st, a)
    a["historique"].append({"date": ctx["maintenant"],
                            "texte": "Chiffrage enregistré : reste à charge " + moteur.fmt_euros(a["resultat"]["rac"])})
    if a["resultat"]["rac"] == 0 and a["resultat"]["totalAides"] > 0:
        journaliser(st, ctx, "Alerte reste à charge nul",
                    f"{a['id']} : reste à charge nul, cellule 3E prévenue pour validation.", "alerte")
    return {}


def maj_chantier(st, p, ctx):
    a = trouver(st["affaires"], p.get("id"), "Affaire")
    a["avancement"] = max(0, min(100, int(math.floor((moteur.num(p.get("avancement")) or 0) + 0.5))))
    a["reserve"] = p.get("reserve") or ""
    a["historique"].append({"date": ctx["maintenant"], "texte": f"Avancement chantier : {a['avancement']} %"})
    if a["reserve"]:
        journaliser(st, ctx, "Notifications",
                    f"{a['id']} : réserve signalée par le conducteur de travaux, responsable d'affaires prévenu.")
    return {}


def changer_etape(st, p, ctx):
    a = trouver(st["affaires"], p.get("id"), "Affaire")
    if p.get("etape") not in moteur.ETAPES:
        raise ErreurAction("Étape inconnue.")
    avant = a["etape"]
    a["etape"] = p["etape"]
    a["interlocuteurs"] = moteur.interlocuteurs(p["etape"], a["offre"], st["annuaire"])
    if p["etape"] == "D" and avant == "C":
        a["avancement"] = 100
    a["historique"].append({"date": ctx["maintenant"], "texte": f"Étape {avant} → {p['etape']}"})
    noms = ", ".join(i["service"] for i in a["interlocuteurs"]) or "aucun service"
    journaliser(st, ctx, "Affectation et notifications",
                f"{a['id']} passe en étape {p['etape']} : {noms} prévenu(s).")
    return {}


def maj_parametres(st, p, ctx):
    for k in ("margeDefaut", "prixMWhCumac"):
        if k in p:
            v = moteur.num(p[k])
            if v is None or v < 0:
                raise ErreurAction("Valeur invalide : " + k)
            st["parametres"][k] = v
    pa = st["parametres"]
    journaliser(st, ctx, "Paramètres",
                f"Marge par défaut {moteur.fmt_nombre(pa['margeDefaut'])} %, "
                f"prix du MWh cumac {moteur.fmt_nombre(pa['prixMWhCumac'])} €.", "info")
    return {}


def maj_regle(st, p, ctx):
    r = trouver(st["regles"], p.get("id"), "Règle")
    if "actif" in p:
        r["actif"] = bool(p["actif"])
    if "seuil" in p:
        c = next((c for c in r["conditions"] if isinstance(c["valeur"], (int, float))
                  and not isinstance(c["valeur"], bool)), None)
        v = moteur.num(p["seuil"])
        if c is None or v is None:
            raise ErreurAction("Seuil non modifiable pour cette règle.")
        c["valeur"] = v
    journaliser(st, ctx, "Paramètres", f"Règle {r['id']} mise à jour.", "info")
    return {}


def importer_clients(st, p, ctx):
    lignes = lire_csv(p.get("csv") or "")
    if len(lignes) < 2:
        raise ErreurAction("Fichier vide ou sans ligne d'en-tête.")
    entete = [moteur.norm(h).strip() for h in lignes[0]]

    def col(noms):
        return next((i for i, h in enumerate(entete) if h in noms), -1)

    idx = {"nom": col(["nom", "raison sociale", "client"]), "site": col(["site", "ville"]),
           "adresse": col(["adresse"]), "lat": col(["lat", "latitude"]), "lon": col(["lon", "lng", "longitude"]),
           "secteur": col(["secteur"]), "statut": col(["statut"]), "agence": col(["agence"])}
    if idx["nom"] < 0:
        raise ErreurAction("Colonne « nom » introuvable dans l'en-tête.")
    n = 0
    for l in lignes[1:]:
        def g(k):
            i = idx[k]
            return (l[i] if 0 <= i < len(l) else "").strip()
        if not g("nom"):
            continue
        st["clients"].append({"id": next_id(st["clients"], "CLI-", 4), "nom": g("nom"), "site": g("site"),
                              "adresse": g("adresse"), "lat": moteur.num(g("lat")), "lon": moteur.num(g("lon")),
                              "secteur": g("secteur"),
                              "statut": "Client" if moteur.norm(g("statut")).startswith("client") else "Prospect",
                              "agence": g("agence")})
        n += 1
    journaliser(st, ctx, "Import", f"{n} client(s) importé(s) depuis le fichier Excel (CSV).", "info")
    return {"importes": n}


def reinitialiser(st, p, ctx):
    neuf = etat_initial(ctx["seed"])
    st.clear()
    st.update(neuf)
    return {}


ACTIONS = {
    "enregistrerPrediag": enregistrer_prediag,
    "ajouterInstallation": ajouter_installation,
    "statutOpportunite": statut_opportunite,
    "creerAffaire": creer_affaire,
    "majChiffrage": maj_chiffrage,
    "majChantier": maj_chantier,
    "changerEtape": changer_etape,
    "majParametres": maj_parametres,
    "majRegle": maj_regle,
    "importerClients": importer_clients,
    "reinitialiser": reinitialiser,
}
