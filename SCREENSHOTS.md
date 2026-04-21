# 📸 Captures d'Écran du Dashboard

## 🎨 Aperçu du Dashboard

Le dashboard Smart Sales Platform comprend 5 pages interactives avec des visualisations Plotly.

---

## 📊 Page 1 - Vue Générale

**KPIs Principaux**
- Ventes totales : 2 297 201 $
- Profit total : 286 397 $
- Commandes : 9 994
- Clients uniques : 793
- Marge moyenne : 12.5%

**Visualisations**
- Ventes & Profit par catégorie (bar chart)
- Profit par sous-catégorie (horizontal bar chart)
- Ventes par région (pie chart)
- Impact des remises sur le profit (bar chart)

**Insights**
- Technology : catégorie la plus rentable
- Tables et Bookcases : sous-catégories déficitaires
- Remises > 30% : 97.8% des commandes sont déficitaires

---

## 📅 Page 2 - Forecast

**Modèle Prophet**
- Prévisions mensuelles avec saisonnalité
- Intervalle de confiance 95%
- Horizon configurable (3-24 mois)

**Métriques**
- MAPE : 17.14%
- MAE : 12 024 $
- Ventes prévues sur 12 mois : ~1.2M $

**Visualisations**
- Graphique temporel avec historique + prévisions
- Ligne de séparation historique/forecast
- Bande de confiance 95%
- Tableau détaillé des prévisions

**Insights**
- Saisonnalité forte en Q4 (Sep, Nov, Déc)
- Creux systématique en Février
- Tendance générale à la hausse

---

## 👥 Page 3 - Analyse Clients & RFM

**Segmentation RFM**
- 8 segments actionnables
- Scoring R/F/M (1-4)
- Pondération : R=40%, F=30%, M=30%

**Segments**
1. Champions (92 clients) - 4 483 $ moy.
2. Loyal Customers (146 clients) - 3 352 $ moy.
3. Potential Loyalists (29 clients) - 5 282 $ moy.
4. At Risk (109 clients) - 3 701 $ moy. ⚠️
5. New Customers (74 clients) - 1 916 $ moy.
6. Can't Lose Them (30 clients) - 5 652 $ moy. 🚨
7. Hibernating (59 clients) - 4 330 $ moy.
8. Lost (254 clients) - 1 071 $ moy.

**Visualisations**
- Distribution des segments (bar chart)
- Scatter Recency vs Frequency (bubble chart)
- Valeur totale par segment (bar chart avec %)
- Filtre interactif par segment

**Insights**
- 573 025 $ de valeur à risque (At Risk + Can't Lose Them)
- 50% des clients génèrent 80% de la valeur (Pareto)
- Champions + Loyal = 39.3% de la valeur totale

---

## 🤖 Page 4 - ML Rentabilité

**Modèle Random Forest**
- ROC-AUC : 0.9831
- 25 features (temporelles, financières, produit, client)
- Prédiction binaire : rentable / non rentable

**Métriques**
- Commandes analysées : 9 994
- Prédites non rentables : ~2 000 (20%)
- Confiance moyenne : 85%

**Visualisations**
- Distribution des probabilités (histogramme overlay)
- Commandes à risque par catégorie (pie chart)
- Taux de risque par palier de remise (bar chart)
- Top 100 commandes à risque (tableau)

**Insights**
- Remises > 30% : 80% de risque de non-rentabilité
- Furniture : catégorie la plus à risque
- Modèle très performant (ROC-AUC 0.9831)

---

## 🚨 Page 5 - Anomalies

**Modèle Isolation Forest**
- Contamination : 5%
- ~500 anomalies détectées
- Features : sales, profit, discount, quantity

**Métriques**
- Anomalies détectées : 500
- % du total : 5%
- Perte moyenne : -150 $
- Remise moyenne : 45%

**Visualisations**
- Scatter plot ventes vs profit (anomalies en rouge)
- Anomalies par catégorie (bar chart)
- Liste des 100 commandes les plus anormales (tableau)

**Insights**
- Anomalies = commandes avec remises excessives
- Perte moyenne de 150 $ par anomalie
- Furniture : catégorie avec le plus d'anomalies

---

## 🎛️ Sidebar - Filtres Interactifs

**Filtres Disponibles**
- Années (multi-select)
- Région (dropdown)
- Catégorie (dropdown)

**Compteur**
- Nombre de commandes filtrées en temps réel

**Navigation**
- 5 pages accessibles via radio buttons
- Logo et titre du projet

---

## 🎨 Design

**Thème**
- Couleurs : Bleu (#636EFA), Vert (#00CC96), Rouge (#EF553B)
- Police : Sans-serif
- Layout : Wide mode
- Responsive : Adapté mobile et desktop

**Composants**
- Métriques avec icônes
- Graphiques Plotly interactifs
- Tableaux avec formatage
- Expanders pour détails
- Sliders pour paramètres

---

## 📱 Responsive Design

Le dashboard s'adapte automatiquement à toutes les tailles d'écran :
- Desktop (1920x1080)
- Laptop (1366x768)
- Tablet (768x1024)
- Mobile (375x667)

---

## 🔄 Interactivité

**Hover**
- Tooltips sur tous les graphiques
- Valeurs détaillées au survol

**Filtres**
- Mise à jour en temps réel
- Compteur de commandes filtrées

**Sliders**
- Horizon de prévision (3-24 mois)
- Mise à jour dynamique des graphiques

**Expanders**
- Tableaux détaillés masquables
- Économie d'espace

---

## 📊 Technologies de Visualisation

- **Plotly Express** : Graphiques rapides et élégants
- **Plotly Graph Objects** : Graphiques personnalisés
- **Streamlit** : Interface interactive
- **Pandas** : Manipulation de données

---

## 🎯 Prochaines Améliorations Visuelles

- [ ] Thème sombre
- [ ] Export PDF des rapports
- [ ] Graphiques animés
- [ ] Cartes géographiques interactives
- [ ] Comparaison période vs période
- [ ] Drill-down sur les catégories

---

**Note** : Les captures d'écran seront ajoutées après le déploiement.

Pour voir le dashboard en action, visite : [URL à ajouter après déploiement]

