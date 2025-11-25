import pandas as pd
import os
from sklearn.model_selection import train_test_split

# --- Configuration ---
CLEAN_PATH = "data/processed/reddit_clean.csv"
TRAIN_PATH = "data/processed/reddit_train.csv"
TEST_PATH = "data/processed/reddit_test.csv"
PROCESSED_DIR = "data/processed"
RANDOM_SEED = 42 # Pour la reproductibilité

def split_and_manage_imbalance(input_path=CLEAN_PATH, train_path=TRAIN_PATH, test_path=TEST_PATH):
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    try:
        print(f"\nChargement du dataset nettoyé depuis {input_path}...")
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Erreur: Fichier nettoyé non trouvé à {input_path}. Veuillez lancer 'clean_data.py' d'abord.")
        return None, None

    # NOUVELLE ÉTAPE DE VÉRIFICATION ET DE NETTOYAGE DES TYPES
    print("--- Vérification du type de données 'text' ---")
    df['text'] = df['text'].fillna('').astype(str)
    
    # Filtrage final des lignes où le texte est vide (longueur 0)
    df = df[df['text'].str.len() > 0].copy() 

    # --- Analyse Exploratoire (EDA) ---
    print("--- Analyse Exploratoire (EDA) ---")

    # Longueur des Textes - Cette ligne fonctionne maintenant
    df['text_length'] = df['text'].apply(len)
    print(f"Longueur moyenne des textes: {df['text_length'].mean():.2f}")
    
    print(f"Distribution des classes initiales:")
    class_dist = df['label'].value_counts().sort_index()
    print(class_dist)
    print(f"Distribution des classes initiales:")
    class_dist = df['label'].value_counts().sort_index()
    print(class_dist)
    
    # Un aperçu de la distribution des longueurs est souvent utile pour la tokenisation.
    print("\nVisualisation de la distribution de la longueur des textes:")
    

 # Représentation visuelle de la distribution
    
    # --- Gestion du Déséquilibre (SANS IMBLEARN) ---
    print("\n--- Gestion du Déséquilibre (Oversampling Manuel) ---")
    
    class_dist = df['label'].value_counts()
    major_class_count = class_dist.max()
    
    # Créer une liste de DataFrames, en commençant par la classe majoritaire
    df_list = [df[df['label'] == class_dist.idxmax()]]

    is_imbalanced = False
    
    for label, count in class_dist.items():
        if count < major_class_count:
            is_imbalanced = True
            
            # Calculer le nombre d'échantillons à ajouter
            n_samples = major_class_count - count
            
            # Suréchantillonnage (échantillonnage avec remplacement) de la classe minoritaire
            df_minority = df[df['label'] == label]
            df_oversampled = df_minority.sample(
                n=n_samples, 
                replace=True, 
                random_state=RANDOM_SEED
            )
            df_list.append(df_oversampled)

    if is_imbalanced:
        # Combiner tous les DataFrames (majoritaire + minoritaires suréchantillonnées)
        df_balanced = pd.concat(df_list, axis=0).sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
        
        print("Déséquilibre détecté. Application de Suréchantillonnage Manuel.")
        print("Nouvelle distribution des labels après suréchantillonnage:")
        print(df_balanced['label'].value_counts().sort_index())
    else:
        print("Déséquilibre non significatif. Pas de suréchantillonnage appliqué.")
        df_balanced = df.copy()

    # --- Split Train/Test Reproductible ---
    print("\n--- Split Train/Test Reproductible ---")

    X = df_balanced[['text']]
    y = df_balanced['label']

    # Split: 80% Train, 20% Test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=RANDOM_SEED,
        stratify=y  # Maintient la proportion des classes dans les deux splits
    )

    # Créer et sauvegarder les DataFrames
    df_train = pd.DataFrame({'text': X_train['text'], 'label': y_train})
    df_test = pd.DataFrame({'text': X_test['text'], 'label': y_test})

    df_train.to_csv(train_path, index=False)
    df_test.to_csv(test_path, index=False)

    print(f"Split Train (80%) sauvegardé dans {train_path}: **{len(df_train)} lignes**")
    print(f"Split Test (20%) sauvegardé dans {test_path}: **{len(df_test)} lignes**")
    print("Proportions des classes dans le Train:")
    print(df_train['label'].value_counts(normalize=True).sort_index())

    return df_train, df_test

if __name__ == "__main__":
    split_and_manage_imbalance()