# AskData Guidelines

## Overview

AskData will allow ordinary business users to query and visualize customers' credit ratings, risk scores, and other related data. 

## Common Guidelines
* All code will be Python >=3.13
* All code will be containerized using Docker
* All variables will be stored in a `.env` file
* All services will be built using FastAPI as the web framework with uvicorn as the ASGI server


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
* Upon container start, the backend services will first run migrations and then check if the database is initialized with data. If not, it will load initial data.


#### ETL Services



#### Data Visualization
* It will be built using Streamlit, a Python framework for building interactive web applications.
* It will provide a user-friendly interface for querying and visualizing data from the Data Warehouse.
* It will include features for filtering, sorting, and aggregating data, as well as generating charts and graphs.
* It will also include a dashboard to provide an overview of key metrics and trends in the data.