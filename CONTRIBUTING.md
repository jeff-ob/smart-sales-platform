# 🤝 Guide de Contribution

Merci de ton intérêt pour contribuer à Smart Sales Platform !

---

## 🚀 Comment Contribuer

### 1. Fork le projet
```bash
# Clique sur "Fork" en haut à droite sur GitHub
```

### 2. Clone ton fork
```bash
git clone https://github.com/[ton-username]/smart-sales-platform.git
cd smart-sales-platform
```

### 3. Crée une branche
```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
```

### 4. Installe les dépendances
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 5. Fais tes modifications
- Écris du code propre et commenté
- Suis les conventions Python (PEP 8)
- Teste tes modifications localement

### 6. Teste ton code
```bash
# Teste le pipeline
python etl/run_pipeline.py

# Teste les modèles
python ml/train_models.py

# Teste le dashboard
streamlit run dashboard/app.py

# Vérifie le déploiement
python verify_deployment.py
```

### 7. Commit tes changements
```bash
git add .
git commit -m "feat: ajoute [description de ta fonctionnalité]"
```

### 8. Push vers ton fork
```bash
git push origin feature/ma-nouvelle-fonctionnalite
```

### 9. Crée une Pull Request
- Va sur GitHub
- Clique sur "New Pull Request"
- Décris tes changements
- Attends la review

---

## 📝 Conventions de Commit

Utilise les préfixes suivants :

- `feat:` - Nouvelle fonctionnalité
- `fix:` - Correction de bug
- `docs:` - Documentation
- `style:` - Formatage, style
- `refactor:` - Refactoring
- `test:` - Ajout de tests
- `chore:` - Maintenance

**Exemples** :
```
feat: ajoute prédiction de churn
fix: corrige calcul RFM score
docs: met à jour README avec nouvelles features
refactor: améliore performance du pipeline ETL
```

---

## 🎯 Domaines de Contribution

### Features Souhaitées
- [ ] Tests unitaires (pytest)
- [ ] API REST (FastAPI)
- [ ] Authentification utilisateur
- [ ] Export PDF des rapports
- [ ] Alertes par email
- [ ] Prédiction de churn
- [ ] Recommandations produits
- [ ] Dashboard temps réel

### Améliorations
- [ ] Optimisation des requêtes SQL
- [ ] Cache Redis pour le dashboard
- [ ] Logging structuré
- [ ] Monitoring avec MLflow
- [ ] CI/CD avec GitHub Actions
- [ ] Documentation API (Sphinx)
- [ ] Type hints complets
- [ ] Docstrings pour toutes les fonctions

### Bugs Connus
- Aucun bug connu actuellement

---

## 🧪 Tests

Avant de soumettre une PR, assure-toi que :

- [ ] Le pipeline ETL fonctionne
- [ ] Les modèles ML s'entraînent correctement
- [ ] Le dashboard s'affiche sans erreur
- [ ] Toutes les pages du dashboard fonctionnent
- [ ] Les filtres de la sidebar fonctionnent
- [ ] Aucune erreur dans la console
- [ ] Le script `verify_deployment.py` passe

---

## 📚 Structure du Code

```
smart-sales-platform/
├── etl/              # Pipeline ETL
├── ml/               # Modèles ML
├── dashboard/        # Dashboard Streamlit
├── data/             # Données
├── notebook/         # Notebooks Jupyter
└── config.py         # Configuration
```

### Conventions de Code

- **Python** : PEP 8
- **Imports** : Groupés (stdlib, third-party, local)
- **Fonctions** : snake_case
- **Classes** : PascalCase
- **Constantes** : UPPER_CASE
- **Docstrings** : Google style

---

## 🐛 Signaler un Bug

Crée une issue sur GitHub avec :

1. **Titre clair** : "Bug: [description courte]"
2. **Description** : Que s'est-il passé ?
3. **Reproduction** : Comment reproduire le bug ?
4. **Environnement** : OS, Python version, etc.
5. **Logs** : Copie les messages d'erreur

---

## 💡 Proposer une Feature

Crée une issue sur GitHub avec :

1. **Titre clair** : "Feature: [description courte]"
2. **Description** : Quelle fonctionnalité veux-tu ?
3. **Motivation** : Pourquoi est-ce utile ?
4. **Implémentation** : Comment l'implémenter ?

---

## 📞 Questions ?

- **Issues** : https://github.com/[username]/smart-sales-platform/issues
- **Discussions** : https://github.com/[username]/smart-sales-platform/discussions
- **Email** : [ton-email]

---

## 📄 License

En contribuant, tu acceptes que tes contributions soient sous licence MIT.

---

**Merci de contribuer ! 🙏**

