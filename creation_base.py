import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Charge les variables du fichier .env
load_dotenv()

# --- CONFIGURATION SÉCURISÉE ---
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# Utilisation d'un chemin relatif pour la portabilité
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "tentative.csv") 
OUTPUT_DIR = os.path.join(BASE_DIR, "metadata")

# --- LE SCRIPT SQL ---
SQL_DDL = """
-- 1. NETTOYAGE PREALABLE
DROP TABLE IF EXISTS SOLUTION CASCADE;
DROP TABLE IF EXISTS DEMANDE CASCADE;
DROP TABLE IF EXISTS ENTRETIEN CASCADE;
DROP TABLE IF EXISTS QUARTIER CASCADE;
DROP TABLE IF EXISTS COMMUNE CASCADE;
DROP TABLE IF EXISTS AGGLO CASCADE;
DROP TABLE IF EXISTS VALEURS_C CASCADE;
DROP TABLE IF EXISTS MODALITE CASCADE;
DROP TABLE IF EXISTS PLAGE CASCADE;
DROP TABLE IF EXISTS VARIABLE CASCADE;
DROP TABLE IF EXISTS RUBRIQUE CASCADE;

-- 2. CREATION PRINCIPALE
CREATE TABLE ENTRETIEN(
   NUM SERIAL,
   DATE_ENT DATE DEFAULT CURRENT_DATE,
   MODE SMALLINT,
   DUREE SMALLINT,
   SEXE SMALLINT,
   AGE SMALLINT,
   VIENT_PR SMALLINT,
   SIT_FAM VARCHAR(2),
   ENFANT SMALLINT,
   MODELE_FAM SMALLINT,
   PROFESSION SMALLINT,
   RESS SMALLINT,
   ORIGINE VARCHAR(2),
   COMMUNE VARCHAR(50),
   PARTENAIRE VARCHAR(50),
   PRIMARY KEY(NUM)
);

COMMENT ON TABLE ENTRETIEN IS 'La table entretien est l''une des tables de stockage des données';
COMMENT ON COLUMN ENTRETIEN.NUM IS 'Identifiant de l''entretien, Rubrique Entretien';
COMMENT ON COLUMN ENTRETIEN.DATE_ENT IS 'Date de l''entretien Valeur par défaut : jour courant';
COMMENT ON COLUMN ENTRETIEN.MODE IS 'Mode de l''entretien (1 : RDV; 2 : Sans RDV;3 : Téléphonique;4 : Courrier;5 : Mail), Rubrique Entretien';
COMMENT ON COLUMN ENTRETIEN.DUREE IS 'Durée de l''entretien (1 : - de 15 min;2 : 15 à 30 min;3 : 30 à 45 min;4 : 45 à 60 min;5 ; + de 60 min), Rubrique Entretien';
COMMENT ON COLUMN ENTRETIEN.SEXE IS 'Sexe si une personne, couple ou professionnel (1 : Homme;2 : Femme;3 : Couple;4 : Professionnel), Rubrique Usager';
COMMENT ON COLUMN ENTRETIEN.AGE IS 'Age de la personne (1 : -18 ans;2 : 18-25 ans;3 : 26-40 ans;4 : 41-60 ans;5 : + 60 ans), Rubrique Usager';
COMMENT ON COLUMN ENTRETIEN.VIENT_PR IS 'Vient pour (1 : Soi;2 : Conjoint;3 : Parent;4 : Enfant;5 : Personne morale;6 : Autre), Rubrique Usager';
COMMENT ON COLUMN ENTRETIEN.SIT_FAM IS 'Situation familiale (1 : Célibataire;2 : Concubin;3 : Pacsé;4 : Marié;5 : Séparé/divorcé;5a : Séparé/divorcé Sans enf. à charge;5b : Séparé/divorcé Avec enf. en garde alternée;5c : Séparé/divorcé Avec enf. en garde principale;5d : Séparé/divorcé Avec enf. en droit de visite/hbgt;5e : Séparé/divorcé Parent isolé; 5f : Séparé/divorcé Séparés sous le même toit;6 : Veuf/ve;6a : Veuf/ve Sans enf. à charge;6b : Veuf/ve Avec enf. à charge;7 : Non renseigné), Rubrique Usager';
COMMENT ON COLUMN ENTRETIEN.ENFANT IS 'Enfant(s) à charge (1;2;3;4;5;6;7;8;9;10;11;12;13), Rubrique Usager';
COMMENT ON COLUMN ENTRETIEN.MODELE_FAM IS 'Si famille avec enfant, il s''agit du modèle familial (1 : Famille traditionnelle;2 : Famille monoparentale;3 : Famille recomposée), Rubrique Usager';
COMMENT ON COLUMN ENTRETIEN.PROFESSION IS 'Profession (1 : Scolaire/étudiant/formation;2 : Pêcheur/agriculteur;3 : Chef d''entreprise;4 : Libéral;5 : Militaire;6 : Employé;7 : Ouvrier;8 : Cadre;9 : Retraité;10 : En recherche d''emploi;11 : Sans profession;12 : Non renseigné) , Rubrique Usager';
COMMENT ON COLUMN ENTRETIEN.RESS IS 'Revenus, ressource principale (1 : Salaire;2 : Revenus pro.;3 : Retraite/réversion;4 : Allocations chômage;5 : RSA;6 : AAH/invalidité;7 : IJSS;8 : Bourse d''études;9 : Sans revenu;10 : Autre;11 : Non renseigné) , Rubrique Usager';
COMMENT ON COLUMN ENTRETIEN.ORIGINE IS 'Origine de la demande (1a : Communication Bouche à oreille;1b : Communication Internet;1c : Communication Presse;2a : Déjà venu Suite problématique;2b : Déjà venu Autre problématique;3a : Par un professionnel du droit Tribunaux;3b : Par un professionnel du droit Police/gendarmerie;3c : Professionnel du droit;4a : Par une administration CAF;4b : Par une administration DIRECCTE;4c : Par une administration Maison France Service;4d : Par une administration Mairie / EPCI;4e : Par une administration Autre;5a : Secteur santé / social Assistante sociale;5b : Secteur santé / social Educateur / autre travailleur social;5c : Secteur santé / social Professionnel de santé;5d : Secteur santé / social Professionnel jeunesse;5e : Secteur santé / social RIPAM;6a : Par une association France Victimes;6b : Par une association Associations de consommateurs;6c : Par une association ADIL;6d : Par une association UDAF;6e : Par une association Association d''accès au droit;6f : Par une association Autre;7a : Organismes privés Protection juridique;7b : Organismes privés Autre;8 : Action collective;9 : 3949 NUAD) , Rubrique Repérage du dispositif';
COMMENT ON COLUMN ENTRETIEN.COMMUNE IS 'Commune de résidence (Allaire;Ambon;Arradon;Arzal;Arzon;Augan;Auray;Auray Gumenen Goaner-Parco Pointer;Baden;Baud;Béganne;Beignon;Belle-Ile;Belz;Berné;Berric;Bieuzy;Bignan;Billers;Billio;Bohal;Brandérion;Brandivy;Brech;Bréhan;Brignac;Bubry;Buléon;Caden;Calan;Camoël;Camors;Campénéac;Carentoir;Carnac;Caro;Caudan;Cléguérec;Cléguers;Colpo;Concoret;Cournon;Crac''h;Crédin;Croixanvec;Cruguel;Damgan;Elven;Erdeven;Etel;Evellys;Evriguet;Férel;Gavres;Glénac;Gestel;Gourhel;Gourrin;Grand-Champ;Guegon;Guéhenno;Gueltas;Guémené-sur-Scorff;Guénin;Guer;Guern;Guidel;Guillac;Guilliers;Guiscriff;Helléan;Hennebont;Ile d''Arz;Ile de Groix;Ile de Hoedic;Ile de Houat;Ile aux Moines;Inguiniel;Inzinzac-Lochrist;Josselin;Kerfourn;Kergrist;Kernascléden;Kervignac;La Chapelle Caro;La Chapelle Gaceline;La Chapelle Neuve;La Croix Helléan;La Gascilly;La Grée-Saint-Laurent;La Roche-Bernard;La Trinité-Porhoët;La Trinité-sur-Mer;La Trinité-Surzur;La Vraie-Croix;Landaul;Landévant;Lanester;Langoëlan;Langonnet;Languidic;Lannouée;Lantillac;Lanvaudan;Lanvénegen;Larmor-Baden;Larmor-Plage;Larré;Lauzach;Le Bono;Le Cours;Le Croisty;Le Faouët;Les Forges de Lannouée;Les Fougerêts;Le Guerno;Le Hézo;Le Roc-Saint-André;Le Saint;Le Sourn;Le Tour-du-Parc;Lignol;Limerzel;Lizio;Locmalo;Locmaria-Grand-Champ;Locmariaquer;Locminé;Locmiquélic;Locoal-Mendon;Locqueltas;Lorient;Loyat;Malensac;Malestroit;Malguénac;Marzan;Mauron;Melrand;Ménéac;Merlevenez;Meslan;Meucon;Missiriac;Mohon;Molac;Monteneuf;Monterblanc;Monterrein;Montertelot;Moréac;Moustoir-Ac;Moustoir-Remungol;Muzillac;Naizin;Néant-sur-Yvel;Neuillac;Nivillac;Nostang;Noyal-Muzillac;Noyal-Pontivy;Péaule;Peillac;Penestin;Persquen;Plaudren;Plescop;Pleucadeuc;Pleugriffet;Ploemel;Ploemeur;Ploërdut;Ploeren;Ploërmel;Plouay;Plougoumelen;Plouharnel;Plouhinec;Plouray;Pluherlin;Plumelec;Pluméliau;Plumelin;Plumergat;Pluneret;Pluvigner;Pont-Scorff;Pontivy;Porcaro;Port-Louis;Priziac;Quelneuc;Questembert;Queven;Quiberon;Quily;Quistinic;Radenac;Réguiny;Réminiac;Remungol;Riantec;Rieux;Rochefort-en-Terre;Rohan;Roudouallec;Ruffiac;Sarzeau;Séglien;Séné;Sérent;Silfiac;St-Abraham;St-Aignan;St-Allouestre;St-Armel;St-Avé;St-Barthélémy;St-Brieuc de Mauron;St-Caradec-Trégomel;St-Congard;St Connec;St-Dolay;St-Gérand;St-Gildas-de-Rhuys;St-Gonnery;St-Gorgon;St-Gravé;St-Guyomard;St-Jacut-les-Pins;St-Jean-Brévelay;St-Jean-la-Poterie;St-Laurent-sur-Oust;St-Léry;St-Malo-de-Beignon;St-Malo-les-Trois-Fontaines;St-Marcel;St-Martin-sur-Oust;St-Nicolas-du-Tertre;St-Nolff;St-Perreux;St-Philibert;St-Pierre-Quiberon;St-Servant;St-Thuriau;St-Tugdual;St-Vincent-sur-Oust;Ste-Anne-d''Auray;Ste-Brigitte;Ste-Hélène;Sulniac;Surzur;Taupont;Tréhillac;Theix-Noyalo;Tréal;Trédion;Treffléan;Tréhoranteuc;Val d''Oust;Vannes;Vannes Bourdonnaye;Vannes Kercado;Vannes Ménimur;HORS 56 Cotes d''Armor;HORS 56 Finistère;HORS 56 Ille et Vilaine;HORS 56 Loire-Atlantique;HORS 56 Autres départements) , Rubrique Résidence';
COMMENT ON COLUMN ENTRETIEN.PARTENAIRE IS 'Partenaire lors de l''entretien (Permanence juridique Vannes;Permanence juridique Auray;Permanence juridique Questembert;Permanence avocat généraliste;Permanence avocat mineurs;Permanence notaire;Permanence conciliateur de justice;Permanence délégué du défenseur des droits), Rubrique Partenaire';
CREATE TABLE DEMANDE(
   NUM INTEGER,
   POS SMALLINT,
   NATURE VARCHAR(50) NOT NULL,
   PRIMARY KEY(NUM, POS),
   FOREIGN KEY(NUM) REFERENCES ENTRETIEN(NUM)
);
COMMENT ON TABLE DEMANDE IS 'La table demande est l''une des tables de stockage des données';
COMMENT ON COLUMN DEMANDE.POS IS 'Identifiant relatif de la demande (1;2;3;4;5;6;7;8;9;10), Rubrique Demande';
COMMENT ON COLUMN DEMANDE.NATURE IS 'Nature de la demande (1a : Droit de la famille / des personnes Union;1b : Droit de la famille / des personnes Séparation / divorce;1c : Droit de la famille / des personnes PA / PC;1d : Droit de la famille / des personnes Droit de garde;1e : Droit de la famille / des personnes Autorité parentale;1f : Droit de la famille / des personnes Filiation adoption;1g : Droit de la famille / des personnes Régimes matrimoniaux;1h : Droit de la famille / des personnes Protection des majeurs;1i : Droit de la famille / des personnes Etat civil;1j : Droit de la famille / des personnes Successions;1k : Droit de la famille / des personnes Assistance éducative;2a : Droit du logement Litiges locatifs;2b : Droit du logement Expulsion;2c : Droit du logement Achat / vente d''un bien;2d : Droit du logement Copropriété;2e : Droit du logement Droit des biens;2f : Droit du logement Construction / urbanisme;2g : Droit du logement Conflit de voisinage;2h : Droit du logement Autre;3a : Droit de la consommation Crédit / reconnaissance de dette;3b : Droit de la consommation Téléphonie / internet;3c : Droit de la consommation Prestation de service;3d : Droit de la consommation Banque / Assurance;3e : Droit de la consommation Surendettement;3f : Droit de la consommation Autre;4a : Autres domaines du droit civil Responsabilité;4b : Autres domaines du droit civil Voies d''exécution;4c : Autres domaines du droit civil Procédure civile;4d : Autres domaines du droit civil Erreur médicale;4e : Autres domaines du droit civil Accident VTM;4f : Autres domaines du droit civil Autre;5a : Droit du travail / affaires / associations Exécution du contrat de travail;5b : Droit du travail / affaires / associations Rupture du contrat de travail;5c : Droit du travail / affaires / associations Droit des affaires / sociétés;5d : Droit du travail / affaires / associations Droit associatif;5e : Droit du travail / affaires / associations Autre;6a : Droit de la protection sociale Aides sociales;6b : Droit de la protection sociale Sécurité sociale;6c : Droit de la protection sociale Retraite;6d : Droit de la protection sociale Cotisations sociales;6e : Droit de la protection sociale Autre;7a : Droit pénal Auteur / mis en cause;7b : Droit pénal Victime;7c : Droit pénal Violences faites aux femmes;7d : Droit pénal Discriminations;7e : Droit pénal Procédure pénale;7f : Droit pénal Autre;8a : Droit administratif Litige avec une administration;8b : Droit administratif Statuts de la fonction publique;8c : Droit administratif Droit des étrangers;8d : Droit administratif Autre;9a : Démarches et formalités Terminologie juridique;9b : Démarches et formalités Aide juridictionnelle;9c : Démarches et formalités Autre), Rubrique Demande';

CREATE TABLE SOLUTION(
   NUM INTEGER,
   POS SMALLINT,
   NATURE VARCHAR(50) NOT NULL,
   PRIMARY KEY(NUM, POS),
   FOREIGN KEY(NUM) REFERENCES ENTRETIEN(NUM)
);
COMMENT ON TABLE SOLUTION IS 'La table solution est l''une des tables de stockage des données';
COMMENT ON COLUMN SOLUTION.POS IS 'Identifiant relatif de la solution (1;2;3;4;5;6;7;8;9;10), Rubrique Solution';
COMMENT ON COLUMN SOLUTION.NATURE IS 'Nature de la solution (1 : Information;2a : Aide aux démarches Saisine justice internet;2b : Aide aux démarches Aide CAF (ASF);2c : Aide aux démarches Autre démarche;3a : Aide à la rédaction Courrier;3b : Aide à la rédaction Requête;3c : Aide à la rédaction Autre;4a : Orientation professionnel du droit Avocat;4b : Orientation professionnel du droit Avocat mineur;4c : Orientation professionnel du droit Notaire;4d : Orientation professionnel du droit Huissier;4e : Orientation professionnel du droit Tribunal;4f : Orientation professionnel du droit Police / gendarmerie;4g : Orientation professionnel du droit Autre;5a : Orientation MARD Conciliateur de justice;5b : Orientation MARD Délégué du Défenseur des Droits;5c : Orientation MARD Médiation familiale;5d : Orientation MARD Médiation administrative;5e : Orientation MARD Médiation consommation;5f : Orientation MARD Médiation banque / assurance;6a : Orientation administration Mairie / EPCI;6b : Orientation administration DIRECCTE;6c : Orientation administration CAF;6d : Orientation administration Maison France Service;6e : Orientation administration Préfecture;6f : Orientation administration Impôts;6g : Orientation administration Autre;7a : Orientation association Aide aux victimes;7b : Orientation association Accès au Droit;7c : Orientation association ADIL;7d : Orientation association Association de consommateurs;7e : Orientation association Autre;8a : Orientation santé / social Travailleur social;8b : Orientation santé / social Professionnel de santé;8c : Orientation santé / social Professionnel jeunesse;8d : Orientation santé / social Autre;9a : Orientation organisme privé Protection juridique;9b : Orientation organisme privé Autre organisme privé), Rubrique Solution';

COMMENT ON COLUMN DEMANDE.NUM IS 'Clé étrangère vers l''identifiant de l''entretien, Rubrique Entretien';
COMMENT ON COLUMN SOLUTION.NUM IS 'Clé étrangère vers l''identifiant de l''entretien, Rubrique Entretien';

SELECT UPPER(TABLE_NAME),ordinal_position,UPPER(COLUMN_NAME) FROM INFORMATION_SCHEMA.COLUMNS WHERE UPPER(TABLE_NAME) IN ('ENTRETIEN','DEMANDE','SOLUTION') ORDER BY 1,2,3;

SELECT UPPER(TABLE_NAME),ordinal_position,UPPER(COLUMN_NAME),
    obj_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid, 'pg_class') as table_description,
    pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position) as column_description
FROM
    information_schema.columns isc
WHERE UPPER(TABLE_NAME) IN ('ENTRETIEN','DEMANDE','SOLUTION')
ORDER BY 1,2,3;
    
SELECT UPPER(TABLE_NAME),ordinal_position,UPPER(COLUMN_NAME),SUBSTRING(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), 1, POSITION('(' in pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position)))
FROM
    information_schema.columns isc
WHERE UPPER(TABLE_NAME) IN ('ENTRETIEN','DEMANDE','SOLUTION')
ORDER BY 1,2,3;

SELECT UPPER(TABLE_NAME),ordinal_position,UPPER(COLUMN_NAME),
CASE
  WHEN POSITION('(' in pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position))>0 THEN SUBSTRING(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), 1, POSITION('(' in pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position))-1)
  ELSE pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position)
END AS COL_COMMENT
FROM
    information_schema.columns isc
WHERE UPPER(TABLE_NAME) IN ('ENTRETIEN','DEMANDE','SOLUTION')
ORDER BY 1,2,3;

SELECT UPPER(TABLE_NAME),ordinal_position,UPPER(COLUMN_NAME),
CASE
  WHEN POSITION('(' in pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position))>0 THEN SUBSTRING(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), 1, POSITION('(' in pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position))-1)
  WHEN POSITION(', Rubrique' in pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position))>0 THEN SUBSTRING(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), 1, POSITION(', Rubrique' in pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position))-1)
  ELSE pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position)
END AS COL_COMMENT
FROM
    information_schema.columns isc
WHERE UPPER(TABLE_NAME) IN ('ENTRETIEN','DEMANDE','SOLUTION')
ORDER BY 1,2,3;

CREATE TABLE RUBRIQUE(
   POS SERIAL,
   LIB VARCHAR(50) NOT NULL,
   PRIMARY KEY(POS)
);
COMMENT ON TABLE RUBRIQUE IS 'Métadonnées sur les rubriques de l''entretien pour générer les formulaires et les ordres SQL à la volée.';
COMMENT ON COLUMN RUBRIQUE.POS IS 'Position logique de la rubrique lors de la collecte de données';
COMMENT ON COLUMN RUBRIQUE.LIB IS 'Libellé de la rubrique';

SELECT DISTINCT CASE WHEN POSITION(', Rubrique ' in pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position))>0 THEN SUBSTRING(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), POSITION(', Rubrique ' in pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position))+11)
ELSE NULL END
FROM
    information_schema.columns isc
WHERE UPPER(TABLE_NAME) IN ('ENTRETIEN','DEMANDE','SOLUTION')
;
INSERT INTO RUBRIQUE (LIB) VALUES
('Entretien'),
('Usager'),
('Demande'),
('Solution'),
('Repérage du dispositif'),
('Résidence'),
('Partenaire');

CREATE TABLE VARIABLE(
   TAB VARCHAR(30),
   POS SMALLINT,
   LIB VARCHAR(50) NOT NULL,
   COMMENTAIRE VARCHAR(4000),
   MOIS_DEBUT_VALIDITE SMALLINT NOT NULL,
   MOIS_FIN_VALIDITE SMALLINT NOT NULL,
   TYPE_V VARCHAR(8) NOT NULL,
   DEFVAL SMALLINT,
   EST_CONTRAINTE BOOLEAN NOT NULL,
   POS_R INTEGER NOT NULL,
   RUBRIQUE INTEGER NOT NULL,
   PRIMARY KEY(TAB, POS),
   UNIQUE(TAB, LIB),
   FOREIGN KEY(RUBRIQUE) REFERENCES RUBRIQUE(POS)
);
COMMENT ON TABLE VARIABLE IS 'Métadonnées sur les variables pour générer les formulaires et les ordres SQL à la volée';
COMMENT ON COLUMN VARIABLE.TAB IS 'Table de stockage de la variable';
COMMENT ON COLUMN VARIABLE.POS IS 'Position de la variable dans table de stockage';
COMMENT ON COLUMN VARIABLE.LIB IS 'Libellé de la variable dans la table de stockage';
COMMENT ON COLUMN VARIABLE.POS_R IS 'Position de la variable dans sa rubrique';
COMMENT ON COLUMN VARIABLE.COMMENTAIRE IS 'Aide à la signification de la variable';
COMMENT ON COLUMN VARIABLE.MOIS_DEBUT_VALIDITE IS 'Début de la validité de la variable exprimée en numéro de mois dans l''année. Cette limite inférieure est incluse dans la validité. Valeur par défaut : 1';
COMMENT ON COLUMN VARIABLE.MOIS_FIN_VALIDITE IS 'Fin de la validité de la variable exprimée en numéro de mois dans l''année. Cette limite supérieure est incluse dans la validité. Valeur par défaut : 12';
COMMENT ON COLUMN VARIABLE.TYPE_V IS 'Type de la valeur (MOD; NUM; CHAINE)';
COMMENT ON COLUMN VARIABLE.DEFVAL IS 'Position dans les modalités, ou la liste numérique ou valeur par défaut pour la plage numérique';
COMMENT ON COLUMN VARIABLE.EST_CONTRAINTE IS 'Faut il faire un combo box (False) ou une boite de selection (True)';
COMMENT ON COLUMN VARIABLE.RUBRIQUE IS 'Clé étrangère vers l''identifiant de la rubrique';

CREATE TABLE PLAGE(
   TAB VARCHAR(30),
   POS SMALLINT,
   VAL_MIN SMALLINT,
   VAL_MAX SMALLINT,
   PRIMARY KEY(TAB, POS),
   FOREIGN KEY(TAB, POS) REFERENCES VARIABLE(TAB, POS)
);
COMMENT ON TABLE PLAGE IS 'Métadonnées sur les plages numériques pour générer les formulaires et les ordres SQL à la volée';
COMMENT ON COLUMN PLAGE.TAB IS 'Table de stockage de la variable';
COMMENT ON COLUMN PLAGE.POS IS 'Position de la variable dans table de stockage';
COMMENT ON COLUMN PLAGE.VAL_MIN IS 'Valeur minimale si numérique, valeur par défaut : 0';
COMMENT ON COLUMN PLAGE.VAL_MAX IS 'Valeur maximale si numérique Valeur par defaut : 128';

CREATE TABLE MODALITE(
   TAB VARCHAR(30),
   POS SMALLINT,
   CODE VARCHAR(2),
   POS_M SMALLINT NOT NULL,
   LIB_M VARCHAR(80) NOT NULL,
   PRIMARY KEY(TAB, POS, CODE),
   FOREIGN KEY(TAB, POS) REFERENCES VARIABLE(TAB, POS)
);
COMMENT ON TABLE MODALITE IS 'Métadonnées sur les modalités des variables pour générer les formulaires et les ordres SQL à la volée';
COMMENT ON COLUMN MODALITE.TAB IS 'Table de stockage de la variable';
COMMENT ON COLUMN MODALITE.POS IS 'Position de la variable dans table de stockage';
COMMENT ON COLUMN MODALITE.CODE IS 'Identifiant de la modalité';
COMMENT ON COLUMN MODALITE.POS_M IS 'Position permettant un tri pour retrouver l''ordre logique des modalités';
COMMENT ON COLUMN MODALITE.LIB_M IS 'Libellé de la modalité';

CREATE TABLE VALEURS_C(
   TAB VARCHAR(30),
   POS SMALLINT,
   POS_C SMALLINT,
   LIB VARCHAR(50) NOT NULL,
   PRIMARY KEY(TAB, POS, POS_C),
   FOREIGN KEY(TAB, POS) REFERENCES VARIABLE(TAB, POS)
);
COMMENT ON TABLE VALEURS_C IS 'Métadonnées sur les éléments chaîne de caractères d''une liste pour générer les formulaires et les ordres SQL à la volée';
COMMENT ON COLUMN VALEURS_C.TAB IS 'Table de stockage de la variable';
COMMENT ON COLUMN VALEURS_C.POS IS 'Position de la variable dans table de stockage';
COMMENT ON COLUMN VALEURS_C.POS_C IS 'Identifiant de l''élément de la liste';
COMMENT ON COLUMN VALEURS_C.LIB IS 'Libellé de l''élément de la liste';

INSERT INTO VARIABLE (TAB, POS, LIB, COMMENTAIRE,MOIS_DEBUT_VALIDITE, MOIS_FIN_VALIDITE, TYPE_V, DEFVAL, EST_CONTRAINTE, POS_R, RUBRIQUE)
SELECT UPPER(TABLE_NAME),ordinal_position,UPPER(COLUMN_NAME),
CASE
  WHEN POSITION('(' in pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position))>0 THEN SUBSTRING(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), 1, POSITION('(' in pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position))-1)
  WHEN POSITION(', Rubrique' in pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position))>0 THEN SUBSTRING(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), 1, POSITION(', Rubrique' in pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position))-1)
  ELSE pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position)
END AS COL_COMMENT, 1, 12,'MOD', NULL, FALSE, 1,1
FROM
    information_schema.columns isc
WHERE UPPER(TABLE_NAME) IN ('ENTRETIEN','DEMANDE','SOLUTION')
ORDER BY 1,2,3;

UPDATE VARIABLE SET COMMENTAIRE='Nombre d''enfant à charge' WHERE TAB='ENTRETIEN' AND POS=9;

COMMENT ON COLUMN ENTRETIEN.DATE_ENT IS 'Date de l''entretien, Valeur par défaut : jour courant, Rubrique Entretien';

-- ERREUR:  une valeur NULL viole la contrainte NOT NULL de la colonne « rubrique »
-- DETAIL:  La ligne en échec contient (ENTRETIEN, 15, PARTENAIRE, Partenaire lors de l'entretien , 1, 12, MOD, null, f, 1, null).
-- Il fallait corriger la rubrique Type de partenaire -> Partenaire dans le commentaire.
UPDATE VARIABLE V SET RUBRIQUE=(
SELECT POS FROM RUBRIQUE WHERE LIB=(SELECT DISTINCT CASE WHEN POSITION(', Rubrique ' in pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position))>0 THEN SUBSTRING(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), POSITION(', Rubrique ' in pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position))+11)
ELSE 'NEANT' END
FROM
    information_schema.columns isc
WHERE UPPER(TABLE_NAME)=V.TAB AND UPPER(COLUMN_NAME)=V.LIB 
)
)
;

UPDATE VARIABLE V SET POS_R=POS
WHERE TAB='ENTRETIEN' AND RUBRIQUE=1;
UPDATE VARIABLE V SET POS_R=POS-4
WHERE TAB='ENTRETIEN' AND RUBRIQUE=2;

UPDATE VARIABLE V SET TYPE_V='NUM' WHERE TAB='ENTRETIEN' AND POS=9;
UPDATE VARIABLE V SET TYPE_V='CHAINE' WHERE TAB='ENTRETIEN' AND POS=14;
UPDATE VARIABLE V SET TYPE_V='CHAINE' WHERE TAB='ENTRETIEN' AND POS=15;

INSERT INTO PLAGE (TAB,POS,VAL_MIN,VAL_MAX)
VALUES('ENTRETIEN',9,0,13);

INSERT INTO VALEURS_C (TAB,POS,LIB,POS_C)
SELECT 'ENTRETIEN',15,a.*
FROM information_schema.columns isc,unnest(string_to_array(split_part(split_part(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), '(', 2),')',1),';')) WITH ORDINALITY a
WHERE UPPER(TABLE_NAME)='ENTRETIEN' AND isc.ordinal_position=15 ;

INSERT INTO VALEURS_C (TAB,POS,LIB,POS_C)
SELECT 'ENTRETIEN',14,a.*
FROM information_schema.columns isc,unnest(string_to_array(split_part(split_part(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), '(', 2),')',1),';')) WITH ORDINALITY a
WHERE UPPER(TABLE_NAME)='ENTRETIEN' AND isc.ordinal_position=14 ;

COMMENT ON COLUMN ENTRETIEN.MODE IS 'Mode de l''entretien (1 : RDV;2 : Sans RDV;3 : Téléphonique;4 : Courrier;5 : Mail), Rubrique Entretien';


SELECT 'ENTRETIEN',3,a.*
FROM information_schema.columns isc,unnest(string_to_array(split_part(split_part(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), '(', 2),')',1),';')) WITH ORDINALITY a
WHERE UPPER(TABLE_NAME)='ENTRETIEN' AND isc.ordinal_position=3 ;

INSERT INTO MODALITE (TAB,POS,CODE,POS_M,LIB_M)
SELECT 'ENTRETIEN',3, split_part(a,' : ',1) AS CODE,a.ordinality as POS_M, split_part(a,' : ',2) AS LIB_M
FROM information_schema.columns isc,unnest(string_to_array(split_part(split_part(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), '(', 2),')',1),';')) WITH ORDINALITY a
WHERE UPPER(TABLE_NAME)='ENTRETIEN' AND isc.ordinal_position=3 ;


COMMENT ON COLUMN ENTRETIEN.DUREE IS 'Durée de l''entretien (1 : - de 15 min;2 : 15 à 30 min;3 : 30 à 45 min;4 : 45 à 60 min;5 : + de 60 min), Rubrique Entretien';

INSERT INTO MODALITE (TAB,POS,CODE,POS_M,LIB_M)
SELECT 'ENTRETIEN',4, split_part(a,' : ',1) AS CODE,a.ordinality as POS_M, split_part(a,' : ',2) AS LIB_M
FROM information_schema.columns isc,unnest(string_to_array(split_part(split_part(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), '(', 2),')',1),';')) WITH ORDINALITY a
WHERE UPPER(TABLE_NAME)='ENTRETIEN' AND isc.ordinal_position=4 ;

INSERT INTO MODALITE (TAB,POS,CODE,POS_M,LIB_M)
SELECT 'ENTRETIEN',5, split_part(a,' : ',1) AS CODE,a.ordinality as POS_M, split_part(a,' : ',2) AS LIB_M
FROM information_schema.columns isc,unnest(string_to_array(split_part(split_part(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), '(', 2),')',1),';')) WITH ORDINALITY a
WHERE UPPER(TABLE_NAME)='ENTRETIEN' AND isc.ordinal_position=5 ;

INSERT INTO MODALITE (TAB,POS,CODE,POS_M,LIB_M)
SELECT 'ENTRETIEN',6, split_part(a,' : ',1) AS CODE,a.ordinality as POS_M, split_part(a,' : ',2) AS LIB_M
FROM information_schema.columns isc,unnest(string_to_array(split_part(split_part(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), '(', 2),')',1),';')) WITH ORDINALITY a
WHERE UPPER(TABLE_NAME)='ENTRETIEN' AND isc.ordinal_position=6 ;

INSERT INTO MODALITE (TAB,POS,CODE,POS_M,LIB_M)
SELECT 'ENTRETIEN',7, split_part(a,' : ',1) AS CODE,a.ordinality as POS_M, split_part(a,' : ',2) AS LIB_M
FROM information_schema.columns isc,unnest(string_to_array(split_part(split_part(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), '(', 2),')',1),';')) WITH ORDINALITY a
WHERE UPPER(TABLE_NAME)='ENTRETIEN' AND isc.ordinal_position=7 ;

COMMENT ON COLUMN ENTRETIEN.SIT_FAM IS 'Situation familiale (1 : Célibataire;2 : Concubin;3 : Pacsé;4 : Marié;5 : Séparé/divorcé;5a : Séparé/divorcé Sans enf. à charge;5b : Séparé/divorcé Avec enf. en garde alternée;5c : Séparé/divorcé Avec enf. en garde principale;5d : Séparé/divorcé Avec enf. en droit de visite/hbgt;5e : Séparé/divorcé Parent isolé;5f : Séparé/divorcé Séparés sous le même toit;6 : Veuf/ve;6a : Veuf/ve Sans enf. à charge;6b : Veuf/ve Avec enf. à charge;7 : Non renseigné), Rubrique Usager';

INSERT INTO MODALITE (TAB,POS,CODE,POS_M,LIB_M)
SELECT 'ENTRETIEN',8, split_part(a,' : ',1) AS CODE,a.ordinality as POS_M, split_part(a,' : ',2) AS LIB_M
FROM information_schema.columns isc,unnest(string_to_array(split_part(split_part(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), '(', 2),')',1),';')) WITH ORDINALITY a
WHERE UPPER(TABLE_NAME)='ENTRETIEN' AND isc.ordinal_position=8 ;

INSERT INTO MODALITE (TAB,POS,CODE,POS_M,LIB_M)
SELECT 'ENTRETIEN',10, split_part(a,' : ',1) AS CODE,a.ordinality as POS_M, split_part(a,' : ',2) AS LIB_M
FROM information_schema.columns isc,unnest(string_to_array(split_part(split_part(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), '(', 2),')',1),';')) WITH ORDINALITY a
WHERE UPPER(TABLE_NAME)='ENTRETIEN' AND isc.ordinal_position=10 ;

INSERT INTO MODALITE (TAB,POS,CODE,POS_M,LIB_M)
SELECT 'ENTRETIEN',11, split_part(a,' : ',1) AS CODE,a.ordinality as POS_M, split_part(a,' : ',2) AS LIB_M
FROM information_schema.columns isc,unnest(string_to_array(split_part(split_part(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), '(', 2),')',1),';')) WITH ORDINALITY a
WHERE UPPER(TABLE_NAME)='ENTRETIEN' AND isc.ordinal_position=11 ;

INSERT INTO MODALITE (TAB,POS,CODE,POS_M,LIB_M)
SELECT 'ENTRETIEN',12, split_part(a,' : ',1) AS CODE,a.ordinality as POS_M, split_part(a,' : ',2) AS LIB_M
FROM information_schema.columns isc,unnest(string_to_array(split_part(split_part(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), '(', 2),')',1),';')) WITH ORDINALITY a
WHERE UPPER(TABLE_NAME)='ENTRETIEN' AND isc.ordinal_position=12 ;

INSERT INTO MODALITE (TAB,POS,CODE,POS_M,LIB_M)
SELECT 'ENTRETIEN',13, split_part(a,' : ',1) AS CODE,a.ordinality as POS_M, split_part(a,' : ',2) AS LIB_M
FROM information_schema.columns isc,unnest(string_to_array(split_part(split_part(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), '(', 2),')',1),';')) WITH ORDINALITY a
WHERE UPPER(TABLE_NAME)='ENTRETIEN' AND isc.ordinal_position=13 ;                                                                                                                      

INSERT INTO MODALITE (TAB,POS,CODE,POS_M,LIB_M)
SELECT 'DEMANDE',3, split_part(a,' : ',1) AS CODE,a.ordinality as POS_M, split_part(a,' : ',2) AS LIB_M
FROM information_schema.columns isc,unnest(string_to_array(split_part(split_part(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), '(', 2),')',1),';')) WITH ORDINALITY a
WHERE UPPER(TABLE_NAME)='DEMANDE' AND isc.ordinal_position=3 ;                                                                                                                      

COMMENT ON COLUMN SOLUTION.NATURE IS 'Nature de la solution (1 : Information;2a : Aide aux démarches Saisine justice internet;2b : Aide aux démarches Aide CAF / ASF;2c : Aide aux démarches Autre démarche;3a : Aide à la rédaction Courrier;3b : Aide à la rédaction Requête;3c : Aide à la rédaction Autre;4a : Orientation professionnel du droit Avocat;4b : Orientation professionnel du droit Avocat mineur;4c : Orientation professionnel du droit Notaire;4d : Orientation professionnel du droit Huissier;4e : Orientation professionnel du droit Tribunal;4f : Orientation professionnel du droit Police / gendarmerie;4g : Orientation professionnel du droit Autre;5a : Orientation MARD Conciliateur de justice;5b : Orientation MARD Délégué du Défenseur des Droits;5c : Orientation MARD Médiation familiale;5d : Orientation MARD Médiation administrative;5e : Orientation MARD Médiation consommation;5f : Orientation MARD Médiation banque / assurance;6a : Orientation administration Mairie / EPCI;6b : Orientation administration DIRECCTE;6c : Orientation administration CAF;6d : Orientation administration Maison France Service;6e : Orientation administration Préfecture;6f : Orientation administration Impôts;6g : Orientation administration Autre;7a : Orientation association Aide aux victimes;7b : Orientation association Accès au Droit;7c : Orientation association ADIL;7d : Orientation association Association de consommateurs;7e : Orientation association Autre;8a : Orientation santé / social Travailleur social;8b : Orientation santé / social Professionnel de santé;8c : Orientation santé / social Professionnel jeunesse;8d : Orientation santé / social Autre;9a : Orientation organisme privé Protection juridique;9b : Orientation organisme privé Autre organisme privé), Rubrique Solution';

INSERT INTO MODALITE (TAB,POS,CODE,POS_M,LIB_M)
SELECT 'SOLUTION',3, split_part(a,' : ',1) AS CODE,a.ordinality as POS_M, split_part(a,' : ',2) AS LIB_M
FROM information_schema.columns isc,unnest(string_to_array(split_part(split_part(pg_catalog.col_description(format('%s.%s',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position), '(', 2),')',1),';')) WITH ORDINALITY a
WHERE UPPER(TABLE_NAME)='SOLUTION' AND isc.ordinal_position=3 ;                                                                                                                      

CREATE TABLE AGGLO(
   CODE_A SERIAL,
   NOM_A VARCHAR(50) NOT NULL,
   ACRONYME VARCHAR(20) NOT NULL,
   URL VARCHAR(50),
   PRIMARY KEY(CODE_A)
);
COMMENT ON TABLE AGGLO IS 'Les communautés de communes ou d''agglomération du morbihan Auray Quiberon Terre Atlantique, AQTA (Auray;Auray Gumenen Goaner-Parco Pointer;Belz;Brech;Camors;Carnac;Crac''h;Erdeven;Etel;Ile de Hoedic;Ile de Houat;Landaul;Landévant;La Trinité-sur-Mer;Locmariaquer;Locoal-Mendon;Ploemel;Plouharnel;Pluneret;Plumergat;Pluvigner;Quiberon;Ste-Anne-d''Auray;St-Philibert;St-Pierre-Quiberon) Golfe du Morbihan - Vannes agglomération, Vannes Agglo (Arradon;Arzon;Baden;Brandivy;Colpo;Elven;Grand-Champ;Ile d''Arz;Ile aux Moines;La Trinité-Surzur;Larmor-Baden;Le Bono;Le Hézo;Le Tour-du-Parc;Meucon;Monterblanc;Plaudren;Plescop;Ploeren;Plougoumelen;St-Armel;St-Avé;St-Gildas-de-Rhuys;St-Nolff;Sarzeau;Séné;Sulniac;Theix-Noyalo;Trédion;Treffléan;Vannes;Vannes Bourdonnaye;Vannes Kercado;Vannes Ménimur) Questembert Communauté, Questembert CO. (Questembert;Limerzel;Caden;Malensac;St-Gravé;Rochefort-en-Terre;Pluherlin;Molac;Le Cours;Larré;La Vraie-Croix;Berric;Lauzach) Arc Sud Bretagne, (Ambon;Arzal;Billiers;Damgan;La Roche-Bernard;Le Guerno;Marzan;Muzillac;Nivillac;Noyal-Muzillac;Péaule;St-Dolay) Oust à Brocéliande Communauté, Oust à Broceliande (Augan;Beignon;Bohal;Carentoir;Caro;Cournon;Guer;La Gascilly;Lizio;Malestroit;Missiriac;Monteneuf;Pleucadeuc;Réminiac;Ruffiac;St-Abraham;St-Congard;St-Guyomard;St-Laurent-sur-Oust;St-Malo-de-Beignon;St-Marcel;St-Martin-sur-Oust;St-Nicolas-du-Tertre;Sérent;Tréal) Ploërmel Communauté, (Brignac;Campénéac;Concoret;Cruguel;Évriguet;Les Forges de Lannouée;Gourhel;Guégon;Guillac;Guilliers;Helléan;Josselin;La Croix Helléan;La Grée-Saint-Laurent;La Trinité-Porhoët;Lantillac;Loyat;Mauron;Ménéac;Mohon;Montertelot;Néant-sur-Yvel;Ploërmel;St-Brieuc de Mauron;St-Léry;St-Malo-les-Trois-Fontaines;St-Servant;Taupont;Tréhorenteuc;Val d''Oust)';
COMMENT ON COLUMN AGGLO.CODE_A IS 'Identifiant de la communauté de communes ou d''agglomération';
COMMENT ON COLUMN AGGLO.NOM_A IS 'Nom complet de la communauté de communes ou d''agglomération';
COMMENT ON COLUMN AGGLO.ACRONYME IS 'Acronyme fait des initiales de la communauté de communes ou d''agglomération ou nom court';
COMMENT ON COLUMN AGGLO.URL IS 'URL du site de l''agglomération';

INSERT INTO AGGLO (NOM_A,ACRONYME) VALUES ('Auray Quiberon Terre Atlantique', 'AQTA'),('Golfe du Morbihan - Vannes agglomération','Vannes Agglo'),('Questembert Communauté','Questembert CO'),('Oust à Brocéliande Communauté','Oust à Broceliande'),('Arc Sud Bretagne',''),('Ploërmel Communauté','');	

CREATE TABLE COMMUNE(
   CODE_C SERIAL,
   NOM_C VARCHAR(50) NOT NULL,
   INSEE VARCHAR(5),
   URL VARCHAR(50),
   CODE_A INTEGER NULL,
   PRIMARY KEY(CODE_C),
   FOREIGN KEY(CODE_A) REFERENCES AGGLO(CODE_A)
);
COMMENT ON TABLE COMMUNE IS 'Les communes du morbihan';
COMMENT ON COLUMN COMMUNE.CODE_C IS 'Identifiant de la commune';
COMMENT ON COLUMN COMMUNE.NOM_C IS 'Nom de la commune';
COMMENT ON COLUMN COMMUNE.INSEE IS 'Code INSEE de la commune pour le recensement de la population';
COMMENT ON COLUMN COMMUNE.URL IS 'URL du site de la commune';

INSERT INTO COMMUNE (NOM_C) 
SELECT LIB FROM VALEURS_C WHERE TAB='ENTRETIEN' AND POS=14 AND POS_C NOT IN (8,262,263,264);

UPDATE COMMUNE SET CODE_A=1 WHERE NOM_C IN ('Auray','Belz','Brech','Camors','Carnac','Crac''h','Erdeven','Etel','Ile de Hoedic','Ile de Houat','Landaul','Landévant','La Trinité-sur-Mer','Locmariaquer','Locoal-Mendon','Ploemel','Plouharnel','Pluneret','Plumergat','Pluvigner','Quiberon','Ste-Anne-d''Auray','St-Philibert','St-Pierre-Quiberon');
UPDATE COMMUNE SET CODE_A=2 WHERE NOM_C IN ('Arradon','Arzon','Baden','Brandivy','Colpo','Elven','Grand-Champ','Ile d''Arz','Ile aux Moines','La Trinité-Surzur','Larmor-Baden','Le Bono','Le Hézo','Le Tour-du-Parc','Meucon','Monterblanc','Plaudren','Plescop','Ploeren','Plougoumelen','St-Armel','St-Avé','St-Gildas-de-Rhuys','St-Nolff','Sarzeau','Séné','Sulniac','Theix-Noyalo','Trédion','Treffléan','Vannes');
UPDATE COMMUNE SET CODE_A=3 WHERE NOM_C IN ('Questembert','Limerzel','Caden','Malensac','St-Gravé','Rochefort-en-Terre','Pluherlin','Molac','Le Cours','Larré','La Vraie-Croix','Berric','Lauzach');
UPDATE COMMUNE SET CODE_A=4 WHERE NOM_C IN ('Augan','Beignon','Bohal','Carentoir','Caro','Cournon','Guer','La Gascilly','Lizio','Malestroit','Missiriac','Monteneuf','Pleucadeuc','Réminiac','Ruffiac','St-Abraham','St-Congard','St-Guyomard','St-Laurent-sur-Oust','St-Malo-de-Beignon','St-Marcel','St-Martin-sur-Oust','St-Nicolas-du-Tertre','Sérent','Tréal');
UPDATE COMMUNE SET CODE_A=5 WHERE NOM_C IN ('Ambon','Arzal','Billiers','Damgan','La Roche-Bernard','Le Guerno','Marzan','Muzillac','Nivillac','Noyal-Muzillac','Péaule','St-Dolay');
UPDATE COMMUNE SET CODE_A=6 WHERE NOM_C IN ('Brignac','Campénéac','Concoret','Cruguel','Évriguet','Les Forges de Lannouée','Gourhel','Guégon','Guillac','Guilliers','Helléan','Josselin','La Croix Helléan','La Grée-Saint-Laurent','La Trinité-Porhoët','Lantillac','Loyat','Mauron','Ménéac','Mohon','Montertelot','Néant-sur-Yvel','Ploërmel','St-Brieuc de Mauron','St-Léry','St-Malo-les-Trois-Fontaines','St-Servant','Taupont','Tréhorenteuc','Val d''Oust');


CREATE TABLE QUARTIER(
   CODE_Q SERIAL,
   NOM_Q VARCHAR(50) NOT NULL,
   INSEE_IRIS VARCHAR(8),
   CODE_C INTEGER NOT NULL,
   PRIMARY KEY(CODE_Q),
   FOREIGN KEY(CODE_C) REFERENCES COMMUNE(CODE_C)
);
COMMENT ON TABLE QUARTIER IS 'Liste des quartiers prioritaires en 2025 dans le morbihan hors la zone de Lorient';
COMMENT ON COLUMN QUARTIER.CODE_Q IS 'Identifiant du quartier prioritaire';
COMMENT ON COLUMN QUARTIER.NOM_Q IS 'Nom complet du quartier prioritaire';
COMMENT ON COLUMN QUARTIER.INSEE_IRIS IS 'Ménimur (QN05609M), Kercado (QN05608M), Bourdonnaye(), Gumenen Goaner-Parco Pointer (QN05601M)  https://www.insee.fr/fr/outil-interactif/7737357/map.html';

INSERT INTO QUARTIER(NOM_Q,CODE_C) VALUES ('Auray Gumenen Goaner-Parco Pointer',7),('Vannes Bourdonnaye',260),('Vannes Kercado',260),('Vannes Ménimur',260);

UPDATE VARIABLE SET DEFVAL=261 WHERE TAB='ENTRETIEN' AND POS=14;
"""

