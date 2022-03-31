import utime
from math import fabs

class Servo():
    __Controller = None
    __Channel = None
    __usMin = None
    __usMax = None
    __degMin = None
    __degMax = None
    __period = None
    __stepus = None
    __stepdeg = None
    __rangeus = None
    __minduty = None
    __maxduty = None
    __ActDegree = None
    __TrgtDegree = None
    __movStepus = None
    __lastchangets = None
    
    def __init__(self, Controller, Channel, usMin = 1000, usMax = 2000, degMin = 0, degMax = 180):
        self.__usMin = usMin
        self.__usMax = usMax
        self.__degMin = degMin
        self.__degMax = degMax
        self.__Controller = Controller
        self.__period = 1 / self.__Controller.freq()
        self.__stepus = (self.__period / 4096) * 1000000
        self.__Channel = Channel
        self.__rangeus = self.__usMax - self.__usMin
        self.__stepdeg = (self.__degMax - self.__degMin) / (self.__rangeus / self.__stepus)
        self.__minduty = int(self.__usMin / self.__stepus)
        self.__maxduty = int(self.__usMax / self.__stepus)
        self.degMove(0)
    
    def degMove(self, TargetDegrees, Speed = None):
        if self.__ActDegree == None or Speed == None:
            # Faster move
            targetDuty = int(self.__minduty + ((TargetDegrees - self.__degMin) / self.__stepdeg))
            self.__Controller.duty(self.__Channel, targetDuty)
            self.__ActDegree = TargetDegrees
            self.__TrgtDegree = TargetDegrees
        else:
            # Speed controlled moving
            # - check limits
            if TargetDegrees < self.__degMin:
                self.__TrgtDegree = self.__degMin
            elif TargetDegrees > self.__degMax:
                self.__TrgtDegree = self.__degMax
            else:
                self.__TrgtDegree = TargetDegrees
            # calculate parameters
            Delta = TargetDegrees - self.__ActDegree
            self.__movStepus = (self.__stepdeg / Speed) * 1000000
            self.__ActDegree += self.__stepdeg 
            targetDuty = int(self.__minduty + ((self.__ActDegree - self.__degMin) / self.__stepdeg))
            self.__Controller.duty(self.__Channel, targetDuty)
            self.__lastchangets = utime.ticks_us()
        
    def periodic(self):
        if self.inPosition or self.__movStepus == None:
            return
        else:
            dus = utime.ticks_diff(utime.ticks_us(), self.__lastchangets)
            if dus < self.__movStepus:
                return
            else:
                num = int(dus / self.__movStepus)
                if self.__ActDegree < self.__TrgtDegree:
                    self.__ActDegree += ( self.__stepdeg * num)
                else:
                    self.__ActDegree -= ( self.__stepdeg * num)
                targetDuty = int(self.__minduty + ((self.__ActDegree - self.__degMin) / self.__stepdeg))
                self.__Controller.duty(self.__Channel, targetDuty)
                self.__lastchangets = utime.ticks_us()
        
    @property    
    def inPosition(self):
        return (fabs(self.__ActDegree - self.__TrgtDegree) < self.__stepdeg)
    
    @property
    def actualPosition(self):
        return self.__ActDegree
        