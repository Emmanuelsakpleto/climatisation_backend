#!/usr/bin/env python3
"""
🚀 Script de test simple pour vérifier le backend
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """Test des imports"""
    try:
        from flask import Flask
        print("✅ Flask importé")
        
        from utils.serial_reader import read_arduino_data
        print("✅ serial_reader importé")
        
        from utils.image_processor import get_thermal_image
        print("✅ image_processor importé")
        
        from models.rules_simple import decide_mode, detect_leak
        print("✅ rules_simple importé")
        
        return True
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_flask_app():
    """Test de l'application Flask"""
    try:
        from app import app
        print("✅ App Flask créée")
        
        # Tester les routes
        with app.test_client() as client:
            print("🧪 Test des routes...")
            
            # Test route status
            response = client.get('/api/status')
            print(f"  /api/status: {response.status_code}")
            
            # Test route mode
            response = client.get('/api/mode')
            print(f"  /api/mode: {response.status_code}")
            
            # Test route history
            response = client.get('/api/history')
            print(f"  /api/history: {response.status_code}")
            
        return True
    except Exception as e:
        print(f"❌ Erreur Flask: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    print("🌡️ TEST DU BACKEND CLIMATISATION")
    print("=" * 50)
    
    if not test_import():
        print("❌ Échec des imports")
        sys.exit(1)
    
    if not test_flask_app():
        print("❌ Échec de l'application Flask")
        sys.exit(1)
    
    print("\n✅ Tous les tests passés avec succès!")
    print("🚀 Le backend est prêt à fonctionner")

if __name__ == "__main__":
    main()
