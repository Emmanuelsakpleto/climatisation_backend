#include <Wire.h>
#include "rgb_lcd.h"

// LEDs
const int LED_BLUE[] = {1, 2, 10};       // Mode solaire
const int LED_RED[] = {3, 4, 5, 6, 9};   // Mode compression
const int LED_YELLOW = 11;              // Alerte fuite
const int BUZZER_PIN = 8;               // Buzzer

// Potentiomètres
#define POT_DEBIT A0
#define POT_PRESSION A1
#define POT_NIVEAU A2
#define POT_ENSOLEILLEMENT A3
#define POT_TEMPERATURE A4

// LCD
rgb_lcd lcd;

// Variables capteurs
float debit, pression, niveau_eau, ensoleillement, temperature;
String current_mode = "Automatique";
bool leak_detected = false;
bool auto_mode = true;

// Affichage cyclique sur LCD
int display_index = 0;
unsigned long last_update = 0;
const unsigned long display_interval = 2000; // 2 secondes

void setup() {
  lcd.begin(16, 2);
  lcd.setRGB(0, 255, 0);
  lcd.print("Amphi2-Clim-System");
  delay(1000);
  lcd.clear();
  
  Serial.begin(9600);

  for (int i = 0; i < 5; i++) pinMode(LED_RED[i], OUTPUT);
  for (int i = 0; i < 3; i++) pinMode(LED_BLUE[i], OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  // Test LEDs et buzzer
  for (int i = 0; i < 5; i++) {
    digitalWrite(LED_RED[i], HIGH); delay(200); digitalWrite(LED_RED[i], LOW);
  }
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_BLUE[i], HIGH); delay(200); digitalWrite(LED_BLUE[i], LOW);
  }
  digitalWrite(LED_YELLOW, HIGH); delay(200); digitalWrite(LED_YELLOW, LOW);
  digitalWrite(BUZZER_PIN, HIGH); delay(200); digitalWrite(BUZZER_PIN, LOW);

  Serial.println("ARDUINO_READY");
}

void loop() {
  lireCapteurs();
  logiqueMode();
  updateLEDs();
  sendDataToBackend();
  handleBackendCommands();
  delay(1000);
}

void lireCapteurs() {
  debit = map(analogRead(POT_DEBIT), 0, 1023, 20, 70);
  pression = map(analogRead(POT_PRESSION), 0, 1023, 10, 35) / 10.0;
  niveau_eau = map(analogRead(POT_NIVEAU), 0, 1023, 30, 100);
  ensoleillement = map(analogRead(POT_ENSOLEILLEMENT), 0, 1023, 0, 1000);
  temperature = map(analogRead(POT_TEMPERATURE), 0, 1023, 32, 40);
}

void logiqueMode() {
  if (auto_mode) {
    if (ensoleillement >= 800  && temperature <= 45)
      current_mode = "Solaire";
    else if (ensoleillement >= 400 && temperature <= 45)
      current_mode = "Hybride";
    else
      current_mode = "Compression";
  }

  leak_detected = (pression < 1.5 && niveau_eau < 50 && debit < 30);
}

void updateLEDs() {
  // Éteindre tout
  for (int i = 0; i < 5; i++) digitalWrite(LED_RED[i], LOW);
  for (int i = 0; i < 3; i++) digitalWrite(LED_BLUE[i], LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  lcd.clear();
  lcd.setCursor(0, 0);

  // Fuite en priorité
  if (leak_detected) {
    digitalWrite(LED_YELLOW, HIGH);
    digitalWrite(BUZZER_PIN, HIGH);
    lcd.print("Fuite detectee!");
    lcd.setRGB(255, 255, 0); // Jaune
  } else {
    // Ligne 1 : Mode
    if (current_mode == "Solaire") {
      for (int i = 0; i < 3; i++) digitalWrite(LED_BLUE[i], HIGH);
      lcd.print("Mode Solaire");
      lcd.setRGB(255, 0, 0); // Rouge
    } else if (current_mode == "Compression") {
      for (int i = 0; i < 5; i++) digitalWrite(LED_RED[i], HIGH);
      lcd.print("Mode Compression");
      lcd.setRGB(0, 0, 255); // Bleu
    } else if (current_mode == "Hybride") {
      for (int i = 0; i < 5; i++) digitalWrite(LED_RED[i], HIGH);
      for (int i = 0; i < 3; i++) digitalWrite(LED_BLUE[i], HIGH);
      lcd.print("Mode Hybride");
      lcd.setRGB(255, 165, 0); // Orange
    }

    // Ligne 2 : capteur cyclique
    lcd.setCursor(0, 1);
    if (millis() - last_update > display_interval) {
      display_index = (display_index + 1) % 5;
      last_update = millis();
    }

    switch (display_index) {
      case 0:
        lcd.print("Debit: "); lcd.print(debit, 0); lcd.print(" L/min");
        break;
      case 1:
        lcd.print("Pression: "); lcd.print(pression, 1); lcd.print(" b");
        break;
      case 2:
        lcd.print("Niveau: "); lcd.print(niveau_eau, 0); lcd.print(" %");
        break;
      case 3:
        lcd.print("Soleil: "); lcd.print(ensoleillement, 0); lcd.print(" lx");
        break;
      case 4:
        lcd.print("Temp: "); lcd.print(temperature, 1); lcd.print(" C");
        break;
    }
  }
}

void sendDataToBackend() {
  Serial.print("DEBIT:"); Serial.print(debit, 2);
  Serial.print(",PRESSION:"); Serial.print(pression, 2);
  Serial.print(",NIVEAU:"); Serial.print(niveau_eau, 2);
  Serial.print(",ENSOLEILLEMENT:"); Serial.print(ensoleillement, 2);
  Serial.print(",TEMPERATURE:"); Serial.print(temperature, 2);
  Serial.print(",MODE:"); Serial.println(current_mode);
}

void handleBackendCommands() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    switch (command) {
      case 'G': current_mode = "Solaire"; auto_mode = false; Serial.println("LED:RED"); break;
      case 'B': current_mode = "Compression"; auto_mode = false; Serial.println("LED:BLUE"); break;
      case 'H': current_mode = "Hybride"; auto_mode = false; Serial.println("LED:HYBRID"); break;
      case 'R': leak_detected = true; Serial.println("LED:YELLOW,BUZZER:ON"); break;
      case 'A': auto_mode = true; Serial.println("LED:AUTO"); break;
      case 'O':
        for (int i = 0; i < 5; i++) digitalWrite(LED_RED[i], LOW);
        for (int i = 0; i < 3; i++) digitalWrite(LED_BLUE[i], LOW);
        digitalWrite(LED_YELLOW, LOW);
        digitalWrite(BUZZER_PIN, LOW);
        lcd.clear(); lcd.print("Systeme Eteint");
        lcd.setRGB(0, 0, 0);
        Serial.println("LED:OFF,BUZZER:OFF");
        break;
    }
  }
}
