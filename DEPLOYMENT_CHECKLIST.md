# ✅ Checklist de Déploiement

## Avant de commencer

- [ ] Le projet fonctionne en local (`streamlit run dashboard/app.py`)
- [ ] Tous les modèles sont entraînés (9 fichiers dans `ml/saved_models/`)
- [ ] La base de données existe (`sales.db`)
- [ ] Les données sont présentes (`data/sales_raw.csv`)
- [ ] Git est installé sur ton PC
- [ ] Tu as un compte GitHub

---

## Étape 1 : Vérification des fichiers

### Fichiers OBLIGATOIRES pour le déploiement

- [ ] `dashboard/app.py` (point d'entrée)
- [ ] `requirements.txt` (dépendances Python)
- [ ] `packages.txt` (dépendances système)
- [ ] `.streamlit/config.toml` (configuration Streamlit)
- [ ] `sales.db` (base de données)
- [ ] `data/sales_raw.csv` (données brutes)
- [ ] `ml/saved_models/*.pkl` (9 modèles)
- [ ] `config.py` (configuration chemins)
- [ ] Tous les fichiers `etl/*.py`
- [ ] Tous les fichiers `ml/*.py`

### Fichiers à EXCLURE (déjà dans .gitignore)

- [ ] `.venv/` (environnement virtuel)
- [ ] `__pycache__/` (cache Python)
- [ ] `dashboard/app_improved.py` (version corrompue)
- [ ] `dashboard/app_v2*.py` (versions expérimentales)
- [ ] `test_project.py` (fichier de test)
- [ ] Fichiers de documentation interne (ANALYSE_CRITIQUE.md, etc.)

---

## Étape 2 : Test local final

```bash
# 1. Activer l'environnement
.venv\Scripts\activate

# 2. Tester le pipeline
python etl/run_pipeline.py

# 3. Tester les modèles
python ml/train_models.py

# 4. Tester le dashboard
streamlit run dashboard/app.py
```

**Vérifier** :
- [ ] Toutes les pages du dashboard s'affichent
- [ ] Aucune erreur dans la console
- [ ] Les graphiques se chargent correctement
- [ ] Les filtres fonctionnent

---

## Étape 3 : Initialisation Git

```bash
# Dans le dossier du projet
git init
git add .
git commit -m "Initial commit - Smart Sales Platform ready for deployment"
```

**Vérifier** :
- [ ] Aucun fichier sensible n'est commité (pas de mots de passe, clés API)
- [ ] Les fichiers `.gitignore` et `.gitattributes` sont bien présents

---

## Étape 4 : Créer le repository GitHub

1. [ ] Aller sur https://github.com/new
2. [ ] Nom du repo : `smart-sales-platform`
3. [ ] Description : "End-to-end sales analytics platform with ML"
4. [ ] Choisir Public ou Private
5. [ ] **NE PAS** cocher "Add README" (on en a déjà un)
6. [ ] Cliquer "Create repository"

---

## Étape 5 : Pousser le code sur GitHub

```bash
# Remplacer [username] par ton username GitHub
git remote add origin https://github.com/[username]/smart-sales-platform.git
git branch -M main
git push -u origin main
```

### Si erreur "file too large"

```bash
# Installer Git LFS
git lfs install
git lfs track "*.pkl"
git lfs track "*.db"
git lfs track "*.csv"
git add .gitattributes
git commit -m "Add Git LFS for large files"
git push
```

**Vérifier** :
- [ ] Tous les fichiers sont sur GitHub
- [ ] Le README s'affiche correctement
- [ ] Les dossiers `ml/saved_models/` et `data/` sont présents

---

## Étape 6 : Déployer sur Streamlit Cloud

1. [ ] Aller sur https://streamlit.io/cloud
2. [ ] Cliquer "Sign up" → Se connecter avec GitHub
3. [ ] Autoriser Streamlit à accéder à ton compte GitHub
4. [ ] Cliquer "New app"
5. [ ] Remplir le formulaire :
   - **Repository** : `[username]/smart-sales-platform`
   - **Branch** : `main`
   - **Main file path** : `dashboard/app.py`
6. [ ] Cliquer "Deploy" 🚀

**Attendre 5-10 minutes** (installation des dépendances)

---

## Étape 7 : Vérification du déploiement

### URL générée
- [ ] Noter l'URL : `https://[username]-smart-sales-platform-[hash].streamlit.app`

### Tests à effectuer
- [ ] Page 1 (Vue Générale) s'affiche correctement
- [ ] Page 2 (Forecast) affiche les prévisions
- [ ] Page 3 (RFM) affiche les segments
- [ ] Page 4 (ML Rentabilité) affiche les prédictions
- [ ] Page 5 (Anomalies) affiche les anomalies
- [ ] Les filtres de la sidebar fonctionnent
- [ ] Aucune erreur dans les logs

### Si problème
- [ ] Vérifier les logs : Bouton "Manage app" → "Logs"
- [ ] Vérifier que tous les fichiers sont sur GitHub
- [ ] Vérifier `requirements.txt` et `packages.txt`

---

## Étape 8 : Partager le projet

### Sur GitHub
- [ ] Ajouter une description au repo
- [ ] Ajouter des topics : `python`, `streamlit`, `machine-learning`, `data-science`, `etl`
- [ ] Mettre à jour le README avec l'URL du dashboard déployé

### Sur LinkedIn
- [ ] Créer un post avec :
  - Screenshot du dashboard
  - Lien vers le repo GitHub
  - Lien vers le dashboard en ligne
  - Description des compétences démontrées

### Sur ton CV
- [ ] Ajouter le projet dans la section "Projets"
- [ ] Mentionner les technologies utilisées
- [ ] Ajouter les liens (GitHub + dashboard)

---

## Étape 9 : Maintenance

### Mettre à jour l'app après modification

```bash
git add .
git commit -m "Description des changements"
git push
```

Streamlit Cloud redéploie automatiquement ! ⚡

### Surveiller l'app
- [ ] Vérifier régulièrement que l'app est en ligne
- [ ] Consulter les logs en cas d'erreur
- [ ] Mettre à jour les dépendances si nécessaire

---

## 🎉 FÉLICITATIONS !

Ton projet est maintenant déployé et accessible publiquement !

**Prochaines étapes** :
- [ ] Ajouter le lien dans ton portfolio
- [ ] Partager sur les réseaux sociaux
- [ ] Continuer à améliorer le projet
- [ ] Ajouter de nouvelles fonctionnalités

---

## 📞 Ressources utiles

- [Documentation Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud)
- [Documentation Git LFS](https://git-lfs.github.com/)
- [Guide GitHub](https://docs.github.com/en/get-started)
- [Troubleshooting Streamlit](https://docs.streamlit.io/knowledge-base)

---

**Bonne chance ! 💪**
