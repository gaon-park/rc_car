// Basic demo for accelerometer readings from Adafruit MPU6050

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include "EspMQTTClient.h"
#include "Thread.h"
#include "ThreadController.h"
#include <Arduino.h>

Adafruit_MPU6050 mpu;

EspMQTTClient client(
  "MULTI_GUEST",   // wifi SSID
  "guest1357",     // wifi password
  "70.12.230.98",  // MQTT Broker server ip
  "LeftControllerID",
  "LeftControllerPW",
  "LeftController",
  1883);

#define GO_BUTTON 18                    // the number of the go button pin
#define BACK_BUTTON 19                  // the number of the back button pin
#define BUZZER_BUTTON 17                // the number of the buzzer button pin

// 한 번만 보내기 위한 flg 변수
volatile bool COMMAND_GO = false,
              COMMAND_BACK = false,
              COMMAND_STOP = false,
              COMMAND_LEFT_MIN = false,
              COMMAND_LEFT_MAX = false,
              COMMAND_RIGHT_MIN = false,
              COMMAND_RIGHT_MAX = false,
              COMMAND_MID = false,
              COMMAND_BUZZER = false;

char *CMD_TOPIC = "command";
char *ETC_TOPIC = "etc";

//송신용 tx()
void tx(char *topic, char *cmd) {
  client.publish(topic, cmd);  //topic , cmd
}

void command_direction_all_false(void) {
  COMMAND_LEFT_MIN = false;
  COMMAND_LEFT_MAX = false;
  COMMAND_RIGHT_MIN = false;
  COMMAND_RIGHT_MAX = false;
  COMMAND_MID = false;
}

// mpu Thread
class MPUThread : public Thread {
public:
  sensors_event_t a, g, temp;
  void cmd_mpu_check(sensors_vec_t ac) {
    if (ac.y > 3) {
      if (ac.y > 8 && !COMMAND_LEFT_MAX) {
        // Serial.println("left_max");
        tx(CMD_TOPIC, "left_max");
        command_direction_all_false();
        COMMAND_LEFT_MAX = true;
      }
      else if (ac.y <= 6 && !COMMAND_LEFT_MIN) {
        // Serial.println("left_min");
        tx(CMD_TOPIC, "left_min");
        command_direction_all_false();
        COMMAND_LEFT_MIN = true;
      }
    }
    else if (ac.y < -3) {
      if (ac.y < -8 && !COMMAND_RIGHT_MAX) {
        // Serial.println("right_max");
        tx(CMD_TOPIC, "right_max");
        command_direction_all_false();
        COMMAND_RIGHT_MAX = true;
      }
      else if (ac.y >= -6 && !COMMAND_RIGHT_MIN) {
        // Serial.println("right_min");
        tx(CMD_TOPIC, "right_min");
        command_direction_all_false();
        COMMAND_RIGHT_MIN = true;
      }
    }
    else if (-2 < ac.y && ac.y < 2 && !COMMAND_MID) {
      tx(CMD_TOPIC, "mid");
      command_direction_all_false();
      COMMAND_MID = true;
    }
  }

  void run() {
    mpu.getEvent(&a, &g, &temp);
    cmd_mpu_check(a.acceleration);
    runned();
  }
};

void command_all_false(void) {
  COMMAND_GO = false;
  COMMAND_BACK = false;
  COMMAND_STOP = false;
}

void cmd_button_check(void) {
  if (digitalRead(GO_BUTTON) == LOW && !COMMAND_GO) {
    // Serial.println("go");
    tx(CMD_TOPIC, "go");
    command_all_false();
    COMMAND_GO = true;
  } else if (digitalRead(BACK_BUTTON) == LOW && !COMMAND_BACK) {
    // Serial.println("back");
    tx(CMD_TOPIC, "back");
    command_all_false();
    COMMAND_BACK = true;
  } else if (digitalRead(GO_BUTTON) == HIGH && digitalRead(BACK_BUTTON) == HIGH && !COMMAND_STOP) {
    // Serial.println("stop");
    tx(CMD_TOPIC, "stop");
    command_all_false();
    COMMAND_STOP = true;
  }
}

void buzzer_button_check(void) {
  if (digitalRead(BUZZER_BUTTON) == LOW && !COMMAND_BUZZER) {
    // Serial.println("buzzer_on");
    tx(ETC_TOPIC, "buzzer_on");
    COMMAND_BUZZER = true;
  } else if (digitalRead(BUZZER_BUTTON) == HIGH && COMMAND_BUZZER) {
    // Serial.println("buzzer_off");
    tx(ETC_TOPIC, "buzzer_off");
    COMMAND_BUZZER = false;
  }
}

// create thread
Thread cmd_th = Thread(),
       buzzer_th = Thread();
MPUThread mpu_th = MPUThread();
ThreadController controller = ThreadController();

// This is the callback for the Timer
void timerCallback() {
  controller.run();
}

void setup(void) {
  Serial.begin(115200);
  client.enableHTTPWebUpdater();
  client.enableOTA();

  // command
  pinMode(GO_BUTTON, INPUT_PULLUP);
  pinMode(BACK_BUTTON, INPUT_PULLUP);

  // etc
  pinMode(BUZZER_BUTTON, INPUT_PULLUP);

  // callback thread func
  cmd_th.onRun(cmd_button_check);
  cmd_th.setInterval(50);
  buzzer_th.onRun(buzzer_button_check);
  buzzer_th.setInterval(50);

  controller.add(&mpu_th);
  controller.add(&cmd_th);
  controller.add(&buzzer_th);

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

void onConnectionEstablished() {
  //client.loop() 에 의해 호출되는 API
}

void loop() {
  controller.run();
  client.loop();
}