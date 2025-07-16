#!/bin/bash
# 🌡️ Climatisation Hybride - Script de démarrage
# Script pour démarrer automatiquement le backend et le frontend

echo "🌡️ Démarrage du système de climatisation hybride..."
echo "=================================================="

# Couleurs pour les messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages colorés
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier si nous sommes dans le bon répertoire
if [ ! -d "../tre-climate-control-dash" ]; then
    log_error "Veuillez exécuter ce script depuis le répertoire 'climatisation_backend'"
    exit 1
fi

# Fonction pour tuer les processus en arrière-plan
cleanup() {
    log_info "Arrêt du système..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Trap pour nettoyer en cas d'interruption
trap cleanup SIGINT SIGTERM

# 1. Démarrer le backend
log_info "Démarrage du backend Python..."

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    log_warning "Environnement virtuel non trouvé. Création..."
    python -m venv venv
fi

# Activer l'environnement virtuel
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Installer les dépendances
log_info "Installation des dépendances backend..."
pip install -r requirements.txt

# Démarrer le serveur backend en arrière-plan
log_info "Lancement du serveur Flask sur http://localhost:5000"
python app.py &
BACKEND_PID=$!

# Attendre que le backend soit prêt
sleep 3

# 2. Démarrer le frontend
log_info "Démarrage du frontend React..."
cd ../tre-climate-control-dash

# Vérifier si node_modules existe
if [ ! -d "node_modules" ]; then
    log_warning "Modules npm non trouvés. Installation..."
    npm install
fi

# Démarrer le serveur de développement frontend
log_info "Lancement du serveur de développement sur http://localhost:5173"
npm run dev &
FRONTEND_PID=$!

# Attendre que le frontend soit prêt
sleep 5

# 3. Afficher les informations de connexion
echo ""
log_success "🚀 Système de climatisation hybride démarré avec succès !"
echo ""
echo "📊 Interfaces disponibles :"
echo "   • Frontend (Dashboard): http://localhost:5173"
echo "   • Backend (API):        http://localhost:5000"
echo "   • API Status:           http://localhost:5000/api/status"
echo ""
echo "🔧 Configuration :"
echo "   • Mode par défaut:      Automatique"
echo "   • Mise à jour:          Toutes les 5 secondes"
echo "   • Port Arduino:         Auto-détection"
echo ""
echo "📱 Modes disponibles :"
echo "   1. ☀️  Mode Solaire"
echo "   2. ❄️  Mode Compression"
echo "   3. 🔄 Mode Hybride"
echo "   4. 🤖 Mode Automatique"
echo ""
echo "⚡ Contrôles :"
echo "   • Changer de mode via le dashboard web"
echo "   • Surveillance automatique des fuites"
echo "   • Gestion automatique de la température"
echo ""
log_warning "Appuyez sur Ctrl+C pour arrêter le système"

# Attendre indéfiniment
wait
