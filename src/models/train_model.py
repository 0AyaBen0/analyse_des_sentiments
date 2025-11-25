import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
import joblib
import time

# Charge les données
df = pd.read_csv("../data/processed/reddit_clean.csv")

df['text'] = df['text'].fillna("")

X = df['text']
y = df['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
# Vectoriseur TF-IDF optimisé
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.8
)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print("=== EXPÉRIMENTATION AVEC DIFFÉRENTS ALGORITHMES ===")

# Teste plusieurs algorithmes
models = {
    'Logistic Regression': LogisticRegression(random_state=42),
    'Random Forest': RandomForestClassifier(random_state=42),
    'SVM': SVC(random_state=42)
}

best_model = None
best_score = 0
best_name = ""

for name, model in models.items():
    print(f"\n--- {name} ---")
    model.fit(X_train_vec, y_train)
    y_pred = model.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='macro')
    print(f"Accuracy: {accuracy:.3f}")
    print(f"F1-score: {f1:.3f}")
    
    if accuracy > best_score:
        best_score = accuracy
        best_model = model
        best_name = name

print(f"\nMeilleur modèle: {best_name} (Accuracy: {best_score:.3f})")

# Optimisation des hyperparamètres pour le meilleur modèle
print("\n=== OPTIMISATION DES HYPERPARAMÈTRES ===")

if best_name == "Logistic Regression":
    param_grid = {
        'C': [0.1, 1, 10],
        'penalty': ['l1', 'l2'],
        'solver': ['liblinear']
    }
elif best_name == "Random Forest":
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5]
    }
else:  # SVM
    param_grid = {
        'C': [0.1, 1, 10],
        'kernel': ['linear', 'rbf']
    }

grid_search = GridSearchCV(best_model, param_grid, cv=3, scoring='accuracy', n_jobs=-1)
grid_search.fit(X_train_vec, y_train)

best_model = grid_search.best_estimator_
print(f"Meilleurs paramètres: {grid_search.best_params_}")

# Évaluation finale
y_pred = best_model.predict(X_test_vec)
accuracy = accuracy_score(y_test, y_pred)
f1_scores = f1_score(y_test, y_pred, average=None)

print(f"\n=== PERFORMANCE FINALE ===")
print(f"Accuracy: {accuracy:.3f}")
print(f"F1-score par classe: {f1_scores}")

# Vérifie les critères de performance
if accuracy >= 0.80:
    print("✅ Accuracy >= 80%")
else:
    print("❌ Accuracy < 80%")

if all(score > 0.75 for score in f1_scores):
    print("✅ F1-score par classe > 0.75")
else:
    print("❌ F1-score par classe <= 0.75")

# Test du temps d'inférence
batch = X_test[:50]
batch_vec = vectorizer.transform(batch)

start_time = time.time()
_ = best_model.predict(batch_vec)
inference_time = (time.time() - start_time) * 1000  # en ms

print(f"Temps d'inférence (50 commentaires): {inference_time:.2f}ms")
if inference_time < 100:
    print("✅ Temps d'inférence < 100ms")
else:
    print("❌ Temps d'inférence >= 100ms")

# Matrice de confusion
print(f"\n=== MATRICE DE CONFUSION ===")
print(confusion_matrix(y_test, y_pred))
print(f"\n=== RAPPORT DE CLASSIFICATION ===")
print(classification_report(y_test, y_pred))

# Sauvegarde
joblib.dump(best_model, 'models/sentiment_model.pkl')
joblib.dump(vectorizer, 'models/tfidf_vectorizer.pkl')
print(f"\nModèle sauvegardé: models/sentiment_model.pkl")