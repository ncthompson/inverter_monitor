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
from threading import Thread, Event
import Queue
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class Mk2(Thread):
    def __init__(self, deviceQueue):
        Thread.__init__(self)
        self.ser = serial.Serial()
        self.ser.baudrate = 2400
        self.ser.port = '/dev/'+self.getTtyDevice()
        self.ser.open()
        self.serOpen = True
        self.deviceQueue = deviceQueue
 
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
        device = self.deviceQueue.get()
        device.setVersion(version)
        self.deviceQueue.put(device)
    
        # DC Value
        send = self.frameCommand(['F', 0])
        self.sendFrame(send)
    
    def ledDecode(self,frame):
        on = '{0:08b}'.format(frame[0])
        blink = '{0:08b}'.format(frame[1])
        leds = [0,0,0,0,0,0,0,0]
        for i in range(8):
            if on[i] == '1':
                leds[i] = 1
            elif blink[i] == '1':
                leds[i] = 2

        device = self.deviceQueue.get()
        device.setLeds(leds)
        device.printState()
        self.deviceQueue.put(device)
        self.ser.close()
        self.serOpen = False
        time.sleep(10)
        
    def dcDecode(self,frame):
        batVoltage = round((frame[5] + frame[6]*256)/100.0, 2)
        usedCurrent = round((frame[7] + frame[8]*256 + frame[9]*256*256)/100.0, 2)
        chargingCurrent = round((frame[10] + frame[11]*256 + frame[12]*256*256)/100.0, 2)
        # As I don not have the documentation for the Multiplus/MK2 comms, I am not quite sure
        # what to do with the period. The answer I receive does not seem correct, but does seem
        # correct for the input frequency.
        inverterFreq = round(100000.0/frame[13], 1)
        
        batCurrent = usedCurrent - chargingCurrent
        device = self.deviceQueue.get()
        device.setBatVoltage(batVoltage)
        device.setBatCurrent(batCurrent)
        device.setOutFreq(inverterFreq)
        self.deviceQueue.put(device)
    
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
        if (frame[13] == 0xFF):
            inFreq = 0
        else:
            inFreq = round((10000.0/frame[13]), 1)
        
        device = self.deviceQueue.get()
        device.setInVoltage(inVoltage)
        device.setInCurrent(inCurrent)
        device.setOutVoltage(outVoltage)
        device.setOutCurrent(outCurrent)
        device.setInFreq(inFreq)
        self.deviceQueue.put(device)
        # LED
        send = self.frameCommand(['L'])
        self.sendFrame(send)
    
    
    def run(self):
        dat = ""
        while True:
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

class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        self.deviceQueue = server.deviceQueue
    
    def _writeheaders(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._writeheaders()

    def do_GET(self):
        self._writeheaders()
        device = self.server.deviceQueue.get()
        self.wfile.write(device.getJson())
        self.server.deviceQueue.put(device)
    
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == "__main__":
    device = Mk2Store()
    deviceQueue = Queue.Queue()
    deviceQueue.put(device)
    mainLoop = True

    mk2 = Mk2(deviceQueue)
    mk2.setDaemon(True)
    mk2.start()

    serveraddr = ('', 9005)
    srvr = ThreadingHTTPServer(serveraddr, RequestHandler)
    srvr.deviceQueue = deviceQueue
    srvrDaemon = Thread(target=srvr.serve_forever)
    srvrDaemon.setDaemon(True)
    srvrDaemon.start()


    try:
        while mainLoop:
            time.sleep(1)
    except KeyboardInterrupt:
        print "\nStopping Daemon\n"
        mainLoop = False

    
