// Arduino Uno : Simulation avancée avec potentiomètres
// Simulation des modes et détection de fuites

#define LED_GREEN 9  // Mode solaire
#define LED_BLUE 10  // Mode compression
#define LED_RED 11   // Fuite/anomalie

// Potentiomètres
#define POT_DEBIT A0
#define POT_PRESSION A1
#define POT_NIVEAU A2
#define POT_ENSOLEILLEMENT A3
#define POT_TEMPERATURE A4

// Variables pour la simulation
float debit, pression, niveau_eau, ensoleillement, temperature;
String current_mode = "Compression";
bool leak_detected = false;
bool auto_mode = true;  // Mode automatique par défaut

void setup() {
  Serial.begin(9600);
  
  // Configuration LEDs
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  
  // Test LEDs au démarrage
  digitalWrite(LED_GREEN, HIGH);
  delay(200);
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_BLUE, HIGH);
  delay(200);
  digitalWrite(LED_BLUE, LOW);
  digitalWrite(LED_RED, HIGH);
  delay(200);
  digitalWrite(LED_RED, LOW);
  
  Serial.println("ARDUINO_READY");
}

void loop() {
  // Lire les potentiomètres avec conversion en valeurs réalistes
  debit = map(analogRead(POT_DEBIT), 0, 1023, 30, 70);
  pression = map(analogRead(POT_PRESSION), 0, 1023, 10, 35) / 10.0;  // 1.0 à 3.5 bar
  niveau_eau = map(analogRead(POT_NIVEAU), 0, 1023, 30, 100);
  ensoleillement = map(analogRead(POT_ENSOLEILLEMENT), 0, 1023, 0, 1000);
  temperature = map(analogRead(POT_TEMPERATURE), 0, 1023, 18, 32);

  // Logique automatique de décision de mode (comme dans le backend)
  if (auto_mode) {
    if (ensoleillement > 300 && debit > 40) {
      current_mode = "Solaire";
    } else {
      current_mode = "Compression";
    }
  }
  
  // Détection de fuite (comme dans le backend)
  leak_detected = (pression < 1.5 || niveau_eau < 50);
  
  // Contrôle des LEDs selon le mode et l'état
  updateLEDs();
  
  // Envoyer données au format attendu par le backend
  sendDataToBackend();
  
  // Recevoir commandes du backend
  handleBackendCommands();
  
  delay(1000);
}

void updateLEDs() {
  // Éteindre toutes les LEDs
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_BLUE, LOW);
  digitalWrite(LED_RED, LOW);
  
  // Priorité à la fuite (LED rouge)
  if (leak_detected) {
    digitalWrite(LED_RED, HIGH);
  } else {
    // Afficher le mode actuel
    if (current_mode == "Solaire") {
      digitalWrite(LED_GREEN, HIGH);
    } else if (current_mode == "Compression") {
      digitalWrite(LED_BLUE, HIGH);
    }
  }
}

void sendDataToBackend() {
  // Format exact attendu par le backend
  Serial.print("DEBIT:"); Serial.print(debit, 2);
  Serial.print(",PRESSION:"); Serial.print(pression, 2);
  Serial.print(",NIVEAU:"); Serial.print(niveau_eau, 2);
  Serial.print(",ENSOLEILLEMENT:"); Serial.print(ensoleillement, 2);
  Serial.print(",TEMPERATURE:"); Serial.println(temperature, 2);
}

void handleBackendCommands() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    switch (command) {
      case 'G':  // Mode solaire forcé
        current_mode = "Solaire";
        auto_mode = false;
        digitalWrite(LED_GREEN, HIGH);
        digitalWrite(LED_BLUE, LOW);
        Serial.println("LED:GREEN");
        break;
        
      case 'B':  // Mode compression forcé
        current_mode = "Compression";
        auto_mode = false;
        digitalWrite(LED_BLUE, HIGH);
        digitalWrite(LED_GREEN, LOW);
        Serial.println("LED:BLUE");
        break;
        
      case 'R':  // Alerte fuite
        digitalWrite(LED_RED, HIGH);
        digitalWrite(LED_GREEN, LOW);
        digitalWrite(LED_BLUE, LOW);
        Serial.println("LED:RED");
        break;
        
      case 'A':  // Mode automatique
        auto_mode = true;
        Serial.println("LED:AUTO");
        break;
        
      case 'O':  // Éteindre toutes les LEDs
        digitalWrite(LED_GREEN, LOW);
        digitalWrite(LED_BLUE, LOW);
        digitalWrite(LED_RED, LOW);
        Serial.println("LED:OFF");
        break;
    }
  }
}
