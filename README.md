# askdata-demo
Our repo to work on our project for presentation/demo.
Test branch change
Test credential store



## Environment Configuration (`.env`)

All sensitive credentials and configuration parameters are stored in the `.env` file

## MongoDB Setup

- MongoDB container runs on port `27017`.
- Root username and password are set via `.env` (`MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD`).
- Initial seed scripts can be placed inside `mongo-init/` folder.

 ## test mongodb
    - docker exec -it mongodb mongosh -u root -p example --authenticationDatabase admin
    - use askdata_mongo
    - show collections
     -db.questions.find().pretty()
     - exit

## Setup & Run

1. Run `rebuild_askdata_container.sh` to build the shared container image.
2. Run `DOCKER_BUILDKIT=0 docker compose build` to build each individual service container from the shared image.
3. Run `docker compose up -d` to start all services.


### Notes

#### Ports in use by services

- **3306** - OLTP Database (MySQL)
- **3307** - Data Warehouse Database (MySQL)  
- **3308** - UI Frontend Database (MySQL)
- **5001** - Data Warehouse Backend API
- **5002** - OLTP Backend API
- **5003** - ETL Services API
- **5004** - API Backend
- **5432** - Keycloak Database (PostgreSQL)
- **8080** - Keycloak Authentication Service
- **8501** - UI Frontend (Streamlit)
- **9000** - ChromaDB Vector Database
- **11434** - Ollama AI Model Service
- **27017** - MongoDB

