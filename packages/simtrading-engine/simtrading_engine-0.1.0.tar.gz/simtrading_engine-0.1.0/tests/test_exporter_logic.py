import sys
import os
import json
from typing import Any, Dict

# Ajout du dossier src au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from simtrading.remote.client import TradeTpClient
from simtrading.remote.exporter import ResultExporter
from simtrading.backtest_engine.entities.portfolio_snapshot import PortfolioSnapshot
from simtrading.backtest_engine.entities.position import Position
from simtrading.backtest_engine.entities.trade import Trade
from simtrading.backtest_engine.entities.enums import PositionSide

class MockClient(TradeTpClient):
    def __init__(self):
        # On ne fait rien ici pour ne pas initier de session requests
        self.base_url = "http://mock"
        self.api_key = "mock"
        self.timeout = 60
        
    def post_backtest_result(self, backtest_id: str, results: Dict[str, Any]) -> Dict[str, Any]:
        print(f"\n--- Mock Client: Received results for {backtest_id} ---")
        print(json.dumps(results, indent=2, default=str))
        return {"status": "success"}

def test_exporter_logic():
    print("=== Test Exporter Logic ===")
    
    # 1. Setup Mock Client
    client = MockClient()
    exporter = ResultExporter(client)
    
    # 2. Create Dummy Data
    # Candle 1: Buy
    ts1 = 1672531200000 # 2023-01-01
    trade1 = Trade(
        symbol="BTCUSD",
        quantity=1.0,
        price=20000.0,
        fee=20.0,
        timestamp=ts1,
        trade_id="t1"
    )
    
    snapshot1 = PortfolioSnapshot(
        timestamp=ts1,
        cash=79980.0,
        equity=99980.0,
        positions=[
            Position(symbol="BTCUSD", side=PositionSide.LONG, quantity=1.0, entry_price=20000.0)
        ]
    )
    
    log1 = {
        "timestamp": ts1,
        "snapshot_after": snapshot1,
        "execution_details": [{"trade": trade1}],
        "indicators": {"sma": 20050.0}
    }
    
    # Candle 2: Hold/Price Move
    ts2 = 1672617600000 # 2023-01-02
    # Price goes to 21000.
    # Equity = 79980 + 1 * 21000 = 100980.
    snapshot2 = PortfolioSnapshot(
        timestamp=ts2,
        cash=79980.0,
        equity=100980.0,
        positions=[
            Position(symbol="BTCUSD", side=PositionSide.LONG, quantity=1.0, entry_price=20000.0)
        ]
    )
    
    log2 = {
        "timestamp": ts2,
        "snapshot_after": snapshot2,
        "execution_details": [],
        "indicators": {"sma": 20100.0}
    }
    
    candles_logs = [log1, log2]
    
    # 3. Run Export
    print("Exporting results...")
    exporter.export(
        backtest_id="test_run_123",
        strategy_name="TestStrategy",
        strategy_params={"param1": 10},
        candles_logs=candles_logs
    )
    
    print("\n=== Test Finished ===")

if __name__ == "__main__":
    test_exporter_logic()
