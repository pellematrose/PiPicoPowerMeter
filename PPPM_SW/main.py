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

# Copyright (c) 2023 Per-Simon Saal

from machine import Pin, I2C
from struct import unpack
from time import sleep
import time
import math
from drivers.ina219 import ina219

import utime
# import uos
from color_setup import ssd
# On a monochrome display Writer is more efficient than CWriter.
from gui.core.writer import Writer
from gui.core.nanogui import refresh
from gui.widgets.meter import Meter
from gui.widgets.label import Label

# Fonts
import gui.fonts.arial10 as arial10
import gui.fonts.courier20 as fixed
import gui.fonts.font6 as small
import gui.fonts.arial35 as arial35
import gui.fonts.arial_50 as arial50
import gui.fonts.freesans20 as free20

#INA219 CONFIG
INA_ADDR = 64
SHUNT_OHMS = 0.1 #R

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

mWh = 0
actual_time = 0
last_time = 0
toggle_time = 0

# page of the UI
page = 0
# refresh rate of take and show measurements in ms
refresh_rate = 500

# state of the led
led1_state = 0

# initialize i2c (which i2cx, GPNr., GPNr., frequency Hz)
i2c_ina  = I2C(1, scl = Pin(15), sda = Pin(14), freq = 400000)

# initialize button
button = Pin(9, Pin.IN, Pin.PULL_UP)
btn_debounce_t = 0
btn_isr_flag = 0

# for logging
file_name = "Logging.csv"

# initialize led1 and led2
led1 = Pin(10, Pin.OUT, None)
led1.value(0)
led2 = Pin(11, Pin.OUT, None)
led2.value(0)

# Create current measuring object
ina = ina219(INA_ADDR, i2c_ina)
ina.configure(SHUNT_OHMS, VBUS_RANGE_16, VSHUNT_MAX_2, BADC_12BIT, SADC_12BIT, MODE_SHUNT_BUS_C)

# clear screen
#ssd.fill(0)
# Writer.set_textpos(ssd, 2, 2)  # In case previous tests have altered it
# wri = Writer(ssd, small, verbose=False)
# wri.set_clip(False, False, False)
# textfield = Label(wri, 2, 2, wri.stringlen('long'), bdcolor=False)
# textfield.value("PPPM")
# refresh(ssd)
# text, x pos, y pos
ssd.text("Power Meter", 0, 0)
ssd.show()

time.sleep_ms(1000)

def btn_callback(button):
    global btn_isr_flag, btn_debounce_t
    if (time.ticks_ms()-btn_debounce_t) > 200:
        btn_isr_flag= 1
        btn_debounce_t=time.ticks_ms()
        
button.irq(trigger=button.IRQ_FALLING, handler=btn_callback)
        
def show_value(label, wert):
    l = label
    d = "x"
    if l == "Voltage    ":
        d = "V"
    elif l == "Current  ":
        d = "A"
    elif l == "Power    ":
        d = "W"
        
    w = f'{str(round(wert,2))}{d}'
    #ssd.fill(0)
    refresh(ssd)
    Writer.set_textpos(ssd, 0, 0)  # In case previous tests have altered it
    wri = Writer(ssd, free20, verbose=False)
    wri.set_clip(False, False, False)
    textfield = Label(wri, 0, 2, wri.stringlen('longer'))
    
    wri2 = Writer(ssd, arial35, verbose=False)
    wri2.set_clip(False, False, False)
    numfield = Label(wri2, 27, 2, wri2.stringlen('99.99'), bdcolor=False)
    
    textfield.value(l)
    numfield.value("              ") # draw black space to erase former value
    numfield.value(w)

    refresh(ssd)
    
def multi_show_values(voltage, current, power):
    u = f'{str(round(voltage,3))}{"V"}'
    i = f'{str(round(current,3))}{"A"}'
    p = f'{str(round(power,3))}{"W"}'

    refresh(ssd)
    #Writer.set_textpos(ssd, 2, 2)  # In case previous tests have altered it
    wri = Writer(ssd, free20, verbose=False)
    wri.set_clip(False, False, False)
    textfield = Label(wri, 2, 2, wri.stringlen('loooooong'), bdcolor=False)
    textfield.value("Overview")
    
    Writer.set_textpos(ssd, 20, 0)  # In case previous tests have altered it
    wri = Writer(ssd, small, verbose=False)
    wri.set_clip(False, False, False)

    vold_field = Label(wri, 23, 2, wri.stringlen('U'), bdcolor=False)
    vold_field.value("U:")
    vol_field = Label(wri, 23, 15, wri.stringlen('longer'), bdcolor=False)
    vol_field.value("                   ") # draw black space to erase former value
    vol_field.value(u)
    curd_field = Label(wri, 36, 2, wri.stringlen('I'), bdcolor=False)
    curd_field.value("I:")
    cur_field = Label(wri, 36, 15, wri.stringlen('longer'), bdcolor=False)
    cur_field.value("                    ") # draw black space to erase former value
    cur_field.value(i)
    powd_field = Label(wri, 49, 2, wri.stringlen('P'), bdcolor=False)
    powd_field.value("P:")
    pow_field = Label(wri, 49, 15, wri.stringlen('longer'), bdcolor=False)
    pow_field.value("                     ") # draw black space to erase former value
    pow_field.value(p)
    
    
while True:
    # get system tick
    actual_time = time.ticks_ms()
        
    # take and show measurements 'refresh_rate' seconds
    if actual_time - last_time > refresh_rate:

        last_time = actual_time
    
        v = ina.vbus()
        #c = ina.vshunt()
        i = ina.current()
        p = ina.power()
        #experimental
        mWh = mWh + p / 3600
        
        print("v = %.3fV" % v ,", i = %.3fA" % i, " P = %.2fW" % p, " E = %.4fmWh" % mWh)
        #print("%.3f"%v,",%.3f"%i,",%.2f"%p,"\n")
        
        if page == 0:
            label = "Voltage    "
            show_value(label, v)
        elif page == 1:
            label = "Current  "
            show_value(label, i)
        elif page == 2:
            label = "Power    "
            show_value(label, p)
#         elif page == 3:
#             label = "Energy   "
#             show_value(label, mWh)
        elif page == 3:
            label = "Overview "
            multi_show_values(v, i, p)
        
        # logging u, i and p to a csv
#         with open (file_name,"a") as logging:
#             logging.write(f'{str(v)}')
#             logging.write(",")
#             logging.write(f'{str(i)}')
#             logging.write(",")
#             logging.write(f'{str(p)}{"\n"}')
#             logging.flush()
#         logging.close()

    
    # todo when button is pressed
    if btn_isr_flag is 1:
        btn_isr_flag = 0
        
        if page < 3:
            page += 1
            ssd.fill(0)	# clear display when open new page
            #print("Page: %d" %page)

        elif page == 3:
            page = 0
            ssd.fill(0)
            #print("Page: %d" %page)
            
        # add custom button code here
    
    # just toggle the led1
    if actual_time - toggle_time > 1000:
        toggle_time = time.ticks_ms()
        if led1_state == 1:
            led1.value(0)
            led1_state = 0
        elif led1_state == 0:
            led1.value(1)
            led1_state = 1
    
    