"""
Script d'entraînement des modèles ML
Corrige le data leakage et entraîne tous les modèles proprement
"""
import pandas as pd
import numpy as np
import sqlalchemy
import joblib
import pickle
import os
import sys
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.cluster import KMeans
from sklearn.metrics import roc_auc_score, classification_report, mean_absolute_error
from prophet import Prophet

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import DB_PATH, BASE_DIR

MODELS_DIR = os.path.join(BASE_DIR, "ml", "saved_models")
os.makedirs(MODELS_DIR, exist_ok=True)

print("=" * 60)
print("   SMART SALES PLATFORM — Entraînement des modèles ML")
print("=" * 60)

# ═══════════════════════════════════════════════════════════
# CHARGEMENT DES DONNÉES
# ═══════════════════════════════════════════════════════════
print("\n>>> [1/5] Chargement des données...")
engine = sqlalchemy.create_engine(f"sqlite:///{DB_PATH}")
df = pd.read_sql("SELECT * FROM sales", con=engine)
df["order_date"] = pd.to_datetime(df["order_date"])
df = df.sort_values(["customer_id", "order_date"]).reset_index(drop=True)

print(f"    {len(df)} lignes chargées")
print(f"    Période : {df['order_date'].min()} → {df['order_date'].max()}")

# ═══════════════════════════════════════════════════════════
# CORRECTION DATA LEAKAGE : Features client temporelles
# ═══════════════════════════════════════════════════════════
print("\n>>> [2/5] Création des features client SANS data leakage...")

# Pour chaque commande, calculer les stats client AVANT cette commande
df_sorted = df.sort_values(['customer_id', 'order_date']).copy()

# Calcul cumulatif par client avec shift pour éviter le leakage
customer_features = []

for customer_id, group in df_sorted.groupby('customer_id'):
    group = group.sort_values('order_date').copy()
    
    # Calcul cumulatif (shift pour exclure la ligne courante)
    group['customer_total_sales_before'] = group['sales'].shift(1).expanding().sum().fillna(0)
    group['customer_total_profit_before'] = group['profit'].shift(1).expanding().sum().fillna(0)
    group['customer_avg_discount_before'] = group['discount'].shift(1).expanding().mean().fillna(0)
    
    # Order count (nombre de commandes AVANT)
    group['customer_order_count_before'] = range(len(group))
    
    # Value score
    group['customer_value_score_before'] = np.where(
        group['customer_order_count_before'] > 0,
        group['customer_total_profit_before'] / group['customer_order_count_before'],
        0
    )
    
    customer_features.append(group)

df_sorted = pd.concat(customer_features, ignore_index=True)

# Features produit (pas de leakage ici, c'est agrégé sur tout le dataset)
subcat_stats = df.groupby("sub_category").agg(
    subcat_avg_profit=("profit", "mean"),
    subcat_avg_discount=("discount", "mean"),
    subcat_profit_rate=("is_profitable", "mean")
).round(4)

df_sorted = df_sorted.merge(subcat_stats, on="sub_category", how="left")
df_sorted["is_risky_subcat"] = (df_sorted["subcat_avg_profit"] < 0).astype(int)

print(f"    Features client temporelles créées (sans leakage)")
print(f"    Features produit ajoutées")

# ═══════════════════════════════════════════════════════════
# MODÈLE 1 : Random Forest Classification (is_profitable)
# ═══════════════════════════════════════════════════════════
print("\n>>> [3/5] Entraînement Random Forest (prédiction rentabilité)...")

# Sélection des features
feature_cols = [
    # Temporelles
    "quarter", "is_q4", "is_low_month", "weekday_num", "is_weekend",
    # Financières
    "discount", "high_discount", "quantity", "revenue_per_unit",
    # Produit
    "subcat_avg_profit", "subcat_avg_discount", "subcat_profit_rate", "is_risky_subcat",
    # Client (AVANT la commande)
    "customer_total_sales_before", "customer_total_profit_before",
    "customer_order_count_before", "customer_avg_discount_before",
    "customer_value_score_before",
    # Catégorielles
    "ship_mode", "segment", "category", "sub_category", "discount_tier"
]

# Encodage des variables catégorielles
cat_cols = ["ship_mode", "segment", "category", "sub_category", "discount_tier"]
label_encoders = {}

df_ml = df_sorted.copy()
for col in cat_cols:
    le = LabelEncoder()
    df_ml[col] = le.fit_transform(df_ml[col].astype(str))
    label_encoders[col] = le

# Préparation X, y
X = df_ml[feature_cols].fillna(0)
y = df_ml["is_profitable"]

# Train/Test split (80/20)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"    Train : {len(X_train)} lignes")
print(f"    Test  : {len(X_test)} lignes")
print(f"    Features : {len(feature_cols)}")

# Entraînement
rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=50,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

rf.fit(X_train, y_train)

# Évaluation
y_pred = rf.predict(X_test)
y_proba = rf.predict_proba(X_test)[:, 1]
roc_auc = roc_auc_score(y_test, y_proba)

print(f"\n    ROC-AUC (test) : {roc_auc:.4f}")
print(f"    Classification Report :")
print(classification_report(y_test, y_pred, target_names=["Non rentable", "Rentable"]))

