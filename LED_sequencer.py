from Sequencers_DC import LED_sequencer_step
from LED_sequencer_data import *

import utime

    
class LED_sequencer:
    __WS2812 = None
    __Sequences = None
    __CurrentSequence = None
    __RequestedSequence = None
    __CurrentSequenceStepID = None
    __CurrentSequenceStepData = None
    __StepStartTime = None
    
    def __init__(self, WS2812B, Sequences):
        self.__WS2812 = WS2812B
        self.__Sequences = Sequences
    
    @property
    def Sequencies(self):
        if self.__Sequences == None:
            return 0
        else:
            return len(self.__Sequences)
    
    def StartSequence(self, Sequence, Immediatelly):
        if Immediatelly or self.__Sequences[self.__CurrentSequence].Duration == 0:
            self.__CurrentSequenceStepID = 0
            self.__CurrentSequence = Sequence
            self.__RequestedSequence = None
            self.__StepStartTime = utime.ticks_ms()
            self.__LoadStep()
            self.__UpdateLED()
        else:
            self.__RequstedSequence = Sequence
    
    def Periodic(self):
        if not self.__CurrentSequenceStepData.IsExpired(self.__StepStartTime):
            return
        self.__CurrentSequenceStepID += 1
        if self.__CurrentSequenceStepID >= self.__StepsInSequence :
            if self.__RequestedSequence != None:
                self.StartSequence(self.__RequestedSequence, True)
            else:
                self.__CurrentSequenceStepID = 0
        self.__LoadStep()
        self.__UpdateLED()        
        
        
    def __UpdateLED(self):
        for LC in self.__CurrentSequenceStepData.LED_Colors:
            (LEDid, red, green, blue) = LC
            self.__WS2812[LEDid] = (red, green, blue)
        self.__StepStartTime = utime.ticks_ms()
        self.__WS2812.write()
        
    
    def __LoadStep(self):
        if isinstance(self.__Sequences[self.__CurrentSequence], tuple) :
            self.__CurrentSequenceStepData = self.__Sequences[self.__CurrentSequence][self.__CurrentSequenceStepID]
        else:
            self.__CurrentSequenceStepData = self.__Sequences[self.__CurrentSequence]
    
    @property
    def __StepsInSequence(self):
        if isinstance(self.__Sequences[self.__CurrentSequence], tuple) :
            return len(self.__Sequences[self.__CurrentSequence])
        else:
            return 1
        