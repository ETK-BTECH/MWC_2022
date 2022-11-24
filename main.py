from machine import Pin, I2C, ADC, Timer, PWM, reset, freq
from SH1106 import SH1106_I2C
from PCA9685 import PCA9685
from Servo import Servo
from ESP_AT import ESP_AT
import neopixel
from LED_sequencer import *
from LED_sequencer_data import LED_sequencies
import Font
from settings import *
from Buttons import *
import gc
import utime
import sys, os
import framebuf
from Screens import *
import _thread

####################################################################################################
# CONSTANTS                                                                                        #
####################################################################################################


####################################################################################################
# GLOBAL VARIABLES                                                                                 #
####################################################################################################
ADC_LSB = VREF / 65535
StartTime = utime.ticks_us()            # Start timestamp [us]
InitializedTS = None                    # Initialization finished timestamp [ms]

BatteryVoltage = None
Temperature = None
DCDCVoltage = None

ScanStartTS = None                      # Scan (while loop) start time stamp
ScanActual = None                       # Scan actual time
ScanAverage = None                      # Scan average time
ScanMinimal = None                      # Scan minimal time
ScanMaximal = None                      # Scan maximal time
ScanNumber = None                       # Scan counter

ButtonState = [ False, False, False ]   # Buttons actual state ( EXE, UP, DOWN)
ButtonLState = ButtonState

DisplayedScreen = None
RequestedScreen = None
LastScreenUpdate = None

btnCode = 0

SecondCoreLock = _thread.allocate_lock();
IIC_Lock = _thread.allocate_lock();

freq(100000000)
print("============== INITIALIZING ==============")
print("--> initializing pins             ... ",end = "")
####################################################################################################
# PIN DEFINITIONS                                                                                  #
####################################################################################################
I_LED     = Pin(25, Pin.OUT)            # Pico onboard LED
ESP_TX    = Pin(0)                      # ESP-07 (WiFi)
ESP_RX    = Pin(1)                      # ESP-07 (WiFi)
ESP_EN    = Pin(2, Pin.OUT)             # ESP-07 (WiFi)
NEO       = Pin(3)                      # Neopixel (WS2812B) LED
AUX_SDATX = Pin(4)                      # Auxiliary communication
AUX_SCLRX = Pin(5)                      # Auxiliary communication
I2C_SDA   = Pin(6)                      # I2C
I2C_SCL   = Pin(7)                      # I2C
PWR_ON    = Pin(8, Pin.OUT, value=0)    # Power switch control pin
PWR_BTN   = Pin(9, Pin.IN, Pin.PULL_UP) # Power button
M4_PWM    = Pin(10)                     # M4 speed control pin
M4_IN2    = Pin(11, Pin.OUT, value=0)   # M4 direction control 2
M4_IN1    = Pin(12, Pin.OUT, value=0)   # M4 direction control 1
M3_IN1    = Pin(13, Pin.OUT, value=0)   # M3 direction control 1
M3_IN2    = Pin(14, Pin.OUT, value=0)   # M3 direction control 2
M3_PWM    = Pin(15)                     # M3 speed control pin
M2_PWM    = Pin(16)                     # M2 speed control pin
M2_IN2    = Pin(17, Pin.OUT, value=0)   # M2 direction control 2
M2_IN1    = Pin(18, Pin.OUT, value=0)   # M2 direction control 1
M_STBY    = Pin(19, Pin.OUT, value=0)   # Motor drivers stand-by
M1_IN1    = Pin(20, Pin.OUT, value=0)   # M1 direction control 1
M1_IN2    = Pin(21, Pin.OUT, value=0)   # M1 direction control 2
M1_PWM    = Pin(22)                     # M1 speed control pin
PWR_EXT   = Pin(24)                     # External (USB) powered

#PWR_BTN.irq(trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING, handler = btnPwrCallback)
print("done")
####################################################################################################
# ADC DEFINITIONS                                                                                  #
####################################################################################################
VBAT_ADC  = ADC(26)                      # Battery voltage ADC (GP26)
BTN_ADC   = ADC(27)                      # Button ADC (GP27)
V5_ADC    = ADC(28)
TEMP_ADC  = ADC(4)                       # On-board temperature sensor

LED_PWM = PWM(I_LED)
LED_PWM.freq(2000)



