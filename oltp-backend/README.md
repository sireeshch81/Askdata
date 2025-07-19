# OLTP Backend

## Overview

The OLTP Backend is a RESTful API service that provides access to the OLTP database for transactional queries. It allows users to manage and query customer financial data, including credit ratings, risk scores, payment history, and product recommendations.

## Features

- RESTful API for querying the OLTP database
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
- `GET /financial-products` - List financial products with pagination
- `GET /financial-products/{product_key}` - Get a specific financial product by key

### Fact Tables

- `GET /financial-health` - List financial health metrics with filtering and pagination
- `GET /payments` - List payment transactions with filtering and pagination
- `GET /product-recommendations` - List product recommendations with filtering and pagination
- `GET /credit-card-balances` - List credit card balances with filtering and pagination

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

Each list endpoint supports specific filtering parameters.

#### Members Endpoint

The `/members` endpoint supports:

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

#### Financial Products Endpoint

The `/financial-products` endpoint supports:

- `product_id` - Filter by product ID
- `product_name` - Filter by product name (partial match)
- `product_type` - Filter by product type (credit_card, personal_loan, mortgage, savings_account, cd, investment)
- `product_category` - Filter by product category (premium, standard, basic, secured)
- `is_active` - Filter by active status

#### Product Recommendations Endpoint

The `/product-recommendations` endpoint supports:

- `member_key` - Filter by member key
- `product_key` - Filter by product key
- `recommendation_date_key` - Filter by recommendation date key
- `recommendation_status` - Filter by recommendation status (pending, accepted, declined, expired)
- `is_expired` - Filter by expired status
- `is_high_confidence` - Filter by high confidence status

#### Credit Card Balances Endpoint

The `/credit-card-balances` endpoint supports:

- `member_key` - Filter by member key
- `card_key` - Filter by card key
- `snapshot_date_key` - Filter by snapshot date key

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

## Alembic Migrations

See `ALEMBIC_MIGRATIONS.md` for instructions on initializing Alembic, generating migrations, and applying them to your database.
