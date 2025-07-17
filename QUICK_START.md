# 🚀 Guide de Démarrage Rapide - Système de Climatisation Hybride

## ✅ État Actuel

### 🔥 Backend (EN COURS)
- **URL**: http://127.0.0.1:5000
- **État**: ✅ FONCTIONNEL
- **Mode**: Simulation (Arduino non connecté)
- **Endpoints disponibles**:
  - `GET /api/status` - État du système
  - `GET /api/mode` - Mode actuel  
  - `POST /api/mode` - Changer de mode
  - `GET /api/history` - Historique
  - `POST /api/control` - Contrôles manuels

## 🎯 Prochaines étapes

### 1. Démarrer le Frontend
```bash
# Dans un nouveau terminal
cd /c/Users/emman/tre-climate-control-dash
npm install  # Si pas encore fait
npm run dev
```

### 2. Tester l'API Backend
```bash
# Test simple avec curl
curl http://localhost:5000/api/status

# Ou ouvrir dans le navigateur
http://localhost:5000/api/status
```

### 3. Tester le changement de mode
```bash
# Changer vers mode solaire
curl -X POST http://localhost:5000/api/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "solar"}'

# Changer vers mode compression
curl -X POST http://localhost:5000/api/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "compression"}'

# Retour en mode automatique
curl -X POST http://localhost:5000/api/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "automatic"}'
```

## 🔧 Configuration

### Backend
- **Port**: 5000
- **Host**: 0.0.0.0 (accessible depuis réseau local)
- **Debug**: Activé
- **CORS**: Configuré pour frontend

### Frontend (prévu)
- **Port**: 5173
- **URL**: http://localhost:5173
- **Build**: Vite + React

## 🌐 URLs Importantes

- **Backend API**: http://localhost:5000
- **Frontend**: http://localhost:5173 (quand démarré)
- **Documentation API**: http://localhost:5000 (page d'accueil)

## 🎮 Modes Disponibles

1. **☀️ Solaire** - Économique et écologique
2. **❄️ Compression** - Refroidissement rapide  
3. **🔄 Hybride** - Équilibre performance/économie
4. **🤖 Automatique** - Gestion intelligente basée sur température

## 📊 Données Simulées

Le système génère automatiquement :
- **Température**: 22.5°C ± variations sinusoïdales
- **Humidité**: 65% ± 5%
- **Pression**: 1013.25 hPa ± 2 hPa
- **Détection fuites**: 1% de probabilité

## 🔍 Monitoring

### Logs Backend
Le serveur affiche en temps réel :
- Requêtes HTTP
- Changements de mode
- Erreurs éventuelles

### Tests API
```bash
# Statut système
curl http://localhost:5000/api/status | jq

# Historique
curl http://localhost:5000/api/history | jq

# Info API
curl http://localhost:5000 | jq
```

## 🛠️ Résolution de Problèmes

### Backend ne démarre pas
```bash
# Vérifier les dépendances
pip install -r requirements.txt

# Tester les imports
python -c "from flask import Flask; print('✅ Flask OK')"

# Utiliser le serveur minimal
python app_minimal.py
```

### Erreur CORS
- Backend configuré avec `CORS(app)`
- Autorise toutes origines en développement

### Port occupé
```bash
# Changer le port dans app_minimal.py
app.run(host='0.0.0.0', port=5001, debug=True)
```

## 🎯 Commandes Utiles

### Démarrage complet
```bash
# Terminal 1: Backend
cd /c/Users/emman/climatisation_backend
python app_minimal.py

# Terminal 2: Frontend  
cd /c/Users/emman/tre-climate-control-dash
npm run dev
```

### Tests rapides
```bash
# Test connexion
curl -f http://localhost:5000/api/status || echo "❌ Backend down"

# Test changement mode
curl -X POST http://localhost:5000/api/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "solar"}' | jq
```

## 🚀 Prêt à Utiliser !

Le backend est maintenant **opérationnel** et prêt à recevoir des requêtes du frontend ou des tests manuels.

**Prochaine étape**: Démarrer le frontend pour une expérience complète ! 🎨