####################################################################################################
# BLINK TIMER INITIALIZATION                                                                       #
####################################################################################################
CLK_1Hz = False
CLK_CNT = 0
def CLK_10Hz_Tick(timer):
    global CLK_1Hz, CLK_CNT, LED_PWM
    gc.collect()
    CLK_CNT += 1
    if CLK_CNT == 5:
        CLK_1Hz = True
    if CLK_CNT == 10:
        CLK_1Hz = False
        CLK_CNT = 0
        #gc.collect()
    if PWR_ON.value() == 1:
        if CLK_CNT == 0 or CLK_CNT == 3 :
            LED_PWM.duty_u16(65052)
        if CLK_CNT == 1 or CLK_CNT == 4:
            LED_PWM.duty_u16(0)
        
CLK_1Hz_Timer = Timer(period=100, mode=Timer.PERIODIC, callback=CLK_10Hz_Tick)


####################################################################################################
# BUSES INITIALIZATION                                                                             #
####################################################################################################
print("--> initializing internal I2C     ... ",end = "")
int_i2c = I2C(1, scl=I2C_SCL, sda=I2C_SDA, freq=500000)
print("done")
print("      - {}".format(int_i2c))
print("      - I2C scanning              ... ",end = "")
int_i2c_dev = int_i2c.scan()

print("done")
print(int_i2c_dev)

####################################################################################################
# DISPLAY INITIALIZATION                                                                           #
####################################################################################################
print("--> initializing display          ... ",end = "")
disp = None
fnt = Font.Font5x7()
if 0x3C in int_i2c_dev:
    disp = SH1106_I2C(128, 64, int_i2c, rotate=180)      # oled controller
    disp.fill(0)
    disp.contrast(30)
    fnt.PrintString(disp, SystemName, int((128 - (len(SystemName) * 12)) / 2), 0, 2, 1)
    disp.hline(0,18,128, 1)
    disp.show()
    print("done")
else:
    print("fail")
    print("    !!! NOT FOUND ON BUS !!!")

def DisplayUpdateThread():
    SecondCoreLock.acquire()
    global disp, fnt, DisplayedScreen, RequestedScreen
    StrtTick = utime.ticks_us()
    """  """
    #print("Display refresh ...", end = " ")
    if RequestedScreen != None: 
        if DisplayedScreen != RequestedScreen:
            disp.fill(0)
            if RequestedScreen == 1:
                PaintScreen_1(disp, fnt)
                UpdateScreen_1(disp, fnt, BatteryVoltage, DCDCVoltage, Temperature, ScanAverage / 1000)
            DisplayedScreen = RequestedScreen
            IIC_Lock.acquire()
            disp.show()
            IIC_Lock.release()
        elif DisplayedScreen == RequestedScreen:
            if DisplayedScreen == 1:
                UpdateScreen_1(disp, fnt, BatteryVoltage, DCDCVoltage, Temperature, ScanAverage / 1000)
            IIC_Lock.acquire()
            disp.show()
            IIC_Lock.release()
    #print("done in {0:d} us".format(utime.ticks_diff(utime.ticks_us(), StrtTick)))
    SecondCoreLock.release()


