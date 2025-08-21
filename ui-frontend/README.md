# AskData UI Frontend

This service provides a Streamlit-based web interface for the AskData application with user authentication and customer/product search capabilities.

## Overview

The user can login and access dashboards based on their roles. The interface provides customer and product search functionality through both manual forms and natural language queries.

## API Endpoints Used

The frontend application makes calls to the following services and endpoints:

### Keycloak Authentication Service
- **Endpoint**: `http://keycloak:8080/auth`
- **Service**: Keycloak OpenID
- **Method**: POST (via keycloak library)
- **Payload**: `{"username": string, "password": string}`
- **Purpose**: User authentication and token generation

### DW Backend Service
- **Endpoint**: `http://dw-backend:5001/offer-customer`
- **Service**: Data Warehouse Backend
- **Method**: POST
- **Payload**: `{"customer_id": string}`
- **Purpose**: Create product offers for customers

### AskData API Backend Service

#### Customer Search Endpoints
- **Endpoint**: `http://askdata-api-backend:5004/customer_detail`
- **Service**: AskData API Backend
- **Method**: GET
- **Payload**: Query parameters - `{"customer_name": string, "email": string, "phone": string}`
- **Purpose**: Search customers by manual criteria

- **Endpoint**: `http://askdata-api-backend:5004/generate_sql`
- **Service**: AskData API Backend
- **Method**: POST
- **Payload**: `{"nl_query": string}`
- **Purpose**: Generate SQL from natural language customer queries

- **Endpoint**: `http://askdata-api-backend:5004/run_custom_query`
- **Service**: AskData API Backend
- **Method**: POST
- **Payload**: `{"sql_query": string}`
- **Purpose**: Execute custom SQL queries for customer data

#### Product Search Endpoints
- **Endpoint**: `http://askdata-api-backend:5004/products`
- **Service**: AskData API Backend
- **Method**: GET
- **Payload**: Query parameters - `{"product_name": string, "product_type": string, "product_category": string}`
- **Purpose**: Search products by manual criteria

- **Endpoint**: `http://askdata-api-backend:5004/generate_product_sql`
- **Service**: AskData API Backend
- **Method**: POST
- **Payload**: `{"nl_query": string}`
- **Purpose**: Generate SQL from natural language product queries

- **Endpoint**: `http://askdata-api-backend:5004/run_custom_product_query`
- **Service**: AskData API Backend
- **Method**: POST
- **Payload**: `{"sql_query": string}`
- **Purpose**: Execute custom SQL queries for product data
- **Headers**: `{"Authorization": "Bearer {access_token}"}`

### MongoDB Connection
- **Service**: MongoDB Database
- **Host**: `mongodb:27017`
- **Purpose**: Store and retrieve customer recommendations and query logs
- **Collections**: `recommendations`, `nlp_queries`, `product_queries`

## Authentication & Authorization

The application uses Keycloak for user authentication and JWT tokens for API authorization. Some endpoints require Bearer token authentication in headers.

### Exporting Keycloak realms, clients, users and roles from the keycloak container
- 1. Find the docker container id with the command 
      docker ps
      docker exec -it <container-id> bash
- 2. Run the below command to export all the keycloak data to a json file.
      /opt/keycloak/bin/kc.sh export --dir /opt/keycloak/data/import --realm <your-realm> --users realm_file

- 3. exit the docker container.

- 4. Copy the exported json file to the askdata-demo/keycloak/import/ directory.
      docker cp <container-id>:/opt/keycloak/data/import/<your-realm>-realm.json /<path/on/your/host>