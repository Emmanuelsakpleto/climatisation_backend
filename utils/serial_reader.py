def read_arduino_data(arduino):
    """
    Lit les données Arduino - Compatible avec l'ancien et nouveau format
    Formats supportés:
    - Ancien: DEBIT:53.00,PRESSION:1.70,NIVEAU:61.00,ENSOLEILLEMENT:383.00,TEMPERATURE:24.00
    - Nouveau: START:DEBIT:53.00,PRESSION:1.70,NIVEAU:61.00,ENSOLEILLEMENT:383.00,TEMPERATURE:24.00:END
    """
    if not arduino:
        raise Exception("Arduino non connecté")
    
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            # Lire ligne par ligne
            line = arduino.readline().decode('utf-8').strip()
            
            if not line:
                continue
            
            # Ignorer les messages système
            if line in ["ARDUINO_READY"] or line.startswith("LED:"):
                continue
                
            data_part = line
            
            # Vérifier si c'est le nouveau format avec START/END
            if line.startswith("START:") and line.endswith(":END"):
                data_part = line[6:-4]  # Enlever "START:" et ":END"
            
            # Parser les données
            data = {}
            pairs = data_part.split(',')
            
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    key = key.strip().upper()
                    
                    # Corriger la faute de frappe "TEMMPERATURE" -> "TEMPERATURE"
                    if key == 'TEMMPERATURE':
                        key = 'TEMPERATURE'
                    
                    # Mapper les clés Arduino vers les clés backend
                    if key == 'DEBIT':
                        data['debit'] = float(value)
                    elif key == 'PRESSION':
                        data['pression'] = float(value)
                    elif key == 'NIVEAU':
                        data['niveau_eau'] = float(value)
                    elif key == 'ENSOLEILLEMENT':
                        data['ensoleillement'] = float(value)
                    elif key == 'TEMPERATURE':
                        data['temperature'] = float(value)
            
            # Vérifier que toutes les données sont présentes
            required_keys = ['debit', 'pression', 'niveau_eau', 'ensoleillement', 'temperature']
            missing_keys = [key for key in required_keys if key not in data]
            
            if not missing_keys:
                return data
            else:
                # Afficher les données reçues pour debug
                print(f"⚠️ Ligne reçue: {line}")
                print(f"⚠️ Données parsées: {data}")
                print(f"⚠️ Clés manquantes: {missing_keys}")
                continue
                
        except Exception as e:
            print(f"⚠️ Erreur parsing ligne {attempt+1}: {e} - Ligne: {line}")
            continue
    
    raise Exception("Impossible de lire des données valides après plusieurs tentatives")