####################################################################################################
# CHECK START REASON                                                                               #
####################################################################################################
if PWR_EXT.value() == 1 and PWR_BTN.value() == 1:
    # charging
    print()
    print("--> battery charging mode         ... ",end = "")
    LED_PWM_duty = 0
    LED_PWM.duty_u16(LED_PWM_duty)
    LED_PWM_inc = True
    if disp != None:
        with open('/Icons/sleep.pbm', 'rb') as f:
            f.readline() # Magic number
            f.readline() # Creator comment
            f.readline() # Dimensions
            data = bytearray(f.read())
            fbuf = framebuf.FrameBuffer(data, 59, 40, framebuf.MONO_HLSB)
        disp.blit(fbuf, 2, 22)
        with open('/Icons/BattCh0.pbm', 'rb') as f:
            f.readline() # Magic number
            f.readline() # Creator comment
            f.readline() # Dimensions
            data = bytearray(f.read())
            fbufB0 = framebuf.FrameBuffer(data, 24, 24, framebuf.MONO_HLSB)
        disp.blit(fbuf, 2, 22)
        disp.blit(fbufB0, 85, 22)
        fnt.PrintString(disp, "0.00", 70, 50, 2, 1)
        fnt.PrintString(disp, "V", 121, 50, 1, 1)
        disp.show()
        
        with open('/Icons/BattCh33.pbm', 'rb') as f:
            f.readline() # Magic number
            f.readline() # Creator comment
            f.readline() # Dimensions
            data = bytearray(f.read())
            fbufB33 = framebuf.FrameBuffer(data, 24, 24, framebuf.MONO_HLSB)
        with open('/Icons/BattCh66.pbm', 'rb') as f:
            f.readline() # Magic number
            f.readline() # Creator comment
            f.readline() # Dimensions
            data = bytearray(f.read())
            fbufB66 = framebuf.FrameBuffer(data, 24, 24, framebuf.MONO_HLSB)
        with open('/Icons/BattCh100.pbm', 'rb') as f:
            f.readline() # Magic number
            f.readline() # Creator comment
            f.readline() # Dimensions
            data = bytearray(f.read())
            fbufB100 = framebuf.FrameBuffer(data, 24, 24, framebuf.MONO_HLSB)
        
    BICnt = 0
    BILCTS = utime.ticks_ms()
    while PWR_BTN.value() == 1:
        if LED_PWM_inc:
            LED_PWM_duty += 1000
        else:
            LED_PWM_duty -= 1000
        if LED_PWM_duty >= 64000:
            LED_PWM_inc = False
        if LED_PWM_duty <= 3000:
            LED_PWM_inc = True
        LED_PWM.duty_u16(LED_PWM_duty)
        if utime.ticks_diff(utime.ticks_ms(), BILCTS) > 400:
            BICnt += 1
            if BICnt == 4:
                BICnt = 0
            disp.fill_rect(70, 22, 50, 42, 0)
            if BICnt == 0:
                disp.blit(fbufB0, 85, 22)
            elif BICnt == 1:
                disp.blit(fbufB33, 85, 22)
            elif BICnt == 2:
                disp.blit(fbufB66, 85, 22)
            elif BICnt == 3:
                disp.blit(fbufB100, 85, 22)
            BatteryVoltage = VBAT_ADC.read_u16() * ADC_LSB * 2 * VBAT_CAL
            fnt.PrintString(disp, "{:0.2f}".format(BatteryVoltage), 70, 50, 2, 1)
            disp.show()
            BILCTS = utime.ticks_ms()
        utime.sleep(0.03)
    print("exit")
    freq(200000000)
    fbufB0 = None
    fbufB33 = None
    fbuf66 = None
    fbuf100 = None 
    print()
    disp.fill_rect(0, 22, 128, 44, 0)

gc.enable()
PWR_ON.on()
gc.threshold(6000)    
####################################################################################################
# NEOPIXEL LED INITIALIZATION                                                                      #
####################################################################################################
print("--> initializing NeoPixel LEDs    ... ",end = "")
NeoLED = None
NeoLED = neopixel.NeoPixel(NEO, 8)
for i in range(NeoLED.n):
    NeoLED[i] = (0, 0, 0)
NeoLED.write()
"""NeoLED.set_pixel(ldFL, 80, 0, 0)
NeoLED.set_pixel(ldFR, 0, 80, 0)
NeoLED.set_pixel(ldRL, 40, 40, 40)
NeoLED.set_pixel(ldRR, 40, 40, 40)
NeoLED.show(True)"""
print("done")
NeoSequencer = LED_sequencer( NeoLED, LED_sequencies)
NeoSequencer.StartSequence( 0, True)


####################################################################################################
# SERVO DRIVER (PCA9686) INITIALIZATION                                                            #
####################################################################################################
print("--> initializing servodriver      ... ",end = "")
ServoDrv = None
if (0x40 in int_i2c_dev):
    ServoDrv = PCA9685(int_i2c)
    ServoDrv.freq(50)
    print("done")
else: 
    print("fail")
    print("    !!! NOT FOUND ON BUS !!!")
    
####################################################################################################
# SERVOS INITIALIZATION                                                                            #
####################################################################################################    
Servos = []
if ServoDrv != None:
    Servos.append( Servo(ServoDrv, 0,
                         usMin = PanS_usMin,
                         usMax = PanS_usMax,
                         degMin = PanS_degMin,
                         degMax = PanS_degMax) )
    PanServo = Servos[0]
    Servos.append( Servo(ServoDrv, 1,
                         usMin = TiltS_usMin,
                         usMax = TiltS_usMax,
                         degMin = TiltS_degMin,
                         degMax = TiltS_degMax) )
    TiltServo = Servos[1]

