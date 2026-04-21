# ⚡ Guide de Déploiement Rapide

## 🎯 Objectif
Déployer Smart Sales Platform sur Streamlit Cloud en 20 minutes

---

## ✅ CHECKLIST AVANT DE COMMENCER

- [ ] Compte GitHub créé
- [ ] Git installé sur ton PC
- [ ] Projet fonctionne en local (`streamlit run dashboard/app.py`)
- [ ] Données et modèles présents :
  - [ ] `data/sales_raw.csv`
  - [ ] `sales.db`
  - [ ] `ml/saved_models/*.pkl` (9 fichiers)

---

## 🚀 ÉTAPES (20 min)

### Étape 1 : Initialiser Git (2 min)

```bash
# Dans le dossier du projet
git init
git add .
git commit -m "Initial commit - Smart Sales Platform"
```

### Étape 2 : Créer le repo GitHub (3 min)

1. Aller sur https://github.com/new
2. Nom du repo : `smart-sales-platform`
3. Description : "End-to-end sales analytics platform with ML"
4. Public ou Private (ton choix)
5. **NE PAS** cocher "Add README" (on en a déjà un)
6. Cliquer "Create repository"

### Étape 3 : Pousser le code (5 min)

```bash
# Remplacer [username] par ton username GitHub
git remote add origin https://github.com/[username]/smart-sales-platform.git
git branch -M main
git push -u origin main
```

**Si erreur "file too large"** :
```bash
# Installer Git LFS
git lfs install
git lfs track "*.pkl"
git lfs track "*.db"
git lfs track "*.csv"
git add .gitattributes
git commit -m "Add Git LFS"
git push
```

### Étape 4 : Déployer sur Streamlit Cloud (10 min)

1. Aller sur https://streamlit.io/cloud
2. Cliquer "Sign up" → Se connecter avec GitHub
3. Cliquer "New app"
4. Remplir :
   - **Repository** : `[username]/smart-sales-platform`
   - **Branch** : `main`
   - **Main file path** : `dashboard/app.py`
5. Cliquer "Deploy" 🚀

**Attendre 5-10 minutes** (installation des dépendances)

### Étape 5 : Tester l'app (2 min)

1. URL générée : `https://[username]-smart-sales-platform-[hash].streamlit.app`
2. Tester toutes les pages
3. Vérifier que les graphiques s'affichent

---

## ✅ C'EST FAIT !

Ton app est en ligne ! 🎉

**Partager l'URL** :
- LinkedIn
- CV
- Portfolio
- GitHub README

---

## 🔄 Mettre à jour l'app

Après chaque modification :

```bash
git add .
git commit -m "Description des changements"
git push
```

Streamlit Cloud redéploie automatiquement ! ⚡

---

## ❌ Problèmes ?

### L'app ne démarre pas
→ Vérifier les logs dans Streamlit Cloud (bouton "Manage app" → "Logs")

### Erreur "File not found"
→ Vérifier que les fichiers sont bien dans le repo GitHub

### Erreur "Module not found"
→ Vérifier `requirements.txt`

---

## 📞 Besoin d'aide ?

Voir `DEPLOIEMENT.md` pour le guide complet
