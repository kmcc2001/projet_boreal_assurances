import duckdb

def run_star_schema():
    db_path = "data/boreal_warehouse.duckdb"
    con = duckdb.connect(db_path)
    
    print("--- Démarrage de la Modélisation en Étoile ---")
    
    # Création du schéma DWH
    con.execute("CREATE SCHEMA IF NOT EXISTS dwh;")
    
    
    # 1. DIMENSION CLIENTS (`dim_clients`)
    
    con.execute("""
        CREATE OR REPLACE TABLE dwh.dim_clients AS
        SELECT 
            ROW_NUMBER() OVER (ORDER BY client_id) AS client_sk, -- Surrogate Key
            client_id,
            date_naissance,
            region,
            csp,
            consent_marketing,
            email_hash
        FROM prep.crm_clients_dedup;
    """)
    print("✓ Dimension dim_clients créée.")

    
    # 2. DIMENSION CONTRATS (`dim_contrats`)
    
    con.execute("""
        CREATE OR REPLACE TABLE dwh.dim_contrats AS
        SELECT 
            ROW_NUMBER() OVER (ORDER BY contrat_id) AS contrat_sk,
            contrat_id,
            produit,
            formule,
            canal,
            zone_risque
        FROM prep.contrats;
    """)
    print("✓ Dimension dim_contrats créée.")

    
    # 3. DIMENSION TEMPS (`dim_temps`)
    # Génération d'une table de dates standard de 2020 à 2030
    
    con.execute("""
        CREATE OR REPLACE TABLE dwh.dim_temps AS
        WITH dates AS (
            SELECT CAST(col AS DATE) AS date_val
            FROM generate_series(DATE '2020-01-01', DATE '2030-12-31', INTERVAL 1 DAY) t(col)
        )
        SELECT 
            CAST(strftime(date_val, '%Y%m%d') AS INTEGER) AS temps_sk,
            date_val AS date_complete,
            EXTRACT(YEAR FROM date_val) AS annee,
            EXTRACT(MONTH FROM date_val) AS mois,
            EXTRACT(DAY FROM date_val) AS jour,
            EXTRACT(QUARTER FROM date_val) AS trimestre,
            strftime(date_val, '%A') AS jour_semaine
        FROM dates;
    """)
    print("✓ Dimension dim_temps créée.")

    
    # 4. TABLE DE FAITS : CONTRATS (`fait_contrats`)
    
    con.execute("""
        CREATE OR REPLACE TABLE dwh.fait_contrats AS
        SELECT 
            c.contrat_sk,
            cl.client_sk,
            t_eff.temps_sk AS temps_effet_sk,
            t_res.temps_sk AS temps_resiliation_sk,
            ct.franchise,
            ct.bonus_malus,
            ct.puissance,
            ct.surface,
            ct.prime_annuelle
        FROM prep.contrats ct
        JOIN dwh.dim_contrats c ON ct.contrat_id = c.contrat_id
        JOIN dwh.dim_clients cl ON ct.client_id = cl.client_id
        LEFT JOIN dwh.dim_temps t_eff ON ct.date_effet = t_eff.date_complete
        LEFT JOIN dwh.dim_temps t_res ON ct.date_resiliation = t_res.date_complete;
    """)
    print("✓ Table de faits fait_contrats créée.")

    
    # 5. TABLE DE FAITS : SINISTRES (`fait_sinistres`)
    
    con.execute("""
        CREATE OR REPLACE TABLE dwh.fait_sinistres AS
        SELECT 
            s.sinistre_id,
            c.contrat_sk,
            t_surv.temps_sk AS temps_survenance_sk,
            t_decl.temps_sk AS temps_declaration_sk,
            s.garantie,
            s.statut,
            s.reserve_initiale
        FROM prep.sinistres s
        JOIN prep.contrats ct ON s.contrat_id = ct.contrat_id
        JOIN dwh.dim_contrats c ON s.contrat_id = c.contrat_id
        LEFT JOIN dwh.dim_temps t_surv ON s.date_survenance = t_surv.date_complete
        LEFT JOIN dwh.dim_temps t_decl ON s.date_declaration = t_decl.date_complete;
    """)
    print("✓ Table de faits fait_sinistres créée.")


    # 6. TABLE DE FAITS : REGLEMENTS (`fait_reglements`)
    
    con.execute("""
        CREATE OR REPLACE TABLE dwh.fait_reglements AS
        SELECT 
            r.paiement_id,
            r.sinistre_id,
            t_pai.temps_sk AS temps_paiement_sk,
            r.montant
        FROM prep.reglements r
        LEFT JOIN dwh.dim_temps t_pai ON r.date_paiement = t_pai.date_complete;
    """)
    print("✓ Table de faits fait_reglements créée.")

    # Bilan rapide
    print("\n   Bilan du Schéma en Étoile (DWH) :")
    for table in ['dim_clients', 'dim_contrats', 'dim_temps', 'fait_contrats', 'fait_sinistres', 'fait_reglements']:
        cnt = con.execute(f"SELECT COUNT(*) FROM dwh.{table};").fetchone()[0]
        print(f"• dwh.{table} : {cnt} lignes")

    con.close()
    print("--- Modélisation en Étoile terminée avec succès ---")

if __name__ == "__main__":
    run_star_schema()