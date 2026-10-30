#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ESP32Servo.h> 

#define RST_PIN         22    
#define SS_PIN          21    
#define BUZZER_PIN      4     
#define RED_LED_PIN     15   // Chân 15 thực tế của bạn
#define GREEN_LED_PIN   2   
#define SERVO_PIN       27    

const char* ssid = "Giabao";           
const char* password = "11111111";    
const char* serverName = "http://192.168.56.1:5000/api/gate_out"; // Cập nhật IP .7

MFRC522 mfrc522(SS_PIN, RST_PIN);
LiquidCrystal_I2C lcd(0x27, 16, 2); 
Servo gateServo; 

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW); 
  digitalWrite(RED_LED_PIN, LOW);
  digitalWrite(GREEN_LED_PIN, LOW);

  gateServo.attach(SERVO_PIN);
  // 👉 ĐÃ SỬA: Khởi động ở góc 90 để gạt ngang đóng cổng
  gateServo.write(90); 

  Wire.begin(25, 26);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0); lcd.print("Dang ket noi...");

  WiFi.begin(ssid, password);
  while(WiFi.status() != WL_CONNECTED) { delay(500); }
  SPI.begin();
  mfrc522.PCD_Init();
  resetLCD();
}

void triggerError(String msg) {
  lcd.clear();
  lcd.setCursor(0, 0); lcd.print("!! TU CHOI !!");
  lcd.setCursor(0, 1); lcd.print(msg);
  digitalWrite(RED_LED_PIN, HIGH); 
  digitalWrite(BUZZER_PIN, HIGH);  
  delay(2500); 
  digitalWrite(RED_LED_PIN, LOW);  
  digitalWrite(BUZZER_PIN, LOW);   
  resetLCD();
}

void resetLCD() {
  lcd.clear();
  lcd.setCursor(0, 0); lcd.print("SMART PARKING OUT");
  lcd.setCursor(0, 1); lcd.print(" Moi quet the!  ");
}

void loop() {
  if ( ! mfrc522.PICC_IsNewCardPresent()) return;
  if ( ! mfrc522.PICC_ReadCardSerial()) return;

  digitalWrite(BUZZER_PIN, HIGH); delay(80); digitalWrite(BUZZER_PIN, LOW);
  
  String uidString = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if(mfrc522.uid.uidByte[i] < 0x10) uidString += "0";
    uidString += String(mfrc522.uid.uidByte[i], HEX);
  }
  uidString.toUpperCase();

  lcd.clear();
  lcd.setCursor(0, 0); lcd.print("UID: " + uidString);
  lcd.setCursor(0, 1); lcd.print("Checking AI...");

  if(WiFi.status() == WL_CONNECTED){
    HTTPClient http;
    http.begin(serverName); 
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST("{\"rfid_uid\":\"" + uidString + "\"}");
    
    if (httpResponseCode > 0) {
      String payload = http.getString();
      if (payload.indexOf("ERR_CHUA_VAO") != -1) triggerError("Xe chua vao bai!");
      else if (payload.indexOf("ERR_SAI_BIEN") != -1) triggerError("Sai bien so xe!");
      else if (payload.indexOf("ERR_KHONG_BIEN") != -1) triggerError("Khong co xe!");
      else if (payload.indexOf("OUTOK") != -1) {
        digitalWrite(GREEN_LED_PIN, HIGH);
        lcd.clear();
        lcd.setCursor(0, 0); lcd.print("XAC NHAN HOP LE");
        lcd.setCursor(0, 1); lcd.print("   MOI RA BAI   ");
        // 👉 ĐÃ SỬA: Mở gạt về 0, đóng gạt về 90
        gateServo.write(0); delay(4000); gateServo.write(90);
        digitalWrite(GREEN_LED_PIN, LOW);
        resetLCD();
      }
    } else triggerError("Loi Server HTTP!");
    http.end();
  } else triggerError("Loi mang Wi-Fi!");
  mfrc522.PICC_HaltA(); delay(500);
}