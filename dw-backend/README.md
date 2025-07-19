# Data Warehouse Backend

## Overview

The Data Warehouse Backend is a RESTful API service that provides access to the data warehouse for analytical queries. It allows users to query and analyze customer financial data, including credit ratings, risk scores, payment history, and product recommendations.

## Features

- RESTful API for querying the Data Warehouse
- Endpoints for dimension tables (members, credit cards, financial products)
- Endpoints for fact tables (payments, financial health, product recommendations)
- Analytics endpoints for pre-defined views
- Filtering and pagination for all list endpoints
- Comprehensive error handling and logging

## Technology Stack

- Python 3.11
- FastAPI - Web framework
- SQLAlchemy - ORM for database interactions
- Uvicorn - ASGI server
- MySQL - Database

## API Endpoints

### Health Check

- `GET /health` - Check if the service is running

### Dimension Tables

- `GET /members` - List members with filtering and pagination
- `GET /members/{member_key}` - Get a specific member by key
- `GET /credit-cards` - List credit cards with filtering and pagination
- `GET /credit-cards/{card_key}` - Get a specific credit card by key

### Fact Tables

- `GET /financial-health` - List financial health metrics with filtering and pagination
- `GET /payments` - List payment transactions with filtering and pagination

### Analytics

- `GET /analytics/member-payment-summary` - Get member payment behavior summary
- `GET /analytics/product-recommendation-metrics` - Get product recommendation success rates
- `GET /analytics/member-health-trends` - Get member financial health trends over time

## Query Parameters

### Pagination

All list endpoints support pagination with the following parameters:

- `skip` - Number of records to skip (default: 0)
- `limit` - Maximum number of records to return (default: 100)

### Filtering

Each list endpoint supports specific filtering parameters. For example, the `/members` endpoint supports:

- `member_id` - Filter by member ID
- `first_name` - Filter by first name (partial match)
- `last_name` - Filter by last name (partial match)
- `email` - Filter by email (partial match)
- `city` - Filter by city (partial match)
- `state` - Filter by state (partial match)
- `income_bracket` - Filter by income bracket
- `employment_status` - Filter by employment status
- `member_status` - Filter by member status
- `is_current` - Filter by current status (default: true)

## Running the Service

The service is designed to run in a Docker container as part of the AskData application. It can be started using Docker Compose:

```bash
docker-compose up dw-backend
```

## Development

### Prerequisites

- Python 3.11
- pip
- MySQL

### Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables:
   ```bash
   export MYSQL_DW_USER=your_user
   export MYSQL_DW_PASSWORD=your_password
   export MYSQL_DW_HOST=localhost
   export MYSQL_DW_PORT=3306
   export MYSQL_DW_DATABASE=dw
   ```
4. Run the service:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 5002 --reload
   ```

### API Documentation

When the service is running, you can access the auto-generated API documentation at:

- Swagger UI: `http://localhost:5002/docs`
- ReDoc: `http://localhost:5002/redoc`