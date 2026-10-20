import duckdb
import pandas as pd

def run_decomposition_sp():
    db_path = "data/boreal_warehouse.duckdb"
    con = duckdb.connect(db_path)
    
    print("--- Démarrage de la Décomposition de l'Évolution du S/P ---\n")

    # 1. Analyse de l'évolution annuelle globale et détection des années incomplètes
    print("1. Évolution annuelle globale du S/P et identification des années incomplètes :")
    query_evolution_globale = """
        SELECT 
            EXTRACT(YEAR FROM t_eff.date_complete) AS annee,
            COUNT(DISTINCT fc.contrat_sk) AS nb_contrats,
            ROUND(SUM(GREATEST(DATEDIFF('day', t_eff.date_complete, COALESCE(t_res.date_complete, CURRENT_DATE)) / 365.25, 0.01)), 2) AS exposition_totale,
            ROUND(SUM(fc.prime_annuelle), 2) AS primes_totales,
            COUNT(fs.sinistre_id) AS nb_sinistres,
            ROUND(SUM(COALESCE(fr.montant, 0) + CASE WHEN fs.statut != 'SANS_SUITE' THEN fs.reserve_initiale ELSE 0 END), 2) AS charge_totale,
            ROUND(
                (SUM(COALESCE(fr.montant, 0) + CASE WHEN fs.statut != 'SANS_SUITE' THEN fs.reserve_initiale ELSE 0 END) 
                / NULLIF(SUM(fc.prime_annuelle), 0)) * 100, 2
            ) AS ratio_sp_pct,
            CASE 
                WHEN EXTRACT(YEAR FROM t_eff.date_complete) >= 2026 THEN ' Année en cours / Incomplète'
                ELSE 'Complet'
            END AS statut_annee
        FROM dwh.fait_contrats fc
        JOIN dwh.dim_temps t_eff ON fc.temps_effet_sk = t_eff.temps_sk
        LEFT JOIN dwh.dim_temps t_res ON fc.temps_resiliation_sk = t_res.temps_sk
        LEFT JOIN dwh.fait_sinistres fs ON fc.contrat_sk = fs.contrat_sk
        LEFT JOIN dwh.fait_reglements fr ON fs.sinistre_id = fr.sinistre_id
        GROUP BY EXTRACT(YEAR FROM t_eff.date_complete)
        ORDER BY annee ASC;
    """
    df_globale = con.execute(query_evolution_globale).fetchdf()
    print(df_globale.to_string(index=False))

    # 2. Décomposition factorielle interannuelle (Volume, Fréquence, Coût moyen, Prime moyenne)
    print("\n2. Facteurs de décomposition par année :")
    query_decomposition = """
        WITH stats_annuelles AS (
            SELECT 
                EXTRACT(YEAR FROM t_eff.date_complete) AS annee,
                COUNT(DISTINCT fc.contrat_sk) AS volume_contrats,
                SUM(GREATEST(DATEDIFF('day', t_eff.date_complete, COALESCE(t_res.date_complete, CURRENT_DATE)) / 365.25, 0.01)) AS exposition,
                SUM(fc.prime_annuelle) AS total_primes,
                COUNT(fs.sinistre_id) AS nb_sinistres,
                SUM(COALESCE(fr.montant, 0) + CASE WHEN fs.statut != 'SANS_SUITE' THEN fs.reserve_initiale ELSE 0 END) AS charge_totale
            FROM dwh.fait_contrats fc
            JOIN dwh.dim_temps t_eff ON fc.temps_effet_sk = t_eff.temps_sk
            LEFT JOIN dwh.dim_temps t_res ON fc.temps_resiliation_sk = t_res.temps_sk
            LEFT JOIN dwh.fait_sinistres fs ON fc.contrat_sk = fs.contrat_sk
            LEFT JOIN dwh.fait_reglements fr ON fs.sinistre_id = fr.sinistre_id
            GROUP BY EXTRACT(YEAR FROM t_eff.date_complete)
        )
        SELECT 
            annee,
            volume_contrats,
            ROUND(exposition, 2) AS exposition,
            ROUND(nb_sinistres / NULLIF(exposition, 0), 4) AS frequence,
            ROUND(charge_totale / NULLIF(nb_sinistres, 0), 2) AS cout_moyen,
            ROUND(total_primes / NULLIF(volume_contrats, 0), 2) AS prime_moyenne,
            ROUND((charge_totale / NULLIF(total_primes, 0)) * 100, 2) AS ratio_sp_pct
        FROM stats_annuelles
        ORDER BY annee ASC;
    """
    df_decomp = con.execute(query_decomposition).fetchdf()
    print(df_decomp.to_string(index=False))

    con.close()
    print("\n[SUCCÈS] Analyse de décomposition terminée avec succès !")

if __name__ == "__main__":
    run_decomposition_sp()