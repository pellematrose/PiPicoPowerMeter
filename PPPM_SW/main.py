# Inspired from
# https://www.youtube.com/watch?v=YR9v04qzJ5E
# mono_test.py Demo program for nano_gui on an SSD1306 OLED display.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2018-2021 Peter Hinch

# https://learn.adafruit.com/monochrome-oled-breakouts/wiring-128x32-spi-oled-display
# https://www.proto-pic.co.uk/monochrome-128x32-oled-graphic-display.html

# V0.33 16th Jan 2021 Hardware configuration is now defined in color_setup to be
# consistent with other displays.
# V0.32 5th Nov 2020 Replace uos.urandom for minimal ports

# Last edit: 29.08.2024
# Copyright (c) 2023 Per-Simon Saal

from machine import Pin, I2C, UART
from struct import unpack
from time import sleep
import time
import math
from drivers.ina219 import ina219
import utime
from functions import format_number, show_value, multi_show_values

from color_setup import ssd

#INA219 CONFIG
INA_ADDR = 64

VBUS_RANGE_16 = 0x00	#BRNG
VBUS_RANGE_32 = 0x01
VSHUNT_MAX_1 = 0x00		#0.040 gain
VSHUNT_MAX_2 = 0x01		#0.080
VSHUNT_MAX_4 = 0x02		#0.160
VSHUNT_MAX_8 = 0x03		#0.320

BADC_9BIT  = 0x00
BADC_10BIT = 0x01
BADC_11BIT = 0x02
BADC_12BIT = 0x03
BADC_2S = 0x08
BADC_4S = 0x0A
BADC_8S = 0x0B
BADC_16S = 0x0C
BADC_32S = 0x0D
BADC_64S = 0x0E
BADC_128S = 0x0F

SADC_9BIT  = 0x00
SADC_10BIT = 0x01
SADC_11BIT = 0x02
SADC_12BIT = 0x03
SADC_2S = 0x08
SADC_4S = 0x0A
SADC_8S = 0x0B
SADC_16S = 0x0C
SADC_32S = 0x0D
SADC_64S = 0x0E
SADC_128S = 0x0F

MODE_POWER_DOWN  = 0x00
MODE_SHUNT_TRIG  = 0x01
MODE_VOLT_TRIG   = 0x02
MODE_SHUNT_BUS_T = 0x03
MODE_ADC_OFF     = 0x04
MODE_SHUNT_C     = 0x05
MODE_VOLT_C      = 0x06
MODE_SHUNT_BUS_C = 0x07	#Shunt and bus, continuous

# actual used mode (edit here)
SHUNT_OHMS = 0.1 #R
VBUS = VBUS_RANGE_32
VSHUNT = VSHUNT_MAX_4
BADC = BADC_12BIT
SADC = SADC_12BIT
MODE = MODE_SHUNT_BUS_C

mWh = 0

# helper variables to run the code periodically
actual_time_oled = 0 
actual_time_meas = 0 
actual_time_csv = 0
last_time_oled = 0
last_time_meas = 0
last_time_csv = 0
toggle_time = 0

# refresh rate of take and show measurements in ms. EDIT here:
refresh_rate_oled = 250
refresh_rate_meas = 250
refresh_rate_csv = 500

# page of the UI
page = 0

# initialize i2c (which i2cx, GPNr., GPNr., frequency Hz)
i2c_ina  = I2C(1, scl = Pin(15), sda = Pin(14), freq = 400000)

# initialize UART on port 1 pins 4 & 5
uart1 = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5), bits=8, parity=None, stop=1)

# initialize button
button = Pin(9, Pin.IN, Pin.PULL_UP)
btn_debounce_t = 0
btn_isr_flag = 0

button2 = Pin(8, Pin.IN, Pin.PULL_UP)
btn_isr_flag2 = 0

button3 = Pin(1, Pin.IN, Pin.PULL_UP)
btn_isr_flag3 = 0

# for logging
file_name = "Logging.csv"

