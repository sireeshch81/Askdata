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
    - docker exec -it askdata-mongodb mongosh -u root -p example --authenticationDatabase admin
    - use askdata_db
    - show collections
     -db.questions.find().pretty()
     - exit

## Rebuild Docker Script

- `rebuild_docker.sh` script stops and removes project containers and images.
- It prunes unused volumes and networks.
- Then rebuilds and restarts the stack using `docker-compose up -d --build`.
- Run with: `./rebuild_docker.sh`
