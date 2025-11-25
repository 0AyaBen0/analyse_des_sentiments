-----

# sentiment-analysis-youtube-mlops 📊

## 📝 Description du Projet

Ce projet implémente un système MLOps complet pour l'analyse automatisée du sentiment des commentaires YouTube. L'objectif est de fournir aux créateurs de contenu un moyen rapide et objectif de quantifier la réception de leurs vidéos.

Le système est composé de trois couches principales :

1.  **ML Engine** : Modèle de Classification **Logistic Regression** entraîné sur des caractéristiques **TF-IDF**.
2.  **API Backend** : Application **FastAPI** servant le modèle.
3.  **Frontend** : **Extension Chrome** pour l'extraction des données et l'affichage des résultats.

-----

## 🏗️ Architecture Technique

[cite\_start]Le système suit une architecture MLOps standard, garantissant la reproductibilité et la scalabilité[cite: 277].

### Flux de Données

1.  L'utilisateur ouvre une vidéo YouTube.
2.  L'Extension Chrome extrait les commentaires.
3.  L'Extension envoie un *batch* de commentaires à l'API déployée.
4.  L'API utilise le Modèle ML (TF-IDF + LogReg) pour prédire le sentiment (-1, 0, 1).
5.  Les prédictions et les statistiques sont retournées à l'Extension.
6.  Les résultats sont affichés dans une interface utilisateur professionnelle (Popup Chrome).

### Structure des Dossiers

```
sentiment-analysis-youtube-mlops/
├── data/
│   ├── raw/                 # Données brutes (reddit.csv)
│   └── processed/           # Données nettoyées et splitées (train/test.csv)
├── models/                  # Modèles entraînés et vectoriseurs (.joblib)
├── src/
│   ├── data/                # Scripts de téléchargement/nettoyage/split
│   ├── models/              # Code d'entraînement et d'évaluation
│   └── api/                 # Application FastAPI (app_api.py)
├── chrome-extension/        # Fichiers du Frontend (manifest, popup.html/js/css)
├── .gitignore
├── Dockerfile               # Fichier de conteneurisation
└── requirements.txt
```

-----

## 🛠️ Instructions d'Installation

### 1\. Prérequis

  * **Python** 3.10+ 
  * **Git** 
  * **Docker Desktop** (pour le déploiement local/cloud)
  * **Google Chrome** (pour tester l'extension) 

### 2\. Configuration du Projet

```bash
# 1. Cloner le repository
git clone https://github.com/votre_nom_utilisateur/sentiment-analysis-youtube-mlops.git
cd sentiment-analysis-youtube-mlops

# 2. Créer et activer l'environnement virtuel
python -m venv venv
# Sur Windows :
.\venv\Scripts\activate
# Sur Linux/macOS :
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt
```

### 3\. Exécution du Pipeline MLOps

Exécutez les scripts suivants dans l'ordre pour préparer les données et entraîner le modèle :

```bash
# 1. Téléchargement et statistiques (Crée data/raw/reddit.csv)
python src/data/download_data.py

# 2. Nettoyage (Crée data/processed/reddit_clean.csv)
python src/data/clean_data.py

# 3. Préparation et Split (Crée data/processed/reddit_train.csv et reddit_test.csv)
python src/data/prepare_data.py

# 4. Entraînement et Sauvegarde du Modèle (Crée models/best_model.joblib et models/tfidf.joblib)
python src/models/train_model.py
```

-----

## ☁️ Déploiement et Utilisation de l'API

L'API est déployée sur **Hugging Face Spaces** à l'aide de Docker.

### 1\. Exécution Locale (Optionnel)

Pour tester l'API localement :

```bash
# 1. Construire l'image Docker (depuis la racine du projet)
docker build -t sentiment-api .

# 2. Exécuter le conteneur en mappant le port 7860
docker run -d -p 7860:7860 sentiment-api

# L'API est accessible à http://localhost:7860
```

### 2\. Endpoint de Prédiction

L'endpoint clé est `/predict_batch`.

  * **Méthode** : `POST` 
  * **URL** : `[URL_VOTRE_HUGGING_FACE_SPACE]/predict_batch`
  * **Corps de la Requête (JSON)** :
    ```json
    {
        "comments": [
            "Ce produit est génial, je l'adore!",
            "C'est correct, mais rien de spécial.",
            "Très déçu par la qualité."
        ]
    }
    ```
  * **Réponse Attendue** : Sentiments prédits et statistiques agrégées.

-----

## 🌐 Démonstration de l'Extension Chrome

L'extension permet d'interagir directement avec l'API déployée.

### 1\. Installation de l'Extension

1.  Ouvrez Google Chrome.
2.  Allez à `chrome://extensions`.
3.  Activez le **Mode développeur** (Developer Mode).
4.  Cliquez sur **"Charger l'extension non empaquetée"** (Load unpacked).
5.  Sélectionnez le dossier **`chrome-extension/`** de votre projet.

### 2\. Guide Utilisateur

1.  Ouvrez n'importe quelle vidéo YouTube.
2.  Cliquez sur l'icône de l'extension.
3.  **Entrez l'URL de votre API** (votre lien Hugging Face Space).
4.  [cite\_start]Cliquez sur **"Extract & Analyze"**[cite: 180].

L'extension effectuera les actions suivantes :

  * Extraction automatique des commentaires visibles.
  * Affichage d'un graphique à secteurs et des statistiques de répartition (Positif, Neutre, Négatif).
  * Affichage de la liste des commentaires avec le sentiment prédit et le niveau de confiance.
  * Fonctionnalités incluses : **Mode sombre** (`#darkToggle`), **Copie CSV** et **Export CSV**.


-----

## 🧑‍💻 Auteur

**Aya Bendahmane**

  * **Filière :** INDIA
  * **Année :** 2025/26
  * **Université :** ENSAM Rabat / Université Mohammed V de Rabat

-----
