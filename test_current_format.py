import serial
import time
from utils.serial_reader import read_arduino_data

def test_current_arduino_format():
    """Test avec le format Arduino actuel (sans START/END)"""
    
    print("🌡️ Test Arduino - Format Actuel")
    print("=" * 50)
    
    try:
        arduino = serial.Serial('COM5', 9600, timeout=3)
        time.sleep(2)
        print("✅ Arduino connecté sur COM5")
        
        # Vider le buffer
        arduino.flushInput()
        time.sleep(1)
        
        print("\n📊 Test de lecture des données (format actuel):")
        
        for i in range(5):
            try:
                print(f"\n🔄 Lecture {i+1}/5:")
                
                # Utiliser la fonction adaptée
                data = read_arduino_data(arduino)
                
                print(f"  ✅ Données reçues:")
                print(f"      🔹 Débit: {data['debit']} L/min")
                print(f"      🔹 Pression: {data['pression']} bars")
                print(f"      🔹 Niveau eau: {data['niveau_eau']} %")
                print(f"      🔹 Ensoleillement: {data['ensoleillement']} W/m²")
                print(f"      🔹 Température: {data['temperature']} °C")
                
                # Test logique
                if data['ensoleillement'] > 300 and data['debit'] > 40:
                    mode = "Solaire"
                    led_cmd = 'G'
                else:
                    mode = "Compression"
                    led_cmd = 'B'
                
                if data['pression'] < 1.5 or data['niveau_eau'] < 50:
                    mode = "ALERTE FUITE"
                    led_cmd = 'R'
                
                print(f"      🧠 Mode: {mode}")
                arduino.write(led_cmd.encode())
                
                time.sleep(1)
                
            except Exception as e:
                print(f"  ❌ Erreur: {e}")
                time.sleep(1)
        
        arduino.close()
        print("\n✅ Test réussi!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_current_arduino_format()
