from flask import Flask, jsonify, request
from utils.serial_reader import read_arduino_data
from utils.image_processor import get_thermal_image
from models.rules_simple import decide_mode, detect_leak
import serial
import random
import time
import math

app = Flask(__name__)

# Connexion Arduino (ajuste 'COM3' selon ton port)
try:
    arduino = serial.Serial('COM3', 9600, timeout=1)
except:
    arduino = None  # Simuler si Arduino non connecté

def get_simulated_data():
    """Génère des données simulées réalistes"""
    # Variation basée sur l'heure pour simuler le cycle jour/nuit
    hour = time.localtime().tm_hour
    sun_factor = max(0, 1000 * (0.5 + 0.5 * math.cos((hour - 12) * math.pi / 12)))
    
    # Ajouter de la variabilité aléatoire
    return {
        'debit': random.uniform(45, 65),
        'pression': random.uniform(2.0, 2.8),
        'niveau_eau': random.uniform(75, 95),
        'ensoleillement': sun_factor + random.uniform(-50, 50),
        'temperature': random.uniform(22, 28)
    }

@app.route('/api/system-status', methods=['GET'])
def system_status():
    # Lire données Arduino (ou simuler si non connecté)
    if arduino:
        try:
            data = read_arduino_data(arduino)
        except:
            data = get_simulated_data()
    else:
        data = get_simulated_data()

    # IA : Décider mode et détecter fuite
    mode = decide_mode(data['ensoleillement'], data['debit'])
    leak_detected, leak_details = detect_leak(data['pression'], data['niveau_eau'])

    # Commande LED (simulation)
    led_command = 'G' if mode == 'Solaire' and not leak_detected else 'B' if mode == 'Compression' and not leak_detected else 'R'
    if arduino:
        arduino.write(led_command.encode())
    else:
        print(f"[SIMULATION] LED Command: {led_command} ({'Green' if led_command == 'G' else 'Blue' if led_command == 'B' else 'Red'})")

    # Simuler image thermique
    thermal_image = get_thermal_image()

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
    mode = request.json.get('mode')
    if mode not in ['Solaire', 'Compression']:
        return jsonify({'error': 'Mode invalide'}), 400
    
    led_command = 'G' if mode == 'Solaire' else 'B'
    if arduino:
        arduino.write(led_command.encode())
    else:
        print(f"[SIMULATION] Manual LED Command: {led_command} ({'Green' if led_command == 'G' else 'Blue'})")
    
    return jsonify({
        'status': 'Mode forcé', 
        'mode': mode,
        'arduino_connected': arduino is not None
    })

if __name__ == '__main__':
    print("🌡️  Système de Climatisation Backend")
    print("📡 Arduino connecté:" if arduino else "🔧 Mode simulation (Arduino non connecté)")
    print("🚀 Serveur démarré sur http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
