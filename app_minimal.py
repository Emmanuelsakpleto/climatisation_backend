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
import serial

# Ajouter le répertoire utils au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from utils.data_simulator import get_random_simulated_data
import joblib

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

# Configuration Arduino
arduino = None
arduino_port = 'COM5'

def connect_arduino():
    global arduino
    try:
        if arduino:
            arduino.close()
        arduino = serial.Serial(arduino_port, 9600, timeout=3)
        time.sleep(2)
        print(f"✅ Arduino connecté sur {arduino_port}")
        return True
    except Exception as e:
        arduino = None
        print(f"❌ Arduino non connecté sur {arduino_port}: {e}")
        print("🔧 Mode simulation activé")
        return False

# Connexion initiale à l'Arduino
connect_arduino()

# Charger le modèle IA DecisionTree
try:
    decision_tree = joblib.load('decision_tree_mode.pkl')
    print("✅ Modèle IA chargé pour le mode automatique")
except Exception as e:
    decision_tree = None
    print(f"❌ Impossible de charger le modèle IA: {e}")

def read_arduino_data():
    """Lit les données réelles depuis l'Arduino, ou simule si non connecté"""
    global system_data, arduino
    if arduino:
        try:
            arduino.flushInput()
            line = arduino.readline().decode('utf-8').strip()
            if not line:
                raise Exception("Aucune donnée reçue")
            # Format attendu: DEBIT:xx,PRESSION:xx,NIVEAU:xx,ENSOLEILLEMENT:xx,TEMPERATURE:xx
            data = {}
            pairs = line.split(',')
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    key = key.strip().upper()
                    if key == 'DEBIT':
                        data['debit'] = float(value)
                    elif key == 'PRESSION':
                        data['pression'] = float(value)
                    elif key == 'NIVEAU':
                        data['niveau_eau'] = float(value)
                    elif key == 'ENSOLEILLEMENT':
                        data['ensoleillement'] = float(value)
                    elif key == 'TEMPERATURE':
                        data['temperature'] = float(value)
            # Vérifier que toutes les données sont présentes
            required = ['debit', 'pression', 'niveau_eau', 'ensoleillement', 'temperature']
            if all(k in data for k in required):
                system_data['debit'] = data['debit']
                system_data['pression_bars'] = data['pression']
                system_data['niveau_eau'] = data['niveau_eau']
                system_data['ensoleillement'] = data['ensoleillement']
                system_data['temperature'] = data['temperature']
                # Simuler l'humidité et la fuite
                system_data['humidity'] = round(65 + random.uniform(-5, 5), 1)
                system_data['leak_detected'] = (data['pression'] < 1.5 and data['niveau_eau'] < 50 and data['debit'] < 30)
                system_data['last_update'] = datetime.now().isoformat()
                logger.info(f"[DATA] Arduino: {line}")
                return
            else:
                raise Exception(f"Clés manquantes: {data}")
        except Exception as e:
            logger.warning(f"[DATA] Erreur Arduino, fallback sur simulation: {e}")
    # Fallback sur simulation CSV
    try:
        csv_data = get_random_simulated_data()
        system_data["temperature"] = csv_data["temperature"]
        system_data["humidity"] = round(65 + random.uniform(-5, 5), 1)
        system_data["pressure"] = round(1013.25 + random.uniform(-2, 2), 2)
        system_data["ensoleillement"] = csv_data["ensoleillement"]
        system_data["debit"] = csv_data["debit"]
        system_data["niveau_eau"] = csv_data["niveau_eau"]
        system_data["pression_bars"] = csv_data["pression"]
        logger.info(f"[DATA] Données CSV utilisées - Temp: {csv_data['temperature']}°C, Ensoleillement: {csv_data['ensoleillement']}W/m²")
    except Exception as e:
        logger.warning(f"[DATA] Erreur CSV, fallback sur simulation: {e}")
        base_temp = 22.5
        variation = math.sin(time.time() / 60) * 3
        system_data["temperature"] = round(base_temp + variation + random.uniform(-0.5, 0.5), 1)
        system_data["humidity"] = round(65 + random.uniform(-5, 5), 1)
        system_data["pressure"] = round(1013.25 + random.uniform(-2, 2), 2)
        system_data["ensoleillement"] = random.randint(200, 1000)
        system_data["debit"] = random.randint(45, 75)
        system_data["niveau_eau"] = random.randint(60, 95)
        system_data["pression_bars"] = system_data["pressure"] / 1000
    system_data["leak_detected"] = random.random() < 0.01
    system_data["last_update"] = datetime.now().isoformat()


def decide_mode_ia(ensoleillement, debit, temperature, forced_mode=None):
    """
    Décision du mode via IA (DecisionTree) ou mode forcé
    """
    if forced_mode:
        return forced_mode
    if decision_tree:
        features = [[ensoleillement, debit, temperature]]
        mode_pred = decision_tree.predict(features)[0]
        return mode_pred
    # Fallback sur la règle simple si pas de modèle IA
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
    read_arduino_data()
    # Décider du mode via IA ou mode forcé
    recommended_mode = decide_mode_ia(
        system_data.get("ensoleillement", 0),
        system_data.get("debit", 0),
        system_data["temperature"],
        current_forced_mode
    )
    logger.info(f"[AUTO] Mode IA ou forcé - Mode recommandé: {recommended_mode} (temp: {system_data['temperature']}°C)")

    response_data = {
        "status": "online",
        "mode": recommended_mode,
        "temperature": system_data["temperature"],
        "humidity": system_data["humidity"],
        "pression": system_data.get("pression_bars", system_data["pressure"] / 1000),
        "debit": system_data.get("debit", random.randint(45, 75)),
        "niveau_eau": system_data.get("niveau_eau", random.randint(60, 95)),
        "ensoleillement": system_data.get("ensoleillement", random.randint(200, 1000)),
        "leak_detected": system_data["leak_detected"],
        "arduino_connected": arduino is not None,
        "forced_mode": current_forced_mode,
        "timestamp": system_data["last_update"],
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
        ensoleillement = random.randint(200, 1000)
        debit = random.randint(45, 75)
        mode = decide_mode_ia(ensoleillement, debit, temp)
        history.append({
            "timestamp": datetime.fromtimestamp(timestamp).isoformat(),
            "temperature": round(temp, 1),
            "mode": mode,
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
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        logger.info("[STOP] Serveur arrêté par l'utilisateur")
        print("\n🛑 Serveur arrêté")
