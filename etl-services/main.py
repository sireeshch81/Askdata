from fastapi import FastAPI
from models import Base

app = FastAPI()

@app.post("/loadOLTP")
def load_oltp():
    # TODO: Implement logic to load initial data into OLTP
    return {"message": "OLTP data loaded (stub)"}

@app.post("/loadDW")
def load_dw():
    # TODO: Implement logic to load data into DW from OLTP
    return {"message": "DW data loaded (stub)"}

@app.get("/queryOLTP")
def query_oltp():
    # TODO: Implement logic to query OLTP
    return {"message": "OLTP query result (stub)"}

@app.get("/queryDW")
def query_dw():
    # TODO: Implement logic to query DW
    return {"message": "DW query result (stub)"}

def main():
    print("Hello from etl-services!")


if __name__ == "__main__":
    main()
