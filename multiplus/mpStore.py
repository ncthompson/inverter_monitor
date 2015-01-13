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
import json

class Mk2Store:
    
    def __init__(self):
        self.version = 0

        self.batVoltage = 0
        self.batCurrent = 0
        
        self.inVoltage = 0
        self.inCurrent = 0
        self.inFreq = 0 

        self.outVoltage = 0
        self.outCurrent = 0
        self.outFreq = 0

        # Save LED state
        # 0 off - 1 on - 2 blink
        self.ledNames = ["temperature", "low_battery", "overload", "inverter", "float", "bulk", "absorption", "mains"]
        self.leds = [0,0,0,0,0,0,0,0]

    def setVersion(self, version):
        self.version = version

    def setBatVoltage(self, voltage):
        self.batVoltage = voltage

    def setBatCurrent(self, current):
        self.batCurrent = current 

    def setInVoltage(self, voltage):
        self.inVoltage = voltage

    def setInCurrent(self, current):
        self.inCurrent = current 

    def setInFreq(self, freq):
        self.inFreq = freq

    def setOutVoltage(self, voltage):
        self.outVoltage = voltage

    def setOutCurrent(self, current):
        self.outCurrent = current 

    def setOutFreq(self, freq):
        self.outFreq = freq
    
    def setTempState(self, state):
        self.temperature_state = state

    def setPowerOutState(self, state):
        self.power_out_state = state

    def setPowerInState(self, state):
        self.power_in_state = state

    def setBatteryState(self, state):
        self.battery_state = state
   
    def setLeds(self, leds):
        self.leds = leds

    def printLed(self):
        print "LEDs On:",
        for i in range(len(self.leds)):
            if self.leds[i] == 1:
                print self.ledNames[i],
        print
        print "LEDs Blink:",
        for i in range(len(self.leds)):
            if self.leds[i] == 2:
                print self.ledNames[i],
        print
    
    def printState(self):
        print "========================================"
        print "                Multiplus"
        print "========================================"
        print "Battery Voltage: ", self.batVoltage
        print "Battery Current: ", self.batCurrent

        print
        print "In Voltage: ", self.inVoltage
        print "In Current: ",  self.inCurrent
        print "In Frequency: ", self.inFreq

        print
        print "Out Voltage: ", self.outVoltage
        print "Out Current: ", self.outCurrent
        print "Out Frequency: ", self.outFreq
        self.printLed()
        print
        print "Version: ", self.version
        print "========================================"
        print
    
    def getJson(self):
        data = [{'batVoltage':self.batVoltage, 'batCurrent':self.batCurrent, 
                'inVoltage':self.inVoltage, 'inCurrent':self.inCurrent,
                'inFreq':self.inFreq, 'outVoltage':self.outVoltage,
                'outCurrent':self.outCurrent, 'outFreq':self.outFreq,
                'leds':self.leds}]

        jsonString = json.dumps(data)
        return jsonString
