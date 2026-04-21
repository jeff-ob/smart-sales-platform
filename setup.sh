#!/bin/bash

# Script d'installation pour Streamlit Cloud
# Ce script s'exécute automatiquement lors du déploiement

echo "🚀 Installation des dépendances système..."

# Installer les dépendances système nécessaires pour Prophet
apt-get update
apt-get install -y build-essential

echo "✅ Installation terminée !"
