import serial
import time

def test_arduino_with_potentiometers():
    """Test complet de l'Arduino avec potentiomètres"""
    
    print("🌡️ Test Arduino - Système de Climatisation avec Potentiomètres")
    print("=" * 70)
    
    # Test de connexion
    try:
        arduino = serial.Serial('COM5', 9600, timeout=3)
        time.sleep(2)  # Attendre que l'Arduino soit prêt
        print("✅ Arduino connecté sur COM5")
        
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
            time.sleep(1)
        
        # Lecture des données des potentiomètres
        print("\n📊 Lecture des données capteurs (potentiomètres):")
        print("⚡ Ajustez les potentiomètres pour voir les valeurs changer...")
        
        for i in range(10):
            try:
                # Vider le buffer
                arduino.flushInput()
                
                # Lire une ligne
                line = arduino.readline().decode('utf-8').strip()
                
                if line:
                    print(f"  📥 Données reçues: {line}")
                    
                    # Parser les données
                    data = {}
                    pairs = line.split(',')
                    
                    for pair in pairs:
                        if ':' in pair:
                            key, value = pair.split(':', 1)
                            data[key.strip()] = float(value)
                    
                    # Afficher les valeurs parsées
                    if data:
                        print(f"      🔹 Débit: {data.get('DEBIT', 'N/A')} L/min")
                        print(f"      🔹 Pression: {data.get('PRESSION', 'N/A')} bars")
                        print(f"      🔹 Niveau eau: {data.get('NIVEAU', 'N/A')} %")
                        print(f"      🔹 Ensoleillement: {data.get('ENSOLEILLEMENT', 'N/A')} W/m²")
                        print(f"      🔹 Température: {data.get('TEMPERATURE', 'N/A')} °C")
                        
                        # Test de la logique de décision
                        ensoleillement = data.get('ENSOLEILLEMENT', 0)
                        debit = data.get('DEBIT', 0)
                        
                        if ensoleillement > 300 and debit > 40:
                            mode = "Solaire"
                            led_cmd = 'G'
                        else:
                            mode = "Compression"
                            led_cmd = 'B'
                        
                        print(f"      🧠 Mode décidé: {mode} (LED {led_cmd})")
                        arduino.write(led_cmd.encode())
                        
                        print("-" * 50)
                else:
                    print(f"  ⚠️ Aucune donnée reçue (tentative {i+1}/10)")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ Erreur lecture: {e}")
                time.sleep(1)
        
        arduino.close()
        print("\n✅ Test terminé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur de connexion Arduino: {e}")
        print("🔧 Vérifiez:")
        print("  - Arduino connecté sur COM5")
        print("  - Code Arduino téléchargé")
        print("  - Potentiomètres connectés aux pins A0-A4")
        print("  - LEDs connectées aux pins 9, 10, 11")

if __name__ == "__main__":
    test_arduino_with_potentiometers()
