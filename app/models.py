from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional, List

class StockDataBase(BaseModel):
    trade_timestamp: datetime = Field(..., description="Timestamp of the trading day")
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: int = Field(..., gt=0)
    instrument: Optional[str] = "HINDALCO"

    @field_validator("high")
    def high_must_be_highest(cls, v, info):
        values = info.data
        if "low" in values and v < values["low"]:
            raise ValueError("high must be >= low")
        if "open" in values and v < values["open"]:
            raise ValueError("high must be >= open")
        if "close" in values and v < values.get("close", 0):
            raise ValueError("high must be >= close")
        return v

    @field_validator("low")
    def low_must_be_lowest(cls, v, info):
        values = info.data
        if "open" in values and v > values["open"]:
            raise ValueError("low must be <= open")
        return v


class StockDataCreate(StockDataBase):
    pass


class StockDataResponse(StockDataBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TradingSignal(BaseModel):
    date: datetime
    signal: str
    short_ma: float
    long_ma: float
    price: float


class StrategyPerformance(BaseModel):
    strategy_name: str = "Moving Average Crossover"
    short_window: int
    long_window: int
    total_signals: int
    buy_signals: int
    sell_signals: int
    initial_capital: float
    final_capital: float
    total_return: float
    total_profit_loss: float
    signals: List[TradingSignal]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "strategy_name": "Moving Average Crossover",
                "short_window": 10,
                "long_window": 50,
                "total_signals": 45,
                "buy_signals": 23,
                "sell_signals": 22,
                "initial_capital": 100000.0,
                "final_capital": 125000.0,
                "total_return": 25.0,
                "total_profit_loss": 25000.0,
                "signals": []
            }
        }
    )
