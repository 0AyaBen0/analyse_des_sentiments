from fastapi import APIRouter, HTTPException
from src.api.schemas import BatchRequest
from src.api.models_loader import model, vectorizer
import numpy as np

router = APIRouter()

@router.post("/predict_batch")
def predict_batch(payload: BatchRequest):
    if len(payload.comments) == 0:
        raise HTTPException(status_code=400, detail="Empty batch")

    try:
        X = vectorizer.transform(payload.comments)
        preds = model.predict(X)
        
        counts = {
            "-1": int(np.sum(preds == -1)),
            "0": int(np.sum(preds == 0)),
            "1": int(np.sum(preds == 1))
        }

        return {
            "sentiments": preds.tolist(),
            "stats": counts,
            "total": len(preds)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
