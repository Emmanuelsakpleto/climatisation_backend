def read_arduino_data(arduino):
    if not arduino:
        raise Exception("Arduino non connecté")
    line = arduino.readline().decode().strip()
    if not line:
        raise Exception("Aucune donnée reçue")
    data = {}
    for item in line.split(','):
        key, value = item.split(':')
        data[key.lower()] = float(value)
    return data