#!/usr/bin/env python3
"""
🌡️ Serveur Flask minimal pour tester le système de climatisation
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import time
import math
import logging
from datetime import datetime
import sys
import os

# Ajouter le répertoire utils au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from data_simulator import get_random_simulated_data

# Créer l'application Flask
app = Flask(__name__)
CORS(app, origins=['http://localhost:5173', 'http://localhost:8080', 'http://127.0.0.1:5173', 'http://127.0.0.1:8080'])

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('climatisation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Variables globales pour simuler les données
current_mode = "automatic"
current_forced_mode = None
system_data = {
    "temperature": 22.5,
    "humidity": 65,
    "pressure": 1013.25,
    "leak_detected": False,
    "last_update": datetime.now().isoformat()
}

def simulate_sensor_data():
    """Simule les données des capteurs"""
    global system_data
    
    # Obtenir des données simulées depuis le CSV
    try:
        csv_data = get_random_simulated_data()
        
        # Utiliser les données du CSV
        system_data["temperature"] = csv_data["temperature"]
        system_data["humidity"] = round(65 + random.uniform(-5, 5), 1)  # Humidité pas dans le CSV
        system_data["pressure"] = round(1013.25 + random.uniform(-2, 2), 2)
        
        # Mettre à jour les données supplémentaires avec les valeurs du CSV
        system_data["ensoleillement"] = csv_data["ensoleillement"]
        system_data["debit"] = csv_data["debit"]
        system_data["niveau_eau"] = csv_data["niveau_eau"]
        system_data["pression_bars"] = csv_data["pression"]
        
        logger.info(f"[DATA] Données CSV utilisées - Temp: {csv_data['temperature']}°C, Ensoleillement: {csv_data['ensoleillement']}W/m²")
        
    except Exception as e:
        logger.warning(f"[DATA] Erreur CSV, fallback sur simulation: {e}")
        # Fallback sur l'ancienne méthode
        base_temp = 22.5
        variation = math.sin(time.time() / 60) * 3
        system_data["temperature"] = round(base_temp + variation + random.uniform(-0.5, 0.5), 1)
        system_data["humidity"] = round(65 + random.uniform(-5, 5), 1)
        system_data["pressure"] = round(1013.25 + random.uniform(-2, 2), 2)
        
        # Données par défaut
        system_data["ensoleillement"] = random.randint(200, 1000)
        system_data["debit"] = random.randint(45, 75)
        system_data["niveau_eau"] = random.randint(60, 95)
        system_data["pression_bars"] = system_data["pressure"] / 1000
    
    # Simuler la détection de fuite (rare)
    system_data["leak_detected"] = random.random() < 0.01  # 1% de chance
    
    # Mettre à jour le timestamp
    system_data["last_update"] = datetime.now().isoformat()

def decide_mode_simple(temperature):
    """Décision simple de mode basée sur la température"""
    if temperature < 20:
        return "solar"
    elif temperature > 28:
        return "compression"
    elif 20 <= temperature <= 28:
        return "hybrid"
    else:
        return "automatic"

@app.route('/api/status', methods=['GET'])
def get_system_status():
    """Retourne l'état actuel du système"""
    logger.info("[GET] Requête /api/status reçue")
    
    simulate_sensor_data()
    
    # Décider du mode si en automatique
    if current_forced_mode is None:
        recommended_mode = decide_mode_simple(system_data["temperature"])
        logger.info(f"[AUTO] Mode automatique - Mode recommandé: {recommended_mode} (temp: {system_data['temperature']}°C)")
    else:
        recommended_mode = current_forced_mode
        logger.info(f"[FORCE] Mode forcé actif: {recommended_mode}")
    
    response_data = {
        "status": "online",
        "mode": recommended_mode,
        "temperature": system_data["temperature"],
        "humidity": system_data["humidity"],
        "pressure": system_data["pressure"],
        "leak_detected": system_data["leak_detected"],
        "arduino_connected": False,  # Simulation
        "forced_mode": current_forced_mode,
        "timestamp": system_data["last_update"],
        # Champs supplémentaires pour le frontend (maintenant depuis CSV)
        "ensoleillement": system_data.get("ensoleillement", random.randint(200, 1000)),
        "debit": system_data.get("debit", random.randint(45, 75)),
        "pression": system_data.get("pression_bars", system_data["pressure"] / 1000),
        "niveau_eau": system_data.get("niveau_eau", random.randint(60, 95)),
        "mode_forced": current_forced_mode is not None,
        "thermal_image": None,
        "leak_details": {}
    }
    
    logger.info(f"[RESP] /api/status - Mode: {recommended_mode}, Temp: {system_data['temperature']}°C, Humidité: {system_data['humidity']}%")
    
    if system_data["leak_detected"]:
        logger.warning("[ALERT] Fuite détectée!")
    
    return jsonify(response_data)

@app.route('/api/mode', methods=['GET'])
def get_current_mode():
    """Retourne le mode actuel"""
    logger.info("[GET] Requête /api/mode reçue")
    
    current_mode_display = current_forced_mode or "automatic"
    is_forced = current_forced_mode is not None
    
    logger.info(f"[MODE] Mode actuel: {current_mode_display} {'(forcé)' if is_forced else '(automatique)'}")
    
    return jsonify({
        "mode": current_mode_display,
        "forced": is_forced
    })

