import base64
import os
import random
import time
from io import BytesIO

def create_thermal_simulation():
    """Crée une simulation d'image thermique basique"""
    # Créer une image SVG simulée qui représente une caméra thermique
    width, height = 320, 240
    
    # Générer des zones de température
    zones = []
    for i in range(5):
        x = random.randint(0, width-50)
        y = random.randint(0, height-50)
        temp = 20 + random.uniform(0, 15)
        
        # Couleur selon température
        if temp < 25:
            color = f"rgb(0, {int(temp*10)}, 255)"  # Bleu
        elif temp < 30:
            color = f"rgb(0, 255, {int((30-temp)*51)})"  # Vert
        else:
            color = f"rgb(255, {int((35-temp)*51)}, 0)"  # Rouge
            
        zones.append((x, y, color, temp))
    
    # Créer SVG
    svg_content = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="rgb(50,50,100)"/>
    <text x="10" y="20" fill="white" font-family="Arial" font-size="14">Caméra Thermique - Simulation</text>
    <text x="10" y="35" fill="white" font-family="Arial" font-size="10">Temps: {time.strftime("%H:%M:%S")}</text>
    '''
    
    for x, y, color, temp in zones:
        svg_content += f'<circle cx="{x}" cy="{y}" r="25" fill="{color}" opacity="0.7"/>'
        svg_content += f'<text x="{x-15}" y="{y+3}" fill="white" font-family="Arial" font-size="10">{temp:.1f}°C</text>'
    
    svg_content += '</svg>'
    
    return base64.b64encode(svg_content.encode()).decode()

def get_thermal_image():
    """Génère une image thermique simulée"""
    try:
        # Essayer d'abord avec une vraie image si elle existe
        image_path = os.path.join(os.path.dirname(__file__), '../data/frame.jpg')
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                image_data = f.read()
            return base64.b64encode(image_data).decode()
    except:
        pass
    
    # Sinon, créer une simulation
    return create_thermal_simulation()

def get_thermal_image_fallback():
    """Fallback avec fichier existant ou simulation"""
    return get_thermal_image()