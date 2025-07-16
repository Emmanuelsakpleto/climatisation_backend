import pandas as pd
import numpy as np

# Fixer la graine pour reproductibilité
np.random.seed(42)
n_rows = 1000

# Générer données simulées
data = {
    'ensoleillement': np.random.uniform(0, 1000, n_rows),  # 0-1000 W/m²
    'debit': np.random.uniform(40, 60, n_rows),           # 40-60 L/min
    'pression': np.random.uniform(1.0, 3.0, n_rows),      # 1.0-3.0 bars
    'niveau_eau': np.random.uniform(45, 90, n_rows),      # 45-90 %
    'temperature': np.random.uniform(20, 30, n_rows),     # 20-30 °C
    'mode': []
}

# Appliquer règle pour déterminer le mode
for i in range(n_rows):
    if data['ensoleillement'][i] > 300 and data['debit'][i] > 40:
        data['mode'].append('Solaire')
    else:
        data['mode'].append('Compression')

# Simuler anomalies (10% des cas) pour représenter des fuites
anomaly_indices = np.random.choice(n_rows, int(n_rows * 0.1), replace=False)
for i in anomaly_indices:
    if np.random.rand() > 0.5:
        data['pression'][i] = np.random.uniform(1.0, 1.5)  # Basse pression (fuite)
    else:
        data['niveau_eau'][i] = np.random.uniform(45, 50)  # Bas niveau d'eau (fuite)

# Créer DataFrame et sauvegarder
df = pd.DataFrame(data)
df.to_csv('simulated_data.csv', index=False)
print(f"Fichier 'simulated_data.csv' généré avec {n_rows} lignes.")