@app.route('/api/mode', methods=['POST'])
def set_mode():
    """Change le mode de fonctionnement"""
    global current_forced_mode
    
    logger.info("[POST] Requête /api/mode reçue")
    
    data = request.get_json()
    if not data or 'mode' not in data:
        logger.error("[ERROR] Mode manquant dans la requête")
        return jsonify({"error": "Mode requis"}), 400
    
    mode = data['mode'].lower()
    valid_modes = ['solar', 'compression', 'hybrid', 'automatic']
    
    logger.info(f"[CHANGE] Tentative de changement de mode: {mode}")
    
    if mode not in valid_modes:
        logger.error(f"[ERROR] Mode invalide: {mode}. Modes valides: {valid_modes}")
        return jsonify({"error": f"Mode invalide. Modes valides: {valid_modes}"}), 400
    
    # Sauvegarder l'ancien mode pour les logs
    old_mode = current_forced_mode or "automatic"
    
    if mode == 'automatic':
        current_forced_mode = None
        logger.info(f"[SUCCESS] Mode changé: {old_mode} -> automatic (mode automatique activé)")
    else:
        current_forced_mode = mode
        logger.info(f"[SUCCESS] Mode changé: {old_mode} -> {mode} (mode forcé)")
    
    response_data = {
        "status": "success",
        "mode": mode,
        "forced": current_forced_mode is not None,
        "message": f"Mode changé vers {mode}"
    }
    
    logger.info(f"[RESP] /api/mode - Nouveau mode: {mode}, Forcé: {current_forced_mode is not None}")
    
    return jsonify(response_data)

@app.route('/api/history', methods=['GET'])
def get_history():
    """Retourne l'historique des données"""
    logger.info("[GET] Requête /api/history reçue")
    
    # Simuler quelques points d'historique
    history = []
    for i in range(10):
        timestamp = datetime.now().timestamp() - (i * 300)  # Toutes les 5 minutes
        temp = 22.5 + math.sin(timestamp / 60) * 3 + random.uniform(-0.5, 0.5)
        history.append({
            "timestamp": datetime.fromtimestamp(timestamp).isoformat(),
            "temperature": round(temp, 1),
            "mode": decide_mode_simple(temp),
            "leak_detected": random.random() < 0.01
        })
    
    logger.info(f"[RESP] Historique généré: {len(history)} entrées")
    
    return jsonify(history)

@app.route('/api/control', methods=['POST'])
def control_system():
    """Contrôle manuel du système"""
    logger.info("[POST] Requête /api/control reçue")
    
    data = request.get_json()
    if not data or 'action' not in data:
        logger.error("[ERROR] Action manquante dans la requête")
        return jsonify({"error": "Action requise"}), 400
    
    action = data['action']
    logger.info(f"[CONTROL] Action de contrôle demandée: {action}")
    
    if action == 'restart':
        logger.info("[RESTART] Redémarrage du système (simulation)")
        return jsonify({
            "status": "success",
            "message": "Système redémarré (simulation)",
            "action": action
        })
    elif action == 'stop':
        logger.info("[STOP] Arrêt du système (simulation)")
        return jsonify({
            "status": "success",
            "message": "Système arrêté (simulation)",
            "action": action
        })
    else:
        logger.error(f"[ERROR] Action invalide: {action}")
        return jsonify({"error": "Action invalide"}), 400

@app.route('/', methods=['GET'])
def root():
    """Page d'accueil de l'API"""
    return jsonify({
        "name": "Climatisation Hybride API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "status": "/api/status",
            "mode": "/api/mode",
            "history": "/api/history",
            "control": "/api/control"
        }
    })

if __name__ == '__main__':
    logger.info("[START] Système de Climatisation Backend - Version Simplifiée")
    logger.info("[START] Mode simulation (Arduino non connecté)")
    logger.info("[START] Serveur démarré sur http://127.0.0.1:5000")
    logger.info("[START] Endpoints disponibles:")
    logger.info("[START]    • GET  /api/status   - État du système")
    logger.info("[START]    • GET  /api/mode     - Mode actuel")
    logger.info("[START]    • POST /api/mode     - Changer de mode")
    logger.info("[START]    • GET  /api/history  - Historique")
    logger.info("[START]    • POST /api/control  - Contrôles manuels")
    logger.info("[START] Logs sauvegardés dans: climatisation.log")
    logger.info("[START] Appuyez sur Ctrl+C pour arrêter")
    
    print("🌡️  Système de Climatisation Backend - Version Simplifiée")
    print("📡 Mode simulation (Arduino non connecté)")
    print("🚀 Serveur démarré sur http://127.0.0.1:5000")
    print("📊 Endpoints disponibles:")
    print("   • GET  /api/status   - État du système")
    print("   • GET  /api/mode     - Mode actuel")
    print("   • POST /api/mode     - Changer de mode")
    print("   • GET  /api/history  - Historique")
    print("   • POST /api/control  - Contrôles manuels")
    print("� Logs sauvegardés dans: climatisation.log")
    print("�🔧 Appuyez sur Ctrl+C pour arrêter")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        logger.info("[STOP] Serveur arrêté par l'utilisateur")
        print("\n🛑 Serveur arrêté")
