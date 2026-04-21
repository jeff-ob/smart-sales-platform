"""
Analyse RFM (Recency, Frequency, Monetary)
Segmentation des clients en 8 segments actionnables
"""
import pandas as pd
import numpy as np
import sqlalchemy
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import DB_PATH


def calculate_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les scores RFM et segmente les clients
    
    Args:
        df: DataFrame avec colonnes order_date, customer_id, sales, profit
        
    Returns:
        DataFrame avec scores RFM et segments par client
    """
    print(">>> [RFM] Calcul des scores RFM...")
    
    # Date de référence (dernière commande + 1 jour)
    reference_date = df["order_date"].max() + pd.Timedelta(days=1)
    
    # Agrégation par client
    rfm = df.groupby("customer_id").agg(
        recency=("order_date", lambda x: (reference_date - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("sales", "sum")
    ).reset_index()
    
    print(f"    {len(rfm)} clients analysés")
    
    # Scoring par quartiles (1 = pire, 4 = meilleur)
    # Pour recency : plus c'est récent (petit nombre), mieux c'est
    rfm["R_score"] = pd.qcut(rfm["recency"], q=4, labels=[4, 3, 2, 1], duplicates='drop')
    rfm["F_score"] = pd.qcut(rfm["frequency"], q=4, labels=[1, 2, 3, 4], duplicates='drop')
    rfm["M_score"] = pd.qcut(rfm["monetary"], q=4, labels=[1, 2, 3, 4], duplicates='drop')
    
    # Conversion en int
    rfm["R_score"] = rfm["R_score"].astype(int)
    rfm["F_score"] = rfm["F_score"].astype(int)
    rfm["M_score"] = rfm["M_score"].astype(int)
    
    # Score RFM pondéré (Recency 40%, Frequency 30%, Monetary 30%)
    rfm["RFM_score"] = (
        rfm["R_score"] * 0.4 +
        rfm["F_score"] * 0.3 +
        rfm["M_score"] * 0.3
    ).round(2)
    
    # Segmentation en 8 groupes actionnables
    def assign_segment(row):
        r, f, m = row["R_score"], row["F_score"], row["M_score"]
        
        # Champions : meilleurs clients (R=4, F=4, M=4)
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        
        # Loyal Customers : bons clients réguliers
        elif r >= 3 and f >= 3 and m >= 3:
            return "Loyal Customers"
        
        # Potential Loyalists : bon potentiel, augmenter fréquence
        elif r >= 3 and f <= 2 and m >= 3:
            return "Potential Loyalists"
        
        # At Risk : bons clients qui s'éloignent (URGENT)
        elif r <= 2 and f >= 3 and m >= 3:
            return "At Risk"
        
        # Can't Lose Them : meilleurs clients perdus (CRITIQUE)
        elif r <= 1 and f >= 4 and m >= 4:
            return "Can't Lose Them"
        
        # Hibernating : clients inactifs à réactiver
        elif r <= 2 and f <= 2 and m >= 2:
            return "Hibernating"
        
        # New Customers : nouveaux clients à onboarder
        elif r >= 4 and f <= 1:
            return "New Customers"
        
        # Lost : clients perdus, faible priorité
        else:
            return "Lost"
    
    rfm["segment"] = rfm.apply(assign_segment, axis=1)
    
    # Statistiques par segment
    print(f"\n    Distribution des segments :")
    segment_stats = rfm.groupby("segment").agg(
        count=("customer_id", "count"),
        avg_monetary=("monetary", "mean")
    ).sort_values("avg_monetary", ascending=False)
    
    for seg, row in segment_stats.iterrows():
        print(f"      {seg:20s} : {int(row['count']):3d} clients (${row['avg_monetary']:,.0f} moy.)")
    
    return rfm


def save_rfm_to_db(rfm_df: pd.DataFrame):
    """Sauvegarde la table RFM dans la base SQLite"""
    print("\n>>> [RFM] Sauvegarde dans la base...")
    
    engine = sqlalchemy.create_engine(f"sqlite:///{DB_PATH}")
    rfm_df.to_sql("rfm_segments", con=engine, if_exists="replace", index=False)
    
    print(f"    Table 'rfm_segments' créée ({len(rfm_df)} lignes)")


if __name__ == "__main__":
    # Test standalone
    engine = sqlalchemy.create_engine(f"sqlite:///{DB_PATH}")
    df = pd.read_sql("SELECT * FROM sales", con=engine)
    df["order_date"] = pd.to_datetime(df["order_date"])
    
    rfm = calculate_rfm(df)
    save_rfm_to_db(rfm)
    
    print("\n✓ Analyse RFM terminée")
