from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.serial_reader import read_arduino_data
from utils.image_processor import get_thermal_image
from models.rules_simple import decide_mode, detect_leak
import serial
import random
import time
import math

app = Flask(__name__)
CORS(app)  # Autoriser les requêtes Cross-Origin (frontend)

# Configuration Arduino
arduino = None
arduino_port = 'COM5'
current_forced_mode = None  # Mode forcé manuellement

def connect_arduino():
    """Tente de se connecter à l'Arduino"""
    global arduino
    try:
        if arduino:
            arduino.close()
        arduino = serial.Serial(arduino_port, 9600, timeout=3)
        time.sleep(2)  # Laisser le temps à l'Arduino de démarrer
        print("✅ Arduino connecté sur COM5")

        # Test LED verte
        arduino.write(b'G')
        time.sleep(0.5)
        return True
    except Exception as e:
        arduino = None
        print(f"❌ Arduino non connecté sur COM5: {e}")
        print("🔧 Mode simulation activé")
        return False

# Connexion initiale à l'Arduino
connect_arduino()

def calculate_humidity(temperature, ensoleillement, niveau_eau):
    """
    Calcule l'humidité relative basée sur les autres métriques physiques
    Ajusté pour le climat tropical du Burkina Faso
    
    Args:
        temperature: Température en °C (32-40°C)
        ensoleillement: Ensoleillement en W/m²
        niveau_eau: Niveau d'eau en %
    
    Returns:
        float: Humidité relative en %
    """
    base_humidity = 45  # Humidité de base plus basse pour climat chaud et sec
    
    # Facteur température : plus chaud = moins humide (ajusté pour 32-40°C)
    temp_factor = (40 - temperature) * 1.5
    
    # Facteur ensoleillement : plus de soleil = moins humide
    sun_factor = (ensoleillement / 1000) * -8
    
    # Facteur niveau d'eau : plus d'eau = plus humide
    water_factor = (niveau_eau - 50) * 0.4
    
    # Calcul final avec limites réalistes pour climat tropical
    humidity = base_humidity + temp_factor + sun_factor + water_factor
    
    # Limiter entre 15% et 85% (climat sec)
    return max(15, min(85, round(humidity, 1)))

def get_simulated_data():
    """Génère des données simulées réalistes avec variation circadienne"""
    hour = time.localtime().tm_hour
    
    # Simulation d'ensoleillement réaliste (jour/nuit)
    if 6 <= hour <= 18:
        base_sun = 800 * math.sin(math.pi * (hour - 6) / 12)
        sun_factor = max(0, base_sun + random.uniform(-100, 100))
    else:
        sun_factor = random.uniform(0, 50)  # Très faible la nuit

    data = {
        'debit': random.uniform(35, 65),
        'pression': random.uniform(1.8, 2.8),
        'niveau_eau': random.uniform(60, 95),
        'ensoleillement': sun_factor,
        'temperature': random.uniform(32, 40)  # Burkina Faso: 32-40°C
    }
    
    # Calculer l'humidité basée sur les autres métriques
    data['humidity'] = calculate_humidity(
        data['temperature'], 
        data['ensoleillement'], 
        data['niveau_eau']
    )
    
    return data

