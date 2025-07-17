#!/usr/bin/env python3
"""
🌡️ Serveur Flask minimal pour tester le système de climatisation
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import time
import math
from datetime import datetime

# Créer l'application Flask
app = Flask(__name__)
CORS(app, origins=['http://localhost:5173', 'http://localhost:8080', 'http://127.0.0.1:5173', 'http://127.0.0.1:8080'])

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
    
    # Simuler des variations de température
    base_temp = 22.5
    variation = math.sin(time.time() / 60) * 3  # Variation sinusoïdale
    system_data["temperature"] = round(base_temp + variation + random.uniform(-0.5, 0.5), 1)
    
    # Simuler l'humidité
    system_data["humidity"] = round(65 + random.uniform(-5, 5), 1)
    
    # Simuler la pression
    system_data["pressure"] = round(1013.25 + random.uniform(-2, 2), 2)
    
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
    simulate_sensor_data()
    
    # Décider du mode si en automatique
    if current_forced_mode is None:
        recommended_mode = decide_mode_simple(system_data["temperature"])
    else:
        recommended_mode = current_forced_mode
    
    return jsonify({
        "status": "online",
        "mode": recommended_mode,
        "temperature": system_data["temperature"],
        "humidity": system_data["humidity"],
        "pressure": system_data["pressure"],
        "leak_detected": system_data["leak_detected"],
        "arduino_connected": False,  # Simulation
        "forced_mode": current_forced_mode,
        "timestamp": system_data["last_update"],
        # Champs supplémentaires pour le frontend
        "ensoleillement": random.randint(200, 1000),
        "debit": random.randint(45, 75),
        "pression": system_data["pressure"] / 1000,  # Convertir en bars
        "niveau_eau": random.randint(60, 95),
        "mode_forced": current_forced_mode is not None,
        "thermal_image": None,
        "leak_details": {}
    })

@app.route('/api/mode', methods=['GET'])
def get_current_mode():
    """Retourne le mode actuel"""
    return jsonify({
        "mode": current_forced_mode or "automatic",
        "forced": current_forced_mode is not None
    })

@app.route('/api/mode', methods=['POST'])
def set_mode():
    """Change le mode de fonctionnement"""
    global current_forced_mode
    
    data = request.get_json()
    if not data or 'mode' not in data:
        return jsonify({"error": "Mode requis"}), 400
    
    mode = data['mode'].lower()
    valid_modes = ['solar', 'compression', 'hybrid', 'automatic']
    
    if mode not in valid_modes:
        return jsonify({"error": f"Mode invalide. Modes valides: {valid_modes}"}), 400
    
    if mode == 'automatic':
        current_forced_mode = None
    else:
        current_forced_mode = mode
    
    return jsonify({
        "status": "success",
        "mode": mode,
        "forced": current_forced_mode is not None,
        "message": f"Mode changé vers {mode}"
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    """Retourne l'historique des données"""
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
    
    return jsonify(history)

@app.route('/api/control', methods=['POST'])
def control_system():
    """Contrôle manuel du système"""
    data = request.get_json()
    if not data or 'action' not in data:
        return jsonify({"error": "Action requise"}), 400
    
    action = data['action']
    
    if action == 'restart':
        return jsonify({
            "status": "success",
            "message": "Système redémarré (simulation)",
            "action": action
        })
    elif action == 'stop':
        return jsonify({
            "status": "success",
            "message": "Système arrêté (simulation)",
            "action": action
        })
    else:
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
    print("🌡️  Système de Climatisation Backend - Version Simplifiée")
    print("📡 Mode simulation (Arduino non connecté)")
    print("🚀 Serveur démarré sur http://127.0.0.1:5000")
    print("📊 Endpoints disponibles:")
    print("   • GET  /api/status   - État du système")
    print("   • GET  /api/mode     - Mode actuel")
    print("   • POST /api/mode     - Changer de mode")
    print("   • GET  /api/history  - Historique")
    print("   • POST /api/control  - Contrôles manuels")
    print("🔧 Appuyez sur Ctrl+C pour arrêter")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté")
