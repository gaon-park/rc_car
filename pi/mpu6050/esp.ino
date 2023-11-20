// Basic demo for accelerometer readings from Adafruit MPU6050

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include "EspMQTTClient.h"
#include "Thread.h"
#include "ThreadController.h"

Adafruit_MPU6050 mpu;

EspMQTTClient client(
  "MULTI_GUEST",   // wifi SSID
  "guest1357",     // wifi password
  "70.12.230.98",  // MQTT Broker server ip
  "MQTTUsername",
  "MQTTPassword",
  "TestClient",
  1883);

const int go_button = 18;     // the number of the go button pin
const int back_button = 19;   // the number of the back button pin
const int buzzer_button = 3;  // the number of the buzzer button pin

// 한 번만 보내기 위한 flg 변수
volatile bool command_go = false,
              command_back = false,
              command_stop = false,
              command_left = false,
              command_right = false,
              command_mid = false;
volatile bool command_buzzer = false;

char *cmd_topic = "command";
char *etc_topic = "etc";

//송신용 tx()
void tx(char *topic, char *cmd) {
  client.publish(topic, cmd);  //topic , cmd
}

// mpu Thread
class MPUThread : public Thread {
public:
  sensors_event_t a, g, temp;
  void cmd_mpu_check(sensors_vec_t ac) {
    if (ac.y >= 5 && !command_left) {
      // Serial.println("left");
      tx(cmd_topic, "left");
      command_left = true;
      command_right = false;
      command_mid = false;
    } else if (ac.y <= -6 && !command_right) {
      // Serial.println("right");
      tx(cmd_topic, "right");
      command_left = false;
      command_right = true;
      command_mid = false;
    } else if (-6 < ac.y && ac.y < 5 && !command_mid) {
      tx(cmd_topic, "mid");
      command_left = false;
      command_right = false;
      command_mid = true;
    }
  }

  void run() {
    mpu.getEvent(&a, &g, &temp);
    cmd_mpu_check(a.acceleration);
    runned();
  }
};

void cmd_button_check(void) {
  if (digitalRead(go_button) == LOW && !command_go) {
    // Serial.println("go");
    tx(cmd_topic, "go");
    command_go = true;
    command_back = false;
    command_stop = false;
  } else if (digitalRead(back_button) == LOW && !command_back) {
    // Serial.println("back");
    tx(cmd_topic, "back");
    command_go = false;
    command_back = true;
    command_stop = false;
  } else if (digitalRead(go_button) == HIGH && digitalRead(back_button) == HIGH && !command_stop) {
    // Serial.println("stop");
    tx(cmd_topic, "stop");
    command_go = false;
    command_back = false;
    command_stop = true;
  }
}

void etc_button_check(void) {
  if (digitalRead(buzzer_button) == LOW && !command_buzzer) {
    // Serial.println("buzzer_on");
    tx(etc_topic, "buzzer_on");
    command_buzzer = true;
  } else if (digitalRead(buzzer_button) == HIGH && command_buzzer) {
    // Serial.println("buzzer_off");
    tx(etc_topic, "buzzer_off");
    command_buzzer = false;
  }
}

// create thread
Thread cmd_th = Thread(),
       etc_th = Thread();
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

  pinMode(go_button, INPUT_PULLUP);
  pinMode(back_button, INPUT_PULLUP);
  pinMode(buzzer_button, INPUT_PULLUP);

  // callback thread func
  cmd_th.onRun(cmd_button_check);
  cmd_th.setInterval(50);
  etc_th.onRun(etc_button_check);
  etc_th.setInterval(50);

  controller.add(&mpu_th);
  controller.add(&cmd_th);
  controller.add(&etc_th);

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