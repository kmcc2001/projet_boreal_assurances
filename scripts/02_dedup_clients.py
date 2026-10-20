import duckdb

def run_crm_dedup():
    db_path = "data/boreal_warehouse.duckdb"
    con = duckdb.connect(db_path)
    
    print("--- Démarrage de la Déduplication CRM & Règles de Survie ---")
    
    # Création d'une table clients dédupliquée dans le schéma prep
    con.execute("""
        CREATE OR REPLACE TABLE prep.crm_clients_dedup AS
        WITH ranked_clients AS (
            SELECT 
                client_id,
                date_naissance,
                region,
                csp,
                consent_marketing,
                email_hash,
                ROW_NUMBER() OVER (
                    PARTITION BY email_hash 
                    -- Règle de survie : On privilégie le consentement TRUE, puis l'ID client le plus récent/élevé
                    ORDER BY consent_marketing DESC, client_id DESC
                ) as rn
            FROM prep.crm_clients
            WHERE email_hash IS NOT NULL AND TRIM(email_hash) != ''
        )
        SELECT 
            client_id,
            date_naissance,
            region,
            csp,
            consent_marketing,
            email_hash
        FROM ranked_clients
        WHERE rn = 1;
    """)
    
    # Statistiques de déduplication
    initial_count = con.execute("SELECT COUNT(*) FROM prep.crm_clients;").fetchone()[0]
    final_count = con.execute("SELECT COUNT(*) FROM prep.crm_clients_dedup;").fetchone()[0]
    duplicates_removed = initial_count - final_count
    
    print(f"\nBilan de la déduplication CRM :")
    print(f"Nombre initial de clients (prep) : {initial_count}")
    print(f"Nombre après déduplication : {final_count}")
    print(f"Doublons fusionnés/écartés : {duplicates_removed}")
    
    con.close()
    print("--- Déduplication terminée avec succès ---")

if __name__ == "__main__":
    run_crm_dedup()