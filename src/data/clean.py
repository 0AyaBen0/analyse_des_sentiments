import pandas as pd
import re
import os

# --- Configuration ---
RAW_PATH = "data/raw/reddit.csv"
CLEAN_PATH = "data/processed/reddit_clean.csv"

def clean_text(text):
    """Nettoie le texte en retirant les URLs, mentions, caractères spéciaux et le met en minuscule."""
    text = str(text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"[^A-Za-z0-9\s]", " ", text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_dataset(input_path=RAW_PATH, output_path=CLEAN_PATH):
    """
    Lit le fichier brut, nettoie la colonne 'text', et sauvegarde le dataset nettoyé.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        print(f"Chargement des données brutes depuis {input_path} pour nettoyage...")
        df = pd.read_csv(input_path)
        
        # Assurez-vous d'avoir une colonne 'text' et 'label'
        # Ajustez si le fichier brut a des noms de colonnes différents (ex: 'comment')
        if 'clean_comment' in df.columns and 'text' not in df.columns:
            df = df.rename(columns={'clean_comment': 'text'})
        
        # Filtrer pour s'assurer d'avoir les labels [-1, 0, 1]
        df = df[df['label'].isin([-1, 0, 1])].copy()
        
    except FileNotFoundError:
        print(f"Erreur: Fichier brut non trouvé à {input_path}. Lancez 'download_data.py' d'abord.")
        return None

    print("--- Nettoyage du Texte en cours... ---")
    df["text"] = df["text"].astype(str).apply(clean_text)
    df = df[df["text"].str.len() > 0] # Supprimer les lignes vides après nettoyage

    # Sauvegarde du dataset nettoyé
    df_cleaned = df[['text', 'label']]
    df_cleaned.to_csv(output_path, index=False)
    print(f"Dataset nettoyé sauvegardé: **{len(df_cleaned)} lignes** dans {output_path}")
    print(df_cleaned.head())
    
    return df_cleaned

if __name__ == "__main__":
    clean_dataset()