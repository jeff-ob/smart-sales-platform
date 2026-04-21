import pandas as pd

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    print(">>> [TRANSFORM] Nettoyage des données...")

    # Renommage des colonnes
    df.columns = [c.strip().lower().replace(" ", "_").replace("-", "_")
                  for c in df.columns]

    # Conversion des dates
    df["order_date"] = pd.to_datetime(df["order_date"], dayfirst=False)
    df["ship_date"]  = pd.to_datetime(df["ship_date"],  dayfirst=False)

    # ── FEATURES DE BASE ─────────────────────────────
    df["delivery_days"] = (df["ship_date"] - df["order_date"]).dt.days
    df["year"]          = df["order_date"].dt.year
    df["month"]         = df["order_date"].dt.month
    df["month_label"]   = df["order_date"].dt.to_period("M").astype(str)
    
    # Profit margin avec gestion division par zéro
    import numpy as np
    df["profit_margin"] = np.where(
        df["sales"] > 0,
        (df["profit"] / df["sales"]).round(4),
        0
    )

    # ── FEATURES TEMPORELLES ─────────────────────────
    df["quarter"]      = df["order_date"].dt.quarter
    df["is_q4"]        = (df["quarter"] == 4).astype(int)
    df["is_low_month"] = (df["month"] == 2).astype(int)
    df["weekday_num"]  = df["order_date"].dt.dayofweek
    df["is_weekend"]   = (df["weekday_num"] >= 5).astype(int)

    # ── FEATURES FINANCIÈRES ─────────────────────────
    def discount_tier(d):
        if d == 0:       return "none"
        elif d <= 0.15:  return "low"
        elif d <= 0.30:  return "medium"
        else:            return "high"

    df["discount_tier"]    = df["discount"].apply(discount_tier)
    df["high_discount"]    = (df["discount"] > 0.30).astype(int)
    df["is_profitable"]    = (df["profit"] > 0).astype(int)
    df["revenue_per_unit"] = (df["sales"] / df["quantity"]).round(2)

    def margin_class(m):
        if m < 0:       return "negative"
        elif m <= 0.20: return "low"
        else:           return "good"

    df["margin_class"] = df["profit_margin"].apply(margin_class)

    # ── NETTOYAGE ────────────────────────────────────
    before = len(df)
    df = df.drop_duplicates()
    print(f"    Doublons supprimés  : {before - len(df)}")

    nulls = df.isnull().sum().sum()
    print(f"    Valeurs nulles      : {nulls}")
    print(f"    Colonnes totales    : {len(df.columns)}")
    print(f"    Lignes transformées : {len(df)}")

    return df