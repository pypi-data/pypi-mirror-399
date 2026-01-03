from typing import Any, Dict, List, Optional, Union
import requests

class TradeTpClient:
    """Client HTTP pour l'API distante avec auth Bearer."""

    def __init__(self, base_url: str, api_key: str, timeout: float = 60.0):
        base_url = base_url.rstrip("/")
        self.base_url = base_url + "/api"
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"x-api-key": self.api_key})

    def _full_url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _check_response(self, resp: requests.Response, context: str):
        if resp.status_code == 401:
            raise PermissionError(f"Invalid API Key during {context}. Please check your API key.")
        if not resp.ok:
            raise RuntimeError(f"Failed to {context}: {resp.status_code} {resp.text}")
        
    def get_candles(self, symbols: List[str], start: int, end: int, timeframe: str = "1d") -> Dict[str, List[Dict[str, Any]]]:
        """
        Récupère les candles pour les symboles et la période donnés.
        Appelle POST /api/candles
        """
        payload = {
            "symbols": symbols, 
            "start": start, 
            "end": end, 
            "timeframe": timeframe
        }
        
        resp = self.session.post(self._full_url("/candles"), json=payload, timeout=self.timeout)
        self._check_response(resp, "fetch candles")
        
        # Retourne un dictionnaire { "BTCUSDT": [ { ... }, ... ], ... }
        return resp.json() or {}

    def get_backtest(self, backtest_id: str) -> Dict[str, Any]:
        """
        Récupère les détails d'un backtest par son ID.
        Appelle GET /api/backtests/{backtest_id}
        """
        resp = self.session.get(self._full_url(f"/backtests/{backtest_id}"), timeout=self.timeout)
        self._check_response(resp, "fetch backtest details")
        
        # retourne un dictionnaire avec les détails du backtest
        # {
        #   "id": "string",
        #   "symbols": ["string", "..."],
        #   "timeframe": "string",
        #   "start": "number",
        #   "end": "number",
        #   "initial_cash": "number",
        #   "fee_rate": "number",
        #   "margin_requirement": "number",
        #   "strategy_name": "string | null",
        #   "strategy_params": "object | null",
        #   "status": "string"
        # }
        return resp.json() or {}

    def create_backtest(self, config: Dict[str, Any]) -> str:
        """
        Crée un nouveau backtest sur la plateforme.
        POST /api/backtests
        
        Args:
            config: Dictionnaire contenant les paramètres du backtest
                   (symbols, start, end, timeframe, initial_cash, etc.)
        
        Returns:
            str: L'ID du backtest créé.
        """
        resp = self.session.post(self._full_url("/backtests"), json=config, timeout=self.timeout)
        self._check_response(resp, "create backtest")
        
        return resp.json()["id"]
    
    def post_backtest_result(self, backtest_id: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envoie les résultats du backtest à l'API.
        POST /api/backtests/{backtest_id}/results

        Le dictionnaire 'results' doit contenir les clés suivantes (snake_case) :
        - total_return (float)
        - final_equity (float)
        - total_fees (float)
        - total_trades (int)
        - trades (List[Dict])
        - equity_curve (List[Dict])
        - indicators (Dict)
        - logs (List[str])
        - strategy_name (str)
        - strategy_params (Dict)
        """
        resp = self.session.post(
            self._full_url(f"/backtests/{backtest_id}/results"), 
            json=results, 
            timeout=self.timeout
        )
        self._check_response(resp, "post backtest results")
        return resp.json()






