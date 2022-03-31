import utime

LastButtonsState = [ False, False, False ]
ButtonsState = [ False, False, False ]
ButtonsPressTS = [ None, None, None ]

btnPwrTS = None

def btnPwrCallback(param):
    global btnPwrTS
    if param.value() == 0 and btnPwrTS == None:
        btnPwrTS = utime.ticks_ms()
    elif param.value() == 1 and btnPwrTS != None:
        btnPwr_pd = utime.ticks_ms() - btnPwrTS
        btnPwrTS = None
        if btnPwr_pd > 10:
            if btnPwr_pd < 20:
                pass#btnPwr_ShortPress()
            

def ButtonsPeriodic(ADC_Pin):
    if btnPwrTS != None:
        if (utime.ticks_ms() - btnPwrTS) > 3000:
            return 'Q'
    return ''


def ADCButtons_Read(ADC_Pin):
    val = ADC_Pin.read_u16()
    if val < 8500:
        return [ False, False, False ]
    elif val < 9500:
        return [ True, False, False ]
    elif val < 11500:
        return [ False, True, False ]
    elif val < 15000:
        return [ True, True, False ]
    elif val < 20000:
        return [ False, False, True ]
    elif val < 26000:
        return [ True, False, True ]
    elif val < 60000:
        return [ False, True, True ]
    else:
        return [ True, True, True ]
    