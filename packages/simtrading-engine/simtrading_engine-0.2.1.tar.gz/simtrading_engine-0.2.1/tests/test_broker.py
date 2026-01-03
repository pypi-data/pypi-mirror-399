import sys
import os
import unittest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from simtrading.backtest_engine.broker import BacktestBroker
from simtrading.backtest_engine.entities.candle import Candle
from simtrading.backtest_engine.entities.order_intent import OrderIntent
from simtrading.backtest_engine.entities.enums import Side, PositionSide

class TestBacktestBroker(unittest.TestCase):
    def setUp(self):
        self.initial_cash = 10000.0
        self.fee_rate = 0.001 # 0.1%
        self.margin_requirement = 1.0 # No leverage
        self.broker = BacktestBroker(
            initial_cash=self.initial_cash,
            fee_rate=self.fee_rate,
            margin_requirement=self.margin_requirement
        )

    def test_initial_state(self):
        snapshot = self.broker.get_snapshot({})
        self.assertEqual(snapshot.cash, self.initial_cash)
        self.assertEqual(snapshot.equity, self.initial_cash)
        self.assertEqual(len(snapshot.positions), 0)

    def test_buy_order_execution(self):
        # Context
        symbol = "BTC-USD"
        price = 50000.0
        quantity = 0.1
        
        candles = {
            symbol: Candle(symbol, 1000, "2023-01-01", price, price, price, price, 100)
        }
        
        # Intent
        intent = OrderIntent(
            symbol=symbol,
            side=Side.BUY,
            quantity=quantity,
            order_type="MARKET"
        )
        
        # Process
        snapshot, details = self.broker.process_bars(candles, [intent])
        
        # Verification
        # Cost = 0.1 * 50000 = 5000
        # Fee = 5000 * 0.001 = 5.0
        # Cash = 10000 - 5000 - 5 = 4995
        expected_cash = 4995.0
        
        self.assertEqual(len(details), 1)
        self.assertEqual(details[0]['status'], 'executed')
        
        self.assertAlmostEqual(snapshot.cash, expected_cash)
        # Equity should be roughly initial cash - fee (since price hasn't moved)
        self.assertAlmostEqual(snapshot.equity, 10000.0 - 5.0)
        
        self.assertEqual(len(snapshot.positions), 1)
        pos = snapshot.positions[0]
        self.assertEqual(pos.symbol, symbol)
        self.assertEqual(pos.quantity, quantity)
        self.assertEqual(pos.side, PositionSide.LONG)

    def test_insufficient_funds(self):
        symbol = "BTC-USD"
        price = 50000.0
        quantity = 1.0 # Cost 50000 > 10000
        
        candles = {
            symbol: Candle(symbol, 1000, "2023-01-01", price, price, price, price, 100)
        }
        
        intent = OrderIntent(symbol, Side.BUY, quantity)
        
        snapshot, details = self.broker.process_bars(candles, [intent])
        
        self.assertEqual(len(details), 1)
        self.assertEqual(details[0]['status'], 'rejected')
        self.assertEqual(snapshot.cash, self.initial_cash)

    def test_sell_order_execution(self):
        # First buy
        symbol = "BTC-USD"
        price = 50000.0
        quantity = 0.1
        candles = {symbol: Candle(symbol, 1000, "2023-01-01", price, price, price, price, 100)}
        
        self.broker.process_bars(candles, [OrderIntent(symbol, Side.BUY, quantity)])
        
        # Then sell half
        price2 = 55000.0 # Price goes up
        candles2 = {symbol: Candle(symbol, 2000, "2023-01-02", price2, price2, price2, price2, 100)}
        
        intent = OrderIntent(symbol, Side.SELL, quantity / 2)
        snapshot, details = self.broker.process_bars(candles2, [intent])
        
        self.assertEqual(details[0]['status'], 'executed')
        
        # Remaining position: 0.05
        self.assertEqual(len(snapshot.positions), 1)
        self.assertAlmostEqual(snapshot.positions[0].quantity, 0.05)
        
        # Check PnL roughly
        # Bought 0.1 at 50000 (Cost 5000, Fee 5)
        # Sold 0.05 at 55000 (Revenue 2750, Fee 2.75)
        # Realized PnL on 0.05: (55000 - 50000) * 0.05 = 250
        # Fees paid: 5 + 2.75 = 7.75
        # Equity should be Initial + PnL (realized + unrealized) - Fees
        # Unrealized on remaining 0.05: (55000 - 50000) * 0.05 = 250
        # Total Equity = 10000 + 250 + 250 - 7.75 = 10492.25
        self.assertAlmostEqual(snapshot.equity, 10492.25)

if __name__ == '__main__':
    unittest.main()
