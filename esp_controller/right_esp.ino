// Basic demo for accelerometer readings from Adafruit MPU6050

#include <Wire.h>
#include "EspMQTTClient.h"
#include "Thread.h"
#include "ThreadController.h"
#include <Arduino.h>
#include <RotaryEncoder.h>

EspMQTTClient client(
  "MULTI_GUEST",   // wifi SSID
  "guest1357",     // wifi password
  "70.12.230.98",  // MQTT Broker server ip
  "RightContollerID",
  "RightContollerPW",
  "RightContoller",
  1883);

const int rotary_encoder_sw = 36;
const int rotary_encoder_data = 39;
const int rotary_encoder_clk = 34;

volatile int counter = 0,  // 회전 카운터 측정용
  currentStateCLK = 0,     // CLK의 현재 신호상태 저장용
  lastStateCLK = 0;        // 직전 CLK의 신호상태 저장용

// 한 번만 보내기 위한 flg 변수
volatile bool command_rotary_button = false;

char *cmd_topic = "command";
char *etc_topic = "etc";

//송신용 tx()
void tx(char *topic, char *cmd) {
  client.publish(topic, cmd);  //topic , cmd
}

volatile int lastEncoded = 0, speed = 1;
volatile long encoderValue = 0;
volatile bool command_speed = false;
char rotary_command_base[10] = "speed=";
void rotary_check(void) {
  int clk = digitalRead(rotary_encoder_clk);
  int dt = digitalRead(rotary_encoder_data);
  int encoded = (clk << 1) | dt;
  int sum = (lastEncoded << 2) | encoded;

  if ((sum == 0b1101 || sum == 0b1011) && !command_speed) {  // left
    if (speed > 1) {                                         // min speed = 1
      speed--;
      rotary_command_base[6] = speed + '0';
      tx(cmd_topic, rotary_command_base);
    }
  }
  if (sum == 0b1110 || sum == 0b1000) {  // right
    if (speed < 9) {                     // max speed = 9
      speed++;
      rotary_command_base[6] = speed + '0';
      tx(cmd_topic, rotary_command_base);
    }
  }
  lastEncoded = encoded;
}

// create thread
Thread rotary_th = Thread();
ThreadController controller = ThreadController();

// This is the callback for the Timer
void timerCallback() {
  controller.run();
}

void setup(void) {
  Serial.begin(115200);
  client.enableHTTPWebUpdater();
  client.enableOTA();

  // etc
  pinMode(rotary_encoder_sw, INPUT);
  pinMode(rotary_encoder_data, INPUT);
  pinMode(rotary_encoder_clk, INPUT);

  // callback thread func
  rotary_th.onRun(rotary_check);
  rotary_th.setInterval(10);

  controller.add(&rotary_th);

  while (!Serial)
    delay(10);  // will pause Zero, Leonardo, etc until serial console opens
}

void onConnectionEstablished() {
  //client.loop() 에 의해 호출되는 API
}

void loop() {
  controller.run();
  client.loop();
}