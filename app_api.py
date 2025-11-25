import os
import time
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np

# config
MAX_BATCH = int(os.getenv("MAX_BATCH", "200"))
MODEL_PATH = os.getenv("MODEL_PATH", "models/sentiment_model.pkl")
VECT_PATH = os.getenv("VECT_PATH", "models/tfidf_vectorizer.pkl")

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentiment_api")

app = FastAPI(title="YouTube Sentiment API")

# CORS - in prod, remplace "*" par l'URL exacte de ton extension/site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schema
class BatchRequest(BaseModel):
    comments: List[str]

class BatchResponse(BaseModel):
    sentiments: List[int]
    confidences: List[float]
    stats: Dict[str, int]
    total: int
    inference_time_ms: float

# Load assets once
try:
    logger.info("Loading vectorizer from %s", VECT_PATH)
    vectorizer = joblib.load(VECT_PATH)
    logger.info("Loading model from %s", MODEL_PATH)
    model = joblib.load(MODEL_PATH)
    # If model supports predict_proba
    has_proba = hasattr(model, "predict_proba")
    logger.info("Model loaded. predict_proba available: %s", has_proba)
except Exception as e:
    logger.exception("Failed to load model/vectorizer: %s", e)
    # keep them None — /health will reflect the status
    vectorizer = None
    model = None
    has_proba = False

@app.get("/health")
def health():
    ok = model is not None and vectorizer is not None
    return {
        "status": "ok" if ok else "error",
        "model_loaded": model is not None,
        "vectorizer_loaded": vectorizer is not None
    }

@app.post("/predict_batch", response_model=BatchResponse)
def predict_batch(payload: BatchRequest, request: Request):
    if model is None or vectorizer is None:
        raise HTTPException(status_code=503, detail="Model or vectorizer not loaded")

    comments = payload.comments or []
    if len(comments) == 0:
        raise HTTPException(status_code=400, detail="Empty comments list")

    if len(comments) > MAX_BATCH:
        raise HTTPException(status_code=413, detail=f"Batch too large (max {MAX_BATCH})")

    start = time.time()
    try:
        X = vectorizer.transform([str(c) for c in comments])
        preds = model.predict(X)
        preds = [int(p) for p in preds]

        # confidences: try predict_proba when available, else fallback to 1.0
        if has_proba:
            probs = model.predict_proba(X)  # shape (n, n_classes)
            # map to max probability per prediction
            confidences = [float(np.max(p)) for p in probs]
        else:
            # Some models (LinearSVC) don't have predict_proba
            confidences = [1.0 for _ in preds]

        stats = {
            "1": int(sum(1 for p in preds if p == 1)),
            "0": int(sum(1 for p in preds if p == 0)),
            "-1": int(sum(1 for p in preds if p == -1)),
        }
        inference_ms = (time.time() - start) * 1000.0

        # small telemetry
        logger.info("predicted %d comments in %.1f ms from %s", len(comments), inference_ms, request.client.host)

        return {
            "sentiments": preds,
            "confidences": confidences,
            "stats": stats,
            "total": len(preds),
            "inference_time_ms": inference_ms
        }
    except Exception as e:
        logger.exception("Prediction failed: %s", e)
        raise HTTPException(status_code=500, detail="Prediction error")
