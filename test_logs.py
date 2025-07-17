#!/usr/bin/env python3
"""
Test des logs pour vérifier que les emojis ne causent plus d'erreur
"""

import requests
import time

def test_logs():
    """Test des endpoints pour vérifier les logs"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Test des logs de l'API...")
    
    try:
        # Test GET /api/status
        print("1. Test GET /api/status")
        response = requests.get(f"{base_url}/api/status")
        print(f"   Status: {response.status_code}")
        
        # Test GET /api/mode
        print("2. Test GET /api/mode")
        response = requests.get(f"{base_url}/api/mode")
        print(f"   Status: {response.status_code}")
        
        # Test POST /api/mode
        print("3. Test POST /api/mode")
        response = requests.post(f"{base_url}/api/mode", json={"mode": "solar"})
        print(f"   Status: {response.status_code}")
        
        # Test GET /api/history
        print("4. Test GET /api/history")
        response = requests.get(f"{base_url}/api/history")
        print(f"   Status: {response.status_code}")
        
        print("✅ Tests terminés! Vérifiez le fichier climatisation.log")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Serveur non accessible. Assurez-vous que le serveur est démarré.")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_logs()
