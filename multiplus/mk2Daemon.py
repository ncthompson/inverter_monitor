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
import Queue
import logging
import argparse
from usbid.device import device_list
from mpStore import Mk2Store
from threading import Thread, Event
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class Mk2(Thread):
    """ Initialize the serial device and set device queue."""
    def __init__(self, deviceQueue, deviceName):
        logging.basicConfig(level=logging.INFO)
        Thread.__init__(self)
        self.ser = serial.Serial()
        self.ser.baudrate = 2400
        if deviceName != '':
            self.ser.port = deviceName
        else:
            self.ser.port = '/dev/'+self.getTtyDevice()
        try:
            self.ser.open()
            logging.info("Connected to serial device" + self.ser.port)
        except SerialException:
            logging.error("Device could not be configured: " + self.ser.port)
        self.serOpen = True
        self.deviceQueue = deviceQueue

    """ Function identifies the ttyUSB device that is associated with the FTDI device,
        that the Mk2 uses. This only looks for a single device, so if multiple devices 
        have the same ID, this will probably break something.""" 
    def getTtyDevice(self):
        vendorId = '0403'
        prodId = '6001'
        for dev in device_list():
           if dev.idVendor == vendorId and dev.idProduct == prodId:
            return dev.tty
    
    """ Transforms the command bytes into a valid frame to send to the Multiplus."""
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
    
    """ Send each byte in the built up frame."""
    def sendFrame(self,frame):
        for i in frame:
            self.ser.write(chr(i)) 
    
    """ Checks then checksum of the frame to determine if it is a valid frame. 
        If it is a valid frame, it will try to determine content of the frame
        for further decoding."""
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
            elif frame[6] == 0x08:#VE.Bus AC Info
                self.acDecode(frame[2:])  
            else:
                print frame
        
    """ Decodes the MK2 version frame that is sent automatically every 1 second or so.
        As I do not have the ICD for the Multiplus, I can only assume this is normal.
        I use the version to sync on a frame and then start a sequence to request
        DC, AC and LED status."""
    def versionDecode(self,frame):
        version = frame[0] + frame[1]*256 + frame[2]*256*256 + frame[3]*256*256*256
        mode = frame[4]
        device = self.deviceQueue.get()
        device.setVersion(version)
        self.deviceQueue.put(device)
    
        # Send the DC status request.
        send = self.frameCommand(['F', 0])
        self.sendFrame(send)
    
    """ Decodes the led status of the led panel."""
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
        logging.debug(device.printState())
        
        self.deviceQueue.put(device)
        
        # Close serial device and wait 10 seconds
        self.ser.close()
        self.serOpen = False
        time.sleep(10)
        
    """ Decode the DC frame information of theMultiplus."""
    def dcDecode(self,frame):
        batVoltage = round((frame[5] + frame[6]*256)/100.0, 2)
        usedCurrent = round((frame[7] + frame[8]*256 + frame[9]*256*256)/100.0, 2)
        chargingCurrent = round((frame[10] + frame[11]*256 + frame[12]*256*256)/100.0, 2)
        # As I don not have the documentation for the Multiplus/MK2 comms, I am not quite sure
        # what to do with the period. The answer I receive does not seem correct, but does seem
        # correct for the input frequency.
        inverterFreq = round(100000.0/frame[13], 1)
        
        # Retrieve device on queue and updates DC status.
        batCurrent = usedCurrent - chargingCurrent
        device = self.deviceQueue.get()
        device.setBatVoltage(batVoltage)
        device.setBatCurrent(batCurrent)
        device.setOutFreq(inverterFreq)
        self.deviceQueue.put(device)
    
        # Send the L1(ac status) status request.
        send = self.frameCommand(['F', 1])
        self.sendFrame(send)
    
    """ Decode the DC frame information of theMultiplus."""
    def acDecode(self,frame):
        # The elorn energy example shows this as the power factor, but I am not sure what
        # the conversion factor is, so I can not use it. My devices shows these two values as 1.
        #inFactor = frame[0])
        #outFactor =frame[1])
        inVoltage = round((frame[5] + frame[6]*256)/100.0, 1)
        inCurrent = round((frame[7] + frame[8]*256)/100.0, 2)
        outVoltage =  round((frame[9] + frame[10]*256)/100.0, 1)
        outCurrent = round((frame[11] + frame[12]*256)/100.0, 2)
        
        # When the AC power is lost, the  period is 0xFF as it loses lock a guess.
        if (frame[13] == 0xFF):
            inFreq = 0
        else:
            inFreq = round((10000.0/frame[13]), 1)
        
        # Retrieve device on queue and updates AC status.
        device = self.deviceQueue.get()
        device.setInVoltage(inVoltage)
        device.setInCurrent(inCurrent)
        device.setOutVoltage(outVoltage)
        device.setOutCurrent(outCurrent)
        device.setInFreq(inFreq)
        self.deviceQueue.put(device)
        
        # Send the LED status request.
        send = self.frameCommand(['L'])
        self.sendFrame(send)
    
    """ The Mk2 thread monitors the serial line for a possible frame."""
    def run(self):
        dat = ""
        while True:
            if self.serOpen == False:
                try:
                    self.ser.open()
                    self.serOpen = True
                    logging.debug("Reopen device.")
                except SerialException:
                    logging.error("Device could not be opened: " + self.ser.port)
            if dat != "":
                length = ord(dat)
            dat = self.ser.read()
            # All of the frames I receive is either 0xFF or 0x20.
            # It is possible the device has other frames that I am not aware of.
            if ord(dat) == 0xff or ord(dat) == 0x20:
                frame = [length, ord(dat)]
                for i in range(length):
                    temp = ord(self.ser.read())
                    frame.append(temp)
                self.deframe(frame)
                
            
""" Handles the HTTP requests."""
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
        # Retrieve device on queue and request current status.
        device = self.server.deviceQueue.get()
        try:
          self.wfile.write(device.getJson())
        finally:
          self.server.deviceQueue.put(device)

""" Allows for a multi threaded HTTP server. """
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--dev', help="The tty device of the Victron MK2. (Defaults to the first USB MK2)")
    args = parser.parse_args()


    device = Mk2Store()
    deviceQueue = Queue.Queue()
    deviceQueue.put(device)
    mainLoop = True

    if args.dev:
        mk2 = Mk2(deviceQueue, args.dev)
    else:
        mk2 = Mk2(deviceQueue, '')
    mk2.setDaemon(True)
    mk2.start()
    logging.info("Starting MK2 Daemon")

    serveraddr = ('', 9005)
    srvr = ThreadingHTTPServer(serveraddr, RequestHandler)
    srvr.deviceQueue = deviceQueue
    srvrDaemon = Thread(target=srvr.serve_forever)
    srvrDaemon.setDaemon(True)
    srvrDaemon.start()
    logging.info("Starting HTTP Daemon")

    # Catch the CTL-C to close the program gracefully.
    try:
        while mainLoop:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping MK2 and HTTP Daemon")
        mainLoop = False

    
