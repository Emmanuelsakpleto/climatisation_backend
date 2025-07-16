import base64
import os

def get_thermal_image():
    # Simuler image thermique avec un fichier placeholder
    image_path = os.path.join(os.path.dirname(__file__), '../data/frame.jpg')
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        return base64.b64encode(image_data).decode()
    except FileNotFoundError:
        return ""  # Placeholder vide si image absente