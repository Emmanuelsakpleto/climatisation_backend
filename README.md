# 🌡️ Système de Climatisation Hybride Intelligent

Un système complet de gestion de climatisation avec Arduino, backend Flask et frontend React pour le contrôle intelligent d'un système de climatisation hybride (solaire + compression).

## 🎯 Vue d'ensemble

Ce projet implémente un système de climatisation intelligent capable de basculer automatiquement entre différents modes de fonctionnement selon les conditions environnementales et les besoins énergétiques.

### 🏗️ Architecture

```
📦 Système Complet
├── 🎨 Frontend (React + Vite)
│   ├── 📊 Dashboard temps réel
│   ├── 🎛️ Contrôles manuels
│   ├── ⚠️ Alertes de fuite
│   └── 📈 Graphiques de performance
├── 🔧 Backend (Flask)
│   ├── 🌐 API REST
│   ├── 🤖 Gestion Arduino
│   ├── 🧠 IA décisionnelle
│   └── 🖼️ Simulation thermique
└── 🤖 Arduino
    ├── 📡 Lecture capteurs
    ├── 💡 Contrôle LEDs
    └── 🔗 Communication série
```

## 🚀 Fonctionnalités

### 🌟 Modes de fonctionnement

| Mode | Conditions | LED | Priorité |
|------|------------|-----|----------|
| **🌞 Solaire** | Ensoleillement > 500 W/m² + Débit > 45 L/min + Temp < 26°C | 🟢 Verte | Énergie renouvelable |
| **❄️ Compression** | Conditions solaires non remplies | 🔵 Bleue | Performance constante |
| **⚡ Hybride** | Ensoleillement > 200 W/m² + Débit > 30 L/min + Temp < 30°C | 🟡 Alternance | Équilibre efficacité |
| **🤖 Automatique** | Par défaut ou via interface | Selon IA | Optimisation intelligente |

### 🔍 Détection de fuites

- **🟡 Fuite probable** : Pression < 1.5 bar ou Niveau eau < 50%
- **🔴 Fuite critique** : Pression < 1.2 bar ou Niveau eau < 30%
- **📱 Alertes** : Notifications temps réel avec localisation

### 📊 Surveillance temps réel

- Ensoleillement (W/m²)
- Température (°C)
- Débit des pompes (L/min)
- Pression du système (bars)
- Niveau d'eau (%)
- Demande de froid (kW)

## 🛠️ Installation

### 1. 📋 Prérequis

```bash
# Node.js et npm
node --version  # v18+
npm --version   # v9+

# Python
python --version  # v3.8+
pip --version

# Arduino IDE (pour flasher le firmware)
```

### 2. 🔧 Backend

```bash
cd climatisation_backend
pip install -r requirements.txt
python run_system.py
```

Le backend sera accessible sur `http://127.0.0.1:5000`

### 3. 🎨 Frontend

```bash
cd tre-climate-control-dash
npm install
npm run dev
```

Le frontend sera accessible sur `http://127.0.0.1:5173`

### 4. 🤖 Arduino

1. Ouvrir `arduino_advanced.ino` dans Arduino IDE
2. Flasher le code sur Arduino Uno
3. Connecter les composants :
   - **Potentiomètres** : A0-A4
   - **LEDs** : Pins 9, 10, 11 (et 12 pour hybride)
   - **Port série** : USB

## 🎮 Utilisation

### 💻 Interface Web

1. **📊 État du système** : Visualisation temps réel de tous les paramètres
2. **🎛️ Contrôles** : Basculer entre modes (Solaire, Compression, Hybride, Auto)
3. **⚠️ Alertes** : Détection automatique de fuites avec géolocalisation
4. **📈 Performances** : Graphiques historiques et statistiques

### 🌐 API REST

```bash
# Obtenir l'état du système
GET /api/system-status

# Contrôler le mode
POST /api/control
{
  "mode": "Solaire"     # Mode forcé
}

POST /api/control
{
  "action": "auto"      # Mode automatique
}
```

### 🤖 Commandes Arduino

| Commande | Action | LED |
|----------|---------|-----|
| `G` | Mode solaire | 🟢 Verte |
| `B` | Mode compression | 🔵 Bleue |
| `H` | Mode hybride | 🟡 Alternance |
| `A` | Mode automatique | Selon IA |
| `R` | Alerte fuite | 🔴 Rouge |
| `O` | Éteindre LEDs | ⚫ Aucune |

## 📁 Structure du projet

