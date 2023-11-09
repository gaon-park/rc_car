from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor
from Raspi_PWM_Servo_Driver import PWM
import mysql.connector
from threading import Timer
from time import sleep
import signal
import sys

speed = 200

def closeDB(signal, frame):
    print("BYE")
    mh.getMotor(2).run(Raspi_MotorHAT.RELEASE)
    cur.close()
    db.close()
    timer.cancel()
    sys.exit(0)

def polling():
    global cur, db, ready

    cur.execute("select * from command where is_finish = 0 order by time desc")
    ids = []
    for (id, time, cmd_string, arg_string, is_finish) in cur:
        if is_finish == 1 : break
        ready = (cmd_string, arg_string)
        ids.append(str(id))

    if len(ids) > 0:
        cur.execute("update command set is_finish = 1 where id in (" + ', '.join(ids) + ")")

    db.commit()

    global timer
    timer = Timer(0.1, polling)
    timer.start()

def go():
    myMotor.setSpeed(speed)
    myMotor.run(Raspi_MotorHAT.BACKWARD)

def back():
    myMotor.setSpeed(speed)
    myMotor.run(Raspi_MotorHAT.FORWARD)

def stop():
    myMotor.setSpeed(speed)
    myMotor.run(Raspi_MotorHAT.RELEASE)

def left():
    pwm.setPWM(0, 0, 250)

def mid():
    pwm.setPWM(0, 0, 375)

def right():
    pwm.setPWM(0, 0, 450)

#init
db = mysql.connector.connect(host='52.78.74.11', user='ondol', password='1234', database='rc_car', auth_plugin='mysql_native_password')
cur = db.cursor()
ready = None
timer = None

mh = Raspi_MotorHAT(addr=0x6f)
myMotor = mh.getMotor(2)
pwm = PWM(0x6F)
pwm.setPWMFreq(60)

signal.signal(signal.SIGINT, closeDB)
polling()

#main thread
while True:
    sleep(0.1)
    if ready == None:
        continue

    cmd, arg = ready
    ready = None

    if cmd == "GO":
        go()
    if cmd == "BACK":
        back()
    if cmd == "STOP":
        stop()
    if cmd == "LEFT":
        left()
    if cmd == "MID":
        mid()
    if cmd == "RIGHT":
        right()
