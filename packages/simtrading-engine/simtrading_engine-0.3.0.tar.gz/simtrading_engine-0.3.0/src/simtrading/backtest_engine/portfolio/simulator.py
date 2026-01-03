from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from simtrading.backtest_engine.entities.enums import PositionSide
from simtrading.backtest_engine.entities.position import Position
from simtrading.backtest_engine.entities.trade import Trade

@dataclass
class SimulationResult:
    success: bool
    new_cash: float
    new_positions: Dict[str, Position]
    reason: Optional[str] = None
    realized_pnl: float = 0.0

class TradeSimulator:
    """
    Responsable de la simulation de l'impact d'un trade sur le portefeuille
    et de la vérification des contraintes (marge).
    """

    def simulate(
        self,
        current_cash: float,
        current_positions: Dict[str, Position],
        trade: Trade,
        price_by_symbol: Dict[str, float],
        maintenance_margin: float,
        check_margin: bool = True
    ) -> SimulationResult:
        """
        Simule l'application d'un trade et vérifie les contraintes.
        """
        symbol = trade.symbol
        qty = float(trade.quantity)
        price = float(trade.price)
        fee = float(trade.fee)

        # --- 1. Construire un état simulé après le trade ---
        cash_after = current_cash - qty * price - fee
        realized_pnl = 0.0

        # Copie superficielle suffisante car Position est immuable
        simulated_positions = current_positions.copy()

        pos = simulated_positions.get(symbol)
        if pos is None:
            side = PositionSide.LONG if qty > 0 else PositionSide.SHORT
            new_pos = Position(symbol=symbol, side=side, quantity=abs(qty), entry_price=price)
            simulated_positions[symbol] = new_pos
        else:
            # Calculate Realized PnL if reducing position
            # Check if reducing (opposite signs)
            is_reduction = (pos.side == PositionSide.LONG and qty < 0) or (pos.side == PositionSide.SHORT and qty > 0)
            
            if is_reduction:
                closed_qty = min(pos.quantity, abs(qty))
                if pos.side == PositionSide.LONG:
                    realized_pnl += (price - pos.entry_price) * closed_qty
                else:
                    realized_pnl += (pos.entry_price - price) * closed_qty

            new_position = pos.update(qty, price)
            if new_position is None:
                del simulated_positions[symbol]
            else:
                simulated_positions[symbol] = new_position

        # --- 2. Calcul de l'equity simulée ---
        equity_after = cash_after
        for s, p in simulated_positions.items():
            p_price = price_by_symbol.get(s, p.entry_price)
            if p.side == PositionSide.LONG:
                equity_after += p_price * p.quantity
            else:
                equity_after += -p_price * abs(p.quantity)

        # --- 3. Vérification de la maintenance margin pour les shorts ---
        if check_margin:
            for s, p in simulated_positions.items():
                if p.side == PositionSide.SHORT:
                    p_price = price_by_symbol.get(s, p.entry_price)
                    notional = p_price * abs(p.quantity)
                    required_maint = notional * maintenance_margin
                    if equity_after < required_maint:
                        return SimulationResult(
                            success=False,
                            new_cash=current_cash,
                            new_positions=current_positions,
                            reason=f"Would breach maintenance margin for {s}."
                        )

        return SimulationResult(
            success=True,
            new_cash=cash_after,
            new_positions=simulated_positions,
            realized_pnl=realized_pnl
        )
