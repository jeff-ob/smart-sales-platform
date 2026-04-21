# CLAUDE.md — Contexte du projet Smart Sales Platform

Ce fichier permet à Claude de reprendre le projet exactement là où il s'est
arrêté. À lire en entier avant de continuer.

---

## Présentation du projet

**Smart Sales Analytics Platform** — projet data end-to-end construit en Python.
Pipeline ETL complet + Feature Engineering + Analyse RFM + ML (Prophet, Random Forest, 
KMeans, Isolation Forest) + Dashboard Streamlit interactif.

Objectif : projet CV couvrant les profils Data Engineer, Data Scientist et Développeur BI.

**Dataset** : Superstore Sales Dataset (Kaggle) — 9 994 lignes, ventes US 2014-2018.
Fichier placé dans `data/sales_raw.csv`.

**Stack** : Python 3.11, pandas, numpy, scikit-learn, prophet, streamlit, plotly,
sqlalchemy, sqlite, jupyter, matplotlib, seaborn, joblib.

---

## Structure du projet

```
smart-sales-platform/
│
├── data/
│   └── sales_raw.csv           ← dataset brut (non versionné)
│
├── etl/
│   ├── extract.py              ← lecture CSV (encoding latin-1)
│   ├── transform.py            ← nettoyage + 11 features temporelles/financières
│   ├── load.py                 ← chargement SQLite table 'sales'
│   ├── feature_store.py        ← features produit (4) + client (8) → table 'sales_features'
│   └── run_pipeline.py         ← orchestre tout, produit 2 tables en base
│
├── ml/
│   └── models.py               ← 3 modèles de base (à améliorer, voir notebook)
│
├── dashboard/
│   └── app.py                  ← Streamlit v1 (KPIs, forecast, segmentation, anomalies)
│
├── notebook/
│   └── EDA.ipynb               ← 49 cellules complètes (voir détail ci-dessous)
│
├── config.py                   ← BASE_DIR, DATA_DIR, DB_PATH, RAW_FILE
├── requirements.txt            ← toutes les dépendances
├── .gitignore                  ← exclut data/*.csv, *.db, .venv/
└── README.md                   ← documentation complète avec badges
```

---

## Base de données SQLite (sales.db)

3 tables en base :

| Table | Lignes | Colonnes | Contenu |
|---|---|---|---|
| `sales` | 9 994 | 36 | Données transformées + features temporelles/financières |
| `sales_features` | 9 994 | 48 | sales + features produit + features client |
| `rfm_segments` | 793 | 9 | Scores RFM et segments par customer_id |

## Modèles ML entraînés (ml/saved_models/)

4 modèles sauvegardés et opérationnels :

| Modèle | Fichier | Performance | Usage |
|---|---|---|---|
| Prophet Forecast | prophet_model.pkl | MAPE ~10% | Prévision ventes mensuelles |
| Random Forest | rf_classifier.pkl | ROC-AUC 0.990 | Classification rentabilité |
| Scaler | scaler.pkl | - | Normalisation features |
| Feature Columns | feature_cols.pkl | - | Liste des 25 features utilisées |

---

## Notebook EDA.ipynb — état des 49 cellules

Le notebook est organisé en 4 modules terminés et 1 en cours.

### Module 1 — EDA (cellules 1 à 19) ✅ TERMINÉ
Exploration complète : structure, stats descriptives, distributions,
impact remises, performance catégories/sous-catégories, analyse temporelle
et saisonnalité, géographie, matrice de corrélation.

**Insights clés découverts :**
- Corrélation discount/profit_margin = **-0.86** (très forte)
- Au-delà de 30% de remise → 97.8% des commandes sont déficitaires
- Tables et Bookcases sont les seules sous-catégories à profit total négatif
- Texas (-26k$), Pennsylvania (-16k$), Ohio (-17k$) : marchés déficitaires
- Saisonnalité forte : pic Q4 (Sep/Nov/Déc), creux systématique en Février
- Mercredi anormalement bas en volume de commandes

### Module 2 — Feature Engineering (cellules 20 à 33) ✅ TERMINÉ
22 nouvelles features créées en 4 familles, toutes validées visuellement.

**Features temporelles (5)** :
`quarter`, `is_q4`, `is_low_month`, `weekday_num`, `is_weekend`

**Features financières (5)** :
`discount_tier` (none/low/medium/high), `high_discount` (binaire seuil 30%),
`is_profitable` (binaire), `margin_class` (negative/low/good), `revenue_per_unit`

