#include <Arduino.h>
#include <Wire.h>
#include <ClosedCube_HDC1080.h>
#include <ESP8266WiFi.h>        // Use ESP8266WiFi for ESP8266

#ifndef STASSID
//#define STASSID "dragino-266230"
//#define STAPSK "dragino+dragino"
#define STASSID "FAMILIA_PG"
#define STAPSK "NicolasAlejandro0715"
#define SERVER "107.22.132.30"
#endif

#define SDA_PIN D2   // Pin for SDA
#define SCL_PIN D1   // Pin for SCL

ClosedCube_HDC1080 hdc1080;

enum State {READ_TEMP, READ_HUMID, AVERAGE, WAIT, SEND_MESSAGE}; 
State currentState = READ_TEMP;

unsigned long previousMillis = 0;
const long sendInterval = 300000; // 5 minutes in milliseconds
const long waitInterval = 500;    // Smaller interval for non-blocking wait
int readingCounter = 0;
float tempReadings[10];
float humidReadings[10];
float avgTemp = 0.0, avgHumid = 0.0;

float average(float *array, int size);
void sendJsonData(float temperature, float humidity);

// WiFi credentials
const char* ssid = STASSID;
const char* password = STAPSK;

// Server details
const int port = 80;

WiFiClient client;  // Create a WiFiClient instance

void setup() {
  Serial.begin(115200);
  Wire.begin(SDA_PIN, SCL_PIN);  // Initialize I2C communication
  hdc1080.begin(0x40);           // HDC1080 I2C address

  // Connect to WiFi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println(" Connected!");

  Serial.println("HDC1080 sensor is ready!");
}

void loop() {
  unsigned long currentMillis = millis();

  switch (currentState) {
    case READ_TEMP:
      if (readingCounter < 10) {
        tempReadings[readingCounter] = hdc1080.readTemperature();
        currentState = READ_HUMID;
      } else {
        currentState = AVERAGE;
      }
      break;

    case READ_HUMID:
      if (readingCounter < 10) {
        humidReadings[readingCounter] = hdc1080.readHumidity();
        readingCounter++;
        currentState = WAIT;
      } else {
        currentState = AVERAGE;
      }
      break;

    case AVERAGE:
      // Calculate the averages
      avgTemp = average(tempReadings, 10);
      avgHumid = average(humidReadings, 10);
      currentState = WAIT; // Transition to WAIT after averaging
      break;

    case WAIT:
      if (currentMillis - previousMillis >= sendInterval) {
        currentState = SEND_MESSAGE;  // Proceed to SEND_MESSAGE if 5 minutes have passed
      } else {
        currentState = READ_TEMP;     // Otherwise, start reading again
      }
      break;

    case SEND_MESSAGE:
      sendJsonData(avgTemp, avgHumid);
      previousMillis = currentMillis; // Reset timer after sending
      readingCounter = 0;             // Reset counter for new readings
      currentState = READ_TEMP;       // Return to reading temperature
      break;
  }
}

// Function to calculate the average of an array
float average(float *array, int size) {
  float sum = 0.0;
  for (int i = 0; i < size; i++) {
    sum += array[i];
  }
  return sum / size;
}

// Function to send data in JSON format via POST request using WiFiClient
void sendJsonData(float temperature, float humidity) {
  if (!client.connect(SERVER, port)) {
    Serial.println("Connection to server failed");
    return;
  }

  // Create JSON string
  String jsonData = "{";
  jsonData += "\"temperature\": " + String(temperature, 2) + ",";
  jsonData += "\"humidity\": " + String(humidity, 2);
  jsonData += "}";

  // Prepare the HTTP POST request
  client.println("POST /endpoint HTTP/1.1");
  client.println("Host: " + String(SERVER));
  client.println("Content-Type: application/json");
  client.print("Content-Length: ");
  client.println(jsonData.length());
  client.println(""); // Blank line between headers and body
  client.println(jsonData); // Send JSON data

  // Read and display server response
  while (client.connected()) {
    String line = client.readStringUntil('\n');
    if (line == "\r") {
      break;
    }
  }

  Serial.println("Response:");
  while (client.available()) {
    String line = client.readStringUntil('\n');
    Serial.println(line);
  }

  client.stop(); // Close the connection
}