# initialize led1 and led2
led1 = Pin(10, Pin.OUT, None)
led1.value(0)
led2 = Pin(11, Pin.OUT, None)
led2.value(0)

# Create current measuring object
ina = ina219(INA_ADDR, i2c_ina)
ina.configure(SHUNT_OHMS, VBUS, VSHUNT, BADC, SADC, MODE)
    
# Write initial Text on OLED                
ssd.text("Power Meter", 0, 0)
ssd.show()

time.sleep_ms(500)

def btn_callback(button):
    global btn_isr_flag, btn_debounce_t
    if (time.ticks_ms()-btn_debounce_t) > 200:
        btn_isr_flag= 1
        btn_debounce_t=time.ticks_ms()
        
button.irq(trigger=button.IRQ_FALLING, handler=btn_callback)
   
def btn2_callback(button2):
    global btn_isr_flag2, btn_debounce_t
    if (time.ticks_ms()-btn_debounce_t) > 200:
        btn_isr_flag2= 1
        btn_debounce_t=time.ticks_ms()
        
button2.irq(trigger=button.IRQ_FALLING, handler=btn2_callback)

def btn3_callback(button3):
    global btn_isr_flag3, btn_debounce_t
    if (time.ticks_ms()-btn_debounce_t) > 200:
        if btn_isr_flag3 == 0:
            btn_isr_flag3 = 1
        else:
            btn_isr_flag3 = 0           
        #btn_isr_flag3 = 1
        btn_debounce_t=time.ticks_ms()
        led2.toggle()
        
button3.irq(trigger=button.IRQ_FALLING, handler=btn3_callback)
    
while True:
    # get system tick
    actual_time_meas = time.ticks_ms()
    actual_time_oled = time.ticks_ms()
    actual_time_csv = time.ticks_ms()
        
    # take and show measurements 'refresh_rate' seconds
    if actual_time_meas - last_time_meas > refresh_rate_meas:
        last_time_meas = actual_time_meas
    
        v = ina.vbus()
        #c = ina.vshunt()
        i = ina.current()
        p = ina.power()
        #experimental
        mWh = mWh + p / 3600
        
        #print("v = %.6fV" % v ,", i = %.6fA" % i, " P = %.6fW" % p, " E = %.6fmWh" % mWh)
        #print("%.3f"%v,",%.3f"%i,",%.2f"%p,"\n")
        
        # Output for Serial Studio
        #print('/*' + str(v) + ',' + str(i) + ',' + str(p) + '*/\n')
     
    if actual_time_oled - last_time_oled > refresh_rate_oled:
        last_time_oled = actual_time_oled
         
        if page == 0:               
            show_value("Voltage", v)
        elif page == 1:             
            show_value("Current", i)
        elif page == 2:      
            show_value("Power", p)
#         elif page == 3:    
#             show_value("Engergy", mWh)
        elif page == 3:             
            multi_show_values(v, i, p)
        
    if actual_time_csv - last_time_csv > refresh_rate_csv:
        last_time_csv = actual_time_csv                                                      
         
        if btn_isr_flag3 is 1:
            btn_isr_flag3 = 0                      
            #logging u, i and p to a csv
            with open (file_name,"a") as logging:
                logging.write(f'{str(v)}')
                logging.write(",")
                logging.write(f'{str(i)}')
                logging.write(",")
                logging.write(f'{str(p)}{"\n"}')
                logging.flush()
            logging.close()
                                  
    # todo when button is pressed
    if btn_isr_flag is 1:
        btn_isr_flag = 0
        
        if page < 3:
            page += 1
            ssd.fill(0)	# clear display when open new page
        elif page == 3:
            page = 0
            ssd.fill(0)    
    
    if btn_isr_flag2 is 1:
        btn_isr_flag2 = 0
        if page > 0:
            page -= 1
            ssd.fill(0)
        elif page == 0:
            page = 3
            ssd.fill(0)                     

    # just toggle the led1
    if actual_time_oled - toggle_time > 1000:
        toggle_time = time.ticks_ms()
        led1.toggle()
