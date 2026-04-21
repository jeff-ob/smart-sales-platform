import pandas as pd
import sqlalchemy
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import DB_PATH

def load_data(df: pd.DataFrame):
    print(">>> [LOAD] Chargement dans la base SQLite...")

    engine = sqlalchemy.create_engine(f"sqlite:///{DB_PATH}")

    df.to_sql("sales", con=engine, if_exists="replace", index=False)

    # Vérification
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM sales"))
        count = result.fetchone()[0]
        print(f"    {count} lignes insérées dans la table 'sales'")

    print(f"    Base de données : {DB_PATH}")

if __name__ == "__main__":
    from extract import extract_data
    from transform import transform_data
    df = extract_data()
    df = transform_data(df)
    load_data(df)