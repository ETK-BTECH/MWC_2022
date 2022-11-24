from settings import *
import gc
import utime

def PaintTitle(disp, Font, ScreenName):
    Font.PrintString(disp, SystemName, 0, 0, 1, 1)
    Font.PrintString(disp, ScreenName, 0, 9, 1, 1)
    disp.hline(0,18,128, 1)
    
    
def PaintScreen_1(disp, Font):
    utime.sleep_ms(10)
    PaintTitle(disp, Font, "System")
    Font.PrintString(disp, "Battery  :", 3, 22, 1, 1)
    Font.PrintString(disp, "V", 110, 22, 1, 1)
    Font.PrintString(disp, "Motor    :", 3, 32, 1, 1)
    Font.PrintString(disp, "V", 110, 32, 1, 1)
    Font.PrintString(disp, "CPU Temp :", 3, 42, 1, 1)
    Font.PrintString(disp, "°C", 110, 42, 1, 1)
    Font.PrintString(disp, "SW scan  :", 3, 52, 1, 1)
    Font.PrintString(disp, "ms", 110, 52, 1, 1)
   
def UpdateScreen_1(disp, Font, BatteryV, MotorV, CPUt, ScanAverage):
    disp.fill_rect(65, 21, 43, 43, 0)
    Font.PrintString(disp, "{: >7.2f}".format(BatteryV), 65, 22, 1, 1)
    Font.PrintString(disp, "{: >7.2f}".format(MotorV), 65, 32, 1, 1)
    Font.PrintString(disp, "{: >7.1f}".format(CPUt), 65, 42, 1, 1)
    Font.PrintString(disp, "{: >7.3f}".format(ScanAverage), 65, 52, 1, 1)