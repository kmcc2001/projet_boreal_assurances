import duckdb

def run_quality_prep():
    db_path = "data/boreal_warehouse.duckdb"
    con = duckdb.connect(db_path)
    
    print("--- Démarrage des Contrôles Qualité et Quarantaine ---")
    
    # 1. Création des schémas
    con.execute("CREATE SCHEMA IF NOT EXISTS prep;")
    con.execute("CREATE SCHEMA IF NOT EXISTS quarantine;")
    
    # Table unique de Quarantaine
    con.execute("""
        CREATE TABLE IF NOT EXISTS quarantine.rejected_records (
            rule_id VARCHAR,
            rule_description VARCHAR,
            source_table VARCHAR,
            record_id VARCHAR,
            rejected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            rejection_reason VARCHAR,
            raw_data VARCHAR
        );
    """)
    
    con.execute("DELETE FROM quarantine.rejected_records;")

    
    # REGLES 1 à 3 : CRM CLIENTS
    
    con.execute("""
        INSERT INTO quarantine.rejected_records (rule_id, rule_description, source_table, record_id, rejection_reason, raw_data)
        SELECT 
            'R01_CRM_ID_NULL', 'ID client nul ou vide', 'raw.crm_clients', CAST(client_id AS VARCHAR),
            'client_id IS NULL', TO_JSON(t)
        FROM raw.crm_clients t
        WHERE client_id IS NULL;
    """)

    con.execute("""
        CREATE OR REPLACE TABLE prep.crm_clients AS
        SELECT 
            CAST(client_id AS VARCHAR) AS client_id,
            CAST(date_naissance AS DATE) AS date_naissance,
            region,
            csp,
            consent_marketing,
            email_hash
        FROM raw.crm_clients
        WHERE client_id IS NOT NULL;
    """)

    
    # REGLES 4 à 9 : CONTRATS
    
    con.execute("""
        INSERT INTO quarantine.rejected_records (rule_id, rule_description, source_table, record_id, rejection_reason, raw_data)
        SELECT 
            'R05_CONTRAT_PRIME_INVALIDE', 'Prime annuelle <= 0', 'raw.contrats', CAST(contrat_id AS VARCHAR),
            'prime_annuelle <= 0', TO_JSON(t)
        FROM raw.contrats t
        WHERE prime_annuelle <= 0;
    """)

    con.execute("""
        INSERT INTO quarantine.rejected_records (rule_id, rule_description, source_table, record_id, rejection_reason, raw_data)
        SELECT 
            'R06_CONTRAT_DATES_INCOHERENTES', 'Date resiliation < Date effet', 'raw.contrats', CAST(contrat_id AS VARCHAR),
            'date_resiliation < date_effet', TO_JSON(t)
        FROM raw.contrats t
        WHERE date_resiliation IS NOT NULL AND date_resiliation < date_effet;
    """)

    con.execute("""
        INSERT INTO quarantine.rejected_records (rule_id, rule_description, source_table, record_id, rejection_reason, raw_data)
        SELECT 
            'R07_CONTRAT_PRODUIT_INCONNU', 'Produit autre que auto/habitation', 'raw.contrats', CAST(contrat_id AS VARCHAR),
            'produit NOT IN (auto, habitation)', TO_JSON(t)
        FROM raw.contrats t
        WHERE LOWER(TRIM(produit)) NOT IN ('auto', 'habitation');
    """)

    con.execute("""
        CREATE OR REPLACE TABLE prep.contrats AS
        SELECT 
            CAST(contrat_id AS VARCHAR) AS contrat_id,
            CAST(client_id AS VARCHAR) AS client_id,
            LOWER(TRIM(produit)) AS produit,
            CAST(date_effet AS DATE) AS date_effet,
            CAST(date_resiliation AS DATE) AS date_resiliation,
            formule,
            canal_distribution AS canal,
            zone_risque,
            franchise,
            bonus_malus,
            puissance_cv AS puissance,
            surface_m2 AS surface,
            prime_annuelle
        FROM raw.contrats
        WHERE prime_annuelle > 0
          AND (date_resiliation IS NULL OR date_resiliation >= date_effet)
          AND LOWER(TRIM(produit)) IN ('auto', 'habitation');
    """)

    
    # REGLES 10 à 13 : SINISTRES
    
    con.execute("""
        INSERT INTO quarantine.rejected_records (rule_id, rule_description, source_table, record_id, rejection_reason, raw_data)
        SELECT 
            'R10_SINISTRE_DATES_INCOHERENTES', 'Date declaration < Date survenance', 'raw.sinistres', CAST(sinistre_id AS VARCHAR),
            'date_declaration < date_survenance', TO_JSON(t)
        FROM raw.sinistres t
        WHERE date_declaration < date_survenance;
    """)

    con.execute("""
        INSERT INTO quarantine.rejected_records (rule_id, rule_description, source_table, record_id, rejection_reason, raw_data)
        SELECT 
            'R11_SINISTRE_CONTRAT_ORPHELIN', 'Contrat inexistant dans prep.contrats', 'raw.sinistres', CAST(sinistre_id AS VARCHAR),
            'contrat_id non trouve', TO_JSON(t)
        FROM raw.sinistres t
        WHERE CAST(contrat_id AS VARCHAR) NOT IN (SELECT contrat_id FROM prep.contrats);
    """)

    con.execute("""
        CREATE OR REPLACE TABLE prep.sinistres AS
        SELECT 
            CAST(sinistre_id AS VARCHAR) AS sinistre_id,
            CAST(contrat_id AS VARCHAR) AS contrat_id,
            CAST(date_survenance AS DATE) AS date_survenance,
            CAST(date_declaration AS DATE) AS date_declaration,
            garantie,
            statut,
            reserve_initiale
        FROM raw.sinistres
        WHERE date_declaration >= date_survenance
          AND CAST(contrat_id AS VARCHAR) IN (SELECT contrat_id FROM prep.contrats);
    """)

    
    # REGLES 14 et 15 : REGLEMENTS
    
    con.execute("""
        INSERT INTO quarantine.rejected_records (rule_id, rule_description, source_table, record_id, rejection_reason, raw_data)
        SELECT 
            'R14_REGLEMENT_MONTANT_INVALIDE', 'Montant de règlement <= 0', 'raw.reglements', CAST(paiement_id AS VARCHAR),
            'montant <= 0', TO_JSON(t)
        FROM raw.reglements t
        WHERE montant <= 0;
    """)

    con.execute("""
        INSERT INTO quarantine.rejected_records (rule_id, rule_description, source_table, record_id, rejection_reason, raw_data)
        SELECT 
            'R15_REGLEMENT_SINISTRE_ORPHELIN', 'Sinistre inexistant dans prep.sinistres', 'raw.reglements', CAST(paiement_id AS VARCHAR),
            'sinistre_id non trouve', TO_JSON(t)
        FROM raw.reglements t
        WHERE CAST(sinistre_id AS VARCHAR) NOT IN (SELECT sinistre_id FROM prep.sinistres);
    """)

    con.execute("""
        CREATE OR REPLACE TABLE prep.reglements AS
        SELECT 
            CAST(paiement_id AS VARCHAR) AS paiement_id,
            CAST(sinistre_id AS VARCHAR) AS sinistre_id,
            CAST(date_paiement AS DATE) AS date_paiement,
            montant
        FROM raw.reglements
        WHERE montant > 0
          AND CAST(sinistre_id AS VARCHAR) IN (SELECT sinistre_id FROM prep.sinistres);
    """)

    # Bilan de la quarantaine
    quarantine_summary = con.execute("""
        SELECT rule_id, rule_description, COUNT(*) AS nb_rejets 
        FROM quarantine.rejected_records 
        GROUP BY rule_id, rule_description
        ORDER BY nb_rejets DESC;
    """).fetchall()

    print("\n--- Bilan de la Quarantaine par Règle ---")
    if quarantine_summary:
        for rule_id, desc, count in quarantine_summary:
            print(f"• [{rule_id}] {desc} : {count} ligne(s) écartée(s)")
    else:
        print("✓ Aucun rejet détecté sur ces contrôles.")

    total_quarantine = con.execute("SELECT COUNT(*) FROM quarantine.rejected_records;").fetchone()[0]
    print(f"\n Total de lignes placées en quarantaine : {total_quarantine}")

    con.close()
    print("--- Phase de contrôles et quarantaine terminée avec succès ---")

if __name__ == "__main__":
    run_quality_prep()