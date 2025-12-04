import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.database import SessionLocal, create_tables, StockData

# Load environment variables
load_dotenv()


def load_csv_to_database(csv_file_path: str):
    """Load stock data from a CSV file into the database."""
    print("Creating database tables...")
    create_tables()

    print(f"Reading CSV file: {csv_file_path}")
    df = pd.read_csv(csv_file_path, sep=',')
    print(f"Loaded {len(df)} records from CSV")
    print(f"Columns: {list(df.columns)}")
    print("First few rows:")
    print(df.head())

    db = SessionLocal()
    try:
        existing_count = db.query(StockData).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} records.")
            response = input("Do you want to clear existing data and reload? (yes/no): ")
            if response.lower() == 'yes':
                print("Clearing existing data...")
                db.query(StockData).delete()
                db.commit()
            else:
                print("Skipping data load.")
                return

        print("Inserting data into database...")
        batch_size = 100
        records_inserted = 0

        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            for _, row in batch.iterrows():
                stock_data = StockData(
                    trade_timestamp=pd.to_datetime(row['datetime']),
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=int(row['volume']),
                    instrument=row.get('instrument', 'HINDALCO')
                )
                db.add(stock_data)
                records_inserted += 1

            db.commit()
            print(f"Inserted {records_inserted}/{len(df)} records", end='\r')

        print(f"\nSuccessfully inserted {records_inserted} records")

        final_count = db.query(StockData).count()
        print(f"Total records in database: {final_count}")

        print("Sample records:")
        sample = db.query(StockData).limit(5).all()
        for record in sample:
            print(f"{record.trade_timestamp.date()} | Close: {record.close} | Volume: {record.volume}")

    except Exception as e:
        print(f"Error loading data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def verify_data():
    """Print summary statistics of stock data in the database."""
    db = SessionLocal()
    try:
        total = db.query(StockData).count()
        print("\nDatabase Statistics:")
        print(f"Total records: {total}")

        if total > 0:
            first = db.query(StockData).order_by(StockData.trade_timestamp.asc()).first()
            last = db.query(StockData).order_by(StockData.trade_timestamp.desc()).first()

            print(f"Date range: {first.trade_timestamp.date()} to {last.trade_timestamp.date()}")
            print(f"First close price: {first.close}")
            print(f"Last close price: {last.close}")

            import statistics
            prices = [r.close for r in db.query(StockData).all()]
            print(f"Average close price: {statistics.mean(prices):.2f}")
            print(f"Highest close: {max(prices):.2f}")
            print(f"Lowest close: {min(prices):.2f}")
    finally:
        db.close()


if __name__ == "__main__":
    csv_path = "data/hindalco_data.csv"
    print("=" * 60)
    print("HINDALCO Stock Data Loader")
    print("=" * 60)

    load_csv_to_database(csv_path)
    verify_data()

    print("=" * 60)
    print("Data loading complete!")
    print("=" * 60)
