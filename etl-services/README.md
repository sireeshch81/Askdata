# ETL Services

## Overview

The ETL Services component is responsible for extracting data from the OLTP database, transforming it as needed, and loading it into the Data Warehouse (DW) database. It is built as a Docker containerized Python application using FastAPI as the web framework.

## Architecture

The ETL Services component consists of the following parts:

1. **FastAPI Application**: Provides RESTful APIs for managing ETL jobs.
2. **ETL Jobs**: Python scripts that define the extraction, transformation, and loading logic for different data entities.
3. **Database Connections**: Uses SQLAlchemy to connect to both the OLTP and DW databases.
4. **Status Tracking**: Stores the IDs of the last processed records to ensure that it can resume from where it left off in case of failure.

## Components

### FastAPI Application

The main application is defined in `main.py` and provides the following endpoints:

- `GET /`: Returns a welcome message.
- `GET /health`: Returns the health status of the service.
- `POST /etl`: Triggers the ETL jobs to extract, transform, and load data.
- `GET /etl/status`: Returns the status of the last ETL job.

### ETL Jobs

The ETL jobs are defined in the `etl_jobs` directory and include:

- `member_etl.py`: ETL job for member data.
- `credit_card_etl.py`: ETL job for credit card data.
- `payment_history_etl.py`: ETL job for payment history data.
- `financial_health_etl.py`: ETL job for financial health metrics data.
- `financial_product_etl.py`: ETL job for financial product data.

Each ETL job includes three main functions:

1. `extract_*`: Extracts data from the OLTP database.
2. `transform_*`: Transforms the extracted data to fit the DW schema.
3. `load_*`: Loads the transformed data into the DW database.

### Database Connections

The database connections are defined in `database.py` and use SQLAlchemy to connect to both the OLTP and DW databases. The connection parameters are read from environment variables.

### Status Tracking

The ETL jobs store the IDs of the last processed records in a JSON file in the `etl_jobs/status` directory. This ensures that the ETL jobs can resume from where they left off in case of failure.

## Usage

### Running the ETL Service

The ETL service is included in the docker-compose.yml file and can be started with the rest of the application:

```bash
docker-compose up -d
```

### Triggering ETL Jobs

To trigger the ETL jobs, send a POST request to the `/etl` endpoint:

```bash
curl -X POST http://localhost:5009/etl
```

### Checking ETL Job Status

To check the status of the last ETL job, send a GET request to the `/etl/status` endpoint:

```bash
curl http://localhost:5009/etl/status
```

## Development

### Prerequisites

- Python 3.13 or higher
- Docker
- MySQL

### Setup

1. Clone the repository.
2. Create a virtual environment and install the dependencies:

```bash
cd etl-services
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

3. Set up the environment variables in the `.env` file.
4. Run the application:

```bash
uvicorn main:app --reload --port 5009
```

### Running Migrations

The ETL service uses Alembic for database migrations. To run the migrations:

```bash
cd etl-services
alembic upgrade head
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

