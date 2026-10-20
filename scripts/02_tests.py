import duckdb
import sys

def run_tests():
    db_path = "data/boreal_warehouse.duckdb"
    con = duckdb.connect(db_path)
    
    print("--- Lancement des Tests Automatisés ---")
    tests_failed = 0
    
    def assert_test(test_name, query, expected_value=0):
        nonlocal tests_failed
        result = con.execute(query).fetchone()[0]
        if result == expected_value:
            print(f"[SUCCÈS] {test_name}")
        else:
            print(f"[ÉCHEC] {test_name} (Valeur trouvée : {result}, attendue : {expected_value})")
            tests_failed += 1

    # 1. Unicité de la clé primaire client_id dans crm_clients_dedup
    assert_test(
        "Test 1 : Unicité des client_id dans CRM dédupliqué",
        "SELECT COUNT(*) - COUNT(DISTINCT client_id) FROM prep.crm_clients_dedup;"
    )

    # 2. Unicité de la clé primaire contrat_id dans contrats prep
    assert_test(
        "Test 2 : Unicité des contrat_id dans prep.contrats",
        "SELECT COUNT(*) - COUNT(DISTINCT contrat_id) FROM prep.contrats;"
    )

    # 3. Unicité de la clé primaire sinistre_id dans sinistres prep
    assert_test(
        "Test 3 : Unicité des sinistre_id dans prep.sinistres",
        "SELECT COUNT(*) - COUNT(DISTINCT sinistre_id) FROM prep.sinistres;"
    )

    # 4. Intégrité référentielle : Sinistres rattachés à des contrats existants
    assert_test(
        "Test 4 : Intégrité référentielle Sinistres -> Contrats",
        "SELECT COUNT(*) FROM prep.sinistres WHERE contrat_id NOT IN (SELECT contrat_id FROM prep.contrats);"
    )

    # 5. Intégrité référentielle : Règlements rattachés à des sinistres existants
    assert_test(
        "Test 5 : Intégrité référentielle Règlements -> Sinistres",
        "SELECT COUNT(*) FROM prep.reglements WHERE sinistre_id NOT IN (SELECT sinistre_id FROM prep.sinistres);"
    )

    # 6. Réconciliation des règlements (Montant total brut vs prep + quarantaine)
    assert_test(
        "Test 6 : Réconciliation des règlements (Brut = Prep + Quarantaine)",
        """
        SELECT 
            ROUND(
                (SELECT COALESCE(SUM(montant), 0) FROM raw.reglements WHERE montant > 0)
                - 
                (
                    (SELECT COALESCE(SUM(montant), 0) FROM prep.reglements)
                    + 
                    (SELECT COALESCE(SUM(CAST(JSON_EXTRACT(raw_data, '$.montant') AS DOUBLE)), 0) 
                     FROM quarantine.rejected_records 
                     WHERE rule_id = 'R15_REGLEMENT_SINISTRE_ORPHELIN')
                ), 2
            )
        ;
        """,
        expected_value=0.0
    )
    
    # 7. Règle métier : Primes annuelles toujours strictement positives dans prep
    assert_test(
        "Test 7 : Prime annuelle toujours positive (> 0)",
        "SELECT COUNT(*) FROM prep.contrats WHERE prime_annuelle <= 0;"
    )

    # 8. Règle métier : Montants des règlements toujours strictement positifs dans prep
    assert_test(
        "Test 8 : Montant des règlements toujours positif (> 0)",
        "SELECT COUNT(*) FROM prep.reglements WHERE montant <= 0;"
    )

    con.close()
    
    print("-" * 50)
    if tests_failed > 0:
        print(f"Fin des tests : {tests_failed} test(s) ont échoué.")
        sys.exit(1)
    else:
        print("Tous les tests automatisés ont réussi avec succès !")
        sys.exit(0)

if __name__ == "__main__":
    run_tests()