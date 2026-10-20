import duckdb
import pandas as pd

def run_analyse_technique_complete():
    db_path = "data/boreal_warehouse.duckdb"
    con = duckdb.connect(db_path)
    
    print("--- Analyse Technique Complète ---\n")

    # Vues de base (Exposition et Sinistres)
    con.execute("""
        CREATE OR REPLACE VIEW dwh.v_exposition_contrats AS
        SELECT 
            fc.contrat_sk,
            fc.client_sk,
            dc.produit,
            dc.formule,
            dc.canal,
            dc.zone_risque,
            dcl.date_naissance,
            CASE 
                WHEN FLOOR(DATEDIFF('day', dcl.date_naissance, CURRENT_DATE) / 365.25) < 30 THEN '< 30 ans'
                WHEN FLOOR(DATEDIFF('day', dcl.date_naissance, CURRENT_DATE) / 365.25) BETWEEN 30 AND 50 THEN '30-50 ans'
                ELSE '> 50 ans'
            END AS tranche_age,
            fc.prime_annuelle,
            t_eff.date_complete AS date_effet,
            COALESCE(t_res.date_complete, DATE '2026-12-31') AS date_fin,
            GREATEST(DATEDIFF('day', t_eff.date_complete, COALESCE(t_res.date_complete, CURRENT_DATE)) / 365.25, 0.01) AS exposition_annees,
            CASE WHEN t_res.date_complete IS NOT NULL THEN 1 ELSE 0 END AS est_resilie
        FROM dwh.fait_contrats fc
        JOIN dwh.dim_contrats dc ON fc.contrat_sk = dc.contrat_sk
        JOIN dwh.dim_clients dcl ON fc.client_sk = dcl.client_sk
        LEFT JOIN dwh.dim_temps t_eff ON fc.temps_effet_sk = t_eff.temps_sk
        LEFT JOIN dwh.dim_temps t_res ON fc.temps_resiliation_sk = t_res.temps_sk;
    """)

    con.execute("""
        CREATE OR REPLACE VIEW dwh.v_sinistres_par_contrat AS
        SELECT 
            fs.contrat_sk,
            COUNT(fs.sinistre_id) AS nb_sinistres,
            COUNT(CASE WHEN fs.statut = 'SANS_SUITE' THEN 1 END) AS nb_sans_suite,
            SUM(fs.reserve_initiale) AS total_reserves,
            COALESCE(SUM(fr.montant), 0) AS total_paye,
            (COALESCE(SUM(fr.montant), 0) + SUM(CASE WHEN fs.statut != 'SANS_SUITE' THEN fs.reserve_initiale ELSE 0 END)) AS charge_totale
        FROM dwh.fait_sinistres fs
        LEFT JOIN dwh.fait_reglements fr ON fs.sinistre_id = fr.sinistre_id
        GROUP BY fs.contrat_sk;
    """)

    def analyser_axe(dimension, nom_affichage):
        query = f"""
            SELECT 
                e.{dimension} AS axe,
                COUNT(DISTINCT e.contrat_sk) AS nb_contrats,
                ROUND(SUM(e.exposition_annees), 2) AS expo,
                ROUND(AVG(e.prime_annuelle), 2) AS prime_moy,
                COALESCE(SUM(s.nb_sinistres), 0) AS nb_sin,
                -- Calcul de la fréquence : Nb de sinistres / Exposition totale en années
                ROUND(COALESCE(SUM(s.nb_sinistres), 0) / NULLIF(SUM(e.exposition_annees), 0), 4) AS frequence,
                COALESCE(SUM(s.nb_sans_suite), 0) AS nb_sans_suite,
                ROUND(COALESCE(SUM(s.total_paye), 0), 2) AS total_paye,
                ROUND(COALESCE(SUM(s.total_reserves), 0), 2) AS total_reserves,
                ROUND(COALESCE(SUM(s.charge_totale), 0) / NULLIF(SUM(s.nb_sinistres), 0), 2) AS cout_moyen,
                ROUND((COALESCE(SUM(s.charge_totale), 0) / NULLIF(SUM(e.prime_annuelle), 0)) * 100, 2) AS ratio_sp_pct
            FROM dwh.v_exposition_contrats e
            LEFT JOIN dwh.v_sinistres_par_contrat s ON e.contrat_sk = s.contrat_sk
            GROUP BY e.{dimension}
            ORDER BY ratio_sp_pct DESC;
        """
        
        print(f"\n--- Indicateurs par {nom_affichage} ---")
        df = con.execute(query).fetchdf()
        print(df.to_string(index=False))

    # Tous les axes requis par le Livrable 3
    analyser_axe("produit", "Produit")
    analyser_axe("zone_risque", "Zone de Risque")
    analyser_axe("formule", "Formule de Garantie")
    analyser_axe("canal", "Canal de Distribution")
    analyser_axe("tranche_age", "Tranche d'Âge")

    con.close()

if __name__ == "__main__":
    run_analyse_technique_complete()