#!/usr/bin/env python3
"""
🔧 Test simple pour identifier le problème d'importation
"""

print("🧪 Test étape par étape...")

# Test 1: Imports de base
print("\n1. Test des imports de base...")
try:
    from flask import Flask, jsonify, request
    print("✅ Flask imports OK")
except Exception as e:
    print(f"❌ Flask imports: {e}")
    exit(1)

try:
    from flask_cors import CORS
    print("✅ CORS import OK")
except Exception as e:
    print(f"❌ CORS import: {e}")
    exit(1)

# Test 2: Imports des modules locaux
print("\n2. Test des imports locaux...")
try:
    from utils.serial_reader import read_arduino_data
    print("✅ serial_reader import OK")
except Exception as e:
    print(f"❌ serial_reader import: {e}")

try:
    from utils.image_processor import get_thermal_image
    print("✅ image_processor import OK")
except Exception as e:
    print(f"❌ image_processor import: {e}")

try:
    from models.rules_simple import decide_mode, detect_leak
    print("✅ rules_simple import OK")
except Exception as e:
    print(f"❌ rules_simple import: {e}")

# Test 3: Imports système
print("\n3. Test des imports système...")
try:
    import serial
    print("✅ serial import OK")
except Exception as e:
    print(f"❌ serial import: {e}")

try:
    import random
    import time
    import math
    print("✅ random, time, math imports OK")
except Exception as e:
    print(f"❌ random, time, math imports: {e}")

# Test 4: Créer une app Flask basique
print("\n4. Test création app Flask...")
try:
    app = Flask(__name__)
    CORS(app)
    print("✅ App Flask créée avec succès")
    print(f"App: {app}")
    print(f"App name: {app.name}")
except Exception as e:
    print(f"❌ Création app Flask: {e}")
    exit(1)

# Test 5: Tester les routes
print("\n5. Test des routes...")
try:
    @app.route('/test')
    def test_route():
        return jsonify({"status": "OK"})
    
    print("✅ Route de test créée")
    
    with app.test_client() as client:
        response = client.get('/test')
        print(f"✅ Test route: {response.status_code}")
        
except Exception as e:
    print(f"❌ Test routes: {e}")

print("\n🎉 Tous les tests terminés!")
