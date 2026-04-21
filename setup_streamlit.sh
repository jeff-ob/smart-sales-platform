#!/bin/bash

# Script de setup pour Streamlit Cloud
echo "🚀 Setup Smart Sales Platform..."

# Créer les dossiers nécessaires
mkdir -p data
mkdir -p ml/saved_models

# Vérifier si les données existent
if [ ! -f "data/sales_raw.csv" ]; then
    echo "⚠️  Attention : data/sales_raw.csv manquant"
    echo "Le dashboard ne pourra pas fonctionner sans données"
fi

# Vérifier si les modèles existent
if [ ! -f "ml/saved_models/rf_classifier.pkl" ]; then
    echo "⚠️  Attention : Modèles ML manquants"
    echo "Exécutez : python ml/train_models.py"
fi

echo "✅ Setup terminé"
