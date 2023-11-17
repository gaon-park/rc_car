// Basic demo for accelerometer readings from Adafruit MPU6050

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include "EspMQTTClient.h"

Adafruit_MPU6050 mpu;

EspMQTTClient client(
  "MULTI_GUEST",    //wifi SSID
  "guest1357",      //wifi password
  "70.12.230.98",    // MQTT Broker server ip
  "MQTTUsername",
  "MQTTPassword",
  "TestClient",
  1883
);

//송신용 tx()
char *tx_topic = "command";
void tx(char *cmd){
  client.publish(tx_topic, cmd); //topic , cmd
}

void setup(void) {
  Serial.begin(115200);
  client.enableHTTPWebUpdater();
  client.enableOTA();

  while (!Serial)
    delay(10); // will pause Zero, Leonardo, etc until serial console opens

  // Try to initialize!
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  Serial.print("Accelerometer range set to: ");
  switch (mpu.getAccelerometerRange()) {
  case MPU6050_RANGE_2_G:
    Serial.println("+-2G");
    break;
  case MPU6050_RANGE_4_G:
    Serial.println("+-4G");
    break;
  case MPU6050_RANGE_8_G:
    Serial.println("+-8G");
    break;
  case MPU6050_RANGE_16_G:
    Serial.println("+-16G");
    break;
  }
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  Serial.print("Gyro range set to: ");
  switch (mpu.getGyroRange()) {
  case MPU6050_RANGE_250_DEG:
    Serial.println("+- 250 deg/s");
    break;
  case MPU6050_RANGE_500_DEG:
    Serial.println("+- 500 deg/s");
    break;
  case MPU6050_RANGE_1000_DEG:
    Serial.println("+- 1000 deg/s");
    break;
  case MPU6050_RANGE_2000_DEG:
    Serial.println("+- 2000 deg/s");
    break;
  }

  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  Serial.print("Filter bandwidth set to: ");
  switch (mpu.getFilterBandwidth()) {
  case MPU6050_BAND_260_HZ:
    Serial.println("260 Hz");
    break;
  case MPU6050_BAND_184_HZ:
    Serial.println("184 Hz");
    break;
  case MPU6050_BAND_94_HZ:
    Serial.println("94 Hz");
    break;
  case MPU6050_BAND_44_HZ:
    Serial.println("44 Hz");
    break;
  case MPU6050_BAND_21_HZ:
    Serial.println("21 Hz");
    break;
  case MPU6050_BAND_10_HZ:
    Serial.println("10 Hz");
    break;
  case MPU6050_BAND_5_HZ:
    Serial.println("5 Hz");
    break;
  }

  Serial.println("");
  delay(100);
}

void read_acceleration(sensors_vec_t ac) {
  if (-4 < ac.x && ac.x < 4 && -2 < ac.y && ac.y < 2) {
    // Serial.println("stop");
    tx("mid stop");
  }
  else if (ac.x < -6) {
    if (ac.y >= 3) {
      // Serial.println("left go");
      tx("left go");
    }
    else if (ac.y <= -5) {
      // Serial.println("right go");
      tx("right go");
    }
    else {
      // Serial.println("go");
      tx("mid go");
    }
  }
  else if (ac.x >= 4) {
    if (ac.y >= 3) {
      // Serial.println("left back");
      tx("left back");
    }
    else if (ac.y <= -3) {
      // Serial.println("right back");
      tx("right back");
    }
    else {
      // Serial.println("back");
      tx("mid back");
    }
  }
  else {
    if (ac.y >= 6) {
      // Serial.println("left");
      tx("left");
    }
    else if (ac.y <= -6) {
      // Serial.println("right");
      tx("right");
    }
  }
}

void onConnectionEstablished(){
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
  read_acceleration(a.acceleration);
  client.loop();
  delay(500);
}