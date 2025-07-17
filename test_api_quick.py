#!/usr/bin/env python3
"""
🧪 Test rapide de l'API pour validation
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_api():
    print("🧪 Test de l'API de climatisation")
    print("=" * 50)
    
    # Test 1: Status
    print("\n1. 📊 Test de l'endpoint /api/status")
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data['status']}")
            print(f"   ✅ Mode: {data['mode']}")
            print(f"   ✅ Température: {data['temperature']}°C")
            print(f"   ✅ Ensoleillement: {data['ensoleillement']} W/m²")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 2: Mode actuel
    print("\n2. 🔧 Test de l'endpoint /api/mode (GET)")
    try:
        response = requests.get(f"{BASE_URL}/mode")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Mode actuel: {data['mode']}")
            print(f"   ✅ Forcé: {data['forced']}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 3: Changement de mode
    print("\n3. 🔄 Test de changement de mode")
    modes = ['solar', 'compression', 'hybrid', 'automatic']
    
    for mode in modes:
        try:
            response = requests.post(f"{BASE_URL}/mode", 
                                   json={"mode": mode},
                                   headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Mode {mode}: {data['message']}")
            else:
                print(f"   ❌ Mode {mode}: Erreur {response.status_code}")
        except Exception as e:
            print(f"   ❌ Mode {mode}: Erreur {e}")
        
        time.sleep(0.5)  # Pause entre les tests
    
    # Test 4: Historique
    print("\n4. 📈 Test de l'endpoint /api/history")
    try:
        response = requests.get(f"{BASE_URL}/history")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Historique: {len(data)} entrées")
            if data:
                print(f"   ✅ Dernière entrée: {data[0]['timestamp']}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Tests terminés!")

if __name__ == "__main__":
    test_api()
