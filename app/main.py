from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from contextlib import asynccontextmanager

from app.database import get_db, create_tables, StockData
from app.models import StockDataCreate, StockDataResponse, StrategyPerformance
from app.strategy import calculate_moving_average_strategy


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()  
    print("Application started successfully")
    yield
    # Shutdown code can go here if needed
    print("Application shutting down")


app = FastAPI(
    title="Trading Strategy API",
    description="API for stock data management and moving average trading strategy",
    version="1.0.0",
    lifespan=lifespan
)



# Root 

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Trading Strategy API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "GET /data": "Fetch all stock records",
            "POST /data": "Add new stock records",
            "GET /strategy/performance": "Get trading strategy performance"
        }
    }


# Stock Data Endpoints
@app.get("/data", response_model=List[StockDataResponse], tags=["Stock Data"])
async def get_all_data(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Fetch all stock data records (with optional pagination)"""
    try:
        records = db.query(StockData).offset(skip).limit(limit).all()
        if not records and skip == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No stock data found. Please load data first."
            )
        return records
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching data: {str(e)}"
        )


@app.post("/data", response_model=StockDataResponse, status_code=status.HTTP_201_CREATED, tags=["Stock Data"])
async def add_stock_data(stock_data: StockDataCreate, db: Session = Depends(get_db)):
    """Add a new stock data record"""
    try:
        db_stock = StockData(
            trade_timestamp=stock_data.trade_timestamp,
            open=stock_data.open,
            high=stock_data.high,
            low=stock_data.low,
            close=stock_data.close,
            volume=stock_data.volume,
            instrument=stock_data.instrument
        )
        db.add(db_stock)
        db.commit()
        db.refresh(db_stock)
        return db_stock
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding stock data: {str(e)}"
        )



# Trading Strategy Endpoint
@app.get("/strategy/performance", response_model=StrategyPerformance, tags=["Trading Strategy"])
async def get_strategy_performance(
    short_window: int = 10,
    long_window: int = 50,
    initial_capital: float = 100000.0,
    db: Session = Depends(get_db)
):
    """Calculate Moving Average Crossover strategy performance"""
    try:
        if short_window >= long_window:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Short window must be less than long window"
            )
        if short_window < 2 or long_window < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Windows must be at least 2 days"
            )

        records = db.query(StockData).order_by(StockData.trade_timestamp).all()
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No stock data found. Please load data first."
            )
        if len(records) < long_window:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough data. Need at least {long_window} records."
            )

        performance = calculate_moving_average_strategy(
            records=records,
            short_window=short_window,
            long_window=long_window,
            initial_capital=initial_capital
        )
        return performance

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating strategy: {str(e)}"
        )
