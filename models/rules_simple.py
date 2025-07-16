def decide_mode(ensoleillement, debit):
    """Décide du mode de fonctionnement basé sur l'ensoleillement et le débit"""
    # Règle simple : mode solaire si ensoleillement > 300 W/m² et débit > 40 L/min
    if ensoleillement > 300 and debit > 40:
        return 'Solaire'
    else:
        return 'Compression'

def detect_leak(pression, niveau_eau):
    """Détecte une fuite basée sur la pression et le niveau d'eau"""
    if pression < 1.5 or niveau_eau < 50:
        return True, {
            'message': 'Fuite détectée dans le circuit hydraulique',
            'location': 'Pompe ou vanne',
            'severity': 'Élevée'
        }
    return False, {}
