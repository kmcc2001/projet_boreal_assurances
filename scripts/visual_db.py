import duckdb

def inspecter_dwh():
    db_path = "data/boreal_warehouse.duckdb"
    con = duckdb.connect(db_path)
    
    print("--- COLONNES DU SCHÉMA DWH (FAITS ET DIMENSIONS) ---\n")
    
    tables_dwh = [
        "dwh.dim_clients", 
        "dwh.dim_contrats", 
        "dwh.dim_temps", 
        "dwh.fait_contrats", 
        "dwh.fait_sinistres"
    ]
    
    for table in tables_dwh:
        print(f"Table : {table}")
        try:
            colonnes = con.execute(f"PRAGMA table_info('{table}');").fetchall()
            for col in colonnes:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"   - {col_name} ({col_type})")
        except Exception as e:
            print(f"   Erreur : {e}")
        print("-" * 40)
        
    con.close()
    
    
def inspecter_reglements():
    db_path = "data/boreal_warehouse.duckdb"
    con = duckdb.connect(db_path)
    
    print("--- COLONNES DES RÈGLEMENTS ET VUES ---")
    
    tables_cibles = [
        "dwh.fait_reglements", 
        "dwh.v_sinistres_par_contrat"
    ]
    
    for table in tables_cibles:
        print(f"\n Table/Vue : {table}")
        try:
            colonnes = con.execute(f"PRAGMA table_info('{table}');").fetchall()
            for col in colonnes:
                print(f"   - {col[1]} ({col[2]})")
        except Exception as e:
            # Si c'est une vue, PRAGMA table_info peut échouer, on utilise DESCRIBE
            try:
                cols_vue = con.execute(f"DESCRIBE {table};").fetchall()
                for col in cols_vue:
                    print(f"   - {col[0]} ({col[1]})")
            except Exception as e2:
                print(f"   Erreur : {e2}")
        print("-" * 40)
        
    con.close()

if __name__ == "__main__":
    inspecter_dwh()
    inspecter_reglements()