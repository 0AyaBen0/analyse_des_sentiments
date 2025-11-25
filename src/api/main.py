from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.health import router as health_router
from src.api.routes.prediction import router as prediction_router

app = FastAPI(title="Sentiment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # autoriser l'extension Chrome
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(prediction_router)
