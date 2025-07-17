import pandas as pd
import random
import os

def get_random_simulated_data():
    """Retourne des données aléatoires depuis le fichier CSV simulé"""
    try:
        # Chemin vers le fichier CSV
        csv_path = os.path.join(os.path.dirname(__file__), 'simulated_data.csv')
        
        # Lire le fichier CSV
        df = pd.read_csv(csv_path)
        
        # Sélectionner une ligne aléatoire
        random_row = df.sample(n=1).iloc[0]
        
        # Retourner les données au format attendu
        return {
            'debit': float(random_row['debit']),
            'pression': float(random_row['pression']),
            'niveau_eau': float(random_row['niveau_eau']),
            'ensoleillement': float(random_row['ensoleillement']),
            'temperature': float(random_row['temperature'])
        }
    except Exception as e:
        print(f"Erreur lors de la lecture du CSV: {e}")
        # Fallback sur des données par défaut
        return {
            'debit': 50.0,
            'pression': 2.5,
            'niveau_eau': 80.0,
            'ensoleillement': 800.0,
            'temperature': 37.0
        }
