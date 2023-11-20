// Basic demo for accelerometer readings from Adafruit MPU6050

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include "EspMQTTClient.h"

Adafruit_MPU6050 mpu;

EspMQTTClient client(
  "MULTI_GUEST",   //wifi SSID
  "guest1357",     //wifi password
  "70.12.230.98",  // MQTT Broker server ip
  "MQTTUsername",
  "MQTTPassword",
  "TestClient",
  1883);

const int go_button = 18;    // the number of the pushbutton pin
const int back_button = 19;  // the number of the LED pin
volatile unsigned long button_time = 0, last_button_time = 0;
volatile bool go_button_pressed = false, back_button_pressed = false;

//송신용 tx()
char *tx_topic = "command";
void tx(char *cmd) {
  client.publish(tx_topic, cmd);  //topic , cmd
}

void go_changed(void) {
  button_time = millis();
  if (button_time - last_button_time > 100) {
    go_button_pressed = !go_button_pressed;
    last_button_time = button_time;
  }
}

void back_changed(void) {
  button_time = millis();
  if (button_time - last_button_time > 100) {
    back_button_pressed = !back_button_pressed;
    last_button_time = button_time;
  }
}

void setup(void) {
  Serial.begin(115200);
  client.enableHTTPWebUpdater();
  client.enableOTA();
  pinMode(go_button, INPUT_PULLUP);
  pinMode(back_button, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(go_button), go_changed, CHANGE);
  attachInterrupt(digitalPinToInterrupt(back_button), back_changed, CHANGE);

  while (!Serial)
    delay(10);  // will pause Zero, Leonardo, etc until serial console opens

  // Try to initialize!
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  delay(100);
}

void read_command(sensors_vec_t ac) {
  if (go_button_pressed) {
    tx("go");
  } else if (back_button_pressed) {
    tx("back");
  } else {
    tx("stop");
  }

  if (ac.y >= 6) {
    // Serial.println("left");
    tx("left");
  } else if (ac.y <= -6) {
    // Serial.println("right");
    tx("right");
  } else {
    tx("mid");
  }
}

void onConnectionEstablished() {
  //client.loop() 에 의해 호출되는 API
}

void loop() {

  /* Get new sensor events with the readings */
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  /* Print out the values */
  // Serial.print("Acceleration X: ");
  // Serial.print(a.acceleration.x);
  // Serial.print(", Y: ");
  // Serial.print(a.acceleration.y);
  // Serial.println();
  read_command(a.acceleration);
  client.loop();
  delay(500);
}