####################################################################################################
# WIFI INITIALIZATION                                                                              #
####################################################################################################
esp = None
if disp != None and DisplayedScreen == None:
    #disp.text("WIFI INITIALIZING", 0, 20, 1)
    fnt.PrintString(disp, "[    ]", 0, 22, 1, 1)
    fnt.PrintString(disp, "SETTING WIFI", 40, 22, 1, 1)
    fnt.PrintString(disp, "CHECKING AP", 40, 32, 1, 1)
    fnt.PrintString(disp, "STA CONNECT", 40, 42, 1, 1)
    fnt.PrintString(disp, "AP ACTIVATE", 40, 52, 1, 1)
    disp.show()
### CALLBACKS ######################################################################################
  # State change callback
def WiFi_StateChange(Connection, NewState):
    global esp, ReadyForConnect, Disconnected_ts, RequestedScreen, LastScreenUpdate
    if esp != None:
        if Connection == None:
            if NewState == esp.ESP_Initialized:
                if disp != None and DisplayedScreen == None:
                    fnt.PrintString(disp, "[ OK ]", 0, 22, 1, 1)
                    fnt.PrintString(disp, "[    ]", 0, 32, 1, 1)
                    disp.show()
                esp.STA_Connect()
            elif NewState == esp.ESP_STA_Connecting:
                if disp != None and DisplayedScreen == None:
                    fnt.PrintString(disp, "[ OK ]", 0, 32, 1, 1)
                    fnt.PrintString(disp, "[    ]", 0, 42, 1, 1)
                    disp.show()
            elif NewState == esp.ESP_STA_ConnectingDone:
                if disp != None and DisplayedScreen == None:
                    fnt.PrintString(disp, "[ OK ]", 0, 42, 1, 1)
                    fnt.PrintString(disp, "[    ]", 0, 52, 1, 1)
                    disp.show()
                esp.StartServer(SystemPort)
            elif NewState == esp.ESP_STA_KnownNetworkNotFound:
                if disp != None and DisplayedScreen == None:
                    fnt.PrintString(disp, "[-NF-]", 0, 32, 1, 1)
                    fnt.PrintString(disp, "[SKIP]", 0, 42, 1, 1)
                    fnt.PrintString(disp, "[    ]", 0, 42, 1, 1)
                    disp.show()
                esp.AP_Activate(SSID = SystemName,
                                Password = WiFi_AP_Password,
                                Channel = WiFi_AP_Channel,
                                IP = WiFi_AP_IP,
                                SM = WiFi_AP_SM,
                                DHCP_From = WiFi_AP_DHCP_From,
                                DHCP_To = WiFi_AP_DHCP_To)
            elif NewState == esp.ESP_AP_Activated:
                if disp != None and DisplayedScreen == None:
                    pass
                esp.StartServer(SystemPort)
            elif NewState == esp.ESP_ServerStarted:
                #esp.Debug(False)
                ReadyForConnect = True
                if disp != None and DisplayedScreen == None:
                    if esp.STA_State.SSID == None:
                        fnt.PrintString(disp, "[ OK ]", 0, 52, 1, 1)
                    else:
                        fnt.PrintString(disp, "[ OK ]", 0, 52, 1, 1)
                    disp.show()
                NeoSequencer.StartSequence( 2, False )
                RequestedScreen = 1
                LastScreenUpdate = utime.ticks_ms()
                print("------")
        elif Connection == 0:
            if NewState == esp.ESP_Connected:
                ReadyForConnect = False
                Disconnected_ts = None
                NeoSequencer.StartSequence( 2, False )
            elif NewState == esp.ESP_Disconnected:
                Disconnected_ts = utime.ticks_ms()
                NeoSequencer.StartSequence( 1, False )

                
  # Data Received callback
def WiFi_DataReceived(ConnectionNumber, From, Data):
    pass
"""    if ConnectionNumber == 0:
        TxData = Modbus.ProcessMessage(Data)
        if TxData != None:
            esp.SendData( 0, TxData)"""
            
### INITIALIZING ESP ###############################################################################            
esp = ESP_AT(0, ESP_TX, ESP_RX, ESP_EN,
             Debug=True,
             StateChangeCallback = WiFi_StateChange,
             DataReceivedCallback = WiFi_DataReceived)

### SWITCH ON (ENABLE) ESP MODULE ##################################################################
esp.ON()




PWM_1 = PWM(M1_PWM)
PWM_1.freq(800)
PWM_1.duty_u16(40000)
M1_IN1.on()
M1_IN2.off()

PWM_2 = PWM(M2_PWM)
PWM_2.freq(800)
PWM_2.duty_u16(40000)
M2_IN1.on()
M2_IN2.off()

