from typing import Any, Dict, List, Optional
from simtrading.remote.client import TradeTpClient
from simtrading.backtest_engine.entities.candle import Candle
from simtrading.backtest_engine.entities.portfolio_snapshot import PortfolioSnapshot
from simtrading.backtest_engine.entities.position import Position
from simtrading.backtest_engine.entities.order_intent import OrderIntent
from simtrading.backtest_engine.entities.enums import Side, PositionSide
from simtrading.backtest_engine.entities.trade import Trade

class ResultExporter:
    """Envoie directement les `candles_logs` (brut) vers l'API distante.

    Le serveur recevra le payload brut `{run_id, params, candles_logs}` et
    pourra effectuer son propre post-traitement/stockage.
    """

    def __init__(self, client: TradeTpClient):
        self.client = client

    def _serialize(self, obj: Any) -> Any:
        """Helper to serialize custom objects to JSON-compatible types."""
        if isinstance(obj, Candle):
            return {
                "symbol": obj.symbol,
                "timestamp": obj.timestamp,
                "open": obj.open,
                "high": obj.high,
                "low": obj.low,
                "close": obj.close,
                "volume": obj.volume
            }
        elif isinstance(obj, PortfolioSnapshot):
            # Handle positions whether it's a list or dict (just in case)
            positions_data = []
            if isinstance(obj.positions, dict):
                positions_data = [self._serialize(p) for p in obj.positions.values()]
            elif isinstance(obj.positions, list):
                positions_data = [self._serialize(p) for p in obj.positions]
            
            return {
                "timestamp": obj.timestamp,
                "cash": obj.cash,
                "equity": obj.equity,
                "positions": positions_data,
                "equity_by_symbol": getattr(obj, "equity_by_symbol", {})
            }
        elif isinstance(obj, Position):
            return {
                "symbol": obj.symbol,
                "side": obj.side.value if hasattr(obj.side, 'value') else str(obj.side),
                "quantity": obj.quantity,
                "entry_price": obj.entry_price
            }
        elif isinstance(obj, OrderIntent):
            return {
                "symbol": obj.symbol,
                "side": obj.side.value if hasattr(obj.side, 'value') else str(obj.side),
                "quantity": obj.quantity,
                "order_type": obj.order_type,
                "limit_price": obj.limit_price,
                "order_id": obj.order_id
            }
        elif isinstance(obj, Trade):
            return {
                "symbol": obj.symbol,
                "quantity": obj.quantity,
                "price": obj.price,
                "fee": obj.fee,
                "timestamp": obj.timestamp,
                "trade_id": obj.trade_id
            }
        elif isinstance(obj, (Side, PositionSide)):
            return obj.value
        elif isinstance(obj, list):
            return [self._serialize(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._serialize(v) for k, v in obj.items()}
        else:
            return obj

    def export(
        self,
        backtest_id: str,
        strategy_name: str,
        strategy_params: Dict[str, Any],
        candles_logs: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Traite les logs et envoie les résultats formatés à l'API.
        """
        
        # 1. Equity Curve & Cash Curve
        equity_curve = []
        cash_curve = []
        for log in candles_logs:
            snap = log['snapshot_after']
            
            # Calculate positions by symbol
            positions_by_symbol = {}
            for pos in snap.positions:
                sign = 1 if pos.side == PositionSide.LONG else -1
                positions_by_symbol[pos.symbol] = pos.quantity * sign

            equity_curve.append({
                "timestamp": log['timestamp'],
                "equity": snap.equity,
                "equity_by_symbol": getattr(snap, "equity_by_symbol", {}),
                "positions_by_symbol": positions_by_symbol
            })
            cash_curve.append({
                "timestamp": log['timestamp'],
                "cash": snap.cash
            })

        # 2. Orders (Intents + Executions) & Fees
        orders = []
        total_fees = 0.0
        executed_trades_count = 0

        for log in candles_logs:
            for detail in log.get("execution_details", []) or []:
                # Base structure
                order_data = {
                    "timestamp": log['timestamp'],
                    "symbol": None,
                    "side": None,
                    "quantity": None,
                    "status": detail.get("status"),
                    "reason": detail.get("reason"),
                    "price": None,
                    "fee": 0.0,
                    "trade_id": None,
                    "intent_order_type": None,
                    "intent_limit_price": None,
                    "intent_order_id": None
                }

                # Handle Intent
                intent = detail.get("intent")
                if intent:
                    order_data["symbol"] = intent.symbol
                    order_data["side"] = intent.side.value if hasattr(intent.side, 'value') else str(intent.side)
                    order_data["quantity"] = intent.quantity
                    order_data["intent_order_type"] = intent.order_type
                    order_data["intent_limit_price"] = intent.limit_price
                    order_data["intent_order_id"] = intent.order_id

                # Handle Trade (if executed or liquidated)
                trade = detail.get("trade")
                if trade:
                    order_data["symbol"] = trade.symbol # Should match intent if present
                    order_data["price"] = trade.price
                    order_data["fee"] = trade.fee
                    order_data["trade_id"] = trade.trade_id
                    order_data["timestamp"] = trade.timestamp
                    
                    # If it was a liquidation, intent is None, so we need to fill side/qty from trade
                    if not intent:
                         order_data["side"] = "BUY" if trade.quantity > 0 else "SELL"
                         order_data["quantity"] = abs(trade.quantity)

                    total_fees += trade.fee
                    executed_trades_count += 1
                
                orders.append(order_data)

        # 4. Summary Stats
        if not candles_logs:
            final_equity = 0.0
            total_return = 0.0
        else:
            # On essaie de récupérer l'equity initiale via le snapshot_before du premier log
            # Sinon on prend le snapshot_after (approximation si pas de trade au 1er tick)
            first_log = candles_logs[0]
            if 'snapshot_before' in first_log:
                initial_equity = first_log['snapshot_before'].equity
            else:
                initial_equity = first_log['snapshot_after'].equity
            
            final_equity = candles_logs[-1]['snapshot_after'].equity
            
            if initial_equity != 0:
                total_return = ((final_equity - initial_equity) / initial_equity) * 100
            else:
                total_return = 0.0

        results = {
            "total_return": total_return,
            "final_equity": final_equity,
            "total_fees": total_fees,
            "total_trades": executed_trades_count,
            "trades": orders,
            "equity_curve": equity_curve,
            "cash_curve": cash_curve,
            "logs": [], # Placeholder pour d'éventuels logs textuels
            "strategy_name": strategy_name,
            "strategy_params": strategy_params
        }

        return self.client.post_backtest_result(backtest_id, results)                
