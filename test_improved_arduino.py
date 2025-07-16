import serial
import time
from utils.serial_reader import read_arduino_data

def test_improved_arduino():
    """Test de l'Arduino avec le nouveau protocole de communication"""
    
    print("🌡️ Test Arduino AMÉLIORÉ - Système de Climatisation")
    print("=" * 60)
    print("📝 Ce test utilise le nouveau protocole avec marqueurs START/END")
    print("🔄 Assurez-vous d'avoir téléchargé arduino_code_improved.ino")
    print()
    
    try:
        # Connexion Arduino
        arduino = serial.Serial('COM5', 9600, timeout=3)
        time.sleep(2)
        print("✅ Arduino connecté sur COM5")
        
        # Vider le buffer au démarrage
        arduino.flushInput()
        time.sleep(1)
        
        # Test des LEDs
        print("\n🔴 Test des LEDs:")
        led_commands = [
            ('G', 'Verte (Mode Solaire)'),
            ('B', 'Bleue (Mode Compression)'),
            ('R', 'Rouge (Alerte Fuite)')
        ]
        
        for command, description in led_commands:
            print(f"  📡 Envoi commande '{command}' - LED {description}")
            arduino.write(command.encode())
            time.sleep(0.5)
            
            # Lire la confirmation
            if arduino.in_waiting > 0:
                response = arduino.readline().decode('utf-8').strip()
                print(f"  📥 Confirmation: {response}")
        
        print("\n📊 Test de lecture des données avec nouvelle fonction:")
        print("⚡ Ajustez les potentiomètres pour voir les valeurs changer...")
        
        for i in range(8):
            try:
                print(f"\n🔄 Lecture {i+1}/8:")
                
                # Utiliser la fonction améliorée
                data = read_arduino_data(arduino)
                
                print(f"  ✅ Données reçues avec succès:")
                print(f"      🔹 Débit: {data['debit']} L/min")
                print(f"      🔹 Pression: {data['pression']} bars")
                print(f"      🔹 Niveau eau: {data['niveau_eau']} %")
                print(f"      🔹 Ensoleillement: {data['ensoleillement']} W/m²")
                print(f"      🔹 Température: {data['temperature']} °C")
                
                # Test de la logique de décision
                if data['ensoleillement'] > 300 and data['debit'] > 40:
                    mode = "Solaire"
                    led_cmd = 'G'
                else:
                    mode = "Compression"
                    led_cmd = 'B'
                
                # Vérifier les fuites
                if data['pression'] < 1.5 or data['niveau_eau'] < 50:
                    mode = "ALERTE FUITE"
                    led_cmd = 'R'
                
                print(f"      🧠 Mode décidé: {mode}")
                arduino.write(led_cmd.encode())
                
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ Erreur: {e}")
                time.sleep(1)
        
        arduino.close()
        print("\n✅ Test terminé avec succès!")
        print("🚀 Vous pouvez maintenant lancer le backend:")
        print("   python app_no_arduino.py")
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        print("\n🔧 Vérifications:")
        print("  - Arduino connecté sur COM5")
        print("  - Code arduino_code_improved.ino téléchargé")
        print("  - Potentiomètres sur pins A0-A4")
        print("  - LEDs sur pins 9, 10, 11")

if __name__ == "__main__":
    test_improved_arduino()
