import os

def generate_full_html_report():
    output_path = "KAYA-MAXIME_Boreal.html"
    
    html_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport d'Architecture & Analytics — Boréal Assurances</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #1E293B; background-color: #F8FAFC; margin: 0; padding: 0; }
        .container { max-width: 1100px; margin: 0 auto; background: #FFFFFF; padding: 50px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        
        /* Couverture */
        .cover-page { background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%); color: #FFFFFF; padding: 80px 50px; text-align: center; margin: -50px -50px 50px -50px; display: flex; flex-direction: column; justify-content: center; min-height: 550px; }
        .cover-page h1 { font-size: 38px; color: #FFFFFF; border-bottom: none; margin-bottom: 15px; letter-spacing: 1px; }
        .cover-page h2 { font-size: 20px; color: #60A5FA; border-bottom: none; margin-top: 0; margin-bottom: 40px; }
        .cover-page p { color: #CBD5E1; font-size: 15px; margin: 5px 0; }
        .cover-meta { margin-top: 60px; font-size: 14px; color: #94A3B8; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 20px; }

        h1, h2, h3 { color: #0F172A; font-weight: 700; }
        h1 { font-size: 26px; border-bottom: 3px solid #2563EB; padding-bottom: 10px; margin-bottom: 20px; }
        h2 { font-size: 18px; color: #2563EB; margin-top: 30px; border-bottom: 1px solid #E2E8F0; padding-bottom: 6px; }
        h3 { font-size: 15px; color: #0F172A; margin-top: 20px; }
        p, li { font-size: 13.5px; color: #334155; }
        
        .page-header { background: #0F172A; color: #FFFFFF; padding: 20px 30px; margin: -50px -50px 30px -50px; }
        .page-header h1 { color: #FFFFFF; border-bottom: none; margin: 0; font-size: 20px; }
        .page-header p { color: #94A3B8; margin: 3px 0 0 0; font-size: 12px; }
        
        .box { background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #2563EB; padding: 15px 20px; margin: 15px 0; border-radius: 0 6px 6px 0; }
        .box-alert { background: #FFF5F5; border: 1px solid #FED7D7; border-left: 4px solid #EF4444; padding: 15px 20px; margin: 15px 0; border-radius: 0 6px 6px 0; }
        
        .terminal { background: #0F172A; color: #38BDF8; font-family: 'Consolas', monospace; padding: 15px; border-radius: 6px; font-size: 12px; overflow-x: auto; margin: 15px 0; white-space: pre; }
        .sql { background: #1E293B; color: #F1F5F9; font-family: 'Consolas', monospace; padding: 15px; border-radius: 6px; font-size: 12px; overflow-x: auto; margin: 15px 0; white-space: pre; }
        
        table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 13px; background: #FFFFFF; }
        th, td { border: 1px solid #E2E8F0; padding: 10px 12px; text-align: left; vertical-align: middle; }
        th { background: #F1F5F9; color: #0F172A; font-weight: 600; font-size: 11px; text-transform: uppercase; }
        .text-right { text-align: right; }
        
        .badge { display: inline-block; padding: 3px 7px; font-size: 10.5px; font-weight: 600; border-radius: 4px; color: #FFF; }
        .badge-danger { background: #EF4444; }
        .badge-success { background: #10B981; }
        .badge-warning { background: #F59E0B; }
        
        .page-break { page-break-after: always; margin-bottom: 40px; border-bottom: 2px dashed #CBD5E1; padding-bottom: 20px; }
    </style>
</head>
<body>

<div class="container">

    <!-- PAGE DE COUVERTURE -->
    <div class="cover-page">
        <h1>BORÉAL ASSURANCES</h1>
        <h2>LIVRABLE 5 : PROJET INTÉGRATEUR DATAWAREHOUSE & DASHBOARD</h2>
        <p>Rapport d'Architecture, Pipeline ETL, Modélisation & Analytics Avancées</p>
        <div class="cover-meta">
            <p><strong>Auteurs :</strong> KAYA MAXIME Christe Celina (Master M2 Data Analytics)</p>
            <p><strong>Date :</strong>23 Octobre 2026</p>
        </div>
    </div>

    <div class="page-break"></div>

    <!-- SOMMAIRE DÉTAILLÉ -->
    <div class="page-header">
        <h1>SOMMAIRE GÉNÉRAL DU RAPPORT</h1>
        <p>Structure analytique et technique du projet</p>
    </div>
    <table>
        <tr><th>Section</th><th>Intitulé du Chapitre</th></tr>
        <tr><td><strong>Section 1</strong></td><td>Cadre Stratégique & Architecture Data (Modèle Médaillon)</td></tr>
        <tr><td><strong>Section 2</strong></td><td>Qualité des Données & Mécanisme de Quarantaine (R01-R15)</td></tr>
        <tr><td><strong>Section 3</strong></td><td>Modélisation Dimensionnelle en Étoile (DWH DuckDB)</td></tr>
        <tr><td><strong>Section 4</strong></td><td>Analyses Avancées, Valeur Client (CLV) & Ratios S/P</td></tr>
        <tr><td><strong>Section 5</strong></td><td>Performance Opérationnelle, Délais (P90) & Dashboard Streamlit</td></tr>
    </table>

    <div class="page-break"></div>

    <!-- SECTION 1 -->
    <div class="page-header">
        <h1>SECTION 1 : CADRE STRATÉGIQUE & ARCHITECTURE DATA</h1>
        <p>Contexte métier et choix technologiques de l'entrepôt</p>
    </div>
    <h2>1.1 Contexte et Enjeux Métier</h2>
    <p>Boréal Assurances fait face à un besoin critique de modernisation de son système d'information décisionnel. L'éclatement des sources de données (CRM, fichiers plats de contrats, historiques de sinistres et 64 flux mensuels de règlements) rendait le pilotage de la rentabilité difficile. Le projet implémente un pipeline de données de bout en bout hautement performant.</p>
    
    <h2>1.2 Justification des Choix Technologiques</h2>
    <ul>
        <li><strong>DuckDB :</strong> Choisi pour sa capacité à traiter des requêtes analytiques massives en mémoire sans la lourdeur d'un cluster Spark ou Snowflake, garantissant des temps de réponse inférieurs à 100ms.</li>
        <li><strong>Python & Pandas :</strong> Orchestration des scripts d'ingestion et transformation.</li>
        <li><strong>Streamlit :</strong> Restitution interactive multi-pages à destination de la direction financière et des gestionnaires.</li>
    </ul>

    <h3>💻 Sortie Terminal — Initialisation du Pipeline</h3>
    <div class="terminal">
[INFO] Connexion à l'instance DuckDB : boreal.duckdb établie.
[INFO] Vérification des répertoires RAW, PREP et DWH... OK.
[INFO] Prêt pour l'ingestion des flux multi-sources.
    </div>

    <div class="page-break"></div>

    <!-- SECTION 2 -->
    <div class="page-header">
        <h1>SECTION 2 : QUALITÉ DES DONNÉES & QUARANTAINE</h1>
        <p>Implémentation des règles de gestion R01 à R15</p>
    </div>
    <h2>2.1 Catalogue des Règles de Contrôle Qualité</h2>
    <p>Le pipeline applique 15 règles de validation rigoureuses lors du passage de la couche RAW vers la couche PREP :</p>
    <table>
        <tr><th>Règle</th><th>Périmètre</th><th>Description du Contrôle</th><th>Impact Technique</th></tr>
        <tr><td><strong>R01 - R04</strong></td><td>Clients / CRM</td><td>Validation format e-mail, code postal et unicité ID client.</td><td>Isolation si corrompu</td></tr>
        <tr><td><strong>R05 - R09</strong></td><td>Contrats & Primes</td><td>Vérification que Prime > 0 € et dates de souscription valides.</td><td>Isolation si Prime <= 0</td></tr>
        <tr><td><strong>R10 - R15</strong></td><td>Sinistres & Règlements</td><td>Intégrité référentielle et cohérence chronologique des règlements.</td><td>Isolation si orphelin</td></tr>
    </table>

    <h2>2.2 Bilan des Rejets (Table de Quarantaine)</h2>
    <p>Sur l'ensemble du volume traité lors du dernier run, <strong>87 enregistrements non conformes</strong> ont été isolés dans la table <code>prep.quarantaine</code> :</p>
    <table>
        <tr><th>Code Règle</th><th>Libellé de l'Anomalie</th><th class="text-right">Rejets</th><th>Action Corrective</th></tr>
        <tr><td><strong>R05</strong></td><td>Prime nette négative ou nulle</td><td class="text-right">25</td><td>Vérification tarifaire source</td></tr>
        <tr><td><strong>R15</strong></td><td>Règlement sans sinistre rattaché</td><td class="text-right">22</td><td>Rapprochement manuel ID</td></tr>
        <tr><td><strong>R06</strong></td><td>Date de survenance > Date déclaration</td><td class="text-right">20</td><td>Inversion de saisie corrigée</td></tr>
        <tr><td><strong>R10</strong></td><td>Champs obligatoires manquants (Null)</td><td class="text-right">20</td><td>Alerte administrateur CRM</td></tr>
    </table>

    <div class="page-break"></div>

    <!-- SECTION 3 -->
    <div class="page-break"></div>

    <!-- SECTION 4 -->
    <div class="page-header">
        <h1>SECTION 4 : ANALYSES AVANCÉES & VALEUR CLIENT</h1>
        <p>Modélisation financière, Pareto et segmentation S/P</p>
    </div>
    <h2>4.1 Analyse du Ratio S/P par Tranche d'Âge</h2>
    <table>
        <tr><th>Tranche d'Âge</th><th class="text-right">Contrats</th><th class="text-right">Primes (€)</th><th class="text-right">Sinistres (€)</th><th class="text-right">Ratio S/P (%)</th></tr>
        <tr><td>Moins de 25 ans</td><td class="text-right">1 277</td><td class="text-right">732 949 €</td><td class="text-right">2 054 642 €</td><td class="text-right">280.33%</td></tr>
        <tr><td>25 - 35 ans</td><td class="text-right">2 850</td><td class="text-right">1 258 354 €</td><td class="text-right">2 699 638 €</td><td class="text-right">214.54%</td></tr>
        <tr style="background:#FFF5F5; font-weight:bold;"><td>36 - 50 ans (Pic)</td><td class="text-right">7 201</td><td class="text-right">3 051 910 €</td><td class="text-right">14 339 424 €</td><td class="text-right"><span class="badge badge-danger">469.85%</span></td></tr>
        <tr><td>51 - 64 ans</td><td class="text-right">5 891</td><td class="text-right">2 530 505 €</td><td class="text-right">6 782 207 €</td><td class="text-right">268.02%</td></tr>
        <tr><td>65 ans et plus</td><td class="text-right">2 890</td><td class="text-right">1 281 875 €</td><td class="text-right">3 614 447 €</td><td class="text-right">281.97%</td></tr>
    </table>

    <div class="box-alert">
        <h3>🚨 Enseignement Clé</h3>
        <p>Le ratio global s'établit à <strong>333.0%</strong>. Le segment des 36-50 ans concentre le risque principal avec un ratio frôlant les 470%, nécessitant une refonte tarifaire ciblée.</p>
    </div>

    <div class="page-break"></div>

    <!-- SECTION 5 -->
    <div class="page-header">
        <h1>SECTION 5 : PERFORMANCE OPÉRATIONNELLE & DÉLAIS</h1>
        <p>Analyse des goulots d'étranglement P90 et plan d'action</p>
    </div>
    <h2>5.1 Délais de Gestion (Médiane vs P90)</h2>
    <table>
        <tr><th>Garantie</th><th class="text-right">Sinistres</th><th class="text-right">Médiane (Jours)</th><th class="text-right">P90 (Jours)</th><th>Diagnostic & Risque</th></tr>
        <tr><td>Tempête</td><td class="text-right">233</td><td class="text-right">4 j</td><td class="text-right">16.8 j</td><td>Traitement rapide et fluide</td></tr>
        <tr><td>Collision</td><td class="text-right">692</td><td class="text-right">5 j</td><td class="text-right">20.0 j</td><td>Délai standard garages</td></tr>
        <tr><td>Dégât des Eaux</td><td class="text-right">589</td><td class="text-right">5 j</td><td class="text-right">19.2 j</td><td>Flux maîtrisé</td></tr>
        <tr style="background:#FFF5F5;"><td>Incendie</td><td class="text-right">108</td><td class="text-right">6 j</td><td class="text-right"><span class="badge badge-danger">23.0 j</span></td><td>Goulot d'expertise lourd</td></tr>
        <tr style="background:#FFF5F5;"><td>Vol</td><td class="text-right">386</td><td class="text-right">5 j</td><td class="text-right"><span class="badge badge-danger">25.0 j</span></td><td>Goulot critique d'enquête</td></tr>
    </table>

    <h2>5.2 Recommandations Stratégiques Finales</h2>
    <div class="box">
        <ol>
            <li><strong>Réalignement Tarifaire :</strong> Corriger immédiatement les classes tarifaires sur la tranche 36-50 ans.</li>
            <li><strong>Automatisation Vol / Incendie :</strong> Dématérialiser les rapports d'expertise pour abaisser le P90 de 25 à 15 jours.</li>
            <li><strong>Rétention VIP :</strong> Lancer un plan de fidélisation sur le Top 10% des souscripteurs (générant 20.5% de la valeur nette).</li>
        </ol>
    </div>

</div>

</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[SUCCÈS] Rapport complet généré : {output_path}")

if __name__ == "__main__":
    generate_full_html_report()