# SimTrading Engine

A robust and flexible Python backtesting engine designed for testing trading strategies with the SimTrading platform. It supports both local execution with your own data and remote execution connected to the SimTrading platform.

## Project Structure

The project is organized around a few key components:

```
src/simtrading/
├── backtest_engine/       # Core backtesting logic
│   ├── broker/            # Broker simulation (validation, liquidation, portfolio updates)
│   ├── entities/          # Data structures (Candle, OrderIntent, Position, etc.)
│   ├── portfolio/         # Portfolio management logic
│   ├── strategy/          # Strategy interface and context
│   └── engine.py          # Main event loop
├── remote/                # Remote execution components (client, provider, exporter)
└── runners/               # Entry points for running backtests (custom and platform)
```

## Core Components

### Broker (`BacktestBroker`)
The broker simulates a real exchange. It is responsible for:
- **Order Validation**: Checks if you have enough cash/margin to open a position.
- **Execution**: Simulates order execution (currently supports MARKET orders).
- **Liquidation**: Monitors your margin level and liquidates positions if the maintenance margin is breached.
- **Portfolio Management**: Updates cash and positions based on trades and market price updates.

### Engine (`BacktestEngine`)
The engine orchestrates the backtest. It:
- Iterates through historical data candle by candle.
- Updates the portfolio snapshot.
- Calls your strategy's `on_bar` method with the current context.
- Sends your order intents to the broker for execution.
- Logs all events for analysis.

## Usage

### 1. Installation

```bash
pip install simtrading-engine
```

### 2. Writing a Strategy

To create a strategy, you must inherit from `BaseStrategy` and implement the `on_bar` method.

```python
from simtrading import BaseStrategy
from simtrading import OrderIntent
from simtrading import Side

class MyStrategy(BaseStrategy):
    def on_bar(self, context):
        # This method is called for every timestamp in the backtest
        
        # 1. Access Data 
        # Get the current close price for a symbol
        current_price = context.candle['BTC-USD'].close
        
        # Get historical close prices (e.g., for moving average)
        closes = context.get_series('BTC-USD', 'close', limit=20)
        
        # 2. Check Portfolio
        # Check if we are already long
        if not context.is_long('BTC-USD'):
            # 3. Generate Order Intents
            # Buy 0.1 BTC
            return [
                OrderIntent(
                    symbol='BTC-USD',
                    side=Side.BUY,
                    quantity=0.1,
                    order_type='MARKET'
                )
            ]
        
        return [] # No action
```

#### Strategy Context (`StrategyContext`)
The `context` object passed to `on_bar` provides everything you need:

- **Market Data**:
    - `context.candle`: Dictionary of current candles `{symbol: Candle}`.
    - `context.past_candles`: Dictionary of historical candles.
    - `context.get_series(symbol, field, limit)`: Helper to get a list of values (e.g., closes).
    - `context.current_timestamp()`: Current timestamp.

- **Portfolio State**:
    - `context.cash`: Available cash.
    - `context.equity`: Total portfolio value.
    - `context.is_long(symbol)` / `context.is_short(symbol)`: Check position direction.
    - `context.get_position(symbol)`: Get detailed position info.

#### Inputs & Outputs
- **Input**: `context` (StrategyContext)
- **Output**: A list of `OrderIntent` objects.

### 3. Running a Backtest

#### Custom Backtest
Run a backtest on your own machine using your own custom data.

```python
from simtrading import run_custom_backtest
from simtrading import Candle

# 1. Prepare Data
# You need a dictionary mapping symbols to lists of Candle objects
candles_data = {
    'BTC-USD': [
        Candle(symbol='BTC-USD', timestamp=1000, date='2023-01-01', open=100, high=110, low=90, close=105, volume=1000),
        # ... more candles
    ]
}

# 2. Run Backtest
run_custom_backtest(
    initial_cash=10000.0,
    strategy=MyStrategy(),
    fee_rate=0.001,           # 0.1% fee
    margin_requirement=1.0,   # 1.0 = no leverage, 0.5 = 2x leverage
    candles_by_symbol=candles_data,
    output_dir="my_results"
)
```

#### Custom Backtest with Platform Export
You can run a backtest locally with your own data and automatically export the results to the SimTrading platform for visualization.

```python
run_custom_backtest(
    # ... standard parameters ...
    api_key="your-api-key",
    base_url="https://simtrading.fr",
    export_to_server=True
)
```

> **⚠️ Important Note on Visualization**: 
> When exporting results from a custom backtest using custom data (e.g., CSV files), the platform will display the Equity Curve, Trade History, and Performance Metrics correctly. 
> However, the **Price Chart** (candlestick graph) might not be displayed if:
> 1. The symbol used (e.g., "MY-CUSTOM-TOKEN") does not exist in the platform's database.
> 2. The timeframe used is not supported by the platform.
> 
> In these cases, you will still see your PnL evolution and trade list, but the trades will not be overlaid on a price chart.

#### Platform Backtest
Run a backtest using data and configuration from the SimTrading platform.

```python
from simtrading.runners.platform_runner import run_platform_backtest

run_platform_backtest(
    backtest_id="your-backtest-id",
    api_key="your-api-key",
    base_url="https://simtrading.fr",
    strategy=MyStrategy()
)
```

## Data Structures

### Candle
Represents a single bar of market data.
- `symbol`: str
- `timestamp`: int
- `date`: str
- `open`, `high`, `low`, `close`: float
- `volume`: float

### OrderIntent
Represents a request to place an order.
- `symbol`: str
- `side`: `Side.BUY` or `Side.SELL`
- `quantity`: float (must be positive)
- `order_type`: str (currently only 'MARKET')

### PortfolioSnapshot
Represents the state of your portfolio at a specific time.
- `cash`: Available liquidity.
- `equity`: Net worth (Cash + Unrealized PnL).
- `positions`: List of open positions.