def create_database():
    """Crée la base de données si elle n'existe pas déjà."""
    print(f"🔌 Connexion au serveur pour vérifier la base '{DB_NAME}'...")
    try:
        conn = psycopg2.connect(dbname="postgres", user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
        exists = cur.fetchone()
        
        if not exists:
            print(f"🔨 Création de la base de données '{DB_NAME}'...")
            cur.execute(f'CREATE DATABASE "{DB_NAME}"')
        else:
            print(f"ℹ️ La base de données '{DB_NAME}' existe déjà.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Erreur lors de la création de la base : {e}")

def execute_ddl_and_exports():
    """Exécute le script SQL de création puis exporte les CSV."""
    print(f"🚀 Connexion à '{DB_NAME}' pour exécuter le script...")
    
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        cur = conn.cursor()

        print("⚙️ Exécution du script SQL (Création tables + Introspection)...")
        cur.execute(SQL_DDL)
        conn.commit()
        print("✅ Tables créées et métadonnées générées avec succès.")

        if not os.path.exists(OUTPUT_DIR):
            print(f"⚠️ Création du dossier {OUTPUT_DIR}...")
            os.makedirs(OUTPUT_DIR)

        tables_to_export = [
            "VARIABLE", "PLAGE", "MODALITE", "VALEURS_C", 
            "RUBRIQUE", "QUARTIER", "COMMUNE", "AGGLO"
        ]

        print(f"📂 Exportation des fichiers CSV vers {OUTPUT_DIR}...")
        
        for table in tables_to_export:
            file_path = os.path.join(OUTPUT_DIR, f"{table}.csv")
            sql_copy = f"COPY {table} TO STDOUT WITH (FORMAT CSV, HEADER)"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                cur.copy_expert(sql_copy, f)
            print(f"   -> {table}.csv généré.")

        cur.close()
        conn.close()
        print("🎉 Terminé ! Tout est en place.")

    except Exception as e:
        print(f"❌ Erreur lors de l'exécution : {e}")
        if conn:
            conn.rollback()

if __name__ == "__main__":
    # Vérification de l'existence et accessibilité de la base de données
    db_exists = False
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        conn.close()
        db_exists = True
        print(f"ℹ️ Connexion réussie à la base '{DB_NAME}'. Pas besoin de la créer.")
    except Exception:
        pass

    if not db_exists:
        create_database()
    execute_ddl_and_exports()