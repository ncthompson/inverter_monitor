#!/usr/bin/python

'''
Copyright (c) 2015, NC Thompson
All rights reserved.
Redistribution and use in source and binary forms, with or without modification,
 are permitted provided that the following conditions are met:

1) Redistributions of source code must retain the above copyright notice,
    this list of conditions and the following disclaimer.

2) Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation 
    and/or other materials provided with the distribution.

3) Neither the name of the ORGANIZATION nor the names of its contributors may 
    be used to endorse or promote products derived from this software without 
    specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY 
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES 
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT 
SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import serial
import time
import sys
import signal
from usbid.device import device_list
from mpStore import Mk2Store
from threading import Thread, Lock, Event

class Mk2:
    def __init__(self, stop_event):
        self.device = Mk2Store()
        self.ser = serial.Serial()
        self.ser.baudrate = 2400
        self.ser.port = '/dev/'+self.getTtyDevice()
        self.ser.open()
        self.serOpen = True
        self.stop_event = stop_event
        
        self.lock = Lock()
        #self.mk2Run = True

    #def stopDaemon(self):
    #    self.mk2Run = False

    def printLed(self, binStr):
        names = ["temperature", "low_battery", "overload", "inverter", "float", "bulk", "absorption", "mains"]
        for i in range(len(binStr)):
            if binStr[i] == '1':
                print names[i]
    
    def getTtyDevice(self):
        vendorId = '0403'
        prodId = '6001'
        for dev in device_list():
           if dev.idVendor == vendorId and dev.idProduct == prodId:
            return dev.tty
    
    def frameCommand(self,command):
        frame = []
        length = len(command) + 1
        frame.append(length)
        frame.append(0xFF)
        for entry in command:
            if type(entry) == str:
                frame.append(ord(entry))
            else:
                frame.append(entry)
        cs = 0
        for entry in frame:
            cs = (cs - entry)%256
        frame.append(cs)
        return frame
    
    def sendFrame(self,frame):
        for i in frame:
            self.ser.write(chr(i)) 
    
    def deframe(self,frame):
        cr = 0
        length = frame[0]
        for i in range(len(frame)):
            cr = (cr + frame[i]) %256
        if cr != 0:
            return "Checksum failed"
        if frame[1] == 0xFF:      #MK2 frame
    
            if frame[2] == ord('V'):        #MK Version
                self.versionDecode(frame[3:])
            elif frame[2] == ord('L'):      #LED status
                self.ledDecode(frame[3:])
        elif frame[1] == 0x20:    #VE.Bus info
            if frame[6] == 0x0C:  #VE.Bus DC Info
                self.dcDecode(frame[2:])  
            elif frame[6] == 0x08:
                self.acDecode(frame[2:])  
            else:
                print frame
        
    def versionDecode(self,frame):
        version = frame[0] + frame[1]*256 + frame[2]*256*256 + frame[3]*256*256*256
        mode = frame[4]
        print "Version: ",version
        print "Mode: " , chr(mode)
    
        # DC Value
        send = self.frameCommand(['F', 0])
        self.sendFrame(send)
    
    def ledDecode(self,frame):
        on = '{0:08b}'.format(frame[0])
        blink = '{0:08b}'.format(frame[1])
        #print "LEDs On: "
        #self.printLed(on)
        #print "LEDs Blink: "
        #self.printLed(blink)

        self.device.printState()
        self.ser.close()
        self.serOpen = False
        self.mk2Run = False
        self.stop_event.wait(10)
        #time.sleep(10)
        print "\n-----------------------------------------------------------------------------"
        
    def dcDecode(self,frame):
        batVoltage = round((frame[5] + frame[6]*256)/100.0, 2)
        usedCurrent = round((frame[7] + frame[8]*256 + frame[9]*256*256)/100.0, 2)
        chargingCurrent = round((frame[10] + frame[11]*256 + frame[12]*256*256)/100.0, 2)
        inverterFreq = round(100000.0/frame[13], 1)
        
        batCurrent = usedCurrent - chargingCurrent
        self.lock.acquire()
        self.device.setBatVoltage(batVoltage)
        self.device.setBatCurrent(batCurrent)
        self.device.setOutFreq(inverterFreq)
        self.lock.release()
    
        # L1
        send = self.frameCommand(['F', 1])
        self.sendFrame(send)
    
    def acDecode(self,frame):
        #print "BF Factor: ", (frame[0])/128.0-1
        #print "Inv Factor: ", (frame[1])/128.0-1
        inVoltage = round((frame[5] + frame[6]*256)/100.0, 1)
        inCurrent = round((frame[7] + frame[8]*256)/100.0, 2)
        outVoltage =  round((frame[9] + frame[10]*256)/100.0, 1)
        outCurrent = round((frame[11] + frame[12]*256)/100.0, 2)
        inFreq = round((10000.0/frame[13]), 1)
        
        self.lock.acquire()
        self.device.setInVoltage(inVoltage)
        self.device.setInCurrent(inCurrent)
        self.device.setOutVoltage(outVoltage)
        self.device.setOutCurrent(outCurrent)
        self.device.setInFreq(inFreq)
        self.lock.release()
        # LED
        send = self.frameCommand(['L'])
        self.sendFrame(send)
    
    
    def servMulti(self):
        dat = ""
        while not self.stop_event.is_set():
            if self.serOpen == False:
                self.ser.open()
                self.serOpen = True
            if dat != "":
                length = ord(dat)
            dat = self.ser.read()
            if ord(dat) == 0xff or ord(dat) == 0x20:
                frame = [length, ord(dat)]
                for i in range(length):
                    temp = ord(self.ser.read())
                    frame.append(temp)
                #print frame
                self.deframe(frame)
    
    #def run(self):
    
if __name__ == "__main__":
    mk2Stop = Event()
    mk2 = Mk2(mk2Stop)
    try:
        print "1"
        usbDaemon = Thread(target = mk2.servMulti)
        print "2"
        #usbDaemon.start()
        print "3"
        #usbDaemon.join()
        print "4"
    except KeyboardInterrupt:
        print "Stopping Daemon"
        mk2Stop.set()
    #mk.servMulti()
    
