def decide_mode(ensoleillement, debit, temperature=None, mode_force=None):
    """
    Décide du mode de fonctionnement basé sur l'ensoleillement, le débit et la température
    Modes disponibles : Solaire, Compression, Hybride, Automatique
    """
    # Si mode forcé (manuel), le retourner
    if mode_force and mode_force in ['Solaire', 'Compression', 'Hybride']:
        return mode_force
        
    # Mode automatique - logique IA améliorée
    if ensoleillement > 500 and debit > 45 and (temperature is None or temperature < 26):
        return 'Solaire'
    elif ensoleillement > 200 and debit > 30 and (temperature is None or temperature < 30):
        return 'Hybride'
    else:
        return 'Compression'

def detect_leak(pression, niveau_eau):
    """Détecte une fuite basée sur la pression et le niveau d'eau"""
    if pression < 1.5 or niveau_eau < 50:
        severity = 'Élevée' if pression < 1.2 or niveau_eau < 30 else 'Moyenne'
        location = 'Circuit principal' if pression < 1.2 else 'Réservoir'
        return True, {
            'message': f'Fuite détectée - Pression: {pression:.1f} bar, Niveau: {niveau_eau:.1f}%',
            'location': location,
            'severity': severity
        }
    return False, {}
