import joblib

def load_assets():
    model = joblib.load("models/sentiment_model.pkl")
    vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
    return model, vectorizer

model, vectorizer = load_assets()
