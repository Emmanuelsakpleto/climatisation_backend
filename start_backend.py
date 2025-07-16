#!/usr/bin/env python3
"""
Script pour démarrer le backend Flask
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import serial
import time
import random
import math

# Import des modules locaux
try:
    from utils.serial_reader import read_arduino_data
    from utils.image_processor import get_thermal_image
    from models.rules_simple import decide_mode, detect_leak
except ImportError as e:
    print(f"⚠️ Erreur import: {e}")
    print("🔧 Utilisation du mode simulation uniquement")

app = Flask(__name__)
CORS(app)

# Tentative de connexion Arduino
arduino = None
try:
    arduino = serial.Serial('COM5', 9600, timeout=3)
    time.sleep(2)
    print("✅ Arduino connecté sur COM5")
except Exception as e:
    print(f"❌ Arduino non connecté: {e}")
    print("🔧 Mode simulation activé")

def get_simulated_data():
    """Génère des données simulées réalistes"""
    hour = time.localtime().tm_hour
    sun_factor = max(0, 1000 * (0.5 + 0.5 * math.cos((hour - 12) * math.pi / 12)))
    
    return {
        'debit': random.uniform(45, 65),
        'pression': random.uniform(2.0, 2.8),
        'niveau_eau': random.uniform(75, 95),
        'ensoleillement': sun_factor + random.uniform(-50, 50),
        'temperature': random.uniform(22, 28)
    }

@app.route('/api/system-status', methods=['GET'])
def system_status():
    """Endpoint principal pour récupérer l'état du système"""
    
    if arduino:
        try:
            arduino.flushInput()
            data = read_arduino_data(arduino)
            print(f"📡 Données Arduino reçues: {data}")
        except Exception as e:
            print(f"⚠️ Erreur Arduino: {e}")
            data = get_simulated_data()
    else:
        data = get_simulated_data()

    # Décision intelligente
    mode = decide_mode(data['ensoleillement'], data['debit'])
    leak_detected, leak_details = detect_leak(data['pression'], data['niveau_eau'])

    # Commande LED
    led_command = 'G' if mode == 'Solaire' and not leak_detected else 'B' if mode == 'Compression' and not leak_detected else 'R'
    
    if arduino:
        try:
            arduino.write(led_command.encode())
            print(f"📡 LED {led_command} envoyée")
        except Exception as e:
            print(f"⚠️ Erreur LED: {e}")
    else:
        print(f"[SIM] LED {led_command}")

    # Image thermique
    try:
        thermal_image = get_thermal_image()
    except:
        thermal_image = ""

    return jsonify({
        'mode': mode,
        'debit': data['debit'],
        'pression': data['pression'],
        'niveau_eau': data['niveau_eau'],
        'ensoleillement': data['ensoleillement'],
        'temperature': data['temperature'],
        'leak_detected': leak_detected,
        'leak_details': leak_details,
        'thermal_image': f'data:image/jpeg;base64,{thermal_image}',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'arduino_connected': arduino is not None
    })

@app.route('/api/control', methods=['POST'])
def control():
    """Endpoint pour contrôler manuellement le système"""
    mode = request.json.get('mode')
    if mode not in ['Solaire', 'Compression']:
        return jsonify({'error': 'Mode invalide'}), 400
    
    led_command = 'G' if mode == 'Solaire' else 'B'
    
    if arduino:
        try:
            arduino.write(led_command.encode())
            print(f"📡 Contrôle manuel - LED {led_command}")
        except Exception as e:
            print(f"⚠️ Erreur contrôle: {e}")
    else:
        print(f"[SIM] Contrôle manuel - LED {led_command}")
    
    return jsonify({
        'status': 'Mode forcé', 
        'mode': mode,
        'led_command': led_command,
        'arduino_connected': arduino is not None
    })

if __name__ == '__main__':
    print("🌡️ Système de Climatisation Backend")
    print("📡 Arduino:" if arduino else "🔧 Mode simulation")
    print("🚀 Serveur démarré sur http://127.0.0.1:5000")
    print("🔗 API disponible sur http://127.0.0.1:5000/api")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
