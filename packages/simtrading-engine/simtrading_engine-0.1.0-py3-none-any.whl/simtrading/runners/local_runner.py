from typing import Any, Dict, List, Optional
import os

from simtrading.backtest_engine.broker import BacktestBroker
from simtrading.backtest_engine.engine import BacktestEngine
from simtrading.backtest_engine.strategy.base import BaseStrategy
from simtrading.backtest_engine.analysis.report import write_local_backtest_analysis

def run_local_backtest(
    initial_cash: float,
    strategy: BaseStrategy,
    fee_rate: float,
    margin_requirement: float,
    save_results_locally: bool = True,
    output_dir: str = "backtest_analysis",
    verbose: bool = True,
    candles_by_symbol: Optional[Dict[str, List[Any]]] = None,
    symbols_map: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
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
