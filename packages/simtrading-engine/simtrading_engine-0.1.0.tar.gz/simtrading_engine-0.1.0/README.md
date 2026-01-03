# SimTrading Engine

A lightweight and flexible Python backtesting engine designed for testing trading strategies with the SimTrading platform.

## Features

- **Event-driven Architecture**: Simulates market data replay candle by candle.
- **Strategy Interface**: Easy-to-implement `BaseStrategy` class.
- **Remote & Local Execution**: Run backtests locally or connect to a remote platform.
- **Detailed Reporting**: Generates comprehensive logs and metrics (PnL, Drawdown, etc.).

## Installation

You can install the package from PyPI:

```bash
pip install simtrading-engine
```

Or from source:

```bash
pip install -e .
```

## Usage

### Defining a Strategy

Create a new class inheriting from `BaseStrategy`:

```python
from simtrading.backtest_engine.strategy.base import BaseStrategy
from simtrading.backtest_engine.entities.order_intent import OrderIntent, OrderSide, OrderType

class MyStrategy(BaseStrategy):
    def on_bar(self, context):
        # Your logic here
        pass
```

### Running a Backtest

```python
from simtrading.runners.local_runner import run_local_backtest
# or
from simtrading.runners.remote_runner import run_remote_backtest
from my_strategy import MyStrategy

strategy = MyStrategy()

# See examples in the repository for more details.
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
