@echo off
:: 🌡️ Climatisation Hybride - Script de démarrage Windows
:: Script pour démarrer automatiquement le backend et le frontend

echo 🌡️ Démarrage du système de climatisation hybride...
echo ==================================================

:: Vérifier si nous sommes dans le bon répertoire
if not exist "..\tre-climate-control-dash" (
    echo [ERROR] Veuillez exécuter ce script depuis le répertoire 'climatisation_backend'
    pause
    exit /b 1
)

:: 1. Démarrer le backend
echo [INFO] Démarrage du backend Python...

:: Vérifier si l'environnement virtuel existe
if not exist "venv" (
    echo [WARNING] Environnement virtuel non trouvé. Création...
    python -m venv venv
)

:: Activer l'environnement virtuel
call venv\Scripts\activate.bat

:: Installer les dépendances
echo [INFO] Installation des dépendances backend...
pip install -r requirements.txt

:: Démarrer le serveur backend
echo [INFO] Lancement du serveur Flask sur http://localhost:5000
start /B python app.py

:: Attendre que le backend soit prêt
timeout /t 3 /nobreak >nul

:: 2. Démarrer le frontend
echo [INFO] Démarrage du frontend React...
cd ..\tre-climate-control-dash

:: Vérifier si node_modules existe
if not exist "node_modules" (
    echo [WARNING] Modules npm non trouvés. Installation...
    call npm install
)

:: Démarrer le serveur de développement frontend
echo [INFO] Lancement du serveur de développement sur http://localhost:5173
start /B npm run dev

:: Attendre que le frontend soit prêt
timeout /t 5 /nobreak >nul

:: 3. Afficher les informations de connexion
echo.
echo [SUCCESS] 🚀 Système de climatisation hybride démarré avec succès !
echo.
echo 📊 Interfaces disponibles :
echo    • Frontend (Dashboard): http://localhost:5173
echo    • Backend (API):        http://localhost:5000
echo    • API Status:           http://localhost:5000/api/status
echo.
echo 🔧 Configuration :
echo    • Mode par défaut:      Automatique
echo    • Mise à jour:          Toutes les 5 secondes
echo    • Port Arduino:         Auto-détection
echo.
echo 📱 Modes disponibles :
echo    1. ☀️  Mode Solaire
echo    2. ❄️  Mode Compression
echo    3. 🔄 Mode Hybride
echo    4. 🤖 Mode Automatique
echo.
echo ⚡ Contrôles :
echo    • Changer de mode via le dashboard web
echo    • Surveillance automatique des fuites
echo    • Gestion automatique de la température
echo.
echo [WARNING] Appuyez sur une touche pour arrêter le système...

:: Ouvrir automatiquement les navigateurs
start http://localhost:5173
start http://localhost:5000

pause
