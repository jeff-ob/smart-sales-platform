# 📦 Modèles ML Sauvegardés

Ce dossier contient tous les artefacts nécessaires pour utiliser les modèles ML en production.

## 📁 Fichiers

| Fichier | Taille | Description |
|---------|--------|-------------|
| `rf_classifier.pkl` | ~1.1 MB | Random Forest pour prédiction rentabilité |
| `label_encoders.pkl` | ~2 KB | Encodeurs pour variables catégorielles |
| `feature_cols.pkl` | ~0.4 KB | Liste des 23 features utilisées |
| `rf_metrics.pkl` | ~0.2 KB | Métriques RF (ROC-AUC, CV scores) |
| `prophet_model.pkl` | ~13.5 KB | Modèle Prophet pour forecast ventes |
| `prophet_metrics.pkl` | ~0.1 KB | Métriques Prophet (MAE, MAPE) |
| `kmeans_model.pkl` | ~3.9 KB | KMeans pour segmentation clients |
| `scaler.pkl` | ~1.1 KB | StandardScaler pour normalisation |
| `isolation_forest.pkl` | ~948 KB | Isolation Forest pour anomalies |

**Total** : ~2.1 MB

---

## 🔄 Génération des modèles

Ces fichiers sont générés par le script d'entraînement :

```bash
python ml/train_models.py
```

**Durée** : ~30 secondes  
**Prérequis** : Base de données `sales.db` avec table `sales`

---

## 📊 Métriques des modèles

### Random Forest
- **ROC-AUC (test)** : 0.9831
- **ROC-AUC (CV 5-fold)** : 0.9842 ± 0.0019
- **Précision** : 92%
- **Features** : 23

### Prophet
- **MAE** : $12,024
- **MAPE** : 17.14%
- **Test set** : 20% des données

### KMeans
- **Clusters** : 3 (Low/Mid/High Value)
- **Clients** : 793

### Isolation Forest
- **Contamination** : 5%
- **Anomalies** : ~500 commandes

---

## ⚠️ Important

- **Ne PAS versionner** ces fichiers dans Git (trop gros)
- **Réentraîner localement** après clonage du repo
- **Ne PAS modifier** manuellement ces fichiers
- **Sauvegarder** avant de réentraîner

---

## 🔒 Reproductibilité

Les modèles utilisent `random_state=42` pour garantir la reproductibilité.

Réentraîner avec les mêmes données donnera les mêmes résultats (à epsilon près pour Prophet).

---

## 📝 Utilisation

Les modèles sont chargés automatiquement par `ml/models.py` :

```python
from ml.models import load_models

models = load_models()
# models['rf'], models['prophet'], models['kmeans'], etc.
```

---

**Généré par** : `ml/train_models.py`  
**Dernière mise à jour** : Avril 2026
