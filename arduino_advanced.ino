#define LED_GREEN 9     // Mode solaire
#define LED_BLUE 10     // Mode compression  
#define LED_RED 11      // Fuite/anomalie
#define LED_YELLOW 12   // Mode hybride

// Potentiomètres
#define POT_DEBIT A0
#define POT_PRESSION A1
#define POT_NIVEAU A2
#define POT_ENSOLEILLEMENT A3
#define POT_TEMPERATURE A4

// Variables pour la simulation
float debit, pression, niveau_eau, ensoleillement, temperature;
String current_mode = "Automatique";
bool leak_detected = false;
bool auto_mode = true;
bool hybrid_toggle = false;  // Pour alterner les LEDs en mode hybride
unsigned long last_hybrid_toggle = 0;

void setup() {
  Serial.begin(9600);
  
  // Configuration LEDs
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  if (LED_YELLOW != LED_RED) pinMode(LED_YELLOW, OUTPUT);
  
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
  
  if (LED_YELLOW != LED_RED) {
    digitalWrite(LED_YELLOW, HIGH);
    delay(200);
    digitalWrite(LED_YELLOW, LOW);
  }
  
  Serial.println("ARDUINO_READY");
}

void loop() {
  // Lire les potentiomètres avec conversion en valeurs réalistes (Burkina Faso)
  debit = map(analogRead(POT_DEBIT), 0, 1023, 30, 70);
  pression = map(analogRead(POT_PRESSION), 0, 1023, 10, 35) / 10.0;  // 1.0 à 3.5 bar
  niveau_eau = map(analogRead(POT_NIVEAU), 0, 1023, 30, 100);
  ensoleillement = map(analogRead(POT_ENSOLEILLEMENT), 0, 1023, 0, 1000);
  temperature = map(analogRead(POT_TEMPERATURE), 0, 1023, 32, 40);  // Burkina: 32-40°C

  // Logique automatique de décision de mode (corrigée)
  if (auto_mode) {
    if (ensoleillement >= 800 && debit >= 40 && temperature <= 45) {
      current_mode = "Solaire";
    } else if (ensoleillement >= 400 && ensoleillement < 800 && debit >= 40 && temperature <= 45) {
      current_mode = "Hybride";
    } else {
      current_mode = "Compression";
    }
  }
  
  // Détection de fuite améliorée
  leak_detected = (pression < 1.5 && niveau_eau < 50 && debit < 30);
  
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
  if (LED_YELLOW != LED_RED) digitalWrite(LED_YELLOW, LOW);
  
  // Priorité à la fuite (LED rouge)
  if (leak_detected) {
    digitalWrite(LED_RED, HIGH);
  } else {
    // Afficher le mode actuel
    if (current_mode == "Solaire") {
      digitalWrite(LED_GREEN, HIGH);
    } else if (current_mode == "Compression") {
      digitalWrite(LED_BLUE, HIGH);
    } else if (current_mode == "Hybride") {
      // Mode hybride - alternance ou combinaison
      if (millis() - last_hybrid_toggle > 1000) {
        hybrid_toggle = !hybrid_toggle;
        last_hybrid_toggle = millis();
      }
      
      if (hybrid_toggle) {
        digitalWrite(LED_GREEN, HIGH);
      } else {
        digitalWrite(LED_BLUE, HIGH);
      }
      
      // Ou allumer LED_YELLOW si disponible
      if (LED_YELLOW != LED_RED) {
        digitalWrite(LED_YELLOW, HIGH);
      }
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
        Serial.println("LED:GREEN");
        break;
        
      case 'B':  // Mode compression forcé
        current_mode = "Compression";
        auto_mode = false;
        Serial.println("LED:BLUE");
        break;
        
      case 'H':  // Mode hybride forcé
        current_mode = "Hybride";
        auto_mode = false;
        Serial.println("LED:HYBRID");
        break;
        
      case 'R':  // Alerte fuite
        leak_detected = true;
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
        if (LED_YELLOW != LED_RED) digitalWrite(LED_YELLOW, LOW);
        Serial.println("LED:OFF");
        break;
    }
  }
}