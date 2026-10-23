# NOTE EXÉCUTIVE & GOUVERNANCE DES DONNÉES

**Projet :** Boreal Assurances — Entrepôt de Données & Pilotage Analytique  
**Destinataires :** Camille Roux — Directrice technique  


## 1. Synthèse Décisionnelle

### A. Constats Chiffrés
1. **Concentration du Portefeuille :** L'analyse de Pareto révèle que **20 % des clients génèrent près de 80 % de la valeur nette**, mettant en évidence une forte dépendance à une frange haut de gamme de la clientèle.
2. **Sinistralité et Rentabilité :** Le ratio Sinistres / Primes global s'établit à **68,4 %**, mais présente des disparités critiques selon les garanties et les canaux de souscription, baissant la marge technique sur certains segments.
3. **Délais de Traitement :** La médiane des délais de déclaration et de gestion des sinistres présente des temps de latence variables selon les régions, impactant directement la satisfaction client et l'exposition au risque de fraude.

### B. Décisions Proposées
1. **Optimisation de la Rétention :** Mettre en place des campagnes de fidélisation ciblées et automatisées pour le top 20 % des clients identifiés par l'analyse de Pareto afin de réduire le taux de churn.
2. **Ajustement Tarifaire Technique :** Réviser la politique de souscription et les tarifs des garanties déficitaires identifiées sur le dashboard pour ramener le ratio S/P sous le seuil d'équilibre cible (< 65 %).
3. **Automatisation et Suivi des Flux :** Inciter à l'utilisation du tableau de bord pour les comités de pilotage mensuels afin d'accélérer les prises de décision opérationnelles.

### C. Limites du Modèle
* **Profondeur historique :** Les analyses s'appuient sur un périmètre de données figé, limitant l'anticipation des tendances macroéconomiques saisonnières à long terme.
* **Granularité des données comportementales :** L'absence de données comportementales fines (ex: interactions web détaillées) restreint la puissance prédictive des modèles de risque.



## 2. Gouvernance & Conformité RGPD

### A. Identification des Données Personnelles (PII)
L'entrepôt traite des données à caractère personnel issues du CRM et des contrats :
* **Données d'identification :** Nom, prénom, identifiant client (`id_client`).
* **Données démographiques :** Âge, région, code postal.
* **Données contractuelles et financières :** Primes, sinistres déclarés, montants indemnisés.

### B. Pseudonymisation et Sécurité
* **Cloisonnement des couches :** Les données brutes nominatives sont isolées dans le schéma `raw`.
* **Masquage technique :** Les couches analytiques (`prep` et `dwh`/`core`) utilisent des clés de substitution techniques (`client_sk`, `contrat_sk`) et ne conservent que les attributs strictement nécessaires aux analyses (ex: tranches d'âge, régions), dissociant l'identité directe des faits mesurés.

### C. Durées de Conservation
Conformément aux recommandations de la CNIL et aux obligations légales en matière d'assurance :
* **Couche `raw` (Données brutes) :** Rétention active limitée à la durée de la relation contractuelle augmentée de 5 ans (prescription civile).
* **Couche `dwh` (Agrégats et faits historiques) :** Conservation à des fins statistiques et prudentielles anonymisées pour une durée maximale de 10 ans.

### D. Gestion du Droit à l'Effacement
* **Procédure technique :** En cas de demande de suppression, un script de purge cible l'identifiant client dans la table source `raw_clients`, cascade la suppression ou l'anonymisation des champs nominatifs, et actualise les tables de dimensions lors de la prochaine exécution du pipeline d'ingestion.