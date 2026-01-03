from typing import Dict, List, Union
from simtrading.backtest_engine.entities.candle import Candle
from simtrading.backtest_engine.entities.symbol import Symbol
from simtrading.remote.client import TradeTpClient

class RemoteDataProvider:
    """Récupère les données via l'API distante."""

    def __init__(self, client: TradeTpClient):
        self.client = client

    def get_candles(self, symbols: List[str], start: int, end: int, timeframe: str = "1d") -> Dict[str, List[Candle]]:
        """
        Récupère les candles pour plusieurs symboles et retourne un dictionnaire indexé par symbole.
        """
        # Appel au client qui retourne un dict { "SYMBOLE": [ {data...}, ... ] }
        raw_response = self.client.get_candles(
            symbols=symbols, 
            start=start, 
            end=end, 
            timeframe=timeframe
        )
        
        candles_by_symbol = {}
        
        # On itère sur chaque symbole reçu
        for symbol, candle_dicts in raw_response.items():
            candles = []
            for c in candle_dicts:
                try:
                    candles.append(
                        Candle(
                            symbol=symbol,
                            timestamp=int(c["timestamp"]), 
                            date=c["date"],
                            open=float(c["open"]),
                            high=float(c["high"]),
                            low=float(c["low"]),
                            close=float(c["close"]),
                            volume=float(c.get("volume", 0.0)),
                        )
                    )
                except KeyError:
                    continue
            
            candles_by_symbol[symbol] = candles
            
        return candles_by_symbol

    def get_backtest_details(self, backtest_id: str) -> Dict[str, Union[str, int, float, List[str], None]]:
        """
        Récupère les détails d'un backtest par son ID.
        """
        return self.client.get_backtest(backtest_id)