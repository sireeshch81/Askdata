# AskData Guidelines

## Overview

AskData will allow ordinary business users to query and visualize customers' credit ratings, risk scores, and other related data. 

* Additional Content

### Components

#### OLTP Backend
* It will be a Docker containerized Python application using FastAPI as the web framework.
* It will use SQLAlchemy as the ORM to interact with a MySQL database.
* The application will expose RESTful APIs for querying and managing customer data.
* The MySQL database will be initialized with a schema defined in `oltp-schema.sql`, which will include tables for customers, credit ratings, risk scores, and other related data.
* It will run migrations and load data using Alembic, with migration scripts stored in the `migrations/` directory.
* It will have an endpoint to run migrations, and another endpoint to load data. 


#### DW Backend

#### ETL Services
* It will be Python-based, leveraging sqlalchemy to model the OLTP and DW databases.
* The initial SQLAlchemy models will be created to represent the OLTP and DW databases, they will be generated using the oltp-schema.sql and dw-schema.sql files.
* It will start by extracting data from the OLTP database, transforming it as needed, and loading it into the Data Warehouse (DW) database.
* It will be designed to handle incremental loads, meaning it will only process new or changed data since the last ETL run.
* It will include error handling and logging to ensure data integrity and traceability.
* It will also include an initial data load to populate the OLTP with generated data. (for now just a few rows, but it can be extended later with more data)
* The services will be callable via restful APIs, allowing for easy integration with other systems or applications, using FastAPI as the framework with gunicorn as the ASGI server.
* The ETL services will be designed to be modular and reusable, allowing for easy updates and additions of new data sources or transformations in the future.
* Data migrations will be managed using Alembic, and the migrations will be stored in the `migrations/` directory.
* The ETL services will be containerized using Docker, allowing for easy deployment and scaling.
* The Alembic migrations will be run automatically when the container starts, ensuring that the database schema is always up-to-date.

#### Data Warehouse
* It will be a PostgreSQL database, chosen for its robustness and support for complex queries.
* It will be designed to support analytical queries and reporting.
* It will include tables for both raw and transformed data, allowing for flexible analysis.
* It will be populated by the ETL services, ensuring that all data is up-to-date and consistent.

#### Data Visualization
* It will be built using Streamlit, a Python framework for building interactive web applications.
* It will provide a user-friendly interface for querying and visualizing data from the Data Warehouse.
* It will include features for filtering, sorting, and aggregating data, as well as generating charts and graphs.
* It will also include a dashboard to provide an overview of key metrics and trends in the data.