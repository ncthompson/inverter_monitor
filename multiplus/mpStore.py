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
        self.temperature_state = 0
        self.power_out_state = 0
        self.power_in_state = 0
        self.battery_state = 0

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
    
    def printState(self):
        print "Battery Voltage: ", self.batVoltage
        print "Battery Current: ", self.batCurrent

        print "In Voltage: ", self.inVoltage
        print "In Current: ",  self.inCurrent
        print "In Frequency: ", self.inFreq

        print "Out Voltage: ", self.outVoltage
        print "Out Current: ", self.outCurrent
        print "Out Frequency: ", self.outFreq
