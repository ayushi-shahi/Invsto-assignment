from typing import List
from app.database import StockData
from app.models import StrategyPerformance, TradingSignal


def calculate_moving_average(prices: List[float], window: int) -> List[float]:
    """Calculate simple moving average."""
    moving_averages = []

    for i in range(len(prices)):
        if i < window - 1:
            moving_averages.append(None)
        else:
            window_avg = sum(prices[i - window + 1:i + 1]) / window
            moving_averages.append(window_avg)

    return moving_averages


def calculate_moving_average_strategy(
    records: List[StockData],
    short_window: int = 10,
    long_window: int = 50,
    initial_capital: float = 100000.0
) -> StrategyPerformance:
    """Calculate Moving Average Crossover strategy."""

    # Extract correct column names
    prices = [record.close for record in records]
    dates = [record.trade_timestamp for record in records]   # ✅ FIXED

    # Moving averages
    short_ma = calculate_moving_average(prices, short_window)
    long_ma = calculate_moving_average(prices, long_window)

    signals = []
    position = None
    shares_held = 0
    cash = initial_capital

    buy_signals = 0
    sell_signals = 0

    for i in range(long_window, len(prices)):
        current_price = prices[i]
        current_date = dates[i]

        short_ma_value = short_ma[i]
        long_ma_value = long_ma[i]

        prev_short_ma = short_ma[i - 1]
        prev_long_ma = long_ma[i - 1]

        signal_type = "HOLD"

        # BUY (Golden Cross)
        if prev_short_ma <= prev_long_ma and short_ma_value > long_ma_value:
            if position is None:
                signal_type = "BUY"
                buy_signals += 1

                shares_held = cash / current_price
                cash = 0
                position = "LONG"

        # SELL (Death Cross)
        elif prev_short_ma >= prev_long_ma and short_ma_value < long_ma_value:
            if position == "LONG":
                signal_type = "SELL"
                sell_signals += 1

                cash = shares_held * current_price
                shares_held = 0
                position = None

        signals.append(
            TradingSignal(
                date=current_date,
                signal=signal_type,
                short_ma=round(short_ma_value, 2),
                long_ma=round(long_ma_value, 2),
                price=round(current_price, 2)
            )
        )

    # Final capital
    final_capital = cash if position is None else shares_held * prices[-1]

    total_return = ((final_capital - initial_capital) / initial_capital) * 100
    total_profit_loss = final_capital - initial_capital

    significant_signals = [s for s in signals if s.signal != "HOLD"]

    return StrategyPerformance(
        strategy_name="Moving Average Crossover",
        short_window=short_window,
        long_window=long_window,
        total_signals=len(significant_signals),
        buy_signals=buy_signals,
        sell_signals=sell_signals,
        initial_capital=round(initial_capital, 2),
        final_capital=round(final_capital, 2),
        total_return=round(total_return, 2),
        total_profit_loss=round(total_profit_loss, 2),
        signals=significant_signals
    )