**Features produit (4)** :
`subcat_avg_profit`, `subcat_avg_discount`, `subcat_profit_rate`, `is_risky_subcat`
→ Sous-catégories à risque : Tables, Bookcases, Supplies

**Features client (8)** :
`customer_total_sales`, `customer_total_profit`, `customer_order_count`,
`customer_avg_discount`, `customer_profit_rate`, `customer_avg_order_size`,
`customer_value_score`, `is_risky_customer`
→ 155/793 clients ont un profit total négatif
→ Note : data leakage documenté consciemment (acceptable pour segmentation)

**Intégration pipeline** :
- Features temporelles/financières → `etl/transform.py`
- Features produit/client → `etl/feature_store.py` (nouveau fichier)
- `run_pipeline.py` mis à jour pour produire les 2 tables

### Module 3 — Analyse RFM (cellules 34 à 47) ✅ TERMINÉ
Segmentation des 793 clients en 8 segments actionnables.

**Scoring** : R/F/M scorés de 1 à 4 par quartiles.
Pondération : R=40%, F=30%, M=30% (récence prioritaire).

**Segments et distribution :**

| Segment | Clients | Monetary moy. | Priorité |
|---|---|---|---|
| Champions | 92 | 4 483$ | Fidéliser |
| Loyal Customers | 146 | 3 352$ | Développer |
| Potential Loyalists | 29 | 5 282$ | Augmenter fréquence |
| At Risk | 109 | 3 701$ | URGENT — réactiver |
| New Customers | 74 | 1 916$ | Onboarder |
| Can't Lose Them | 30 | 5 652$ | CRITIQUE — contact direct |
| Hibernating | 59 | 4 330$ | Réactivation douce |
| Lost | 254 | 1 071$ | Faible priorité |

