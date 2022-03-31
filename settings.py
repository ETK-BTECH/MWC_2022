from ESP_DC import Network

VREF                 = 3.24
VBAT_CAL             = 1.051
VDC_CAL              = 1.000
SystemName           = "HAL9000"
SystemPort           = 6000

PanS_usMin           = 850
PanS_usMax           = 2400
PanS_degMin          = -155
PanS_degMax          = 155

TiltS_usMin          = 900
TiltS_usMax          = 2400
TiltS_degMin         = 80
TiltS_degMax         = -20

ldFL                 = const(0)     # Front Left LED
ldBFL                = const(2)     # Front Left Bottom LED
ldBRL                = const(5)     # Rear Left Bottom LED
ldRL                 = const(6)     # Rear Left LED
ldFR                 = const(7)     # Front Right LED
ldBFR                = const(3)     # Front Right Bottom LED
ldBRR                = const(4)     # Rear Right Bottom LED
ldRR                 = const(1)     # Rear Right LED


WiFi_AP_Password     = "2knedLici"
WiFi_AP_Channel      = 8
WiFi_AP_IP           = "192.168.50.254"
WiFi_AP_SM           = "255.255.255.0"
WiFi_AP_DHCP_From    = "192.168.50.200"
WiFi_AP_DHCP_To      = "192.168.50.210"

ESP_Networks = (    
        Network(SSID="BTECH RV4 demo",
                Password="10knedLiku"
                ),
        
        Network(SSID="HOME_SSID",
                Password="HOME_PWD",
                #IP="192.168.2.10",
                #SM="255.255.255.0",
                #DG="192.168.2.254"
                ),        
        )