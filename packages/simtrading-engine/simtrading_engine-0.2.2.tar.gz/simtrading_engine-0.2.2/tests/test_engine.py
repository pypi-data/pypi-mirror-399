import sys
import os
import unittest
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from simtrading.backtest_engine.engine import BacktestEngine
from simtrading.backtest_engine.broker import BacktestBroker
from simtrading.backtest_engine.strategy.base import BaseStrategy
from simtrading.backtest_engine.entities.candle import Candle
from simtrading.backtest_engine.entities.order_intent import OrderIntent
from simtrading.backtest_engine.entities.enums import Side

class MockStrategy(BaseStrategy):
    def __init__(self):
        self.on_bar_called_count = 0
        
    def on_bar(self, context):
        self.on_bar_called_count += 1
        # Return a dummy intent on the first call
        if self.on_bar_called_count == 1:
            return [OrderIntent("BTC-USD", Side.BUY, 0.1)]
        return []

class TestBacktestEngine(unittest.TestCase):
    def setUp(self):
        self.broker = MagicMock(spec=BacktestBroker)
        # Setup broker mock returns
        self.broker.get_snapshot.return_value = MagicMock()
        self.broker.process_bars.return_value = (MagicMock(), []) # snapshot, details
        
        self.strategy = MockStrategy()
        self.engine = BacktestEngine(self.broker, self.strategy, verbose=False)

    def test_engine_loop(self):
        candles = {
            "BTC-USD": [
                Candle("BTC-USD", 1000, "2023-01-01", 100, 100, 100, 100, 100),
                Candle("BTC-USD", 2000, "2023-01-02", 100, 100, 100, 100, 100)
            ]
        }
        
        logs = self.engine.run(candles)
        
        # Verify strategy was called twice (once per timestamp)
        self.assertEqual(self.strategy.on_bar_called_count, 2)
        
        # Verify broker interactions
        # get_snapshot called twice
        self.assertEqual(self.broker.get_snapshot.call_count, 2)
        # process_bars called twice
        self.assertEqual(self.broker.process_bars.call_count, 2)
        
        # Verify logs
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0]['timestamp'], 1000)
        self.assertEqual(logs[1]['timestamp'], 2000)

if __name__ == '__main__':
    unittest.main()
