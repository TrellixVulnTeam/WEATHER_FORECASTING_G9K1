#include "ThingSpeak.h" //install library for thing speak
#include <ESP8266WiFi.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_Sensor.h>
#include <AHT10.h>
#include <Wire.h>
#include <SPI.h>

#define D1 5
#define D2 4
#define D3 0
#define D5 14
//
//#define BMP_SCK  13
//#define BMP_MISO 12
//#define BMP_MOSI 11
//#define BMP_CS   10

char ssid[] = "iPhone de Ayoub";
char pass[] = "delay_ms(368)";
int keyIndex = 0;

WiFiClient client;
Adafruit_BMP280 bmp;
AHT10  myAHT10;

//Thingspeak configue
unsigned long myChannelNumber = 1419929;
const char * myWriteAPIKey = "80U29RR7VKI94XHL";
// Initialize our values
String myStatus = "";


void setup() {
  Serial.begin(115200);  //Initialize serial

  WiFi.mode(WIFI_STA);   
  ThingSpeak.begin(client);  // Initialize ThingSpeak
  
  while(!myAHT10.begin(0x38)){
      Serial.println("setup error");
    delay(1000);
   }
  while(!bmp.begin(0x76))
  {
    Serial.println("Could not find BME280 sensor!");
    delay(1000);
  }
  
//bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
//                 Adafruit_BMP280::SAMPLING_X2,
//                 Adafruit_BMP280::SAMPLING_X16,
//                 Adafruit_BMP280::FILTER_X16,
//                 Adafruit_BMP280::STANDBY_MS_500);
}

void loop() {
  // Connect or reconnect to WiFi
  if(WiFi.status() != WL_CONNECTED){
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    while(WiFi.status() != WL_CONNECTED){
      WiFi.begin(ssid, pass);  // Connect to WPA/WPA2 network. Change this line if using open or WEP network
      Serial.print(".");
      delay(5000);     
    } 
    Serial.println("\nConnected.");
  }
  
float tem = myAHT10.readTemperature(AHT10_FORCE_READ_DATA);
float hum = myAHT10.readHumidity(AHT10_FORCE_READ_DATA);
float pres = bmp.readPressure();

  // set the fields with the values
  ThingSpeak.setField(1, tem);
  ThingSpeak.setField(2, hum);  
  ThingSpeak.setField(3, pres);


  // set the status
  ThingSpeak.setStatus(myStatus);
  
  // write to the ThingSpeak channel
  int x = ThingSpeak.writeFields(myChannelNumber, myWriteAPIKey);
  if(x == 200){
    Serial.println("Channel update successful.");
  }
  else{
    Serial.println("Problem updating channel. HTTP error code " + String(x));
  }
  delay(20000); // Wait 20 seconds to update the channel again
}
