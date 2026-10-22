import duckdb
import pandas as pd

def run_analyse_delais_audits():
    db_path = "data/boreal_warehouse.duckdb"
    con = duckdb.connect(db_path)
    
    print("--- LIVRABLE 4 - ETAPE 3 : DÉLAIS ET AUDITS ---\n")

    # 1. Analyse des délais de déclaration par garantie
    query_delais = """
        WITH delais_bruts AS (
            SELECT 
                fs.garantie,
                (t_dec.date_complete - t_surv.date_complete) AS delai_declaration_jours
            FROM dwh.fait_sinistres fs
            JOIN dwh.dim_temps t_surv ON fs.temps_survenance_sk = t_surv.temps_sk
            JOIN dwh.dim_temps t_dec ON fs.temps_declaration_sk = t_dec.temps_sk
            WHERE t_dec.date_complete >= t_surv.date_complete
        )
        SELECT 
            garantie,
            COUNT(*) as nb_sinistres,
            ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY delai_declaration_jours), 1) AS mediane_delai_declaration,
            ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY delai_declaration_jours), 1) AS p90_delai_declaration
        FROM delais_bruts
        GROUP BY garantie;
    """
    
    print("Analyse des délais de déclaration par garantie :")
    df_delais = con.execute(query_delais).fetchdf()
    print(df_delais.to_string(index=False))
    print("\n")

    # 2. Taux de confirmation de fraude et impact financier
    query_fraude = """
        SELECT 
            COUNT(*) AS total_audits,
            SUM(CASE WHEN fraude_confirmee = 1 THEN 1 ELSE 0 END) AS audits_confirmes,
            ROUND(SUM(CASE WHEN fraude_confirmee = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS taux_confirmation_pct
        FROM raw.antifraude_audits;
    """
    
    print("Taux de confirmation de fraude :")
    df_fraude = con.execute(query_fraude).fetchdf()
    print(df_fraude.to_string(index=False))
    print("\n")

    # 3. Évaluation de l'intérêt des audits au regard des montants concernés (Réserves / Coûts)
    query_impact = """
        SELECT 
            a.fraude_confirmee,
            COUNT(a.sinistre_id) AS nb_sinistres_audites,
            ROUND(AVG(fs.reserve_initiale), 2) AS reserve_initiale_moyenne,
            ROUND(SUM(fs.reserve_initiale), 2) AS reserve_initiale_totale
        FROM raw.antifraude_audits a
        JOIN dwh.fait_sinistres fs ON a.sinistre_id = fs.sinistre_id
        GROUP BY a.fraude_confirmee;
    """
    
    print("Impact financier des audits (comparaison des réserves initiales) :")
    df_impact = con.execute(query_impact).fetchdf()
    print(df_impact.to_string(index=False))

    con.close()

if __name__ == "__main__":
    run_analyse_delais_audits()