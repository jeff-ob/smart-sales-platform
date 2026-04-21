# 📊 Smart Sales Analytics Platform

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?logo=streamlit)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-orange?logo=scikit-learn)
![Prophet](https://img.shields.io/badge/Prophet-Forecasting-green)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

Plateforme d'analyse de ventes end-to-end avec pipeline ETL, feature engineering, segmentation RFM, modèles ML (Prophet, Random Forest, KMeans, Isolation Forest) et dashboard interactif Streamlit.

**🚀 [Voir le Dashboard en Ligne](#)** (à ajouter après déploiement)

---

## 🎯 Objectifs du projet

Ce projet démontre des compétences complètes en :

- **Data Engineering** : Pipeline ETL automatisé, feature store, base SQLite
- **Data Science** : Feature engineering (22 features), 4 modèles ML, analyse RFM
- **Business Intelligence** : Dashboard interactif avec 5 pages, KPIs, visualisations Plotly
- **MLOps** : Modèles sauvegardés (joblib/pickle), réutilisables, versionnés

---

## 📁 Structure du projet

```
smart-sales-platform/
│
├── data/
│   ├── sales_raw.csv              # Dataset brut (9 994 lignes)
│   └── Sample - Superstore.csv.zip
│
├── etl/
│   ├── extract.py                 # Lecture CSV (encoding latin-1)
│   ├── transform.py               # 11 features temporelles/financières
│   ├── feature_store.py           # 12 features produit/client
│   ├── load.py                    # Chargement SQLite
│   └── run_pipeline.py            # Orchestration complète
│
├── ml/
│   ├── models.py                  # 4 modèles ML (Prophet, RF, KMeans, IsoForest)
│   └── saved_models/
│       ├── prophet_model.pkl      # Modèle Prophet entraîné
│       ├── rf_classifier.pkl      # Random Forest (ROC-AUC 0.990)
│       ├── scaler.pkl             # StandardScaler
│       └── feature_cols.pkl       # Liste des 25 features
│
├── dashboard/
│   └── app.py                     # Dashboard Streamlit (5 pages)
│
├── notebook/
│   └── EDA.ipynb                  # Analyse exploratoire complète (49 cellules)
│
├── config.py                      # Configuration chemins et paramètres
├── requirements.txt               # Dépendances Python
├── sales.db                       # Base SQLite (3 tables)
├── README.md                      # Documentation principale
└── CLAUDE.md                      # Contexte détaillé pour reprise projet
```

---

## 🗄️ Base de données

**SQLite** (`sales.db`) avec 3 tables :

| Table | Lignes | Colonnes | Description |
|-------|--------|----------|-------------|
| `sales` | 9 994 | 36 | Données transformées + features temporelles/financières |
| `sales_features` | 9 994 | 48 | Données enrichies (features produit + client) |
| `rfm_segments` | 793 | 9 | Segmentation RFM (8 segments actionnables) |

---

## 🧠 Modèles Machine Learning

### 1. Prophet Forecast
- **Objectif** : Prévision des ventes mensuelles avec saisonnalité
- **Performance** : MAE $12,024, MAPE 17.14% (test set 20%)
- **Features** : Tendance + saisonnalité annuelle
- **Usage** : Horizon configurable (3-24 mois), intervalle confiance 95%

### 2. Random Forest Classifier
- **Objectif** : Prédiction de rentabilité (`is_profitable`)
- **Performance** : ROC-AUC 0.9831 (test), 0.9842 ± 0.0019 (CV 5-fold)
- **Features** : 23 features (temporelles, financières, produit, client SANS leakage)
- **Gestion déséquilibre** : `class_weight='balanced'`
- **Correction** : Features client calculées AVANT chaque commande (pas de data leakage)

### 3. KMeans Clustering
- **Objectif** : Segmentation clients en 3 groupes (Low/Mid/High Value)
- **Features** : total_sales, total_profit, order_count, avg_discount
- **Normalisation** : StandardScaler
- **Reproductibilité** : Modèle sauvegardé, pas de réentraînement

### 4. Isolation Forest
- **Objectif** : Détection d'anomalies dans les commandes
- **Contamination** : 5% (~500 commandes anormales)
- **Features** : sales, profit, discount, quantity
- **Reproductibilité** : Modèle sauvegardé, pas de réentraînement

---

## 🎨 Dashboard Streamlit

Dashboard interactif avec **5 pages** :

### 📊 Page 1 — Vue Générale
- 5 KPIs : ventes, profit, commandes, clients, marge moyenne
- Ventes/profit par catégorie et sous-catégorie
- Distribution géographique (4 régions US)
- Impact des remises sur le profit

### 📅 Page 2 — Forecast
- Graphique Prophet : historique + prévisions
- Slider horizon (3-24 mois)
- Intervalle de confiance 95%
- Métriques : MAPE, MAE, ventes prévues
- Tableau détaillé des prévisions

### 👥 Page 3 — Analyse Clients & RFM
- 8 segments actionnables (Champions, Loyal, At Risk, Can't Lose Them, etc.)
- Distribution des segments + scatter Recency/Frequency
- Valeur totale par segment (analyse Pareto)
- Filtre interactif par segment avec métriques détaillées

### 🤖 Page 4 — ML Rentabilité
- Distribution des probabilités de rentabilité
- Commandes à risque par catégorie
- Taux de risque par palier de remise
- Top 100 commandes prédites non rentables

### 🚨 Page 5 — Anomalies
- Scatter plot ventes vs profit (anomalies en rouge)
- Anomalies par catégorie
- Métriques : nombre, %, perte moyenne, remise moyenne
- Liste des 100 commandes les plus anormales

**Sidebar** : Filtres (années, région, catégorie) + compteur commandes filtrées

---

## 🚀 Installation et lancement

### Prérequis
- Python 3.11+
- pip ou conda

### Installation

```bash
# Cloner le repository
git clone https://github.com/jeff-ob/smart-sales-platform.git
cd smart-sales-platform

# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Reproduction complète du projet

**IMPORTANT** : Suivre cet ordre d'exécution

#### Étape 1 : Pipeline ETL

```bash
python etl/run_pipeline.py
```

**Sortie attendue** :
- Table `sales` créée (9 994 lignes, 36 colonnes)
- Table `sales_features` créée (9 994 lignes, 53 colonnes)
- Table `rfm_segments` créée (793 clients, 9 colonnes)

#### Étape 2 : Entraînement des modèles ML

```bash
python ml/train_models.py
```

**Sortie attendue** :
- 9 fichiers créés dans `ml/saved_models/`
- ROC-AUC : 0.9831 (Random Forest)
- MAPE : 17.14% (Prophet)
- Durée : ~30 secondes

#### Étape 3 : Lancer le dashboard

```bash
streamlit run dashboard/app.py
```

Le dashboard s'ouvre automatiquement dans votre navigateur à `http://localhost:8501`

### Lancer le notebook

```bash
jupyter notebook notebook/EDA.ipynb
```

---

## 📊 Features Engineering

### Features temporelles (5)
- `quarter` : Trimestre (1-4)
- `is_q4` : Indicateur Q4 (pic saisonnier)
- `is_low_month` : Indicateur février (creux)
- `weekday_num` : Jour de la semaine (0-6)
- `is_weekend` : Indicateur weekend

### Features financières (6)
- `discount_tier` : Palier remise (none/low/medium/high)
- `high_discount` : Remise > 30% (seuil critique)
- `is_profitable` : Commande rentable (binaire)
- `margin_class` : Classe de marge (negative/low/good)
- `revenue_per_unit` : Revenu par unité
- `profit_margin` : Marge bénéficiaire

### Features produit (4)
- `subcat_avg_profit` : Profit moyen de la sous-catégorie
- `subcat_avg_discount` : Remise moyenne de la sous-catégorie
- `subcat_profit_rate` : Taux de rentabilité de la sous-catégorie
- `is_risky_subcat` : Sous-catégorie à risque (profit < 0)

### Features client (8)
- `customer_total_sales` : Ventes totales du client
- `customer_total_profit` : Profit total du client
- `customer_order_count` : Nombre de commandes du client
- `customer_avg_discount` : Remise moyenne du client
- `customer_profit_rate` : Taux de rentabilité du client
- `customer_avg_order_size` : Taille moyenne des commandes
- `customer_value_score` : Score de valeur (profit/commande)
- `is_risky_customer` : Client à risque (profit total < 0)

---

## 📈 Insights clés

### Remises et rentabilité
- Corrélation discount/profit_margin = **-0.86** (très forte)
- Au-delà de **30% de remise** → 97.8% des commandes sont déficitaires
- Palier optimal : 0-15% de remise

### Produits à risque
- **Tables** et **Bookcases** : seules sous-catégories à profit total négatif
- **Supplies** : faible marge, volume élevé

### Géographie
- **Texas** (-26k$), **Pennsylvania** (-16k$), **Ohio** (-17k$) : marchés déficitaires
- **California** et **New York** : marchés les plus rentables

### Saisonnalité
- **Pic Q4** : Septembre, Novembre, Décembre (fêtes de fin d'année)
- **Creux Février** : baisse systématique post-fêtes
- **Mercredi** : jour anormalement bas en volume

### Clients
- **793 clients** au total
- **155 clients** (19.5%) ont un profit total négatif
- **50% des clients** génèrent **80% de la valeur** (Pareto)
- **573 025$** de valeur à risque (segments At Risk + Can't Lose Them)

---

## 🎯 Segmentation RFM

8 segments actionnables basés sur Recency, Frequency, Monetary :

| Segment | Clients | Monetary moy. | Action recommandée |
|---------|---------|---------------|-------------------|
| **Champions** | 92 | 4 483$ | Fidéliser, programmes VIP |
| **Loyal Customers** | 146 | 3 352$ | Développer, upsell |
| **Potential Loyalists** | 29 | 5 282$ | Augmenter fréquence |
| **At Risk** ⚠️ | 109 | 3 701$ | URGENT — réactiver |
| **New Customers** | 74 | 1 916$ | Onboarder, première expérience |
| **Can't Lose Them** 🚨 | 30 | 5 652$ | CRITIQUE — contact direct |
| **Hibernating** | 59 | 4 330$ | Réactivation douce |
| **Lost** | 254 | 1 071$ | Faible priorité |

**Pondération** : Recency 40%, Frequency 30%, Monetary 30%

---

## 🛠️ Technologies utilisées

| Catégorie | Technologies |
|-----------|-------------|
| **Langage** | Python 3.11 |
| **Data Processing** | pandas, numpy |
| **Machine Learning** | scikit-learn, prophet |
| **Visualisation** | plotly, matplotlib, seaborn |
| **Dashboard** | streamlit |
| **Base de données** | SQLite, sqlalchemy |
| **Notebook** | Jupyter |
| **Sérialisation** | joblib, pickle |

---

## 📝 Commandes utiles

```bash
# Activer l'environnement virtuel
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/Mac

# Relancer le pipeline ETL complet
python etl/run_pipeline.py

# Tester les modèles ML
python ml/models.py

# Lancer le dashboard
streamlit run dashboard/app.py

# Lancer Jupyter
jupyter notebook notebook/EDA.ipynb

# Installer une nouvelle dépendance
pip install <package>
pip freeze > requirements.txt
```

---

---

## 📄 License

MIT License - voir le fichier LICENSE pour plus de détails

---

## 👤 Auteur

**[Votre Nom]**
- GitHub: [@username](https://github.com/jeff-ob)
- LinkedIn: [Votre Profil](https://www.linkedin.com/in/jefferson-obanda/)
- Email: jeffobanda4@gmail.com

---

## 🙏 Remerciements

- Dataset : [Superstore Sales Dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) (Kaggle)
- Inspiration : Projets data end-to-end pour portfolio
- Stack : Communautés Python, Streamlit, scikit-learn

---

**⭐ Si ce projet vous a été utile, n'hésitez pas à lui donner une étoile !**
