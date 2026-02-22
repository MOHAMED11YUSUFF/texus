from fastapi import FastAPI
from .routes import sample
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Hybrid Django + FastAPI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # better than "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sample.router)