@app.route('/api/system-status', methods=['GET'])
def system_status():
    global arduino

    # Lire depuis l'Arduino ou passer en simulation
    if arduino:
        try:
            arduino.flushInput()  # Vider le buffer

            attempts = 0
            while attempts < 5:
                try:
                    data = read_arduino_data(arduino)
                    break
                except Exception as e:
                    attempts += 1
                    if attempts >= 5:
                        print(f"⚠️ Erreur lecture Arduino: {e}")
                        data = get_simulated_data()
                    time.sleep(0.2)
        except Exception as e:
            print(f"⚠️ Erreur Arduino: {e}")
            # Reconnexion
            if "PermissionError" in str(e) or "SerialException" in str(e):
                print("🔄 Tentative de reconnexion...")
                if connect_arduino():
                    try:
                        data = read_arduino_data(arduino)
                    except:
                        data = get_simulated_data()
                else:
                    data = get_simulated_data()
            else:
                data = get_simulated_data()
    else:
        data = get_simulated_data()

    # Traitement IA avec mode forcé
    mode = decide_mode(
        data['ensoleillement'], 
        data['debit'], 
        data['temperature'], 
        current_forced_mode
    )
    leak_detected, leak_details = detect_leak(data['pression'], data['niveau_eau'])

    # Définir la commande LED selon le mode et les fuites
    if leak_detected:
        led_command = 'R'  # Rouge pour fuite
    elif mode == 'Solaire':
        led_command = 'G'  # Vert pour solaire
    elif mode == 'Compression':
        led_command = 'B'  # Bleu pour compression
    elif mode == 'Hybride':
        led_command = 'H'  # Hybride (alternance ou couleur spéciale)
    else:
        led_command = 'A'  # Automatique

    # Envoyer la commande LED à l'Arduino
    if arduino:
        try:
            arduino.write(led_command.encode())
            color_map = {
                'G': 'Vert (Solaire)', 
                'B': 'Bleu (Compression)', 
                'R': 'Rouge (Fuite)', 
                'H': 'Hybride',
                'A': 'Automatique'
            }
            color = color_map.get(led_command, 'Inconnue')
            print(f"📡 LED Command envoyée: {led_command} ({color})")
        except Exception as e:
            print(f"⚠️ Erreur envoi commande LED: {e}")
    else:
        color_map = {
            'G': 'Vert (Solaire)', 
            'B': 'Bleu (Compression)', 
            'R': 'Rouge (Fuite)', 
            'H': 'Hybride',
            'A': 'Automatique'
        }
        color = color_map.get(led_command, 'Inconnue')
        print(f"[SIMULATION] LED Command: {led_command} ({color})")

    # Image thermique simulée
    thermal_image = get_thermal_image()

    return jsonify({
        'mode': mode,
        'debit': round(data['debit'], 1),
        'pression': round(data['pression'], 2),
        'niveau_eau': round(data['niveau_eau'], 1),
        'ensoleillement': round(data['ensoleillement'], 1),
        'temperature': round(data['temperature'], 1),
        'humidity': round(data['humidity'], 1),  # Humidité calculée
        'leak_detected': leak_detected,
        'leak_details': leak_details,
        'thermal_image': f'data:image/svg+xml;base64,{thermal_image}',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'arduino_connected': arduino is not None,
        'mode_forced': current_forced_mode is not None
    })

@app.route('/api/control', methods=['POST'])
def control():
    global current_forced_mode
    
    mode = request.json.get('mode')
    action = request.json.get('action', 'set')  # 'set' ou 'auto'
    
    if action == 'auto':
        # Retour au mode automatique
        current_forced_mode = None
        led_command = 'A'
        print("🤖 Mode automatique activé")
    else:
        # Mode forcé
        if mode not in ['Solaire', 'Compression', 'Hybride']:
            return jsonify({'error': 'Mode invalide'}), 400
        
        current_forced_mode = mode
        led_command = {
            'Solaire': 'G',
            'Compression': 'B', 
            'Hybride': 'H'
        }.get(mode, 'A')
        print(f"🎛️ Mode forcé: {mode}")

    # Envoyer la commande à l'Arduino
    if arduino:
        try:
            arduino.write(led_command.encode())
            color_map = {
                'G': 'Vert (Solaire)', 
                'B': 'Bleu (Compression)', 
                'H': 'Hybride',
                'A': 'Automatique'
            }
            color = color_map.get(led_command, 'Inconnue')
            print(f"📡 Contrôle manuel - LED Command: {led_command} ({color})")
        except Exception as e:
            print(f"⚠️ Erreur contrôle manuel: {e}")
    else:
        color_map = {
            'G': 'Vert (Solaire)', 
            'B': 'Bleu (Compression)', 
            'H': 'Hybride',
            'A': 'Automatique'
        }
        color = color_map.get(led_command, 'Inconnue')
        print(f"[SIMULATION] Manual LED Command: {led_command} ({color})")

    return jsonify({
        'status': 'Mode automatique' if action == 'auto' else 'Mode forcé',
        'mode': mode if action != 'auto' else 'Automatique',
        'led_command': led_command,
        'arduino_connected': arduino is not None,
        'forced_mode': current_forced_mode
    })

if __name__ == '__main__':
    print("🌡️  Système de Climatisation Backend")
    print("📡 Arduino connecté." if arduino else "🔧 Mode simulation (Arduino non connecté)")
    print("🚀 Serveur démarré sur http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
