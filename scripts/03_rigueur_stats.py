import duckdb
import pandas as pd
import numpy as np
from scipy import stats

def run_statistiques_descriptives():
    db_path = "data/boreal_warehouse.duckdb"
    con = duckdb.connect(db_path)
    
    print("--- ETAPE 3 : RIGUEUR STATISTIQUE DESCRIPTIVE ---\n")

    # 1. INTERVALLES DE CONFIANCE (IC 95%)
    print("Intervalles de Confiance à 95% pour les indicateurs clés :")
    query_ic = """
        SELECT 
            COUNT(DISTINCT fc.contrat_sk) AS N_contrats,
            SUM(GREATEST(DATEDIFF('day', t_eff.date_complete, COALESCE(t_res.date_complete, CURRENT_DATE)) / 365.25, 0.01)) AS total_expo,
            COUNT(fs.sinistre_id) AS total_sinistres
        FROM dwh.fait_contrats fc
        JOIN dwh.dim_temps t_eff ON fc.temps_effet_sk = t_eff.temps_sk
        LEFT JOIN dwh.dim_temps t_res ON fc.temps_resiliation_sk = t_res.temps_sk
        LEFT JOIN dwh.fait_sinistres fs ON fc.contrat_sk = fs.contrat_sk;
    """
    res_ic = con.execute(query_ic).fetchone()
    n_contrats, expo, n_sin = res_ic
    
    freq = n_sin / expo
    se_freq = np.sqrt(n_sin) / expo
    ic_freq_low, ic_freq_high = freq - 1.96 * se_freq, freq + 1.96 * se_freq

    query_costs = """
        SELECT 
            fs.sinistre_id,
            COALESCE(SUM(fr.montant), 0) + CASE WHEN ANY_VALUE(fs.statut) != 'SANS_SUITE' THEN ANY_VALUE(fs.reserve_initiale) ELSE 0 END AS charge
        FROM dwh.fait_sinistres fs
        LEFT JOIN dwh.fait_reglements fr ON fs.sinistre_id = fr.sinistre_id
        GROUP BY fs.sinistre_id
    """
    df_costs = con.execute(query_costs).fetchdf()
    costs = df_costs['charge'].values

    cout_moyen = np.mean(costs)
    se_cout = np.std(costs, ddof=1) / np.sqrt(len(costs))
    ic_cout_low, ic_cout_high = cout_moyen - 1.96 * se_cout, cout_moyen + 1.96 * se_cout

    print(f"Fréquence moyenne : {freq:.4f} (IC 95% : [{ic_freq_low:.4f} ; {ic_freq_high:.4f}])")
    print(f"Coût moyen : {cout_moyen:.2f} € (IC 95% : [{ic_cout_low:.2f} € ; {ic_cout_high:.2f} €])\n")

    # 2. TESTS D'HYPOTHÈSES
    print("Tests statistiques d'hypothèses :")
    
    # Test 1: Comparaison de Fréquence entre Zone 1 et Zone 4
    query_zones = """
        SELECT 
            CAST(d.zone_risque AS VARCHAR) AS zone_risque,
            SUM(GREATEST(DATEDIFF('day', t_eff.date_complete, COALESCE(t_res.date_complete, CURRENT_DATE)) / 365.25, 0.01)) AS expo,
            COUNT(fs.sinistre_id) AS nb_sin
        FROM dwh.fait_contrats fc
        JOIN dwh.dim_contrats d ON fc.contrat_sk = d.contrat_sk
        JOIN dwh.dim_temps t_eff ON fc.temps_effet_sk = t_eff.temps_sk
        LEFT JOIN dwh.dim_temps t_res ON fc.temps_resiliation_sk = t_res.temps_sk
        LEFT JOIN dwh.fait_sinistres fs ON fc.contrat_sk = fs.contrat_sk
        WHERE CAST(d.zone_risque AS VARCHAR) IN ('1', '4', 'Zone 1', 'Zone 4')
        GROUP BY CAST(d.zone_risque AS VARCHAR)
    """
    df_z = con.execute(query_zones).fetchdf().set_index('zone_risque')
    key1 = '1' if '1' in df_z.index else 'Zone 1'
    key4 = '4' if '4' in df_z.index else 'Zone 4'

    e1, s1 = df_z.loc[key1, 'expo'], df_z.loc[key1, 'nb_sin']
    e4, s4 = df_z.loc[key4, 'expo'], df_z.loc[key4, 'nb_sin']
    
    p1, p4 = s1 / e1, s4 / e4
    p_pool = (s1 + s4) / (e1 + e4)
    z_stat = (p1 - p4) / np.sqrt(p_pool * (1 - p_pool) * (1/e1 + 1/e4))
    p_val_z = 2 * (1 - stats.norm.cdf(abs(z_stat)))

    print(f" [Test 1 - Fréquence Zone 1 vs Zone 4]")
    print(f"Freq Z1: {p1:.4f} | Freq Z4: {p4:.4f}")
    print(f"Test Z (Deux proportions) : Z = {z_stat:.4f}, p-value = {p_val_z:.4e}")
    print(f"Conclusion : {'Différence significative' if p_val_z < 0.05 else 'Pas de différence significative'}\n")

    # Test 2: Comparaison dynamique du Coût Moyen entre les 2 principaux canaux
    query_chan_costs = """
        SELECT 
            CAST(d.canal AS VARCHAR) AS canal_distribution,
            COALESCE(SUM(fr.montant), 0) + CASE WHEN ANY_VALUE(fs.statut) != 'SANS_SUITE' THEN ANY_VALUE(fs.reserve_initiale) ELSE 0 END AS charge
        FROM dwh.fait_sinistres fs
        JOIN dwh.fait_contrats fc ON fs.contrat_sk = fc.contrat_sk
        JOIN dwh.dim_contrats d ON fc.contrat_sk = d.contrat_sk
        LEFT JOIN dwh.fait_reglements fr ON fs.sinistre_id = fr.sinistre_id
        GROUP BY fs.sinistre_id, CAST(d.canal AS VARCHAR)
    """
    df_chan = con.execute(query_chan_costs).fetchdf()
    canaux_populaires = df_chan['canal_distribution'].value_counts().index[:2]
    
    if len(canaux_populaires) >= 2:
        c1, c2 = canaux_populaires[0], canaux_populaires[1]
        costs_c1 = df_chan[df_chan['canal_distribution'] == c1]['charge'].values
        costs_c2 = df_chan[df_chan['canal_distribution'] == c2]['charge'].values

        stat_mw, p_val_mw = stats.mannwhitneyu(costs_c1, costs_c2, alternative='two-sided')
        print(f" [Test 2 - Coût Moyen Canal {c1} vs {c2}]")
        print(f"Coût Moyen {c1}: {np.mean(costs_c1):.2f} € | Coût Moyen {c2}: {np.mean(costs_c2):.2f} €")
        print(f"Test de Mann-Whitney U : Stat = {stat_mw:.1f}, p-value = {p_val_mw:.4e}")
        print(f"Conclusion : {'Différence significative' if p_val_mw < 0.05 else 'Pas de différence significative'}\n")
    else:
        print(" [Test 2] Impossible de comparer : pas assez de canaux distincts trouvés.\n")

    # 3. QUEUE DE DISTRIBUTION DES COÛTS
    print("📌 3. Description de la queue de distribution des coûts de sinistres :")
    p50 = np.percentile(costs, 50)
    p75 = np.percentile(costs, 75)
    p90 = np.percentile(costs, 90)
    p95 = np.percentile(costs, 95)
    p99 = np.percentile(costs, 99)

    top_1_pct_val = np.percentile(costs, 99)
    top_5_pct_val = np.percentile(costs, 95)
    
    part_top1 = np.sum(costs[costs >= top_1_pct_val]) / np.sum(costs) * 100
    part_top5 = np.sum(costs[costs >= top_5_pct_val]) / np.sum(costs) * 100

    print(f"Médiane (P50) : {p50:.2f} €")
    print(f"Quantiles : P75 = {p75:.2f} € | P90 = {p90:.2f} € | P95 = {p95:.2f} € | P99 = {p99:.2f} €")
    print(f"Part du TOP 5% des sinistres les plus chers : {part_top5:.2f} % de la charge totale")
    print(f"Part du TOP 1% des sinistres les plus chers : {part_top1:.2f} % de la charge totale")

    con.close()

if __name__ == "__main__":
    run_statistiques_descriptives()