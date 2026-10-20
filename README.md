# Projet Boréal Assurances - Data Engineering & Data Analyse

## Livrable 1 : Architecture et Ingestion

### 1. Schéma de l'Architecture Cible (End-to-End)
Le pipeline de données est structuré en couches successives pour garantir la traçabilité, la reproductibilité et la qualité :

[ Sources (CSV, JSONL, 64x CSV) ]
│
▼
[ Couche 1 : Brut / Raw ] ── (Copie conforme + métadonnées d'ingestion)
│
▼
[ Couche 2 : Préparation / Staging ] ── (Typage, nettoyage, quarantaine)
│
▼
[ Couche 3 : Cœur / Core ] ── (Schéma en étoile, déduplication, historique)
│
▼
[ Couche 4 : Marts ] ── (Agrégations métiers : S/P, exposition, cohortes)
│
▼
[ Couche 5 : Restitution ] ── (Dashboard Streamlit + Note exécutive)

### 2. Justification des Choix Techniques
* **Stockage & Moteur SQL (DuckDB)** : Choisi pour sa rapidité d'exécution sur des volumes de l'ordre de ~30k lignes, son format fichier unique (zéro coût d'infrastructure cloud) et sa portabilité totale dans le dépôt Git.

* **Orchestration & Pipeline (Python 3.10+)** : Permet une modularité complète des scripts d'ingestion, de transformation et de tests, facilement exécutables via un terminal ou un Makefile.

### 3. Passage à l'Échelle (x100 de données)
Si le volume de données passait de ~1 Go à 100 Go+ :
* Migration du moteur local DuckDB vers un Data Warehouse cloud distribué (**Snowflake** ou **BigQuery**).

* Remplacement des scripts d'ingestion locaux par un orchestrateur robuste type **Apache Airflow** ou **Prefect** et un framework de transformation ELT comme **dbt**.

* Mise en place d'un partitionnement par date sur les tables de faits (règlements et sinistres).

### 4. Chargement Incrémental & Idempotence
Le pipeline intègre une journalisation des exécutions (`ingestion_log`) et un chargement incrémental idempotent basé sur des clauses `NOT EXISTS`. Un test automatisé garantit que le re-jeu d'un mois de données ne génère strictement aucun doublon dans la base cible.