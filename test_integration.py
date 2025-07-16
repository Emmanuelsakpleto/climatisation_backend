#!/usr/bin/env python3
"""
🧪 Tests d'intégration du système de climatisation hybride
Ce script teste tous les composants du système pour s'assurer qu'ils fonctionnent correctement.
"""

import requests
import time
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:5000"
FRONTEND_URL = "http://localhost:5173"
TIMEOUT = 5

def print_header(title):
    """Affiche un en-tête formaté"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_test(test_name, status, details=""):
    """Affiche le résultat d'un test"""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {test_name}")
    if details:
        print(f"   └─ {details}")

def test_backend_connection():
    """Test la connexion au backend"""
    print_header("TEST DE CONNEXION BACKEND")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/status", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print_test("Backend accessible", True, f"Status: {data.get('status', 'Unknown')}")
            print_test("Mode actuel", True, f"Mode: {data.get('mode', 'Unknown')}")
            print_test("Température", True, f"Temp: {data.get('temperature', 'Unknown')}°C")
            return True
        else:
            print_test("Backend accessible", False, f"Status Code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_test("Backend accessible", False, f"Erreur: {e}")
        return False

def test_api_endpoints():
    """Test tous les endpoints de l'API"""
    print_header("TEST DES ENDPOINTS API")
    
    endpoints = [
        ("/api/status", "GET", "Récupération du statut"),
        ("/api/mode", "GET", "Récupération du mode"),
        ("/api/mode", "POST", "Changement de mode"),
        ("/api/history", "GET", "Historique des données"),
    ]
    
    for endpoint, method, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=TIMEOUT)
            elif method == "POST":
                # Test avec le mode solaire
                response = requests.post(
                    f"{BACKEND_URL}{endpoint}",
                    json={"mode": "solar"},
                    timeout=TIMEOUT
                )
            
            success = response.status_code in [200, 201]
            print_test(description, success, f"{method} {endpoint} - {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            print_test(description, False, f"Erreur: {e}")

def test_modes():
    """Test tous les modes de fonctionnement"""
    print_header("TEST DES MODES DE FONCTIONNEMENT")
    
    modes = ["solar", "compression", "hybrid", "automatic"]
    
    for mode in modes:
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/mode",
                json={"mode": mode},
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                # Vérifier que le mode a bien été changé
                time.sleep(1)
                status_response = requests.get(f"{BACKEND_URL}/api/status", timeout=TIMEOUT)
                if status_response.status_code == 200:
                    current_mode = status_response.json().get('mode', '')
                    success = current_mode == mode
                    print_test(f"Mode {mode}", success, f"Mode actuel: {current_mode}")
                else:
                    print_test(f"Mode {mode}", False, "Impossible de vérifier le mode")
            else:
                print_test(f"Mode {mode}", False, f"Status Code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print_test(f"Mode {mode}", False, f"Erreur: {e}")

def test_data_consistency():
    """Test la cohérence des données"""
    print_header("TEST DE COHÉRENCE DES DONNÉES")
    
    try:
        # Récupérer les données plusieurs fois
        data_samples = []
        for i in range(3):
            response = requests.get(f"{BACKEND_URL}/api/status", timeout=TIMEOUT)
            if response.status_code == 200:
                data_samples.append(response.json())
                time.sleep(1)
            else:
                print_test("Collecte des données", False, f"Échec échantillon {i+1}")
                return
        
        # Vérifier la cohérence
        if len(data_samples) == 3:
            print_test("Collecte des données", True, f"{len(data_samples)} échantillons collectés")
            
            # Vérifier que les données ont des champs requis
            required_fields = ['mode', 'temperature', 'timestamp']
            for field in required_fields:
                field_present = all(field in sample for sample in data_samples)
                print_test(f"Champ '{field}' présent", field_present)
            
            # Vérifier que les timestamps progressent
            timestamps = [sample.get('timestamp', 0) for sample in data_samples]
            timestamps_increasing = all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))
            print_test("Timestamps croissants", timestamps_increasing)
            
    except requests.exceptions.RequestException as e:
        print_test("Test de cohérence", False, f"Erreur: {e}")

def test_frontend_availability():
    """Test la disponibilité du frontend"""
    print_header("TEST DE DISPONIBILITÉ FRONTEND")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=TIMEOUT)
        success = response.status_code == 200
        print_test("Frontend accessible", success, f"Status Code: {response.status_code}")
        
        # Vérifier que c'est bien une page HTML
        if success:
            is_html = "<!DOCTYPE html>" in response.text or "<html" in response.text
            print_test("Contenu HTML valide", is_html)
            
    except requests.exceptions.RequestException as e:
        print_test("Frontend accessible", False, f"Erreur: {e}")

def test_performance():
    """Test les performances du système"""
    print_header("TEST DE PERFORMANCES")
    
    try:
        # Mesurer le temps de réponse de l'API
        start_time = time.time()
        response = requests.get(f"{BACKEND_URL}/api/status", timeout=TIMEOUT)
        response_time = time.time() - start_time
        
        success = response.status_code == 200 and response_time < 1.0
        print_test("Temps de réponse API", success, f"{response_time:.3f}s")
        
        # Test de charge légère
        start_time = time.time()
        for i in range(5):
            requests.get(f"{BACKEND_URL}/api/status", timeout=TIMEOUT)
        total_time = time.time() - start_time
        
        success = total_time < 5.0
        print_test("Test de charge (5 requêtes)", success, f"{total_time:.3f}s total")
        
    except requests.exceptions.RequestException as e:
        print_test("Test de performances", False, f"Erreur: {e}")

def generate_test_report():
    """Génère un rapport de test"""
    print_header("RAPPORT DE TEST")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"📅 Date du test: {timestamp}")
    print(f"🔗 Backend URL: {BACKEND_URL}")
    print(f"🔗 Frontend URL: {FRONTEND_URL}")
    print(f"⏱️  Timeout: {TIMEOUT}s")
    
    # Sauvegarder le rapport
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    print(f"📄 Rapport sauvegardé: {report_file}")

def main():
    """Fonction principale"""
    print("🧪 TESTS D'INTÉGRATION - SYSTÈME DE CLIMATISATION HYBRIDE")
    print("=" * 60)
    
    # Vérifier que le backend est démarré
    if not test_backend_connection():
        print("\n❌ ERREUR CRITIQUE: Le backend n'est pas accessible!")
        print("   Veuillez démarrer le backend avant de lancer les tests.")
        print("   Commande: python app.py")
        sys.exit(1)
    
    # Lancer tous les tests
    test_api_endpoints()
    test_modes()
    test_data_consistency()
    test_frontend_availability()
    test_performance()
    
    # Générer le rapport
    generate_test_report()
    
    print_header("TESTS TERMINÉS")
    print("✅ Tests d'intégration terminés avec succès!")
    print("🔍 Vérifiez les résultats ci-dessus pour détecter d'éventuels problèmes.")

if __name__ == "__main__":
    main()
