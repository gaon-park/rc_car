import requests

import smbus
from time import sleep
from MPU6050 import MPU6050

SENSOR_INTERVAL = 1 # sec

def read_val(val):
    if val['x'] >= 7 and -3 < val['y'] < 3:
        print('go')
    elif 3 <= val['x'] < 7 <= val['y']:
        print('left go')
    elif 3 <= val['x'] < 7 and val['y'] <= -7:
        print('right go')
    elif val['x'] <= -7 and -3 < val['y'] < 3:
        print('back')
    elif -3 >= val['x'] > -7 >= val['y']:
        print('right back')
    elif -3 >= val['x'] > -7 and val['y'] >= 7:
        print('left back')
    elif val['y'] >= 7 and -3 < val['x'] < 3:
        print('left')
    elif val['y'] <= -7 and -3 < val['x'] < 3:
        print('right')


if __name__ == '__main__':
    i2c = smbus.SMBus(1)
    sensor = MPU6050(i2c)
    sleep(0.1)

    while True:
        sleep(SENSOR_INTERVAL)

        accel = sensor.get_accel_data()
        sleep(0.1)
        val = {
            'x': round(accel['x'], 4),
            'y': round(accel['y'], 4),
            'z': round(accel['z'], 4)
        }

        read_val(val)
        print(val)


