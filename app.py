from flask import Flask, jsonify, request
from utils.serial_reader import read_arduino_data
from utils.image_processor import get_thermal_image
from utils.data_simulator import get_random_simulated_data
from models.rules_simple import decide_mode, detect_leak
import serial
import math

app = Flask(__name__)

# Connexion Arduino (ajuste 'COM3' selon ton port)
try:
    arduino = serial.Serial('COM3', 9600, timeout=1)
except:
    arduino = None  # Simuler si Arduino non connecté

@app.route('/api/system-status', methods=['GET'])
def system_status():
    # Lire données Arduino (ou simuler si non connecté)
    try:
        data = read_arduino_data(arduino)
    except:
        # Utiliser des données simulées depuis le fichier CSV
        data = get_random_simulated_data()

    # IA : Décider mode et détecter fuite
    mode = decide_mode(data['ensoleillement'], data['debit'])
    leak_detected, leak_details = detect_leak(data['pression'], data['niveau_eau'])

    # Commande LED
    led_command = 'G' if mode == 'Solaire' and not leak_detected else 'B' if mode == 'Compression' and not leak_detected else 'R'
    if arduino:
        arduino.write(led_command.encode())

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
        'timestamp': '2025-07-16 09:20'
    })

@app.route('/api/control', methods=['POST'])
def control():
    mode = request.json.get('mode')
    if mode not in ['Solaire', 'Compression']:
        return jsonify({'error': 'Mode invalide'}), 400
    led_command = 'G' if mode == 'Solaire' else 'B'
    if arduino:
        arduino.write(led_command.encode())
    return jsonify({'status': 'Mode forcé', 'mode': mode})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)