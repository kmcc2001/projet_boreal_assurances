import os
import glob
import duckdb

def run_ingestion():
    db_path = "data/boreal_warehouse.duckdb"
    # S'assure que le dossier data existe
    os.makedirs("data", exist_ok=True)
    
    con = duckdb.connect(db_path)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    
    base_path = "data"
    
    print("--- Ingestion de la couche BRUTE (Raw) ---")
    
    # 1. CRM
    crm_path = os.path.join(base_path, "crm", "clients.csv")
    if os.path.exists(crm_path):
        con.execute(f"""
            CREATE OR REPLACE TABLE raw.crm_clients AS
            SELECT *, CURRENT_TIMESTAMP AS _loaded_at, 'clients.csv' AS _source_file
            FROM read_csv_auto('{crm_path}', delim=';', encoding='latin-1', header=True);
        """)
        print("CRM clients ingéré")
    else:
        print(f"Fichier introuvable : {crm_path}")

    # 2. Contrats
    contrat_path = os.path.join(base_path, "contrats", "contrats.csv")
    if os.path.exists(contrat_path):
        con.execute(f"""
            CREATE OR REPLACE TABLE raw.contrats AS
            SELECT *, CURRENT_TIMESTAMP AS _loaded_at, 'contrats.csv' AS _source_file
            FROM read_csv_auto('{contrat_path}', delim=',', encoding='utf-8', header=True);
        """)
        print("Contrats ingérés")
    else:
        print(f"Fichier introuvable : {contrat_path}")

    # 3. Sinistres
    sinistre_path = os.path.join(base_path, "sinistres", "sinistres.jsonl")
    if os.path.exists(sinistre_path):
        con.execute(f"""
            CREATE OR REPLACE TABLE raw.sinistres AS
            SELECT *, CURRENT_TIMESTAMP AS _loaded_at, 'sinistres.jsonl' AS _source_file
            FROM read_json_auto('{sinistre_path}');
        """)
        print("Sinistres ingérés")
    else:
        print(f"Fichier introuvable : {sinistre_path}")

    # 4. Antifraude
    audit_path = os.path.join(base_path, "antifraude", "audits.csv")
    if os.path.exists(audit_path):
        con.execute(f"""
            CREATE OR REPLACE TABLE raw.antifraude_audits AS
            SELECT *, CURRENT_TIMESTAMP AS _loaded_at, 'audits.csv' AS _source_file
            FROM read_csv_auto('{audit_path}', header=True);
        """)
        print("Audits antifraude ingérés")
    else:
        print(f"Fichier introuvable : {audit_path}")

    # 5. Règlements
    reglement_pattern = os.path.join(base_path, "reglements", "reglements_*.csv")
    reglement_files = glob.glob(reglement_pattern)
    
    if reglement_files:
        # Utilisation de read_csv_auto avec le pattern global et union_by_name pour éviter les erreurs de position
        con.execute(f"""
            CREATE OR REPLACE TABLE raw.reglements AS
            SELECT *, 
                   CURRENT_TIMESTAMP AS _loaded_at, 
                   filename AS _source_file
            FROM read_csv_auto('{reglement_pattern}', union_by_name=true, filename=true, header=True);
        """)
        print(f"{len(reglement_files)} fichiers de règlements mensuels ingérés avec succès.")
    else:
        print(f"Aucun fichier de règlement trouvé avec le pattern : {reglement_pattern}")

    con.close()
    print("--- Ingestion brute terminée avec succès ---")

if __name__ == "__main__":
    run_ingestion()