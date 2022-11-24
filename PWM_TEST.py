from machine import Pin, PWM
import utime


GreenLED = Pin(25, Pin.OUT)


GreenLED_PWM = PWM(GreenLED)
GreenLED_PWM.freq(150)
GreenLED_PWM.duty_u16(0)

for i in range(65):
    GreenLED_PWM.duty_u16(i * 1000)
    utime.sleep_ms(100)



BImage = 0x0805

while True:
    BImageBF = BImage
    for n in range(0,10):
        if (BImageBF & 1) == 1:
            GreenLED_PWM.duty_u16(65535)
        else:
            GreenLED_PWM.duty_u16(0)
        BImageBF = BImageBF >> 1
        utime.sleep_ms(50)
        
    