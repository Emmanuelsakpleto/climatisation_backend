def read_arduino_data(arduino):
    """
    Lit les données Arduino avec le format actuel (avec TEMMPERATURE typo)
    Format: DEBIT:53.00,PRESSION:1.70,NIVEAU:61.00,ENSOLEILLEMENT:383.00,TEMMPERATURE:24.00
    """
    if not arduino:
        raise Exception("Arduino non connecté")
    
    try:
        # Lire une ligne complète
        line = arduino.readline().decode('utf-8').strip()
        
        if not line:
            raise Exception("Aucune donnée reçue")
        
        # Parser les données
        data = {}
        pairs = line.split(',')
        
        for pair in pairs:
            if ':' in pair:
                key, value = pair.split(':', 1)
                key = key.strip().upper()
                
                # Mapper les clés Arduino vers les clés backend (avec correction typo)
                if key == 'DEBIT':
                    data['debit'] = float(value)
                elif key == 'PRESSION':
                    data['pression'] = float(value)
                elif key == 'NIVEAU':
                    data['niveau_eau'] = float(value)
                elif key == 'ENSOLEILLEMENT':
                    data['ensoleillement'] = float(value)
                elif key in ['TEMPERATURE', 'TEMMPERATURE']:  # Gérer la typo
                    data['temperature'] = float(value)
        
        # Vérifier que toutes les données nécessaires sont présentes
        required_keys = ['debit', 'pression', 'niveau_eau', 'ensoleillement', 'temperature']
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            raise Exception(f"Données manquantes: {missing_keys}")
        
        return data
        
    except ValueError as e:
        raise Exception(f"Erreur de format des données: {e}")
    except Exception as e:
        raise Exception(f"Erreur de lecture série: {e}")
