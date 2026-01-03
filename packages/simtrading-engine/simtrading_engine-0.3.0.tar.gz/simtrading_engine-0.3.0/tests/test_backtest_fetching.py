import sys
import os
import json

# Ajout du dossier src au path pour pouvoir importer les modules du projet
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from simtrading.remote.client import TradeTpClient
from simtrading.remote.provider import RemoteDataProvider

def test_backtest_fetching():

    API_URL = "http://localhost:3000"
    API_KEY = "KqOREzBSEuhGRkIYQigywqxFIEbdmdHMLbQacKUREYhARYWFoKMaNoUQcFKFaXIN" # Clé de test par défaut
    TEST_BACKTEST_ID = "cmjremedi000nj9hnnd1g1keh" # ID de backtest existant pour les tests

    print("=== Test Fetching Backtest Config ===")

    # 1. Initialisation du client et du provider
    client = TradeTpClient(base_url=API_URL, api_key=API_KEY)
    provider = RemoteDataProvider(client)
    
    try:
        # 2. Appel de la fonction get_backtest_details via le provider
        # Note: On pourrait aussi tester client.get_backtest(TEST_BACKTEST_ID) directement
        backtest_config = provider.get_backtest_details(TEST_BACKTEST_ID)
        
        # 3. Affichage des résultats
        print("\n=== Résultats ===")
        print(json.dumps(backtest_config, indent=2))
        
        # Vérifications basiques
        if "id" in backtest_config and backtest_config["id"] == TEST_BACKTEST_ID:
            print("\nID correspond.")
        else:
            print(f"\n ID mismatch or missing. Got: {backtest_config.get('id')}")

        if "symbols" in backtest_config:
             print(f"Symbols found: {backtest_config['symbols']}")
        else:
             print("Symbols missing in config.")

    except Exception as e:
        print(f"\nErreur lors du test: {e}")
        # import traceback
        # traceback.print_exc()

if __name__ == "__main__":
    test_backtest_fetching()
