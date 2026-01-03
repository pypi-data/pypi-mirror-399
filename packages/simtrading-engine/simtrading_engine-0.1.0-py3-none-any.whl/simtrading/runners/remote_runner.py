from typing import Any, Dict
from simtrading.backtest_engine.strategy.base import BaseStrategy
from simtrading.remote.client import TradeTpClient


from simtrading.backtest_engine.analysis.report import write_local_backtest_analysis

from simtrading.backtest_engine.broker import BacktestBroker
from simtrading.backtest_engine.engine import BacktestEngine
from simtrading.remote.exporter import ResultExporter

from simtrading.remote.provider import RemoteDataProvider

import os

def run_remote_backtest(
    backtest_id: str,
    api_key: str,
    strategy: BaseStrategy,
    base_url: str,
    save_results_locally: bool = True,
    output_dir: str = "backtest_analysis",
    export_to_server: bool = True,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Exécute un backtest configuré à distance.
    """
    if not api_key or not base_url:
        raise ValueError("API key and Base URL must be provided for remote backtest.")
    
    client = TradeTpClient(base_url=base_url, api_key=api_key)
    remote_data_provider = RemoteDataProvider(client)

    # récupération de la configuration du backtest
    try:
        config = remote_data_provider.get_backtest_details(backtest_id)
    except Exception as e:
        raise RuntimeError(f"Impossible de récupérer la configuration: {e}")

    # récupération de la classe de stratégie
    if isinstance(strategy, BaseStrategy):
        strategy_instance = strategy
    else:
        raise TypeError("The provided strategy must be an instance of BaseStrategy")

    # récupération des données de marché
    try:
        candles_by_symbol = remote_data_provider.get_candles(
            symbols=config['symbols'],
            start=config['start'],
            end=config['end'],
            timeframe=config['timeframe']
        )
    except Exception as e:
        raise RuntimeError(f"Impossible de récupérer les données de marché: {e}")
    
    # configuration du broker
    try:
        broker = BacktestBroker(
            initial_cash=float(config.get('initial_cash', 10_000)),
            fee_rate=float(config.get('fee_rate', 0.001)),
            margin_requirement=float(config.get('margin_requirement', 0.5)),
        )
    except Exception as e:
        raise RuntimeError(f"Erreur lors de l'initialisation du broker: {e}")

    # exécution du backtest localement avec les données récupérées
    try: 
        engine = BacktestEngine(
            broker=broker,
            strategy=strategy_instance,
            verbose=verbose,
        )
        candles_logs = engine.run(candles_by_symbol)
    except Exception as e:
        raise RuntimeError(f"Erreur pendant l'exécution du backtest: {e}")


    # envoie des résultats au serveur distant si demandé
    if export_to_server:
        try:
            exporter = ResultExporter(client)
            
            # récupération d'informations sur la stratégie
            strategy_name = strategy_instance.__class__.__name__
            strategy_params = {
                k: v for k, v in strategy_instance.__dict__.items() 
                if not k.startswith('_') and k != 'prices'
            }
            
            exporter.export(
                backtest_id=backtest_id, 
                strategy_name=strategy_name,
                strategy_params=strategy_params,
                candles_logs=candles_logs
            )
        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'envoi des résultats: {e}")

    if save_results_locally:
        os.makedirs(output_dir, exist_ok=True)
        write_local_backtest_analysis(
            candles_logs=candles_logs,
            run_id=backtest_id,
            output_dir=output_dir,
            verbose=verbose
        )

