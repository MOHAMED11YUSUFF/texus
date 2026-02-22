from fastapi import FastAPI
from .routes import sample

app = FastAPI(title="Hybrid Django + FastAPI")

app.include_router(sample.router)