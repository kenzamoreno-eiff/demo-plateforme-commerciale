window.SEED = {
  "version": "demo-1",
  "parametres": {
    "margeDefaut": 20,
    "prixMWhCumac": 8.5,
    "partUptimumDR": 6.6,
    "partUptimumMoyenne": 13
  },
  "questions": [
    { "id": "consoElec", "label": "Consommation d'électricité", "unite": "GWh/an", "type": "nombre", "groupe": "Consommations" },
    { "id": "consoGaz", "label": "Consommation de gaz", "unite": "GWh/an", "type": "nombre", "groupe": "Consommations" },
    { "id": "auditDate", "label": "Date du dernier audit énergétique", "type": "date", "groupe": "Consommations" },
    { "id": "puissanceCVC", "label": "Puissance CVC cumulée (chauffage + climatisation)", "unite": "kW", "type": "nombre", "groupe": "Bâtiment et équipements" },
    { "id": "gtbExistante", "label": "GTB existante", "type": "texte", "groupe": "Bâtiment et équipements" },
    { "id": "surfaceTotale", "label": "Surface totale du site", "unite": "m²", "type": "nombre", "groupe": "Bâtiment et équipements" },
    { "id": "surfaceTertiaire", "label": "Surfaces tertiaires (bureaux…)", "unite": "m²", "type": "nombre", "groupe": "Bâtiment et équipements" },
    { "id": "surfaceParking", "label": "Surface du parking extérieur", "unite": "m²", "type": "nombre", "groupe": "Bâtiment et équipements" },
    { "id": "bornesIRVE", "label": "Nombre de bornes IRVE", "unite": "bornes", "type": "nombre", "groupe": "Bâtiment et équipements" },
    { "id": "comptagePartiel", "label": "Plan de comptage partiel ou incomplet", "type": "ouinon", "groupe": "Bâtiment et équipements" },
    { "id": "actions", "label": "Actions envisagées ou besoins exprimés", "type": "texte-long", "groupe": "Besoins du client" }
  ],
  "exemplePrediag": {
    "clientId": "CLI-0001",
    "ref": "PE-000278",
    "date": "2026-10-07",
    "auditeur": "Auditeur Eiffage",
    "energyExpert": "Energy Expert de référence",
    "valeurs": {
      "consoElec": "8.3",
      "consoGaz": "3.5",
      "auditDate": "2025-06-01",
      "puissanceCVC": "300",
      "gtbExistante": "Niagara + Siemens, problème d'accès",
      "surfaceTotale": "35000",
      "surfaceTertiaire": "2000",
      "surfaceParking": "",
      "bornesIRVE": "50",
      "comptagePartiel": "non",
      "actions": "Recherche de fuites d'air comprimé à budgéter ; étude aéraulique de la cabine de peinture ; chiffrage Décret tertiaire demandé. Comptage LoRa en cours côté client."
    }
  },
  "regles": [
    { "id": "R01", "titre": "Audit énergétique réglementaire", "offre": "Conseil", "priorite": "Haute", "echeance": "Tous les 4 ans (loi DDADUE)", "declencheur": "prediag", "actif": true,
      "conditions": [ { "champ": "consoTotale", "op": ">=", "valeur": 2.75 }, { "champ": "auditDate", "op": "plusAncienQue", "valeur": 4 } ] },
    { "id": "R02", "titre": "SMÉ certifié ISO 50001", "offre": "Conseil", "priorite": "Haute", "echeance": "11 octobre 2027", "declencheur": "prediag", "actif": true,
      "conditions": [ { "champ": "consoTotale", "op": ">=", "valeur": 23.6 } ] },
    { "id": "R03", "titre": "Conformité GTB / BACS", "offre": "EMS", "priorite": "Haute", "echeance": "Depuis le 1er janvier 2025", "declencheur": "prediag", "actif": true,
      "conditions": [ { "champ": "puissanceCVC", "op": ">", "valeur": 290 } ] },
    { "id": "R04", "titre": "Conformité GTB / BACS (70 à 290 kW)", "offre": "EMS", "priorite": "Moyenne", "echeance": "2027 ou 2030, à confirmer", "declencheur": "prediag", "actif": true,
      "conditions": [ { "champ": "puissanceCVC", "op": "entre", "valeur": [70, 290] } ] },
    { "id": "R05", "titre": "Accompagnement Décret tertiaire", "offre": "Conseil", "priorite": "Moyenne", "echeance": "-40 % en 2030", "declencheur": "prediag", "actif": true,
      "conditions": [ { "champ": "surfaceTertiaire", "op": ">=", "valeur": 1000 } ] },
    { "id": "R06", "titre": "Ombrières photovoltaïques (loi APER)", "offre": "Smart Grid", "priorite": "Moyenne", "echeance": "2028 à 2030 selon la surface", "declencheur": "prediag", "actif": true,
      "conditions": [ { "champ": "surfaceParking", "op": ">", "valeur": 1500 } ] },
    { "id": "R07", "titre": "Smart charging et pilotage des bornes", "offre": "IRVE", "priorite": "Moyenne", "echeance": "—", "declencheur": "prediag", "actif": true,
      "conditions": [ { "champ": "bornesIRVE", "op": ">", "valeur": 0 } ] },
    { "id": "R08", "titre": "Complément du plan de comptage", "offre": "EMS", "priorite": "Basse", "echeance": "—", "declencheur": "prediag", "actif": true,
      "conditions": [ { "champ": "comptagePartiel", "op": "vrai", "valeur": true } ] },
    { "id": "R09", "titre": "Air comprimé : recherche de fuites + CEE", "offre": "CEE + travaux", "priorite": "Moyenne", "echeance": "—", "declencheur": "prediag", "actif": true,
      "conditions": [ { "champ": "actions", "op": "contient", "valeur": "air comprimé" } ] },
    { "id": "R10", "titre": "Étude aéraulique (BE automatisme)", "offre": "Études", "priorite": "Basse", "echeance": "—", "declencheur": "prediag", "actif": true,
      "conditions": [ { "champ": "actions", "op": "contient", "valeur": "peinture" } ] },
    { "id": "R11", "titre": "EMS / Smart Grid (vente complémentaire)", "offre": "Smart Grid", "priorite": "Haute", "echeance": "—", "declencheur": "parc", "actif": true,
      "conditions": [ { "champ": "parc", "op": "possede", "valeur": ["PV", "Batteries"] }, { "champ": "parc", "op": "nePossedePas", "valeur": ["EMS"] } ] }
  ],
  "annuaire": [
    { "id": "S01", "service": "Responsable d'affaires", "role": "Porte l'affaire : fiche client, chiffrage, offre", "nom": "À compléter", "email": "", "etapes": ["A", "B", "C", "D"], "offres": [] },
    { "id": "S02", "service": "Energy Expert", "role": "Valide le pré-diagnostic, les opportunités et les fiches CEE", "nom": "À compléter", "email": "", "etapes": ["A", "B", "D"], "offres": [] },
    { "id": "S03", "service": "Bureau d'études automatisme", "role": "Études EMS, GTB, smart grid", "nom": "À compléter", "email": "", "etapes": ["B", "C"], "offres": ["EMS", "Smart Grid", "Études"] },
    { "id": "S04", "service": "Service achats", "role": "Prix du catalogue, commandes", "nom": "À compléter", "email": "", "etapes": ["B", "C"], "offres": [] },
    { "id": "S05", "service": "DR Colmar", "role": "Partie PV et batteries", "nom": "À compléter", "email": "", "etapes": ["B", "C"], "offres": ["Batteries", "Smart Grid"] },
    { "id": "S06", "service": "Conducteur de travaux", "role": "Réalisation sur site, avancement, réception", "nom": "À compléter", "email": "", "etapes": ["C"], "offres": [] },
    { "id": "S07", "service": "Cellule 3E", "role": "CEE, aides, prix du MWh cumac, validation des restes à charge nuls", "nom": "À compléter", "email": "", "etapes": ["A", "B", "D"], "offres": [] },
    { "id": "S08", "service": "Direction de la DR", "role": "Suivi du pipeline sur le tableau de bord", "nom": "À compléter", "email": "", "etapes": [], "offres": [] }
  ],
  "produits": [
    { "id": "P01", "categorie": "Compteur d'énergie triphasé", "marque": "Lettel", "reference": "MCT4-35", "designation": "Compteur multi-mesures triphasé sur TC 1/5 A", "protocole": "Modbus", "prixAchat": 180 },
    { "id": "P02", "categorie": "Compteur d'énergie triphasé", "marque": "Schneider Electric", "reference": "iEM3255", "designation": "Compteur triphasé sur TC", "protocole": "Modbus", "prixAchat": 260 },
    { "id": "P03", "categorie": "Compteur d'énergie triphasé", "marque": "Ewattch", "reference": "Réf. à confirmer", "designation": "Compteur communicant", "protocole": "Radio, à confirmer", "prixAchat": 210 },
    { "id": "P04", "categorie": "Mesure multi-départs", "marque": "Lettel", "reference": "Enerclip", "designation": "Mesure électrique multi-départs", "protocole": "Modbus", "prixAchat": 950 },
    { "id": "P05", "categorie": "Superviseur / passerelle", "marque": "Schneider Electric", "reference": "Com'X 510", "designation": "Serveur d'énergie", "protocole": "Modbus / Ethernet", "prixAchat": 1900 },
    { "id": "P06", "categorie": "Superviseur / passerelle", "marque": "Ewattch", "reference": "Réf. à confirmer", "designation": "Box de supervision", "protocole": "IP", "prixAchat": 1500 },
    { "id": "P07", "categorie": "Automate", "marque": "Wago", "reference": "PFC200", "designation": "Contrôleur programmable", "protocole": "Modbus / Ethernet", "prixAchat": 1200 },
    { "id": "P08", "categorie": "Automate", "marque": "Schneider Electric", "reference": "Réf. à confirmer", "designation": "Automate programmable", "protocole": "Modbus / Ethernet", "prixAchat": 1100 },
    { "id": "P09", "categorie": "Borne de recharge 22 kW", "marque": "Schneider Electric", "reference": "EVlink Pro AC", "designation": "Borne de recharge 22 kW", "protocole": "OCPP", "prixAchat": 2400 },
    { "id": "P10", "categorie": "Capteur d'ambiance", "marque": "Ewattch", "reference": "Réf. à confirmer", "designation": "Capteur température / CO2", "protocole": "Radio, à confirmer", "prixAchat": 120 }
  ],
  "aides": [
    { "id": "A01", "nom": "CEE : GTB / BACS", "type": "cee", "coefKwhc": 600, "uniteQte": "m² chauffés", "note": "Coefficient de démonstration, à remplacer par la fiche officielle" },
    { "id": "A02", "nom": "CEE : variation électronique de vitesse", "type": "cee", "coefKwhc": 30000, "uniteQte": "kW de moteurs", "note": "Coefficient de démonstration, à remplacer par la fiche officielle" },
    { "id": "A03", "nom": "CEE : récupération de chaleur sur compresseur d'air", "type": "cee", "coefKwhc": 40000, "uniteQte": "kW de compresseur", "note": "Coefficient de démonstration, à remplacer par la fiche officielle" },
    { "id": "A04", "nom": "CEE : éclairage LED", "type": "cee", "coefKwhc": 15000, "uniteQte": "kW installés", "note": "Coefficient de démonstration, à remplacer par la fiche officielle" },
    { "id": "A05", "nom": "Décarb Flash", "type": "fixe", "coefKwhc": 0, "uniteQte": "", "note": "Montant à saisir, conditions à vérifier" },
    { "id": "A06", "nom": "Aide collectivité / région", "type": "fixe", "coefKwhc": 0, "uniteQte": "", "note": "Montant à saisir" }
  ],
  "clients": [
    { "id": "CLI-0001", "nom": "Endress Hauser", "site": "Cernay", "adresse": "Cernay (68)", "lat": 47.807, "lon": 7.176, "secteur": "Industrie", "statut": "Client", "agence": "Mulhouse" },
    { "id": "CLI-0002", "nom": "Exemple : agroalimentaire", "site": "Colmar", "adresse": "Colmar (68)", "lat": 48.079, "lon": 7.358, "secteur": "Industrie", "statut": "Client", "agence": "Colmar" },
    { "id": "CLI-0003", "nom": "Exemple : clinique", "site": "Mulhouse", "adresse": "Mulhouse (68)", "lat": 47.750, "lon": 7.336, "secteur": "Santé", "statut": "Client", "agence": "Mulhouse" },
    { "id": "CLI-0004", "nom": "Exemple : centre commercial", "site": "Wittenheim", "adresse": "Wittenheim (68)", "lat": 47.808, "lon": 7.337, "secteur": "Commerce", "statut": "Prospect", "agence": "Mulhouse" },
    { "id": "CLI-0005", "nom": "Exemple : plateforme logistique", "site": "Saint-Louis", "adresse": "Saint-Louis (68)", "lat": 47.590, "lon": 7.560, "secteur": "Logistique", "statut": "Prospect", "agence": "Mulhouse" },
    { "id": "CLI-0006", "nom": "Exemple : collège", "site": "Guebwiller", "adresse": "Guebwiller (68)", "lat": 47.910, "lon": 7.210, "secteur": "Enseignement", "statut": "Prospect", "agence": "Mulhouse" },
    { "id": "CLI-0007", "nom": "Exemple : fonderie", "site": "Altkirch", "adresse": "Altkirch (68)", "lat": 47.624, "lon": 7.240, "secteur": "Industrie", "statut": "Prospect", "agence": "Mulhouse" }
  ],
  "contacts": [
    { "id": "CT-0001", "clientId": "CLI-0001", "nom": "À compléter", "fonction": "Référent énergie", "email": "", "telephone": "", "referentEnergie": true },
    { "id": "CT-0002", "clientId": "CLI-0002", "nom": "À compléter", "fonction": "Responsable maintenance", "email": "", "telephone": "", "referentEnergie": true },
    { "id": "CT-0003", "clientId": "CLI-0003", "nom": "À compléter", "fonction": "Directeur technique", "email": "", "telephone": "", "referentEnergie": true }
  ],
  "installations": [
    { "id": "INS-0001", "clientId": "CLI-0001", "type": "IRVE", "puissance": 50, "unite": "bornes", "annee": null, "marque": "", "note": "48 bornes 22 kW + 2 bornes 110 kW" },
    { "id": "INS-0002", "clientId": "CLI-0001", "type": "GTB", "puissance": null, "unite": "", "annee": null, "marque": "Niagara + Siemens", "note": "Problème d'accès signalé" },
    { "id": "INS-0003", "clientId": "CLI-0002", "type": "PV", "puissance": 250, "unite": "kWc", "annee": 2023, "marque": "", "note": "" },
    { "id": "INS-0004", "clientId": "CLI-0003", "type": "GTB", "puissance": null, "unite": "", "annee": 2009, "marque": "", "note": "GTB ancienne, non conforme" }
  ],
  "prediagnostics": [
    { "id": "PD-0001", "ref": "PE-EX-001", "clientId": "CLI-0003", "date": "2026-09-15", "auditeur": "Auditeur Eiffage", "energyExpert": "Energy Expert de référence",
      "valeurs": { "consoElec": "2.1", "consoGaz": "1.9", "auditDate": "2024-03-01", "puissanceCVC": "420", "surfaceTertiaire": "800", "bornesIRVE": "0", "comptagePartiel": "non", "actions": "Remplacement GTB" } },
    { "id": "PD-0002", "ref": "PE-EX-002", "clientId": "CLI-0004", "date": "2026-09-29", "auditeur": "Auditeur Eiffage", "energyExpert": "Energy Expert de référence",
      "valeurs": { "consoElec": "1.6", "consoGaz": "0.4", "puissanceCVC": "60", "surfaceTertiaire": "600", "surfaceParking": "12000", "bornesIRVE": "8", "comptagePartiel": "non", "actions": "" } },
    { "id": "PD-0003", "ref": "PE-EX-003", "clientId": "CLI-0006", "date": "2026-10-02", "auditeur": "Auditeur Eiffage", "energyExpert": "Energy Expert de référence",
      "valeurs": { "consoElec": "0.3", "consoGaz": "0.9", "puissanceCVC": "180", "surfaceTertiaire": "4200", "bornesIRVE": "0", "comptagePartiel": "oui", "actions": "" } }
  ],
  "opportunites": [
    { "id": "OPP-0001", "clientId": "CLI-0003", "prediagId": "PD-0001", "regleId": "R03", "titre": "Conformité GTB / BACS", "offre": "EMS", "priorite": "Haute", "echeance": "Depuis le 1er janvier 2025", "statut": "En affaire", "origine": "Règle R03", "date": "2026-09-15" },
    { "id": "OPP-0002", "clientId": "CLI-0004", "prediagId": "PD-0002", "regleId": "R06", "titre": "Ombrières photovoltaïques (loi APER)", "offre": "Smart Grid", "priorite": "Moyenne", "echeance": "2028 à 2030 selon la surface", "statut": "Nouvelle", "origine": "Règle R06", "date": "2026-09-29" },
    { "id": "OPP-0003", "clientId": "CLI-0004", "prediagId": "PD-0002", "regleId": "R07", "titre": "Smart charging et pilotage des bornes", "offre": "IRVE", "priorite": "Moyenne", "echeance": "—", "statut": "En affaire", "origine": "Règle R07", "date": "2026-09-29" },
    { "id": "OPP-0004", "clientId": "CLI-0006", "prediagId": "PD-0003", "regleId": "R04", "titre": "Conformité GTB / BACS (70 à 290 kW)", "offre": "EMS", "priorite": "Moyenne", "echeance": "2027 ou 2030, à confirmer", "statut": "Validée", "origine": "Règle R04", "date": "2026-10-02" },
    { "id": "OPP-0005", "clientId": "CLI-0006", "prediagId": "PD-0003", "regleId": "R05", "titre": "Accompagnement Décret tertiaire", "offre": "Conseil", "priorite": "Moyenne", "echeance": "-40 % en 2030", "statut": "Nouvelle", "origine": "Règle R05", "date": "2026-10-02" },
    { "id": "OPP-0006", "clientId": "CLI-0006", "prediagId": "PD-0003", "regleId": "R08", "titre": "Complément du plan de comptage", "offre": "EMS", "priorite": "Basse", "echeance": "—", "statut": "Nouvelle", "origine": "Règle R08", "date": "2026-10-02" }
  ],
  "affaires": [
    { "id": "AFF-2026-001", "clientId": "CLI-0002", "oppId": null, "titre": "Supervision énergétique (EMS)", "offre": "EMS", "etape": "B", "avancement": 0, "reserve": "",
      "chiffrage": { "lignes": [ { "produitId": "P01", "qte": 24 }, { "produitId": "P04", "qte": 2 }, { "produitId": "P05", "qte": 1 }, { "produitId": "P07", "qte": 1 } ],
        "mainOeuvre": 28000, "marge": 20, "base": "avant", "aides": [ { "aideId": "A02", "qte": 90 }, { "aideId": "A05", "montant": 10000 } ] },
      "historique": [ { "date": "2026-10-05 10:12", "texte": "Affaire créée (saisie manuelle)" } ] },
    { "id": "AFF-2026-002", "clientId": "CLI-0003", "oppId": "OPP-0001", "titre": "Conformité GTB / BACS", "offre": "EMS", "etape": "C", "avancement": 40, "reserve": "",
      "chiffrage": { "lignes": [ { "produitId": "P02", "qte": 12 }, { "produitId": "P05", "qte": 1 }, { "produitId": "P07", "qte": 2 } ],
        "mainOeuvre": 45000, "marge": 20, "base": "avant", "aides": [ { "aideId": "A01", "qte": 9000 } ] },
      "historique": [ { "date": "2026-09-16 09:00", "texte": "Affaire créée depuis OPP-0001" }, { "date": "2026-10-01 14:30", "texte": "Étape B → C" } ] },
    { "id": "AFF-2026-003", "clientId": "CLI-0004", "oppId": "OPP-0003", "titre": "Smart charging et pilotage des bornes", "offre": "IRVE", "etape": "A", "avancement": 0, "reserve": "",
      "chiffrage": { "lignes": [ { "produitId": "P09", "qte": 20 } ], "mainOeuvre": 30000, "marge": 20, "base": "avant", "aides": [] },
      "historique": [ { "date": "2026-09-30 11:20", "texte": "Affaire créée depuis OPP-0003" } ] }
  ],
  "journal": []
};
