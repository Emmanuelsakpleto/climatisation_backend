import serial
import time

def test_arduino_connection():
    """Test la connexion Arduino sur différents ports"""
    ports_to_test = ['COM5', 'COM3', 'COM4', 'COM6']
    
    for port in ports_to_test:
        try:
            print(f"🔍 Test de connexion sur {port}...")
            arduino = serial.Serial(port, 9600, timeout=2)
            time.sleep(2)  # Attendre que l'Arduino soit prêt
            
            print(f"✅ Arduino connecté sur {port}")
            
            # Test de lecture des données
            try:
                arduino.write(b'G')  # Envoyer commande LED verte
                time.sleep(0.5)
                
                # Essayer de lire des données
                if arduino.in_waiting > 0:
                    data = arduino.readline().decode().strip()
                    print(f"📡 Données reçues: {data}")
                else:
                    print("📡 Aucune donnée reçue (normal si Arduino n'envoie pas encore)")
                    
            except Exception as e:
                print(f"⚠️ Erreur lors de la communication: {e}")
            
            arduino.close()
            return port
            
        except Exception as e:
            print(f"❌ Échec sur {port}: {e}")
    
    print("❌ Aucun Arduino trouvé sur les ports testés")
    return None

if __name__ == "__main__":
    print("🌡️ Test de connexion Arduino pour le système de climatisation")
    print("=" * 60)
    
    connected_port = test_arduino_connection()
    
    if connected_port:
        print(f"\n✅ Arduino détecté sur {connected_port}")
        print(f"📝 Mettre à jour le fichier app_no_arduino.py avec le port {connected_port}")
    else:
        print("\n❌ Aucun Arduino détecté")
        print("🔧 Le système fonctionnera en mode simulation")
        
    print("\n🚀 Vous pouvez maintenant lancer l'application avec:")
    print("   python app_no_arduino.py")
