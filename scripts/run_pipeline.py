import os
import subprocess
import sys
from datetime import datetime

def run_step(script_name, description):
    "Exécute un script Python et gère les erreurs."
    print(f"\n[INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Démarrage : {description} ({script_name})")
    start_time = datetime.now()
    
    try:
        # Exécute le script avec l'interpréteur Python actif
        result = subprocess.run([sys.executable, script_name], check=True, text=True, capture_output=True)
        duration = (datetime.now() - start_time).total_seconds()
        print(f"[SUCCÈS] {description} exécuté en {duration:.2f} secondes.")
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Échec lors de l'exécution de : {description}")
        print(e.stderr)
        sys.exit(1)

def main():
    print("  LANCEMENT DU PIPELINE GLOBAL - BOREAL ASSURANCES")
    
    
    # Définition des étapes successives du pipeline
    steps = [
        ("scripts/01_ingest_raw.py", "Ingestion des données brutes"),
        ("scripts/02_quality_prep.py", "Préparation et nettoyage"),
        ("scripts/02_schema.py", "Alimentation de l'Entrepôt de Données"),
        ("scripts/04_valeur_clients.py", "Génération du graphique de Pareto")
    ]
    
    for script_path, desc in steps:
        if os.path.exists(script_path):
            run_step(script_path, desc)
        else:
            print(f"[AVERTISSEMENT] Le fichier {script_path} est introuvable ou facultatif. Étape ignorée.")
            
    print("\n  PIPELINE EXÉCUTÉ AVEC SUCCÈS ! MODELE ET DASHBOARD PRÊTS.")

if __name__ == "__main__":
    main()