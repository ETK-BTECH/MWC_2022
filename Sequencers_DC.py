import utime

class LED_sequencer_step:
    __LED_Colors = None
    __duration = None
    
    def __init__(self, LED_Colors, Duration):
        self.__LED_Colors = LED_Colors
        self.__duration = Duration
        
    @property
    def LED_Colors(self):
        return self.__LED_Colors
    
    @property
    def Duration(self):
        return self.__duration
    
    def IsExpired(self, StartTime):
        if StartTime == None:
            return True
        if self.__duration == 0:
            return False
        else:
            return utime.ticks_diff(utime.ticks_ms(), StartTime) >= self.__duration