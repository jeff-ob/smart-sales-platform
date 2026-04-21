"""
Module ML - Utilisation des modèles entraînés
IMPORTANT : Ce fichier charge les modèles, il ne les entraîne PAS
Pour entraîner : python ml/train_models.py
"""
import pandas as pd
import numpy as np
import sqlalchemy
import joblib
import pickle
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import DB_PATH, BASE_DIR

MODELS_DIR = os.path.join(BASE_DIR, "ml", "saved_models")

# ─────────────────────────────────────────
# CHARGEMENT
# ─────────────────────────────────────────
def load_from_db(table="sales_features"):
    """Charge les données depuis SQLite"""
    engine = sqlalchemy.create_engine(f"sqlite:///{DB_PATH}")
    df = pd.read_sql(f"SELECT * FROM {table}", con=engine)
    return df


def load_models():
    """Charge TOUS les modèles et artefacts sauvegardés"""
    try:
        rf = joblib.load(os.path.join(MODELS_DIR, "rf_classifier.pkl"))
        label_encoders = joblib.load(os.path.join(MODELS_DIR, "label_encoders.pkl"))
        feature_cols = joblib.load(os.path.join(MODELS_DIR, "feature_cols.pkl"))
        rf_metrics = joblib.load(os.path.join(MODELS_DIR, "rf_metrics.pkl"))
        
        with open(os.path.join(MODELS_DIR, "prophet_model.pkl"), "rb") as f:
            prophet = pickle.load(f)
        prophet_metrics = joblib.load(os.path.join(MODELS_DIR, "prophet_metrics.pkl"))
        
        kmeans = joblib.load(os.path.join(MODELS_DIR, "kmeans_model.pkl"))
        scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
        
        iso_forest = joblib.load(os.path.join(MODELS_DIR, "isolation_forest.pkl"))
        
        return {
            "rf": rf,
            "label_encoders": label_encoders,
            "feature_cols": feature_cols,
            "rf_metrics": rf_metrics,
            "prophet": prophet,
            "prophet_metrics": prophet_metrics,
            "kmeans": kmeans,
            "scaler": scaler,
            "iso_forest": iso_forest
        }
    except FileNotFoundError as e:
        print(f"\n⚠️  ERREUR : Modèles non trouvés dans {MODELS_DIR}")
        print(f"    Veuillez d'abord entraîner les modèles avec :")
        print(f"    python ml/train_models.py\n")
        raise e


# ─────────────────────────────────────────
# MODÈLE 1 — Forecast Prophet
# ─────────────────────────────────────────
def forecast_sales(df: pd.DataFrame, periods=12):
    """
    Prévision des ventes mensuelles avec Prophet
    
    Args:
        df: DataFrame avec colonnes order_date, sales
        periods: Nombre de mois à prévoir
        
    Returns:
        monthly: Données historiques mensuelles
        forecast_future: Prévisions futures
        forecast: Forecast complet Prophet
        metrics: Métriques du modèle (MAE, MAPE)
    """
    from prophet import Prophet
    
    models = load_models()
    prophet = models["prophet"]
    metrics = models["prophet_metrics"]
    
    # Agrégation mensuelle
    monthly = (
        df.groupby("month_label")["sales"]
        .sum()
        .reset_index()
        .sort_values("month_label")
    )
    monthly.columns = ["ds", "y"]
    monthly["ds"] = pd.to_datetime(monthly["ds"])
    
    # Prédiction
    future = prophet.make_future_dataframe(periods=periods, freq="MS")
    forecast = prophet.predict(future)
    
    # Extraction des prévisions futures
    forecast_future = forecast[forecast["ds"] > monthly["ds"].max()][
        ["ds", "yhat", "yhat_lower", "yhat_upper"]
    ].copy()
    forecast_future.columns = ["date", "predicted_sales",
                                "lower_bound", "upper_bound"]
    forecast_future["predicted_sales"] = forecast_future["predicted_sales"].round(2)
    
    print(f">>> [ML] Prophet Forecast — {periods} mois générés")
    print(f"    MAE : ${metrics['mae']:,.0f}")
    print(f"    MAPE : {metrics['mape']:.2f}%")
    
    return monthly, forecast_future, forecast, metrics


