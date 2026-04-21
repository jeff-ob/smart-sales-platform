import pandas as pd
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import RAW_FILE

def extract_data():
    print(">>> [EXTRACT] Lecture du fichier CSV...")

    df = pd.read_csv(RAW_FILE, encoding="latin-1")

    print(f"    {len(df)} lignes chargées")
    print(f"    Colonnes : {list(df.columns)}")

    return df

if __name__ == "__main__":
    df = extract_data()
    print(df.head())