#include <ESP8266WiFi.h>
#include <PubSubClient.h>
const char* ssid     = "Gia Long";
const char* password = "0969143889";

/* ===== MQTT ===== */
const char* mqtt_server = "broker.hivemq.com";
const char* cmd_topic   = "lop9/relay/cmd";
const char* state_topic = "lop9/relay/state";

#define RELAY D1
#define RELAY_ON  LOW     // relay được kích hoạt ở chế độ LOW
#define RELAY_OFF HIGH
#define BUTTON D2 // tạo nút bấm D2       
WiFiClient espClient;
PubSubClient client(espClient);
bool trang_thai_chuong = false;
bool lastButtonState = HIGH;
void setChuong(bool bat) {
  trang_thai_chuong = bat;
  digitalWrite(RELAY, bat ? RELAY_ON : RELAY_OFF);
  client.publish(state_topic, bat ? "ON" : "OFF", true); //phần để gửi trạng thái của relay lên sever
}
void callback(char* topic, byte* payload, unsigned int length) {
  String msg = "";
  for (unsigned int i = 0; i < length; i++) {
    msg += (char)payload[i];
  }
  if (String(topic) == cmd_topic) {
    if (msg == "ON")  setChuong(true);
    if (msg == "OFF") setChuong(false);
  }
}
void reconnect() {
  while (!client.connected()) {
    String clientId = "ESP8266-" + String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      client.subscribe(cmd_topic);
      setChuong(false);
    } else {
      delay(2000);
    }
  }
}
void setup() {
  Serial.begin(9600);
  pinMode(RELAY, OUTPUT);
  pinMode(BUTTON, INPUT_PULLUP);
  digitalWrite(RELAY, RELAY_OFF);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
  }
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  bool btn = digitalRead(BUTTON);
  if (btn == LOW && lastButtonState == HIGH) {
    setChuong(true);
  }
  if (btn == HIGH && lastButtonState == LOW) {
    setChuong(false);
  }
  lastButtonState = btn;
  delay(20);
}
