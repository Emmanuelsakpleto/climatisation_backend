#!/usr/bin/env python3
"""
Script de démarrage rapide pour tester l'API
"""
import requests
import time
import json

def test_api():
    """Test de l'API Backend"""
    base_url = "http://127.0.0.1:5000/api"
    
    print("🌡️ Test API Backend - Système de Climatisation")
    print("=" * 60)
    
    # Test de santé
    print("🔍 Test de connexion...")
    try:
        response = requests.get(f"{base_url}/system-status", timeout=5)
        if response.status_code == 200:
            print("✅ Backend connecté!")
            
            # Afficher les données
            data = response.json()
            print(f"\n📊 Données système:")
            print(f"  🔹 Mode: {data['mode']}")
            print(f"  🔹 Débit: {data['debit']} L/min")
            print(f"  🔹 Pression: {data['pression']} bars")
            print(f"  🔹 Niveau eau: {data['niveau_eau']} %")
            print(f"  🔹 Ensoleillement: {data['ensoleillement']} W/m²")
            print(f"  🔹 Température: {data['temperature']} °C")
            print(f"  🔹 Arduino connecté: {data['arduino_connected']}")
            print(f"  🔹 Fuite détectée: {data['leak_detected']}")
            
            # Test contrôle
            print(f"\n🎛️ Test contrôle des modes:")
            modes = ['Solaire', 'Compression']
            
            for mode in modes:
                try:
                    control_response = requests.post(
                        f"{base_url}/control",
                        json={'mode': mode},
                        timeout=5
                    )
                    if control_response.status_code == 200:
                        print(f"  ✅ Mode {mode} activé")
                    else:
                        print(f"  ❌ Erreur mode {mode}: {control_response.status_code}")
                    time.sleep(1)
                except Exception as e:
                    print(f"  ❌ Erreur contrôle {mode}: {e}")
            
        else:
            print(f"❌ Erreur backend: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Impossible de se connecter au backend: {e}")
        print("🔧 Assurez-vous que le backend est démarré:")
        print("   python app_no_arduino.py")

if __name__ == "__main__":
    test_api()
