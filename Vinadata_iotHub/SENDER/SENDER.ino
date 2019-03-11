/*
  Using UDOpenLora_ArduinoShield for reading temperature and humdimity.
  
  Most UDOpenLora_ArduinoShield have an on-board Buzzer you can control. On the Uno, 
  it is attached to digital pin 6. If you're unsure what
  pin the on-board buzzer is connected to on your UDOpenLora_ArduinoShield model, check
  the documentation at https://github.com/udopenlora

  This example code is in the public domain.

  modified 25 January 2019
  by Dao Minh Canh & Nguyen Ta Quang
 */
 
#include <UDOpenLora.h>
#include "DHT.h"

#define DHTPIN 3    
#define DHTTYPE DHT11   
#define M0_PIN 7
#define M1_PIN 8
#define AUX_PIN 4
#define lora_power TSMT_PWR_30DB

DHT dht(DHTPIN, DHTTYPE);
HardwareSerial* debugSerial = &Serial;;
SoftwareSerial LoraSerial(10,9);// RX, TX
UDOpenLora loraBoard(&LoraSerial);
/*--------------SENDER------------*/

int networkAddrH = 0x35;
int networkAddrL = 0x35;
int networkChanel = 0x19;
int deviceAddrH = 0x00; // 1 device : 1 addrH & addrL : receiver device address
int deviceAddrL = 0x00;
byte ADDR_H, ADDR_L;

char msg[32];
float h = 0;
float t = 0;

void setup() {
  Serial.begin(9600); 
  dht.begin();
  LoraSerial.begin(9600);  
  loraBoard.setDebugPort(debugSerial);
  Serial.print("Configure Lora Module: ");
  loraBoard.setIOPin(M0_PIN, M1_PIN, AUX_PIN);
  delay(1000);
  loraBoard.LoraBegin((byte)(networkAddrH), (byte)(networkAddrL), (byte)(networkChanel), lora_power);
  Serial.println("SETUP DONE");
}

void loop() {
  h = dht.readHumidity();             //read data
  t = dht.readTemperature();          //read data
  if(isnan(h))
  {
    Serial.println("h = isnan");
    h = 0;
  }
  if(isnan(t))
  {
    Serial.println("t = isnan");
    t = 0;
  }
  char msg[32];
  sprintf (msg, "%s%d%s%d%s", "{\"T\":\"" , int((t*10)) , "\",\"H\":\"" , int((h*10)) , "\"}");
  loraBoard.SendMessage((byte)(deviceAddrH), (byte)(deviceAddrL), msg); //send message
  memset(msg,'\0',32);
  delay(5000);
}
