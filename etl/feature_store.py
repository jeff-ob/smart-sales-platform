import pandas as pd
import sqlalchemy
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import DB_PATH

def build_feature_store(df: pd.DataFrame) -> pd.DataFrame:
    print(">>> [FEATURE STORE] Calcul des features agrégées...")

    df = df.copy()
    df = df.sort_values(['customer_id', 'order_date']).reset_index(drop=True)

    # ── FEATURES CLIENT TEMPORELLES (sans data leakage) ──────
    print("    Calcul features client temporelles (sans leakage)...")
    customer_features = []

    for customer_id, group in df.groupby('customer_id'):
        group = group.sort_values('order_date').copy()
        
        # Calcul cumulatif (shift pour exclure la ligne courante)
        group['customer_total_sales_before'] = group['sales'].shift(1).expanding().sum().fillna(0)
        group['customer_total_profit_before'] = group['profit'].shift(1).expanding().sum().fillna(0)
        group['customer_avg_discount_before'] = group['discount'].shift(1).expanding().mean().fillna(0)
        
        # Order count (nombre de commandes AVANT)
        group['customer_order_count_before'] = range(len(group))
        
        # Value score
        import numpy as np
        group['customer_value_score_before'] = np.where(
            group['customer_order_count_before'] > 0,
            group['customer_total_profit_before'] / group['customer_order_count_before'],
            0
        )
        
        customer_features.append(group)

    df = pd.concat(customer_features, ignore_index=True)

    # ── FEATURES PRODUIT ─────────────────────────────
    subcat_stats = df.groupby("sub_category").agg(
        subcat_avg_profit   = ("profit",       "mean"),
        subcat_avg_discount = ("discount",     "mean"),
        subcat_profit_rate  = ("is_profitable","mean")
    ).round(4)

    df = df.merge(subcat_stats, on="sub_category", how="left")
    df["is_risky_subcat"] = (df["subcat_avg_profit"] < 0).astype(int)

    # ── FEATURES CLIENT ──────────────────────────────
    customer_stats = df.groupby("customer_id").agg(
        customer_total_sales    = ("sales",         "sum"),
        customer_total_profit   = ("profit",        "sum"),
        customer_order_count    = ("order_id",      "nunique"),
        customer_avg_discount   = ("discount",      "mean"),
        customer_profit_rate    = ("is_profitable", "mean"),
        customer_avg_order_size = ("sales",         "mean")
    ).round(2)

    customer_stats["customer_value_score"] = (
        customer_stats["customer_total_profit"] /
        customer_stats["customer_order_count"]
    ).round(2)

    customer_stats["is_risky_customer"] = (
        customer_stats["customer_total_profit"] < 0
    ).astype(int)

    df = df.merge(customer_stats, on="customer_id", how="left")

    print(f"    Features client temporelles : 5 colonnes")
    print(f"    Features produit            : 4 colonnes ajoutées")
    print(f"    Features client agrégées    : 8 colonnes ajoutées")
    print(f"    Colonnes totales            : {len(df.columns)}")

    return df

if __name__ == "__main__":
    engine = sqlalchemy.create_engine(f"sqlite:///{DB_PATH}")
    df = pd.read_sql("SELECT * FROM sales", con=engine)
    df = build_feature_store(df)
    df.to_sql("sales_features", con=engine, if_exists="replace", index=False)
    print("    Table 'sales_features' sauvegardée en base.")