import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import os

def run_analyse_valeur_clients():
    db_path = "data/boreal_warehouse.duckdb"
    con = duckdb.connect(db_path)
    
    print("---LIVRABLE 4 - ETAPE 2 : VALEUR OBSERVÉE DES CLIENTS ---\n")

    # 1. Reconstitution de la valeur observée par client (Primes - Sinistres payés)
    query_valeur = """
        WITH primes_client AS (
            SELECT 
                client_sk,
                SUM(prime_annuelle) AS total_primes
            FROM dwh.fait_contrats
            GROUP BY client_sk
        ),
        sinistres_client AS (
            SELECT 
                fc.client_sk,
                SUM(v.total_paye) AS total_sinistres
            FROM dwh.v_sinistres_par_contrat v
            JOIN dwh.fait_contrats fc ON v.contrat_sk = fc.contrat_sk
            GROUP BY fc.client_sk
        )
        SELECT 
            p.client_sk,
            COALESCE(p.total_primes, 0) AS total_primes,
            COALESCE(s.total_sinistres, 0) AS total_sinistres,
            (COALESCE(p.total_primes, 0) - COALESCE(s.total_sinistres, 0)) AS valeur_net_client
        FROM primes_client p
        LEFT JOIN sinistres_client s ON p.client_sk = s.client_sk
        ORDER BY valeur_net_client DESC;
    """
    
    df_valeur = con.execute(query_valeur.strip()).fetchdf()
    
    # 2. Statistiques descriptives globales
    total_clients = len(df_valeur)
    clients_rentables = df_valeur[df_valeur['valeur_net_client'] > 0]
    clients_deficitaires = df_valeur[df_valeur['valeur_net_client'] < 0]
    
    print(f"Nombre total de clients : {total_clients}")
    print(f"Clients rentables (>0€) : {len(clients_rentables)} ({round(len(clients_rentables)/total_clients*100, 2)}%)")
    print(f"Clients déficitaires (<0€) : {len(clients_deficitaires)} ({round(len(clients_deficitaires)/total_clients*100, 2)}%)\n")

    # 3. Courbe de Pareto (Concentration de la rentabilité)
    df_valeur['cum_valeur'] = df_valeur['valeur_net_client'].cumsum()
    total_valeur_positive = clients_rentables['valeur_net_client'].sum()
    
    if total_valeur_positive > 0:
        df_valeur['pct_cum_valeur'] = (df_valeur['cum_valeur'] / total_valeur_positive) * 100
    else:
        df_valeur['pct_cum_valeur'] = 0
        
    df_valeur['pct_cum_clients'] = ((df_valeur.index + 1) / total_clients) * 100

    # Top 10 % des clients
    top_10_idx = int(total_clients * 0.10)
    if top_10_idx < len(df_valeur):
        top_10_pct = df_valeur.iloc[top_10_idx]
        print(f"Concentration Pareto : Le Top 10% des clients représente {round(top_10_pct['pct_cum_valeur'], 2)}% de la valeur nette cumulée.\n")

    # 4. Génération du graphique Pareto
    os.makedirs("reports", exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.plot(df_valeur['pct_cum_clients'], df_valeur['pct_cum_valeur'], color='navy', lw=2, label='Courbe de Pareto (Valeur nette)')
    plt.axhline(80, color='red', linestyle='--', label='80% de la valeur')
    plt.axvline(20, color='orange', linestyle='--', label='20% des clients')
    plt.title('Courbe de Pareto - Concentration de la Valeur Clients')
    plt.xlabel('% cumulé des clients')
    plt.ylabel('% cumulé de la valeur nette')
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    
    plot_path = "graphique/pareto_valeur_clients.png"
    plt.savefig(plot_path)
    print(f"Graphique de Pareto sauvegardé sous : {plot_path}\n")

    con.close()

if __name__ == "__main__":
    run_analyse_valeur_clients()