#!/usr/bin/env python3
#
# This is a NetworkTables server (eg, the robot or simulator side).
#
# On a real robot, you probably would create an instance of the
# wpilib.SmartDashboard object and use that instead -- but it's really
# just a passthru to the underlying NetworkTable object.
#
# When running, this will continue incrementing the value 'robotTime',
# and the value should be visible to networktables clients such as
# SmartDashboard. To view using the SmartDashboard, you can launch it
# like so:
#
#     SmartDashboard.jar ip 127.0.0.1
#

import time
import random
import string
from networktables import NetworkTables

# To see messages from networktables, you must setup logging
import logging

logging.basicConfig(level=logging.DEBUG)

sd = NetworkTables.getTable("SmartDashboard")

t = 1

line = []
for i in range(0, 30):
    line.append(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4)))
print(line)
while True:
    try:
        print('dsTime:', sd.getNumber('dsTime'))
    except KeyError:
        print('dsTime: N/A')


    sd.putNumber('time', t)
    sd.putNumber('encoder', random.randint(0, 10))
    sd.putNumber('centerX', random.randint(0, 100))
    sd.putNumber('vision', random.randint(0, 1000))
    sd.putNumber('num1', random.randint(0, 10))
    sd.putNumber('num2', random.randint(0, 100))
    sd.putNumber('batman', random.randint(0, 1000))
    sd.putNumber('robin', random.randint(0, 10))
    sd.putNumber('DT_FLTalon', random.randint(0, 100))
    sd.putNumber('DT_FRTalon', random.randint(0, 1000))
    for i in line:
        sd.putNumber(i, random.randint(0,200))

    time.sleep(0.25)
    t += 0.25
