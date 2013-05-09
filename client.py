import datetime
import serial
import sys
from time import sleep


COM_PORT = int(sys.argv[1]) - 1
ser = serial.Serial(COM_PORT)

try:
    while True:
        ser.write("PING\n")
        print datetime.datetime.now()
        if ser.inWaiting() > 0:
            sys.stdout.write(ser.read(ser.inWaiting()))
        sleep(5)
except KeyboardInterrupt:
    ser.close()
