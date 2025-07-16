/*
 * Code Arduino pour système de climatisation hybride
 * Envoie des données simulées via le port série
 * Contrôle des LEDs selon les commandes reçues
 */

// Pins des LEDs
const int LED_GREEN = 2;   // LED verte (mode solaire)
const int LED_BLUE = 3;    // LED bleue (mode compression)
const int LED_RED = 4;     // LED rouge (alerte fuite)

// Variables pour simulation des capteurs
float debit = 50.0;
float pression = 2.5;
float niveau_eau = 80.0;
float ensoleillement = 800.0;
float temperature = 24.0;

// Timing pour l'envoi des données
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 2000; // Envoie toutes les 2 secondes

void setup() {
  // Initialiser le port série
  Serial.begin(9600);
  
  // Configurer les pins des LEDs
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  
  // Test initial des LEDs
  testLEDs();
  
  Serial.println("Arduino climatisation - Prêt");
}

void loop() {
  // Lire les commandes depuis le port série
  if (Serial.available() > 0) {
    char command = Serial.read();
    handleCommand(command);
  }
  
  // Envoyer les données des capteurs
  if (millis() - lastSendTime >= sendInterval) {
    sendSensorData();
    lastSendTime = millis();
  }
  
  // Simuler des variations des capteurs
  updateSensorValues();
  
  delay(100);
}

void handleCommand(char command) {
  // Éteindre toutes les LEDs
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_BLUE, LOW);
  digitalWrite(LED_RED, LOW);
  
  switch (command) {
    case 'G': // Green - Mode solaire
      digitalWrite(LED_GREEN, HIGH);
      Serial.println("LED_MODE:SOLAIRE");
      break;
      
    case 'B': // Blue - Mode compression
      digitalWrite(LED_BLUE, HIGH);
      Serial.println("LED_MODE:COMPRESSION");
      break;
      
    case 'R': // Red - Alerte fuite
      digitalWrite(LED_RED, HIGH);
      Serial.println("LED_MODE:ALERTE");
      break;
      
    default:
      Serial.println("LED_MODE:INCONNU");
      break;
  }
}

void sendSensorData() {
  // Format: paramettre:valeur,paramettre:valeur,...
  Serial.print("debit:");
  Serial.print(debit);
  Serial.print(",pression:");
  Serial.print(pression);
  Serial.print(",niveau_eau:");
  Serial.print(niveau_eau);
  Serial.print(",ensoleillement:");
  Serial.print(ensoleillement);
  Serial.print(",temperature:");
  Serial.println(temperature);
}

void updateSensorValues() {
  // Simuler des variations légères des capteurs
  debit += random(-2, 3);
  if (debit < 40) debit = 40;
  if (debit > 70) debit = 70;
  
  pression += random(-10, 11) / 100.0;
  if (pression < 1.5) pression = 1.5;
  if (pression > 3.0) pression = 3.0;
  
  niveau_eau += random(-2, 3);
  if (niveau_eau < 60) niveau_eau = 60;
  if (niveau_eau > 95) niveau_eau = 95;
  
  ensoleillement += random(-50, 51);
  if (ensoleillement < 0) ensoleillement = 0;
  if (ensoleillement > 1000) ensoleillement = 1000;
  
  temperature += random(-5, 6) / 10.0;
  if (temperature < 20) temperature = 20;
  if (temperature > 35) temperature = 35;
}

void testLEDs() {
  // Test séquentiel des LEDs au démarrage
  digitalWrite(LED_GREEN, HIGH);
  delay(300);
  digitalWrite(LED_GREEN, LOW);
  
  digitalWrite(LED_BLUE, HIGH);
  delay(300);
  digitalWrite(LED_BLUE, LOW);
  
  digitalWrite(LED_RED, HIGH);
  delay(300);
  digitalWrite(LED_RED, LOW);
  
  Serial.println("Test LEDs terminé");
}
