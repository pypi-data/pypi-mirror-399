from typing import Any, Dict, List, Optional
import os

from simtrading.backtest_engine.broker import BacktestBroker
from simtrading.backtest_engine.engine import BacktestEngine
from simtrading.backtest_engine.strategy.base import BaseStrategy
from simtrading.backtest_engine.analysis.report import write_local_backtest_analysis
from simtrading.remote.client import TradeTpClient
from simtrading.remote.exporter import ResultExporter

def run_custom_backtest(
    initial_cash: float,
    strategy: BaseStrategy,
    fee_rate: float,
    margin_requirement: float,
    save_results_locally: bool = True,
    output_dir: str = "backtest_analysis",
    verbose: bool = True,
    candles_by_symbol: Optional[Dict[str, List[Any]]] = None,
    symbols_map: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    export_to_server: bool = False,
) -> List[Dict[str, Any]]:
    """
    Exécute un backtest localement en utilisant des données locales.
    """

    broker = BacktestBroker(
        initial_cash=initial_cash,
        fee_rate=fee_rate,
        margin_requirement=margin_requirement,
        symbols_map=symbols_map,
    )

    engine = BacktestEngine(
        broker=broker,
        strategy=strategy,
        verbose=verbose,
    )

    candles_logs = engine.run(candles_by_symbol)
    
    run_id = os.urandom(8).hex()

    if save_results_locally:
        os.makedirs(output_dir, exist_ok=True)
        write_local_backtest_analysis(
            candles_logs,
            run_id=run_id,
            output_dir=output_dir,
            verbose=verbose
        )

    if export_to_server and api_key and base_url:
        if verbose:
            print("Exporting results to remote server...")
        
        try:
            client = TradeTpClient(base_url=base_url, api_key=api_key)
            
            # Infer metadata from candles
            symbols = list(candles_by_symbol.keys()) if candles_by_symbol else []
            
            start_ts = 0
            end_ts = 0
            if candles_by_symbol:
                all_timestamps = [c.timestamp for candles in candles_by_symbol.values() for c in candles]
                if all_timestamps:
                    start_ts = min(all_timestamps)
                    end_ts = max(all_timestamps)
            
            strategy_name = strategy.__class__.__name__
            strategy_params = {
                k: v for k, v in strategy.__dict__.items() 
                if not k.startswith('_') and k != 'prices'
            }

            backtest_config = {
                "symbols": symbols,
                "start": start_ts,
                "end": end_ts,
                "timeframe": "1d", # Defaulting to 1d
                "initial_cash": initial_cash,
                "fee_rate": fee_rate,
                "margin_requirement": margin_requirement,
                "strategy_name": strategy_name,
                "strategy_params": strategy_params
            }
            
            backtest_id = client.create_backtest(backtest_config)
            
            if verbose:
                print(f"Created remote backtest with ID: {backtest_id}")

            exporter = ResultExporter(client)
            exporter.export(
                backtest_id=backtest_id, 
                strategy_name=strategy_name,
                strategy_params=strategy_params,
                candles_logs=candles_logs
            )
            
            if verbose:
                print("Results successfully exported to server.")
                
        except Exception as e:
            print(f"Failed to export results to server: {e}")

    return candles_logs
