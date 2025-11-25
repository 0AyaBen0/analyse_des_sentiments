import pandas as pd
import os

# --- Configuration ---
URL = "https://raw.githubusercontent.com/Himanshu-1703/reddit-sentiment-analysis/refs/heads/main/data/reddit.csv" 
RAW_PATH = "data/raw/reddit.csv"
DATA_DIR = "data/raw"

def download_and_analyze_data(url=URL, path=RAW_PATH):
    os.makedirs(DATA_DIR, exist_ok=True)
    
    try:
        print(f"Téléchargement du fichier depuis {url}...")
        df = pd.read_csv(url)
        
        # 1. RENOMMER LES COLONNES ICI
        # Le fichier source utilise 'clean_comment' et 'category'
        df = df.rename(columns={'clean_comment': 'text', 'category': 'label'})
        print("Colonnes renommées : 'clean_comment' -> 'text', 'category' -> 'label'")
        
        # 2. Convertir la nouvelle colonne 'label' en entier si nécessaire (catégories sont souvent des chaînes)
        # Assurez-vous que 'category' contenait bien les valeurs -1, 0, 1.
        df['label'] = pd.to_numeric(df['label'], errors='coerce').astype('Int64')
        
        # Sauvegarde
        df.to_csv(path, index=False)
        print(f"Fichier sauvegardé dans {path}")
        
    except Exception as e:
        print(f"Erreur lors du téléchargement ou du renommage : {e}")
        # Tente de charger le fichier local s'il existe déjà
        if os.path.exists(path):
            print("Tentative de lecture du fichier existant...")
            df = pd.read_csv(path)
            # Répéter le renommage si vous lisez un fichier brut non renommé
            df = df.rename(columns={'clean_comment': 'text', 'category': 'label'})
        else:
            return None

    # --- Statistiques Initiales (Utilise maintenant la colonne 'label') ---
    print("\n--- Statistiques Initiales du Dataset ---")
    print(f"Nombre total de commentaires : **{len(df)}**")
    
    # Le filtrage fonctionne maintenant car la colonne 'label' existe
    df = df[df['label'].isin([-1, 0, 1])].copy()
    label_counts = df['label'].value_counts().sort_index()
    
    print("Distribution des labels après filtrage des labels valides:")
    print(label_counts)
    
    return df

if __name__ == "__main__":
    download_and_analyze_data()