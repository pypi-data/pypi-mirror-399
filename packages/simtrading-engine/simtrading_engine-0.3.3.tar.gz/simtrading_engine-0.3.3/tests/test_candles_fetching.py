import os
import sys

# Ajout du dossier src au path pour pouvoir importer les modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from datetime import datetime, timedelta

from simtrading.remote.client import TradeTpClient
from simtrading.remote.provider import RemoteDataProvider

def test_fetching():

    print("=== Test Fetching Candles ===")

    API_URL = "http://localhost:3000"
    API_KEY = "KqOREzBSEuhGRkIYQigywqxFIEbdmdHMLbQacKUREYhARYWFoKMaNoUQcFKFaXIN" # Clé de test par défaut
        
    client = TradeTpClient(base_url=API_URL, api_key=API_KEY)
    provider = RemoteDataProvider(client)
    
    symbols = ["BTC-USD"] 
    
    now = datetime.now()

    # Début de la semaine courante (lundi 00:00)
    this_week_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=now.weekday())

    # Semaine d'encore avant (week-2) : du lundi il y a 14 jours au lundi il y a 7 jours
    start_dt = this_week_start - timedelta(days=14)
    end_dt   = this_week_start - timedelta(days=7)

    # Conversion en timestamps (secondes)
    start_ts = int(start_dt.timestamp())
    end_ts   = int(end_dt.timestamp())
    
    print(f"Fetching candles for {symbols}")
    print(f"From: {start_dt} ({start_ts})")
    print(f"To:   {end_dt} ({end_ts})")
    
    try:
        # 3. Appel de la fonction get_candles
        candles_map = provider.get_candles(
            symbols=symbols,
            start=start_ts,
            end=end_ts,
            timeframe="1h" # Timeframe 1 heure
        )
        
        # 4. Affichage des résultats
        print("\n=== Résultats ===")
        for symbol, candles in candles_map.items():
            print(f"Symbol: {symbol}")
            print(f"Nombre de bougies reçues: {len(candles)}")
            
            if candles:
                first = candles[0]
                last = candles[-1]
                print(f"Première bougie: {first.date} | Open: {first.open}")
                print(f"Dernière bougie: {last.date} | Close: {last.close}")
                
                # Vérification basique d'intégrité
                print(f"Type de timestamp: {type(first.timestamp)}")
                print(f"Type de date: {type(first.date)}")
            else:
                print("Aucune bougie trouvée.")
                
    except Exception as e:
        print(f"\n Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fetching()