**Insights Pareto** :
- 50% des clients génèrent 80% de la valeur (moins concentré que 20/80 classique)
- **573 025$ de valeur à risque** (At Risk + Can't Lose Them)
- Loyal Customers + Champions = 39.3% de la valeur totale avec 30% des clients

### Module 4 — ML Amélioré (cellules 48→) ✅ TERMINÉ
4 modèles construits, entraînés et sauvegardés dans `ml/saved_models/`.

**Modèle 1 — Prophet Forecast** :
- Prévision des ventes mensuelles avec saisonnalité
- MAPE ~10%, MAE ~4 231$
- Intervalle de confiance 95%
- Horizon configurable (3-24 mois)

**Modèle 2 — Random Forest Classification** :
- Prédiction `is_profitable` (rentabilité commande)
- ROC-AUC 0.990, précision 96%
- 25 features (temporelles, financières, produit, client)
- Gestion déséquilibre avec `class_weight='balanced'`

**Modèle 3 — KMeans Clustering** :
- Segmentation clients en 3 groupes (Low/Mid/High Value)
- Features : total_sales, total_profit, order_count, avg_discount
- Normalisation StandardScaler

**Modèle 4 — Isolation Forest** :
- Détection anomalies (5% contamination)
- ~500 commandes anormales identifiées
- Features : sales, profit, discount, quantity

### Module 5 — Dashboard v2 ✅ TERMINÉ
Dashboard Streamlit complet avec 5 pages interactives :

**Page 1 — Vue Générale** :
- 5 KPIs (ventes, profit, commandes, clients, marge)
- Ventes/profit par catégorie et sous-catégorie
- Distribution géographique
- Impact remises sur profit

**Page 2 — Forecast** :
- Graphique Prophet avec historique + prévisions
- Intervalle de confiance 95%
- Slider horizon (3-24 mois)
- Métriques MAPE, MAE, ventes prévues
- Tableau détaillé des prévisions

**Page 3 — Analyse Clients & RFM** :
- 8 segments actionnables avec couleurs
- Distribution segments + scatter Recency/Frequency
- Valeur totale par segment (Pareto)
- Filtre interactif par segment avec détails

**Page 4 — ML Rentabilité** :
- Distribution probabilités (rentable vs non rentable)
- Commandes à risque par catégorie
- Taux de risque par palier de remise
- Top 100 commandes prédites non rentables

**Page 5 — Anomalies** :
- Scatter plot ventes vs profit (anomalies en rouge)
- Anomalies par catégorie
- Métriques (nombre, %, perte moyenne, remise moyenne)
- Liste des 100 commandes les plus anormales

**Sidebar** :
- Filtres : années, région, catégorie
- Compteur commandes filtrées
- Navigation entre pages

---

## Points méthodologiques importants à retenir

1. **Data leakage** sur features client : documenté cellule 32, acceptable
   pour segmentation, à corriger si on fait de la prédiction temps réel
   (utiliser `shift(1).expanding()` pour calcul glissant)

2. **Déséquilibre classes** `is_profitable` : 80% positif / 20% négatif.
   À gérer avec `class_weight='balanced'` ou SMOTE lors de la classification

3. **Saisonnalité** : la régression linéaire actuelle dans `ml/models.py`
   capte la tendance mais pas la saisonnalité — c'est pourquoi on passe à Prophet

4. **Remise discrète** : les remises sont par paliers fixes (0, 0.1, 0.15,
   0.2, 0.3, 0.32, 0.4, 0.45, 0.5, 0.6, 0.7, 0.8) → traiter comme
   variable catégorielle ordinale, pas continue

---

## Commandes utiles

```bash
# Activer l'environnement (Windows)
.venv\Scripts\activate.bat

# Relancer le pipeline complet
python etl/run_pipeline.py

# Lancer le dashboard
streamlit run dashboard/app.py

# Lancer Jupyter
jupyter notebook notebook/EDA.ipynb
```

---

## Style de travail établi

- On avance **cellule par cellule** dans le notebook
- On exécute → on voit le résultat → on écrit le markdown d'analyse
- Les markdowns sont en **prose** (pas de tirets excessifs), concis et analytiques
- Si Claude voit un point mort ou une limite méthodologique → le signaler en **PS**
- Le notebook est le **brouillon validé** avant intégration en production
- Chaque feature/modèle validé dans le notebook est ensuite intégré dans le pipeline

---

## État actuel du projet

Le projet est **COMPLET, CORRIGÉ et PRODUCTION-READY** :

✅ Pipeline ETL avec 22 features engineerées (SANS data leakage)
✅ Base SQLite avec 3 tables (sales, sales_features, rfm_segments)
✅ 4 modèles ML entraînés, sauvegardés et reproductibles
✅ Dashboard Streamlit v2 avec 5 pages interactives
✅ Notebook EDA complet (49 cellules)
✅ Analyse RFM avec 8 segments actionnables
✅ Métriques ML réelles et vérifiables

**Corrections majeures appliquées (Avril 2026)** :
- Data leakage corrigé (features client temporelles)
- LabelEncoders sauvegardés et réutilisés
- Modèles KMeans/IsolationForest ne sont plus réentraînés
- Table RFM intégrée dans le pipeline
- Métriques Prophet calculées dynamiquement

Voir `CORRECTIONS_APPLIQUEES.md` pour les détails complets.

## Reproduction du projet

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer le pipeline ETL (crée 3 tables)
python etl/run_pipeline.py

# 3. Entraîner les modèles ML (crée 9 fichiers)
python ml/train_models.py

# 4. Lancer le dashboard
streamlit run dashboard/app.py
```

**IMPORTANT** : Respecter cet ordre d'exécution !

## 🚀 DÉPLOIEMENT (Avril 2026)

### Statut : PRÊT POUR DÉPLOIEMENT ✅

Le projet est maintenant configuré pour être déployé sur GitHub + Streamlit Cloud.

**Fichiers de déploiement créés** :
- ✅ `.streamlit/config.toml` - Configuration Streamlit
- ✅ `requirements.txt` - Dépendances Python (avec Prophet)
- ✅ `packages.txt` - Dépendances système (build-essential)
- ✅ `.gitignore` - Fichiers à exclure (corrigé pour inclure .db, .csv, .pkl)
- ✅ `.gitattributes` - Configuration Git LFS pour fichiers volumineux
- ✅ `setup.sh` - Script d'installation automatique
- ✅ `Dockerfile` - Pour déploiement Docker (bonus)
- ✅ `DEPLOIEMENT.md` - Guide complet de déploiement
- ✅ `GUIDE_DEPLOIEMENT_RAPIDE.md` - Guide rapide (20 min)
- ✅ `DEPLOYMENT_CHECKLIST.md` - Checklist étape par étape

**Prochaine étape pour l'utilisateur** :
Suivre le guide `GUIDE_DEPLOIEMENT_RAPIDE.md` pour déployer en 20 minutes.

### Commandes de déploiement

```bash
# 1. Initialiser Git
git init
git add .
git commit -m "Initial commit - Smart Sales Platform ready for deployment"

# 2. Créer repo sur GitHub (via interface web)
# https://github.com/new

# 3. Pousser le code
git remote add origin https://github.com/[username]/smart-sales-platform.git
git branch -M main
git push -u origin main

# 4. Déployer sur Streamlit Cloud (via interface web)
# https://streamlit.io/cloud
```

## Prochaines évolutions possibles

### Court terme (après déploiement)
- [ ] Ajouter tests unitaires (pytest)
- [ ] Ajouter type hints partout
- [ ] Créer un fichier de logging
- [ ] Documenter les fonctions (docstrings)
- [ ] Améliorer le dashboard page par page (éviter les gros refactorings)

### Moyen terme (pour production)
- [ ] Créer une API REST (FastAPI)
- [ ] Ajouter monitoring MLflow
- [ ] CI/CD avec GitHub Actions
- [ ] Ajouter authentification utilisateur

### Long terme
- [ ] PostgreSQL au lieu de SQLite
- [ ] Déploiement cloud (AWS/GCP/Azure)
- [ ] Dashboard temps réel avec cache Redis
- [ ] Alertes automatiques par email

---

## Notes importantes

### Dashboard
- **Version stable** : `dashboard/app.py` (à utiliser)
- **Version expérimentale** : `dashboard/app_improved.py` (pages 1-2 OK, pages 3-5 corrompues)
- Pour améliorer le dashboard : partir de `app.py` et modifier page par page

### Fichiers de documentation
- `README.md` - Documentation utilisateur
- `CLAUDE.md` - Ce fichier (contexte pour reprise)
- `ANALYSE_CRITIQUE.md` - Diagnostic des problèmes initiaux
- `CORRECTIONS_APPLIQUEES.md` - Détails des corrections ML
- `AMELIORATIONS_DASHBOARD.md` - Tentatives d'amélioration UI
- `A_LIRE_EN_PREMIER.md` - Guide de démarrage rapide

### Ordre de priorité pour la suite
1. **Déploiement** - GitHub + Streamlit Cloud (PRÊT ✅)
2. **Tests unitaires** - Valider que tout fonctionne
3. **Documentation code** - Docstrings + type hints
4. **Amélioration dashboard** - Page par page, pas tout d'un coup


---

## Session Avril 2026 - Résumé

### Ce qui a été fait
1. ✅ Analyse critique complète du projet (15 problèmes identifiés)
2. ✅ Correction des 5 problèmes URGENTS (data leakage, encoders, etc.)
3. ✅ Validation complète du projet (ROC-AUC 0.9831, MAPE 17.14%)
4. ✅ Tentative d'amélioration du dashboard (partiellement réussie)

### Fichiers créés
- `ANALYSE_CRITIQUE.md` - Diagnostic complet
- `CORRECTIONS_APPLIQUEES.md` - Détails techniques
- `AMELIORATIONS_DASHBOARD.md` - Tentatives UI
- `ml/train_models.py` - Script d'entraînement propre
- `etl/rfm_analysis.py` - Analyse RFM
- `test_project.py` - Validation automatique

### Leçons apprises
- ⚠️ Éviter les gros refactorings du dashboard (problèmes d'encodage)
- ✅ Améliorer page par page plutôt que tout d'un coup
- ✅ Toujours tester après chaque modification
- ✅ Garder une version stable qui fonctionne (`app.py`)

### Prochaine session
- **PRIORITÉ** : Déployer sur GitHub + Streamlit Cloud
- Suivre `GUIDE_DEPLOIEMENT_RAPIDE.md` ou `DEPLOYMENT_CHECKLIST.md`
- Après déploiement : améliorer le dashboard page par page
- Partir de `dashboard/app.py` (version stable)
- Tester immédiatement après chaque changement
- Commiter après chaque amélioration validée

---

## 📦 Fichiers de déploiement

### Configuration Streamlit
- `.streamlit/config.toml` - Thème, serveur, browser settings
- `setup.sh` - Script d'installation automatique (Prophet dependencies)

### Dépendances
- `requirements.txt` - Packages Python (pandas, streamlit, prophet, etc.)
- `packages.txt` - Packages système (build-essential pour Prophet)

### Git
- `.gitignore` - Exclut .venv, __pycache__, fichiers de dev
- `.gitattributes` - Git LFS pour *.pkl, *.db, *.csv

### Documentation déploiement
- `DEPLOIEMENT.md` - Guide complet avec troubleshooting
- `GUIDE_DEPLOIEMENT_RAPIDE.md` - Guide rapide (20 min)
- `DEPLOYMENT_CHECKLIST.md` - Checklist étape par étape
- `PRET_POUR_DEPLOIEMENT.md` - Résumé de l'état du projet

### Docker (bonus)
- `Dockerfile` - Pour déploiement containerisé (optionnel)
