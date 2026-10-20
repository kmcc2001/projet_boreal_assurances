import duckdb
import time
from datetime import datetime

def run_incremental_load():
    db_path = "data/boreal_warehouse.duckdb"
    con = duckdb.connect(db_path)
    
    print("--- Démarrage du chargement incrémental et test d'idempotence ---")
    
    # 1. Création des schémas et tables
    con.execute("CREATE SCHEMA IF NOT EXISTS core;")
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    
    # Table du journal d'ingestion
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw.ingestion_log (
            execution_id VARCHAR,
            file_pattern VARCHAR,
            records_read INT,
            records_inserted INT,
            execution_start TIMESTAMP,
            execution_duration_sec DOUBLE,
            status VARCHAR
        );
    """)
    
    # Table core.reglements
    con.execute("""
        CREATE TABLE IF NOT EXISTS core.reglements (
            paiement_id VARCHAR PRIMARY KEY,
            sinistre_id VARCHAR,
            date_paiement DATE,
            montant DOUBLE
        );
    """)
    
    start_time = time.time()
    exec_start = datetime.now()
    exec_id = f"EXEC_{int(start_time)}"
    
    # Nombre de lignes lues dans raw
    records_read = con.execute("SELECT COUNT(*) FROM raw.reglements;").fetchone()[0]
    count_before = con.execute("SELECT COUNT(*) FROM core.reglements;").fetchone()[0]
    
    # Insertion incrémentale
    con.execute("""
        INSERT INTO core.reglements (paiement_id, sinistre_id, date_paiement, montant)
        SELECT 
            paiement_id, 
            sinistre_id, 
            CAST(date_paiement AS DATE), 
            CAST(montant AS DOUBLE)
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY paiement_id ORDER BY _loaded_at DESC) as rn
            FROM raw.reglements
            WHERE paiement_id IS NOT NULL
        ) sub
        WHERE rn = 1
          AND NOT EXISTS (
              SELECT 1 
              FROM core.reglements r 
              WHERE r.paiement_id = sub.paiement_id
          );
    """)
    
    count_after = con.execute("SELECT COUNT(*) FROM core.reglements;").fetchone()[0]
    inserted_rows = count_after - count_before
    duration = time.time() - start_time
    
    # Enregistrement dans le journal d'ingestion
    con.execute(f"""
        INSERT INTO raw.ingestion_log VALUES (
            '{exec_id}',
            'reglements_*.csv',
            {records_read},
            {inserted_rows},
            '{exec_start}',
            {round(duration, 4)},
            'SUCCESS'
        );
    """)
    
    print(f" Journal d'ingestion mis à jour dans raw.ingestion_log.")
    print(f"✓ {inserted_rows} nouvelles lignes insérées dans core.reglements.")
    
    # --- TEST D'IDEMPOTENCE (Second passage) ---
    print("\n--- Test d'idempotence : Re-jeu du chargement ---")
    
    start_time_replay = time.time()
    exec_start_replay = datetime.now()
    
    con.execute("""
        INSERT INTO core.reglements (paiement_id, sinistre_id, date_paiement, montant)
        SELECT 
            paiement_id, 
            sinistre_id, 
            CAST(date_paiement AS DATE), 
            CAST(montant AS DOUBLE)
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY paiement_id ORDER BY _loaded_at DESC) as rn
            FROM raw.reglements
            WHERE paiement_id IS NOT NULL
        ) sub
        WHERE rn = 1
          AND NOT EXISTS (
              SELECT 1 
              FROM core.reglements r 
              WHERE r.paiement_id = sub.paiement_id
          );
    """)
    
    count_final = con.execute("SELECT COUNT(*) FROM core.reglements;").fetchone()[0]
    replay_inserted = count_final - count_after
    duration_replay = time.time() - start_time_replay
    
    # Enregistrement du second passage dans le journal
    con.execute(f"""
        INSERT INTO raw.ingestion_log VALUES (
            '{exec_id}_REPLAY',
            'reglements_*.csv',
            {records_read},
            {replay_inserted},
            '{exec_start_replay}',
            {round(duration_replay, 4)},
            'SUCCESS_REPLAY'
        );
    """)
    
    if count_final == count_after:
        print(" SUCCESS : Le test d'idempotence est validé ! Zéro doublon créé lors du re-jeu.")
    else:
        print(" ERREUR : Des doublons ont été créés.")

    con.close()

if __name__ == "__main__":
    run_incremental_load()