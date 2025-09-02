from fastapi import FastAPI

from src.routes.predecir import predecir

app = FastAPI()
app.include_router(predecir)
@app.get("/")
def read_root():
    return {"Hello": "World"}