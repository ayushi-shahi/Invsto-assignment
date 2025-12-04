from datetime import datetime
from app.strategy import calculate_moving_average, calculate_moving_average_strategy
from app.database import StockData
from datetime import datetime, timedelta

# Helper to make dummy stock data
def make_data(prices):
    start_date = datetime(2025, 1, 1)
    return [
        StockData(
            trade_timestamp=start_date + timedelta(days=i),
            open=p,
            high=p,
            low=p,
            close=p,
            volume=1000,
            instrument="TEST"
        )
        for i, p in enumerate(prices)
    ]



# Moving Average Tests

def test_moving_average_basic():
    assert calculate_moving_average([1,2,3,4,5], 3) == [None, None, 2.0, 3.0, 4.0]

def test_moving_average_window_too_big():
    assert calculate_moving_average([10,20], 5) == [None, None]


# Strategy Tests

def test_strategy_no_cross():
    data = make_data(list(range(1, 60)))
    result = calculate_moving_average_strategy(data, short_window=3, long_window=5)
    assert result.total_signals >= 0

def test_strategy_with_cross():
    data = make_data([10]*10 + [20]*10 + [5]*10)
    result = calculate_moving_average_strategy(data, short_window=3, long_window=5)
    assert result.buy_signals > 0
    assert result.sell_signals > 0

def test_final_capital():
    data = make_data([10,15,20,15,10,20,25,30,35,40])
    result = calculate_moving_average_strategy(data, short_window=2, long_window=3, initial_capital=1000)
    assert result.final_capital >= 0
    assert abs(result.total_profit_loss - (result.final_capital - result.initial_capital)) < 1e-6
