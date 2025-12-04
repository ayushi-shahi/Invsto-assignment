# FastAPI Trading Strategy Assignment

## Overview

This project stores historical stock data in PostgreSQL, provides REST APIs using FastAPI, and implements a **Moving Average Crossover trading strategy**. Unit tests are included, and the project can run using Docker.

---

## Requirements

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL
- `pip` for Python dependencies

---

## Setup

### 1. Clone the repository




### 2. Install dependencies (if not using Docker)

python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt


### 3. Create a `.env` file

Add your database URL:

DATABASE_URL=postgresql://postgres:password@localhost:5432/trading_db


## 4. Using Docker

Start PostgreSQL and FastAPI together:

docker-compose up

* FastAPI runs on `http://localhost:8000`
* PostgreSQL container is `postgres-trading`

Stop containers:

docker-compose down


## 5. Load Stock Data

* Loads CSV data (`data/hindalco_data.csv`) into PostgreSQL
* Prints a sample of inserted records


## 6. API Endpoints

| Method | Endpoint                  | Description                            |
| ------ | ------------------------- | -------------------------------------- |
| GET    | `/data`                 | Fetch all stock records                |
| POST   | `/data`                 | Add a new stock record                 |
| GET    | `/strategy/performance` | Calculate trading strategy performance |


## 7. Run Tests

pytest tests/ --cov=app

* Validates API inputs
* Checks moving average strategy calculations
* Ensures test coverage
