import utime

LastButtonsState = [ False, False, False ]
ButtonsState = [ False, False, False ]
ButtonsPressTS = [ None, None, None ]

btnPwrTS = None

def btnPwrCallback(param):
    global btnPwrTS
    print("------- button callback")
    if param.value() == 0 and btnPwrTS == None:
        btnPwrTS = utime.ticks_ms()
    elif param.value() == 1 and btnPwrTS != None:
        btnPwr_pd = utime.ticks_ms() - btnPwrTS
        btnPwrTS = None
        if btnPwr_pd > 10:
            if btnPwr_pd < 20:
                pass#btnPwr_ShortPress()
            

def ButtonsPeriodic(PWR_BTN, ADC_Pin):
    global btnPwrTS
    global LastButtonsState, ButtonsState, ButtonPressTS
    # PWR Button
    if PWR_BTN.value() == 0 and btnPwrTS == None:
        btnPwrTS = utime.ticks_ms()
    elif PWR_BTN.value() == 1 and btnPwrTS != None:
        btnPwr_pd = utime.ticks_diff(utime.ticks_ms(), btnPwrTS)
        btnPwrTS = None
        if btnPwr_pd > 30:
            return 'P'
    elif PWR_BTN.value() == 0 and btnPwrTS != None:
        btnPwr_pd = utime.ticks_diff(utime.ticks_ms(), btnPwrTS)
        if btnPwr_pd > 3000:
            btnPwrTS = None
            return 'Q'
    ButtonsState = ADCButtons_Read(ADC_Pin)
    if ButtonsState != LastButtonsState:
        LastButtonsState = ButtonsState
    return ''


def ADCButtons_Read(ADC_Pin):
    val = ADC_Pin.read_u16()
    print(val)
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
    