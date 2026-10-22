import duckdb
import pandas as pd

def run_analyse_cohortes_complete():
    db_path = "data/boreal_warehouse.duckdb"
    con = duckdb.connect(db_path)
    
    print("--- LIVRABLE 4 - ETAPE 1 : COHORTES ET MULTI-DÉTENTION ---\n")

    # 1. Analyse de la multi-détention (Auto + Habitation vs Mono-détenteurs)
    print("Comparaison de la rétention (Multi-détenteurs vs Mono-détenteurs) :")
    query_retention_client = """
        WITH client_profil AS (
            SELECT 
                fc.client_sk,
                COUNT(DISTINCT LOWER(d.produit)) AS nb_produits,
                MAX(CASE WHEN LOWER(CAST(d.produit AS VARCHAR)) LIKE '%auto%' THEN 1 ELSE 0 END) as has_auto,
                MAX(CASE WHEN LOWER(CAST(d.produit AS VARCHAR)) LIKE '%habita%' OR LOWER(CAST(d.produit AS VARCHAR)) LIKE '%mrh%' THEN 1 ELSE 0 END) as has_mrh,
                MAX(CASE WHEN t_res.temps_sk IS NOT NULL THEN 1 ELSE 0 END) as a_resilie
            FROM dwh.fait_contrats fc
            JOIN dwh.dim_contrats d ON fc.contrat_sk = d.contrat_sk
            JOIN dwh.dim_temps t_eff ON fc.temps_effet_sk = t_eff.temps_sk
            LEFT JOIN dwh.dim_temps t_res ON fc.temps_resiliation_sk = t_res.temps_sk
            GROUP BY fc.client_sk
        )
        SELECT 
            CASE 
                WHEN has_auto = 1 AND has_mrh = 1 THEN 'Multi-détenteur (Auto + Habitation)'
                ELSE 'Mono-détenteur / Autre'
            END AS categorie_client,
            COUNT(client_sk) AS total_clients,
            SUM(CASE WHEN a_resilie = 0 THEN 1 ELSE 0 END) AS clients_actifs,
            ROUND(SUM(CASE WHEN a_resilie = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(client_sk), 2) AS taux_retention_brut_pourcent
        FROM client_profil
        GROUP BY 1;
    """
    df_comp = con.execute(query_retention_client.strip()).fetchdf()
    print(df_comp.to_string(index=False))
    print("\n")

    # 2. Matrice de rétention empirique par cohorte de souscription
    print("Matrice de rétention empirique par cohorte et produit :")
    query_cohort_matrix = """
        SELECT 
            EXTRACT(YEAR FROM t_eff.date_complete) AS cohorte_annee,
            LOWER(d.produit) AS produit,
            COUNT(DISTINCT fc.contrat_sk) AS nb_contrats_initiaux,
            SUM(CASE WHEN t_res.temps_sk IS NOT NULL THEN 1 ELSE 0 END) AS nb_resiliations,
            ROUND((1 - (SUM(CASE WHEN t_res.temps_sk IS NOT NULL THEN 1 ELSE 0 END) * 1.0 / COUNT(DISTINCT fc.contrat_sk))) * 100, 2) AS taux_retention_pct
        FROM dwh.fait_contrats fc
        JOIN dwh.dim_contrats d ON fc.contrat_sk = d.contrat_sk
        JOIN dwh.dim_temps t_eff ON fc.temps_effet_sk = t_eff.temps_sk
        LEFT JOIN dwh.dim_temps t_res ON fc.temps_resiliation_sk = t_res.temps_sk
        GROUP BY 1, 2
        ORDER BY 1, 2;
    """
    df_matrix = con.execute(query_cohort_matrix.strip()).fetchdf()
    print(df_matrix.to_string(index=False))

    con.close()

if __name__ == "__main__":
    run_analyse_cohortes_complete()