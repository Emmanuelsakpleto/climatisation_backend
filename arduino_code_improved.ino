// Arduino Uno : Simulation avec potentiomètres - VERSION CORRIGÉE
#define LED_GREEN 9  // Mode solaire
#define LED_BLUE 10  // Mode compression
#define LED_RED 11   // Fuite/anomalie
#define POT_DEBIT A0
#define POT_PRESSION A1
#define POT_NIVEAU A2
#define POT_ENSOLEILLEMENT A3
#define POT_TEMPERATURE A4

void setup() {
  Serial.begin(9600);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  
  // Message de démarrage
  Serial.println("ARDUINO_READY");
  delay(1000);
}

void loop() {
  // Lire potentiomètres avec moyennage pour stabilité
  float debit = map(analogRead(POT_DEBIT), 0, 1023, 40, 60);
  float pression = map(analogRead(POT_PRESSION), 0, 1023, 15, 30) / 10.0;
  float niveau_eau = map(analogRead(POT_NIVEAU), 0, 1023, 50, 90);
  float ensoleillement = map(analogRead(POT_ENSOLEILLEMENT), 0, 1023, 0, 1000);
  float temperature = map(analogRead(POT_TEMPERATURE), 0, 1023, 20, 30);

  // Envoyer données avec marqueur de début et fin
  Serial.print("START:");
  Serial.print("DEBIT:"); Serial.print(debit);
  Serial.print(",PRESSION:"); Serial.print(pression);
  Serial.print(",NIVEAU:"); Serial.print(niveau_eau);
  Serial.print(",ENSOLEILLEMENT:"); Serial.print(ensoleillement);
  Serial.print(",TEMPERATURE:"); Serial.print(temperature);
  Serial.println(":END");

  // Recevoir commande LED
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    // Éteindre toutes les LEDs
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_BLUE, LOW);
    digitalWrite(LED_RED, LOW);
    
    // Allumer la LED correspondante
    switch(command) {
      case 'G':
        digitalWrite(LED_GREEN, HIGH);
        Serial.println("LED:GREEN_ON");
        break;
      case 'B':
        digitalWrite(LED_BLUE, HIGH);
        Serial.println("LED:BLUE_ON");
        break;
      case 'R':
        digitalWrite(LED_RED, HIGH);
        Serial.println("LED:RED_ON");
        break;
    }
    
    // Vider le buffer
    while(Serial.available() > 0) {
      Serial.read();
    }
  }
  
  delay(1000);
}
