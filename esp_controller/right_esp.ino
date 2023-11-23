// Basic demo for accelerometer readings from Adafruit MPU6050

#include <Wire.h>
#include "EspMQTTClient.h"
#include "Thread.h"
#include "ThreadController.h"
#include <Arduino.h>
#include <RotaryEncoder.h>
#include <Keypad.h>

EspMQTTClient client(
  "MULTI_GUEST",   // wifi SSID
  "guest1357",     // wifi password
  "70.12.230.98",  // MQTT Broker server ip
  "RightControllerID",
  "RightControllerPW",
  "RightController",
  1883);

#define ROTARY_ENCODER_SW 36
#define ROTARY_ENCODER_DATA 39
#define ROTARY_ENCODER_CLK 34

const byte ROWS = 4;  // define row 4
const byte COLS = 4;  // define column 4
const char KEYS[ROWS][COLS] = {
  { '0', '1', '2', '3' },
  { '4', '5', '6', '7' },
  { '8', '9', 'A', 'B' },
  { 'C', 'D', 'E', 'F' }
};

// connect row ports of the button to corresponding IO ports on the board
byte ROW_PINS[ROWS] = { 18, 5, 17, 16 };
// connect column ports of the button to corresponding IO ports on the board
byte COL_PINS[COLS] = { 23, 22, 21, 19 };
// call class library performance function of Keypad
Keypad KEYPAD = Keypad(makeKeymap(KEYS), ROW_PINS, COL_PINS, ROWS, COLS);

char *CMD_TOPIC = "command";
char *LCD_TOPIC = "lcd";

//송신용 tx()
void tx(char *topic, char *cmd) {
  client.publish(topic, cmd);  //topic , cmd
}

volatile int LAST_ENCODED = 0, SPEED = 1;
volatile bool COMMAND_SPEED = false;
char rotary_command_base[10] = "speed=";
void rotary_check(void) {
  int clk = digitalRead(ROTARY_ENCODER_CLK);
  int dt = digitalRead(ROTARY_ENCODER_DATA);
  int encoded = (clk << 1) | dt;
  int sum = (LAST_ENCODED << 2) | encoded;

  if ((sum == 0b1101 || sum == 0b1011) && !COMMAND_SPEED) {  // left
    if (SPEED > 1) {                                         // min SPEED = 1
      // Serial.println("rotary change");
      SPEED--;
      rotary_command_base[6] = SPEED + '0';
      tx(CMD_TOPIC, rotary_command_base);
    }
  }
  if (sum == 0b1110 || sum == 0b1000) {  // right
    if (SPEED < 9) {                     // max SPEED = 9
      // Serial.println("rotary change");
      SPEED++;
      rotary_command_base[6] = SPEED + '0';
      tx(CMD_TOPIC, rotary_command_base);
    }
  }
  LAST_ENCODED = encoded;
}

void keypad_check(void) {
  char key = KEYPAD.getKey();
  if (key != NO_KEY) {
    String data = "";
    switch (key) {
      case '0':
        data = "^~^";
        break;
      case '1':
        data = "ㅇ0ㅇ";
        break;
      case '2':
        data = "ㅠ_ㅜ";
        break;
      case '3':
        data = "ㅡ_ㅡ";
        break;
      case '4':
        data = "안녕?";
        break;
      case '5':
        data = "나 갈게..";
        break;
      case '6':
        data = "비켜";
        break;
      case '7':
        data = "치워줘..";
        break;
      case '8':
        data = "지나갈래..";
        break;
      case '9':
        data = "막지마..";
        break;
      case 'A':
        data = "먹을거..";
        break;
      case 'B':
        data = "고마워!";
        break;
      case 'C':
        data = "뒤에 비켜!";
        break;
      case 'D':
        data = "좋아~!";
        break;
      case 'E':
        data = "따라와라!";
        break;
      case 'F':
        data = "공부해!!";
        break;
    }
    char tx_data[20] = {};
    for (int i = 0; i < data.length(); i++) {
      tx_data[i] = data[i];
    }
    Serial.println(tx_data);
    tx(LCD_TOPIC, tx_data);
  }
}

// create thread
Thread rotary_th = Thread(),
       keypad_th = Thread();
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
  pinMode(ROTARY_ENCODER_SW, INPUT);
  pinMode(ROTARY_ENCODER_DATA, INPUT);
  pinMode(ROTARY_ENCODER_CLK, INPUT);

  // callback thread func
  rotary_th.onRun(rotary_check);
  rotary_th.setInterval(10);
  keypad_th.onRun(keypad_check);
  keypad_th.setInterval(10);

  controller.add(&rotary_th);
  controller.add(&keypad_th);

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