# Boreal Assurances - Entrepôt de Données & Dashboard Exécutif

Projet de mise en place d'un entrepôt de données (Data Warehouse) sous DuckDB, alimentant un tableau de bord analytique et décisionnel sous Streamlit.



## 1. Guide d'exécution en 5 commandes

Pour initialiser, exécuter et lancer l'application complète à partir du code source :

1. **Installer les dépendances Python requises** :
   pip install -r requirements.txt


2. **Exécuter le pipeline d'ingestion et de transformation** :
   python scripts/run_pipeline.py


3. **Lancer les tests de validation de la qualité des données** :
   pytest 02_test/


4. **Générer les graphiques d'analyse** :
   python scripts/04_valeur_clients.py


5. **Lancer le Dashboard** :
   streamlit run app.py



## 2. Catalogue des Données (Data Catalog)
L'entrepôt est structuré en plusieurs schémas logiques au sein de la base DuckDB (data/boreal_warehouse.duckdb) :

**A. Schéma raw (Données Brutes)**

**raw_clients* : Données clients issues du CRM (id_client, nom, age, region, date_souscription).

**raw_contrats* : Extrait du système de gestion des contrats (id_contrat, id_client, produit, formule, canal, prime).

**raw_sinistres* : Déclarations brutes de sinistres (id_sinistre, id_contrat, garantie, date_survenance, date_declaration, montant).

**raw_reglements* & **raw_antifraude* : Tables de suivi des paiements et des signalements d'audit de fraude.

**B. Schéma prep (Données Nettoyées & Qualité)**
Tables intermédiaires de déduplication, correction du typage des dates, harmonisation des codes régionaux et validation de la complétude.

**C. Schéma dwh / core (Modèle Dimensionnel en Étoile)**

**dim_clients* : Dimension client enrichie (client_sk, id_client, region, tranche_age).

**dim_contrats* : Dimension contrat (contrat_sk, produit, formule, canal).

**dim_temps* : Dimension calendrier (temps_sk, date_complete, annee, mois, jour).

**fait_contrats* : Table de faits des contrats et primes (contrat_sk, client_sk, temps_effet_sk, prime_annuelle).

**fait_sinistres* : Table de faits des sinistres et délais (sinistre_sk, contrat_sk, client_sk, temps_survenance_sk, temps_declaration_sk, montant_indemnise, garantie).


## 3. Schéma de Lignage d'un Indicateur (Exemple : Primes & Valeur Client Pareto)
Le parcours de la donnée suit une chaîne de traçabilité stricte :

**Source (Fichiers CSV)* : Fichiers sources situés dans data/crm/, data/contrats/, data/sinistres/, data/reglements/ et data/antifraude/.

**Couche Raw (01_ingest_raw.py)* : Chargement direct dans data/boreal_warehouse.duckdb (schéma raw).

**Couche Prep (02_dedup_clients.py & 02_quality_prep.py)* : Nettoyage des doublons, typage strict et contrôles de cohérence.

**Couche Core (02_schema.py)* : Construction des dimensions (dim_clients, dim_contrats) et tables de faits (fait_contrats).

**Analyse & Graphique (04_valeur_clients.py)* : Calcul de la valeur nette par client et génération de la courbe dans graphique/pareto_valeur_clients.png.

**Restitution (app.py)* : Requêtes SQL dynamiques en temps réel alimentant les KPI et graphiques du tableau de bord Streamlit.