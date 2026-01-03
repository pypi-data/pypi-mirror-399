import unittest
from unittest.mock import patch, MagicMock

from simtrading.runners.custom_runner import run_custom_backtest
from simtrading.backtest_engine.strategy.base import BaseStrategy
from simtrading.backtest_engine.entities.candle import Candle

class DummyStrategy(BaseStrategy):
    def on_bar(self, context):
        return []

class TestCustomRunnerExport(unittest.TestCase):
    
    @patch('simtrading.runners.custom_runner.TradeTpClient')
    @patch('simtrading.runners.custom_runner.ResultExporter')
    def test_run_custom_backtest_with_export(self, MockResultExporter, MockTradeTpClient):
        # Setup Mocks
        mock_client_instance = MockTradeTpClient.return_value
        mock_client_instance.create_backtest.return_value = "mock_backtest_id"
        
        mock_exporter_instance = MockResultExporter.return_value
        
        # Setup Data
        strategy = DummyStrategy()
        candles = {
            "BTC-USD": [
                Candle("BTC-USD", 1000, "2023-01-01", 100, 110, 90, 105, 1000)
            ]
        }
        
        # Run
        run_custom_backtest(
            initial_cash=10000,
            strategy=strategy,
            fee_rate=0.001,
            margin_requirement=1.0,
            candles_by_symbol=candles,
            save_results_locally=False,
            verbose=False,
            api_key="test_key",
            base_url="http://test.url",
            export_to_server=True
        )
        
        # Verify Client Initialization
        MockTradeTpClient.assert_called_with(base_url="http://test.url", api_key="test_key")
        
        # Verify Backtest Creation
        mock_client_instance.create_backtest.assert_called_once()
        call_args = mock_client_instance.create_backtest.call_args[0][0]
        self.assertEqual(call_args['symbols'], ["BTC-USD"])
        self.assertEqual(call_args['initial_cash'], 10000)
        self.assertEqual(call_args['strategy_name'], "DummyStrategy")
        
        # Verify Export
        MockResultExporter.assert_called_with(mock_client_instance)
        mock_exporter_instance.export.assert_called_once()
        export_args = mock_exporter_instance.export.call_args[1]
        self.assertEqual(export_args['backtest_id'], "mock_backtest_id")
        self.assertEqual(export_args['strategy_name'], "DummyStrategy")
        self.assertTrue(len(export_args['candles_logs']) > 0)

    @patch('simtrading.runners.custom_runner.TradeTpClient')
    def test_run_custom_backtest_no_export(self, MockTradeTpClient):
        strategy = DummyStrategy()
        candles = {"BTC-USD": []}
        
        run_custom_backtest(
            initial_cash=10000,
            strategy=strategy,
            fee_rate=0.001,
            margin_requirement=1.0,
            candles_by_symbol=candles,
            save_results_locally=False,
            verbose=False,
            export_to_server=False # Disabled
        )
        
        MockTradeTpClient.assert_not_called()

if __name__ == '__main__':
    unittest.main()
