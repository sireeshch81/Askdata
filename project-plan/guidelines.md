# AskData Guidelines

## Overview

AskData will allow ordinary business users to query and visualize customers' credit ratings, risk scores, and other related data. 

## Common Guidelines
* All code will be Python >=3.13
* All code will be containerized using Docker
* All variables will be stored in a `.env` file
* All services' applicationas will use UV to manage the Python dependencies.
* All services will be built using FastAPI as the web framework with uvicorn as the ASGI server, unless otherwise specified.


### Components


#### OLTP Backend
* It will be a Docker containerized Python application using FastAPI as the web framework.
* It will use SQLAlchemy as the ORM to interact with a MySQL database.
* The application will expose RESTful APIs for querying and managing customer data.
* The MySQL database will be initialized with a schema defined in `oltp-schema.sql`, which will include tables for customers, credit ratings, risk scores, and other related data.
* It will run migrations and load data using Alembic, with migration scripts stored in the `migrations/` directory.
* It will have an endpoint to run migrations, and another endpoint to load data. 
* Upon container start, the backend services will first run migrations and then check if the database is initialized with data. If not, it will load initial data.


#### DW Backend
* It will be a Docker containerized Python application using FastAPI as the web framework.
* It will use SQLAlchemy as the ORM to interact with a MySQL database.
* The application will expose RESTful APIs for querying and managing customer data.
* The MySQL database will be initialized with a schema defined in `dw-schema.sql`, which will include tables for customers, credit ratings, risk scores, and other related data.
* It will run migrations and load data using Alembic, with migration scripts stored in the `migrations/` directory.
* It will have an endpoint to run migrations, and another endpoint to load data. 
* Upon container start, the backend services will first run migrations.


#### ETL Services
* This service will not be a FastAPI application, only a set of Python scripts that will run periodically on a schedule (using celery or Airflow). (Scheduler will be defined later)
* It will use SQLAlchemy as the ORM to interact with two MySQL databases.
  * One will be the OLTP database, and the other will be the Data Warehouse (DW) database.
* It will connect to the OLTP database to extract data, transform it as needed, and write it into the Data Warehouse (DW) database.
  * It will not store the data in its own database, but only write to the DW database.
  * It will store the IDs of the last processed records in a table on the datawarehouse database to ensure that it can resume from where it left off previously.
  * When the service runs, it will check the last processed record ID and only process new records that have been added since the last run.
* The `etl-services/etl-jobs/` directory will contain the ETL job scripts, which will define the extraction, transformation, and loading logic.
* It will be a Docker containerized Python application using FastAPI as the web framework.
* The application will expose RESTful APIs for managing ETL jobs.
* It will have a `/etl` endpoint to trigger the ETL jobs for now, but will be extended to use a scheduler like Celery or Airflow in the future.


#### Data Visualization
* It will be built using Streamlit, a Python framework for building interactive web applications.
* It will provide a user-friendly interface for querying and visualizing data from the Data Warehouse.
* It will include features for filtering, sorting, and aggregating data, as well as generating charts and graphs.
* It will also include a dashboard to provide an overview of key metrics and trends in the data.


#### API Backend
* It will have its dependencies managed by UV.
* It will be a Docker containerized Python application using FastAPI as the web framework, running Uvicorn as the ASGI server.
* It will use SQLAlchemy as the ORM to interact with a MySQL database.
* It will need to connect to MongoDB to retrieve user authentication data.
* It will connect to MongoDB to retrieve custom JSON data for the UI layer.
* It will use Pydantic for data validation and serialization.
* It will leverage a common .env file for configuration management.
* It will include a caching layer using Redis to improve performance for frequently accessed data. (if time permits)
* The application will expose RESTful APIs to perform actions on behalf of the ui-layer
* It will include endpoints for user authentication, customer data retrieval, and data retrieval
  * The three endpoints will be: 
    * http://api-backend/customer_detail to retrieve customer details from the OLTP database
      * It will accept a string "customer_name" as a query parameter, execute a hard-coded SQL query and return the customer details from the OLTP database in the form of:
        * {"customers": [{ "member_id", "first_name", "last_name", "email", "phone", "date_of_birth" }]}
    * http://api-backend/recommendations to retrieve recommendations from the DocumentDB database
      * It will accept a string "customer_id" as a query parameter and return the recommendations for the customer in the form of:
        * { "recommendations": [ { "id", "title", "description" } ] }
    * http://api-backend/auth to authenticate the user
      * It will accept a string "username" and "password" as query parameters and return a JWT token if the authentication is successful.
      * It will return a 401 Unauthorized error if the authentication fails.
* 