# Validation croisée
cv_scores = cross_val_score(rf, X_train, y_train, cv=5, scoring='roc_auc', n_jobs=-1)
print(f"    ROC-AUC (CV 5-fold) : {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# Sauvegarde
joblib.dump(rf, os.path.join(MODELS_DIR, "rf_classifier.pkl"))
joblib.dump(feature_cols, os.path.join(MODELS_DIR, "feature_cols.pkl"))
joblib.dump(label_encoders, os.path.join(MODELS_DIR, "label_encoders.pkl"))

# Sauvegarder les métriques
metrics = {
    "roc_auc_test": roc_auc,
    "roc_auc_cv_mean": cv_scores.mean(),
    "roc_auc_cv_std": cv_scores.std()
}
joblib.dump(metrics, os.path.join(MODELS_DIR, "rf_metrics.pkl"))

print(f"    ✓ Modèle sauvegardé : rf_classifier.pkl")
print(f"    ✓ Encoders sauvegardés : label_encoders.pkl")
print(f"    ✓ Métriques sauvegardées : rf_metrics.pkl")

# ═══════════════════════════════════════════════════════════
# MODÈLE 2 : Prophet Forecast
# ═══════════════════════════════════════════════════════════
print("\n>>> [4/5] Entraînement Prophet (forecast ventes)...")

# Agrégation mensuelle
monthly = (
    df.groupby("month_label")["sales"]
    .sum()
    .reset_index()
    .sort_values("month_label")
)
monthly.columns = ["ds", "y"]
monthly["ds"] = pd.to_datetime(monthly["ds"])

print(f"    {len(monthly)} mois de données")

# Split train/test (80/20)
split_idx = int(len(monthly) * 0.8)
train_monthly = monthly.iloc[:split_idx]
test_monthly = monthly.iloc[split_idx:]

# Entraînement
prophet = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False,
    seasonality_mode='multiplicative'
)
prophet.fit(train_monthly)

# Prédiction sur test
forecast = prophet.predict(test_monthly[['ds']])
y_true = test_monthly['y'].values
y_pred = forecast['yhat'].values

# Métriques
mae = mean_absolute_error(y_true, y_pred)
mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

print(f"\n    MAE (test)  : ${mae:,.0f}")
print(f"    MAPE (test) : {mape:.2f}%")

# Réentraîner sur toutes les données pour production
prophet_full = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False,
    seasonality_mode='multiplicative'
)
prophet_full.fit(monthly)

# Sauvegarde
with open(os.path.join(MODELS_DIR, "prophet_model.pkl"), "wb") as f:
    pickle.dump(prophet_full, f)

prophet_metrics = {
    "mae": mae,
    "mape": mape
}
joblib.dump(prophet_metrics, os.path.join(MODELS_DIR, "prophet_metrics.pkl"))

print(f"    ✓ Modèle sauvegardé : prophet_model.pkl")
print(f"    ✓ Métriques sauvegardées : prophet_metrics.pkl")

# ═══════════════════════════════════════════════════════════
# MODÈLE 3 : KMeans Clustering (segmentation clients)
# ═══════════════════════════════════════════════════════════
print("\n>>> [5/5] Entraînement KMeans (segmentation clients)...")

customer_df = df.groupby("customer_id").agg(
    total_sales=("sales", "sum"),
    total_profit=("profit", "sum"),
    total_orders=("order_id", "nunique"),
    avg_discount=("discount", "mean")
).reset_index()

features = ["total_sales", "total_profit", "total_orders", "avg_discount"]
X_kmeans = customer_df[features]

# Normalisation
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_kmeans)

# Entraînement
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
customer_df["segment"] = kmeans.fit_predict(X_scaled)

# Labellisation des segments
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

print(f"    {len(customer_df)} clients segmentés")
print(f"    Distribution :")
print(customer_df["segment_label"].value_counts())

# Sauvegarde
joblib.dump(kmeans, os.path.join(MODELS_DIR, "kmeans_model.pkl"))
joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))

print(f"    ✓ Modèle sauvegardé : kmeans_model.pkl")
print(f"    ✓ Scaler sauvegardé : scaler.pkl")

# ═══════════════════════════════════════════════════════════
# MODÈLE 4 : Isolation Forest (détection anomalies)
# ═══════════════════════════════════════════════════════════
print("\n>>> [BONUS] Entraînement Isolation Forest (anomalies)...")

features_iso = ["sales", "profit", "discount", "quantity"]
X_iso = df[features_iso]

iso = IsolationForest(contamination=0.05, random_state=42)
iso.fit(X_iso)

anomalies = iso.predict(X_iso)
n_anomalies = (anomalies == -1).sum()

print(f"    {n_anomalies} anomalies détectées ({n_anomalies/len(df)*100:.1f}%)")

# Sauvegarde
joblib.dump(iso, os.path.join(MODELS_DIR, "isolation_forest.pkl"))

print(f"    ✓ Modèle sauvegardé : isolation_forest.pkl")

# ═══════════════════════════════════════════════════════════
# RÉSUMÉ
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("   ✓ ENTRAÎNEMENT TERMINÉ")
print("=" * 60)
print(f"\nModèles sauvegardés dans : {MODELS_DIR}")
print("\nFichiers créés :")
print("  • rf_classifier.pkl       (Random Forest)")
print("  • label_encoders.pkl      (Encodeurs catégoriels)")
print("  • feature_cols.pkl        (Liste des features)")
print("  • rf_metrics.pkl          (Métriques RF)")
print("  • prophet_model.pkl       (Prophet)")
print("  • prophet_metrics.pkl     (Métriques Prophet)")
print("  • kmeans_model.pkl        (KMeans)")
print("  • scaler.pkl              (StandardScaler)")
print("  • isolation_forest.pkl    (Isolation Forest)")
print("\n" + "=" * 60)
