# Démo — Plateforme commerciale Performance énergétique

Prototype HTML / CSS / JavaScript + Python de la plateforme décrite dans le cahier des charges,
à montrer avant de la construire dans Power Apps.

## Deux façons de lancer la démo

### 1. Sans rien installer (poste Eiffage)
Ouvrir `dist/demo_autonome.html` par double-clic. Tout tourne dans le navigateur ;
les données restent dans ce navigateur (bouton « Réinitialiser la démo » dans Paramètres).

### 2. Avec Python (poste personnel)
Python 3.9 ou plus, aucune bibliothèque à installer.

```
python backend/server.py            # ouvre http://localhost:8000
python backend/server.py --reset    # repart des données de démonstration
python backend/tests.py             # tests du moteur
python tools/build_standalone.py    # régénère dist/demo_autonome.html
```

Le badge en haut à droite indique le mode : « Python connecté · SQLite » ou « Mode autonome ».
En mode Python, les données sont dans `data/plateforme.db` (à ouvrir avec DB Browser for SQLite)
et Paramètres propose l'export CSV de chaque liste.

## Scénario de démonstration (5 minutes)

1. **Pré-diagnostics** → « Charger l'exemple Endress Hauser » : l'aperçu montre les 5 règles qui vont se déclencher.
   → « Enregistrer et analyser » : 5 opportunités créées, notifications Power Automate simulées.
2. **Profil Energy Expert** → Accueil : valider une opportunité.
3. **Profil Responsable d'affaires** → Opportunités → « Chiffrer » : l'affaire s'ouvre avec la calculette.
   Ajouter du matériel, changer de marque (équivalence), cocher une prime CEE, basculer marge avant / après aides.
   → « Enregistrer dans l'affaire », puis « Passer à l'étape B » : les services de l'étape sont prévenus.
4. **Clients** → Exemple : agroalimentaire → Installations → ajouter « Batteries » :
   la règle R11 crée une opportunité de vente complémentaire EMS / Smart Grid.
5. **Profils Conducteur de travaux, Cellule 3E, Direction** : chaque accueil est différent.
6. **Automatisations** : le journal de tous les flux déclenchés.

## Organisation du code

| Fichier | Rôle | Devient dans Power Apps |
| --- | --- | --- |
| `frontend/index.html`, `styles.css` | Écrans, charte bleu / blanc / rouge / vert | Écrans de l'application canevas, App.Formulas |
| `frontend/app.js` | Interface + moteur JS (mode autonome) | Formules Power Fx |
| `frontend/seed.js` | Données de démonstration, partagées JS / Python | Contenu initial des listes SharePoint |
| `backend/moteur.py` | Règles d'opportunités, calculette, affectation | Formules + flux Power Automate |
| `backend/actions.py` | Actions (enregistrer, valider, chiffrer…) et journal | Flux Power Automate |
| `backend/db.py` | Une table SQLite par liste SharePoint | Listes SharePoint |
| `backend/server.py` | Serveur web + API JSON | — |

`backend/moteur.py` et l'objet `Moteur` de `frontend/app.js` sont jumeaux : un test de parité
a vérifié qu'ils donnent exactement le même résultat. Toute modification doit être faite dans les deux.

## Ce qui est fictif

Prix d'achat du catalogue, coefficients CEE (kWh cumac), prix du MWh cumac, clients « Exemple »
et noms de l'annuaire. À remplacer par les vraies valeurs (achats, cellule 3E, base Excel)
avant toute présentation chiffrée. Modèle d'import : `modele_import_clients.csv`.
