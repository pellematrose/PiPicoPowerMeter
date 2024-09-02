from color_setup import ssd                                                              
from gui.core.writer import Writer
from gui.core.nanogui import refresh                             
from gui.widgets.label import Label
from time import sleep
import time
# Fonts
import gui.fonts.arial10 as arial10
#import gui.fonts.courier20 as fixed
import gui.fonts.font6 as small
import gui.fonts.arial35 as arial35
#import gui.fonts.arial_50 as arial50
import gui.fonts.freesans20 as free20

def start_screen(bus, shunt):
    print(bus)
    print(shunt)
    if bus == 0:
        vol = 16
    elif bus == 1:
        vol = 32
    
    if shunt == 0:
        vsh = 40
    elif shunt == 1:
        vsh = 80
    elif shunt == 2:
        vsh = 160
    elif shunt == 3:
        vsh = 320
    else: vsh = 0    
    
    ssd.fill(0)
    refresh(ssd)
    
    wri = Writer(ssd, free20, verbose=False)
    wri.set_clip(False, False, False)
    Label(wri, 0, 0, 'Settings', bdcolor=False)

    wri2 = Writer(ssd, arial10, verbose=False)
    wri2.set_clip(False, False, False)
    Label(wri2, 25, 0, f"Max Volage = {vol}V")
    Label(wri2, 35, 0, f"Max Current = {vsh}mA")
    
    refresh(ssd)
    time.sleep_ms(1000)
    ssd.fill(0)
    refresh(ssd)

def format_number(num):
    if num >= 100:
        return f"{int(num)}"
    elif num >= 10:
        return f"{num:.1f}"
    elif num >= 1:
        return f"{num:.2f}"
    
def show_value(label, wert):

    if (wert < 40 and wert >= 1):
        d = "x"
        if label == "Voltage":
            d = "V"
        elif label == "Current":
            d = "A"
        elif label == "Power":
            d = "W"   
        w = f"{format_number(wert)}{d}"

    elif (wert < 1 and wert >= 0.001):
        wert = wert*1000
        d = "m"
        if label == "Voltage":
            d = "mV"
        elif label == "Current":
            d = "mA"
        elif label == "Power":
            d = "m"
        w = f"{format_number(wert)}{d}"

    else:
        wert = wert*1000000
        d = "u"
        w = f"{format_number(wert)}{d}"
    
    wri = Writer(ssd, free20, verbose=False)
    wri.set_clip(False, False, False)
    Label(wri, 0, 2, label)
    
    wri2 = Writer(ssd, arial35, verbose=False)
    wri2.set_clip(False, False, False)
    Label(wri2, 27, 0, '            ', bdcolor=False)
    Label(wri2, 27, 0, w, bdcolor=False)

    refresh(ssd)
    
def multi_show_values(voltage, current, power):
    u = f"{voltage:.3f}{"V"}"
    i = f"{current:.3f}{"A"}"
    p = f"{power:.3f}{"W"}"
                                                                     
    wri = Writer(ssd, free20, verbose=False)
    wri.set_clip(False, False, False)
    Label(wri, 2, 2, 'Overview', bdcolor=False)

    Writer.set_textpos(ssd, 20, 0)  # In case previous tests have altered it
    wri = Writer(ssd, small, verbose=False)
    wri.set_clip(False, False, False)

    Label(wri, 23, 2, 'U:', bdcolor=False)                                                               
    Label(wri, 23, 15, '                    ', bdcolor=False) # draw black space to erase former value
    Label(wri, 23, 15, u, bdcolor=False)

    Label(wri, 36, 2, 'I:', bdcolor=False)                                                                  
    Label(wri, 36, 15, '                    ', bdcolor=False) # draw black space to erase former value
    Label(wri, 36, 15, i, bdcolor=False)
    
    Label(wri, 49, 2, 'P:', bdcolor=False)                                                                  
    Label(wri, 49, 15, '                    ', bdcolor=False) # draw black space to erase former value
    Label(wri, 49, 15, p, bdcolor=False)    
    
    refresh(ssd)    
