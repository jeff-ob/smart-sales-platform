# 🚀 Guide de Déploiement - Smart Sales Platform

## Déploiement sur Streamlit Cloud

### Prérequis
- Compte GitHub
- Compte Streamlit Cloud (gratuit)
- Données et modèles ML dans le repo

### Étapes

#### 1. Préparer les données

**IMPORTANT** : Les fichiers suivants doivent être dans le repo :
- `data/sales_raw.csv` (dataset)
- `ml/saved_models/*.pkl` (9 fichiers de modèles)
- `sales.db` (base SQLite avec 3 tables)

**Note** : Ces fichiers sont gros. Si GitHub refuse, utilisez Git LFS :
```bash
git lfs install
git lfs track "*.pkl"
git lfs track "*.db"
git lfs track "*.csv"
```

#### 2. Pousser sur GitHub

```bash
# Initialiser Git (si pas déjà fait)
git init
git add .
git commit -m "Initial commit - Smart Sales Platform"

# Créer un repo sur GitHub puis :
git remote add origin https://github.com/[username]/smart-sales-platform.git
git branch -M main
git push -u origin main
```

#### 3. Déployer sur Streamlit Cloud

1. Aller sur https://streamlit.io/cloud
2. Se connecter avec GitHub
3. Cliquer sur "New app"
4. Sélectionner :
   - Repository : `[username]/smart-sales-platform`
   - Branch : `main`
   - Main file path : `dashboard/app.py`
5. Cliquer sur "Deploy"

#### 4. Configuration avancée (optionnel)

Dans les paramètres de l'app sur Streamlit Cloud :
- **Python version** : 3.11
- **Secrets** : Ajouter si nécessaire (API keys, etc.)

### Temps de déploiement

- Premier déploiement : ~5-10 minutes
- Redéploiements : ~2-3 minutes

### URL de l'application

Après déploiement : `https://[username]-smart-sales-platform-dashboardapp-[hash].streamlit.app`

Vous pouvez personnaliser l'URL dans les paramètres.

---

## Alternative : Déploiement Local avec Docker

Si vous préférez Docker :

```bash
# Créer l'image
docker build -t smart-sales-platform .

# Lancer le conteneur
docker run -p 8501:8501 smart-sales-platform
```

Voir `Dockerfile` pour plus de détails.

---

## Problèmes Courants

### Erreur : "ModuleNotFoundError"
→ Vérifier que toutes les dépendances sont dans `requirements.txt`

### Erreur : "File not found: sales.db"
→ S'assurer que `sales.db` est dans le repo (pas dans `.gitignore`)

### Erreur : "Models not found"
→ S'assurer que les fichiers `.pkl` sont dans `ml/saved_models/`

### App très lente au démarrage
→ Normal pour le premier chargement (téléchargement des dépendances)

---

## Support

Pour toute question : voir `README.md` ou `CLAUDE.md`