# ─────────────────────────────────────────
# MODÈLE 2 — Classification is_profitable
# ─────────────────────────────────────────
def predict_profitability(df: pd.DataFrame):
    """
    Prédiction de rentabilité avec Random Forest
    
    Args:
        df: DataFrame avec toutes les features nécessaires
        
    Returns:
        df: DataFrame enrichi avec profit_proba et profit_predicted
    """
    models = load_models()
    rf = models["rf"]
    label_encoders = models["label_encoders"]
    feature_cols = models["feature_cols"]
    
    df = df.copy()
    
    # Encodage des colonnes catégorielles avec les encoders sauvegardés
    for col, le in label_encoders.items():
        if col in df.columns:
            # Gérer les nouvelles catégories non vues à l'entraînement
            df[col] = df[col].astype(str).apply(
                lambda x: le.transform([x])[0] if x in le.classes_ else -1
            )
    
    # Prédiction
    X = df[feature_cols].fillna(0)
    proba = rf.predict_proba(X)[:, 1]
    pred = rf.predict(X)
    
    df["profit_proba"] = proba.round(3)
    df["profit_predicted"] = pred
    
    n_flagged = (pred == 0).sum()
    print(f">>> [ML] Classification — {n_flagged} commandes "
          f"prédites non rentables / {len(df)}")
    
    return df


# ─────────────────────────────────────────
# MODÈLE 3 — Segmentation clients KMeans
# ─────────────────────────────────────────
def segment_customers(df: pd.DataFrame):
    """
    Segmentation clients avec KMeans (utilise le modèle sauvegardé)
    
    Args:
        df: DataFrame avec colonnes customer_id, sales, profit, order_id, discount
        
    Returns:
        kmeans: Modèle KMeans chargé
        scaler: StandardScaler chargé
        customer_df: DataFrame avec segments par client
    """
    models = load_models()
    kmeans = models["kmeans"]
    scaler = models["scaler"]
    
    # Agrégation par client
    customer_df = df.groupby("customer_id").agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        total_orders=("order_id", "nunique"),
        avg_discount=("discount", "mean")
    ).reset_index()
    
    features = ["total_sales", "total_profit", "total_orders", "avg_discount"]
    X = customer_df[features]
    
    # Normalisation et prédiction avec modèles sauvegardés
    X_scaled = scaler.transform(X)
    customer_df["segment"] = kmeans.predict(X_scaled)
    
    # Labellisation (même logique qu'à l'entraînement)
    segment_map = {}
    for seg in range(3):
        avg = customer_df[customer_df["segment"] == seg]["total_sales"].mean()
        segment_map[seg] = avg
    sorted_segs = sorted(segment_map, key=segment_map.get)
    labels = {
        sorted_segs[0]: "Low Value",
        sorted_segs[1]: "Mid Value",
        sorted_segs[2]: "High Value"
    }
    customer_df["segment_label"] = customer_df["segment"].map(labels)
    
    print(f">>> [ML] KMeans — {len(customer_df)} clients segmentés")
    
    return kmeans, scaler, customer_df


# ─────────────────────────────────────────
# MODÈLE 4 — Détection d'anomalies
# ─────────────────────────────────────────
def detect_anomalies(df: pd.DataFrame):
    """
    Détection d'anomalies avec Isolation Forest (utilise le modèle sauvegardé)
    
    Args:
        df: DataFrame avec colonnes sales, profit, discount, quantity
        
    Returns:
        iso: Modèle Isolation Forest chargé
        df: DataFrame enrichi avec anomaly et is_anomaly
    """
    models = load_models()
    iso = models["iso_forest"]
    
    features = ["sales", "profit", "discount", "quantity"]
    X = df[features]
    
    # Prédiction avec modèle sauvegardé
    df = df.copy()
    df["anomaly"] = iso.predict(X)
    df["is_anomaly"] = df["anomaly"] == -1
    
    print(f">>> [ML] Anomalies — {df['is_anomaly'].sum()} détectées")
    
    return iso, df


# ─────────────────────────────────────────
# RUN COMPLET (pour tests)
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("   SMART SALES PLATFORM — ML Module v2")
    print("=" * 50)
    
    try:
        df = load_from_db()
        df["order_date"] = pd.to_datetime(df["order_date"])
        
        monthly, forecast_df, _, metrics = forecast_sales(df)
        df_scored = predict_profitability(df)
        _, _, customer_df = segment_customers(df)
        _, df_anomalies = detect_anomalies(df)
        
        print("\n" + "=" * 50)
        print("   ✓ Tous les modèles chargés et opérationnels")
        print("=" * 50)
    except FileNotFoundError:
        print("\n⚠️  Veuillez d'abord entraîner les modèles :")
        print("    python ml/train_models.py")