PWM_3 = PWM(M3_PWM)
PWM_3.freq(800)
PWM_3.duty_u16(40000)
M3_IN1.on()
M3_IN2.off()

PWM_4 = PWM(M4_PWM)
PWM_4.freq(800)
PWM_4.duty_u16(40000)
M4_IN1.off()
M4_IN2.on()

#M_STBY.on()


####################################################################################################
# MAIN LOOP                                                                                        #
####################################################################################################
try:
    InitializedTS = utime.ticks_us()
    LastScreenUpdate = utime.ticks_ms()
    PanServo.degMove(130, 130)
    TiltServo.degMove(-20, 5)
    while True:
        ##### CHECK BUTTONS PRESS ###########################################################
        btnCode = ButtonsPeriodic(PWR_BTN, BTN_ADC)
        if btnCode != '':
            print(btnCode)
        if btnCode == 'Q':
            while SecondCoreLock.locked():
                utime.sleep_ms(1)
            break
        
        ##### Battery voltage and temperature reading #######################################
        BatteryVoltage = VBAT_ADC.read_u16() * ADC_LSB * 2 * VBAT_CAL
        DCDCVoltage = V5_ADC.read_u16() * ADC_LSB * 2 * VDC_CAL
        Temperature = 27 - ((TEMP_ADC.read_u16() * ADC_LSB) - 0.706)/0.001721
        
        
        ##### Periodical class update #######################################################
        NeoSequencer.Periodic()
        """if not IIC_Lock.locked():
            for srv in Servos:
                srv.periodic()       
        if PanServo.inPosition:
            if PanServo.actualPosition > 0:
                PanServo.degMove(-130, 110)
            else:
                PanServo.degMove(130, 110)"""
                
        """if TiltServo.inPosition:
            if TiltServo.actualPosition > 0:
                TiltServo.degMove(80, 5)                 
            else:        
                TiltServo.degMove(-20, 5)"""
        
        ##### Screen updates ################################################################
        FromLastUpdate = utime.ticks_diff(utime.ticks_ms(), LastScreenUpdate)
        #if not SecondCoreLock.locked() and disp != None and RequestedScreen != None and FromLastUpdate > 500:
        if not SecondCoreLock.locked() :
            LastScreenUpdate = utime.ticks_ms()
            _thread.start_new_thread(DisplayUpdateThread, ())

                    
                
        
        ##### Scan duration statistics counting #############################################
        if ScanStartTS == None:
            ScanNumber = 1
            ScanActual = utime.ticks_diff(utime.ticks_us(), InitializedTS)
            ScanAverage = ScanActual
        else:
            ScanNumber += 1
            ScanActual = utime.ticks_diff(utime.ticks_us(), ScanStartTS)
            AvgD = (ScanActual - ScanAverage) / ScanNumber
            ScanAverage = ScanAverage + AvgD
        ScanStartTS = utime.ticks_us()
        """if ScanMaximal == None or ScanMaximal < ScanActual:
            ScanMaximal = ScanActual
        if ScanMinimal == None or ScanMinimal > ScanActual:
            ScanMinimal = ScanActual"""
        #utime.sleep(0.001)
        
        

    
except KeyboardInterrupt:
    print("==========================================")
    print("=====         Breaked by user        =====")
    while SecondCoreLock.locked():
        utime.sleep_ms(1)
except Exception as e:
    print("==========================================")
    print()
    sys.print_exception(e)
    print()
else:
    print("==========================================")
    print("=====          SWITCHED OFF          =====")


print("===== init : {0: >15.1f} ms".format((InitializedTS - StartTime)/1000))
print("===== run  : {0: >15.1f} min".format((utime.ticks_us() - StartTime) / 60000000))
print("===== SCAN TIME STATISTICS:")
#print("=====  max : {0: >15.2f} ms".format(ScanMaximal/1000))
print("=====  avg : {0: >15.2f} ms".format(ScanAverage/1000))
#print("=====  min : {0: >15.2f} ms".format(ScanMinimal/1000))
print("=====  num : {0: >15d}".format(ScanNumber))
print("===== GOOD BYE")

CLK_1Hz_Timer.deinit()
I_LED.off()
M_STBY.off()
if disp != None:
    disp.fill(0)
    disp.show()
if NeoLED != None:
    for i in range(NeoLED.n):
        NeoLED[i] = (0, 0, 0)
    NeoLED.write()
if esp != None:
    esp.OFF()

PWR_ON.off()
utime.sleep(2)
if BatteryVoltage > 2.8:
    reset()
    

