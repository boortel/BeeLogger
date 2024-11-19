import utime
import sys
import os
#import usb_serial
from machine import Pin, PWM

from SensorThread import SensorThread
from SensorThread import eventSensorThread_run
import _thread

led = Pin(25, Pin.OUT)
led.value(1)
PWM_IR = PWM(Pin(16))
PWM_Tyr = PWM(Pin(17))
PWM_W = PWM(Pin(20))
PWM_IR.freq (5000)
PWM_Tyr.freq (5000)
PWM_W.freq (5000)
ports_set = 0
#PWM_W.duty_u16(50000)
PWM_IR.duty_u16(50000)
PWM_Tyr.duty_u16(50000)


if __name__ == "__main__":  
    while True:
        PWM_W.duty_u16(25000)
        v = sys.stdin.readline().strip()
        if v == "start":
            if ports_set:
                sen.flush = 1
                led.value(0)
            else:
                sen = SensorThread(name = 'SensThread')
                
            if not eventSensorThread_run.locked():
                eventSensorThread_run.acquire()
            _thread.start_new_thread(sen.run, ())
        elif "Ports:" in v:
            v = v[6:]
            ports = v.split(";")
            try:
                sen = SensorThread(name = 'SensThread',port_HX711 = int(ports[0]), port_light = int(ports[1]))
            except:
                sen = SensorThread(name = 'SensThread')
            ports_set = 1
        elif v == "send data":
            sen.sendData = 1
        elif "ILLUminATion:" in v:
            v = v[13:]
            mess = v.split(";")
            color = mess[0]
            intensity = mess[1]
            #PWM_IR.duty_u16(0)
            #PWM_TYR.duty_u16(0)
            #PWM_W.duty_u16(0)
            if color == "IR":
                PWM_IR.duty_u12(intensity)
            elif color == "Tyr":
                PWM_Tyr.duty_u12(intensity)
            elif color == "W":
                PWM_W.duty_u12(intensity)
            print("PWM nastavene")
        elif v =="reset":
            try:
                eventSensorThread_run.release()
            except:
                pass
            print("ready")
        
