import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib

# Charger le CSV généré
csv_path = 'simulated_data.csv'
df = pd.read_csv(csv_path)

# Features et label
X = df[['ensoleillement', 'debit', 'temperature']]
y = df['mode']

# Entraîner le modèle DecisionTree
model = DecisionTreeClassifier(max_depth=5, random_state=42)
model.fit(X, y)

# Sauvegarder le modèle entraîné
joblib.dump(model, 'decision_tree_mode.pkl')
print("✅ Modèle DecisionTree entraîné et sauvegardé dans 'decision_tree_mode.pkl'.")
