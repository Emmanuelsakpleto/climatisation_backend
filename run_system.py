#!/usr/bin/env python3
"""
Script de démarrage du système de climatisation
Détecte automatiquement l'Arduino et démarre le serveur Flask
"""

import subprocess
import sys
import os
import time
import serial
import serial.tools.list_ports

def find_arduino_port():
    """Trouve automatiquement le port Arduino"""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'Arduino' in port.description or 'USB' in port.description:
            return port.device
    return None

def check_arduino_connection(port):
    """Vérifie la connexion Arduino"""
    try:
        arduino = serial.Serial(port, 9600, timeout=2)
        time.sleep(2)
        # Tenter de lire une ligne
        arduino.readline()
        arduino.close()
        return True
    except:
        return False

def install_dependencies():
    """Installe les dépendances si nécessaire"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Dépendances installées")
    except:
        print("⚠️ Erreur installation dépendances")

def main():
    print("🌡️  Système de Climatisation Hybride")
    print("=====================================")
    
    # Installer les dépendances
    if os.path.exists('requirements.txt'):
        install_dependencies()
    
    # Chercher l'Arduino
    print("🔍 Recherche de l'Arduino...")
    arduino_port = find_arduino_port()
    
    if arduino_port:
        print(f"🔌 Arduino détecté sur {arduino_port}")
        if check_arduino_connection(arduino_port):
            print("✅ Connexion Arduino confirmée")
        else:
            print("⚠️ Arduino détecté mais connexion échouée")
            arduino_port = None
    else:
        print("⚠️ Arduino non trouvé, mode simulation activé")
    
    # Mettre à jour le port dans app.py
    if arduino_port:
        try:
            with open('app.py', 'r') as f:
                content = f.read()
            
            # Remplacer le port COM
            content = content.replace("arduino_port = 'COM5'", f"arduino_port = '{arduino_port}'")
            
            with open('app.py', 'w') as f:
                f.write(content)
            
            print(f"📝 Port Arduino mis à jour : {arduino_port}")
        except:
            print("⚠️ Impossible de mettre à jour le port Arduino")
    
    # Démarrer le serveur Flask
    print("\n🚀 Démarrage du serveur Flask...")
    print("📡 Serveur accessible sur http://127.0.0.1:5000")
    print("📊 Frontend sur http://127.0.0.1:5173")
    print("\nAppuyez sur Ctrl+C pour arrêter\n")
    
    try:
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur")

if __name__ == '__main__':
    main()
