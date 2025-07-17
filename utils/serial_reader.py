def calculate_humidity(temperature, ensoleillement, niveau_eau):
    """
    Calcule l'humidité relative basée sur les autres métriques physiques
    Ajusté pour le climat tropical du Burkina Faso
    
    Args:
        temperature: Température en °C (32-40°C)
        ensoleillement: Ensoleillement en W/m²
        niveau_eau: Niveau d'eau en %
    
    Returns:
        float: Humidité relative en %
    """
    base_humidity = 45  # Humidité de base plus basse pour climat chaud et sec
    
    # Facteur température : plus chaud = moins humide (ajusté pour 32-40°C)
    temp_factor = (40 - temperature) * 1.5
    
    # Facteur ensoleillement : plus de soleil = moins humide
    sun_factor = (ensoleillement / 1000) * -8
    
    # Facteur niveau d'eau : plus d'eau = plus humide
    water_factor = (niveau_eau - 50) * 0.4
    
    # Calcul final avec limites réalistes pour climat tropical
    humidity = base_humidity + temp_factor + sun_factor + water_factor
    
    # Limiter entre 15% et 85% (climat sec)
    return max(15, min(85, round(humidity, 1)))

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
                # Calculer l'humidité basée sur les autres métriques
                data['humidity'] = calculate_humidity(
                    data['temperature'], 
                    data['ensoleillement'], 
                    data['niveau_eau']
                )
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