from sklearn.tree import DecisionTreeClassifier
import pandas as pd
import numpy as np

def train_model():
    """Créer et entraîner un modèle de décision avec des données simulées"""
    # Créer des données simulées pour l'entraînement
    np.random.seed(42)
    n_samples = 1000
    
    # Génération de données simulées
    ensoleillement = np.random.uniform(0, 1000, n_samples)
    debit = np.random.uniform(20, 80, n_samples)
    pression = np.random.uniform(1.0, 3.0, n_samples)
    niveau_eau = np.random.uniform(30, 100, n_samples)
    
    # Règle pour déterminer le mode
    mode = ['Solaire' if (e > 300 and d > 40) else 'Compression' 
            for e, d in zip(ensoleillement, debit)]
    
    # Créer le DataFrame
    data = pd.DataFrame({
        'ensoleillement': ensoleillement,
        'debit': debit,
        'pression': pression,
        'niveau_eau': niveau_eau,
        'mode': mode
    })
    
    X = data[['ensoleillement', 'debit', 'pression', 'niveau_eau']]
    y = data['mode']
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X, y)
    return model

# Entraîner le modèle au démarrage
model = train_model()

def decide_mode(ensoleillement, debit):
    """Décide du mode de fonctionnement basé sur l'ensoleillement et le débit"""
    try:
        # Utiliser le modèle ML avec des valeurs par défaut pour pression et niveau_eau
        prediction = model.predict([[ensoleillement, debit, 2.0, 75.0]])[0]
        return prediction
    except:
        # Fallback sur la règle simple si le modèle échoue
        return 'Solaire' if ensoleillement > 300 and debit > 40 else 'Compression'

def detect_leak(pression, niveau_eau):
    """Détecte une fuite basée sur la pression et le niveau d'eau"""
    if pression < 1.5 or niveau_eau < 50:
        return True, {
            'message': 'Fuite détectée dans le circuit hydraulique',
            'location': 'Pompe ou vanne',
            'severity': 'Élevée'
        }
    return False, {}