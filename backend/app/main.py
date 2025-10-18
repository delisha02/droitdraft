from fastapi import FastAPI
from app.db.database import engine, Base

app = FastAPI()

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to DroitDraft"}