```
📦 Projet
├── 📂 climatisation_backend/
│   ├── 📄 app.py                    # Serveur Flask principal
│   ├── 📄 run_system.py             # Script de démarrage
│   ├── 📄 arduino_advanced.ino      # Firmware Arduino
│   ├── 📄 requirements.txt          # Dépendances Python
│   ├── 📂 models/
│   │   └── 📄 rules_simple.py       # Logique IA
│   ├── 📂 utils/
│   │   ├── 📄 serial_reader.py      # Communication Arduino
│   │   └── 📄 image_processor.py    # Simulation thermique
│   └── 📂 tests/                    # Tests unitaires
├── 📂 tre-climate-control-dash/
│   ├── 📄 package.json              # Dépendances Node.js
│   ├── 📄 vite.config.ts            # Configuration Vite
│   ├── 📂 src/
│   │   ├── 📂 components/
│   │   │   ├── 📄 Dashboard.jsx     # Interface principale
│   │   │   ├── 📄 StatusCard.jsx    # État système
│   │   │   ├── 📄 ControlPanel.jsx  # Contrôles
│   │   │   └── 📄 LeakAlert.jsx     # Alertes
│   │   ├── 📂 hooks/
│   │   │   └── 📄 useClimatisation.js # Hook système
│   │   └── 📂 services/
│   │       └── 📄 climatisationAPI.js # Client API
│   └── 📂 public/                   # Assets statiques
└── 📄 README.md                     # Ce fichier
```

## 🔧 Développement

### 🛠️ Mode simulation

Le système fonctionne entièrement sans Arduino grâce à :
- **📊 Données simulées** : Variation circadienne réaliste
- **🖼️ Images thermiques** : Génération automatique
- **🔄 Reconnexion automatique** : Tolérance aux pannes

### 🧪 Tests

```bash
# Backend
cd climatisation_backend
python -m pytest tests/

# Frontend
cd tre-climate-control-dash
npm test
```

### 🐛 Débogage

```bash
# Logs détaillés du backend
python app.py --debug

# Monitoring Arduino
python -c "from utils.serial_reader import read_arduino_data; print('Test OK')"
```

## 🚨 Dépannage

### ❌ Problèmes courants

| Problème | Solution |
|----------|----------|
| **Arduino non détecté** | Vérifier port COM, redémarrer `run_system.py` |
| **Erreur de communication** | Vérifier baudrate (9600), contrôler connexions |
| **Frontend ne se connecte pas** | Vérifier CORS, redémarrer backend |
| **Données incohérentes** | Vérifier calibration capteurs |

### 📊 Performance

- **Fréquence mise à jour** : 5 secondes
- **Timeout Arduino** : 3 secondes
- **Reconnexion automatique** : Oui
- **Mode dégradé** : Simulation automatique

## 🔮 Extensions possibles

### 🌟 Fonctionnalités avancées
- **📷 Caméra thermique réelle** : Intégration FLIR
- **🗄️ Base de données historique** : PostgreSQL/MongoDB
- **📱 Notifications push** : Email/SMS
- **📱 API mobile** : React Native
- **🏠 IoT** : Intégration Home Assistant

### 🤖 Intelligence artificielle
- **🧠 Machine Learning** : Prédiction des pannes
- **📈 Optimisation** : Algorithmes génétiques
- **🔄 Auto-apprentissage** : Adaptation comportementale

## 🛡️ Sécurité

- **🔐 Authentification** : JWT tokens
- **🌐 HTTPS** : Certificats SSL
- **🔒 Validation** : Sanitisation des entrées
- **📝 Logs** : Audit trail complet

## 📚 Documentation

- **📖 API Documentation** : Swagger/OpenAPI
- **🎓 Tutoriels** : Guide pas à pas
- **🔧 Manuel technique** : Spécifications complètes

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir `LICENSE` pour plus de détails.

## 👥 Équipe

- **Développeur Principal** : Emmanuel Sakpleto
- **Système** : Climatisation Hybride Amphithéâtre 2
- **Organisation** : TRE (Transition et Ressources Énergétiques)

---

## 🚀 Démarrage rapide

```bash
# 1. Cloner le projet
git clone https://github.com/Emmanuelsakpleto/tre-climate-control-dash.git

# 2. Démarrer le backend
cd climatisation_backend
pip install -r requirements.txt
python run_system.py

# 3. Démarrer le frontend (nouveau terminal)
cd tre-climate-control-dash
npm install
npm run dev

# 4. Ouvrir le navigateur
# Frontend : http://localhost:5173
# Backend API : http://localhost:5000/api/system-status
```

**✨ Le système est maintenant opérationnel ! ✨**
